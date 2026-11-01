.. meta::
    :description lang=zh_CN: 适用于 HPC 环境的 Ray 集群速查表，涵盖 Slurm 上的集群设置、基于 Docker 的部署、使用 raytop 进行监控以及分布式工作负载
    :keywords: Ray, Ray cluster, HPC, Slurm, distributed computing, GPU cluster, raytop, monitoring, Docker, sbatch, machine learning, distributed training

======================================
Ray 集群（Ray Cluster）
======================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

`Ray <https://docs.ray.io/>`_ 是一个开源框架，用于跨集群扩展 Python 应用程序。它为分布式计算提供了简单的API，广泛用于分布式机器学习训练、强化学习、超参数调整和服务。在 HPC 环境中，Ray 集群通常使用 Docker 容器在 Slurm 托管节点之上启动，将 Slurm 的资源管理功能与 Ray 灵活的分布式运行时相结合。

本速查表涵盖了 Ray Python API、在 Slurm 上启动 Ray 集群、集群监控以及分布式 GPU 工作负载的实际部署示例。

连接到 Ray 集群（Connect to a Ray Cluster）
------------------------------------------------------------------------

Ray 使用三个默认端口：

- ``6379`` — GCS（全局控制存储），主集群协调端口
- ``8265`` — 仪表板和 REST API（由 ``ray job submit`` 和 ``raytop`` 使用）
- ``10001`` — Ray 客户端服务器（由 ``ray.init(address="ray://...")`` 使用）

.. code-block:: python

    import ray

    # 自动检测（在 Ray 容器内或通过 ray 作业提交提交）
    ray.init()

    # 直接通过GCS连接（端口6379）
    ray.init(address="<HEAD_IP>:6379")

    # 通过Ray客户端连接（端口10001）
    ray.init(address="ray://<HEAD_IP>:10001")

    # or set RAY_ADDRESS env var and just call ray.init()
    # export RAY_ADDRESS=<HEAD_IP>:6379

    # 检查可用资源
    print(ray.cluster_resources())
    # {'CPU'：192.0，'GPU'：16.0，...}

远程函数（Remote Functions）
--------------------------------------------

``@ray.remote`` 将 function 转变为分布式任务。使用 ``.remote()`` 提交并使用 ``ray.get()`` 收集结果。

.. code-block:: python

    import ray

    @ray.remote
    def add(a, b):
        return a + b

    # 并行提交任务
    futures = [add.remote(i, i) for i in range(4)]
    print(ray.get(futures))  # [0, 2, 4, 6]

    # 请求特定资源
    @ray.remote(num_gpus=1)
    def train_on_gpu(data):
        import torch
        device = torch.device("cuda")
        # ...

    # 请求多个 GPU
    @ray.remote(num_gpus=4, num_cpus=8)
    def train_large_model(config):
        ...

对象存储（Object Store）
------------------------------------

``ray.put()`` 将 objects 放置在共享 object 存储中，以便多个任务可以访问它们而无需重新序列化。这对于大型模型或数据集很有用。

.. code-block:: python

    import ray
    import numpy as np

    # 将一个大的 array 放入 object 存储中（返回一个 ObjectRef）
    data = np.random.rand(10000, 10000)
    data_ref = ray.put(data)

    @ray.remote
    def process(data_ref):
        data = ray.get(data_ref)  # 同一节点上的零拷贝读取
        return data.sum()

    # 所有任务共享相同的副本 - 无需重新 serialization
    futures = [process.remote(data_ref) for _ in range(4)]
    print(ray.get(futures))

``ray.wait()`` 用法（ ``ray.wait()`` ）
----------------------------------------------------------------------

``ray.wait()`` 返回已完成的期货，且不会阻止所有期货。对于在结果到达时对其进行处理很有用。

.. code-block:: python

    import ray

    @ray.remote
    def slow_task(i):
        import time
        time.sleep(i)
        return i

    futures = [slow_task.remote(i) for i in range(5)]

    # 等待至少2个结果，3秒后超时
    ready, not_ready = ray.wait(futures, num_returns=2, timeout=3.0)
    print(ray.get(ready))

    # process 完成后的结果
    while futures:
        ready, futures = ray.wait(futures, num_returns=1)
        print(f"Got: {ray.get(ready[0])}")

资源管理（Resource Management）
--------------------------------------------------

Ray公开集群资源信息，并支持部分GPU分配和自定义资源types以进行细粒度的调度控制。

.. code-block:: python

    import ray

    # 检查集群资源
    print(ray.cluster_resources())    # 全部的
    print(ray.available_resources())  # 目前免费

    # 部分 GPU（e.g.，2 个任务共享 1 GPU）
    @ray.remote(num_gpus=0.5)
    def light_inference(batch):
        ...

容错能力（Fault Tolerance）
------------------------------------------

对于长时间运行的分布式训练，Ray 可以自动重新启动崩溃的 Actor 并重试失败的任务，而无需停止整个作业。

.. code-block:: python

    import ray

    # 失败时自动重启 Actor 最多 3 次
    @ray.remote(num_gpus=1, max_restarts=3)
    class ResilientWorker:
        def __init__(self):
            self.setup_model()

        def setup_model(self):
            ...

        def train(self, batch):
            ...

    # 重试失败的任务最多 3 次
    @ray.remote(num_gpus=1, max_retries=3)
    def train_step(data):
        ...

运行时环境（Runtime Environments）
------------------------------------------------------

运行时环境允许您指定每个任务或每个参与者的依赖关系（pip packages、环境变量、工作目录），而无需将它们烘焙到容器中。

.. code-block:: python

    import ray

    # 每个任务运行时环境
    @ray.remote(runtime_env={"pip": ["torch==2.9.1"], "env_vars": {"NCCL_DEBUG": "INFO"}})
    def train():
        ...

    # 或 set（位于 ray.init）适用于所有任务
    ray.init(runtime_env={"working_dir": "/workspace", "pip": ["vllm==0.15.1"]})

Ray Actors 用法（Ray Actors）
--------------------------------------------------

演员是有状态的工作者。每个参与者都在自己的 process 中运行，并在 method 调用之间保持状态。

.. code-block:: python

    import ray

    @ray.remote(num_gpus=1)
    class Worker:
        def __init__(self, model_path):
            import torch
            self.model = torch.load(model_path)
            self.device = torch.device("cuda")

        def predict(self, batch):
            return self.model(batch.to(self.device))

    # 创建演员 instances
    workers = [Worker.remote("/fsx/model.pt") for _ in range(4)]

    # 拨打 methods
    futures = [w.predict.remote(data) for w, data in zip(workers, batches)]
    results = ray.get(futures)

归置组（Placement Groups）
------------------------------------------

归置组控制任务和参与者如何跨节点共置。这对于分布式训练至关重要，您需要将 GPU 工作线程固定到特定节点（e.g，每个带有 ``STRICT_PACK`` 的节点一个置放组）。

.. code-block:: python

    import ray
    from ray.util.placement_group import placement_group
    from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy

    ray.init()

    # 创建一个置放群组：8 个 GPU 打包在一个节点上
    pg = placement_group([{"GPU": 1} for _ in range(8)], strategy="STRICT_PACK")
    ray.get(pg.ready())

    # 将参与者安排在组内的特定捆绑包上
    @ray.remote(num_gpus=1)
    class GpuWorker:
        def run(self, rank):
            return f"rank {rank} on {ray.util.get_node_ip_address()}"

    workers = []
    for i in range(8):
        w = GpuWorker.options(
            scheduling_strategy=PlacementGroupSchedulingStrategy(
                placement_group=pg,
                placement_group_bundle_index=i,
            )
        ).remote()
        workers.append(w)

    futures = [w.run.remote(i) for i, w in enumerate(workers)]
    print(ray.get(futures))

多节点放置组（e.g.，用于跨 2 个节点的分布式训练）：

.. code-block:: python

    def create_placement_groups(num_nodes, gpus_per_node):
        """One placement group per node, each with gpus_per_node GPU bundles."""
        pgs = []
        for _ in range(num_nodes):
            bundles = [{"GPU": 1} for _ in range(gpus_per_node)]
            pg = placement_group(bundles, strategy="STRICT_PACK")
            ray.get(pg.ready())
            pgs.append(pg)
        return pgs

    # 2 nodes x 8 GPUs = 16 GPU workers
    pgs = create_placement_groups(num_nodes=2, gpus_per_node=8)

安置策略：

- ``STRICT_PACK`` — 同一节点上的所有包（分布式训练）
- ``PACK`` — 在最少节点上尽力打包
- ``STRICT_SPREAD`` — 每个节点一个捆绑包（容错）
- ``SPREAD`` — 尽最大努力跨节点传播

在 Ray 上部署 Megatron（Deploy Megatron on Ray）
------------------------------------------------------------------------------------

Ray 安置组可以替代 ``torchrun`` 来启动 Megatron 分布式训练。每个 Ray 参与者映射到一个 GPU 等级，放置组确保工作人员固定到正确的节点。以下示例跨 2 个节点（每个节点有 8 个 GPU）启动 DeepSeek-V2-Lite 预训练。来源： `raytop Megatron example <https://github.com/crazyguitar/raytop/tree/main/examples/megatron>`_ 。

.. code-block:: bash

    # 首先启动Ray集群：
    salloc -N 2 bash examples/ray/ray.sbatch --image /fsx/megatron-lm+latest.tar.gz

    # 然后从头容器内部：
    python3 main.py
    python3 main.py --hf-path /fsx/models/deepseek-ai/DeepSeek-V2-Lite
    python3 main.py --nodes 2 --gpus-per-node 8

.. code-block:: python

    #!/usr/bin/env python3
    """Launch Megatron Bridge DeepSeek-V2-Lite pretrain on a Ray cluster.

    Uses Ray placement groups to pin workers to nodes (same pattern as verl's
    Megatron backend). Each Ray actor = one GPU rank, calling
    torch.distributed.init_process_group() directly — no torchrun needed.
    """

    import argparse
    import os

    import ray
    from ray.util.placement_group import placement_group
    from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy

    EFA_ENV = {
        "FI_PROVIDER": "efa",
        "FI_EFA_USE_DEVICE_RDMA": "1",
        "FI_EFA_FORK_SAFE": "1",
        "NCCL_DEBUG": "WARN",
        "NCCL_BUFFSIZE": "8388608",
        "NCCL_P2P_NET_CHUNKSIZE": "524288",
        "CUDA_DEVICE_MAX_CONNECTIONS": "1",
        "OMP_NUM_THREADS": "1",
    }

    def build_config(hf_path=None):
        from megatron.bridge.recipes.deepseek.deepseek_v2 import (
            deepseek_v2_lite_pretrain_config,
        )

        cfg = deepseek_v2_lite_pretrain_config(
            **({"hf_path": hf_path} if hf_path else {}),
            tensor_model_parallel_size=8,
            pipeline_model_parallel_size=1,
            expert_model_parallel_size=2,
            sequence_parallel=True,
            seq_length=4096,
            train_iters=500,
            global_batch_size=64,
            micro_batch_size=1,
            eval_interval=100,
            lr_warmup_iters=50,
            save_interval=0,
        )
        cfg.model.moe_permute_fusion = False
        return cfg

    @ray.remote(num_cpus=0, num_gpus=1)
    class Worker:
        def run(self, rank, local_rank, world_size, master_addr, master_port, hf_path):
            # 必须重置 CUDA_VISIBLE_DEVICES BEFORE 任何 torch/CUDA 导入
            gpu_ids = ray.get_gpu_ids()
            cuda_device = int(gpu_ids[0]) if gpu_ids else local_rank
            os.environ.pop("CUDA_VISIBLE_DEVICES", None)

            os.environ.update(EFA_ENV)
            os.environ.update(
                {
                    "RANK": str(rank),
                    "LOCAL_RANK": str(cuda_device),
                    "WORLD_SIZE": str(world_size),
                    "MASTER_ADDR": master_addr,
                    "MASTER_PORT": str(master_port),
                }
            )

            import megatron.core.jit as _jit

            if not hasattr(_jit, "disable_jit_fuser"):
                _jit.disable_jit_fuser = lambda: None

            from megatron.bridge.training.gpt_step import forward_step
            from megatron.bridge.training.pretrain import pretrain

            cfg = build_config(hf_path)
            pretrain(config=cfg, forward_step_func=forward_step)

    def create_placement_groups(num_nodes, gpus_per_node):
        """Create one placement group per node, each with gpus_per_node GPU bundles."""
        pgs = []
        for _ in range(num_nodes):
            bundles = [{"GPU": 1} for _ in range(gpus_per_node)]
            pg = placement_group(bundles, strategy="STRICT_PACK")
            ray.get(pg.ready())
            pgs.append(pg)
        return pgs

    def resolve_master_and_sort_pgs(pgs):
        """Resolve node IPs for each PG, sort by IP, return (sorted_pgs, master_addr)."""

        @ray.remote(num_cpus=0)
        def _get_ip():
            return ray.util.get_node_ip_address()

        ip_futures = []
        for pg in pgs:
            ref = _get_ip.options(
                scheduling_strategy=PlacementGroupSchedulingStrategy(
                    placement_group=pg,
                    placement_group_bundle_index=0,
                )
            ).remote()
            ip_futures.append(ref)

        ips = ray.get(ip_futures)
        pg_ip_pairs = sorted(zip(pgs, ips), key=lambda x: x[1])
        sorted_pgs = [p for p, _ in pg_ip_pairs]
        master_addr = pg_ip_pairs[0][1]
        return sorted_pgs, master_addr

    def main():
        parser = argparse.ArgumentParser()
        parser.add_argument("--hf-path", default="deepseek-ai/DeepSeek-V2-Lite")
        parser.add_argument("--nodes", type=int, default=2)
        parser.add_argument("--gpus-per-node", type=int, default=8)
        parser.add_argument("--master-port", type=int, default=29500)
        args = parser.parse_args()

        world_size = args.nodes * args.gpus_per_node

        ray.init()
        pgs = create_placement_groups(args.nodes, args.gpus_per_node)
        sorted_pgs, master_addr = resolve_master_and_sort_pgs(pgs)

        # 每个 GPU 生成一名工作人员，固定到安置组
        futures = []
        rank = 0
        for pg in sorted_pgs:
            for local_rank in range(args.gpus_per_node):
                worker = Worker.options(
                    scheduling_strategy=PlacementGroupSchedulingStrategy(
                        placement_group=pg,
                        placement_group_bundle_index=local_rank,
                    )
                ).remote()
                futures.append(
                    worker.run.remote(
                        rank, local_rank, world_size,
                        master_addr, args.master_port, args.hf_path,
                    )
                )
                rank += 1

        ray.get(futures)


    if __name__ == "__main__":
        main()

在 Slurm 上启动 Ray 集群（Launch a Ray Cluster on Slurm）
--------------------------------------------------------------------------------------------------

以下 sbatch 脚本跨 Slurm 托管节点在 Docker 容器内配置 Ray 集群。它在第一个分配的节点上启动 Ray 头，并在所有剩余节点上启动 Ray 工作器，然后等待，直到每个节点都在集群中注册。

.. code-block:: bash

    # 分配节点并交互启动
    salloc -N 2 bash ray.sbatch

    # 作为批处理作业提交
    sbatch -N 2 ray.sbatch

    # 使用自定义容器镜像
    sbatch -N 4 ray.sbatch --image /fsx/ray+latest.tar.gz

该脚本通过 ``ray status`` 处理图像加载（tarball 或注册表拉取）、head/worker 启动和运行状况检查。完整脚本请参见 ``src/ray/ray.sbatch`` 。

Ray 集群状态（Ray Cluster Status）
--------------------------------------------------------

.. code-block:: bash

    # 从头节点检查集群状态
    docker exec ray-head ray status

    # 从容器内部检查
    ray status

    # 通过 REST API 获取集群信息
    curl http://${HEAD_IP}:8265/api/cluster_status

    # list 节点通过 REST API
    curl http://${HEAD_IP}:8265/api/v0/nodes

    # list 正在运行的作业
    curl http://${HEAD_IP}:8265/api/jobs/

Ray 仪表板（Ray Dashboard）
--------------------------------------------

Ray 在头节点的 ``8265`` 端口上提供内置 Web 仪表板。当在防火墙后面的 HPC 集群上运行时，使用 SSH 端口转发来访问它：

.. code-block:: bash

    # 将 Ray 仪表板转发到本地计算机
    ssh -L 8265:${HEAD_IP}:8265 login-node

    # 然后在浏览器中打开
    # http://localhost:8265

使用 Raytop 进行监控（Monitoring with raytop）
----------------------------------------------------------------------------

`raytop <https://github.com/crazyguitar/raytop>`_ 是用于 Ray 集群的实时 TUI 监视器，就像用于分布式 GPU 训练的 ``htop`` 一样。它通过 Prometheus 指标提供集群范围资源利用率的统一视图，包括 CPU、GPU、内存、每个节点故障、每个 GPU 利用率、正在运行的作业状态和实时参与者计数。

原文使用以下 cargo 命令安装。若 registry 中的包不可用，请参阅 `raytop 安装说明 <https://github.com/crazyguitar/raytop>`_；此处保留原命令：

.. code-block:: bash

    cargo install raytop

将 ``raytop`` 指向 Ray 仪表板端点：

.. code-block:: bash

    raytop --master http://${HEAD_IP}:8265

``raytop`` 从多个 Ray APIs 检索数据：

- ``/api/cluster_status`` — 集群范围内的 CPU/GPU/内存分配
- ``/api/v0/nodes`` — 每个节点的信息和状态
- ``/api/prometheus/sd`` — 实时每个 GPU 利用率和 GRAM 使用情况
- ``/api/jobs/`` — 正在运行的作业
- ``/api/v0/actors`` — 每个节点的参与者计数

使用 ``j`` / ``k`` 或箭头 keys 导航节点，使用 ``Enter`` 打开详细信息面板，使用 ``Tab`` 在作业和节点之间切换焦点，使用 ``t`` 循环主题，使用 ``q`` 退出。

为了监控长时间运行的分布式训练作业（e.g.、版本 RLHF、Megatron 预训练）， ``raytop`` 提供了一种快速方法来验证所有节点是否处于活动状态、GPU 是否得到充分利用以及没有 Actor 崩溃，而无需在浏览器中打开 Ray 仪表板。

提交 Ray 作业（Submit a Ray Job）
------------------------------------------------------

sbatch脚本在最后打印出Ray头地址：

.. code-block:: bash

    # sbatch 脚本在成功时打印此内容：
    # [info] Ray 集群已在 <HEAD_IP>:<RAY_PORT> 处就绪

    # 或者从头容器内部查询它
    docker exec ray-head ray status

    # 或者检查Slurm作业输出日志
    cat slurm-<JOB_ID>.out | grep "Ray cluster ready"

使用 ``ray job submit`` 提交作业：

.. code-block:: bash

    RAY_HEAD=http://<HEAD_IP>:8265

    # 提交工作
    ray job submit --address ${RAY_HEAD} -- python train.py

    # 提交 Megatron 示例
    ray job submit --address ${RAY_HEAD} \
        --runtime-env-json='{"working_dir": "/workspace"}' \
        -- python main.py --nodes 2 --gpus-per-node 8

    # 使用运行时环境提交
    ray job submit --address ${RAY_HEAD} \
        --runtime-env-json='{"working_dir": "/workspace"}' \
        -- python train.py

    # list 的职位
    ray job list --address ${RAY_HEAD}

    # 检查工作状态
    ray job status --address ${RAY_HEAD} JOB_ID

    # 获取作业日志
    ray job logs --address ${RAY_HEAD} JOB_ID

    # 停止工作
    ray job stop --address ${RAY_HEAD} JOB_ID

环境变量（Environment Variables）
------------------------------------------------------

HPC 集群上 Ray 的常见环境 variables：

.. code-block:: bash

    # Ray设置
    export RAY_DEDUP_LOGS=0           # 禁用日志重复数据删除
    export RAY_USAGE_STATS_ENABLED=0  # 禁用使用统计

    # NCCL 多节点 GPU 通信设置
    export NCCL_DEBUG=INFO
    export NCCL_SOCKET_IFNAME=^docker,lo,veth
    export NCCL_P2P_NET_CHUNKSIZE=524288

    # EFA 设置 (AWS)
    export FI_PROVIDER=efa
    export FI_EFA_USE_DEVICE_RDMA=1
    export FI_EFA_FORK_SAFE=1
