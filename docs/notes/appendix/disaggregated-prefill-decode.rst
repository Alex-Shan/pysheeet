.. meta::
    :description lang=zh_CN: 评估在 AWS 上与 vLLM、NIXL 和 EFA 一起服务的 LLM 的分解 prefill/decode
    :keywords: LLM, vLLM, NIXL, disaggregated prefill decode, KV cache, EFA, inference serving

分离式 Prefill/Decode 是 LLM 服务的灵丹妙药吗？（Is Disaggregated Prefill/Decode a Silver Bullet for LLM Serving?）
========================================================================================================================================================================================================

:Date: 2026-03-10

摘要（Abstract）
------------------------

分解式 prefill/decode 作为 LLM 服务的一种有前途的架构而受到关注，它将计算密集型 prefill 阶段与内存绑定的 decode 阶段分离到专用节点组上。支持者认为，这种分离可以实现独立缩放并消除两相之间的干扰。但这真的是灵丹妙药吗？本文通过在 4 节点集群上的 AWS Elastic Fabric Adapter (EFA) 上使用 vLLM 和 NIXL 来评估分解的 prefill/decode，从而对这一说法进行了测试。我们将数据并行性和简单的负载平衡路由作为基准与分解配置进行比较。我们的结果表明，虽然分解极大地减少了令牌间 latency (ITL)，但它对 throughput 和首次令牌时间 (TTFT) 造成了巨大的成本，这表明该架构远非通用解决方案。

介绍（Introduction）
--------------------------------

在标准 LLM 服务中，每个节点处理 prefill 和 decode 传入请求。 prefill 阶段是计算限制的，processes 是并行的整个输入提示，而 decode 阶段是内存 bandwidth 限制并自回归生成令牌。当两个阶段共享相同的 GPU 池时，长 prefill 请求可能会阻止 decode 迭代，从而增加并发请求的令牌间 latency。

分解式 prefill/decode 通过将 prefill 和 decode 分配给单独的节点组来解决这种干扰。 prefill节点完成提示处理后，KV cache通过高bandwidth互连传输到decode节点。 NIXL [1]_ （NVIDIA Inference Xfer Library）提供 KV cache 传输机制，并且在 AWS 上，此传输使用 ``LIBFABRIC`` 后端在 EFA 上发生。

其吸引力很直观：通过将 decode 节点与 prefill 干扰隔离，代币生成应该以稳定、低 latency 的速度进行。然而，这种分离引入了新的成本 - KV cache 传输开销、长输入长度下的 prefill 节点饱和以及每个阶段有效集群容量的减少。问题是，与数据并行或无状态负载平衡路由等更简单的替代方案相比，这些权衡是否值得。

此实验使用 vLLM [2]_ 和 ``NixlConnector`` 来编排分类服务，并使用 ``vllm-router`` [3]_ 作为反向代理来跨节点组负载平衡请求。实验代码可在配套存储库的 `src/nixl <https://github.com/crazyguitar/pysheeet/tree/master/src/nixl>`_ 下找到。

容器镜像（Container Image）
------------------------------------------

该实验使用捆绑所有必需组件的自定义 Docker 映像。 ``Dockerfile`` 基于 ``nvidia/cuda:12.8.1-devel-ubuntu24.04`` 构建并安装以下 stack：

- **GDRCopy** v2.5.1 用于GPU-直接内存注册
- **EFA 安装程序** v1.47.0，用于 AWS 弹性结构适配器支持
- **UCX** v1.20.0 使用动词、rdmacm 和 EFA 传输构建
- **NIXL** v0.10.1 与 ``LIBFABRIC`` 后端用于 KV cache 传输
- **nixlbench** ，用于独立 NIXL bandwidth/latency 微基准测试
- **PyTorch**2.9.1、**flash-attn**2.8.1 和**DeepGEMM** v2.1.1.post3
- **vLLM** 0.15.1，支持 ``NixlConnector``
- **vllm-router** 用于跨分解节点组的负载平衡

图像通过 ``Makefile`` 构建并保存为便携式 tarball：

.. code-block:: bash

    make docker && make save

这会产生 ``nixl-latest.tar.gz`` ，在启动时通过 ``pigz`` 解压和 ``docker load`` 分发到所有 Slurm 节点。

服务脚本（Serving Script）
----------------------------------------

``vllm.sbatch`` 脚本协调在 Slurm 上提供服务的多节点 vLLM。它接受两个控制服务拓扑的 key 标志：

- ``--route R`` ：将分配的节点分成 ``R`` 相同的组，每个组运行一个独立的vLLM instance。头节点上的 ``vllm-router`` process 跨组循环请求。
- ``--prefill P`` ：在每个组内，将 ``P`` 节点分配为仅 prefill ( ``kv_producer`` )，将其余节点分配为仅 decode ( ``kv_consumer`` )。 KV cache 在 prefill 和 decode 节点之间的传输使用 ``NixlConnector`` 以及 EFA 上的 ``LIBFABRIC`` 后端。

当 ``--prefill 0`` （默认）时，组中的所有节点都运行标准数据并行服务。该脚本计算 ``DP = nodes_per_group * (8 / TP)`` 并相应地启动 vLLM 和 ``--data-parallel-size`` 。

对于分解模式，每个 prefill 和 decode 节点作为独立的 vLLM process 运行，并具有显式 KV 传输配置：

.. code-block:: bash

    # Prefill节点
    vllm serve ... \
        --kv-transfer-config.kv_connector NixlConnector \
        --kv-transfer-config.kv_role kv_producer \
        --kv-transfer-config.kv_connector_extra_config.backends+ LIBFABRIC

    # Decode节点
    vllm serve ... \
        --kv-transfer-config.kv_connector NixlConnector \
        --kv-transfer-config.kv_role kv_consumer \
        --kv-transfer-config.kv_connector_extra_config.backends+ LIBFABRIC

路由器对纯 DP 组使用 ``round_robin`` 策略，对 PD 组使用 ``consistent_hash`` 和 ``--vllm-pd-disaggregation`` ，将初始请求定向到 prefill 端点，并将后续 decode 流量定向到 decode 端点：

.. code-block:: bash

    # 纯 DP 组的路由器（跨组端点循环）
    vllm-router \
        --policy round_robin \
        --worker-urls http://<GROUP0_IP>:8000 http://<GROUP1_IP>:8001 \
        --host 0.0.0.0 --port 8010

    # 用于 PD 分解的路由器（hash 与 prefill/decode 分解一致）
    vllm-router \
        --policy consistent_hash \
        --vllm-pd-disaggregation \
        --prefill http://<PREFILL0_IP>:8000 \
        --decode http://<DECODE0_IP>:8001 --decode http://<DECODE1_IP>:8002 \
        --host 0.0.0.0 --port 8010

每个容器都使用 ``--privileged`` 、 ``--net=host`` 以及显式 ``/dev/infiniband/uverbs*`` 和 ``/dev/gdrdrv`` 设备安装来启动，以通过 EFA 启用 GPU-direct RDMA。

基准脚本（Benchmark Script）
--------------------------------------------

``bench.sh`` 脚本包装 ``vllm bench serve`` 并透明地处理 Docker 图像加载。如果 ``vllm`` CLI 在主机上不可用，则脚本会在容器内重新执行自身。它将 benchmark 客户端指向路由器端点（或单组配置的直接 vLLM 端点）：

.. code-block:: bash

    bash bench.sh -H <ROUTER_IP> -p <ROUTER_PORT> -- \
        --model /fsx/models/deepseek-ai/DeepSeek-V2-Lite \
        --dataset-name random \
        --random-input-len 512 --random-output-len 256 \
        --num-prompts 1024

实验配置（Experimental Setup）
------------------------------------------------

所有实验均在 4 个节点上运行，每个节点有 8 个 GPU (TP=8)，使用 DeepSeek-V2-Lite 作为模型。 benchmark 使用随机输入/输出数据，通过 ``vllm bench serve`` 提供 1024 个提示。

配置是：

- **基线（数据并行度）** ：4个节点，TP=8，DP=4。所有节点均服务于prefill和decode。这是标准的数据并行服务设置。
- **Route 2** ：2组，每组2个节点，TP=8，DP=每组2个。路由器对跨组的请求进行轮询。每个组独立处理 prefill 和 decode。
- **Route 4** ：4组，每组1个节点，TP=8，无数据并行。路由器将请求分发到所有 4 个独立节点。
- **PD 1P3D** ：分解的 prefill/decode，具有 1 个 prefill 节点和 3 个 decode 节点。 KV cache从prefill节点通过NIXL传输到decode节点。
- **PD 2P2D** ：分解的 prefill/decode，具有 2 个 prefill 节点和 2 个 decode 节点。

.. code-block:: bash

    # Exp 1: Baseline — 4 nodes, TP=8, pure DP
    salloc -N 4 bash vllm.sbatch \
        --model /fsx/models/deepseek-ai/DeepSeek-V2-Lite \
        --gpu-memory-utilization 0.9

    # Exp 2: 2 groups × 2 nodes, DP=2 per group, router round-robins
    salloc -N 4 bash vllm.sbatch --route 2 \
        --model /fsx/models/deepseek-ai/DeepSeek-V2-Lite \
        --gpu-memory-utilization 0.9

    # Exp 3：4组×1节点，无DP，路由器轮询
    salloc -N 4 bash vllm.sbatch --route 4 \
        --model /fsx/models/deepseek-ai/DeepSeek-V2-Lite \
        --gpu-memory-utilization 0.9

    # 经验 4：1 prefill + 3 decode
    salloc -N 4 bash vllm.sbatch --prefill 1 \
        --model /fsx/models/deepseek-ai/DeepSeek-V2-Lite \
        --gpu-memory-utilization 0.9

    # 经验 5：2 prefill + 2 decode
    salloc -N 4 bash vllm.sbatch --prefill 2 \
        --model /fsx/models/deepseek-ai/DeepSeek-V2-Lite \
        --gpu-memory-utilization 0.9

结果（Results）
----------------------

我们根据四个指标评估每个配置：输出令牌 throughput、请求 throughput、第一个令牌的时间 (TTFT) 和令牌间 latency (ITL)。每个图包含两个面板 - 左侧面板以 256 个标记的固定输出长度（prefill 主导的体系）扫描输入长度，而右侧面板以 512 个标记的固定输入长度（decode 主导的体系）扫描输出长度。这使我们能够观察当工作负载从 prefill-heavy 转移到 decode-heavy 时每种配置的行为方式。

微基准测试：KV Cache 传输带宽（Microbenchmark: KV Cache Transfer Bandwidth）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在检查端到端服务结果之前，我们使用 ``nixlbench`` 来测量两个节点之间通过 EFA 的原始 NIXL 传输 bandwidth。这确定了 KV cache 传输速度的上限，并有助于了解在分解配置中观察到的 TTFT 开销。

benchmark 在 Multi-GPU (MG) 模式下运行，每个节点的所有 8 个 GPU 通过 ``LIBFABRIC`` 后端执行 VRAM 到 VRAM 传输：

.. code-block:: bash

    salloc -N 2 bash nixl.sbatch --backend LIBFABRIC \
        --initiator_seg_type VRAM --target_seg_type VRAM \
        --mode MG --num_initiator_dev 8 --num_target_dev 8

    Block Size (B)      Batch Size     B/W (GB/Sec)   Avg Lat. (us)  P99 Tx (us)
    ---------------------------------------------------------------------------------
    4096                1              0.670064       6.1            47.0
    8192                1              1.315392       6.2            45.0
    16384               1              2.511416       6.5            47.0
    32768               1              4.820423       6.8            50.0
    65536               1              8.733224       7.5            56.0
    131072              1              12.341950      10.6           52.0
    262144              1              23.272188      11.3           59.0
    524288              1              43.365764      12.1           62.0
    1048576             1              74.816773      14.0           77.0
    2097152             1              121.086563     17.3           105.0
    4194304             1              180.631395     23.2           146.0
    8388608             1              239.037623     35.1           247.0
    16777216            1              289.500030     58.0           432.0
    33554432            1              327.436372     102.5          796.0
    67108864            1              349.608429     192.0          1724.0

**映射到 DeepSeek-V2-Lite KV cache 传输。**DeepSeek-V2-Lite 使用多头潜在 Attention (MLA)，它压缩KV cache 转化为每层每个标记的潜在向量。每个令牌每层 KV cache 大小为 ``(kv_lora_rank + qk_rope_head_dim) × dtype_size = (512 + 64) × 2 = 1,152 bytes`` 。对于跨 27 层的 512 个输入令牌，总 KV cache 约为**15.2 MB**。当 TP=8 时，每个 GPU 传输大约**1.9 MB** ，根据上表，该值落在 ~121 GB/s bandwidth range 内。如果没有 tensor 并行性，完整的 15.2 MB 传输可达到约 289 GB/s。

输出 Token 吞吐量（Output Token Throughput）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: /_static/appendix/nixl/throughput.png
    :alt: Output token throughput comparison

.. admonition:: 图例

   Without Expert Parallelism：未启用专家并行；Output Token Throughput：输出 Token 吞吐量（tok/s）。左图横轴 Input Length 为输入长度，固定 output_len=256；右图横轴 Output Length 为输出长度，固定 input_len=512。图例中 baseline 为基线，pd 为分离式部署，route 为路由方案；各曲线名称保留为实验配置标识。

左侧面板以 256 个令牌的固定输出长度（以 prefill 为主）改变输入长度，而右侧面板以 512 个令牌的固定输入长度（以 decode 为主）改变输出长度。

对于 prefill 为主的工作负载，Route 4 实现了最高的 throughput，因为每个节点独立运行，没有数据并行协调的开销。分解配置（PD 1P3D 和 PD 2P2D）在较短的输入长度下显示出具有竞争力的 throughput，但在较长的输入下性能下降，其中 prefill 节点成为瓶颈。

对于以 decode 为主的工作负载，Route 4 再次领先，其次是 PD 1P3D。 PD 2P2D 在该机制中显示出最低的 throughput，因为它的两个 decode 节点无法与其他配置的 decode 容量相匹配。

请求吞吐量（Request Throughput）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: /_static/appendix/nixl/req_throughput.png
    :alt: Request throughput comparison

.. admonition:: 图例

   Without Expert Parallelism：未启用专家并行；Request Throughput：请求吞吐量（req/s）。左图横轴 Input Length 为输入长度，固定 output_len=256；右图横轴 Output Length 为输出长度，固定 input_len=512。图例中 baseline 为基线，pd 为分离式部署，route 为路由方案；各曲线名称保留为实验配置标识。

请求 throughput 遵循类似的模式。 Route 4 在所有配置中始终满足最高要求 throughput。分解的 PD 1P3D 配置保持了对短输入的合理请求 throughput，但在较长的输入长度（4096 个令牌）下显着下降，其中单个 prefill 节点变得饱和。

首个 Token 延迟（TTFT）（Time to First Token (TTFT)）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: /_static/appendix/nixl/ttft.png
    :alt: TTFT comparison

.. admonition:: 图例

   Without Expert Parallelism：未启用专家并行；Mean TTFT：平均首个 Token 延迟（ms）。左图横轴 Input Length 为输入长度，固定 output_len=256；右图横轴 Output Length 为输出长度，固定 input_len=512。图例中 baseline 为基线，pd 为分离式部署，route 为路由方案；各曲线名称保留为实验配置标识。

TTFT 对于用户感知的 latency 至关重要。基线 DP 和路线 2 配置显示中等 TTFT，可随输入长度缩放。由于缺乏跨节点协调，路线 4 在所有输入长度上实现了最低的 TTFT。

分解配置表现出更高的 TTFT，特别是在较长的输入长度下。 PD 1P3D 显示 TTFT 在 4096 个输入令牌处超过 37 秒，因为所有 prefill 工作都通过单个节点进行。 PD 2P2D 对此进行了改进，但仍然落后于非分解配置。从 KV cache 传输到 NIXL 的额外 latency 有助于提高 TTFT。

对于 decode 主导的工作负载（右图），差异较小。在短输出长度（256–512 个令牌）下，PD 1P3D 显示 TTFT 比基线高 1–2 秒，因为 KV cache 传输开销按比例更显着。在较长的输出长度（1024+令牌）下，分解的配置与基线收敛或改进，因为基线在较重的并发 decode 负载下会受到 prefill/decode 争用的增加。

Token 间延迟（ITL）（Inter-Token Latency (ITL)）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: /_static/appendix/nixl/itl.png
    :alt: ITL comparison

.. admonition:: 图例

   Without Expert Parallelism：未启用专家并行；Mean ITL：平均 Token 间延迟（ms）。左图横轴 Input Length 为输入长度，固定 output_len=256；右图横轴 Output Length 为输出长度，固定 input_len=512。图例中 baseline 为基线，pd 为分离式部署，route 为路由方案；各曲线名称保留为实验配置标识。

ITL 测量 decode 阶段期间连续生成的令牌之间的 latency。这就是分类服务显示其主要优势的地方。

在 prefill 主导的体系中（左图），PD 1P3D 在所有输入长度上实现了最低的 ITL，在 4096 个输入令牌时，平均 ITL 低至 10 ms。通过隔离decode节点与prefill干扰，decode阶段不间断运行。与基线相比，PD 2P2D 还显示 ITL 有所减少，但由于 decode 节点较少，因此优势不太明显。基线 DP 和路由配置显示更高的 ITL，特别是在 prefill 和 decode 争夺相同 GPU 资源的较长输入长度时。

在 decode 主导的体系中（右图），路线 4 实现了最低的 ITL（~25–29 ms），因为每个节点独立服务，无需跨节点协调。在分解配置中，PD 1P3D 优于 PD 2P2D，因为它具有更大的 decode 容量（3 个 decode 节点 vs. 2 个节点），将 ITL 维持在 26–35 ms 左右。 PD 2P2D 仅具有 2 个 decode 节点，显示 ITL 与基线相当（~45–50 ms）。随着输出长度的增加，ITL 在所有配置中逐渐增加，反映了不断增长的 decode 负载。

讨论（Discussion）
----------------------------

那么，分解的 prefill/decode 是灵丹妙药吗？答案显然是否定的——至少在此处测试的条件下不是。所有基准测试都使用随机生成的提示，这意味着每个请求都会生成唯一的 KV cache，前缀 cache 命中率为零。这代表了分类服务的最坏情况，其中每个 prefill 必须从头开始计算，并且完整的 KV cache 必须通过网络传输。在具有共享系统提示或重复前缀的生产工作负载中，prefill 节点上的前缀 caching 可以大大减少冗余计算和传输量，从而有可能改变平衡以利于分解。即便如此，结果还是揭示了 set 的尖锐权衡，使得分解成为一种专门的工具，而不是一种普遍的改进：

- **ITL 获胜，但 throughput 取决于扩展** ：分解配置可显着降低代币间 latency — PD 1P3D 在长输入长度下实现低至 10 毫秒的 ITL，最多提高 14 倍比 prefill 主导体系中的基线更好，而 1.4–2.4× 在 decode 主导体系中更好。这里观察到的 throughput 和 TTFT 性能下降部分是固定 4 节点集群的产物：将节点专用于一个角色会使另一个角色挨饿。在实践中，prefill和decode池可以独立扩展——添加更多prefill节点以消除prefill瓶颈，或添加更多decode节点以增加代币throughput。面临的挑战是针对给定工作负载找到 prefill 和 decode 容量之间的正确比例，因为任何一方的过度配置都会增加成本，而不会带来相应的效益。

- **预填充瓶颈是一个硬约束** ：在固定集群大小的情况下，将节点专用于prefill会减少decode的容量，反之亦然。 PD 1P3D 在长输入长度下会遭受严重的 prefill 饱和（TTFT > 37s，4096 个令牌），而 PD 2P2D 的 decode 节点较少，限制了 decode throughput。 `NVIDIA Dynamo <https://github.com/ai-dynamo/dynamo>`_ 等框架旨在通过根据实时需求动态扩展 prefill 和 decode 池来解决此问题，但这会增加操作复杂性。

- **简单路由在吞吐量方面胜过分解** ：路线4（纯路由，无DP，无分解）通过完全消除跨节点同步，在所有配置中一致实现最高的throughput。它还在以 prefill 为主的工作负载中实现了最低的 TTFT，尽管 PD 1P3D 在以 decode 为主的体系中比 TTFT 略胜一筹，其中固定 512 个令牌输入足够短，足以避免 prefill 饱和。这是一个令人惊讶的强大基线 - 对于 ITL 不是主要问题的工作负载，无状态负载平衡独立节点的性能优于数据并行性和分解配置。

- **KV cache 传输不是免费的** ：EFA 上的 NIXL 传输在分解配置中将可测量的 latency 添加到 TTFT。对于较长的 decode 序列，此开销会被摊销，但对于较短的输出长度来说会很明显，使得分解对于短响应工作负载的吸引力较小。

总之，分解的 prefill/decode 旨在通过隔离两个阶段来优化 TTFT 和 ITL，但不能保证实现这些目标。 KV cache 通过网络传输会带来额外的开销，从而抵消 TTFT 的优势，特别是在传输量较大的长输入长度下。虽然由于消除了 decode 节点上的 prefill 干扰而持续观察到 ITL 的改进，但总体服务性能在很大程度上取决于 prefill 与 decode 的比率、工作负载特性和网络 bandwidth。考虑此架构的团队应在承诺增加的复杂性之前仔细分析其输入/输出长度分布、latency SLA 和 throughput 要求。

参考资料（References）
--------------------------------

.. [1] NVIDIA，"NIXL: NVIDIA Inference Xfer Library," GitHub，2025。https://github.com/ai-dynamo/nixl

.. [2] vLLM 项目，"vLLM: Easy, fast, and cheap LLM serving," GitHub，2024。https://github.com/vllm-project/vllm

.. [3] vLLM 项目，"vllm-router: Production-ready router for vLLM," GitHub，2025。https://github.com/vllm-project/router
