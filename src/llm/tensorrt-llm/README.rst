==========================================================================
TensorRT-LLM 服务（TensorRT-LLM Serving）
==========================================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

此速查表提供了在本地（单节点）和 SLURM 环境中启动 TensorRT-LLM 服务器的快速参考命令。它涵盖了构建 Docker 映像、使用不同的并行策略运行以及测试服务器。 TensorRT-LLM v1.1.0 使用 ``trtllm-serve`` 进行 OpenAI 兼容的在线服务，使用 ``trtllm-bench`` 进行基准测试。

有关更多详细信息，请参阅 `TensorRT-LLM documentation <https://nvidia.github.io/TensorRT-LLM/>`_ 和 `GitHub repository <https://github.com/NVIDIA/TensorRT-LLM>`_ 。

有关并行策略和 benchmark 方法，请参阅 `LLM Serving Guide <https://github.com/crazyguitar/pysheeet/blob/master/docs/notes/llm/llm-serving.rst>`_ 和 `LLM Benchmark Guide <https://github.com/crazyguitar/pysheeet/blob/master/docs/notes/llm/llm-bench.rst>`_ 。

.. _build-docker-image:

构建 Docker 镜像（Build Docker Image）
----------------------------------------------------------------

Dockerfile 将 TensorRT-LLM 与 EFA 驱动程序、NCCL 和 GDRCopy 捆绑在一起，以在 GPU 集群上进行高性能推理。

.. code-block:: bash

    # 构建 Docker 映像
    make docker

    # 保存为 SLURM 节点的压缩 tarball
    # 输出：tensorrt-llm-服务-latest.tar.gz
    make save

.. _local-serving-single-node:

本地服务（单节点）（Local Serving (Single Node)）
----------------------------------------------------------------------------

TensorRT-LLM 默认通过 ``trtllm-serve`` 在端口 8000 上公开 OpenAI 兼容的 API。

**裸机** — 直接运行（需要安装TensorRT-LLM）：

.. code-block:: bash

    # 单GPU
    trtllm-serve Qwen/Qwen2.5-7B-Instruct --host 0.0.0.0 --port 8000

    # Tensor 跨 8 个 GPU 并行
    trtllm-serve Qwen/Qwen2.5-14B-Instruct --tp_size 8

    # FP8 量化模型
    trtllm-serve nvidia/Qwen3-8B-FP8

**使用 Docker（通过 Makefile）** ：

.. code-block:: bash

    # 单GPU 默认型号
    make serve MODEL=Qwen/Qwen2.5-7B-Instruct

    # Tensor 跨 8 个 GPU 并行
    make serve MODEL=Qwen/Qwen2.5-14B-Instruct TP=8

**直接使用NGC容器** ：

.. code-block:: bash

    docker run --gpus all --rm --ipc host --net=host \
      --ulimit memlock=-1 --ulimit stack=67108864 \
      -v /fsx:/fsx \
      nvcr.io/nvidia/tensorrt-llm/release:1.1.0 \
      trtllm-serve Qwen/Qwen2.5-7B-Instruct --host 0.0.0.0 --port 8000

.. _slurm-serving:

SLURM 服务（SLURM Serving）
----------------------------------------------

``run.sbatch`` 负责协调 SLURM clusters 上的 TensorRT-LLM serving，处理 Docker image 分发、启用 EFA/GPU passthrough 的 container 启动及健康检查。服务器会持续运行，直到使用 ``Ctrl+C`` 或 ``scancel`` 停止它。

**Script flags** — 由脚本使用，不传递给 trtllm-serve：

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - 旗帜
     - 描述
   * - ``--image PATH``
     - Docker 映像 tarball 或注册表路径（默认值： ``$WORKSPACE/tensorrt-llm-serve-latest.tar.gz`` ）
   * - ``--workspace, -w PATH``
     - 默认图像和日志的基目录（默认： ``$PWD`` ）
   * - ``--container-mount PATH``
     - 绑定挂载到容器中的主机路径（默认值： ``/fsx`` ）
   * - ``--force, -f``
     - 加载前强制删除现有容器和镜像

所有其他 arguments 都直接传递到 ``trtllm-serve`` 。

**基本用法** ：

.. code-block:: bash

    # 分配1个节点8个GPU
    salloc -N 1 --gpus-per-node=8 --exclusive

    # Serve with TP=8
    bash run.sbatch \
      Qwen/Qwen2.5-14B-Instruct \
      --tp_size 8

**自定义图像** ：

.. code-block:: bash

    bash run.sbatch \
      --image /fsx/images/tensorrt-llm-serve-latest.tar.gz \
      Qwen/Qwen2.5-72B-Instruct \
      --tp_size 8

**FP8量化模型** ：

.. code-block:: bash

    bash run.sbatch nvidia/Qwen3-8B-FP8

.. _test-the-server:

测试服务器（Test the Server）
--------------------------------------------

TensorRT-LLM 默认服务于端口 8000：

.. code-block:: bash

    # 健康检查
    curl http://<HEAD_IP>:8000/health

    # List型号
    curl http://<HEAD_IP>:8000/v1/models

    # 聊天完成（兼容 OpenAI）
    curl -X POST http://<HEAD_IP>:8000/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{
        "model": "Qwen/Qwen2.5-14B-Instruct",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 50
      }'

    # 完成终点
    curl -X POST http://<HEAD_IP>:8000/v1/completions \
      -H "Content-Type: application/json" \
      -d '{
        "model": "Qwen/Qwen2.5-14B-Instruct",
        "prompt": "The capital of France is",
        "max_tokens": 20
      }'

    # 运行包含的测试脚本
    bash test.sh

    # 针对远程服务器进行测试
    bash test.sh -H 10.0.128.193 -p 8000

.. _benchmark:

基准（Benchmark）
--------------------------

``bench.sh`` 通过向正在运行的 TensorRT-LLM 服务器发送请求来测量服务性能（throughput、TTFT、ITL、latency）。它自动处理 Docker 图像加载和容器管理。

.. code-block:: bash

    # 运行所有基准测试
    bash bench.sh -H 10.0.128.193 -i tensorrt-llm-serve:latest

    # 运行特定基准测试
    bash bench.sh -H 10.0.128.193 -i tensorrt-llm-serve:latest --type throughput,prefill

    # 通过生成文件
    make bench HOST=10.0.128.193
    make bench HOST=10.0.128.193 BENCH_TYPE=throughput,prefill

可用 benchmark types：

- **吞吐量** — 最大请求速率下的峰值输出令牌/秒
- **prefill** — TTFT 根据输入长度进行缩放（128→4096 个令牌）
- **decode** — ITL 随着输出长度的增长（128→1024 个令牌）
- **latency** — 最小负载下的端到端 latency
- **concurrency** — 不同并发级别下的 throughput 与 latency
- **sharegpt** — 真实的对话工作负载

您还可以使用内置的 ``trtllm-bench`` CLI 进行更详细的基准测试：

.. code-block:: bash

    # 静态benchmark（无需服务器）
    trtllm-bench --model Qwen/Qwen2.5-7B-Instruct \
      --dataset-type synthetic --num-requests 100

.. _parallelism:

并行性（Parallelism）
--------------------------------

TensorRT-LLM 支持多种并行策略，通过与 ``--config`` 一起传递的 YAML 文件 ( ``parallel_config.yaml`` ) 进行配置：

- **Tensor Parallel (TP)** — 跨 GPU 分片模型权重
- **Pipeline Parallel (PP)** — 在 GPU 之间分配层
- **Data Parallel (DP)** — 针对不同请求跨 GPU 复制模型
- **Expert Parallel (EP)** — 跨 GPU 分配 MoE 专家
- **Context Parallel (CP)** — 跨 GPU 分配长上下文处理
- **Wide-EP** — 高级 EP，具有大规模 MoE 的负载平衡功能（DeepSeek-V3/R1、LLaMA4、Qwen3）

**注意力模块** 通过 ``enable_attention_dp`` 支持TP（小批量）或DP（大批量）。 **MoE FFN** 支持 TP、EP 或混合 ETP，其中 ``moe_tensor_parallel_size × moe_expert_parallel_size = tensor_parallel_size`` 。

.. list-table::
   :widths: 25 55 20
   :header-rows: 1

   * - 战略
     - 使用案例
     - Key配置
   * - 仅限 TP
     - 密集模型、小批量、内存受限
     - ``tensor_parallel_size: 8``
   * - PP
     - 不适合单节点 GPU 内存的超大型型号
     - ``pipeline_parallel_size: 2``
   * - DP (attention)
     - 大批量、高 throughput
     - ``enable_attention_dp: true``
   * - 仅 EP (MoE)
     - MoE 型号专家数量多
     - ``moe_expert_parallel_size: 8``
   * - 混合动力 ETP (MoE)
     - 平衡工作负载和内核效率
     - ``moe_tensor_parallel_size: 4, moe_expert_parallel_size: 2``
   * - 宽幅-EP (MoE)
     - 带负载均衡的大规模MoE（热专家复制）
     - 参见 ``examples/wide_ep/``

** 通过 YAML** 配置（推荐）：

.. code-block:: yaml

    # parallel_config.yaml

    # Dense model: TP=8
    tensor_parallel_size: 8

    # Dense model: TP=8 with attention DP
    # tensor_parallel_size：8
    # enable_attention_dp: true

    # MoE：仅 EP
    # tensor_parallel_size：8
    # moe_expert_parallel_size：8

    # MoE：混合动力 TP-4 × EP-2
    # tensor_parallel_size：8
    # moe_tensor_parallel_size：4
    # moe_expert_parallel_size：2

.. code-block:: bash

    trtllm-serve Qwen/Qwen2.5-14B-Instruct --config parallel_config.yaml

** 通过 CLI 标志 ** 的快速示例：

.. code-block:: bash

    # TP=4
    trtllm-serve Qwen/Qwen2.5-14B-Instruct --tp_size 4

    # TP=8, PP=2
    trtllm-serve Qwen/Qwen2.5-72B-Instruct --tp_size 8 --pp_size 2

    # MoE 与 EP
    trtllm-serve Qwen/Qwen1.5-MoE-A2.7B --tp_size 8 --ep_size 4

.. _key-differences-from-sglang-vllm:

与 SGLang / vLLM 的主要区别（Key Differences from SGLang / vLLM）
------------------------------------------------------------------------------------------------------------------

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 1

   * - 特征
     - TensorRT-LLM
     - SGLang
     - vLLM
   * - 发球指令
     - ``trtllm-serve <model>``
     - ``python -m sglang.launch_server``
     - ``vllm serve <model>``
   * - 默认端口
     - 8000
     - 30000
     - 8000
   * - TP 标志
     - ``--tp_size N``
     - ``--tp N``
     - ``--tensor-parallel-size N``
   * - 台式工具
     - ``trtllm-bench``
     - ``sglang.bench_serving``
     - ``vllm bench``
   * - 容器
     - ``nvcr.io/nvidia/tensorrt-llm/release``
     - 定制构建
     - 定制构建
   * - 量化
     - FP8、FP4、INT4 AWQ、INT8 SQ
     - FP8、AWQ、GPTQ
     - FP8、AWQ、GPTQ、位和字节
