#!/usr/bin/env bash
# vLLM 服务 benchmark 套件
# 用法：
#   salloc -N1 bash bench.sh -H 10.0.128.193 -i /fsx/vllm-serve-latest.tar.gz
#   bash bench.sh -H 10.0.128.193 -i vllm-服务：最新
set -euo pipefail

info() { echo "[$(date +'%H:%M:%S')] $*"; }

# Docker 图像助手（镜子 run.sbatch）
CONTAINER_MOUNT="${CONTAINER_MOUNT:-/fsx}"

# 如果在 SLURM 分配内，则用 srun 包装命令，否则直接运行
_run() {
    if [[ -n "${SLURM_JOB_ID:-}" ]]; then
        srun -N1 --ntasks-per-node=1 bash -c "$*"
    else
        bash -c "$*"
    fi
}

load_or_pull_image() {
    if [[ "${IMAGE}" == *.tar.gz ]]; then
        CONTAINER_IMAGE=$(pigz -dc "${IMAGE}" | tar -xf - -O manifest.json \
            | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['RepoTags'][0])")
        info "Image tag: ${CONTAINER_IMAGE}"
        _run "
            if ! docker image inspect '${CONTAINER_IMAGE}' &>/dev/null; then
                echo 'Loading Docker image from tarball...'
                pigz -dc '${IMAGE}' | docker load
            fi
        "
    else
        CONTAINER_IMAGE="${IMAGE}"
        _run "
            if ! docker image inspect '${CONTAINER_IMAGE}' &>/dev/null; then
                echo 'Pulling ${CONTAINER_IMAGE}...'
                registry=\"\${CONTAINER_IMAGE%%/*}\"
                region=\$(echo \"\${registry}\" | sed -n 's/.*\.ecr\.\([^.]*\)\.amazonaws\.com/\1/p')
                region=\"\${region:-us-west-2}\"
                aws ecr get-login-password --region \"\${region}\" \
                    | docker login --username AWS --password-stdin \"\${registry}\"
                docker pull '${CONTAINER_IMAGE}'
            fi
        "
    fi
}

launch_container() {
    local cmd="$1"
    _run "
        docker run --rm --net=host \
            -v '${PWD}:${PWD}' -w '${PWD}' \
            -v '${CONTAINER_MOUNT}:${CONTAINER_MOUNT}' \
            --entrypoint bash '${CONTAINER_IMAGE}' \
            -c '${cmd}'
    "
}

# 如果 vllm CLI 不可用，则加载映像并在容器内重新执行
if ! command -v vllm &>/dev/null; then
    # 在完整参数解析之前预解析 --image/-i
    IMAGE="" _args=("$@")
    for ((i=0; i<${#_args[@]}; i++)); do
        [[ "${_args[$i]}" == "--image" || "${_args[$i]}" == "-i" ]] \
            && { IMAGE="${_args[$((i+1))]}"; break; }
    done
    IMAGE="${IMAGE:-${PWD}/vllm-serve-latest.tar.gz}"

    load_or_pull_image
    _SCRIPT="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
    launch_container "bash ${_SCRIPT} $*"
    exit $?
fi

HOST="localhost"
PORT="8000"
MODEL=""
SEED="42"
RESULT_DIR="./results"
PROFILE=""
TYPES="throughput,prefill,decode,latency,concurrency,longctx,sharegpt,sonnet"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  -H, --host HOST         Server host (default: $HOST)
  -p, --port PORT         Server port (default: $PORT)
  -m, --model MODEL       Model name (auto-detected if omitted)
  -t, --type TYPES        Comma-separated tests (default: all)
                          Available: throughput,prefill,decode,latency,concurrency,longctx,sharegpt,sonnet
  -o, --output DIR        Result directory (default: $RESULT_DIR)
  -i, --image IMAGE       Docker image or tarball (default: ./vllm-serve-latest.tar.gz)
  --profile               Enable PyTorch profiler (server must have --profiler-config set)
  -h, --help              Show this help

Examples:
  $(basename "$0") -H 10.0.128.193
  $(basename "$0") -H 10.0.128.193 --type throughput,prefill
  $(basename "$0") -H 10.0.128.193 --type latency -m Qwen/Qwen3-30B-A3B-FP8
  $(basename "$0") -H 10.0.128.193 --type throughput --profile
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -H|--host)  HOST="$2"; shift 2 ;;
        -p|--port)  PORT="$2"; shift 2 ;;
        -m|--model) MODEL="$2"; shift 2 ;;
        -t|--type)  TYPES="$2"; shift 2 ;;
        -o|--output) RESULT_DIR="$2"; shift 2 ;;
        -i|--image)  shift 2 ;;  # 上面的序言消耗了
        --profile)   PROFILE="--profile"; shift ;;
        -h|--help)   usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

BASE_URL="http://${HOST}:${PORT}"
if [[ -z "$MODEL" ]]; then
    MODEL=$(curl -s "${BASE_URL}/v1/models" | python3 -c "import sys,json; print(json.load(sys.stdin)['data'][0]['id'])")
fi
mkdir -p "$RESULT_DIR"

if [[ -n "$PROFILE" ]]; then
    info "Profiling enabled (server must have --profiler-config set)"
    info "View traces at https://ui.perfetto.dev/"
fi

bench() {
    local label="$1"; shift
    echo "==> $label"
    vllm bench serve \
        --model "$MODEL" \
        --base-url "$BASE_URL" \
        --backend openai-chat \
        --endpoint /v1/chat/completions \
        --seed "$SEED" \
        --save-result \
        --result-dir "$RESULT_DIR" \
        $PROFILE \
        "$@"
    echo ""
}


# Throughput：测量峰值输出令牌/秒并请求 throughput。
# Uses request-rate=inf to saturate the server — all 1000 prompts are sent as fast as
# 可能，迫使调度程序积极地进行批处理。 512in/256out 适中
# 执行 prefill 和 decode 阶段的工作负载。 1000 条提示如下
# 用于统计稳定 throughput 数字的 GPUStack 方法。
bench_throughput() {
    bench "Throughput (random 512in/256out, max rate)" \
        --dataset-name random \
        --random-input-len 512 --random-output-len 256 \
        --num-prompts 100 --request-rate inf
}

# Prefill（TTFT）：测量Time to First Token，反映即时处理速度。
# output-len=1 isolates prefill from decode — we only care how fast the model processes
# 输入。扫描 128→16K 标记以显示 TTFT 如何随上下文长度缩放（应该
# 由于 attention 在 prefill 期间每层的 O(n) 计算，大致呈线性增长。
# rate=4 keeps the server lightly loaded so TTFT reflects compute, not queueing.
bench_prefill() {
    for len in 128 512 2048 4096 16384; do
        bench "Prefill TTFT (input=${len})" \
            --dataset-name random \
            --random-input-len "$len" --random-output-len 1 \
            --num-prompts 100 --request-rate 4
    done
}

# Decode (ITL)：测量生成期间的令牌间 Latency 和每个输出令牌的时间。
# input=128 keeps prefill minimal so the benchmark focuses on autoregressive decode.
# 扫描 128→1024 个输出令牌，以揭示 ITL 如何随着 KV cache 的增长而变化 - 更长
# 序列会增加内存压力并可能触发抢占/交换。
# rate=4 avoids batching interference so ITL reflects per-request decode speed.
bench_decode() {
    for len in 128 256 512 1024; do
        bench "Decode ITL (output=${len})" \
            --dataset-name random \
            --random-input-len 128 --random-output-len "$len" \
            --num-prompts 100 --request-rate 4
    done
}

# Latency (E2E)：测量最小负载下的端到端请求 latency。
# rate=1 ensures requests are mostly processed alone (no batching), giving a baseline
# 最佳情况 latency。测试短/中/长以显示 latency 总量的缩放情况。
# 这些数字代表 "single user" 体验（类似于 ChatGPT 风格的使用
# 其中一个用户等待完整的响应）。
bench_latency() {
    bench "Latency (short 128/128, rate=1)" \
        --dataset-name random \
        --random-input-len 128 --random-output-len 128 \
        --num-prompts 100 --request-rate 1
    bench "Latency (medium 512/256, rate=1)" \
        --dataset-name random \
        --random-input-len 512 --random-output-len 256 \
        --num-prompts 100 --request-rate 1
    bench "Latency (long 4096/512, rate=1)" \
        --dataset-name random \
        --random-input-len 4096 --random-output-len 512 \
        --num-prompts 100 --request-rate 1
}

# 并发：通过扫描并发请求来找到服务器的饱和点。
# request-rate=inf with max-concurrency=N caps how many requests run in parallel.
# 在低并发（1-4）时，latency 很好，但 throughput 较低（GPU 未充分利用）。
# 在高并发 (64-256) 下，throughput 趋于稳定，latency 性能下降（排队）。
# throughput 停止改进的 "knee" 是最佳工作点。
# 每个级别 500 个提示为稳定的百分位数指标提供了足够的样本。
bench_concurrency() {
    for c in 1 4 16 64 256; do
        bench "Concurrency=${c} (512in/256out)" \
            --dataset-name random \
            --random-input-len 512 --random-output-len 256 \
            --num-prompts 100 --request-rate inf --max-concurrency "$c"
    done
}

# 长上下文：使用很长的输入（4K→32K 标记）测​​试行为。
# 受到 GPUStack 的 "very long prompt" 配置（32000in/100out）的启发。长输入应力
# KV cache memory, attention compute, and may trigger chunked prefill. output=100 keeps
# decode short so we focus on prefill scaling. rate=1 and fewer prompts (50) because
# 每个请求都很昂贵，我们希望避免在内存压力下出现 OOM。
bench_longctx() {
    for len in 4096 16384 32000; do
        bench "Long context (input=${len})" \
            --dataset-name random \
            --random-input-len "$len" --random-output-len 100 \
            --num-prompts 50 --request-rate 1
    done
}

# ShareGPT：来自真实用户对话的真实对话工作负载。 Variable
# 输入/输出长度反映实际使用模式。这是标准数据集
# 由 vLLM CI 使用， GPUStack 性能实验室， 以及大多数已发布的基准。 与随机不同
# 数据集，ShareGPT 捕获短/长提示的自然分布，
# 响应，使其成为生产聊天流量的最佳代理。
# 参考：github.com/vllm-project/vllm/blob/main/benchmarks/README.md
# 参考：GPUStack 性能实验室使用具有 1000 个提示的 ShareGPT 作为主要 benchmark。
#
# 需要：wget https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered/resolve/main/ShareGPT_V3_unfiltered_cleaned_split.json
SHAREGPT_PATH="${SHAREGPT_PATH:-ShareGPT_V3_unfiltered_cleaned_split.json}"
bench_sharegpt() {
    if [[ ! -f "$SHAREGPT_PATH" ]]; then
        echo "Downloading ShareGPT dataset..."
        wget -q -O "$SHAREGPT_PATH" \
            https://huggingface.co/datasets/anon8231489123/ShareGPT_Vicuna_unfiltered/resolve/main/ShareGPT_V3_unfiltered_cleaned_split.json
    fi
    bench "ShareGPT (1000 prompts, max rate)" \
        --dataset-name sharegpt \
        --dataset-path "$SHAREGPT_PATH" \
        --num-prompts 100 --request-rate inf
    bench "ShareGPT (1000 prompts, rate=4)" \
        --dataset-name sharegpt \
        --dataset-path "$SHAREGPT_PATH" \
        --num-prompts 100 --request-rate 4
}

# Sonnet：使用具有共享前缀的莎士比亚十四行诗来测试前缀caching。
# All prompts share a common prefix (--sonnet-prefix-len=200 tokens of sonnet text),
# 那么每个请求都会有一个唯一的后缀。这个练习vLLM的自动前缀
# caching — 如果启用，则共享前缀 KV cache 计算一次并在各个区域重复使用
# 请求，大大减少了 TTFT。比较带有前缀 caching 的十四行诗结果
# 打开与关闭显示 caching 加速比。
# 参考：vllm/基准/datasets.py SonnetDataset
# Ref: Default params: input=550, output=150, prefix=200
bench_sonnet() {
    SONNET_PATH="${SONNET_PATH:-sonnet.txt}"
    if [[ ! -f "$SONNET_PATH" ]]; then
        echo "Downloading Shakespeare sonnets..."
        wget -q -O "$SONNET_PATH" \
            https://raw.githubusercontent.com/vllm-project/vllm/main/benchmarks/sonnet.txt
    fi
    bench "Sonnet (prefix caching, max rate)" \
        --dataset-name sonnet --dataset-path "$SONNET_PATH" \
        --sonnet-input-len 550 --sonnet-output-len 150 --sonnet-prefix-len 200 \
        --num-prompts 100 --request-rate inf
    bench "Sonnet (prefix caching, rate=4)" \
        --dataset-name sonnet --dataset-path "$SONNET_PATH" \
        --sonnet-input-len 550 --sonnet-output-len 150 --sonnet-prefix-len 200 \
        --num-prompts 100 --request-rate 4
}

IFS=',' read -ra TESTS <<< "$TYPES"
for t in "${TESTS[@]}"; do
    t=$(echo "$t" | xargs)  # 修剪空白
    echo "========================================"
    echo "Running: $t"
    echo "========================================"
    case "$t" in
        throughput)  bench_throughput ;;
        prefill)     bench_prefill ;;
        decode)      bench_decode ;;
        latency)     bench_latency ;;
        concurrency) bench_concurrency ;;
        longctx)     bench_longctx ;;
        sharegpt)    bench_sharegpt ;;
        sonnet)      bench_sonnet ;;
        *) echo "Unknown test: $t"; exit 1 ;;
    esac
done
