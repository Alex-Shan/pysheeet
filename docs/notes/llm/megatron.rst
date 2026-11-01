.. meta::
    :description lang=zh_CN: Megatron Bridge 速查表 — 预训练配方、Nsys profiling 以及使用 EFA 在 SLURM 上进行分布式训练。
    :keywords: Megatron, Megatron-LM, Megatron Bridge, distributed training, pretrain, Nsys, profiling, EFA, SLURM, DeepSeek, MoE, NCCL, GPU, LLM

======================================================
Megatron-LM 框架（Megatron-LM）
======================================================

.. contents:: 目录（Table of Contents）
    :backlinks: none

`Megatron-LM 框架（Megatron-LM） <https://github.com/NVIDIA/Megatron-LM/tree/main>`_ 是 NVIDIA 的框架，用于使用 tensor、管道和专家并行性来训练和微调大型Transformer 模型。 `Megatron Bridge <https://github.com/NVIDIA-NeMo/Megatron-Bridge/tree/main>`_ 位于 Megatron-LM 之上，并提供基于配方的接口 - 您无需传递数十个 CLI 标志，而是编写一个简短的 Python 配方，该配方返回配置 object。配方可以直接通过 ``hf_path`` parameter 加载 `HuggingFace <https://huggingface.co/models>`_ 预训练权重，因此您可以从任何检查点开始，无需手动转换。

在本笔记中，我们演示如何使用 Megatron Bridge 加载 HuggingFace 预训练权重并使用 Megatron-LM 进行训练。这些示例使用 `src/megatron <https://github.com/crazyguitar/pysheeet/blob/master/src/megatron>`__ 中的脚本。

使用 Megatron Bridge（How to Use Megatron Bridge）
--------------------------------------------------------------------------------------------

容器映像是使用 Docker 构建的，并导出为 `enroot <https://github.com/NVIDIA/enroot>`_ squashfs ( ``.sqsh`` ) 文件。 Enroot 是专为 HPC 设计的轻量级容器运行时 - 它将 Docker 图像转换为非特权沙箱，并通过 `pyxis <https://github.com/NVIDIA/pyxis>`_ 插件与 SLURM 集成。当 ``srun.sh`` 运行时，它将 ``--container-image`` 和 ``--container-mounts`` 传递给 ``srun`` ，pyxis 处理导入 ``.sqsh`` 并启动容器内的每个任务。

.. code-block:: bash

    # 构建 Docker 镜像并导出到 enroot sqsh
    make build

    # 这会在当前目录中生成 megatron-lm+latest.sqsh。
    # srun.sh picks it up via the SQSH env var (default: ./megatron-lm+latest.sqsh).

您可以使用环境 variables 覆盖映像路径和容器安装：

.. list-table::
   :header-rows: 1

   * - Variable
     - 默认
     - 描述
   * - ``SQSH``
     - ``./megatron-lm+latest.sqsh``
     - enroot 图像的路径
   * - ``MOUNT``
     - ``.:/workspace/megatron,/fsx:/fsx``
     - 集装箱支架
   * - ``GPUS_PER_NODE``
     - ``8``
     - 每个节点的 GPU 数量

配方是一个 Python 文件，它调用 Megatron 桥配置 function 并返回 ``ConfigContainer`` 。例如， `deepseek_v2_lite_pretrain.py <https://github.com/crazyguitar/pysheeet/blob/master/src/megatron/recipes/deepseek_v2_lite_pretrain.py>`__ ：

.. code-block:: python

    from megatron.bridge.recipes.deepseek.deepseek_v2 import (
        deepseek_v2_lite_pretrain_config,
    )


    def configure(hf_path=None, moe_token_dispatcher_type=None):
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
        if moe_token_dispatcher_type == "deepep":
            cfg.model.moe_token_dispatcher_type = "flex"
            cfg.model.moe_flex_dispatcher_backend = "deepep"
            cfg.model.moe_enable_deepep = True
            cfg.model.moe_shared_expert_overlap = False
        return cfg

使用 ``srun.sh`` 启动预训练作业，该作业包装 ``srun`` + pyxis 以在 enroot 容器内运行：

.. code-block:: bash

    # 2 节点 DeepSeek V2 Lite 预训练
    salloc -N 2
    ./srun.sh recipes/deepseek_v2_lite_pretrain.py \
        hf_path=/fsx/models/deepseek-ai/DeepSeek-V2-Lite

    # 使用 Hydra 风格的参数覆盖配置
    ./srun.sh recipes/deepseek_v2_lite_pretrain.py \
        train.train_iters=1000

`entrypoint.py <https://github.com/crazyguitar/pysheeet/blob/master/src/megatron/entrypoint.py>`__ 加载配方，应用CLI覆盖，并调用 ``pretrain()`` 。 ``srun.sh`` 脚本 sets 到 EFA 环境 variables（ ``FI_PROVIDER=efa`` 、 ``NCCL_NET_PLUGIN`` 等）并将 ``SLURM_PROCID`` / ``SLURM_LOCALID`` 映射到 ``RANK`` / ``LOCAL_RANK`` 以便Megatron 的分布式初始化无需 ``torchrun`` 即可工作。

如何启用 Nsys 分析（How to Enable Nsys Profiling）
------------------------------------------------------------------------------------

将 ``--nsys`` 传递给 ``srun.sh`` 和 set，profiling 在配方中覆盖：

.. code-block:: bash

    ./srun.sh --nsys recipes/deepseek_v2_lite_pretrain.py \
        hf_path=/fsx/models/deepseek-ai/DeepSeek-V2-Lite \
        profiling.use_nsys_profiler=true \
        profiling.profile_step_start=10 \
        profiling.profile_step_end=15 \
        profiling.profile_ranks=[0]

当 ``--nsys`` 使能时， ``srun.sh`` 在 ``nsys profile`` 前面添加 ``--capture-range=cudaProfilerApi`` ，以便仅捕获 ``profile_step_start`` 和 ``profile_step_end`` 之间的步骤。输出 ``.nsys-rep`` 文件写入容器挂载内的 ``nsys-megatron/`` 。

在 AWS 上，如果要监控 Nsys 时间线中的 EFA 网络流量，请将 ``--enable efa_metrics`` 添加到 nsys 命令（已包含在 ``srun.sh`` 中）。有关使用 NCCL、GIN 和 Nsys 监控 EFA 的详细演练，请参阅 :doc:`/notes/appendix/megatron-efa-monitoring` 。

为什么是 ``python`` 而不是 ``torchrun`` （Why ``python`` Instead of ``torchrun`` ）
----------------------------------------------------------------------------------------------------------------------------------------------------

``srun.sh`` 脚本直接启动 ``python3 entrypoint.py`` ，而不是使用 ``torchrun`` 。这是故意的。 ``torchrun`` 通过 ``multiprocessing`` 生成工作线程 processes，生成边界可能会干扰 Nsys profiling — profiler 有时无法捕获子 process 发出的 ``cudaProfilerStart`` 和 ``cudaProfilerStop`` 调用，从而导致在空的或不完整的痕迹中。

通过直接在 ``srun --ntasks-per-node=<GPUS>`` 下运行 ``python`` ，每个 GPU 都会获得由 SLURM 管理的自己的 process。 ``RANK`` 、 ``LOCAL_RANK`` 和 ``WORLD_SIZE`` 环境 variables 分别源自 ``SLURM_PROCID`` 、 ``SLURM_LOCALID`` 和 ``SLURM_NTASKS`` 。这完全避免了生成层，为 Nsys（以及其他 profilers，如 VizTracer）提供每个等级的干净、单 process 视图。

自定义分析器 (VizTracer)（Custom Profilers (VizTracer)）
------------------------------------------------------------------------------------------------

Megatron Bridge 的 profiling 挂钩可扩展以支持定制 profilers。 `viztracer_plugin.py <https://github.com/crazyguitar/pysheeet/blob/master/src/megatron/viztracer_plugin.py>`__ 展示了如何通过猴子修补 ``megatron.bridge.training.profiling`` 来做到这一点：

1. 通过 ``dataclasses.field`` 将新字段（e.g. ``use_viztracer`` ）添加到 ``ProfilingConfig`` ，以便 OmegaConf 将其识别为有效覆盖。
2. 修补 ``handle_profiling_step`` 以在 ``profile_step_start`` 处启动 profiler。
3. 修补 ``handle_profiling_stop`` 以停止并保存在 ``profile_step_end`` 。

该插件在任何 Megatron 导入之前加载到 `entrypoint.py <https://github.com/crazyguitar/pysheeet/blob/master/src/megatron/entrypoint.py>`__ 中：

.. code-block:: python

    import viztracer_plugin
    viztracer_plugin.install()

然后在 command line 上传递覆盖：

.. code-block:: bash

    ./srun.sh recipes/deepseek_v2_lite_pretrain.py \
        hf_path=/fsx/models/deepseek-ai/DeepSeek-V2-Lite \
        profiling.use_viztracer=true \
        profiling.profile_step_start=10 \
        profiling.profile_step_end=15 \
        profiling.profile_ranks=[0]

相同的模式适用于任何 profiler — 在修补的钩子中实现 ``start()`` / ``stop()`` / ``save()`` 并注册一个配置字段，以便可以通过 Hydra 覆盖进行切换。
