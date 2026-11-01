"""VizTracer profiling plugin for Megatron Bridge.

Monkey-patches megatron.bridge.training.profiling to add viztracer support.
Activated when `profiling.use_viztracer=true` is passed as a Hydra override.

Usage:
    ./srun.sh recipes/deepseek_v2_lite_pretrain.py \
        profiling.use_viztracer=true \
        profiling.profile_step_start=10 \
        profiling.profile_step_end=15 \
        profiling.profile_ranks=[0]
"""

import os
from dataclasses import dataclass, field
from typing import Optional

import torch

from megatron.bridge.training import profiling as _profiling
from megatron.bridge.training.config import ProfilingConfig

# 专卖店原装functions
_orig_handle_step = _profiling.handle_profiling_step
_orig_handle_stop = _profiling.handle_profiling_stop

# 每个等级的全球 viztracer instance
_viztracer_instance: Optional[object] = None


def _patched_handle_step(config, iteration, rank, pytorch_prof):
    global _viztracer_instance

    # 委托给 nsys/pytorch 的原件
    result = _orig_handle_step(config, iteration, rank, pytorch_prof)
    if result is not None:
        return result

    if not getattr(config, "use_viztracer", False):
        return None
    if not _profiling.should_profile_rank(config, rank):
        return None
    if iteration != config.profile_step_start:
        return None

    from viztracer import VizTracer

    out_dir = os.environ.get(
        "VIZTRACER_OUTPUT_DIR",
        os.path.join(os.path.dirname(__file__), "viztracer_output"),
    )
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"trace_rank{rank}.json")

    _viztracer_instance = VizTracer(
        output_file=out_path,
        log_torch=True,
    )
    _viztracer_instance.start()
    return None


def _patched_handle_stop(
    config, iteration, rank, pytorch_prof, nsys_nvtx_context=None
):
    global _viztracer_instance

    _orig_handle_stop(config, iteration, rank, pytorch_prof, nsys_nvtx_context)

    if not getattr(config, "use_viztracer", False):
        return
    if not _profiling.should_profile_rank(config, rank):
        return
    if iteration != config.profile_step_end:
        return
    if _viztracer_instance is not None:
        _viztracer_instance.stop()
        _viztracer_instance.save()
        _viztracer_instance = None


def install():
    """Monkey-patch profiling hooks and extend ProfilingConfig."""
    import dataclasses

    # 将 use_viztracer 注册为真实的数据类字段，以便 OmegaConf 识别它
    f = dataclasses.field(default=False)
    f.name = "use_viztracer"
    f._field_type = dataclasses._FIELD
    ProfilingConfig.__dataclass_fields__["use_viztracer"] = f
    ProfilingConfig.use_viztracer = False

    # 修补原始定稿以接受 viztracer
    _orig_finalize = ProfilingConfig.finalize

    def _patched_finalize(self):
        if getattr(self, "use_viztracer", False):
            assert (
                not self.use_nsys_profiler and not self.use_pytorch_profiler
            ), "use_viztracer is mutually exclusive with nsys and pytorch profilers"
        else:
            _orig_finalize(self)

    ProfilingConfig.finalize = _patched_finalize

    # 贴片 profiling 挂钩
    _profiling.handle_profiling_step = _patched_handle_step
    _profiling.handle_profiling_stop = _patched_handle_stop
