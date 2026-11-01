========================================
法学硕士服务（vLLM Serving）
========================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

此速查表提供了在本地（单节点）和 SLURM（多节点）环境中启动 vLLM 服务器的快速参考命令。它涵盖了构建 Docker 映像、使用不同的并行策略运行以及测试服务器端点。

有关更多详细信息，请参阅 `vLLM documentation <https://docs.vllm.ai/>`_ 和 `GitHub repository <https://github.com/vllm-project/vllm>`_ 。

有关 tensor 并行性、管道并行性、数据并行性和专家并行性的详细说明，请参阅并行策略和 benchmark 方法，请参阅 `LLM Serving Guide <https://github.com/crazyguitar/pysheeet/blob/master/docs/notes/llm/llm-serving.rst>`_ 和 `LLM Benchmark Guide <https://github.com/crazyguitar/pysheeet/blob/master/docs/notes/llm/llm-bench.rst>`_ 。

.. _build-docker-image:

构建 Docker 镜像（Build Docker Image）
----------------------------------------------------------------

Dockerfile 将 vLLM 与 EFA 驱动程序、NCCL、NVSHMEM 和 GDRCopy 捆绑在一起，以在 GPU 集群上进行高性能多节点推理。构建映像并将其保存为压缩 tarball，以便通过共享文件系统分发到 SLURM 节点。

.. code-block:: bash

    # 构建具有所有依赖项的 Docker 映像
    make docker

    # 保存为 SLURM 节点的压缩 tarball
    # 输出：vllm-服务-latest.tar.gz
    make save

.. _local-serving-single-node:

本地服务（单节点）（Local Serving (Single Node)）
----------------------------------------------------------------------------

对于开发或单节点部署，vLLM 可以直接在主机上或 Docker 容器内运行。服务器在端口 8000 上公开 OpenAI 兼容的 API。

**裸机** — 直接运行vLLM，无需Docker：

.. code-block:: bash

    # 单个 GPU — 服务模型的最简单方法
    vllm serve Qwen/Qwen2.5-7B-Instruct --host 0.0.0.0 --port 8000

    # Tensor 跨 8 个 GPU 并行 — 适用于对于单个 GPU 来说太大的模型
    vllm serve Qwen/Qwen2.5-14B-Instruct --tensor-parallel-size 8

**使用 Docker（通过 Makefile）** — 常见配置的便捷目标：

.. code-block:: bash

    # 单GPU 默认型号
    make single

    # Tensor 跨 8 个 GPU 并行
    make mp TP=8

    # Pipeline parallel — split model into 2 stages, each with TP=4
    make mp TP=4 PP=2

    # 具有数据并行性的 Ray 后端 — 2 个副本，每个副本使用 4 个 GPU
    make ray TP=4 DP=2

**使用 Docker（通过 run.sh）** — 入口点脚本支持多种服务模式（单一、ray、mp、rpc），并可显式控制并行设置：

.. code-block:: bash

    # 单GPU模式
    docker run --gpus all --rm --net=host -v /fsx:/fsx \
      vllm-serve:latest ./run.sh single --model Qwen/Qwen2.5-7B-Instruct

    # 具有 tensor 并行度的 Multiprocessing 模式
    docker run --gpus all --rm --net=host -v /fsx:/fsx \
      vllm-serve:latest ./run.sh mp --model Qwen/Qwen2.5-14B-Instruct --tp 8

.. _slurm-serving-multi-node:

SLURM 服务（多节点）（SLURM Serving (Multi-Node)）
----------------------------------------------------------------------------------

``run.sbatch`` 编排在 SLURM 集群上服务的多节点 vLLM。它处理 Docker 映像分发、使用 EFA/GPU 直通的容器启动、并行计算和运行状况检查。服务器会一直运行，直到您使用 ``Ctrl+C`` 或 ``scancel`` 停止它为止。

**脚本标志** — 这些由脚本使用，不会传递给 vLLM：

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - 旗帜
     - 描述
   * - ``--image PATH``
     - Docker 映像 tarball 或注册表路径（默认值： ``$WORKSPACE/vllm-serve-latest.tar.gz`` ）
   * - ``--workspace, -w PATH``
     - 默认图像和日志的基目录（默认： ``$PWD`` ）
   * - ``--container-mount PATH``
     - 绑定挂载到容器中的主机路径（默认值： ``/fsx`` ）
   * - ``--force, -f``
     - 加载前强制删除现有容器和镜像
   * - ``--nsys``
     - 启用 Nsight Systems profiling（写入 ``$WORKSPACE/nsys-vllm/`` ）

所有其他 arguments 均按原样直接传递到 ``vllm serve`` 。

**基本用法** — 使用 ``salloc`` 分配节点，然后运行脚本。该脚本自动检测 SLURM 分配并根据 GPU 总数和 TP/PP 计算 DP：

.. code-block:: bash

    # 分配 2 个节点，每个节点 8 个 GPU
    salloc -N 2 --gpus-per-node=8 --exclusive

    # Expert parallel for MoE models (TP=8, DP=2, EP=16 auto-computed)
    bash run.sbatch \
      Qwen/Qwen3-30B-A3B-FP8 \
      --tensor-parallel-size 8 \
      --enable-expert-parallel

**自定义映像** — 指定不同的 Docker 映像 tarball 或注册表路径：

.. code-block:: bash

    bash run.sbatch \
      --image /fsx/images/vllm-serve-latest.tar.gz \
      Qwen/Qwen3-30B-A3B-FP8 \
      --tensor-parallel-size 8 \
      --enable-expert-parallel

**管道并行** - 适用于需要跨节点拆分的大型密集模型。当 PP > 1 时，脚本自动选择 multiprocessing 后端：

.. code-block:: bash

    bash run.sbatch \
      deepseek-ai/DeepSeek-V2-Lite \
      --tensor-parallel-size 8 \
      --pipeline-parallel-size 2

**强制重新加载** — 在加载之前删除 cached 容器和图像：

.. code-block:: bash

    bash run.sbatch -f \
      Qwen/Qwen3-30B-A3B-FP8 \
      --tensor-parallel-size 8 \
      --enable-expert-parallel

**后端选择** — 该脚本支持三个分布式后端。 RPC 是默认值，最适合大多数情况。当您需要其调度功能时，Ray 非常有用。自动选择 Multiprocessing 以实现管道并行性：

.. code-block:: bash

    # RPC 后端（默认）——轻量级，最适合 DP + EP
    bash run.sbatch Qwen/Qwen3-30B-A3B-FP8 --tensor-parallel-size 8

    # Ray 后端 — 使用 Ray 集群进行工作人员管理
    DP_BACKEND=ray bash run.sbatch \
      Qwen/Qwen3-30B-A3B-FP8 \
      --tensor-parallel-size 8 \
      --enable-expert-parallel

    # Multiprocessing 后端 — 当 PP > 1 时自动选择
    bash run.sbatch \
      deepseek-ai/DeepSeek-V2-Lite \
      --tensor-parallel-size 8 \
      --pipeline-parallel-size 2

.. _test-the-server:

测试服务器（Test the Server）
--------------------------------------------

一旦服务器准备就绪，它就会打印头节点 IP 地址。使用标准 HTTP 请求与 OpenAI 兼容的 API 进行交互：

.. code-block:: bash

    # 健康检查 — 当服务器准备就绪时返回 200
    curl http://<HEAD_IP>:8000/health

    # List 可用型号
    curl http://<HEAD_IP>:8000/v1/models

    # 聊天完成请求
    curl -X POST http://<HEAD_IP>:8000/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{
        "model": "Qwen/Qwen3-30B-A3B-FP8",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 50
      }'

    # 或者运行附带的测试脚本
    bash test.sh

    # 针对远程服务器进行测试
    bash test.sh -H 10.0.128.193

    # 使用特定端口和型号进行测试
    bash test.sh -H 10.0.128.193 -p 8000 -m Qwen/Qwen3-30B-A3B-FP8

.. _benchmark:

基准（Benchmark）
--------------------------

``bench.sh`` 通过向正在运行的 vLLM 服务器发送请求来测量服务性能（throughput、TTFT、ITL、latency）。它自动处理 Docker 图像加载和容器管理。

.. code-block:: bash

    # 运行所有基准测试
    bash bench.sh -H 10.0.128.193 -i vllm-serve:latest

    # 运行特定基准测试
    bash bench.sh -H 10.0.128.193 -i vllm-serve:latest --type throughput,prefill

    # 通过生成文件
    make bench HOST=10.0.128.193
    make bench HOST=10.0.128.193 BENCH_TYPE=throughput,prefill

.. _sweep:

扫（Sweep）
----------------

``sweep.sh`` 通过为每个配置调用 ``sweep.sbatch`` 来运行预定义的扫描套件。每个套件都会启动自己的 ``vllm serve`` ，扫描 parameter，并收集结果。需要 GPU 访问权限。

.. code-block:: bash

    # 所有套件（速率、并发、输入、输出）
    bash sweep.sh -m Qwen/Qwen3-0.6B

    # 选择特定套房
    bash sweep.sh -m Qwen/Qwen3-30B-A3B-FP8 \
        -i vllm-serve:latest \
        --serve-cmd "vllm serve Qwen/Qwen3-30B-A3B-FP8 -tp 8 --enable-expert-parallel" \
        --type rate,input

    # 通过生成文件
    make sweep
    make sweep SWEEP_MODEL=Qwen/Qwen3-30B-A3B-FP8 SWEEP_TYPE=rate,concurrency

    # 显示 vllm 服务 stdout（模型加载、请求日志）——对于 debugging 非常有用
    bash sweep.sh -m Qwen/Qwen3-0.6B --show-stdout

    # Custom serve command — TP=2 with expert parallel, rate sweep only
    bash sweep.sh -m Qwen/Qwen1.5-MoE-A2.7B \
        --serve-cmd "vllm serve Qwen/Qwen1.5-MoE-A2.7B -tp 2 --enable-expert-parallel" \
        --type rate --show-stdout

可用套房：

- **rate** — 扫描请求率（1、2、4、8、16、32、inf）以查找饱和点
- **concurrency** — 扫描并发请求 (1–128) 以找到最佳批量大小
- **input** — 扫描输入长度 (128–16K) 以测量 TTFT 与上下文的缩放
- **output** — 随着 KV cache 的增长，扫描输出长度 (64–2048) 以测量 ITL

要直接控制扫描 parameters，请使用 ``sweep.sbatch`` 将所有参数传递给 ``vllm bench sweep serve`` ：

.. code-block:: bash

    # 自定义服务+替补命令
    bash sweep.sbatch -m Qwen/Qwen3-30B-A3B-FP8 \
        --serve-cmd "vllm serve Qwen/Qwen3-30B-A3B-FP8 -tp 8 --enable-expert-parallel" \
        --bench-cmd "vllm bench serve --model Qwen/Qwen3-30B-A3B-FP8 --dataset-name sharegpt" \
        --bench-params results/bench_params.json --show-stdout

有关每个 benchmark type 和指标的详细说明，请参阅 `LLM Benchmark Guide <https://github.com/crazyguitar/pysheeet/blob/master/docs/notes/llm/llm-bench.rst>`_ 。

.. _notes-and-limitations:

注意事项和限制（Notes and Limitations）
------------------------------------------------------------

**分析：**

vLLM 支持通过 ``--profiler-config`` 跟踪 PyTorch profiler。服务器必须在启用 profiling 的情况下启动，然后 benchmark 客户端通过 ``--profile`` 触发 ``/start_profile`` 和 ``/stop_profile`` 端点。

.. code-block:: bash

    # 服务器 — 以启用 profiling 的方式启动（默认写入 $PWD/vllm_profile）
    bash run.sbatch --profile \
      Qwen/Qwen3-30B-A3B-FP8 \
      --tensor-parallel-size 8

    # 服务器 — 自定义 profiler 配置
    bash run.sbatch \
      --profiler-config '{"profiler": "torch", "torch_profiler_dir": "/fsx/traces"}' \
      Qwen/Qwen3-30B-A3B-FP8 \
      --tensor-parallel-size 8

    # 客户端 — 使用 profiling 运行 benchmark
    bash bench.sh -H 10.0.128.193 --type throughput --profile

在 https://ui.perfetto.dev/ 查看跟踪（直接支持 ``.gz`` 文件）。

有关更多详细信息，请参阅 `vLLM Profiling Guide <https://docs.vllm.ai/en/latest/contributing/profiling/>`_ 。

**Nsight 系统 profiling:**

``--nsys`` 将 ``vllm serve`` 命令与 ``nsys profile`` 包装在一起，以进行 GPU 级别的跟踪（CUDA 内核、NVTX ranges、内存使用情况）。配置文件按节点保存到 ``$WORKSPACE/nsys-vllm/`` 。该脚本在清理时将 ``SIGINT`` 发送到 nsys 以顺利完成。

.. code-block:: bash

    # 服务器 — 启用 nsys + vLLM 的 CUDA profiler (terminal 0)
    bash run.sbatch --nsys \
      Qwen/Qwen3-30B-A3B-FP8 \
      --tensor-parallel-size 8 \
      --enable-expert-parallel \
      --profiler-config '{"profiler": "cuda"}'

    # 客户端 — 使用 profiling 运行 benchmark (terminal 1)
    bash bench.sh -H <server-host> --type throughput --profile

    # 使用 Ctrl+C (terminal 0) 停止服务器
    # Nsys 将最终确定配置文件（约 30 秒）
    # 配置文件：nsys-vllm/profile-node*.nsys-rep

使用 `Nsight Systems <https://developer.nvidia.com/nsight-systems>`_ 打开 ``.nsys-rep`` 文件或导出到 JSON 进行自定义分析。

**并行度约束：**

- vLLM 不支持同时组合 PP、TP 和 DP。使用 PP 模式时，DP 不可用（ ``TOTAL_GPUS = TP × PP`` ）。
- EP 和 PP 是互斥的。对于 MoE 模型使用 EP，对于大型密集模型使用 PP。
- EP 自动计算： ``EP = TP × DP = world_size`` 。随着 TP 的增加，DP 按比例减少以保持相同的总并行度。

**公式：**

- EP模式： ``TOTAL_GPUS = DP × TP`` 、EP由vLLM自动计算
- PP 模式： ``TOTAL_GPUS = TP × PP`` （无 DP）
- DP 模式： ``TOTAL_GPUS = DP × TP``


.. _offline-benchmarking:

离线基准测试（Offline Benchmarking）
--------------------------------------------------------

``offline_bench.sh`` 测量原始推理性能，无需 API 服务器开销。使用 ``torchrun`` 进行多节点协调，并支持profiling和Nsight Systems。

**单GPU：**

.. code-block:: bash

    bash offline_bench.sh \
      --model meta-llama/Llama-3.1-8B \
      --input-len 512 --output-len 128 \
      --num-prompts 100

**多 GPU 与 tensor 并行度：**

.. code-block:: bash

    salloc -N 1 bash offline_bench.sh \
      --model Qwen/Qwen2-57B-A14B \
      --tensor-parallel-size 4 --enable-expert-parallel \
      --input-len 1024 --output-len 256 \
      --num-prompts 100

    # 具有自定义 docker 映像的多节点
    salloc -N 4 bash offline_bench.sh \
      --image "$PWD/vllm-serve-latest.tar.gz" \
      --model Qwen/Qwen2-57B-A14B \
      --all2all-backend allgather_reducescatter \
      --tensor-parallel-size 4 --enable-expert-parallel \
      --gpu-memory-utilization 0.8 \
      --input-len 2048 --output-len 512 \
      --num-prompts 50

    # ShareGPT 数据集
    wget -O ShareGPT_V3_unfiltered_cleaned_split.json \
      https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered/resolve/main/ShareGPT_V3_unfiltered_cleaned_split.json

    bash offline_bench.sh \
      --model meta-llama/Llama-3.1-8B \
      --dataset-path ShareGPT_V3_unfiltered_cleaned_split.json \
      --num-prompts 100

**Nsight 系统 profiling:**

与上面的服务器工作流程类似， ``--nsys`` 用 ``nsys profile`` 包装 ``torchrun`` 命令（而不是 ``vllm serve`` ）。配置文件按节点保存到 ``$WORKSPACE/nsys-offline/`` 。

.. code-block:: bash

    salloc -N 4 bash offline_bench.sh --nsys \
      --model Qwen/Qwen2-57B-A14B \
      --tensor-parallel-size 4 --enable-expert-parallel \
      --all2all-backend allgather_reducescatter \
      --input-len 2048 --output-len 512 \
      --num-prompts 50
    # 配置文件：nsys-offline/profile-node*.nsys-rep

**VizTracer profiling（Python级跟踪）：**

VizTracer 是一个轻量级的 Python profiler，它可以跟踪 function 调用，而不会产生 PyTorch profiler 的内存开销。它可以在多节点/高数据并行设置下可靠地工作，其中 PyTorch profiler 可能会导致 OOM。使用 VizTracer 了解 Python 级别的执行流程并识别应用程序逻辑中的瓶颈。

.. code-block:: bash

    salloc -N 2 bash offline_bench.sh \
      --model Qwen/Qwen2-57B-A14B \
      --tensor-parallel-size 4 --enable-expert-parallel \
      --viztracer ./vllm-trace.json \
      --num-prompts 50
    # 在 https://ui.perfetto.dev/ 查看跟踪

**剖面比较：**

- **nsys** ：GPU内核级profiling（CUDA操作、内存传输、NCCL）
- **VizTracer** ：Python function级profiling（应用逻辑、调度）
- 使用nsys进行GPU性能分析，使用VizTracer进行Python代码分析
