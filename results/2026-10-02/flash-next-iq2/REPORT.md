# qwen3.8-flash-next IQ2_XXS — 2026-10-02

A for-fun follow-up to `2026-09-19/qwen3.8-flash-next` (UD-IQ3_XXS, 82 GB, 5.3 tok/s steady).

- **File:** `bartowski/Qwen3.8-Flash-Next-GGUF`, `Qwen3.8-Flash-Next-IQ2_XXS` (2 splits, 75.2 GB),
  SHA-256 verified against Hugging Face, in `~/models/qwen3.8-flash-next_iq2_xxs/`.
  Unsloth publishes no UD-IQ2; its nearest are UD-IQ1_M (74.5 GB) and UD-Q2_K_XL (78.9 GB).
  Even IQ1 is 70+ GB because the ~22.5 GB embedding stays high precision.
- **Runtime:** stock `~/llama-cuda12` (50631b3), `llama-server -c 8192 -fa on`, all defaults.
  `--fit` (on by default) put experts on CPU by itself and filled each card to 15.2 GB.
  Loaded in 29 s from the NVMe.
- **Method:** `probe.py`, 48 distinct prompts (the 24 from 09-19 plus 24 new), 128 tokens,
  temp 0, thinking off; the first 24 warm up, the last 24 are measured.

## Result

| | 09-19 UD-IQ3_XXS (Ollama) | 10-02 IQ2_XXS (llama.cpp) |
|---|---:|---:|
| generation, steady | 5.3 tok/s | **19.2 tok/s** (17.9–19.7) |
| prompt | 6.7 tok/s | **26.7 tok/s** |
| page cache at steady state | ~35 GB, still churning | 32.6 GB, stable |

Answers are coherent (correct methods, valid code). Accuracy was not scored.

**Confound:** two things changed at once, the quant (82 → 75 GB) and the runtime (Ollama →
llama.cpp with `--fit` expert offload). Their shares cannot be separated without re-downloading
the IQ3_XXS. The 7 GB saving is probably what lets the RAM-resident part (~33 GB) fit with
headroom instead of churning, but that is inferred, not measured. The page cache was also
partly warm from the SHA-256 pass, so the warm-up phase is shorter than a cold start would be.

Not tried: tensor split, manual `--n-cpu-moe` tuning, MMLU-Pro (09-19's IQ3_XXS: 70.0%).
