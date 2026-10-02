# Speed sweep, all local models — 2026-10-02 13:03–13:40

Every model on the shelf that loads on llama.cpp, in one session. `llama-bench` pp512 + tg128,
f16 KV, flash attention on, 3 repetitions; tensor split with `NCCL_P2P_DISABLE=1` (see
`../p100-optimize/REPORT.md`). Main build `~/llama-cuda12` (50631b3); K2 Horizon on its fork
build `~/llama-cuda12-k2h`; g9v3 on `~/llama-cuda12-g9v3` (the main build cannot load it).
The :8080 devstral service was stopped for the sweep and restarted afterwards.

| model | decode layer | decode tensor | gain | prefill layer | prefill tensor |
|---|---:|---:|---:|---:|---:|
| qwen3.6-35b-a3b UD-Q6_K (planner) | 54.0 | 67.7 | +25% | 467.5 | 731.7 |
| qwen3.6-27b-abliterated Q5_K_M | 11.1 | 18.8 | +70% | 143.2 | 210.5 |
| devstral-patched Q8_0 | 12.9 | 22.3 | +73% | 174.7 | 391.1 |
| gpt-oss-20b Q8_0 | 67.0 | 100.4 | +50% | 504.8 | 842.2 |
| k2-horizon-7b Q8_0 | 35.0 | 55.9 | +60% | 703.1 | 873.0 |
| qwen3.8-27b Q8_0 (ggml-org) | 10.8 | 18.6 | +72% | 142.4 | 218.0 |
| qwen3.8-27b Q8_0 (unsloth) | 10.9 | 18.6 | +70% | 143.0 | 217.6 |
| qwen3.8-27b Q6_K_P (HauhauCS) | 9.9 | 17.1 | +73% | 145.9 | 222.4 |
| qwen3.8-27b Q4_K_M | 12.4 | 20.5 | +66% | 140.3 | 207.3 |
| qwen3.8-27b-stock Q4_K_M | 12.1 | 20.2 | +67% | 140.2 | 212.3 |
| ornith-1.5-35b-a3b Q4_K_M | 54.3 | 67.1 | +24% | 457.6 | 716.1 |
| g9v3-39a5b Q4_K_M | 39.2 | 51.1 | +30% | 276.2 | 459.1 |
| qwen3.8-flash-next IQ2_XXS (server, 24 distinct prompts) | 19.3 | not supported | — | 26.8 | — |

Tensor split gains: +24–30 % on the MoE models (planner, Ornith, g9v3), +50–60 % on gpt-oss and
K2 Horizon, +66–73 % on every dense 24–27B. Devstral, the :8080 production model, goes from
12.9 to 22.3 tok/s and more than doubles its prefill (175 → 391).

The first five models repeat this morning's `p100-optimize` numbers to within 0.1 tok/s.

Flash-Next is bigger than VRAM, so it was measured with the 48-distinct-prompt server probe
(`../flash-next-iq2/probe.py`, default `--fit`, median of the last 24) instead of llama-bench,
and its tensor split was not tried (`--fit` is not implemented for tensor mode).
Not loadable on llama.cpp and skipped: qwen3.6-27b-opus-distill, qwen3.6-35b-a3b-abliterated-vl,
gemma4-e4b-abliterated.

`sweep.sh` reruns everything; `table.py` prints this table from `raw/`.
