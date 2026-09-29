# Round 2 candidates vs qwen3.6-27b-abliterated:q5_k_m — and the first working speculative decoding on this box

Run 2026-09-19/20. Brief unchanged from `../candidates/`: **coding and reasoning, tok/s floor
~10, benchmarks must beat the best qwen3.6.** Four newer models were picked from a web search
(not from memory), downloaded, and scored; the incumbent was re-run to test reproducibility.

## Result

| model | file | HumanEval | MMLU-Pro @96 | @2048 | gen tok/s | HE wall |
|---|---:|---:|---:|---:|---:|---:|
| `qwen3.6-27b-abliterated:q5_k_m` (incumbent, re-run) | 20.8 GB | **96.34%** | **71.43%** | 71.43% | 11.1 | 66 min |
| `gpt-oss-20b:q8_0` (2026-09-19, for reference) | 12.1 GB | 95.1% | **77.1%** | — | 66.1 | 12.6 min |
| `qwen3.8-27b-stock:q4_k_m` (already on the shelf) | 13.9 GB | 93.29% | 67.14% | 67.14% | 12.1–12.6 | 61.5 min |
| `ornith-1.5-35b-a3b:q4_k_m` | 21.7 GB | 92.07% | 61.43% | 61.43% | 47.8–49.6 | 13.6 min |
| `nemotron-cascade-2-30b-a3b:q4_k_m` | 24.7 GB | 89.02% | 48.57% | 48.57% | 69.0–70.5 | 11.3 min |
| `xing4.0-29b-a4b:iq4_nl` | 20.1 GB | 83.54% | 44.29% | 44.29% | 31.7–32.4 | 19.2 min |
| `g9v3-39a5b:q4_k_m` | 23.6 GB | 93.90% | 67.14% | 67.14% | 39.0–40.2 | 17.8 min |
| `qwen3.8-27b-unsloth:q8_0` (2026-09-21) | 29.0 GB | 97.56% | 68.57% | 68.57% | 10.9–11.2 | 68.9 min |
| `qwen3.8-27b-unsloth:ud_q6_k` (2026-09-21) | 21.0 GB | 95.73% | 70.00% | 70.00% | 9.8–10.2 | 74.2 min |
| `qwen3.8-27b-uncensored-hauhaucs:q6_k_p` (2026-09-21) | 25.9 GB | 95.73% | 68.57% | 68.57% | 9.9–10.3 | 77.2 min |

**No new model beat the incumbent on either axis.** Ornith −4.3 coding / −10.0 reasoning,
Nemotron −7.3 / −22.9, Xing −12.8 / −27.1, G9v3 −2.4 / −4.3. They win only on speed, by
2.9–6.3×. `gpt-oss-20b` from the previous round still holds the MMLU-Pro record (77.1%).

> **Read the margins with the power analysis below.** MMLU-Pro at 70 questions resolves gaps
> of ~15–20 points and nothing smaller; HumanEval at 164 tasks cannot separate models within
> ~3 points. Nemotron's and Xing's deficits are real (p<0.001). Ornith's −10.0 (p=0.092),
> G9v3's −4.3 (p=0.581) and every margin among the Qwen3.8 quants are **not** resolvable at
> this sample size. None of them beat the incumbent either — "not distinguishable from" is
> not "better than", and the brief requires better — but the ordering between the close
> models in this table should not be treated as a ranking.

**G9v3 is the closest any candidate came, and it is the one worth a second look.** At 93.90%
HumanEval / 67.14% MMLU-Pro it still loses to the incumbent on both, but it beats the shelf's
`qwen3.8-27b-stock` on coding (93.90 vs 93.29), ties it exactly on reasoning (67.14 vs 67.14),
and does it at **39–40 tok/s against that model's 12.1 — 3.2×**. Against the incumbent it is
3.5× the speed for −2.4 coding points. `gguf_active_bytes.py` says why: it is an MoE routing
**32 of 320 experts**, so despite 23.6 GB on disk it reads only **2.66 GB/token** against
qwen3.8-stock's 13.36 GB and the incumbent's 17.88 GB — 5.0× and 6.7× less. Its KV is
**38.0 KiB/token f16** against their 260 and 256, so it is also the only candidate here that
could hold a long context in this box's memory. Nothing else in round 2 gave up so little
accuracy for so much throughput.

Worth recording for the bandwidth model: g9v3 converts 2.66 GB/token into 39.1 tok/s, an
effective **104 GB/s**, where the dense models reach 162 GB/s (qwen3.8-stock) and 198 GB/s
(incumbent). Scattered expert reads cost roughly 40% of achievable bandwidth — the MoE win is
real but it is smaller than active-bytes alone predicts, and `tok/s = bandwidth ÷ active bytes`
overestimates MoE throughput unless that penalty is carried.

**The incumbent reproduced exactly.** MMLU-Pro 71.43% vs 71.4% on record, HumanEval
**96.34% vs 96.34%**, 11.1 tok/s vs 11.1, 70/70 parsed both times. The harness and the
2026-09-06/09-19 numbers are trustworthy.

## The reasoning scores measure the wrong mode

`@96` and `@2048` are identical to the hundredth for **every** model. The extra budget bought
nothing because both harnesses hard-code `"think": False`, which `ollama_shim.py` turns into
`enable_thinking:false` + `reasoning_budget:0` + `reasoning_effort:low`. So every candidate was
scored **with thinking off**, while their published claims (Ornith GPQA-D 89.2, Nemotron IMO
2025 + IOI 2025 gold, LiveCodeBench v6 87.2) are thinking-mode results.

This is the mirror image of the gpt-oss problem in `../candidates/REPORT.md`: that model could
not be stopped from reasoning; these were never allowed to start. **The MMLU-Pro column above is
a valid like-for-like comparison against the thinking-disabled shelf, and is NOT a test of what
these models are sold as.** Re-running with thinking enabled is the missing measurement.

### Thinking-on re-run (2026-09-20) — the conclusion survives

`scripts/ollama_shim.py` gained an opt-in `--force-think` flag and runs as a second shim on
:11501; the :11500 thinking-off path is unchanged and still produced every baseline above.
Router ctx 16384, `num_predict` 12288, same harness, same seed, same 70 questions.

| model | off | on (scored) | delta | parsed | answered | gen tok | tok/s |
|---|---:|---:|---:|---:|---:|---:|---:|
| `qwen3.6-27b-abliterated:q5_k_m` (incumbent) | 71.43% | **87.14%** | +15.71 | **70/70** | 87.14% | 44,201 | 11.0 |
| `ornith-1.5-35b-a3b:q4_k_m` | 61.43% | 81.43% | +20.00 | 65/70 | 87.69% | 41,180 | 53.0 |
| `nemotron-cascade-2-30b-a3b:q4_k_m` | 48.57% | 71.43% | +22.86 | 60/70 | 83.33% | 59,583 | 68.4 |
| `g9v3-39a5b:q4_k_m` | 67.14% | 68.57% | +1.43 | 55/70 | 87.27% | 54,288 | 38.1 |
| `xing4.0-29b-a4b:iq4_nl` | 44.29% | 40.00% | −4.29 | 32/70 | 87.50% | 121,269 | 29.5 |
| `qwen3.8-27b-stock:q4_k_m` (shelf) | 67.14% | 82.86% | +15.71 | 64/70 | 90.62% | 44,659 | 12.0 |

**Thinking was never on, and it is worth 15–23 points — to the incumbent as much as to the
candidates.** With it off every model answered a whole 5-question batch in ~10 tokens (280
tokens for all 70, identical across models); with it on they generate 150–400× that.

**No candidate beats the incumbent in thinking mode either.** The incumbent gains 15.71 to
**87.14%** and finishes 5.71 ahead of the best candidate. The round-2 verdict is unchanged by
the mode switch — which is the thing this re-run existed to test.

**The incumbent was the only model that terminated on all 14 batches.** Every candidate hit
the 12288-token cap on at least one batch and scored 0/5 there, because a batch that spends
its whole budget reasoning emits no answer line and the harness scores an unparsed answer as
incorrect. `law` truncated for **all four** candidates; the incumbent answered it in 6,462
tokens. So the truncation is not the question set being too long for the budget — it is a
termination failure specific to the candidates.

**The scored delta tracks truncation count, not reasoning quality.** Ornith truncates 1 batch
and gains 20 points; Xing truncates 8 and *loses* 4. Among questions actually answered all
five cluster at 83–88%, a band that says little: it conditions on the batches that terminated,
which are the ones needing less reasoning, i.e. the easier ones. Xing's 87.50% is over 32 of
70 questions and is not comparable to the incumbent's 87.14% over all 70.

**`xing4.0` is not measurable on this harness.** 8 of 14 batches never converged within 12288
tokens, 121k tokens generated for a 40.00% score. This is the mirror of the gpt-oss problem in
`../candidates/REPORT.md`: that model could not be stopped from reasoning, this one cannot be
made to finish.

**The paired tests say only three of these gaps are real.** Against the incumbent's 87.14%:
nemotron −15.7 (p=0.003), g9v3 −18.6 (p=0.002) and xing −47.1 (p<0.001) are significant;
ornith −5.7 (p=0.219) and the shelf qwen3.8 −4.3 (p=0.453) are not. **G9v3 flips sign of
significance between modes**: indistinguishable from the incumbent thinking-off (p=0.581),
significantly *worse* thinking-on (p=0.002), because truncation costs it three whole batches.
Thinking mode actively penalises a model that does not terminate.

**"Among answered" does not extrapolate — measured, not argued.** `qwen3.8-27b-stock` first
scored 80.00% with two batches lost, at 93.33% among the 60 it answered; extrapolating that
rate predicted ~92% overall. Re-run with a working timeout, the two recovered batches scored
**2 of 10** and the real figure is **82.86%**. The among-answered column conditions on the
batches that terminated, which are the ones needing less reasoning. Treat it as a diagnostic
for how much truncation is costing, never as an estimate of the true score.

Three traps in producing this column, all of which silently yield plausible numbers:

1. **num_predict 4096 is far too small.** Three of ornith's batches capped, reporting 70.00%
   for a run that was 89.09% among answered. Evidence kept in `mmlu-ornith-think4096-TRUNCATED/`.
2. **`reasoning_effort` is not portable.** The shim first sent `reasoning_effort:"high"`; the
   **Qwen3.8** template validates that field against `('xhigh','medium','low')` and raises a
   Jinja exception, so `qwen3.8-27b-stock` returned 0.0% in 94 seconds with every request a
   router 500. The other five models do not reference `reasoning_effort` in their templates at
   all, so it was a no-op for them and removing it leaves their numbers unchanged. The shim now
   omits it and each model uses its own default depth (`xhigh` for Qwen3.8).
3. **The harness's `--api-timeout` default of 900s is too short for thinking-on.** A 12288
   token budget needs `12288 / tok_s` seconds: 232s at ornith's 53 tok/s, but **1024s** at
   qwen3.8-stock's 12.0. Two of its batches returned `TimeoutError` with `eval_count=0` while
   the model was still generating. This is easy to misread as the cap-truncation the other
   models show — the tell is the token count: cap-truncation yields exactly 12288, a timeout
   yields 0. `bench_think.sh` now takes an api_timeout argument (default 2400) and flags
   timeouts as RIG-FAIL separately from truncation. The incumbent escaped only by luck: its
   longest batch was 7014 tokens, 638s at 11.0 tok/s.

Any thinking-on figure from this harness must be read with its parsed count. A scored number
alone cannot distinguish a model that reasoned badly from one that never stopped reasoning.

## Three more Qwen3.8-27B quants (2026-09-21) — and how much of this table is noise

Three GGUFs supplied in `~/Downloads/Models`, all `qwen35` arch so all three ran on the
production build. All are DENSE — 20.0 / 24.9 / 27.7 GB active per token against the shelf
Q4_K_M's 13.36 — so all three sit at or just under the brief's ~10 tok/s floor.

**Quantisation buys more than any of the four round-2 candidate models did.** Same base
model, HumanEval: Q4_K_M 153/164 -> Q6_K 157/164 -> Q8_0 **160/164**. The Q8_0-vs-Q4_K_M
gain is the one between-model result in this whole round that survives a paired test:
7 tasks fixed, 0 broken, **p = 0.016**.

**`Q6_K` is confirmed the wrong quant on GP100, and the Q8_0 run is what proves it.**
UD-Q6_K reads **28% fewer bytes per token than Q8_0 yet runs 10% slower** (9.8 vs 10.9
tok/s). Fitting `t = overhead + active_bytes/BW` through the two non-Q6_K points and testing
the Q6_K files against that line gives **−15%** (UD-Q6_K) and **−11%** (Q6_K_P); the smaller
penalty on Q6_K_P matches its header, which is dominated by Q8_0 tensors (bpw 7.59), not
Q6_K. An earlier reading of this that compared Q6_K only against Q4_K_M suggested no penalty
— that was wrong, because Q4_K_M is itself a K-quant and not a control.

### Statistical power: most of the differences in this report are not resolvable

Every model answers the same seeded questions, so the correct test is paired (McNemar), not
an independent-sample comparison. Run over the per-question records:

| comparison | gap | discordant | p | |
|---|---:|---:|---:|---|
| incumbent vs `xing` (MMLU, off) | +27.1 | 22 / 3 | <0.001 | **significant** |
| incumbent vs `nemotron` (MMLU, off) | +22.9 | 17 / 1 | <0.001 | **significant** |
| incumbent thinking-off vs thinking-ON (MMLU) | +15.7 | 3 / 14 | 0.013 | **significant** |
| `q8_0` vs shelf `q4_k_m` (HumanEval) | +4.27 | 7 / 0 | 0.016 | **significant** |
| incumbent vs `ornith` (MMLU, off) | +10.0 | 10 / 3 | 0.092 | noise |
| incumbent vs `g9v3` (MMLU, off) | +4.3 | 8 / 5 | 0.581 | noise |
| incumbent vs `ud_q6_k` (MMLU, off) | +1.4 | 4 / 3 | 1.000 | noise |
| incumbent vs `q8_0` (MMLU, off) | +2.9 | 5 / 3 | 0.727 | noise |
| `q8_0` vs incumbent (HumanEval) | +1.22 | 5 / 3 | 0.727 | noise |
| incumbent (ON) vs `ornith` (ON) (MMLU) | +5.7 | 5 / 1 | 0.219 | noise |

**MMLU-Pro at 70 questions resolves gaps of roughly 15–20 points and nothing smaller.**
HumanEval at 164 tasks does better but still cannot separate models within ~3 points.

What this does and does not change:

* **It does not rescue any candidate.** Nemotron and Xing are genuinely worse than the
  incumbent. Ornith and G9v3 are merely *not distinguishable* from it on MMLU-Pro at this
  sample size — which is not the same as beating it, and the brief requires beating it.
* **`qwen3.8-27b-unsloth:q8_0` ties the incumbent.** 97.56% vs 96.34% HumanEval is +2 tasks
  (p=0.73) and 68.57% vs 71.43% MMLU is −2 questions (p=0.73). Calling it a coding win would
  be reading noise. It is a genuine tie, at 10.9 vs 11.1 tok/s and 29.0 GB vs 20.8 GB.
* **The two findings that are solid are both about configuration, not model choice:**
  turn thinking on (+15.7, p=0.013) and stop using Q4_K_M (+4.27 HumanEval, p=0.016).

To resolve 5-point differences reliably this harness needs roughly 4-8x its current
`--per-category 5`. That is a cheap change (`--per-category 20` is 280 questions) and it
should be made before any future round is asked to rank models this closely.

## Speculative decoding works here — 1.7–2.1×, and it is the real result of this run

`ggml-org/Qwen3.8-27B-GGUF` publishes two draft modules beside the weights
(`mtp-…Q8_0.gguf` 3.2 GB, `dflash-…Q8_0.gguf` 2.1 GB). A drafter shipped with the model has the
model's vocabulary by construction — the blocker that made this a dead end for devstral.
Measured on a **verified-empty GPU**, six distinct realistic prompts per config,
`scripts/spec_ab.sh`:

| config | mean gen tok/s | vs baseline | draft accepted |
|---|---:|---:|---:|
| Q4_K_M baseline | 12.32 | — | — |
| Q4_K_M + MTP | 21.42 | **1.74×** | 139/178 (78%) |
| Q4_K_M + DFlash | 21.19 | **1.72×** | 138/181 (76%) |
| Q4_K_M + ngram-cache (draft-free) | 11.90 | 0.97× | 4/35 (11%) |
| Q8_0 baseline | 10.86 | — | — |
| **Q8_0 + DFlash** | **22.72** | **2.09×** | 140/177 (79%) |
| Q8_0 + MTP | 19.46 | 1.79× | 139/180 (77%) |

**`Qwen3.8-27B` at Q8_0 + DFlash runs at 22.72 tok/s — 2× the incumbent's 11.1, at the best
quant, in a model that already scores better on HumanEval.** The `-np 2` prediction (a second
token in the same decode step costs 1.2%) held: acceptance is 76–79% and the win is ~1.8×.

**Draft-free speculation does not work here.** `--spec-type ngram-cache` exists in this build
(the notes said no draft-free mode existed — wrong) but accepts 11% of drafts and is a net
*loss*. So for devstral the conclusion stands for a different reason: not "no draft-free mode"
but "draft-free mode doesn't pay". A matched drafter is still required.

## Quant selection and fit

- Ornith `Q4_K_M` 21.7 GB — `Q5_K_M` is 25.4 GB, `Q8_0` 37.8 GB (does not fit).
- Nemotron `Q4_K_M` 24.7 GB — `Q8_0` is 33.6 GB (does not fit). `Q6_K` skipped: worst quant on
  GP100 per `../devstral-p100-bandwidth/`.
- Xing4.0 `IQ4_NL` 20.1 GB — the **only** quant the vendor publishes.
- G9v3 `Q4_K_M` 23.6 GB.
- Qwen3.8-27B: shelf `Q4_K_M` 13.9 GB (13.36 GB active/token), plus `ggml-org` `Q4_K_M`
  19.0 GB and `Q8_0` 28.6 GB. The Q8_0 + a 2.1 GB drafter + 8k f16 KV fits 32.5 GB; at
  260 KiB/token of KV this model cannot hold a long context at Q8_0.

## Two of the four needed out-of-tree runtimes

Architecture support was checked against the build's string table *before* downloading:

| model | `general.architecture` | upstream? |
|---|---|---|
| Ornith-1.5 | `qwen35moe` | yes — loaded on the production build unmodified |
| Nemotron-Cascade-2 | `nemotron_h_moe` | yes |
| Xing4.0 | `xing4_0` | **no** — open PR ggml-org/llama.cpp#29141 (`fairydreaming:xing4_0-port`) |
| G9v3 | `g9v3` | **no** — `linuxid10t/llama.cpp:feature/g9v3-support` |

`build_llama_cuda12.sh` now takes `REPO`/`REF`, so each fork builds into its own `OUT`
(`~/llama-cuda12-xing`, `~/llama-cuda12-g9v3`) and the production runtime is untouched.
4 minutes per build.

Ornith's MTP tensors are dropped on load by the production build
(`blk.40.nextn.* — unused tensor`), so its 47–49 tok/s is without its draft path.

## Three bugs found the hard way

1. **`build_llama_cuda12.sh` copied no CUDA runtime libs into the fork builds** — `find` without
   `-L` on `/usr/local/cuda/lib64`, which is a symlink. Both fork binaries died with
   `libcudart.so.12: cannot open shared object file`, and Xing4.0 + G9v3 silently scored 0/0.
   This is the exact trap already recorded in the build notes; the script had lost the fix.
   Now fixed with `find -L`, `libnccl` added, and a post-copy assertion that fails the build.
2. **The llama.cpp router enumerates `--models-dir` once, at startup.** A GGUF symlinked in
   afterwards is invisible — the harness reports `Requested model(s) not installed` and writes a
   0/0 result in two seconds. Restart the router after adding a model.
3. **`env VAR=x py …` returns 127** — `env` cannot run a shell function. Cost two throughput runs.

A fourth, non-bug: the first speculative pass ran while the bench router still held
`qwen3.8-27b` (17 GB of 32.5), so both baselines spilled to CPU and both DFlash configs OOMed.
Void numbers preserved under `spec-decoding-VOID-contaminated/`. **`--models-max 1` keeps the
last model resident; stop the router before any measurement that needs the whole GPU.**

## Caveat that is not about benchmarks

All four candidates are **stock models with intact safety training**, like `gpt-oss-20b` and
unlike almost all of the shelf. Nothing here measures refusal behaviour. Agentic tool use —
the thing Ornith, Xing and Nemotron are actually sold on, and what pi asks of devstral — is
still unmeasured by any harness here.

## Method

Rig per `../candidates/REPORT.md`: bench router on :8081 (`--ctx-size 8192`, f16 KV, layer
split, `--models-max 1`), `scripts/ollama_shim.py` on :11500, harnesses unmodified. Speculative
A/B on :8082 via `scripts/spec_ab.sh` (new, reusable) so it never touches :8080 or :8081.
Drivers, logs and raw per-task JSON are all in this directory: `download*.sh`, `build-forks.sh`,
`bench_one.sh`, `bench_one2.sh`, `run-queue-{main,2,3,4,5}.sh`, `driver.log`.

```fish
# per model, through the shim
2026-09-19/candidates-round2/bench_one2.sh '<tag>' <slug>
# speculative decoding, one config at a time, on a GPU with nothing else loaded
SPEC_AB_OUT=<dir> scripts/spec_ab.sh q8-dflash <model.gguf> draft-dflash <drafter.gguf>
```

GGUFs live in `/var/lib/ollama/candidates-r2/` (114 GB) with symlinks in `~/llama-bench-models/`.
