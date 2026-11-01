更多 GPU Ranks 下的 NCCL 多链路广播（NCCL Multi-Rail Broadcast with More GPU Ranks）
==================================================================================================================================================


摘要（Abstract）
------------------------

NCCL broadcast 用于在 `Slime`_ 等框架中同步训练工作器和 rollout 引擎之间的模型权重。但是，每个节点拥有多个 RDMA NIC 并不能保证 broadcast 会使用所有这些 NIC。在我们的单发送器设置中，权重传输仅使用源 GPU 的本地 NIC 对，从而使节点的大部分网络容量未使用。本说明比较了源节点上的 1 个和 8 个参与 GPU，两种情况下都有 8 个接收器，以显示rank 放置方式如何影响 NIC 利用率和权重转移 throughput。在两个 Cambrian H100 节点上，将源节点从 1 个 rank 扩展至 8 个 ranks，将 broadcast throughput 中位数从 47.86 增加到 290.17 GB/s，即一个 process 组内的 6.06x 加速。

介绍（Introduction）
--------------------------------

当一个节点有多个 RDMA NIC 时，很自然地期望大型 broadcast 使用它们组合的 bandwidth。然而，要达到 bandwidth，流量需要并行流经多个 NIC。在 NCCL 中，这些路径取决于参与的 GPU ranks、GPU 到 NIC 拓扑以及通信布局。下面的简化图说明了通过其本地网络连接的单个发送者 GPU broadcasting。在我们实验中使用的 Cambrian 节点上，该连接由两个 200 Gb/s 端口组成，由 NCCL 组合成一个 400 Gb/s 虚拟设备。问题是如何让其他 GPU 和 NIC 参与以使用更多节点的可用 bandwidth。

.. image:: /_static/appendix/nccl/nccl-broadcast-0.png
   :alt: 单个发送端 GPU 经由本地 NIC 向接收节点广播。

.. admonition:: 图例

   Node0 与 Node1 表示节点 0 和节点 1；GPU 与 NIC 后的数字为设备编号，A、B、C 为传输数据标识，箭头表示数据传输方向。

NCCL 的环 broadcast 将 buffer 分成块，并通过参与的 ranks将它们管道化。在节点内，这些传输可以使用快速 GPU 互连，例如 NVLink。在发送方节点上包含更多 GPU ranks可以为 NCCL 提供通过本地 GPU 及其附近 NIC 的额外路径。我们的第二种配置将两个节点上的所有 GPU rank 放置方式在单个 process 组中，如下所示。流量是否分布在多个NIC上取决于NCCL选择的拓扑和通道布局；仅仅增加 ranks并不能保证这一点。此配置不同于使用多个 process 组来分发传输。

.. image:: /_static/appendix/nccl/nccl-broadcast-8.png
   :alt: 多个发送端 GPU 和 NIC 共同传输广播数据块。

.. admonition:: 图例

   Node0 与 Node1 表示节点 0 和节点 1；GPU 与 NIC 后的数字为设备编号，A、B、C 为传输数据标识，箭头表示数据传输方向。


实验（Experiment）
----------------------------

环境（Environment）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **硬件：** 两个Cambrian 节点，每个节点配备8×NVIDIA H100 80GB GPU。
* **软件：** PyTorch 2.11.0+cu130、CUDA 13.0、NCCL 2.28.9、NVIDIA 驱动570.172.08。
* **基准：** 1 GiB BF16 broadcast，每个配置 300 秒。
* **NCCL：** 默认设置，与 ``NCCL_DEBUG=INFO`` 。

单发送者基线（Single-sender baseline）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

从每个节点上的存储库根运行这些命令。他们在节点 0 上启动一个发送方 process，在节点 1 上启动八个接收方 processes。将 Set ``MASTER_ADDR`` 发送到两个节点上的发送方节点地址，然后在每个节点上运行相应的命令。每个命令使用 ``--seconds 300`` 到 set 实验持续时间。

.. code-block:: bash

    # 第一个节点（节点等级 0）
    export OMP_NUM_THREADS=1
    torchrun --standalone \
      --nproc-per-node=1 src/nccl/broadcast.py \
      --node-rank 0 \
      --sender-ranks 1 \
      --master-addr ${MASTER_ADDR} \
      --seconds 300

    # 第二个节点（节点等级 1）
    export OMP_NUM_THREADS=1
    torchrun --standalone --nproc-per-node=8 \
      src/nccl/broadcast.py \
      --node-rank 1 \
      --sender-ranks 1 \
      --master-addr ${MASTER_ADDR} \
      --seconds 300

基线实现的中位数为 **47.86 GB/s** ，接近 400 Gb/s 端口对的 50 GB/s 原始线路速率。所有等级均通过有效载荷检查。

下图是早期的 `rdmatop`_ 捕获，说明流量集中在源 GPU 附近。对于此处报告的 Cambrian 运行，NCCL 的日志将源的虚拟设备识别为 ``mlx5_11`` 。 RDMA 计数器显示大量流量分布在这两个 200 Gb/s 端口上，而其余源节点端口实际上处于空闲状态。

.. image:: /_static/appendix/nccl/nccl-broadcast-0.gif
   :alt: RDMA NIC traffic on node 0 during the single-sender broadcast experiment.

.. admonition:: 图例

   Node0 与 Node1 表示节点 0 和节点 1；GPU 与 NIC 后的数字为设备编号，A、B、C 为传输数据标识，箭头表示数据传输方向。

源节点上的八个 Ranks（Eight ranks on the source node）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

对于第二种配置，在两个节点上启动八个 processes，并在两个命令上启动 set ``--sender-ranks 8`` 。有效负载大小、测量持续时间和 broadcast 源保持不变。

.. code-block:: bash

    # 第一个节点（节点等级 0）
    export OMP_NUM_THREADS=1
    torchrun --standalone --nproc-per-node=8 \
      src/nccl/broadcast.py \
      --node-rank 0 \
      --sender-ranks 8 \
      --master-addr ${MASTER_ADDR} \
      --seconds 300

    # 第二个节点（节点等级 1）
    export OMP_NUM_THREADS=1
    torchrun --standalone --nproc-per-node=8 \
      src/nccl/broadcast.py \
      --node-rank 1 \
      --sender-ranks 8 \
      --master-addr ${MASTER_ADDR} \
      --seconds 300

.. image:: /_static/appendix/nccl/nccl-broadcast-8.gif
   :alt: RDMA NIC traffic with eight participating GPU ranks on the source node.

.. admonition:: 图例

   Node0 与 Node1 表示节点 0 和节点 1；GPU 与 NIC 后的数字为设备编号，A、B、C 为传输数据标识，箭头表示数据传输方向。

结果（Results）
~~~~~~~~~~~~~~~~~~~~~~

两个实验均使用一个 NCCL process 组：

* **1 → 8：** 一组，包含 9 个 GPU ranks。
* **8 → 8：** 一组，包含 16 个 GPU ranks。

添加源节点排名将 broadcast throughput 中位数从 **47.86 GB/s 增加到 290.17 GB/s**，即**6.06x加速** 。这似乎违反直觉：通过更多 processes 传递数据会引入额外的传输。然而，在此设置中，通过 NVLink 在本地 GPU 之间分配数据允许 NCCL 并行使用更多 NIC。聚合网络 bandwidth 的收益超过了这些传输的成本。

.. list-table:: 1 GiB 有效负载的广播吞吐量（Broadcast throughput for a 1 GiB payload）
   :header-rows: 1
   :widths: 24 12 18 22 12

   * - 源节点排名
     - 接球手排名
     - 中值（GB/秒）
     - Range (GB/秒)
     - 加速比
   * - 1
     - 8
     - 47.86
     - 47.86–47.87
     - 1.00x
   * - 8
     - 8
     - 290.17
     - 282.12–290.39
     - 6.06x

结论（Conclusion）
----------------------------

在我们的实验中，在一个 process 组中包含更多源节点 GPU 允许 NCCL 并行使用更多 NIC。对于大负载，额外的网络 bandwidth 超过本地 GPU 传输的开销。这使得该方法对于批量传输非常有用，例如在 GRPO 期间同步训练工作人员和推出引擎之间的模型权重。


.. _Slime: https://github.com/THUDM/slime/blob/4c193f1f37509cca70f0e88807a9305b70f63f4e/slime/backends/megatron_utils/update_weight/update_weight_from_distributed.py#L348-L352

.. _rdmatop: https://github.com/crazyguitar/rdmatop
