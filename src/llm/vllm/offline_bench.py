#!/usr/bin/env python3
"""
Offline vLLM benchmark without API server overhead.
Based on vllm torchrun_dp_example.py for distributed inference.

Usage:
    # Single GPU
    python offline_bench.py --model meta-llama/Llama-3.1-8B --num-prompts 50

    # Multi-GPU with tensor parallelism
    torchrun --nproc-per-node=4 offline_bench.py \
        --model Qwen/Qwen2-57B-A14B \
        --tp-size 4 --enable-ep \
        --num-prompts 100

    # Data parallelism
    torchrun --nproc-per-node=8 offline_bench.py \
        --model meta-llama/Llama-3.1-8B \
        --tp-size 2 --dp-size 4 \
        --num-prompts 200
"""

import argparse
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import List
import numpy as np

from vllm import LLM, SamplingParams


@contextmanager
def viztracer_profiler(output_file, world_rank):
    """VizTracer profiler context manager."""
    viztracer = None
    if output_file:
        try:
            from viztracer import VizTracer

            viztracer = VizTracer(
                output_file=output_file, verbose=0, log_torch=True
            )
            if world_rank == 0:
                print(f"VizTracer profiling enabled. Output: {output_file}")
        except ImportError:
            if world_rank == 0:
                print(
                    "Warning: viztracer not installed (pip install viztracer)"
                )

    try:
        if viztracer:
            viztracer.start()
            if world_rank == 0:
                print("VizTracer started")
        yield
    finally:
        if viztracer:
            viztracer.stop()
            viztracer.save()
            if world_rank == 0:
                print(f"VizTracer trace saved to {output_file}")


@contextmanager
def cuda_profiler(enabled, world_rank):
    """CUDA profiler context manager for nsys."""
    profiler = None

    if enabled:
        import torch.cuda.profiler as profiler

    try:
        if enabled:
            profiler.start()
            if world_rank == 0:
                print("CUDA profiler started for nsys")
        yield
    finally:
        if enabled and profiler:
            profiler.stop()
            if world_rank == 0:
                print("CUDA profiler stopped")


def load_sharegpt_prompts(dataset_path: str, num_prompts: int) -> List[str]:
    """Load prompts from ShareGPT dataset."""
    with open(dataset_path) as f:
        data = json.load(f)

    prompts = []
    for item in data[:num_prompts]:
        if "conversations" in item and len(item["conversations"]) > 0:
            prompts.append(item["conversations"][0]["value"])

    return prompts[:num_prompts]


def generate_random_prompts(
    num_prompts: int, input_len: int, tokenizer
) -> List[str]:
    """Generate random prompts with specified input length."""
    # 使用固定词汇以实现可重复性
    vocab = list(range(1000, 10000))  # 使用 vocab 中的令牌 ID
    prompts = []

    for _ in range(num_prompts):
        # 生成随机令牌 ID
        token_ids = [vocab[i % len(vocab)] for i in range(input_len)]
        # Decode 转文字
        prompt = tokenizer.decode(token_ids)
        prompts.append(prompt)

    return prompts


def generate_dummy_prompts(num_prompts: int) -> List[str]:
    """Generate dummy prompts for testing."""
    base_prompts = [
        "Hello, my name is",
        "The president of the United States is",
        "The capital of France is",
        "The future of AI is",
        "Explain quantum computing in simple terms:",
        "Write a short story about a robot:",
    ]
    return [base_prompts[i % len(base_prompts)] for i in range(num_prompts)]


def parse_args():
    parser = argparse.ArgumentParser(description="Offline vLLM benchmark")

    # 模型参数
    parser.add_argument(
        "--model", type=str, required=True, help="Model name or path"
    )
    parser.add_argument(
        "--max-model-len", type=int, default=None, help="Max model length"
    )
    parser.add_argument(
        "--gpu-memory-utilization",
        type=float,
        default=0.9,
        help="GPU memory utilization",
    )

    # 并行参数
    parser.add_argument(
        "--tensor-parallel-size",
        "--tp-size",
        type=int,
        default=1,
        dest="tp_size",
        help="Tensor parallel size",
    )
    parser.add_argument(
        "--pipeline-parallel-size",
        "--pp-size",
        type=int,
        default=1,
        dest="pp_size",
        help="Pipeline parallel size",
    )
    parser.add_argument(
        "--data-parallel-size",
        "--dp-size",
        type=int,
        default=1,
        dest="dp_size",
        help="Data parallel size",
    )
    parser.add_argument(
        "--enable-expert-parallel",
        "--enable-ep",
        action="store_true",
        dest="enable_ep",
        help="Enable expert parallel",
    )

    # Benchmark 参数
    parser.add_argument(
        "--num-prompts", type=int, default=50, help="Number of prompts"
    )
    parser.add_argument(
        "--dataset-path",
        type=str,
        default=None,
        help="Path to ShareGPT dataset",
    )
    parser.add_argument(
        "--input-len",
        type=int,
        default=None,
        help="Input length for random prompts (default: use dataset or dummy prompts)",
    )
    parser.add_argument(
        "--output-len",
        type=int,
        default=None,
        help="Output length (maps to --max-tokens)",
    )
    parser.add_argument(
        "--max-tokens", type=int, default=128, help="Max output tokens"
    )
    parser.add_argument(
        "--temperature", type=float, default=0.0, help="Sampling temperature"
    )
    parser.add_argument("--seed", type=int, default=0, help="Random seed")

    # Profiling 参数
    parser.add_argument(
        "--nsys",
        type=str,
        default=None,
        help="Enable nsys profiling and save to file (e.g., ./profile.nsys-rep)",
    )
    parser.add_argument(
        "--viztracer",
        type=str,
        default=None,
        help="Enable VizTracer profiling and save to file (e.g., ./vllm-trace.json)",
    )
    # vLLM 参数
    parser.add_argument(
        "--enforce-eager", action="store_true", help="Disable CUDA graph"
    )
    parser.add_argument(
        "--all2all-backend",
        type=str,
        default=None,
        help="All-to-all backend (allgather_reducescatter, nccl)",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # 将 --output-len 映射到 --max-tokens
    if args.output_len:
        args.max_tokens = args.output_len

    # 采样参数
    sampling_params = SamplingParams(
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        seed=args.seed,
        ignore_eos=args.input_len is not None,  # 忽略 EOS 随机提示
    )

    # 首先初始化LLM以获取分词器
    llm_kwargs = {
        "model": args.model,
        "tensor_parallel_size": args.tp_size,
        "pipeline_parallel_size": args.pp_size,
        "data_parallel_size": args.dp_size,
        "enable_expert_parallel": args.enable_ep,
        "gpu_memory_utilization": args.gpu_memory_utilization,
        "seed": args.seed,
        "enforce_eager": args.enforce_eager,
        "disable_log_stats": False,
    }

    if args.max_model_len:
        llm_kwargs["max_model_len"] = args.max_model_len

    if args.all2all_backend:
        llm_kwargs["all2all_backend"] = args.all2all_backend

    # 使用多 process 的外部启动器
    if args.dp_size > 1:
        llm_kwargs["distributed_executor_backend"] = "external_launcher"

    print(f"Initializing LLM with config: {json.dumps(llm_kwargs, indent=2)}")

    llm = LLM(**llm_kwargs)

    # 加载提示
    if args.input_len:
        prompts = generate_random_prompts(
            args.num_prompts, args.input_len, llm.get_tokenizer()
        )
    elif args.dataset_path:
        prompts = load_sharegpt_prompts(args.dataset_path, args.num_prompts)
    else:
        prompts = generate_dummy_prompts(args.num_prompts)

    # 获取 data parallel rank 与 size
    dp_rank = llm.llm_engine.vllm_config.parallel_config.data_parallel_rank
    dp_size = llm.llm_engine.vllm_config.parallel_config.data_parallel_size

    # 获取用于打印的 world rank
    import torch.distributed as dist

    world_rank = dist.get_rank() if dist.is_initialized() else 0

    # 将 prompts 分配到各个 DP ranks
    local_prompts = [
        p for i, p in enumerate(prompts) if i % dp_size == dp_rank
    ]

    # 预热
    if world_rank == 0:
        print("Warming up...")
    _ = llm.generate(local_prompts[:1], sampling_params)

    # 执行带 profiling 的 benchmark
    if world_rank == 0:
        print(f"Running benchmark with {len(prompts)} total prompts...")

    with cuda_profiler(args.nsys, world_rank), viztracer_profiler(
        args.viztracer, world_rank
    ):
        start = time.perf_counter()
        outputs = llm.generate(local_prompts, sampling_params)
        elapsed = time.perf_counter() - start

    # 收集每个请求的 metrics
    metrics = []
    for output in outputs:
        num_output_tokens = len(output.outputs[0].token_ids)
        input_tokens = len(output.prompt_token_ids)

        # 检查是否存在详细 metrics
        req_metrics = output.metrics
        if req_metrics and hasattr(req_metrics, "first_token_ts"):
            ttft = (
                req_metrics.first_token_ts - req_metrics.scheduled_ts
            ) * 1000
            if num_output_tokens > 1:
                total_gen_time = (
                    req_metrics.last_token_ts - req_metrics.first_token_ts
                ) * 1000
                tpot = total_gen_time / (num_output_tokens - 1)
            else:
                tpot = 0
        else:
            ttft = 0
            tpot = 0

        metrics.append(
            {
                "ttft": ttft,
                "tpot": tpot,
                "input_tokens": input_tokens,
                "output_tokens": num_output_tokens,
            }
        )

    # 汇总统计数据
    total_input = sum(m["input_tokens"] for m in metrics)
    total_output = sum(m["output_tokens"] for m in metrics)
    ttfts = [m["ttft"] for m in metrics]
    tpots = [m["tpot"] for m in metrics if m["tpot"] > 0]

    # 跨 DP ranks 汇总
    if dp_size > 1:
        import torch.distributed as dist

        # 收集所有 ranks 的统计数据
        local_stats = [
            len(metrics),
            elapsed,
            total_input,
            total_output,
            np.mean(ttfts) if ttfts else 0,
            np.median(ttfts) if ttfts else 0,
            np.percentile(ttfts, 99) if ttfts else 0,
            np.mean(tpots) if tpots else 0,
            np.median(tpots) if tpots else 0,
            np.percentile(tpots, 99) if tpots else 0,
        ]

        # 从全部 world ranks 汇集数据
        world_size = dist.get_world_size()
        world_rank = dist.get_rank()
        all_stats = [None] * world_size
        dist.all_gather_object(all_stats, local_stats)

        # 仅在 world rank 0 打印
        if world_rank == 0:
            # 仅保留 DP ranks（每隔 TP_SIZE 个 rank 取一个）
            tp_size = (
                llm.llm_engine.vllm_config.parallel_config.tensor_parallel_size
            )
            dp_stats = [all_stats[i] for i in range(0, world_size, tp_size)]

            # 汇总
            total_reqs = sum(s[0] for s in dp_stats)
            max_time = max(s[1] for s in dp_stats)
            total_in = sum(s[2] for s in dp_stats)
            total_out = sum(s[3] for s in dp_stats)

            # 平均 latency 指标
            mean_ttft = np.mean([s[4] for s in dp_stats])
            median_ttft = np.mean([s[5] for s in dp_stats])
            p99_ttft = max(s[6] for s in dp_stats)
            mean_tpot = np.mean([s[7] for s in dp_stats])
            median_tpot = np.mean([s[8] for s in dp_stats])
            p99_tpot = max(s[9] for s in dp_stats)

            print_results(
                total_reqs,
                0,
                max_time,
                total_in,
                total_out,
                mean_ttft,
                median_ttft,
                p99_ttft,
                mean_tpot,
                median_tpot,
                p99_tpot,
            )

        # 通过 barrier 确保所有 ranks 完成后再清理
        dist.barrier()
    else:
        # 单process
        print_results(
            len(metrics),
            0,
            elapsed,
            total_input,
            total_output,
            np.mean(ttfts) if ttfts else 0,
            np.median(ttfts) if ttfts else 0,
            np.percentile(ttfts, 99) if ttfts else 0,
            np.mean(tpots) if tpots else 0,
            np.median(tpots) if tpots else 0,
            np.percentile(tpots, 99) if tpots else 0,
        )


def print_results(
    successful,
    failed,
    duration,
    total_input,
    total_output,
    mean_ttft,
    median_ttft,
    p99_ttft,
    mean_tpot,
    median_tpot,
    p99_tpot,
):
    """Print results in vLLM bench serve format."""
    print("\n============ Serving Benchmark Result ============")
    print(f"Successful requests:                     {successful:<10}")
    print(f"Failed requests:                         {failed:<10}")
    print(f"Benchmark duration (s):                  {duration:<10.2f}")
    print(f"Total input tokens:                      {total_input:<10}")
    print(f"Total generated tokens:                  {total_output:<10}")
    print(
        f"Request throughput (req/s):              {successful/duration:<10.2f}"
    )
    print(
        f"Output token throughput (tok/s):         {total_output/duration:<10.2f}"
    )
    print(
        f"Total token throughput (tok/s):          {(total_input+total_output)/duration:<10.2f}"
    )
    print("---------------Time to First Token----------------")
    print(f"Mean TTFT (ms):                          {mean_ttft:<10.2f}")
    print(f"Median TTFT (ms):                        {median_ttft:<10.2f}")
    print(f"P99 TTFT (ms):                           {p99_ttft:<10.2f}")
    print("-----Time per Output Token (excl. 1st token)------")
    print(f"Mean TPOT (ms):                          {mean_tpot:<10.2f}")
    print(f"Median TPOT (ms):                        {median_tpot:<10.2f}")
    print(f"P99 TPOT (ms):                           {p99_tpot:<10.2f}")
    print("---------------Inter-token Latency----------------")
    print(f"Mean ITL (ms):                           {mean_tpot:<10.2f}")
    print(f"Median ITL (ms):                         {median_tpot:<10.2f}")
    print(f"P99 ITL (ms):                            {p99_tpot:<10.2f}")
    print("==================================================\n")


if __name__ == "__main__":
    main()
