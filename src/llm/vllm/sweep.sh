#!/usr/bin/env bash
# vLLM扫benchmark套件
#
# 通过 sweep.sbatch 运行预定义的扫描配置。每个套房都写着
# 不同的 bench_params.json 并使用适当的调用 sweep.sbatch
# --bench-cmd 用于该工作负载。
#
# 用法：
#   bash sweep.sh -m Qwen/Qwen3-0.6B
#   bash sweep.sh -m Qwen/Qwen3-30B-A3B-FP8 -i $PWD/vllm-服务-latest.tar.gz \
#       --serve-cmd "vllm serve Qwen/Qwen3-30B-A3B-FP8 -tp 8 --enable-expert-parallel" \
#       --type 速率、并发数
set -euo pipefail

info() { echo "[$(date +'%H:%M:%S')] $*"; }

MODEL="Qwen/Qwen3-0.6B"
IMAGE=""
RESULT_DIR="results"
NUM_PROMPTS=100
SEED=42
TYPES="rate,concurrency,input,output"
SBATCH_ARGS=()          # 直通至 sweep.sbatch

usage() {
    cat <<EOF
Usage: $(basename "$0") [options] [sweep.sbatch args...]

Options (consumed by sweep.sh):
  -m, --model MODEL       Model name/path (default: $MODEL)
  -i, --image IMAGE       Docker image tarball or registry URI
  -o, --output DIR        Results directory (default: $RESULT_DIR)
  -t, --type TYPES        Comma-separated suites (default: all)
                          Available: rate,concurrency,input,output
  -h, --help              Show this help

All other args are passed through to sweep.sbatch (and then to vllm bench sweep serve):
  --serve-cmd, --show-stdout, --num-runs, --dry-run, etc.
EOF
    exit 0
}

while (( "$#" )); do
    case "$1" in
        -m|--model)  MODEL="$2"; shift 2 ;;
        -i|--image)  IMAGE="$2"; shift 2 ;;
        -o|--output) RESULT_DIR="$2"; shift 2 ;;
        -t|--type)   TYPES="$2"; shift 2 ;;
        -h|--help)   usage ;;
        *)           SBATCH_ARGS+=("$1"); shift ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

run_sweep() {
    local name="$1" bench_extra="$2" params_json="$3"
    local out="${RESULT_DIR}/${name}"
    mkdir -p "$out"

    echo "$params_json" > "${out}/bench_params.json"

    info "=== Sweep: ${name} ==="
    bash "${SCRIPT_DIR}/sweep.sbatch" \
        -m "$MODEL" \
        ${IMAGE:+-i "$IMAGE"} \
        --bench-cmd "vllm bench serve --model ${MODEL} ${bench_extra} --seed ${SEED}" \
        --bench-params "${out}/bench_params.json" \
        -o "$out" \
        "${SBATCH_ARGS[@]+"${SBATCH_ARGS[@]}"}"
}


# 请求率：找到固定工作负载的饱和点
sweep_rate() {
    run_sweep "rate" \
        "--dataset-name random --random-input-len 512 --random-output-len 256 --num-prompts ${NUM_PROMPTS}" \
        '[{"request-rate":1},{"request-rate":2},{"request-rate":4},{"request-rate":8},{"request-rate":16},{"request-rate":32},{"request-rate":"inf"}]'
}

# 并发：找到最佳批量大小
sweep_concurrency() {
    run_sweep "concurrency" \
        "--dataset-name random --random-input-len 512 --random-output-len 256 --num-prompts ${NUM_PROMPTS}" \
        '[{"max-concurrency":1},{"max-concurrency":2},{"max-concurrency":4},{"max-concurrency":8},{"max-concurrency":16},{"max-concurrency":32},{"max-concurrency":64},{"max-concurrency":128}]'
}

# 输入长度：测量 TTFT 与上下文大小的缩放
sweep_input() {
    run_sweep "input" \
        "--dataset-name random --random-output-len 128 --num-prompts ${NUM_PROMPTS} --request-rate inf" \
        '[{"random-input-len":128},{"random-input-len":256},{"random-input-len":512},{"random-input-len":1024},{"random-input-len":2048},{"random-input-len":4096},{"random-input-len":8192},{"random-input-len":16384}]'
}

# 输出长度：随着 KV cache 的增长测量 ITL
sweep_output() {
    run_sweep "output" \
        "--dataset-name random --random-input-len 512 --num-prompts ${NUM_PROMPTS} --request-rate inf" \
        '[{"random-output-len":64},{"random-output-len":128},{"random-output-len":256},{"random-output-len":512},{"random-output-len":1024},{"random-output-len":2048}]'
}


IFS=',' read -ra TESTS <<< "$TYPES"
for t in "${TESTS[@]}"; do
    t=$(echo "$t" | xargs)
    case "$t" in
        rate)        sweep_rate ;;
        concurrency) sweep_concurrency ;;
        input)       sweep_input ;;
        output)      sweep_output ;;
        *) echo "Unknown sweep: $t"; exit 1 ;;
    esac
done

info "All sweeps complete — results in ${RESULT_DIR}/"
