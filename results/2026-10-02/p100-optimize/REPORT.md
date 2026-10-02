# P100 optimisation — 2026-10-02

Trying the dual-P100 tuning ideas from the 2026-10-01 research on the stock build
`~/llama-cuda12` (llama.cpp 50631b3, 2026-09-18). No fork, no rebuild, no system
settings changed, production services untouched.

Hardware as found: 2× Tesla P100-PCIE-16GB, no NVLink (PCIe card has no connector),
GPU0 at Gen3 x16, **GPU1 at Gen3 x4**, topology PHB (through the Ryzen 7600X root complex).
Under load both cards boost to 1328 MHz by themselves, so raising application clocks would
change nothing.

## Headline

| model (planner tasks, temp 0, grammar) | before | after | how |
|---|---:|---:|---|
| qwen3.6-35b-a3b UD-Q6_K (current planner) | 52.7 t/s | **66.0 t/s** (+25%) | `-sm tensor` |
| qwen3.8-27b Q8_0 (dense) | ~10.9 t/s | 18.4 t/s (+69%) | `-sm tensor` |
| qwen3.8-27b Q8_0 (dense) | ~10.9 t/s | **49.1 t/s** (4.5×) | `-sm tensor` + MTP head, n-max 4, `-ub 256` |

Every configuration kept its output correct (scored by the planner-bench validator).

## 1. Tensor split works, but only with NCCL P2P off

`-sm tensor` (llama.cpp's experimental tensor parallelism) **hangs on the first token** with
default NCCL: both cards show 100% utilisation at 37 W with no memory traffic. The driver
reports P2P as OK (`nvidia-smi topo -p2p r`), but peer DMA between these slots does not
work in practice — typical for AMD consumer boards, especially with one card behind a
chipset-attached x4 slot. `NCCL_P2P_DISABLE=1` routes the all-reduce through host shared
memory (`via SHM/direct/direct`) and everything works. This is the deadlock recorded on
2026-09-18 in `devstral-p100-bandwidth` (same 37 W spin). That report ruled out P2P
because the driver says OK; disabling it in NCCL is what fixes it. `GGML_CUDA_P2P=1` made no
difference either way.

llama-bench, f16 KV, `-fa on`, 3 reps (stddev < 1%):

| model | decode layer → tensor | prefill pp512 layer → tensor |
|---|---|---|
| qwen3.6-35b-a3b UD-Q6_K | 54.0 → **67.7** (+25%) | 468 → **732** (+56%) |
| … at 16k depth | 51.9 → **65.2** | 373 → **600** |
| qwen3.8-27b Q8_0 | 10.9 → **18.6** (+71%) | 145 → **217** (+50%) |
| … at 8k depth | 10.7 → **18.3** | 137 → **210** |
| qwen3.8-27b Q4_K_M | 12.4 → **20.5** | 141 → 205 |
| qwen3.6-27b Q5_K_M | 11.1 → **18.8** | 143 → 218 |
| gpt-oss-20b Q8_0 | 67.0 → **100.4** (+50%) | 506 → **842** |

VRAM is unchanged (planner at 32k ctx: 14.9/14.3 GB layer vs 14.6/14.6 GB tensor).
Limits: tensor mode needs `-fa on` and an f16/bf16/f32 KV cache, the llama.cpp docs still
call it experimental, and `--fit` is not implemented for it (harmless warning).

## 2. The q8_0 KV cache on :8080 costs decode speed

The :8080 router runs `--cache-type-k q8_0 --cache-type-v q8_0`. On the planner at 16k
depth that is 45.8 t/s against 51.9 with f16 (−12%), with no prefill difference. It is
also incompatible with tensor split.

## 3. Speculative decoding: big win on dense, loss on MoE

Server runs: single-model `llama-server` on :8090, ctx 32768, planner-bench tasks with
pinned checks and thinking off (same as `drive_pinned.sh`).

**Dense qwen3.8-27b + its MTP head** (`mtp-Qwen3.8-27B-Q8_0.gguf`). Round 2 (2026-09-19,
`candidates-round2`) measured MTP at 1.79× and DFlash at 2.09× with layer split on general
prompts, 77–79% acceptance. On planner edits, 5 tasks (1.9–7.3 KiB rewrites + escaping +
injection):

| config | correct | decode | wall (5 tasks) | size-7500 wall |
|---|---|---:|---:|---:|
| tensor | 5/5 | 18.4 | 533 s | 175 s |
| tensor + MTP n-max 2 | 5/5 | 39.5 | 278 s | 90 s |
| tensor + MTP n-max 3 | 5/5 | 45.4 | 249 s | 81 s |
| tensor + MTP n-max 4, `-ub 256` | 5/5 | **49.1** | 227 s | 74 s |
| tensor + MTP n-max 4/6, `-ub 512` | — | OOM at load | | |
| Q4_K_M, tensor | 5/5 | 20.4 | 489 s | |
| Q4_K_M, tensor + MTP n-max 3 | 5/5 | 42.9 | 261 s | |
| Q4_K_M, tensor + MTP n-max 5 | 5/5 | 47.1 | 244 s | |
| Q4_K_M, layer + DFlash n-max 8 | 5/5 | 28.8 | 380 s | |

Large rewrites with the best config (Q8_0, tensor, MTP n-max 4, `-ub 256`):

| task | tokens | wall | 09-23 wall (layer, no MTP) |
|---|---:|---:|---:|
| size-10000-port | 3892 | 97 s | 386 s |
| size-13000-port | 5029 | 125 s | 498 s |
| size-15500-port | 6032 | 151 s | 598 s |
| escaping-timeout-7500 | 3029 | 76 s | 303 s |

All 4 correct, 48.6 t/s average, 99.3% draft acceptance. Every rewrite up to 15.5 KiB now fits the 240 s deadline (09-23: only up to 4.7 KiB).

Q8_0 + MTP n-max 4 sits at 15.86 GB per card at 32k context, so there is no headroom:
n-max 4 only loads with `-ub 256` (which also raised prefill to 241 t/s). Q4_K_M leaves
4 GB free per card, but its K-quant verify passes are slower, so Q8_0 still wins at equal
draft depth (45.4 vs 42.9 at n-max 3).

Draft acceptance is ~99.5% here against 77% on round 2's general prompts: the plan is
mostly a copy of the input file and the MTP head predicts it almost perfectly. That and
tensor split are why MTP now beats DFlash, the reverse of round 2. 4 of 5 outputs are byte-identical to the non-speculative run;
the fifth differs only in JSON whitespace (a near-tie at temp 0) and is also correct.

DFlash (`dflash-Qwen3.8-27B-Q8_0.gguf`) crashes under tensor split
(`GGML_ASSERT(meta_buf_ctx->bufs[i])` in ggml-backend-meta.cpp).

**MoE planner + n-gram drafting** (no draft model needed; the idea was that the plan copies
the prompt). It is a loss at every setting:

| config | decode | draft acceptance |
|---|---:|---|
| tensor, no speculation | **66.0** | — |
| + ngram-mod (defaults) | 43.1 | 12–34% |
| + ngram-simple (defaults n12/m48) | 37.4 | 19–40% |
| + ngram-simple n3/m8 | 35.5 | 30–48% |
| + ngram-simple n4/m16 | 36.9 | 42–55% |

Acceptance is limited because the file sits raw in the prompt but JSON-escaped in the
output, so matches break at every newline and quote. Even at 55% acceptance, verifying
multi-token batches on the MoE costs more than it saves — the same pattern gavinbrow saw.

## What this means for the planner choice

- Tensor split is a free +25% for the chosen MoE planner: the 15.5 KiB rewrite goes from
  127 s to 102 s, inside the 120 s deadline.
- Dense qwen3.8-27b, ruled out on 09-23 at ~11 t/s (31/40 within 240 s), now decodes at
  ~49 t/s with tensor split + MTP: the 15.5 KiB rewrite takes 151 s instead of 598 s.
  That is MoE-class speed from the model that scored 40/40 correct with 0 injections
  followed. It has only been run on 9 of the 40 tasks here (9/9 correct), so a full
  40-task run is the next step before it can be compared with the MoE planner.

## Not done

- No production change. Switching :8080/:8081 to `-sm tensor` needs `NCCL_P2P_DISABLE=1`
  in the service environment and f16 KV.
- Kmic-68's P100 fork (claims 32.6 t/s plain / 54 MTP on Qwen3.8-27B Q6_K, built for
  exactly this model) was not built: it is unreviewed third-party code.
- A full 40-task planner-bench run of qwen3.8 + tensor + MTP (roughly 45 min at these speeds).
- Fixing peer-to-peer (BIOS ACS/IOMMU settings, or moving GPU1 to a CPU-attached slot)
  might let NCCL use direct P2P and speed up tensor mode further. Untested.

## Files

- `bench.sh` — guarded llama-bench wrapper (refuses if the GPUs are in use), raw output in `raw/`.
- `serve_bench.sh` — single-model server on :8090 + planner-bench subset, output in `serve/`.
- `summ.py` — decode/prefill/correctness summary of `serve/*.json`.
- `phaseB4.sh` — MTP-depth and DFlash runs.
