#!/usr/bin/env bash
# vLLM 服务 benchmark 套件
# 用法：
#   salloc -N1 bash bench.sh -H 10.0.128.193 -i /fsx/nixl-latest.tar.gz
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
    CONTAINER_IMAGE=$(pigz -dc "${IMAGE}" | tar -xf - -O manifest.json |
      python3 -c "import sys,json; print(json.load(sys.stdin)[0]['RepoTags'][0])")
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
  for ((i = 0; i < ${#_args[@]}; i++)); do
    [[ "${_args[$i]}" == "--image" || "${_args[$i]}" == "-i" ]] &&
      {
        IMAGE="${_args[$((i + 1))]}"
        break
      }
  done
  IMAGE="${IMAGE:-${PWD}/nixl-latest.tar.gz}"

  load_or_pull_image
  _SCRIPT="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
  launch_container "bash ${_SCRIPT} $*"
  exit $?
fi

HOST="localhost"
PORT="8000"
BENCH_ARGS=()

usage() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS] [-- VLLM_BENCH_ARGS...]

Options:
  -H, --host HOST         Server host (default: $HOST)
  -p, --port PORT         Server port (default: $PORT)
  -i, --image IMAGE       Docker image or tarball (default: ./nixl-latest.tar.gz)
  -h, --help              Show this help

Examples:
  $(basename "$0") -H 10.0.128.193 -- --model meta-llama/Llama-3.1-8B --dataset-name sharegpt --num-prompts 100
  $(basename "$0") -H 10.0.128.193 -- --model meta-llama/Llama-3.1-8B --profile
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
  -H | --host)
    HOST="$2"
    shift 2
    ;;
  -p | --port)
    PORT="$2"
    shift 2
    ;;
  -i | --image) shift 2 ;; # 上面的序言消耗了
  -h | --help)
    usage
    exit 0
    ;;
  --)
    shift
    BENCH_ARGS+=("$@")
    break
    ;;
  *)
    echo "Unknown option: $1"
    usage
    exit 1
    ;;
  esac
done

BASE_URL="http://${HOST}:${PORT}"

info "========================================"
info "vLLM Benchmark Client"
info "========================================"
info "Server: ${BASE_URL}"
info "Command: vllm bench serve --base-url ${BASE_URL} ${BENCH_ARGS[*]}"
info "========================================"

vllm bench serve \
  --base-url "$BASE_URL" \
  "${BENCH_ARGS[@]}"
