# qwen3.8-27b-mtp: raising context past 40k by spilling to CPU (2026-10-05)

Model: `qwen3.8-27b-unsloth_q8_0.gguf` (29.0 GB, built-in MTP head) on 2× P100 16 GB, tensor
split, MTP n-max 4, f16 KV, through the `:8080` router with `check.py` (3 decode prompts of 512
tokens at temp 0, then a fill to ctx−1024 plus 512 generated). `watchdog.sh` killed the model if
host MemAvailable fell under 6 GiB; it never fired.

Why spill: the weights take 29 of the 32 GB. The model has 65 blocks, but only 17 hold a KV cache
(every 4th block plus the MTP block); the rest are linear-attention state. So KV is 68 KiB/token
at f16, split across both cards, and the 40k preset already peaked at 15.90 GB per card.

| probe | ctx | KV | on CPU | VRAM at peak (MiB/card) | decode t/s | prefill t/s | result |
|---|---:|---|---|---|---:|---:|---|
| baseline (preset before) | 40960 | f16 | nothing | 15902 | 32.9 (33.5 / 27.8 / 37.4; 43.1 deep) | 188 | measured later the same day, `../qwen38-q6k-think/` |
| A | 131072 | f16 | FFN of blocks 40–63, mmap | 15740 at load | 8.3 / 7.1 / 9.5 | 52 (CPU-bound, 540% CPU) | aborted during fill, too slow |
| B | 81920 | q8_0 | nothing | — | — | — | CUDA OOM at first prompt (`ggml_cuda_pool_vmm::alloc` in cuBLAS mul_mat) |
| **C** | **65536** | f16 | FFN of blocks 56–63, `load-mode = none` | **15660 / 15657** (724 free) | **16.3 / 14.0 / 19.1** (mean 16.5; 22.2 deep) | **94.7** | **pass**, fill 704 s, HTTP 200 |

Notes:
- Each spilled block frees ~135 MiB per card and costs ~4–5 ms per pass: its FFN is read from
  DDR5 every pass (~0.26 GiB at ~60 GB/s), on top of a GPU↔CPU round trip. MTP can't amortize
  that the way it does on the GPUs. 8 blocks (12% of the weights) cost ~50% of the decode speed (32.9 → 16.5 on the same prompts).
- `load-mode = none` (no mmap for the CPU tensors) roughly doubled prefill against probe A; the
  loader itself suggests it whenever tensor overrides put weights on CPU.
- q8_0 KV halves the cache on paper, but at 80k the first prompt runs out of VRAM. That fits the
  attention path converting the quantized cache back to f16 in context-sized scratch buffers, so
  it is not a free 2× here (inferred from the crash site, not measured).
- `backend sampling not supported with SPLIT_MODE_TENSOR; using CPU` is printed for every tensor
  split load and is not specific to the spill.

## Applied

- `~/llama-cuda12/models.ini` `[qwen3.8-27b-mtp]`: `ctx-size = 65536`, the `override-tensor` for
  blocks 56–63, `load-mode = none` (backup `models.ini.bak-pre-spill` here).
- `~/.pi/agent/models.json`: `contextWindow 65536`, name "· 64k" (backup
  `models.json.bak-pre-27b-64k-2026-10-05`). `pi_check.py` (in `../max-context/`): all four
  llamacpp entries OK.
- pi budget for this model: reserve 16384 and maxTokens 12288, so compaction starts at 49152 and the
  worst case uses 61440 of 65536. After a compaction a session sits at ~23k (8.8k prompt floor +
  12k kept + summary), so it no longer re-compacts every turn as it did at 40k.
- A cold 49k-token prompt takes ~525 s (load + prefill at ~95 t/s), inside pi's 600 s
  `retry.provider.timeoutMs`.

## Better route (taken later the same day)

A stock Qwen3.8-27B Q5_K_M/Q6_K with the MTP head (~19–22 GB) would leave 10–13 GB for KV: 128k with
no spill. Done the same day: UD-Q6_K, 126k, 28 t/s on these prompts. See `../qwen38-q6k-think/`. The only other
quant on disk is HauhauCS Uncensored-Aggressive Q6_K_P (25.9 GB). That is a different fine-tune,
and it frees only ~3 GB.

Files: `run.sh` (probe driver), `set_preset.py`, `watchdog.sh`, `check.py`, `driver.log`,
`watchdog.log`, `results.jsonl`, `last-*.json`, `run-*.out`.
