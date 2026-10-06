# Fastest presets for the fast-tier models — 2026-10-04

The user asked for every model on the fast NVMe to run at its fastest tested config, and for pi
to drop any model in cold storage. All five pi llamacpp models already load from `~/models`, so
none were removed (the other pi models are cloud openai-codex).

Changed in `~/llama-cuda12/models.ini` (backup `models.ini.bak-pre-fastest-2026-10-04`) and
pi `~/.pi/agent/models.json` (backup `models.json.bak-pre-fastest-2026-10-04`):

| preset | change |
|---|---|
| qwen3.6-27b-abliterated | `split-mode = tensor`, MTP from `~/models/mtp-Qwen3.8-27B-Q8_0.gguf` (copied from candidates-r2, SHA 6447a4e9… matches), n-max 3, `-ts 54,46` removed, ctx 131072 → 114688 |
| qwen3.6-35b-a3b-planner | `split-mode = tensor` |
| qwen3.6-35b-a3b-planner-mtp | `split-mode = tensor` |
| qwen3.8-27b-mtp | unchanged (already tensor + MTP n-max 4) |
| qwen3.8-flash-next-iq2 | unchanged (tensor split cannot be combined with `--fit`; MTP needs the PR build) |

## Results (`check.py`, through the :8080 router, `results.jsonl`)

Decode = mean of 3 general prompts × 512 tokens, temp 0. Deep = 512 tokens after filling to ctx−1024.

| preset | ctx | decode | MTP acceptance | deep decode | prefill (full fill) | peak per card |
|---|---:|---:|---:|---:|---:|---:|
| abliterated (before: layer, no MTP) | 131072 | 9.3 (pi log) | — | — | ~150 | — |
| abliterated, tensor + MTP | 131072 | 29.6 | 62% | 28.5 | 140 | 16.12 GB, 0.26 GB free: rejected |
| **abliterated, tensor + MTP** | **114688** | **29.6** | 62% | 30.0 | 146 | 15.55 GB, 0.84 GB free |
| planner, tensor | 81920 | 66.8 | — | 59.0 | 495 | 15.23 GB |
| planner-mtp, tensor | 49152 | 83.7 | 65% | 101.3 | 544 | 15.54 GB |

On general prompts the MTP heads accept about 62–65% of drafts, compared with 95–99% on the
copy-heavy planner tasks of 10-02. So these numbers sit below the 40 / 111 tok/s planner-task
figures. The deep-decode filler is repetitive, which flatters MTP (planner-mtp 101).
The router's `--ubatch-size 512` on the command line overrides presets, so `-ub 256` (which would
save VRAM) cannot be set per model without editing serve-devstral.sh.
