.. meta::
    :description lang=zh_CN: LLM 服务指南 — vLLM、SGLang 和 TensorRT-LLM，适用于 GPU 集群上的单节点、多节点 SLURM、tensor/管道/数据/专家并行性。
    :keywords: vLLM, SGLang, TensorRT-LLM, LLM serving, LLM inference, model serving, distributed inference, tensor parallelism, pipeline parallelism, data parallelism, expert parallelism, MoE serving, GPU inference, OpenAI compatible API, multi-node GPU, SLURM, HPC, EFA, NCCL, PagedAttention, RadixAttention, continuous batching, Docker, Qwen, Llama, DeepSeek

======================================
LLM 服务（LLM Serving）
======================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

本指南涵盖了使用三个高性能引擎的 LLM 推理服务：

- **vLLM** — 具有 PagedAttention 的高 throughput 推理引擎，可实现高效的 KV cache 内存管理、连续批处理以最大化 GPU 利用率，并优化 CUDA 内核。提供兼容 OpenAI 的 API 作为 OpenAI 服务的直接替代品。

- **SGLang** - 具有 RadixAttention 的快速推理引擎，可在具有共享提示的请求之间实现高效的前缀 caching。通过常见系统提示针对多轮对话和工作负载进行了优化。

- **TensorRT-LLM** — NVIDIA 的推理引擎，具有 PyTorch 后端、优化的 CUDA 内核和 FP8/INT4 量化。使用 ``trtllm-serve`` 进行 OpenAI 兼容服务。通过 YAML 配置支持 TP、PP、EP 和 attention DP。

所有支持跨多个 GPU 和节点的分布式推理，具有 tensor 并行性 (TP)、管道并行性 (PP)、数据并行性 (DP) 以及针对专家混合 (MoE) 模型的专家并行性 (EP)。本指南涵盖了从基本的单 GPU 部署到 SLURM 集群上的高级多节点分布式服务的所有内容。

脚本和示例：

- vLLM: `src/llm/vllm/ <https://github.com/crazyguitar/pysheeet/tree/master/src/llm/vllm>`_
- SGLang: `src/llm/sglang/ <https://github.com/crazyguitar/pysheeet/tree/master/src/llm/sglang>`_
- TensorRT-LLM： `src/llm/tensorrt-llm/ <https://github.com/crazyguitar/pysheeet/tree/master/src/llm/tensorrt-llm>`_

快速入门（Quick Start）
----------------------------------

只需几分钟即可开始。安装 package，启动服务器，并使用标准 HTTP 请求对其进行查询。两个引擎都公开了兼容 OpenAI 的 ``/v1/chat/completions`` 和 ``/v1/completions`` 端点。

**vLLM** （端口8000）：

.. code-block:: bash

    pip install vllm
    vllm serve Qwen/Qwen2.5-7B-Instruct --host 0.0.0.0 --port 8000

    curl -X POST http://localhost:8000/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{"model": "Qwen/Qwen2.5-7B-Instruct", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 50}'

**SGLang** （端口30000）：

.. code-block:: bash

    pip install "sglang[all]"
    python -m sglang.launch_server --model-path Qwen/Qwen2.5-7B-Instruct --host 0.0.0.0 --port 30000

    curl -X POST http://localhost:30000/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{"model": "Qwen/Qwen2.5-7B-Instruct", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 50}'

**TensorRT-LLM** （端口8000）：

.. code-block:: bash

    pip install tensorrt-llm
    trtllm-serve Qwen/Qwen2.5-7B-Instruct --host 0.0.0.0 --port 8000

    curl -X POST http://localhost:8000/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{"model": "Qwen/Qwen2.5-7B-Instruct", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 50}'

张量并行 (TP)（Tensor Parallel (TP)）
--------------------------------------------------------------

Tensor 并行性将各个模型层分割到多个 GPU 上，每个 GPU 保存一部分权重矩阵。所有 GPU 都参与每个前向传递，通过 all-reduce 操作进行通信。对于不适合单个 GPU 内存的型号至关重要。

**在以下情况下使用：** 模型不适合单个 GPU，或者您需要减少每个 GPU 内存。

.. code-block:: bash

    # vLLM
    vllm serve Qwen/Qwen2.5-14B-Instruct --tensor-parallel-size 8

    # SGLang
    python -m sglang.launch_server --model-path Qwen/Qwen2.5-14B-Instruct --tp 8

    # TensorRT-LLM
    trtllm-serve Qwen/Qwen2.5-14B-Instruct --tp_size 8

流水线并行（PP）（Pipeline Parallel (PP)）
------------------------------------------------------------------

管道并行性将模型划分为连续的阶段，每个阶段分配给不同的 GPU。与 tensor 并行性（所有 GPU 在每一层上工作）不同，管道并行性 processes 模型的不同部分在不同 GPU 上工作。这减少了通信开销，因为 GPU 仅在阶段之间传递激活。

**在以下情况下使用：** 您想要减少 GPU 之间的通信或跨互连速度较慢的节点进行扩展。

.. code-block:: bash

    # vLLM: PP=2 splits model into 2 stages, TP=4 within each
    vllm serve Qwen/Qwen2.5-14B-Instruct --tensor-parallel-size 4 --pipeline-parallel-size 2

    # SGLang
    python -m sglang.launch_server --model-path Qwen/Qwen2.5-14B-Instruct --tp 4 --pp 2

    # TensorRT-LLM
    trtllm-serve Qwen/Qwen2.5-14B-Instruct --tp_size 4 --pp_size 2

数据并行（DP）（Data Parallel (DP)）
--------------------------------------------------------

数据并行性创建模型的多个独立副本，每个副本同时处理不同的请求。当您有足够的 GPU 内存用于多个模型副本时，这是增加 throughput 的最有效方法。每个副本都可以在内部使用 tensor 并行性。

**使用时：** 您需要更高的要求 throughput 并且有足够的 GPU 来复制模型。

.. code-block:: bash

    # vLLM：2个副本，每个副本使用8个GPU
    vllm serve Qwen/Qwen2.5-14B-Instruct --tensor-parallel-size 8 --data-parallel-size 2

    # SGLang：多节点DP需要--enable-dp-attention
    python -m sglang.launch_server --model-path Qwen/Qwen2.5-14B-Instruct --tp 8 --dp 2 --enable-dp-attention

    # TensorRT-LLM: DP via multi-node with TP=8 per node
    trtllm-serve Qwen/Qwen2.5-14B-Instruct --tp_size 8

专家并行 (EP)（Expert Parallel (EP)）
--------------------------------------------------------------

专家并行性专为专家混合 (MoE) 模型而设计，其中该模型包含多个专家子网络，并且门控机制将令牌路由到不同的专家。 EP 在 GPU 上对专家进行分片，允许每个 GPU 保存一个专家子集。

**vLLM:** EP 自动计算 ( ``EP = DP × TP`` )。

**SGLang:** EP 是 TP 的细分。对于 ``--tp 8 --ep 2`` ，8 个 TP GPU 分为 2 个专家组，每个专家组有 4 个 GPU。

**TensorRT-LLM:** EP 细分 TP（与 SGLang 相同）。对于 ``--tp_size 8 --ep_size 2`` ，专家被分配到 2 组，每组 4 个 GPU。

.. code-block:: bash

    # vLLM: EP 自动计算
    vllm serve Qwen/Qwen3-30B-A3B-FP8 --tensor-parallel-size 8 --enable-expert-parallel

    # SGLang：EP细分TP
    python -m sglang.launch_server --model-path Qwen/Qwen1.5-MoE-A2.7B --tp 8 --ep 2

    # TensorRT-LLM：EP细分TP
    trtllm-serve Qwen/Qwen1.5-MoE-A2.7B --tp_size 8 --ep_size 2

并行度公式（Parallelism Formulas）
------------------------------------------------------

两个引擎使用相同的公式来计算 GPU 总需求：

.. code-block:: text

    Total GPUs = TP × PP × DP

专家并行性 (EP) 的处理方式有所不同：

- **vLLM** ：当 ``--enable-expert-parallel`` 为set时，自动计算EP（ ``EP = TP × DP`` ）。世界上所有 GPU 都会自动参与专家并行。
- **SGLang** ：EP 显式细分 TP。例如， ``--tp 8 --ep 2`` 将 8 个 TP GPU 分成 2 个专家组，每个专家组有 4 个 GPU。每个组处理不同的专家，而所有 8 个 GPU 仍对非专家层执行 tensor 并行性。
- **TensorRT-LLM** ：EP细分TP（与SGLang相同）。 ``--tp_size 8 --ep_size 2`` 将专家分为 2 组。约束： ``moe_tp × ep = tp_size`` 。

.. _distributed-serving-on-slurm:

SLURM上的分布式服务（Distributed Serving on SLURM）
------------------------------------------------------------------------------------

某些大型型号（e.g.、DeepSeek-V3、Llama-3.1-405B）可能不适合单个节点。所有三个引擎都支持使用不同并行策略（TP、PP、EP、DP）跨多个节点提供服务。多节点部署一开始可能会很棘手 - 下面的 ``run.sbatch`` 示例展示了如何将 ``salloc`` 与每个引擎一起使用，以便在 Slurm 上快速入门。这些脚本处理 Docker 映像到所有节点的分发、使用 EFA/GPU 直通的容器启动、工作人员协调和运行状况检查。服务器将一直运行，直到您使用 ``Ctrl+C`` 或 ``scancel`` 停止它为止。

**vLLM:**

.. code-block:: bash

    salloc -N 2 --gpus-per-node=8 --exclusive

    # MoE 具有专家并行性
    bash run.sbatch Qwen/Qwen3-30B-A3B-FP8 --tensor-parallel-size 8 --enable-expert-parallel

    # 密集的管道并行性
    bash run.sbatch deepseek-ai/DeepSeek-V2-Lite --tensor-parallel-size 8 --pipeline-parallel-size 2

**SG郎:**

.. code-block:: bash

    salloc -N 2 --gpus-per-node=8 --exclusive

    # Large model with TP=8 (uses 8 GPUs on first node)
    bash run.sbatch --model-path Qwen/Qwen2.5-72B-Instruct --tp 8

    # MoE with expert parallelism (TP=8, EP=2 across 2 nodes)
    bash run.sbatch --model-path Qwen/Qwen1.5-MoE-A2.7B --tp 8 --ep 2

**TensorRT-LLM:**

.. code-block:: bash

    salloc -N 2 --gpus-per-node=8 --exclusive

    # MoE 具有专家并行性
    bash run.sbatch /path/to/Qwen1.5-MoE-A2.7B --tp_size 8 --ep_size 2

    # 密集模型
    bash run.sbatch /path/to/Qwen2.5-14B-Instruct --tp_size 8

有关完整脚本选项，请参阅自述文件：

- `vLLM README <https://github.com/crazyguitar/pysheeet/blob/master/src/llm/vllm/README.rst>`_
- `SGLang README <https://github.com/crazyguitar/pysheeet/blob/master/src/llm/sglang/README.rst>`_
- `TensorRT-LLM README <https://github.com/crazyguitar/pysheeet/blob/master/src/llm/tensorrt-llm/README.rst>`_
