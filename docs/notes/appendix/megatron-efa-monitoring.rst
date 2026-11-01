.. meta::
    :description lang=zh_CN: 在 AWS 上进行分布式 LLM 训练期间，使用 NCCL GIN 和 Nsys 监控 EFA 网络性能
    :keywords: EFA, NCCL, GIN, Nsys, Megatron-LM, distributed training, network monitoring, AWS

使用 NCCL GIN 和 Nsys 监控 EFA（Monitoring EFA with NCCL GIN and Nsys）
================================================================================================================================

:Date: 2026-02-28

摘要（Abstract）
------------------------

大规模分布式训练需要深入了解网络行为，以识别瓶颈并优化通信模式。当使用 Elastic Fabric Adapter (EFA) 在 AWS 基础设施上使用 Megatron-LM 训练大型语言模型时，了解网络性能对于实现最佳 throughput 至关重要。本文演示如何使用 Megatron Bridge 在 Megatron-LM 中启用 NCCL GPU 启动网络 (GIN)，并利用 Nsys 和 EFA 指标来监控分布式训练工作负载期间的网络行为。此处介绍的技术基于 AWS re:Invent 2024 [1]_ 的最佳实践。

介绍（Introduction）
--------------------------------

`Megatron-LM 框架（Megatron-LM） <https://github.com/NVIDIA/Megatron-LM>`_ 是一种广泛采用的框架，用于使用模型并行性、管道并行性和数据并行性来训练大型 Transformer 模型。当部署在 AWS instances 和 EFA 上时，网络结构提供高 bandwidth、低 latency 通信，这对于扩展到数百或数千个 GPU 至关重要。然而，实现峰值性能需要仔细调整和监控通信层。

NCCL GPU-Initiated Networking允许GPU直接发起网络操作，无需CPU参与，从而减少latency并实现内核融合。 Nsys（NVIDIA Nsight Systems）提供全面的profiling的GPU内核、CUDA API的调用和网络操作。当与 EFA 指标 collection ( ``--enable efa_metrics`` ) 结合使用时，Nsys 捕获详细的网络适配器统计信息，包括与 GPU 执行时间线相关的 bandwidth 利用率、数据包计数和错误率。这使从业人员能够诊断性能问题并验证网络是否按预期容量运行。

`Megatron Bridge <https://github.com/NVIDIA-NeMo/Megatron-Bridge>`_ 通过提供基于配方的高级界面，简化了 Megatron-LM 训练作业的配置和部署。这样就无需手动构建 complex command-line arguments，并且可以更轻松地为 MoE 模型启用 NCCL GIN 和 DeepEP 等高级功能。因此，本文中的教程将使用Megatron Bridge。

先决条件（Prerequisites）
--------------------------------------

本指南假设以下环境：

- AWS HyperPod 或 EC2 instances，支持 EFA（e.g.、P5、P5e、P5en）
- NCCL >= v2.29.3-1，支持设备 API
- 支持 GIN 的 aws-ofi-nccl 插件
- Megatron-LM，带 Megatron-桥

我们在上一篇文章中演示了如何将 vLLM 与 NCCL GIN 和 DeepEP 一起使用。如果您有兴趣从源代码构建 NCCL 和 aws-ofi-nccl，请参阅此存储库中的 `NCCL GIN article <https://www.pythonsheets.com/notes/appendix/nccl-gin.html>`_ 。

构建 Megatron 容器（Building the Megatron Container）
----------------------------------------------------------------------------------------------

Megatron 训练环境打包为 Docker 容器，并转换为 Enroot 压缩文件，以便部署在 Slurm 集群上。该容器包括支持设备 API 的 NCCL、支持 GIN 的 aws-ofi-nccl 以及支持 Megatron 桥的 Megatron-LM。

构建容器并创建 Enroot 映像：

.. code-block:: bash

    cd src/megatron
    make build

这将创建一个可与 Slurm 启动器脚本一起使用的 ``megatron-lm+latest.sqsh`` 文件。有关容器构建 process 的详细信息，请参阅存储库中的 `Dockerfile <https://github.com/crazyguitar/pysheeet/blob/master/src/megatron/Dockerfile>`_ 和 `enroot.sh <https://github.com/crazyguitar/pysheeet/blob/master/src/megatron/enroot.sh>`_ 脚本。

在 Megatron Bridge 中启用 NCCL GIN（Enabling NCCL GIN in Megatron Bridge）
----------------------------------------------------------------------------------------------------------------------------------------

Megatron Bridge 配方提供了一种配置训练作业的声明性方法。要使用 DeepEP 为 MoE 模型启用 NCCL GIN， ``srun.sh`` 启动程序脚本会自动将以下环境 variables 设为 set：

.. code-block:: bash

    export DEEP_EP_BACKEND=nccl
    export NCCL_GIN_TYPE=2  # 基于代理的 GIN
    export LD_LIBRARY_PATH=/opt/amazon/ofi-nccl/lib:$LD_LIBRARY_PATH

``NCCL_GIN_TYPE=2`` 选择基于代理的实现，其中 CPU thread 调解 GPU 发起的传输。 EFA 目前支持此模式，而截至撰写本文时（2026 年 2 月），AWS 尚不支持 GPU 直接异步内核启动 (DAKI) 网络 ( ``NCCL_GIN_TYPE=3`` )。

``srun.sh`` 脚本还配置其他 EFA 特定设置以获得最佳性能：

.. code-block:: bash

    export FI_PROVIDER=efa
    export FI_EFA_USE_DEVICE_RDMA=1
    export FI_EFA_FORK_SAFE=1
    export NCCL_NET_PLUGIN=/opt/amazon/ofi-nccl/lib/libnccl-net-ofi.so
    export NCCL_TUNER_PLUGIN=/opt/amazon/ofi-nccl/lib/libnccl-tuner-ofi.so
    export NCCL_BUFFSIZE=8388608
    export NCCL_P2P_NET_CHUNKSIZE=524288

使用 DeepEP 和 NCCL GIN 启动 Megatron 训练（Launching Megatron Training with DeepEP and NCCL GIN）
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

以下示例演示如何启动 DeepSeek-V2-Lite 预训练作业，并为 MoE 令牌调度启用 DeepEP。该配方将模型配置为跨 64 个等级使用专家并行性，并使用 NCCL GIN 进行低 latency all-to-all 通信。

.. code-block:: bash

    cd src/megatron

    # 在Slurm上分配2个节点
    salloc -N 2

    # 使用 DeepEP 和 NCCL GIN 启动 DeepSeek-V2-Lite
    ./srun.sh recipes/deepseek_v2_lite_pretrain.py \
        hf_path=/fsx/models/deepseek-ai/DeepSeek-V2-Lite \
        moe_token_dispatcher_type=deepep \
        model.tensor_model_parallel_size=1 \
        model.expert_model_parallel_size=64 \
        model.sequence_parallel=false

``moe_token_dispatcher_type=deepep`` argument 启用 DeepEP 作为 MoE 调度程序后端。在底层，配方配置以下设置：

.. code-block:: python

    cfg.model.moe_token_dispatcher_type = "flex"
    cfg.model.moe_flex_dispatcher_backend = "deepep"
    cfg.model.moe_enable_deepep = True
    cfg.model.moe_shared_expert_overlap = False

训练作业开始时，通过检查设备 API 初始化消息的日志来验证 NCCL 是否在启用 GIN 的情况下进行初始化：

.. code-block:: text

    [NCCL] Device API initialized
    [NCCL] GIN proxy mode enabled (type=2)
    [NCCL Backend] LOW LATENCY MODE: Rank 0 connecting to all ranks
    [NCCL Backend] Initialized global rank 0/64

使用 Nsys 和 EFA 指标监控 EFA（Monitoring EFA with Nsys and EFA Metrics）
--------------------------------------------------------------------------------------------------------------------------------

Nsys（NVIDIA Nsight Systems）提供全面的profiling的GPU内核、CUDA API的调用和网络操作。 ``--enable efa_metrics`` 标志指示 Nsys 以 10Hz 采样率从 EFA 设备计数器（e.g.、rdmap113s0、rdmap114s0）实时收集 EFA 适配器统计信息，包括：

- **TX/RX 带宽** ：发送和接收throughput
- **TX/RX 数据包** ：发送和接收的数据包计数
- **错误计数器** ：链路错误和丢弃的数据包

此外，aws-ofi-nccl 使用 NVTX 注释来标记时间线中的 NCCL 操作，从而允许 NCCL 集体调用与 EFA 网络活动之间的关联。这些指标嵌入在 Nsys 时间线中，并与 GPU 内核执行和 NCCL 操作相关，从而可以轻松识别通信瓶颈并验证网络饱和度。

要分析使用 Nsys 运行的 Megatron 训练并捕获 EFA 指标：

.. code-block:: bash

    cd src/megatron
    salloc -N 8

    ./srun.sh --nsys recipes/deepseek_v2_lite_pretrain.py \
        hf_path=/fsx/models/deepseek-ai/DeepSeek-V2-Lite \
        moe_token_dispatcher_type=deepep \
        model.tensor_model_parallel_size=1 \
        model.expert_model_parallel_size=64 \
        model.sequence_parallel=false \
        profiling.use_nsys_profiler=true \
        profiling.profile_step_start=10 \
        profiling.profile_step_end=15 \
        profiling.profile_ranks=[0]

``--nsys`` 标志通过以下配置启用 Nsys profiling：

.. code-block:: bash

    nsys profile \
        -t cuda,nvtx \
        -s none \
        --cpuctxsw=none \
        --capture-range=cudaProfilerApi \
        --capture-range-end=stop \
        --enable efa_metrics \
        -o nsys-megatron/profile-<hostname>-rank<RANK>.nsys-rep \
        --force-overwrite=true

``--enable efa_metrics`` 标志是 key parameter，它启用 EFA 适配器监控。 Nsys 将自动检测所有 EFA 设备（通常为 ``rdmap182s0`` 、 ``rdmap183s0`` 等），并在整个 profiling 会话期间定期收集统计信息。

profiling完成后，可以下载 ``.nsys-rep`` 文件并在Nsight Systems GUI中打开进行分析。 EFA 指标在时间线视图中显示为附加行，显示与 GPU 内核执行和 NCCL 集体操作相关的 bandwidth 和数据包速率。

.. image:: /_static/appendix/deepep-nsys.png
   :alt: 本图为 Nsys 原始性能截图；横向时间轴表示执行时间，各轨道展示 GPU kernels、通信与 EFA 活动，工具界面及原始测量值保持原样。

.. admonition:: 图例

   本图为 Nsys 原始性能截图；横向时间轴表示执行时间，各轨道展示 GPU kernels、通信与 EFA 活动，工具界面及原始测量值保持原样。

使用 Viztracer 进行分析（Profiling with Viztracer）
--------------------------------------------------------------------------------------

对于训练 loop 的 Python 级 profiling，Megatron Bridge 支持 Viztracer，这是一种低开销跟踪工具，可捕获 function 调用和计时信息。这对于识别可能间接影响网络性能的数据加载、预处理或调度程序逻辑中的 CPU 瓶颈非常有用。

.. code-block:: bash

    salloc -N 2
    ./srun.sh recipes/deepseek_v2_lite_pretrain.py \
        hf_path=/fsx/models/deepseek-ai/DeepSeek-V2-Lite \
        train.train_iters=100 \
        profiling.use_viztracer=true \
        profiling.profile_step_start=10 \
        profiling.profile_step_end=15 \
        profiling.profile_ranks=[0]

生成的 ``.json`` 跟踪文件可以在 Viztracer Web UI 或 Chrome 的 ``chrome://tracing`` 界面中可视化。通过启用 ``log_torch`` ，Viztracer 可以捕获额外的 PyTorch 级详细信息，例如 NCCL stream 和 CUDA stream 操作，从而提供对集体通信和 GPU 内核的执行流程的可见性。然而，要观察详细的 EFA 适配器统计信息（bandwidth、数据包计数、错误计数器），Nsys 和 ``--enable efa_metrics`` 仍然是必需的工具。

结论（Conclusion）
----------------------------

Nsys profiling 和 ``--enable efa_metrics`` 现在提供在分布式训练期间同时监控 EFA 适配器行为和 NCCL 操作的功能。这种可见性对于诊断 NCCL 操作时间长是否是由实际 EFA 传输延迟或其他问题（例如 CPU 瓶颈、内存争用或次优 NCCL 配置）引起的至关重要。通过检查 GPU 内核、NCCL 集合和 EFA bandwidth 利用率的相关时间线，从业人员可以查明性能瓶颈的根本原因，并验证网络结构是否以预期容量运行。

在本文中，我们以 Megatron-LM 和 NCCL GIN 和 DeepEP 为例演示了这种监控方法。 Megatron Bridge 基于配方的方法简化了 complex 训练配置的部署，使得更容易采用 DeepEP 和 NCCL GIN 等高级功能进行大规模 MoE 模型训练，同时保持对网络性能的完全可观察性。

有关完整的示例和脚本，请参阅此存储库中的 `megatron directory <https://github.com/crazyguitar/pysheeet/blob/master/src/megatron/>`_ 。

参考资料（References）
--------------------------------

.. [1] `AWS re:Invent 2024 - CMP335：深入分析分布式训练性能 <https://d1.awsstatic.com/onedam/marketing-channels/website/aws/en_US/events/approved/reinvent-2025/reinvent/2024/slides/cmp/CMP335_Drilling-down-into-performance-for-distributed-training.pdf>`_
