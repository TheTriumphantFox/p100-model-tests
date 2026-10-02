#!/usr/bin/env bash
# Overnight extension: once the 10-hour run has finished, take the top 3 models and keep
# them going down the SAME exercise order until a hard wall-clock stop (06:00 by default).
#
# Same run folder on purpose: the first 25 exercises are reused, every model reaches the
# same end index, and the extension stays paired with the original five-model prefix.
#
# Top 3 = best pass@2 on the common 25 (ties: pass@1, then faster). The end index is set
# from MEASURED seconds per exercise, so all three get the same exercises.
set -uo pipefail
R=/home/hm/Projects/Tests/2026-10-01/aider-polyglot-10h
STOP_AT=${STOP_AT:-"2026-10-02 06:00:00"}
HARD_END=$(date -d "$STOP_AT" +%s)
cd "$R"
log() { echo "[$(date +'%F %T')] $*" | tee -a "$R/driver.log"; }

log "extension armed: waits for the resumed run to finish, then top 3 until $STOP_AT"
until grep -q '=== finished at .* (resumed run)' "$R/driver.log"; do sleep 60; done
sleep 30   # let the router finish releasing VRAM

PLAN=$(python3 - "$HARD_END" <<'EOF'
import json, sys, time
hard_end = int(sys.argv[1])
order = [l.strip() for l in open("order.txt") if l.strip()]
ms = ["gpt-oss-20b_q8_0", "qwen3.6-35b-a3b_ud-q6_k", "devstral-patched_q8_0",
      "qwen3.6-27b-abliterated_q5_k_m", "qwen3.8-27b-unsloth_q8_0"]
d = {m: {json.loads(l)["exercise"]: json.loads(l) for l in open(f"runs/{m}/progress.jsonl")} for m in ms}
common = [e for e in order if all(e in d[m] for m in ms)]
def key(m):
    rows = [d[m][e] for e in common]
    wall = sum(r["wall_s"] for r in d[m].values()) / len(d[m])
    return (-sum(r["pass"] for r in rows), -sum(bool(r["outcomes"] and r["outcomes"][0]) for r in rows), wall)
top = sorted(ms, key=key)[:3]
mean = {m: sum(r["wall_s"] for r in d[m].values()) / len(d[m]) for m in top}
loads = {}
for l in open("preflight.jsonl"):
    if l.strip().startswith("{"):
        r = json.loads(l); loads[r["model"]] = r["wall_s"]
done = max(len(d[m]) for m in top)
usable = hard_end - time.time() - sum(loads.get(m, 60) for m in top) - 300
extra = max(0, int(usable // sum(mean.values())))
end = min(225, done + extra)
# Fastest first: its slack rolls forward to the slower models' deadlines.
top.sort(key=lambda m: mean[m])
print(" ".join(top), end, len(common),
      " ".join(f"{m}:{-key(m)[0]}/{len(common)}:{mean[m]:.0f}s" for m in top))
EOF
)
read -r M1 M2 M3 E NCOMMON DETAIL <<< "$PLAN"
log "extension plan: top 3 on $NCOMMON common = $DETAIL; target end index $E, hard end $STOP_AT"
if [ -z "${E:-}" ] || [ "$E" -le 25 ]; then
  log "!!! extension skipped: no time left for even one more round (E=${E:-?})"; exit 0
fi
RESUME_E=$E MODELS="$M1 $M2 $M3" HARD_END=$HARD_END exec bash "$R/drive.sh" >> "$R/drive.out" 2>&1
