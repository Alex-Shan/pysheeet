#!/bin/bash
# vLLM 多种模式的服务器启动器

set -uo pipefail

PROGRAM="$0"
MODE="single"
MODEL="Qwen/Qwen2.5-7B-Instruct"
PORT="8000"
TP="1"
PP="1"
DP="1"
HEAD_IP="127.0.0.1"
NODE_RANK="0"

# 带有时间戳的日志信息消息
info() {
  echo -e "[$(date +'%Y-%m-%dT%H:%M:%S%z')][info] $*"
}

# 将带有时间戳的错误消息记录到 stderr
err() {
  echo -e "[$(date +'%Y-%m-%dT%H:%M:%S%z')][error] $*" >&2
}

# 显示使用信息
usage() {
  cat <<EOF
Usage:  $PROGRAM [OPTIONS] MODE

Modes:
  single                    Simple single-GPU server (default)
  ray                        Ray cluster backend
  mp                         Multiprocessing (TP/PP)
  rpc                        RPC backend (multi-node)

Options:
  -h,--help                  show this help
  -m,--model MODEL           model path or HuggingFace ID (default: Qwen/Qwen2.5-7B-Instruct)
  -p,--port PORT             API port (default: 8000)
  --tp SIZE                  tensor parallel size (default: 1)
  --pp SIZE                  pipeline parallel size (default: 1)
  --dp SIZE                  data parallel size (default: 1)
  --head-ip IP               head node IP for RPC mode (default: 127.0.0.1)
  --node-rank RANK           node rank for RPC mode (default: 0)

Examples:
  $PROGRAM                                    # single mode
  $PROGRAM ray                                # Ray backend
  $PROGRAM mp --tp 8                          # TP=8
  $PROGRAM mp --tp 4 --pp 2                   # TP=4, PP=2
  $PROGRAM rpc --head-ip 10.0.0.1 --node-rank 0 --tp 8 --dp 2  # head
  $PROGRAM rpc --head-ip 10.0.0.1 --node-rank 1 --tp 8 --dp 2  # worker

EOF
}

# 启动单人模式
launch_single() {
  info "Starting single mode..."
  vllm serve "${MODEL}" \
    --host 0.0.0.0 \
    --port "${PORT}" \
    --gpu-memory-utilization 0.9
}

# 启动Ray后端
launch_ray() {
  info "Starting Ray backend (TP=${TP}, PP=${PP}, DP=${DP})..."
  local gpus
  gpus=$(nvidia-smi -L | wc -l)
  ray start --head --port=6379 --num-gpus="${gpus}" --disable-usage-stats
  trap "ray stop" EXIT

  vllm serve "${MODEL}" \
    --host 0.0.0.0 \
    --port "${PORT}" \
    --tensor-parallel-size "${TP}" \
    --pipeline-parallel-size "${PP}" \
    --data-parallel-size "${DP}" \
    --data-parallel-backend ray \
    --gpu-memory-utilization 0.9
}

# 启动multiprocessing模式
launch_mp() {
  info "Starting multiprocessing (TP=${TP}, PP=${PP}, DP=${DP})..."
  local args=(
    --host 0.0.0.0
    --port "${PORT}"
    --gpu-memory-utilization 0.9
  )
  [ "${TP}" -gt 1 ] && args+=(--tensor-parallel-size "${TP}")
  [ "${PP}" -gt 1 ] && args+=(--pipeline-parallel-size "${PP}")
  [ "${DP}" -gt 1 ] && args+=(--data-parallel-size "${DP}")

  vllm serve "${MODEL}" "${args[@]}"
}

# 启动RPC后端
launch_rpc() {
  if [ "${NODE_RANK}" -eq 0 ]; then
    info "Starting RPC head (TP=${TP}, PP=${PP}, DP=${DP})..."
    local args=(
      --host 0.0.0.0
      --port "${PORT}"
      --data-parallel-address "${HEAD_IP}"
      --data-parallel-rpc-port 13345
      --gpu-memory-utilization 0.9
    )
    [ "${TP}" -gt 1 ] && args+=(--tensor-parallel-size "${TP}")
    [ "${PP}" -gt 1 ] && args+=(--pipeline-parallel-size "${PP}")
    [ "${DP}" -gt 1 ] && args+=(--data-parallel-size "${DP}")

    vllm serve "${MODEL}" "${args[@]}"
  else
    info "Starting RPC worker rank ${NODE_RANK} (TP=${TP}, PP=${PP}, DP=${DP})..."
    local args=(
      --data-parallel-address "${HEAD_IP}"
      --data-parallel-rpc-port 13345
      --headless
      --gpu-memory-utilization 0.9
    )
    [ "${TP}" -gt 1 ] && args+=(--tensor-parallel-size "${TP}")
    [ "${PP}" -gt 1 ] && args+=(--pipeline-parallel-size "${PP}")
    [ "${DP}" -gt 1 ] && args+=(--data-parallel-size "${DP}")

    vllm serve "${MODEL}" "${args[@]}"
  fi
}

# 根据模式启动vLLM服务器
launch() {
  local mode="$1"

  case "$mode" in
    single) launch_single ;;
    ray) launch_ray ;;
    mp) launch_mp ;;
    rpc) launch_rpc ;;
    *)
      err "Unknown mode: $mode"
      usage
      return 1
      ;;
  esac
}

while (( "$#" )); do
  case "$1" in
    -h|-\?|--help) usage; exit 0 ;;
    -m|--model) MODEL="$2"; shift 2 ;;
    -p|--port) PORT="$2"; shift 2 ;;
    --tp) TP="$2"; shift 2 ;;
    --pp) PP="$2"; shift 2 ;;
    --dp) DP="$2"; shift 2 ;;
    --head-ip) HEAD_IP="$2"; shift 2 ;;
    --node-rank) NODE_RANK="$2"; shift 2 ;;
    --*=|-*) err "unsupported option $1"; exit 1 ;;
    *) MODE="$1"; shift ;;
  esac
done

if ! launch "${MODE}"; then
  exit 1
fi
