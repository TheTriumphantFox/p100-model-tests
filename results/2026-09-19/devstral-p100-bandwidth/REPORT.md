# Devstral Small 2 Q8_0 P100 memory-bandwidth and KV-cache study

Run date: 2026-09-19 (HBM2 ceiling and split-mode A/B measured 2026-09-18)

## Test setup

- Model: `devstral-patched` (Devstral Small 2 24B Instruct Q8_0, 25.05 GB)
- `~/llama-cuda12` llama.cpp build, CUDA 12.6 / sm_60, commit `50631b3`
- Two Tesla P100-PCIE-16GB, layer split, flash attention on, `--parallel 1`, batch/ubatch 512
- `llama-devstral.service` stopped for every run; restored afterwards
- Every prompt freshly randomized — both backends prefix-cache, so a repeated prompt
  reports nonsense prefill numbers

## Hardware ceiling, not the nameplate

`hbm_bandwidth.cu` (sm_60, `-cudart static`, 256 MiB buffers so it runs beside the live server):

| | GPU0 | GPU1 | vs 732 GB/s nameplate |
|---|---:|---:|---:|
| pure read | 598.9 | 599.4 | 82% |
| copy (r+w) | 519.5 | 520.3 | 71% |
| `cudaMemcpy` D2D | 509.0 | 538.5 | 70-74% |

**599 GB/s is the figure weight streaming should be compared against.** Bytes read per token,
from the GGUF tensor table: blocks 23.62 GB + `output.weight` 0.71 GB = **24.33 GB**
(`token_embd` is a one-row gather, not a stream). Generation at 78.7 ms/token is therefore
**309 GB/s — 52% of achievable**, correcting an earlier back-of-envelope figure of ~177 GB/s.

## Multi-GPU split modes

| mode | result |
|---|---|
| `layer` (current) | 12.72 tok/s gen, 274 tok/s prefill |
| `row` | **fails to load** — `device CUDA0 does not support split buffers`; the CUDA backend at this commit exports no `ggml_backend_cuda_split_buffer_type` |
| `tensor` (experimental) | **deadlocks** — loads in 6 s, then never serves; both GPUs pin at 100% utilization drawing 37 W (idle power), i.e. a device-side spin barrier. Reproduced at ctx 49152 and 4096, with and without `--no-warmup`. P2P is OK both directions (PHB), so that is not the cause |
| `layer`, `--parallel 2` | 12.56 + 12.56 = **23.36 tok/s aggregate**, -1.2% per stream |

The `--parallel 2` result is not the idle card being filled — llama.cpp batches both slots into
one decode step, so the second token rides along on the same weight read. That a whole extra
token costs 1.2% is the proof the decode step is **weight-streaming-bound**.

## KV cache type

| KV | ctx | gen @~0 | prefill | gen @13.4k | gen @27.8k |
|---|---:|---:|---:|---:|---:|
| q8_0 | 49152 (live) | 12.72 | 274 | 11.13 | **9.75** |
| **f16** | **32768** | **12.88** | 274 | **12.26** | **11.68** |
| K f16 / V q8_0 | 40960 | 12.79 | 273 | 11.29 | ~10.0 (extrapolated) |
| K q8_0 / V f16 | 40960 | 12.77 | 275 | 11.28 | ~10.0 (extrapolated) |
| f16 | 40960 | 11.15 | 166 | — | spilled layers to CPU |
| f16 | 40960 `-fitt 256` | 12.87 | **OOM** | — | loads, dies on first prefill |

Taking the marginal cost of context depth as the KV read rate: **f16 reads KV at 546 GB/s**
(91% of the 599 GB/s ceiling), **q8_0 at 104 GB/s**, either mixed pairing at ~162 GB/s. It is
binary — any q8_0 in the cache puts the flash-attention kernel on the slow path, and halving
the bytes does not come close to paying for 5.3x worse kernel efficiency. Mixed K/V is useless.

f16's ceiling is 32768 and it is firm: at 40960 the fitter's default 1 GiB/device margin is
breached and layers spill to CPU; cutting the margin to 256 MiB loads and generates at full
speed, then aborts in `ggml_cuda_mul_mat_cublas_impl` on the first real prefill — the margin
exists for the cuBLAS workspace.

## Conclusion — live config unchanged

f16 @ 32k is 20% faster at working depth, but with pi's `reserveTokens: 8192` a 32768 window
compacts at 24,576 against a ~23.5k prompt floor, leaving about 1k of working room. The service
stays **q8_0 @ 49152**; f16 @ 32768 is the right profile for short-context one-shot work.

Separately, pi's `devstral-patched` entry was serving a `contextWindow` of 65536 against a
server window of 49152 and was corrected to 49152.

A bandwidth model of `24.33 GB + (depth x KV bytes/token)` divided by the rates above predicted
both deep-context measurements within 1%.

Raw per-run JSON and server logs are in this directory; `kv_ab_2026-09-19.{sh,py}` is the
harness as run, and the reusable copies are `scripts/kv_ab.sh`, `scripts/hbm_bandwidth.cu` and
`scripts/gguf_active_bytes.py`.
