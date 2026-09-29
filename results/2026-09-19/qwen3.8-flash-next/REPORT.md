# qwen3.8-flash-next:ud-iq3_xxs — viability on 2× P100

Run 2026-09-19. Answers the one open question from the model-shelf review: the tag had
never been benchmarked, and at 82 GB it was the largest thing on the box.

## Verdict

**Works, scores well, and is slow.** MMLU-Pro **70.0%** — third on the shelf, behind
`opus-distill` (75.7) and `qwen3.6-27b-abliterated` (72.9), ahead of `qwen3.8-27b-stock`
(67.1). Steady-state throughput on varied prompts is **~5.3 tok/s generation / ~6.7 tok/s
prompt**, reached only after ~20 warm-up requests, and it needs the whole machine to get there.

> ### Correction (supersedes the first version of this report)
>
> The original figures — "12.53 tok/s warm, 153.64 tok/s prompt, usable" — were **wrong, and
> the method produced them.** That test sent the *same prompt twice* and called the second run
> warm. Identical input means identical routing, so the second pass drew the same 10-of-512
> experts already resident, and the prompt hit the prefix cache. It measured best-case expert
> reuse, not a warm model. Correct figures, from 24 **distinct** prompts:
>
> | | first (bad) method | varied prompts |
> |---|---:|---:|
> | generation | 12.53 tok/s | **5.3 tok/s** |
> | prompt | 153.64 tok/s | **6.7 tok/s** — 23× off |
> | page cache | "54 GB, converges" | settles ~35 GB |
>
> This is the same prompt-repeat trap recorded in [[p100-cuda12-llama-build]], arrived at from
> a different direction. **Any benchmark of a sparse MoE must use distinct prompts per
> measurement** — far more so than for a dense model, where repeats only distort prefill.

## What it is

`scripts/gguf_meta.py` / `gguf_active_bytes.py` on blob `f15e411c2e57`:

| | |
|---|---|
| arch | `qwen4exp`, 48 blocks, 262144 native context |
| experts | 512 total, **10 routed per token** |
| quant | dominant IQ4_NL, 3.20 bpw |
| file | 70.83 GB (embed 22.52 GB, experts 44.30 GB) |
| **active** | **4.87 GB/token** |
| KV | 96.0 KiB/token f16, 51.0 KiB q8_0 |

The active figure is the best on the box — an order of magnitude below the dense 27Bs
(17.88 GB/token). That is what made it worth testing despite the size.

## Placement

70.83 GB of weights against 32 GB VRAM + 61 GB RAM. It loads without thrashing:

- ~15.1 GB on each P100 (30.2 GB of 32 GB)
- remainder mmap'd; page cache grew 33.5 GB → 54.1 GB across the run
- swap essentially untouched (26 MiB of 61 GB zram); the desktop stayed responsive
- `llama-server` reported 98 graph splits at bs=512

## Measurements

`probe.py`, 66-token prompt, `num_predict=128`, temperature 0, `num_ctx=4096`.

| | cold (first load) | repeated prompt (INVALID — see Correction) |
|---|---:|---:|
| load | 250.5 s | 0.0 s |
| prompt eval | **0.55 tok/s** | 153.64 tok/s |
| generation | **0.66 tok/s** | 12.53 tok/s |
| wall | 565.3 s | 10.8 s |

### Warm-up curve on 24 distinct prompts (`warmup.py`, 200 tokens each)

| pass | 1 | 2 | 3 | 4 | 6 | 8 | 11 | 15 | 18 | 21 | 24 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gen tok/s | 0.47 | 1.02 | 1.64 | 2.41 | 3.33 | 4.08 | 5.05 | 6.81 | 5.90 | 5.30 | 5.51 |
| prompt tok/s | 0.22 | 0.58 | 0.76 | 1.18 | 2.91 | 2.83 | 6.37 | 6.61 | 6.80 | 6.26 | 8.28 |
| cache GB | 51.5 | 30.9 | 30.1 | 31.7 | 33.0 | 34.1 | 34.5 | 34.8 | 34.9 | 35.1 | 33.4 |

It plateaus from roughly pass 13 at **~5.3 tok/s generation, ~6.7 tok/s prompt**. Page cache
falls from the initial 51.5 GB and settles at ~35 GB: the working set is the full 44 GB expert
pool, which cannot coexist with 30 GB of resident weights, so it reaches an equilibrium of
partial residency rather than converging.

### MMLU-Pro, scored warm

70 questions, 5 per category × 14, seed 42, `--num-ctx 8192`, all 70 parsed, 23.5 min.

**70.0% (49/70)**, 8.20 tok/s during the run — higher than the 5.3 plateau because MMLU's
prompts are structurally similar within a category, so expert reuse is above what a mixed
workload gets. Strongest: biology 100, then computer science / engineering / health / history /
other / philosophy / psychology all 80. Weakest: **math 20**.

| shelf rank, MMLU-Pro | |
|---|---:|
| `qwen3.6-27b-opus-distill:q4_k_m` | 75.7% |
| `qwen3.6-27b-abliterated:q5_k_m` | 72.9% |
| **`qwen3.8-flash-next:ud-iq3_xxs`** | **70.0%** |
| `qwen3.8-27b-stock:q4_k_m` | 67.1% |
| `devstral-patched:latest` | 57.1% |

During the cold run the GPUs sat at 0–1% utilisation while `sda` read a sustained
~150 MB/s for the whole pass. The bottleneck was fetching expert weights, not compute:
with 10 of 512 experts routed per token, consecutive tokens touch a near-random subset of
the 44 GB expert pool, so a cold page cache never converges on a working set.

Warm generation of 12.53 tok/s against 4.87 GB/token is ~61 GB/s effective — well under
the 309 GB/s that generation reaches when a model is fully resident (see
`2026-09-19/devstral-p100-bandwidth/`), because only 30 of the 70.8 GB sits in VRAM and
the rest is served across PCIe from host RAM.

## Caveats

- **It needs the whole machine and ~20 requests of warm-up.** 30 GB of VRAM plus ~35 GB of
  page cache. It cannot coexist with devstral (28.8 GB of VRAM alone), and anything that
  evicts the cache drops it back toward 0.5 tok/s with another 20-request climb to recover.
- **Cost per answer is the real problem, not the score.** 70.0% is respectable, but
  `qwen3.6-27b-abliterated:q5_k_m` scores higher (72.9%) in 20.8 GB, runs on the CUDA build at
  11.1 tok/s, and needs no warm-up. flash-next is beaten on quality, speed, size and
  operational simplicity simultaneously.
- **HumanEval was not run** — at 5-8 tok/s with `num_predict 1024` it is a ~9-12 hour pass,
  and the model must hold the machine exclusively for all of it.
- **math 20%** is the weakest category by a wide margin and pulls against using it for
  quantitative work.
- All runs went through ollama (Vulkan on Pascal). It cannot load on the CUDA sm_60 build
  — untested there, and the three-tag load failure list in [[ollama-model-shelf]] suggests
  checking before assuming.

## Reproducing

```fish
cd ~/Projects/Tests/2026-09-19/qwen3.8-flash-next
python3 warmup.py 200        # 24 distinct prompts; watch for the plateau
python3 warmup.py 200 6      # continue from prompt 7 without reusing 1-6
```

**Do not measure this model with a repeated prompt** — see the Correction above. `probe.py`
remains for the cold-load and placement measurement only; its warm column is invalid.
