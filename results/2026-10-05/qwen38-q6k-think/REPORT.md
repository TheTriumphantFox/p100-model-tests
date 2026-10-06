# Qwen3.8-27B UD-Q6_K: 126k context with nothing on CPU (2026-10-05)

Follow-up to `../qwen38-27b-spill/`. The Q8_0 only reached 64k by putting 8 blocks on CPU, at
16.5 t/s. The user approved downloading a smaller quant of the same model instead.

**File:** `unsloth/Qwen3.8-27B-GGUF` / `Qwen3.8-27B-UD-Q6_K.gguf`, 21.98 GB, built-in MTP head.
SHA-256 `c9c20681…3cd436` matches HF. It is at `~/models/qwen3.8-27b-unsloth_ud-q6_k.gguf`, fetched by
`~/models/_dl-q38-q6k/get.sh`. That repo's Q8_0 hashes identical to the one already on disk, so this
is the same model at a lower quant.

**Preset** `[qwen3.8-27b-q6-mtp]` on `:8080` is the Q8 preset's setup: tensor split, MTP n-max 4,
f16 KV, `fit = off`, and the 2026-10-04 anti-loop fix (temp 1.0, top-p 0.95, top-k 20, min-p 0,
reasoning-effort medium, reasoning-budget 6144). Shim tag `qwen3.8-27b:ud-q6k-prod`.

## Measurements (`check.py`: 3 decode prompts ×512 at temp 0, then a fill to ctx−1024 plus 512 generated)

| run | ctx | VRAM peak (MiB/card) | decode t/s (3 prompts) | MTP acceptance | deep decode | prefill |
|---|---:|---|---|---|---:|---:|
| UD-Q6_K | 131072 | 15814 / 15811 (570 free) | 28.2 (28.0 / 24.6 / 32.0) | 0.58 / 0.48 / 0.70 | 29.6 | 139.7 (fill 949 s) |
| UD-Q6_K | 40960 | 12676 / 12673 | 28.1 (27.9 / 24.6 / 31.9) | 0.58 / 0.48 / 0.70 | 37.1 | 183.9 |
| Q8_0, all GPU | 40960 | 15902 / 15899 | 32.9 (33.5 / 27.8 / 37.4) | 0.59 / 0.45 / 0.69 | 43.1 | 187.6 |
| Q8_0, 8 blocks on CPU (spill test) | 65536 | 15660 / 15657 | 16.5 | | 22.2 | 94.7 |

The 40k rows were run without the anti-loop sampling (temporary presets, since removed). The
decode prompts use temp 0 either way.

- VRAM at peak equals VRAM at load: the KV is allocated up front, and nothing grew during the fill.
- 570 MiB free is under the 600 MiB floor used for every other preset, so production runs at
  **129024 (126k)**. That is 2048 tokens × 68 KiB less, ~68 MiB/card, so ~640 MiB free. Smaller
  context can only use less memory, so it was not re-probed.
- Q6_K decodes ~15% slower than Q8_0 at the same context, even though it reads 24% fewer bytes. The
  likely cause is K-quant dequantization on Pascal (sm_60), which is not measured here. Its speed is
  flat from 40k to 128k.
- The "43 t/s" quoted for the Q8 earlier today was its deep-context figure; on these prompts it is 33.

## Applied

- `~/llama-cuda12/models.ini`: `[qwen3.8-27b-q6-mtp]`, ctx 129024 (backups
  `models.ini.bak-pre-q6k-2026-10-05`, and `models.ini.bak-pre-tmp` here).
- `~/.pi/agent/models.json`: entry "· 126k", contextWindow 129024, maxTokens 12288.
  `settings.json`: the same compaction override as the Q8 (reserve 16384, keep 12000). Backups
  `*.bak-pre-q6k-2026-10-05`. `../max-context/pi_check.py`: all 5 entries OK.
- `~/Projects/Tests/scripts/ollama_shim.py`: TAGS `qwen3.8-27b-q6-mtp` → `qwen3.8-27b:ud-q6k-prod`.
- The Q8 64k preset `[qwen3.8-27b-mtp]` is left as it is, for comparison.

Thinking-on accuracy with the fix: `../think-fix-full/` (scheduled 21:00).

Files: `probe_ctx.sh`, `ab40k.sh`, `check.py`, `watchdog.sh`, `driver.log`, `last-*.json`, `results.jsonl`.
