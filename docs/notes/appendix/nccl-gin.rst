
.. meta::
    :description lang=zh_CN: 使用 EFA 在 AWS 上通过 DeepEP 为 NCCL 启用 GPU 发起的网络
    :keywords: NCCL, GIN, GPU-Initiated Networking, DeepEP, EFA, AWS, MoE, HyperPod

AWS 上 NCCL 的 GPU 主动发起网络通信（GPU-Initiated Networking for NCCL on AWS）
======================================================================================================================================

:Date: 2026-02-22

摘要（Abstract）
------------------------

GPU-Initiated Networking (GIN) 作为 key 大型语言模型 (LLM) 训练和推理中内核融合的推动者，吸引了大量 attention。专家混合 (MoE) 架构，例如 DeepSeek-V3 和 Qwen3-30B，需要跨 MoE 层进行高效的令牌调度和组合。传统上，GPU 间通信由 CPU 通过集体 libraries（例如 NCCL 或 Gloo）发起，需要显式的 GPU 同步屏障和额外的 ``cudaLaunchKernel`` 调用，从而引入不小的开销。 GPU-Initiated Networking 通过允许数据交换直接在 CUDA 内核内进行，消除了这种由 CPU 介导的往返，从而实现内核融合和高效的 CUDA 图捕获，从而加速端到端 LLM 层计算。本文演示如何使用 AWS Elastic Fabric Adapter (EFA) 在 AWS HyperPod Slurm 上启用 NCCL GIN 和 DeepEP。

介绍（Introduction）
--------------------------------

2026 年之前，采用 DeepEP 作为 AWS 上的混合专家调度和组合后端提出了重大挑战。 DeepEP 内核最初构建在 InfiniBand 之上，具有定制的 NVSHMEM 实现，传输层在 AWS 基础设施上不可用。这种不兼容性有效地阻止了用户在配备 Elastic Fabric Adapter (EFA) 的 instances 上利用 DeepEP。 NVIDIA 和 Amazon Annapurna Labs 最近的合作努力解决了这一差距，在 NCCL 和 EFA 提供商中引入了 GPU 发起的网络支持，使 DeepEP 能够在 EFA 上运行，而无需依赖 InfiniBand（请参阅 `DeepEP PR #521 <https://github.com/deepseek-ai/DeepEP/pull/521>`_ 和 `aws-ofi-nccl PR #1069 <https://github.com/aws/aws-ofi-nccl/pull/1069>`_ ）。以下实验基于这些贡献，说明如何使用 EFA 在 AWS 上部署带有 NCCL GIN 的 DeepEP。

构建 DeepEP（Build DeepEP）
----------------------------------------------

在 AWS HyperPod Slurm 上部署 DeepEP 之前，必须从源代码构建多个组件。首先，需要 NCCL >= v2.29.3-1，因为这是公开 GPU 启动网络所需的设备 API 的最低版本。该构建针对 ``sm_90`` (NVIDIA H100) 和 ``sm_100`` (NVIDIA B200) 计算功能，以确保与当前一代 GPU instances 的兼容性。

.. code-block:: bash

    NCCL_VERSION=v2.29.3-1
    git clone -b ${NCCL_VERSION} https://github.com/NVIDIA/nccl.git /opt/nccl \
        && cd /opt/nccl \
        && make -j $(nproc) src.build CUDA_HOME=/usr/local/cuda \
        NVCC_GENCODE="-gencode=arch=compute_90,code=sm_90 -gencode=arch=compute_100,code=sm_100"

或者，可以构建 NCCL 设备 API 示例来验证 GPU 在目标环境中是否正确启动了通信 functions。此外，最新版本的 nccl 测试 (v2.17.9) 附带了适用于 ``alltoall`` 集合的支持 GIN 的微基准测试，这对于在全面运行之前验证 GPU bandwidth 和 latency 之间非常有用MoE 工作负载（请参阅 `nccl-tests alltoall.cu <https://github.com/NVIDIA/nccl-tests/blob/v2.17.9/src/alltoall.cu#L214-L291>`_ ）。

.. code-block:: bash

    ## 构建 NCCL 设备 API 示例
    cd /opt/nccl/examples/06_device_api \
        && make -j $(nproc) NCCL_HOME=/opt/nccl/build CUDA_HOME=/usr/local/cuda MPI=1 MPI_HOME=/opt/amazon/openmpi

    NCCL_TESTS_VERSION=v2.17.9
    git clone -b ${NCCL_TESTS_VERSION} https://github.com/NVIDIA/nccl-tests.git /opt/nccl-tests \
        && cd /opt/nccl-tests \
        && make -j $(nproc) \
        MPI=1 \
        MPI_HOME=/opt/amazon/openmpi/ \
        CUDA_HOME=/usr/local/cuda \
        NCCL_HOME=/opt/nccl/build \
        NVCC_GENCODE="-gencode=arch=compute_90,code=sm_90 -gencode=arch=compute_100,code=sm_100"

要在 HyperPod Slurm 上测试 DeepEP，DeepEP 和 aws-ofi-nccl 都必须固定到包含 NCCL GIN 传输路径的特定提交。 Aamir Shafi 的 DeepEP 分支引入了基于 NCCL 的通信后端，作为原始 NVSHMEM/InfiniBand 路径的替代方案，而 aws-ofi-nccl 插件提供了 EFA 所需的 libfabric-to-NCCL 转换层。请注意，NCCL GIN 实现已合并到 aws-ofi-nccl 主分支中；为了重现性，提交 hash 被固定在此处。

.. code-block:: bash

    ## 使用 NCCL GIN 后端安装 DeepEP (PR #521)
    unset NVSHMEM_DIR NVSHMEM_HOME \
        && export ENABLE_NCCL=1 \
        && export NCCL_DIR=/opt/nccl/build \
        && export LD_LIBRARY_PATH=/opt/nccl/build/lib:$LD_LIBRARY_PATH \
        && export LD_PRELOAD=/opt/nccl/build/lib/libnccl.so.2 \
        && git clone -b nccl https://github.com/aamirshafi/DeepEP.git /opt/DeepEP \
        && cd /opt/DeepEP \
        && git checkout 6d29f34 \
        && python3 setup.py build_ext --inplace \
        && pip install --break-system-packages --no-build-isolation .

    AWS_OFI_NCCL_VERSION=5f4202f11db1585d878196db4430aeda0e834a0c
    git clone https://github.com/aws/aws-ofi-nccl.git /tmp/aws-ofi-nccl \
        && cd /tmp/aws-ofi-nccl \
        && git checkout ${AWS_OFI_NCCL_VERSION} \
        && ./autogen.sh \
        && ./configure --prefix=/opt/amazon/ofi-nccl \
            --with-libfabric=/opt/amazon/efa \
            --with-cuda=/usr/local/cuda \
        && make -j$(nproc) \
        && make install \
        && rm -rf /tmp/aws-ofi-nccl

有关包含所有必要依赖项的完整构建，请参阅此存储库中提供的 `Dockerfile <https://github.com/crazyguitar/pysheeet/blob/master/src/gin/Dockerfile>`_ 。

测试 NCCL GIN（Test NCCL GIN）
----------------------------------------------------

使用上一节中准备的 Docker 映像（或 Enroot 压缩文件），可以在 Slurm 集群上验证 NCCL GIN 功能。以下示例演示如何启动 NCCL 设备 API 示例和 nccl 测试基准。相应的 Slurm 包装器脚本可在该存储库的 `gin <https://github.com/crazyguitar/pysheeet/blob/master/src/gin/>`_ 目录下找到。

.. code-block:: bash

    make docker && make save  # 构建 docker 映像并导入 Enroot 压缩文件

    # 01_allreduce_lsa（仅限单节点）
    salloc -N 1 ./run.enroot /opt/nccl/examples/06_device_api/01_allreduce_lsa/allreduce_lsa

    # 01_allreduce_lsa（多节点）— 需要 MNNVL (e.g.P6e-GB200)，NOT 是否比 RDMA/EFA 工作
    salloc -N 2 ./run.enroot /opt/nccl/examples/06_device_api/01_allreduce_lsa/allreduce_lsa

    # 02_alltoall_gin（多节点）
    salloc -N 2 ./run.enroot /opt/nccl/examples/06_device_api/02_alltoall_gin/alltoall_gin

    # 03_alltoall_hybrid（多节点）
    salloc -N 2 ./run.enroot /opt/nccl/examples/06_device_api/03_alltoall_hybrid/alltoall_hybrid

nccl 测试 ``alltoall`` benchmark 公开了两个用于选择 GIN 传输模式和内存注册策略的关键标志：

``-D`` 标志选择 ``alltoall`` 集体的设备端实现：

.. code-block:: text

    -D 0 — Host API (default)
    -D 1 — NVL simple (LSA/NVLink only)
    -D 2 — NVL optimized (LSA/NVLink only)
    -D 3 — GIN only (network)
    -D 4 — Hybrid (LSA intra-node + GIN inter-node)

``-R`` 标志控制内存注册。任何设备端实现 ( ``-D > 0`` ) 都需要对称内存分配 ( ``NCCL_MEM_SHARED`` )，因为它将 GPU 内存映射到所有级别以启用通过网络的直接远程读写：

.. code-block:: text

    -R 0 — no registration (default)
    -R 1 — register memory with ncclMemAlloc
    -R 2 — register memory with symmetric memory allocation (NCCL_MEM_SHARED)

以下示例在仅 GIN 模式 ( ``-D 3`` ) 和混合模式 ( ``-D 4`` ) 下启动 nccl 测试 ``alltoall_perf`` benchmark，将消息大小从 32 MB 扫描到 2048 MB。 ``--blocking 0`` 标志启用非阻塞集合，这代表了 MoE 层如何将通信与生产工作负载中的计算重叠：

.. code-block:: bash

    # alltoall_perf 与 GIN (-D 3)
    salloc -N 2 ./run.enroot /opt/nccl-tests/build/alltoall_perf \
      -D 3 -R 2 -b 32M -e 2048M -f 2 -n 1000 -w 10 --blocking 0

    # alltoall_perf 与混合 LSA+GIN (-D 4)
    salloc -N 2 ./run.enroot /opt/nccl-tests/build/alltoall_perf \
      -D 4 -R 2 -b 32M -e 2048M -f 2 -n 1000 -w 10 --blocking 0

通过 NCCL GIN 使用 vLLM 和 DeepEP 部署 MoE 模型（Serving MoE Models with vLLM and DeepEP over NCCL GIN）
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

通过在 AWS HyperPod Slurm 上验证 NCCL、GIN 和 EFA，本部分演示使用 vLLM 和 DeepEP 作为 MoE all-to-all 通信后端的端到端推理部署。 DeepEP 的低 latency 调度和组合内核现在在 NCCL GIN 而不是 NVSHMEM 上运行，可为大型 MoE 模型（例如 DeepSeek-V3）实现高效的专家并行推理。

Slurm 启动脚本 ``run.sbatch`` 与用于在 `vllm example directory <https://github.com/crazyguitar/pysheeet/blob/master/src/llm/vllm/>`_ 中启动 vLLM 服务器的脚本相同。但是，要指示 DeepEP 后端使用 NCCL GIN，启动时以下环境 variables 必须为 set：

.. code-block:: bash

    DEEP_EP_BACKEND=nccl
    NCCL_GIN_TYPE=2  # proxy-based GIN

``NCCL_GIN_TYPE=2`` 选择基于代理的 GIN 路径，其中 CPU 侧代理 thread 代表 GPU 调解网络传输。 ``NCCL_GIN_TYPE=3`` 将启用 GPU 直接异步内核启动 (DAKI) 网络，该网络完全绕过代理；但是，在撰写本文时，AWS 和 EFA 尚不支持 DAKI。

有关服务配置和基准测试的更多详细信息，请参阅 `llm-serving.rst <https://github.com/crazyguitar/pysheeet/blob/master/docs/notes/llm/llm-serving.rst>`_ 或 `vLLM README <https://github.com/crazyguitar/pysheeet/blob/master/src/llm/vllm/README.rst>`_ 。

以下示例为 DeepSeek-V3-0324 启动多节点 vLLM 推理服务器，并启用专家并行性和 DeepEP low-latency all-to-all 后端：

.. code-block:: bash

   IMAGE="${PWD}/src/gin/nccl+latest.tar.gz"
   MODEL="/fsx/models/deepseek-ai/DeepSeek-V3-0324"

   salloc -N 4 bash run.sbatch "${MODEL}" \
     --image "${IMAGE}" \
     --all2all-backend deepep_low_latency \
     --tensor-parallel-size 8 \
     --enable-expert-parallel \
     --gpu-memory-utilization 0.8 \
     --enforce-eager

成功启动后，vLLM 服务器日志确认 DeepEP 作为 all-to-all 后端处于活动状态，并且 NCCL GIN 正在用于 GPU 间通信。 key 指示器是 ``DeepEPLLAll2AllManager`` 管理器选择和 ``[NCCL Backend]`` 初始化消息，显示所有级别的通信器设置、对称内存分配和窗口注册：

.. code-block:: bash

    ...
    INFO 02-22 19:06:49 [serve.py:100] Defaulting api_server_count to data_parallel_size (4).
    INFO 02-22 19:06:49 [utils.py:325]
    INFO 02-22 19:06:49 [utils.py:325]        █     █     █▄   ▄█
    INFO 02-22 19:06:49 [utils.py:325]  ▄▄ ▄█ █     █     █ ▀▄▀ █  version 0.15.1
    INFO 02-22 19:06:49 [utils.py:325]   █▄█▀ █     █     █     █  model   /fsx/models/deepseek-ai/DeepSeek-V3-0324
    INFO 02-22 19:06:49 [utils.py:325]    ▀▀  ▀▀▀▀▀ ▀▀▀▀▀ ▀     ▀
    INFO 02-22 19:06:49 [utils.py:325]
    ...
    INFO 02-22 19:07:51 [cuda_communicator.py:124] Using DeepEPLLAll2AllManager all2all manager.
    ...
    [NCCL Backend] LOW LATENCY MODE: Rank 0 connecting to all 32 ranks
    [NCCL Backend] NCCL version: 2.29.3 (loaded library)
    [NCCL Backend] Initializing 2 communicator(s) (qps_per_rank=8) for rank 0/32
    [NCCL Backend] Rank 0 successfully initialized 2 communicator(s)
    [NCCL Backend] Rank 0 created 2 device communication(s) with 32 barrier sessions each
    [NCCL Backend] Initialized global rank 0/32 (comm rank 0/32)
    [NCCL Backend - Memory Alloc] Rank 0: Allocated ptr=0xf882000000, size=3816818816
    [NCCL Backend - Memory Register] Rank 0: Copying 2 NCCL windows to GPU
    [NCCL Backend - Memory Register] Rank 0: Successfully copied windows to GPU
    [NCCL Backend - Memory Register] Rank 0: Registered windows for ptr=0xf882000000, size=3816818816

一旦服务器准备就绪，就可以通过 OpenAI 兼容的完成 API 发出推理请求：

.. code-block:: bash

    curl -sf -X POST http://<VLLM_HOST>:8000/v1/completions \
      -H 'Content-Type: application/json' \
      -d '{
        "model": "/fsx/models/deepseek-ai/DeepSeek-V3-0324",
        "prompt": "Hello",
        "max_tokens": 10
      }'

      # 输出
      {"id":"cmpl-b6e9530a07561f11","object":"text_completion" ... }

结论（Conclusion）
----------------------------

本文演示了如何使用 Elastic Fabric Adapter 在 AWS HyperPod Slurm 上部署带有 DeepEP 的 vLLM 和 NCCL GIN。由于此集成仍在积极开发中，因此在撰写本文时仍存在某些限制。对于instance，虽然DeepEP的低latency模式支持CUDA图捕获，但通过删除 ``--enforce-eager`` 来启用它目前会导致vLLM启动失败。此外，EFA 的性能可能尚未与基于 InfiniBand 的部署相匹配，因为进一步的优化正在进行中。

本文旨在作为在 AWS 上使用 NCCL GIN 评估 DeepEP 的早期参考。对于生产工作负载，建议等待 NVIDIA 和 Amazon Annapurna Labs 的官方稳定版本。
