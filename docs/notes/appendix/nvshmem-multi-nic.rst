.. meta::
    :description lang=zh_CN: NVSHMEM 3.6.5 对带有 AWS EFA 的 Libfabric 的多 NIC 支持：针对 MoE 和 DeepEP 工作负载的循环 NIC 选择
    :keywords: NVSHMEM, Multi-NIC, AWS, EFA, libfabric, DeepEP, MoE, round-robin, GPU, HPC, LLM, IBGDA, proxy thread

AWS EFA 上的 NVSHMEM Multi-NIC 支持（NVSHMEM Multi-NIC Support with AWS EFA）
==============================================================================================================================================

:Date: 2026-03-27

摘要（Abstract）
------------------------

`NVSHMEM 3.6.5 <https://github.com/NVIDIA/nvshmem/releases/tag/v3.6.5-0>`_ 为 libfabric transport 引入了 multi-NIC 支持，并采用 round-robin NIC 选择策略；这是 NVIDIA 与 Amazon Annapurna Labs 的合作成果。 `DeepEP <https://github.com/deepseek-ai/DeepEP>`_ 展示了使用 NVSHMEM 实现 MoE layer 的 dispatch 和 combine 操作能够显著提升采用 Mixture-of-Experts（MoE）架构的 LLM 性能，此后 NVSHMEM 受到广泛关注。不过，DeepEP 依赖 `InfiniBand GPUDirect Async <https://developer.nvidia.com/blog/improving-network-performance-of-hpc-systems-using-nvidia-magnum-io-nvshmem-and-gpudirect-async/>`_ （IBGDA），而 AWS GPU instances 只支持通过 libfabric 使用 proxy thread transport，因此在 AWS 上的兼容性受到限制。此外，3.6.5 之前的 NVSHMEM 仅支持单个 NIC，即每个 GPU 只能通过一个 EFA NIC 传输数据。本文介绍新的 multi-NIC 功能，并通过实验探索它在 AWS 上可能带来的性能提升。

介绍（Introduction）
--------------------------------

Mixture-of-Experts（MoE）架构依靠 all-to-all collective communication，在 expert replicas 之间 dispatch 和 combine tokens。不过，传统的 all-to-all 实现在 LLM 训练中常因与计算的重叠不足、bandwidth 利用率不佳而成为瓶颈。NVSHMEM 提供 device-side API，使开发者能够实现支持 GPU-initiated networking 的自定义 all-to-all kernels，例如 `pplx-kernels <https://github.com/perplexityai/pplx-kernels>`__ 和 `DeepEP <https://github.com/deepseek-ai/DeepEP>`__ ，从而消除代价高昂的 GPU–CPU context switches。

尽管有这些优点，但之前的 NVSHMEM 版本（3.6.5 之前）在 libfabric 传输上仅支持每个 GPU 一个 NIC。在配备多个EFA网卡的AWS instances上，这意味着基于NVSHMEM的MoE内核无法充分利用可用网络bandwidth，并且在实践中并没有优于普通all-to-all集体通信。

为了评估多 NIC 支持的影响，我们使用 NVSHMEM 器件 all-to-all 性能工具来比较单 NIC 和多 NIC 配置。我们还使用 benchmark `pplx-kernels <https://github.com/perplexityai/pplx-kernels>`__ 来评估 MoE 调度和合并操作是否受益于 libfabric 后端上的多个 NIC EFA。

NVSHMEM 设备端 All-to-All（NVSHMEM Device All-to-All）
--------------------------------------------------------------------------------------------------

为了验证多 NIC 循环是否正常运行，我们在 NVSHMEM 基准测试期间使用 `rdmatop <https://github.com/crazyguitar/rdmatop>`__ 监控所有 EFA NIC 上的 RDMA 流量。实验遵循 `rdmatop <https://github.com/crazyguitar/rdmatop/tree/main/examples/nvshmem>`__ 存储库中的 NVSHMEM 示例。

我们在 Slurm 集群上运行 NVSHMEM perftest 套件中的两个基准测试。第一个测量每个节点单个 GPU 之间的点对点放置 bandwidth，第二个测量每个节点所有 8 个 GPU 上设备启动的 all-to-all latency。

Put 带宽（跨节点，每节点一个 GPU）（Put Bandwidth (Inter-Node, 1 GPU per Node)）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在本实验中，我们启动了一个发送器和一个接收器的点对点作业，以验证单个 GPU 是否可以通过循环 NIC 选择充分利用所有可用的 EFA NIC。

.. code-block:: bash

    salloc -N 2 NTASKS_PER_NODE=1 \
      bash examples/nvshmem/nvshmem.sbatch \
      /opt/nvshmem/bin/perftest/device/pt-to-pt/shmem_put_bw \
      -b 8 -e 128M -f 2 -n 1000 -w 100

All-to-All 延迟（设备端，每节点使用全部八个 GPU）（All-to-All Latency (Device, All 8 GPUs per Node)）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

此实验使用 NVSHMEM 设备 all-to-all 性能工具来确定当每个节点的所有 8 个 GPU 参与时，all-to-all 通信是否可以使所有 EFA NIC 完全饱和。

.. code-block:: bash

    NODES=2 # 4, 8, 16
    salloc -N ${NODES} bash examples/nvshmem/nvshmem.sbatch \
      /opt/nvshmem/bin/perftest/device/coll/alltoall_latency \
      -b 16 -e 1G -f 2 -n 1000 -s all

pplx-kernels 的 All-to-All（pplx-kernels All-to-All）
----------------------------------------------------------------------------------------------------

为了评估实际的 MoE 工作负载是否受益于多 NIC 支持，我们使用 benchmark `pplx-kernels <https://github.com/ppl-ai/pplx-kernels>`__ \ — 一种基于 NVSHMEM 的 MoE 调度和组合操作的实现，用于 `vLLM <https://github.com/vllm-project/vllm>`_ 等生产服务系统中。该实验遵循 `rdmatop <https://github.com/crazyguitar/rdmatop/tree/main/examples/pplx>`__ 存储库中的 pplx 示例。

.. code-block:: bash

    salloc -N 2 bash examples/pplx/pplx.sbatch \
      python3 -m tests.bench_all_to_all

结果（Result）
--------------------

以下小节介绍了点对点放置 bandwidth 和设备 all-to-all latency 的结果，并将 NVSHMEM 3.5.21（单个 NIC）与 3.6.5（多个 NIC）进行比较。

Put 带宽（点对点）（Put Bandwidth (Point-to-Point)）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在点对点放置 bandwidth 实验中，NVSHMEM 3.5.21 对于 Tx 和 Rx，每个 GPU 仅使用一个 EFA NIC，如下面的 ``rdmatop`` 输出所示。这证实，在多 NIC 支持之前，每个 GPU 仅限于一个 NIC 的 bandwidth，无论 instance 上有多少可用。

.. image:: /_static/appendix/nvshmem/nvshmem-put-3.5.21.gif
   :alt: 本录屏保留原始终端命令、版本、测量值与输出。Size 为消息大小，Bandwidth 为带宽，Latency 为延迟；具体单位以终端输出为准。

.. admonition:: 图例

   本录屏保留原始终端命令、版本、测量值与输出。Size 为消息大小，Bandwidth 为带宽，Latency 为延迟；具体单位以终端输出为准。

对于 NVSHMEM 3.6.5，同一实验显示流量通过循环选择分布在所有 4 个 EFA NIC 上。这允许单个 GPU 聚合来自多个 NIC 的 bandwidth，从而显着增加可实现的点对点 throughput。

.. image:: /_static/appendix/nvshmem/nvshmem-put-3.6.5.gif
   :alt: 本录屏保留原始终端命令、版本、测量值与输出。Size 为消息大小，Bandwidth 为带宽，Latency 为延迟；具体单位以终端输出为准。

.. admonition:: 图例

   本录屏保留原始终端命令、版本、测量值与输出。Size 为消息大小，Bandwidth 为带宽，Latency 为延迟；具体单位以终端输出为准。

All-to-All 延迟（设备端）（All-to-All Latency (Device)）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在器件all-to-all实验中，NVSHMEM 3.5.21显示每个GPU仅利用单个NIC来传输数据，与上面的点对点结果一致。

.. image:: /_static/appendix/nvshmem/nvshmem-3.5.21.gif
   :alt: 本录屏保留原始终端命令、版本、测量值与输出。Size 为消息大小，Bandwidth 为带宽，Latency 为延迟；具体单位以终端输出为准。

.. admonition:: 图例

   本录屏保留原始终端命令、版本、测量值与输出。Size 为消息大小，Bandwidth 为带宽，Latency 为延迟；具体单位以终端输出为准。

通过 NVSHMEM 3.6.5、 ``rdmatop`` 确认所有 Tx NIC 都承载流量，证明多 NIC 循环在 all-to-all 操作期间处于活动状态。然而，我们观察到各个 NIC 的 Rx 流量不平衡。

.. image:: /_static/appendix/nvshmem/nvshmem-3.6.5.gif
   :alt: 本录屏保留原始终端命令、版本、测量值与输出。Size 为消息大小，Bandwidth 为带宽，Latency 为延迟；具体单位以终端输出为准。

.. admonition:: 图例

   本录屏保留原始终端命令、版本、测量值与输出。Size 为消息大小，Bandwidth 为带宽，Latency 为延迟；具体单位以终端输出为准。

出现这种不平衡的原因是所有PE同时计算相同的循环目标NIC，导致所有流量汇聚在相同的NIC上。 PR `libfabric：修复 EFA transport 的 multi-NIC RX 不均衡 <https://github.com/NVIDIA/nvshmem/pull/76>`_ 中提出了修复。应用修复后，我们可以观察到 all-to-all 实验中所有 NIC 上的 Rx 流量是平衡的。

.. image:: /_static/appendix/nvshmem/nvshmem-fix.gif
   :alt: 本录屏保留原始终端命令、版本、测量值与输出。Size 为消息大小，Bandwidth 为带宽，Latency 为延迟；具体单位以终端输出为准。

.. admonition:: 图例

   本录屏保留原始终端命令、版本、测量值与输出。Size 为消息大小，Bandwidth 为带宽，Latency 为延迟；具体单位以终端输出为准。

我们还将 NVSHMEM 3.5.21、NVSHMEM 3.6.5 和 NVSHMEM 3.6.5 的不同节点数的 all-to-all bandwidth 与 Rx 不平衡修复进行比较。应用修复后，throughput 明显高于其他两种配置。值得注意的是，如果没有修复，即使 NVSHMEM 3.6.5 使用多个 NIC 进行 Tx，Rx 不平衡也会成为瓶颈，导致 throughput 的性能可能低于单 NIC 模式，如 2 节点和 4 节点情况中所观察到的那样。

.. image:: /_static/appendix/nvshmem/nvshmem-all2all-bandwidth.png
   :alt: 各子图的 Nodes 表示节点数；横轴 Size 为消息大小（KiB），纵轴 Bus Bandwidth 为总线带宽（Gbps）。3.5.21、3.6.5 和 PR#76 为版本或补丁标识。

.. admonition:: 图例

   各子图的 Nodes 表示节点数；横轴 Size 为消息大小（KiB），纵轴 Bus Bandwidth 为总线带宽（Gbps）。3.5.21、3.6.5 和 PR#76 为版本或补丁标识。

pplx-kernels 的 All-to-All（pplx-kernels All-to-All）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

对于 NVSHMEM 3.6.5（没有 Rx 不平衡修复），所有 Tx 和 Rx NIC 均处于活动状态。尽管 Rx 流量略有不平衡，但 MoE 调度内核本身可能会在专家之间不均匀地分配令牌，从而导致不平衡。

.. image:: /_static/appendix/nvshmem/nvshmem-all2all-pplx-original.gif
   :alt: 本录屏保留原始终端命令、版本、测量值与输出。Size 为消息大小，Bandwidth 为带宽，Latency 为延迟；具体单位以终端输出为准。

.. admonition:: 图例

   本录屏保留原始终端命令、版本、测量值与输出。Size 为消息大小，Bandwidth 为带宽，Latency 为延迟；具体单位以终端输出为准。

使用 NVSHMEM 3.6.5 并应用 Rx 不平衡修复后，所有 Tx 和 Rx NIC 保持活动状态，并且 Rx 流量显得相对更加平衡。然而，MoE 调度和组合 bandwidth 与未修复版本相比没有显着差异。

.. image:: /_static/appendix/nvshmem/nvshmem-all2all-pplx.gif
   :alt: 本录屏保留原始终端命令、版本、测量值与输出。Size 为消息大小，Bandwidth 为带宽，Latency 为延迟；具体单位以终端输出为准。

.. admonition:: 图例

   本录屏保留原始终端命令、版本、测量值与输出。Size 为消息大小，Bandwidth 为带宽，Latency 为延迟；具体单位以终端输出为准。

比较这两种配置，应用 Rx 不平衡修复后，NVSHMEM bandwidth 相对较高。然而，其他因素（例如内核计算）可能会主导 MoE 内核的整体性能，从而导致两个版本之间的类似调度和组合 throughput。

.. image:: /_static/appendix/nvshmem/pplx_bandwidth.png
   :alt: Nodes 表示节点数；横轴 Tokens per Expert 为每个 Expert 的 Token 数，纵轴 Bandwidth 为带宽（Gbps）。Dispatch 为分发阶段，Combine 为合并阶段；baseline 为基线，E 为 Expert 数量，PR#76 为补丁标识。

.. admonition:: 图例

   Nodes 表示节点数；横轴 Tokens per Expert 为每个 Expert 的 Token 数，纵轴 Bandwidth 为带宽（Gbps）。Dispatch 为分发阶段，Combine 为合并阶段；baseline 为基线，E 为 Expert 数量，PR#76 为补丁标识。

结论（Conclusion）
----------------------------

NVSHMEM 3.6.5 引入了对 libfabric 传输的多 NIC 支持，从而在配备多个 EFA NIC 的 AWS instances 上启用循环 NIC 选择。我们的实验证实，此功能允许点对点和 all-to-all NVSHMEM 操作在所有可用 NIC 之间分配流量，与旧的 NVSHMEM 版本相比，显着增加了 bandwidth 的总流量。

然而，我们在最初的 3.6.5 版本中发现了 Rx 不平衡问题，其中所有 PE 同时选择相同的循环目标 NIC，导致 Rx 流量汇聚在单个 NIC 上。在某些配置中，这种不平衡可能会将 all-to-all throughput 降级至单 NIC 模式以下的水平。提议的修复通过偏移每个 PE 的循环选择来解决此问题，从而实现平衡的 Rx 流量并显着改进 all-to-all bandwidth。

对于 pplx-kernels，多 NIC 支持成功地在所有 EFA NIC 上分配流量。虽然 NVSHMEM 级别的 bandwidth 通过 Rx 修复得到改善，但端到端 MoE 调度和组合 throughput 显示出最小的差异，这表明内核计算而不是网络 bandwidth 是这些工作负载的主导因素。

总体而言，NVSHMEM 3.6.5 中的多 NIC 支持是实现基于 NVSHMEM 的 MoE 内核充分利用 AWS GPU instances 的网络容量的重要一步，并且可以潜在地提高MoE 内核 throughput，用于大规模 LLM 训练和服务工作负载。

参考资料（References）
--------------------------------

#. `NVSHMEM 3.6.5 Release <https://github.com/NVIDIA/nvshmem/releases/tag/v3.6.5-0>`__
#. `DeepEP：开源 EP 通信库 <https://github.com/deepseek-ai/DeepEP>`__
#. `pplx-kernels：基于 NVSHMEM 的 MoE kernels <https://github.com/ppl-ai/pplx-kernels>`__
#. `rdmatop: RDMA traffic monitoring tool <https://github.com/crazyguitar/rdmatop>`__
#. `libfabric：修复 EFA transport 的 multi-NIC RX 不均衡 <https://github.com/NVIDIA/nvshmem/pull/76>`__
#. `使用 NVIDIA Magnum IO NVSHMEM 与 GPUDirect Async 提升 HPC 系统网络性能 <https://developer.nvidia.com/blog/improving-network-performance-of-hpc-systems-using-nvidia-magnum-io-nvshmem-and-gpudirect-async/>`__
