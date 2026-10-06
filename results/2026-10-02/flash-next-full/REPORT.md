# Qwen3.8 Flash-Next IQ2_XXS: full test run, 2026-10-02 22:40 → 2026-10-03 04:54

Goal: the best all-around model (the default since 2026-10-02). Flash-Next is bartowski
`Qwen3.8-Flash-Next-IQ2_XXS`, 75 GB, on 2× P100 (32 GB) + 61 GB RAM. `--fit` keeps ~30 GB
on the GPUs and the experts in RAM. Build `~/llama-cuda12` (50631b3), layer split, f16 KV.

Two phases, both unattended:
1. **The 2026-09-30 harness** (`run.sh`, copied from `2026-09-30/qwen36-q8kp`): MMLU-Pro
   (70 Q, per-category 5, seed 42) thinking off at np 96/2048 and thinking on at np
   12288 / ctx 16384, HumanEval 164, throughput, and a context ladder. Every question pairs
   with the incumbent's 2026-09-19 runs (exact McNemar, `pairs-flashnext-iq2.txt`).
2. **Aider Polyglot, the first 50 exercises** (`polyglot/phase2.sh`): the fixed 2026-10-01
   order, the same aider commit, whole format, thinking off, 2 tries, router ctx 16384. Paired
   per exercise with the five models of `2026-10-01/aider-polyglot-10h` (`polyglot/compare.py`).

## Answer

**Not the new all-around pick. Flash-Next is a capable generalist, but the planner MoE
beats it on the only axis it doesn't tie.** On knowledge and short-form code it matches the
incumbent: HumanEval 97.56% (the shelf's best, tied), MMLU-Pro thinking off 68.6% vs 71.4%,
and thinking on tied 55/60 once the two capped categories are set aside. It decodes ~1.9× faster
(21 vs 11 tok/s). On Aider Polyglot, the test closest to what pi asks of a model, it
scores 21/50 against the incumbent's 28/50 (p = 0.09) and the planner MoE's 24/50, and the MoE
gets there 3.7× faster per exercise. It also costs 75 GB of NVMe, two GPUs plus ~40 GB of
page cache, ~100 tok/s prefill, and very long thinking (3 of 14 MMLU batches ran out at 12k).

## Results

| | **Flash-Next IQ2_XXS** | incumbent qwen3.6-27b-abl Q5_K_M | p (paired) |
|---|---:|---:|---:|
| HumanEval | **97.56%** (160/164) | 96.34% | 0.69 (4 FN-only / 2 inc-only) |
| MMLU-Pro, thinking off (np 96 = np 2048) | 68.57% | 71.43% | 0.79 (6 / 8) |
| MMLU-Pro, thinking on (np 12288) | 78.57% **floor** | 87.14% | 0.07 (1 / 7), cap-driven, see below |
| same, without the 2 capped categories (60 Q) | **55/60** | 55/60 | 1 / 1 |
| Aider Polyglot pass@2, first 50 | 21/50 (42%) | 28/50 (56%) | 0.09 (3 FN-only / 10 inc-only) |
| decode tok/s (brief / medium / long / coding) | **21.5 / 20.9 / 20.7 / 20.8** | 11.5 / 11.1 / 11.1 / 11.1 | |
| prefill | ~100–130 tok/s on long prompts | ~143 | |
| context | 128k measured in pi-context (fit-managed); ladder 8k/16k/32k at 19.6–19.7 tok/s | 128k | |

Against its own earlier quant: the 2026-09-19 UD-IQ3_XXS through Ollama scored 70.0% on the
same 70 thinking-off questions. IQ2_XXS gets 68.57% with 4/3 discordant (p = 1.00), so the
smaller quant costs nothing measurable and runs ~4× faster (5.3 → 20.7 tok/s; the runtime
changed too, see flash-next-iq2).

### The thinking-on confound, quantified

Three of the 14 batches (economics, history and law, 5 questions each) used up the full
12,288-token thinking budget. History and law scored 0/5 and economics 4/5. The harness flags
this, and 78.57% is a floor. **Leave out history and law and the two models tie at 55/60,
with 1 / 1 discordant.** The whole 8.6-point gap is the cap. The incumbent got 6 of those 10
right, so Flash-Next's realistic ceiling here is about the incumbent's 87%. It also thinks
long: 67,919 thinking tokens for 70 questions, 243× its thinking-off output. That is 65 min
for this leg at 18.8 tok/s.

### Aider Polyglot

| model | n (common) | pass@2 | pass@1 | mean s/exercise | Flash-Next only / model only | p |
|---|---:|---:|---:|---:|---:|---:|
| **qwen3.8-flash-next IQ2_XXS** | 50 | **21/50 (42%)** | 12 | 306 | — | — |
| qwen3.6-27b-abliterated_q5_k_m | 50 | 28/50 (56%) | 12 | 293 (FN 306) | 3 / 10 | 0.09 |
| qwen3.6-35b-a3b_ud-q6_k | 50 | 24/50 (48%) | 10 | 82 (FN 306) | 5 / 8 | 0.58 |
| qwen3.8-27b-unsloth_q8_0 | 50 | 17/50 (34%) | 8 | 424 (FN 306) | 8 / 4 | 0.39 |
| devstral-patched_q8_0 | 25 | 4/25 (16%) | 1 | 183 (FN 287) | 7 / 0 | 0.02 |
| gpt-oss-20b_q8_0 | 25 | 4/25 (16%) | 2 | 58 (FN 287) | 9 / 2 | 0.07 |

Flash-Next prompt tokens per exercise: median 6051, max 80302; exceptions 0, malformed 0, test timeouts 0

Same 50 exercises for the top 3, the first 25 for devstral and gpt-oss (all they ran). FN = Flash-Next's
mean on that same subset.

- **pass@1 ties the incumbent (12 vs 12); the second try is where it loses.** It fixed 9 of its
  38 first-try failures from the test output, while the incumbent fixed 16 of 38. The 3/10
  discordance (p = 0.09) is a lean toward the incumbent, not a resolved gap.
- It is level with the planner MoE (21 vs 24, p = 0.58) but takes **3.7× longer per exercise**
  (306 s vs 82 s). It is ahead of the dense Qwen3.8-27B (21 vs 17, p = 0.39) and faster than it.
- It ran clean: 0 exceptions, 0 malformed edits and 0 test timeouts in 50. Median prompt was
  6k tokens. The worst exercise sent 80k prompt tokens over its requests, and at ~100 tok/s
  prefill those long retry prompts are what make it slow.

## What decides it

**Editing real code with test feedback (Polyglot), then wall time per task.** Every other
gap is inside noise. On Polyglot the order is incumbent 28, MoE 24, Flash-Next 21, Qwen3.8-27B
17. The MoE matches Flash-Next's accuracy at about a quarter of the time per exercise, so for an
all-around seat it dominates. Flash-Next's real advantages are HumanEval and decode speed: the
first is saturated across the shelf and the second is beaten by the MoE (54–68 tok/s, 111 with
MTP). Ranking for all-around use: **incumbent ≈ planner MoE > Flash-Next > Qwen3.8-27B**. The
first two split on accuracy vs speed, and Flash-Next is third on both.

## Caveats

- Polyglot runs Flash-Next at ctx 16384 like the 10-01 run, but with `--fit` on; the others
  were fully on-GPU. Its exercise times include ~100 tok/s prefill on long retry prompts. The
  worst was C++ queen-attack, which took 992 s for 49k prompt tokens of compiler output.
- 50 exercises and 70 MMLU questions resolve only large gaps. Every MMLU and HumanEval gap here
  has p ≥ 0.07.
- Throughput comes from `llm_benchmark.py` at ctx 8192. Decode held at 17 tok/s throughout
  Polyglot (router log), with no page-cache thrash. RAM: 16 GB used, 40 GB page cache.
- Refusal behaviour is not measured. Flash-Next is a stock (not abliterated) model.

## Files

`run.sh`, `bench_off.sh`, `bench_think.sh` (harness copies), `driver.log`, `pairs-flashnext-iq2.txt`,
`ctx-ladder.jsonl`, `mmlu-*`, `humaneval-*`, `throughput/`; `polyglot/phase2.sh`, `polyglot/compare.py`,
`polyglot/runs/`, `polyglot/driver.log`. The shim gained one TAGS line (`scripts/ollama_shim.py`,
backup `.bak-2026-10-02`). `~/llama-bench-models/qwen3.8-flash-next_iq2_xxs/` holds the split
GGUF symlinks; the router id is the folder name.
