# Candidate models vs qwen3.6-27b-abliterated:q5_k_m

Run 2026-09-19. Two candidates downloaded and scored on the CUDA sm_60 build against the
incumbent best model on the shelf. Brief: **coding and reasoning, tok/s floor ~10.**

## Result

| model | HumanEval | MMLU-Pro | tok/s | size | HE wall |
|---|---:|---:|---:|---:|---:|
| **gpt-oss-20b:q8_0** | 95.1% | **77.1%** | **66.1** | **12.1 GB** | 12.6 min |
| `qwen3.6-27b-abliterated:q5_k_m` (incumbent) | **96.3%** | 71.4% | 11.1 | 20.8 GB | 1.11 h |
| `glm-4.7-flash:q5_k_m` | 84.8% | 55.7% | 44.7 | 21.4 GB | 15.4 min |

**gpt-oss-20b wins.** +5.7 points of reasoning over the incumbent, −1.2 on coding, at **6×
the speed in 58% of the space**. 77.1% is the highest MMLU-Pro anything has scored on this
box — above `qwen3.6-27b-opus-distill` (75.7), the previous best.

**GLM-4.7-Flash loses on both axes** — 11.5 points of coding and 15.7 of reasoning below the
incumbent. Fast and well-behaved, but there is no reason to keep it for this brief.

Both cleared the 10 tok/s floor by 6.6× and 4.5×; speed did not decide this.

## Quant selection

- **gpt-oss-20b Q8_0 (12.11 GB).** Its expert FFN is pinned to MXFP4 at every quant level, so
  the whole ladder spans only 11.46-12.11 GB — the label changes only attention/embedding
  tensors. Q8_0 is the Pascal-friendly choice for those (no `dp4a`, so K-quants are slower per
  byte here), and costs 0.5 GB over Q4_K_M. **MXFP4 works on sm_60** — this was the main
  unknown and it is settled.
- **GLM-4.7-Flash Q5_K_M (21.41 GB)**, deliberately matched to the incumbent's quant and size
  class so the comparison is not confounded. Q8_0 exists at 31.84 GB but leaves no room for KV.
- Both loaded first try. Neither hit the GGUF conversion failures that killed three of the
  eight existing shelf tags.

## The MMLU token-budget problem

**gpt-oss cannot be told not to reason.** `think:false` (→ `enable_thinking:false` +
`reasoning_budget:0`) does not switch off its harmony-format analysis channel; only
`reasoning_effort` moderates it. At MMLU's baseline `num_predict 96` it burned the whole
budget on analysis and never emitted an answer: **0/70 parsed, scored 0.0%** — while visibly
getting the answers right in the reasoning text. Escalation:

| num_predict | parsed | score |
|---|---:|---:|
| 96 (baseline) | 0/70 | 0.0% — meaningless |
| 512 | 51/70 | 54.3% — still truncating on arithmetic-heavy categories |
| **2048** | **70/70** | **77.1%** |

GLM needed no such accommodation: **55.7% @96 and 54.3% @2048, both 70/70 parsed**, and its
2048 run finished in 0.1 min — it answers immediately at any budget. So the two models were
given the same instruction and the same budget; one could comply and one could not.

**There is no budget at which the gpt-oss comparison is perfectly clean** — at 96 it scores 0
on a formatting timeout, at 2048 it gets chain-of-thought the thinking-disabled shelf models
never had. The number that survives is wall-clock: it answered all 70 in **1.8 minutes**.
Whatever the extra tokens bought, they did not cost time. HumanEval needed no asterisk — its
1024 budget was ample for both candidates, zero truncation, zero execution errors.

## Caveat that is not about benchmarks

**gpt-oss-20b is a stock model with intact safety training; the shelf is almost entirely
abliterated.** That is a deliberate choice on this box (see [[ollama-model-shelf]]), and
nothing here measures refusal behaviour. gpt-oss wins on coding and reasoning, but it will
refuse things `qwen3.6-27b-abliterated` will not. If that matters, the comparison to make is
against an abliterated derivative of gpt-oss, whose quality will differ from these numbers.

Also unmeasured: **agentic tool use.** GLM's published strengths were SWE-bench Verified (59.2)
and τ²-Bench (79.5), neither of which HumanEval or MMLU-Pro touches, and that is exactly the
gap that still makes devstral's case in pi. GLM losing here does not settle that.

## Method

Same rig as `../cuda-rerun/`: bench router on :8081 (`--ctx-size 8192`, f16 KV, layer split,
`--models-max 1`), `scripts/ollama_shim.py` on :11500 presenting ollama's API so the harnesses
run unmodified. Two shim bugs were found and fixed during this run — see its header comments:
`reasoning_content` must not be prepended to `content`, and `reasoning_effort` must be sent
for gpt-oss. The first would have corrupted gpt-oss's code extraction; verified it did **not**
affect the earlier `cuda-rerun` scores (0 of 492 responses showed leakage).

```fish
cd ~/Projects/Tests
.venv/bin/python 2026-09-06/local-llm-humaneval-benchmark/benchmark.py run \
    --base-url http://127.0.0.1:11500 --model 'gpt-oss-20b:q8_0' --output <dir>
.venv/bin/python 2026-09-05/local-llm-mmlu-pro-benchmark/benchmark.py run \
    --base-url http://127.0.0.1:11500 --model 'gpt-oss-20b:q8_0' \
    --num-ctx 8192 --num-predict 2048 --output <dir>
```
