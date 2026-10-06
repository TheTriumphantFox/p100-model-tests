# pi: Patriot-only models, context sized and truncation-checked — 2026-10-02 evening

pi now lists only the models whose weights are on the Patriot NVMe (`~/models`), all through
the :8080 llama.cpp router. Ollama (every model on the Seagate) is gone from pi.

During the session a peer session demoted devstral, gpt-oss-20b, K2 Horizon and the stock
Qwen3.6-27B MTP file to `/var/lib/ollama/archive` (19:09–19:31) and repointed the router
symlinks. So those are no longer Patriot models and are not in pi. devstral-cuda stays in the
router unchanged (49152, q8_0 KV) for its other users.

## Result

2× P100 16 GB, layer split, flash attention, `--parallel 1`, `-ub 512`. Peak = nvidia-smi peak
while filling the context to ctx−1024 and generating 512 tokens (`verify.py`).

| pi model (router id) | ctx before | ctx now | KV | peak GB/card | free on tighter card | prefill / decode at that depth |
|---|---:|---:|---|---|---:|---|
| qwen3.6-27b-abliterated (`-ts 54,46`) | 32k (Ollama) | **131072** | f16 | 15.26 / 14.45 | 1.1 GB | 125 / 8.1 tok/s at 130k |
| qwen3.6-35b-a3b-planner | 48k (router, not in pi) | **81920** | f16 (was q8_0) | 15.66 / 15.01 | 0.7 GB | 473 / 45 tok/s at 81k |
| qwen3.6-35b-a3b-planner-mtp (n-max 3) | not served | **49152** | f16 | 15.31 / 15.80 | 0.6 GB | 347 / 77 tok/s at 48k |
| qwen3.8-flash-next-iq2 (`--fit` on, experts on CPU) | not served | **131072** | f16 | 15.20 / 15.24 | fit-managed | 131 / 17.0 tok/s, 8k prompt only |

Every model refused a ctx+256 prompt with HTTP 400 `exceeds the available context size`, a
pattern pi recognizes as overflow, so it compacts and retries instead of losing text.

Ceilings found by load test (`loadtest.sh`, `--fit off -ngl 999`): planner 96k loads, but
leaves 0.5 GB and 128k OOMs. MTP twin 64k leaves 0.4 GB. Load success alone is not enough:
devstral at 64k q8_0 loaded and then OOMed in warmup, so every pick keeps ≥0.6 GB free.

## Truncation findings, fixed

1. **pi's compaction reserve (8192) was smaller than maxTokens (16384).** pi compacts when
   context > contextWindow − reserveTokens, so a reply begun just under that line could
   need 16k tokens with only 8k left and get cut off at n_ctx. Fixed: `reserveTokens` = 20480,
   i.e. 16k of output plus 4k of slack for pi's chars/4 estimate of fresh tool output.
   (pi does recover from a `length` stop by compacting and retrying, but that wastes a turn.)
2. **The router's command-line `--ctx-size`/`--cache-type-*` override per-model presets.**
   They were moved into `[*]` in `~/llama-cuda12/models.ini`, and the CLI no longer passes them.
3. **`--fit` (on by default) keeps 1 GiB free per card** and would silently move layers to CPU
   at these sizes (a speed loss, not truncation). Every GPU-resident preset sets `fit = off`.
4. **Ollama truncates silently** (it drops the start of prompts longer than `num_ctx`, with
   no error). Removing it from pi removes that path.

## Not done / caveats

- Flash-Next was filled to 8k, not 128k (that would take ~17 min of prefill). Fit sizes the
  full KV at load, and on every other model the full-fill peak was within 0.3 GB of the load
  footprint.
- The 27B at full 128k is slow in practice: 17 min to prefill from cold, 8 tok/s at that
  depth. Prompt caching makes later turns incremental.
- Tensor split (+25–70% speed, needs `NCCL_P2P_DISABLE=1`) was not applied; it is a separate
  service change ([p100-optimize](../p100-optimize/REPORT.md)).

## Files changed (backups beside each)

- `~/llama-cuda12/models.ini` (new): per-model presets.
- `~/llama-cuda12/serve-devstral.sh`: adds `--models-preset` and drops the CLI ctx/KV flags
  (`.bak-pre-presets-2026-10-02`). Service restarted at idle.
- `~/.pi/agent/models.json`: llamacpp provider only, 4 models, `thinkingFormat:
  qwen-chat-template` (`.bak-pre-patriot-2026-10-02`).
- `~/.pi/agent/settings.json`: default `llamacpp/qwen3.6-27b-abliterated`,
  `compaction.reserveTokens` 20480 (`.bak-pre-patriot-2026-10-02`).

## Addendum, same evening: Qwen3.8-27B promoted, every model called through pi

- **Promoted** `~/Downloads/Models/Qwen3.8-27B-Q8_0.gguf` (unsloth, built-in MTP head, 29.0 GB)
  to `~/models/qwen3.8-27b-unsloth_q8_0.gguf` by copying it. Both copies hash to SHA-256
  `a680f44a06920e5d689774823782006aa3acc8db95750323373b24139b67e348`, the same as Hugging Face's
  hash. The HDD original stays as the archive copy. Chosen over the HauhauCS Q6_K_P, stock
  Q4_K_M and ggml-org Q8_0 + MTP file because it had 40/40 on the planner bench and the fastest
  MTP among the built-in heads (48.8 tok/s), with no separate draft file using VRAM.
- **Router id `qwen3.8-27b-mtp`**: tensor split + MTP n-max 4, 40960 ctx, f16 KV. A full
  fill (39,936 + 512) gave 180 tok/s prefill and 43 tok/s decode, with a peak of 15.90/15.90 GB
  (0.48 GB free, the thinnest margin here, but at the worst case). 48k leaves 0.45 GB at load,
  and 64k OOMs.
- **Second CLI-override trap**: the router's `--split-mode layer` beat the preset's `tensor`, so
  split-mode moved into `[*]` too. `serve-devstral.sh` exports `NCCL_P2P_DISABLE=1`, which
  only tensor-split presets use.
- **pi**: maxTokens 12288 for this model, with `compaction.modelOverrides` reserve 16384 /
  keepRecent 12000, so history gets 24k of the 40k.
- **pi calls** (`pi-calls.txt`): `pi -p --model llamacpp/<id>` for all five models. Each
  answered and loaded at the verified ctx/split/VRAM. Each also ran pi's bash tool and returned
  a random token it could only get from `cat secret.txt`, and all five matched.
