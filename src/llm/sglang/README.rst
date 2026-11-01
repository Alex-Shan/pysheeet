==================================================
SGLang 服务（SGLang Serving）
==================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

此速查表提供了在本地（单节点）和 SLURM（多节点）环境中启动 SGLang 服务器的快速参考命令。它涵盖了构建 Docker 映像、使用不同的并行策略运行以及测试服务器。

有关更多详细信息，请参阅 `SGLang documentation <https://docs.sglang.ai/>`_ 和 `GitHub repository <https://github.com/sgl-project/sglang>`_ 。

有关并行策略和 benchmark 方法，请参阅 `LLM Serving Guide <https://github.com/crazyguitar/pysheeet/blob/master/docs/notes/llm/llm-serving.rst>`_ 和 `LLM Benchmark Guide <https://github.com/crazyguitar/pysheeet/blob/master/docs/notes/llm/llm-bench.rst>`_ 。

.. _build-docker-image:

构建 Docker 镜像（Build Docker Image）
----------------------------------------------------------------

Dockerfile 将 SGLang 与 EFA 驱动程序、NCCL 和 GDRCopy 捆绑在一起，以在 GPU 集群上进行高性能多节点推理。

.. code-block:: bash

    # 构建 Docker 映像
    make docker

    # 保存为 SLURM 节点的压缩 tarball
    # 输出：sglang-服务-latest.tar.gz
    make save

.. _local-serving-single-node:

本地服务（单节点）（Local Serving (Single Node)）
----------------------------------------------------------------------------

对于开发或单节点部署，SGLang 可以直接在主机上或 Docker 容器内运行。服务器在端口 30000 上公开 OpenAI 兼容的 API。

**裸机** — 直接运行SGLang，无需Docker：

.. code-block:: bash

    # 单GPU
    python -m sglang.launch_server --model-path Qwen/Qwen2.5-7B-Instruct --host 0.0.0.0 --port 30000

    # Tensor 跨 8 个 GPU 并行
    python -m sglang.launch_server --model-path Qwen/Qwen2.5-14B-Instruct --tp 8

    # 具有专家并行性的MoE模型（EP细分TP）
    python -m sglang.launch_server --model-path Qwen/Qwen1.5-MoE-A2.7B --tp 8 --ep 2

**使用 Docker（通过 Makefile）** ：

.. code-block:: bash

    # 单GPU 默认型号
    make serve MODEL=Qwen/Qwen2.5-7B-Instruct

    # Tensor 跨 8 个 GPU 并行
    make serve MODEL=Qwen/Qwen2.5-14B-Instruct TP=8

**直接使用Docker** ：

.. code-block:: bash

    # 单GPU
    docker run --gpus all --rm --net=host -v /fsx:/fsx \
      sglang-serve:latest \
      python3 -m sglang.launch_server --model-path Qwen/Qwen2.5-7B-Instruct --host 0.0.0.0 --port 30000

    # Tensor 跨 8 个 GPU 并行
    docker run --gpus all --rm --net=host -v /fsx:/fsx \
      sglang-serve:latest \
      python3 -m sglang.launch_server --model-path Qwen/Qwen2.5-14B-Instruct --tp 8 --host 0.0.0.0 --port 30000

.. _slurm-serving-multi-node:

SLURM 服务（多节点）（SLURM Serving (Multi-Node)）
----------------------------------------------------------------------------------

``run.sbatch`` 编排在 SLURM 集群上服务的多节点 SGLang。它处理 Docker 映像分发、使用 EFA/GPU 直通的容器启动以及运行状况检查。服务器会一直运行，直到您使用 ``Ctrl+C`` 或 ``scancel`` 停止它为止。

**Script flags** — 由脚本使用，不传递给 SGLang：

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - 旗帜
     - 描述
   * - ``--image PATH``
     - Docker 映像 tarball 或注册表路径（默认值： ``$WORKSPACE/sglang-serve-latest.tar.gz`` ）
   * - ``--workspace, -w PATH``
     - 默认图像和日志的基目录（默认： ``$PWD`` ）
   * - ``--container-mount PATH``
     - 绑定挂载到容器中的主机路径（默认值： ``/fsx`` ）
   * - ``--force, -f``
     - 加载前强制删除现有容器和镜像
   * - ``--profile``
     - 启用 PyTorch profiler（写入 ``$PWD/sglang_profile`` ）

所有其他 arguments 都直接传递到 ``python -m sglang.launch_server`` 。

**基本用法** ：

.. code-block:: bash

    # 分配 2 个节点，每个节点 8 个 GPU
    salloc -N 2 --gpus-per-node=8 --exclusive

    # MoE with expert parallelism (TP=8, EP=2 across 2 nodes)
    bash run.sbatch \
      --model-path Qwen/Qwen1.5-MoE-A2.7B \
      --tp 8 --ep 2

**数据并行性** — 多节点需要 ``--enable-dp-attention`` ：

.. code-block:: bash

    # TP=8, DP=2 (2 replicas across 16 GPUs)
    bash run.sbatch \
      --model-path Qwen/Qwen2.5-14B-Instruct \
      --tp 8 --dp 2 --enable-dp-attention

**管道并行度** ：

.. code-block:: bash

    # TP=8, PP=2
    bash run.sbatch \
      --model-path deepseek-ai/DeepSeek-V2-Lite \
      --tp 8 --pp 2

**自定义图像** ：

.. code-block:: bash

    bash run.sbatch \
      --image /fsx/images/sglang-serve-latest.tar.gz \
      --model-path Qwen/Qwen2.5-72B-Instruct \
      --tp 8

**分析** ：

.. code-block:: bash

    # PyTorch profiler
    bash run.sbatch --profile \
      --model-path Qwen/Qwen2.5-14B-Instruct \
      --tp 8

.. _test-the-server:

测试服务器（Test the Server）
--------------------------------------------

SGLang 默认服务于端口 30000：

.. code-block:: bash

    # 健康检查
    curl http://<HEAD_IP>:30000/health

    # List型号
    curl http://<HEAD_IP>:30000/v1/models

    # 聊天完成（兼容 OpenAI）
    curl -X POST http://<HEAD_IP>:30000/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{
        "model": "Qwen/Qwen2.5-14B-Instruct",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 50
      }'

    # SGLang 本机生成端点
    curl -X POST http://<HEAD_IP>:30000/generate \
      -H "Content-Type: application/json" \
      -d '{"text": "Hello", "sampling_params": {"max_new_tokens": 50}}'

    # 运行包含的测试脚本
    bash test.sh

    # 针对远程服务器进行测试
    bash test.sh -H 10.0.128.193 -p 30000

.. _benchmark:

基准（Benchmark）
--------------------------

``bench.sh`` 通过向正在运行的 SGLang 服务器发送请求来测量服务性能（throughput、TTFT、ITL、latency）。它自动处理 Docker 图像加载和容器管理。

.. code-block:: bash

    # 运行所有基准测试
    bash bench.sh -H 10.0.128.193 -i sglang-serve:latest

    # 运行特定基准测试
    bash bench.sh -H 10.0.128.193 -i sglang-serve:latest --type throughput,prefill

    # 通过生成文件
    make bench HOST=10.0.128.193
    make bench HOST=10.0.128.193 BENCH_TYPE=throughput,prefill

可用 benchmark types：

- **吞吐量** — 最大请求速率下的峰值输出令牌/秒
- **prefill** — TTFT 根据输入长度进行缩放（128→16K 令牌）
- **decode** — ITL 随着输出长度的增长（128→1024 个令牌）
- **latency** — 最小负载下的端到端 latency
- **concurrency** — 不同并发级别下的 throughput 与 latency
- **sharegpt** — 真实的对话工作负载

.. _parallelism:

并行性（Parallelism）
--------------------------------

SGLang的并行度公式：

.. code-block:: text

    Total GPUs = TP × DP × PP

**EP 是 TP** 的细分，而不是单独的乘法器。当使用 ``--ep N`` 时，TP GPU被分为N个专家并行组。

.. list-table::
   :widths: 20 10 10 10 10 40
   :header-rows: 1

   * - 配置
     - TP
     - EP
     - DP
     - PP
     - 使用案例
   * - 密集，最大 throughput
     - 2
     - 1
     - 8
     - 1
     - TP的8个副本=2
   * - 密集、大模型
     - 8
     - 1
     - 2
     - 1
     - TP=8 的 2 个副本
   * - 密集，非常大
     - 8
     - 1
     - 1
     - 2
     - 单副本、2 级管道
   * - MoE型号
     - 8
     - 2
     - 1
     - 1
     - 专家分为2组
   * - MoE, 更多EP
     - 8
     - 4
     - 1
     - 1
     - 专家分为4组

**约束：**

- 多节点DP需要 ``--enable-dp-attention``
- EP 仅适用于 MoE 型号，并且需要 ``--enable-ep``
- 对于多节点， ``TP`` 必须能被 ``nnodes`` 整除
