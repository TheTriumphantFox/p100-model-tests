# Benchmark rerun on the CUDA sm_60 build

Run 2026-09-19. Reruns the shelf benchmarks against `~/llama-cuda12` (llama.cpp, CUDA 12.6,
sm_60) instead of ollama's Vulkan fallback, to test whether the Vulkan-era speed rankings
survive a backend change.

## Headline

1. **CUDA is 4.3–6.6× faster than ollama/Vulkan**, not the ~1.12× recorded on 2026-09-18.
2. **Accuracy is backend-invariant.** MMLU-Pro moved by one question on one model and zero on
   another. Rerunning accuracy across backends is not worth doing again.
3. **Three of the eight shelf tags cannot load on llama.cpp at all** — including the qwen
   worker model and the best-MMLU model. The speedup is unavailable to exactly those.

## Method

The three harnesses are written against ollama (`/api/tags`, `/api/chat`, `/api/generate`).
Rather than fork them — which would have put the CUDA numbers on a different code path from
the Vulkan baseline they are compared against — `scripts/ollama_shim.py` presents ollama's API
and forwards to a llama.cpp router. **The harnesses ran unmodified**; the backend is the only
variable. The shim maps `num_predict`→`max_tokens`, `think:false`→`chat_template_kwargs.
enable_thinking` + `reasoning_budget:0`, and llama-server's `timings` block back onto ollama's
`eval_count`/`eval_duration`, and reports the original ollama tag names so reports line up.

A **separate** bench router ran on :8081 with its own `--models-dir` so the production router
on :8080 (and devstral's on-demand loading) stayed untouched. Router config: `--ctx-size 8192`,
f16 KV, `--split-mode layer`, flash-attn on, `--models-max 1`.

Running at 8192 rather than MMLU's nominal 32768 is safe and was verified, not assumed: all
70 answers parsed for all three models, so nothing truncated. It also keeps KV off the VRAM
cliff documented in [[p100-cuda12-llama-build]].

## What loads

Six shelf models were symlinked into the bench dir. **Three fail to load on llama.cpp**, each
with a distinct GGUF conversion mismatch — ollama runs all three, which points to ollama using
its own model implementations rather than llama.cpp for these architectures:

| model | CUDA | error |
|---|---|---|
| `qwen3.8-27b-stock:q4_k_m` | loads | — |
| `qwen3.6-27b-abliterated:q5_k_m` | loads | — |
| `devstral-patched:latest` | loads | — |
| `qwen3.6-27b-opus-distill:q4_k_m` | **fails** | `check_tensor_dims: tensor 'blk.0.ssm_dt.bias' not found` |
| `qwen3.6-35b-a3b-abliterated-vl:q4_k_m` | **fails** | `qwen35moe.rope.dimension_sections has wrong array length; expected 4, got 3` |
| `gemma4-e4b-abliterated:q4_k_m` | **fails** | `done_getting_tensors: wrong number of tensors; expected 2131, got 720` |

`opus-distill` and `stock` both declare `qwen35` with identical SSM hyperparameters; the
difference is that opus-distill also declares a 27-block vision tower and its file lacks the
`blk.0` SSM tensors the loader demands. This is a property of how those GGUFs were converted —
a rebuild does not fix it.

## Throughput — three legs

`scripts/llm_benchmark.py`, tests `speed_brief,speed_medium,speed_long,python_coding`,
3 iterations, matched `--context 8192`, worst run dropped per model/test.

| model | CUDA | Vulkan (service env) | Vulkan (no `GGML_VK_DISABLE_*`) | gain |
|---|---:|---:|---:|---:|
| `devstral-patched:latest` | **13.00** | 1.96 | — | **6.6×** |
| `qwen3.8-27b-stock:q4_k_m` | **12.27** | 2.87 | — | **4.3×** |
| `qwen3.6-27b-abliterated:q5_k_m` | **11.25** | 2.42 | 2.46 | **4.6×** |

**The `GGML_VK_DISABLE_MMVQ` / `GGML_VK_DISABLE_INTEGER_DOT_PRODUCT` flags are neutral** —
2.46 vs 2.42 tok/s, inside noise. They were raised as a suspect for the slow Vulkan baseline
and are ruled out. (They also postdate the 2026-09-06 baseline by twelve days, so they could
not have affected it.)

**The backend inverts the ranking.** On Vulkan devstral is the slowest of the three (1.96); on
CUDA it is the fastest (13.00). No ordering taken from the Vulkan runs survives the change.

## MMLU-Pro — accuracy is backend-invariant

70 questions, 5 per category × 14 categories, seed 42, identical dataset.

| model | CUDA | Vulkan | Δ | tok/s CUDA | tok/s Vulkan |
|---|---:|---:|---:|---:|---:|
| `qwen3.6-27b-abliterated:q5_k_m` | 71.4% | 72.9% | −1.4 (one question) | 11.63 | 2.36 |
| `qwen3.8-27b-stock:q4_k_m` | 67.1% | 67.1% | **0.0** | 12.66 | 2.90 |
| `devstral-patched:latest` | **57.1%** | — | first score | 13.50 | — |

All 70 parsed for every model. The generation rates here agree closely with the independent
throughput sweep above (11.63/12.66 vs 11.25/12.27), which is the cross-check that the 4–5×
is real and not an artefact of one harness.

**devstral's 57.1% is its first accuracy measurement of any kind** — previously it had only
ever been measured on throughput. It is the weakest of the three on general reasoning, which
is what a code-specialised model should look like.

## Contradiction with the 2026-09-18 note

[[p100-cuda12-llama-build]] records, for `qwen3.6-27b-abliterated:q5_k_m` at matched ctx 32768:
Vulkan 9.79 tok/s, CUDA 10.96, i.e. **1.12×**, and concludes "do NOT migrate the rest of the
shelf". Today's like-for-like is **4.6×**. The disagreement is **entirely on the Vulkan side**:

| | ctx 32768 (2026-09-18) | ctx 8192 (2026-09-19) |
|---|---:|---:|
| CUDA | 10.96 | 11.25 — **consistent** |
| Vulkan | 9.79 | 2.42 — **4× apart** |

Today's Vulkan figure reproduces in three independent places (throughput sweep 2.42, MMLU
timing 2.36, the 2026-09-06 HumanEval baseline 2.6). The 9.79 does not reproduce. The cause is
not established — it was not the `GGML_VK_DISABLE_*` flags — so **the 1.12× figure and the
"do not migrate" conclusion that rests on it should be treated as unsafe until re-derived.**

## HumanEval — 164 tasks, pass@1

Completed 492/492 generations, zero execution errors, bubblewrap sandbox as before.

| model | CUDA | Vulkan | Δ | tok/s CUDA | tok/s Vk | wall CUDA | wall Vk |
|---|---:|---:|---:|---:|---:|---:|---:|
| `qwen3.6-27b-abliterated:q5_k_m` | 96.3% | 97.0% | −0.6 (1 task) | 11.14 | 2.60 | 1.11 h | 4.67 h |
| `qwen3.8-27b-stock:q4_k_m` | 93.3% | 95.1% | −1.8 (3 tasks) | 12.13 | 3.30 | 1.03 h | 3.80 h |
| `devstral-patched:latest` | **85.4%** | — | first score | 12.96 | — | 0.78 h | — |

Accuracy again essentially unchanged — 1 and 3 tasks out of 164. Speed 4.2× and 3.7×, which
turns a 4.7-hour run into 1.1 hours. Combined with MMLU-Pro, **accuracy is backend-invariant
across both benchmarks and all four comparable measurements**; only latency moves.

### devstral is the weakest of the three, including at code

This was the expected place for devstral to win, and it did not:

| | HumanEval | MMLU-Pro | tok/s |
|---|---:|---:|---:|
| `qwen3.6-27b-abliterated:q5_k_m` | **96.3%** | **71.4%** | 11.14 |
| `qwen3.8-27b-stock:q4_k_m` | 93.3% | 67.1% | 12.13 |
| `devstral-patched:latest` | 85.4% | 57.1% | 12.96 |

`qwen3.6-27b-abliterated:q5_k_m` beats devstral by **10.9 points on HumanEval and 14.3 on
MMLU-Pro**, for 14% less speed — and it is one of the three models that runs on the CUDA build,
so it can be served the same way.

**Caveat before acting on this.** devstral is pi's default and a tool-calling agent model; its
Jinja template drives Mistral `[INST]` markers and `tool_calls`. HumanEval measures standalone
function completion, not agentic tool use, so it does not measure what pi actually asks of the
model. These numbers are a strong reason to *test* the swap, not a finished case for it. The
right follow-up is a tool-calling/agentic comparison, which no harness here currently covers.

## Reproducing

```fish
cd ~/Projects/Tests
# bench router (separate from the production one on :8080)
env LD_LIBRARY_PATH=$HOME/llama-cuda12/lib $HOME/llama-cuda12/bin/llama-server \
    --models-dir ~/llama-bench-models --models-autoload --models-max 1 \
    --host 127.0.0.1 --port 8081 --ctx-size 8192 --split-mode layer \
    --cache-type-k f16 --cache-type-v f16 --flash-attn on --jinja \
    --parallel 1 --batch-size 512 --ubatch-size 512 &
python3 scripts/ollama_shim.py --router http://127.0.0.1:8081 --port 11500 &
# then point any harness at the shim
env OLLAMA_HOST=http://127.0.0.1:11500 .venv/bin/python scripts/llm_benchmark.py ...
.venv/bin/python 2026-09-06/local-llm-humaneval-benchmark/benchmark.py run \
    --base-url http://127.0.0.1:11500 --model '<tag>' --output <dir>
```

`2026-09-19/cuda-rerun/loadcheck.sh` re-runs the load check on its own.
