.. meta::
    :description lang=zh_CN: LLM benchmark 套件 — 测量 throughput、TTFT、ITL、latency 的 vLLM、SGLang 和 TensorRT-LLM 服务性能。
    :keywords: LLM benchmark, vLLM benchmark, SGLang benchmark, TensorRT-LLM benchmark, serving benchmark, throughput, latency, TTFT, time to first token, ITL, inter-token latency, prefill, decode, concurrency, ShareGPT, GPU benchmark, tokens per second

==============================================
LLM 基准测试（LLM Benchmark）
==============================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

Benchmark 套件用于通过 vLLM、SGLang 和 TensorRT-LLM 测量 LLM 服务性能。所有这些都使用相似的方法——相同的测试类别、工作负载和指标——以便在三个推理引擎之间进行轻松比较。

- **vLLM：** ``vllm bench serve`` 通过 `bench.sh <https://github.com/crazyguitar/pysheeet/blob/master/src/llm/vllm/bench.sh>`__
- **SGLang:** ``python -m sglang.bench_serving`` 通过 `bench.sh <https://github.com/crazyguitar/pysheeet/blob/master/src/llm/sglang/bench.sh>`__
- **TensorRT-LLM:** ``python -m tensorrt_llm.serve.scripts.benchmark_serving`` 通过 `bench.sh <https://github.com/crazyguitar/pysheeet/blob/master/src/llm/tensorrt-llm/bench.sh>`__

脚本自动处理 Docker 图像加载和容器管理。如果 CLI 在主机上不可用，它们会加载 Docker 映像并在容器内重新执行。当在 SLURM 分配下运行时，它们使用 ``srun`` 调度到计算节点。

快速入门（Quick Start）
----------------------------------

在一台 terminal 中启动服务器，然后从另一台运行基准测试。 benchmark 脚本自动从服务器检测模型。

**vLLM:**

.. code-block:: bash

    # Terminal 1：启动服务器
    vllm serve Qwen/Qwen2.5-7B-Instruct --host 0.0.0.0 --port 8000

    # Terminal 2：运行基准测试
    bash bench.sh -H localhost -i vllm-serve:latest
    bash bench.sh -H localhost --type throughput,prefill

**SG郎:**

.. code-block:: bash

    # Terminal 1：启动服务器
    python -m sglang.launch_server --model-path Qwen/Qwen2.5-7B-Instruct --host 0.0.0.0 --port 30000

    # Terminal 2：运行基准测试
    bash bench.sh -H localhost -i sglang-serve:latest
    bash bench.sh -H localhost --type throughput,prefill

**TensorRT-LLM:**

.. code-block:: bash

    # Terminal 1：启动服务器
    trtllm-serve /path/to/Qwen2.5-7B-Instruct --host 0.0.0.0 --port 8000

    # Terminal 2：运行基准测试（需要 -m 进行分词器加载）
    bash bench.sh -H localhost -m /path/to/Qwen2.5-7B-Instruct -i tensorrt-llm-serve:latest
    bash bench.sh -H localhost -m /path/to/Qwen2.5-7B-Instruct --type throughput,prefill

带有 Slurm 的多节点（Multi-Node with Slurm）
------------------------------------------------------------------------

对于无法适应单个节点的大型模型（e.g.、DeepSeek-V3、Llama-3.1-405B）的基准测试，请参阅 `SLURM上的分布式服务（Distributed Serving on SLURM） <https://www.pythonsheets.com/notes/llm/llm-serving.html#distributed-serving-on-slurm>`__ 了解如何使用不同的并行策略部署多节点服务。服务器运行后，benchmark 使用 ``bench.sh`` ，如上面的快速入门所示。

吞吐量（Throughput）
------------------------------

通过使服务器充满请求来测量每秒的峰值输出令牌。使用 ``request-rate=inf`` 立即发送所有提示，强制调度程序积极批处理。这揭示了服务器在满负载下的最大throughput。

``512in/256out`` 是中等工作负载，它同时执行 prefill 阶段（处理输入）和 decode 阶段（生成令牌）。

.. code-block:: bash

    # vLLM
    vllm bench serve --dataset-name random --random-input-len 512 --random-output-len 256 \
        --num-prompts 100 --request-rate inf

    # SGLang
    python -m sglang.bench_serving --dataset-name random --random-input 512 --random-output 256 \
        --num-prompts 100 --request-rate inf

    # TensorRT-LLM
    python -m tensorrt_llm.serve.scripts.benchmark_serving \
        --dataset-name random --random-input-len 512 --random-output-len 256 \
        --num-prompts 100 --max-concurrency 100

预填充 (TTFT)（Prefill (TTFT)）
----------------------------------------------------

测量第一个令牌的时间 — 在生成第一个输出令牌之前，服务器 processes 输入提示的速度有多快。 ``output-len=1`` 将 prefill 与 decode 隔离，因为几乎所有计算都用于处理输入。

扫描输入长度（128→16K）揭示了 TTFT 如何随上下文大小缩放。 Prefill 每层计算量为 O(n)，因此 TTFT 应大致线性增长。 ``rate=4`` 使服务器保持轻负载，因此 TTFT 反映计算时间，而不是排队延迟。

.. code-block:: bash

    # vLLM - 扫描输入长度：128、512、2048、4096、16384
    vllm bench serve --dataset-name random --random-input-len $LEN --random-output-len 1 \
        --num-prompts 100 --request-rate 4

    # SGLang
    python -m sglang.bench_serving --dataset-name random --random-input $LEN --random-output 1 \
        --num-prompts 100 --request-rate 4

    # TensorRT-LLM
    python -m tensorrt_llm.serve.scripts.benchmark_serving \
        --dataset-name random --random-input-len $LEN --random-output-len 1 \
        --num-prompts 100 --max-concurrency 4

解码（ITL）（Decode (ITL)）
------------------------------------------

测量令牌间 Latency — 自回归生成过程中连续输出令牌之间的时间。 ``input-len=128`` 使 prefill 保持最小，因此 benchmark 专注于 decode 阶段。

扫描输出长度（128→1024）揭示了ITL如何随着KV cache的增长而变化。较长的序列会增加内存压力，并可能触发 PagedAttention 块分配或抢占。 ``rate=4`` 避免了批处理干扰，因此 ITL 反映了单个请求 decode 的速度。

.. code-block:: bash

    # vLLM - 扫描输出长度：128、256、512、1024
    vllm bench serve --dataset-name random --random-input-len 128 --random-output-len $LEN \
        --num-prompts 100 --request-rate 4

    # SGLang
    python -m sglang.bench_serving --dataset-name random --random-input 128 --random-output $LEN \
        --num-prompts 100 --request-rate 4

    # TensorRT-LLM
    python -m tensorrt_llm.serve.scripts.benchmark_serving \
        --dataset-name random --random-input-len 128 --random-output-len $LEN \
        --num-prompts 100 --max-concurrency 4

延迟 (E2E)（Latency (E2E)）
----------------------------------------------

测量最小负载下的端到端请求 latency — "single user" 体验。 ``rate=1`` 确保请求大部分单独处理，不进行批处理，从而给出基线最佳情况 latency（类似于 ChatGPT 风格的用法，其中一个用户等待完整响应）。

三种尺寸 classes（短/中/长）显示 latency 总数如何随请求尺寸变化。 E2E latency = TTFT + (output_tokens × ITL)。

.. code-block:: bash

    # vLLM - 测试短 (128/128)、中 (512/256)、长 (4096/512)
    vllm bench serve --dataset-name random --random-input-len $IN --random-output-len $OUT \
        --num-prompts 100 --request-rate 1

    # SGLang
    python -m sglang.bench_serving --dataset-name random --random-input $IN --random-output $OUT \
        --num-prompts 100 --request-rate 1

    # TensorRT-LLM
    python -m tensorrt_llm.serve.scripts.benchmark_serving \
        --dataset-name random --random-input-len $IN --random-output-len $OUT \
        --num-prompts 100 --max-concurrency 1

并发（Concurrency）
------------------------------

通过扫描并发请求数来查找服务器的饱和点。 ``request-rate=inf`` 和 ``max-concurrency=N`` 限制并行运行的请求数量，从而将到达率与并发性解耦。

在低并发 (1–4) 下，latency 很好，但 throughput 较低（GPU 未充分利用）。在高并发 (64–256) 下，throughput 处于稳定状态，latency 会降级（排队）。 throughput 停止改进的 "knee" 是最佳操作点 - 它告诉您服务器在质量下降之前可以处理多少并发用户。

.. code-block:: bash

    # vLLM - 扫描并发数：1、4、16、64、256
    vllm bench serve --dataset-name random --random-input-len 512 --random-output-len 256 \
        --num-prompts 100 --request-rate inf --max-concurrency $C

    # SGLang
    python -m sglang.bench_serving --dataset-name random --random-input 512 --random-output 256 \
        --num-prompts 100 --request-rate inf --max-concurrency $C

    # TensorRT-LLM
    python -m tensorrt_llm.serve.scripts.benchmark_serving \
        --dataset-name random --random-input-len 512 --random-output-len 256 \
        --num-prompts 100 --max-concurrency $C

ShareGPT 数据集（ShareGPT）
--------------------------------------------

来自具有 variable 输入/输出长度的真实用户对话的真实对话工作负载。与固定长度的随机数据集不同，ShareGPT 捕获实际 ChatGPT 对话中短提示和长提示的自然分布，使其成为生产聊天流量的最佳代理。

ShareGPT是vLLM CI使用的标准数据集， GPUStack 性能实验室， 以及大多数已发布的基准。 如果本地不存在该数据集，则会从 HuggingFace 自动下载。

.. code-block:: bash

    # vLLM - throughput 模式
    vllm bench serve --dataset-name sharegpt --dataset-path ShareGPT_V3_unfiltered_cleaned_split.json \
        --num-prompts 100 --request-rate inf

    # vLLM - 实际负载
    vllm bench serve --dataset-name sharegpt --dataset-path ShareGPT_V3_unfiltered_cleaned_split.json \
        --num-prompts 100 --request-rate 4

    # SGLang - throughput 模式
    python -m sglang.bench_serving --dataset-name sharegpt \
        --dataset-path ShareGPT_V3_unfiltered_cleaned_split.json \
        --num-prompts 100 --request-rate inf

    # TensorRT-LLM - throughput 模式
    python -m tensorrt_llm.serve.scripts.benchmark_serving \
        --dataset-name sharegpt --dataset-path ShareGPT_V3_unfiltered_cleaned_split.json \
        --num-prompts 100 --max-concurrency 100

Sonnet（前缀缓存）（Sonnet (Prefix Caching)）
--------------------------------------------------------------------------

十四行诗数据集使用莎士比亚的十四行诗，并在所有提示中使用共享前缀。此测试前缀 caching — 如果启用，则共享前缀 KV cache 计算一次并在请求之间重复使用，从而减少 TTFT。

.. code-block:: bash

    # 下载十四行诗数据集
    wget -q https://raw.githubusercontent.com/vllm-project/vllm/main/benchmarks/sonnet.txt

    # vLLM - prefill-重型（短输出隔离 prefill）
    vllm bench serve --dataset-name sonnet --dataset-path sonnet.txt \
        --sonnet-input-len 550 --sonnet-output-len 150 --sonnet-prefix-len 200 \
        --num-prompts 100 --request-rate inf

    # vLLM - 实际负载
    vllm bench serve --dataset-name sonnet --dataset-path sonnet.txt \
        --sonnet-input-len 550 --sonnet-output-len 150 --sonnet-prefix-len 200 \
        --num-prompts 100 --request-rate 4

ShareGPT 和 sonnet 均由 vLLM 团队的 `v0.6.0 performance blog <https://blog.vllm.ai/2024/09/05/perf-update.html>`__ 至 benchmark 服务引擎使用。要了解有关该方法的更多信息，请参阅 `reproduction steps <https://github.com/vllm-project/vllm/issues/8176>`__ 和 SGLang 的 `counter-benchmark <https://github.com/sgl-project/sglang/tree/main/benchmark>`__ ，其中使用 ``sglang.bench_serving`` 来比较两个引擎：

.. code-block:: bash

    # 启动服务器
    # vLLM 具有多步调度
    python -m vllm.entrypoints.openai.api_server \
        --model meta-llama/Llama-3.1-8B-Instruct \
        --disable-log-requests --num-scheduler-steps 10 --max_model_len 4096

    # SGLang
    python -m sglang.launch_server \
        --model-path meta-llama/Llama-3.1-8B-Instruct \
        --enable-torch-compile --disable-radix-cache

    # 在线benchmark（实际负载）
    python3 -m sglang.bench_serving --backend sglang --dataset-name sharegpt \
        --num-prompts 1200 --request-rate 4
    python3 -m sglang.bench_serving --backend vllm --dataset-name sharegpt \
        --num-prompts 1200 --request-rate 4

    # 离线 benchmark（最大 throughput）
    python3 -m sglang.bench_serving --backend sglang --dataset-name sharegpt \
        --num-prompts 5000
    python3 -m sglang.bench_serving --backend vllm --dataset-name sharegpt \
        --num-prompts 5000

关键指标（Key Metrics）
----------------------------------

- **TTFT** （第一个令牌的时间）：从请求到达到第一个生成令牌的时间。以 prefill 计算为主。越低越适合交互式使用。
- **ITL** （令牌间 Latency）：连续令牌之间的时间。体现decode的速度和一致性。
- **TPOT** （每个输出令牌的时间）：每个生成令牌的平均时间。与 ITL 类似，但对所有代币进行平均。
- **E2E Latency** ：从请求到完成的总时间。 E2E ≈ TTFT +（代币 × ITL）。
- **Throughput** ：所有请求的输出令牌/秒。对于批量工作负载来说越高越好。

CLI 差异（CLI Differences）
----------------------------------------------

.. list-table::
   :widths: 20 27 27 26
   :header-rows: 1

   * - Parameter
     - vLLM
     - SGLang
     - TensorRT-LLM
   * - 输入长度
     - ``--random-input-len``
     - ``--random-input``
     - ``--random-input-len``
   * - 输出长度
     - ``--random-output-len``
     - ``--random-output``
     - ``--random-output-len``
   * - 最大速率
     - ``--request-rate inf``
     - ``--request-rate inf``
     - ``--max-concurrency``
   * - 随机数据集
     - （默认工作）
     - （默认工作）
     - ``--random-ids --random-prefix-len 0``
   * - 型号旗
     - 自动检测
     - 自动检测
     - 需要 ``-m`` （标记器）
   * - 结果
     - ``--result-dir ./results``
     - ``--output-file ./results/out.json``
     - ``--result-dir ./results``

分析（Profiling）
--------------------------

Benchmark 运行可以与 profiling 结合使用，以将性能指标与 GPU 级跟踪关联起来。 vLLM 有两种 profiling 方法可用：

**PyTorch 分析器** — vLLM 的内置 profiler 通过 REST 端点触发。使用 ``--profile`` （或 ``--profiler-config`` ）启动服务器，然后将 ``--profile`` 传递给benchmark客户端以围绕工作负载调用 ``/start_profile`` 和 ``/stop_profile`` 。

.. code-block:: bash

    # 服务器 — 以启用 profiling 的方式启动
    bash run.sbatch --profile \
      Qwen/Qwen3-30B-A3B-FP8 \
      --tensor-parallel-size 8

    # 客户端 — benchmark 和 profiling
    bash bench.sh -H <server-host> --type throughput --profile

在 https://ui.perfetto.dev/ 查看跟踪（直接支持 ``.gz`` 文件）。

**Nsight Systems** — 将 ``vllm serve`` 与 ``nsys profile`` 包装在一起，用于 CUDA 内核、NVTX 和内存跟踪。与 ``--profiler-config '{"profiler": "cuda"}'`` 结合还可以捕获 vLLM 的内部 CUDA profiler 标记。

.. code-block:: bash

    # 服务器 — 启用 nsys + CUDA profiler (terminal 0)
    bash run.sbatch --nsys \
      Qwen/Qwen3-30B-A3B-FP8 \
      --tensor-parallel-size 8 \
      --enable-expert-parallel \
      --profiler-config '{"profiler": "cuda"}'

    # 客户端 — benchmark 和 profiling (terminal 1)
    bash bench.sh -H <server-host> --type throughput --profile

    # 使用 Ctrl+C (terminal 0) 停止服务器
    # Nsys 最终确定配置文件（约 30 秒）
    # Profile files: nsys-vllm/profile-node*.nsys-rep

使用 `Nsight Systems <https://developer.nvidia.com/nsight-systems>`_ 打开 ``.nsys-rep`` 文件。

有关完整的 ``run.sbatch`` 标志参考，请参阅 `vLLM Serving Guide <https://github.com/crazyguitar/pysheeet/blob/master/src/llm/vllm/README.rst>`_ ；有关更多详细信息，请参阅 `vLLM Profiling Guide <https://docs.vllm.ai/en/latest/contributing/profiling/>`_ 。

离线基准测试（Offline Benchmarking）
--------------------------------------------------------

vLLM 还支持离线基准测试来测量原始推理性能，而无需 API 服务器开销。这对于：

- 测量峰值 throughput 无网络/serialization 开销
- 多节点分布式推理测试
- Profiling 与 Nsight Systems 或 PyTorch profiler
- 使用自定义数据集进行测试（ShareGPT、随机提示）

有关完整的离线基准测试文档，请参阅 `vLLM Offline Benchmark Guide <https://github.com/crazyguitar/pysheeet/blob/master/src/llm/vllm/README.rst>`_ 。
