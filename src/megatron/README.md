<a id="megatron"></a>

# Megatron 框架（Megatron）

```bash
make build

# 启动 2 节点 DeepSeek V2 Lite 预训练作业：
salloc -N 2
./srun.sh recipes/deepseek_v2_lite_pretrain.py \
    hf_path=/fsx/models/deepseek-ai/DeepSeek-V2-Lite

# 启动 DeepSeek V2 预训练（4 个节点）：
salloc -N 4
./srun.sh recipes/deepseek_v2_pretrain.py \
    hf_path=/fsx/models/deepseek-ai/DeepSeek-V2

# 使用 Hydra 风格的参数覆盖配置：
./srun.sh recipes/deepseek_v2_lite_pretrain.py \
    train.train_iters=1000

# 使用 DeepEP 和 NCCL GIN 启动 DeepSeek-V2-Lite
./srun.sh recipes/deepseek_v2_lite_pretrain.py \
    hf_path=/fsx/models/deepseek-ai/DeepSeek-V2-Lite \
    moe_token_dispatcher_type=deepep \
    model.tensor_model_parallel_size=1 \
    model.expert_model_parallel_size=64 \
    model.sequence_parallel=false

# Nsys简介
./srun.sh --nsys recipes/deepseek_v2_lite_pretrain.py \
  hf_path=/fsx/hf_pretrained_models/deepseek-ai/DeepSeek-V2-Lite \
  moe_token_dispatcher_type=deepep \
  model.tensor_model_parallel_size=1 \
  model.expert_model_parallel_size=64 \
  model.sequence_parallel=false \
  profiling.use_nsys_profiler=true \
  profiling.profile_step_start=10 \
  profiling.profile_step_end=15 \
  profiling.profile_ranks=[0]

# Viztracer 简介
./srun.sh recipes/deepseek_v2_lite_pretrain.py \
  hf_path=/fsx/models/deepseek-ai/DeepSeek-V2-Lite \
  profiling.use_viztracer=true \
  profiling.profile_step_start=10 \
  profiling.profile_step_end=15 \
  profiling.profile_ranks=[0]
```

<a id="environment-variables"></a>

## 环境变量（Environment Variables）

| Variable | Default | Description |
|---|---|---|
| `SQSH` | `./megatron-lm+latest.sqsh` | Path to enroot image |
| `MOUNT` | `.:/workspace/megatron,/fsx:/fsx` | Container mounts |
| `GPUS_PER_NODE` | `8` | GPUs per node |
