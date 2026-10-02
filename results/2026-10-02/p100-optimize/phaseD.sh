#!/usr/bin/env bash
# The two unsloth MTP GGUFs downloaded 2026-10-02: the planner's twin and the stock Qwen3.6-27B.
cd "$(dirname "$0")"
until grep -q PHASE_DONE serve/phaseC.txt; do sleep 10; done
P=~/models/_mtp-dl/planner/Qwen3.6-35B-A3B-UD-Q6_K.gguf
Q=~/models/_mtp-dl/q36-27b/Qwen3.6-27B-Q5_K_M.gguf
T5="size-2000-port size-5000-port size-7500-port escaping-banner injection-retarget"
export GGML_ENV=NCCL_P2P_DISABLE=1
B=(-fa on -sm tensor)
./serve_bench.sh d-plannermtp-tensor $P "$T5" "${B[@]}"
./serve_bench.sh d-plannermtp-tensor-mtp2 $P "$T5" "${B[@]}" --spec-type draft-mtp --spec-draft-n-max 2
./serve_bench.sh d-plannermtp-tensor-mtp3 $P "$T5" "${B[@]}" --spec-type draft-mtp --spec-draft-n-max 3
./serve_bench.sh d-plannermtp-tensor-mtp4 $P "$T5" "${B[@]}" --spec-type draft-mtp --spec-draft-n-max 4
./serve_bench.sh d-q36stock-tensor $Q "$T5" "${B[@]}"
./serve_bench.sh d-q36stock-tensor-mtp3 $Q "$T5" "${B[@]}" --spec-type draft-mtp --spec-draft-n-max 3
./serve_bench.sh d-q36stock-tensor-mtp4 $Q "$T5" "${B[@]}" --spec-type draft-mtp --spec-draft-n-max 4
./summ.py serve/d-*.json
echo PHASE_DONE
