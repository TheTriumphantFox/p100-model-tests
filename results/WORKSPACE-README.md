# Local AI testing workspace

All benchmark inputs, reusable scripts, dated test artifacts, logs, generated
media, and reports live under:

```text
~/Projects/Tests/
```

## Organization

Completed or planned test artifacts use:

```text
YYYY-MM-DD/<subject>/
```

Reusable material stays directly under its own top-level folder instead of
being copied into every dated test:

```text
Tests/
├── 2026-09-01/local-llm-benchmark/
├── 2026-09-02/image-generation/
├── 2026-09-04/local-llm-coding-benchmark/
├── 2026-09-05/local-llm-mmlu-pro-benchmark/
├── 2026-09-06/local-llm-humaneval-benchmark/
├── datasets/
├── rig/
├── models/
├── scripts/
├── tools/
├── workflows/
└── .venv/
```

## Dated tests

### 2026-09-01 — local LLM benchmark

Archived Ollama throughput benchmark results and graphs are in:

- `2026-09-01/local-llm-benchmark/benchmark_results_full_20260901_220432.json`
- `2026-09-01/local-llm-benchmark/graphs/index.html`

The full historical run contains 12 model tags, 12 prompts, and 720 requests.
The older failed/smoke reports are retained beside it for provenance.

### 2026-09-02 — image generation

The image-generation artifacts are organized under:

- `2026-09-02/image-generation/pilot_geneval/`
- `2026-09-02/image-generation/pilot_t2i/`
- `2026-09-02/image-generation/realvisxl_full/`
- `2026-09-02/image-generation/runtime/`

The pilot and completed RealVisXL runs retain their manifests, generated
images, CLIP scores, and graph pages. Runtime logs and the temporary ComfyUI
output are in the subject's `runtime/` folder.

### 2026-09-04 — local LLM coding benchmark

The coding benchmark setup is in:

- `2026-09-04/local-llm-coding-benchmark/`

The completed 10-model, 8-task run is in:

- `2026-09-04/local-llm-coding-benchmark/runs/2026-09-05_00-01-44/`

Its `benchmark.py` discovers all locally installed Ollama model tags, displays
a terminal progress bar, safely checks generated Python solutions, and produces
correctness, task-heatmap, speed, CSV, JSON, and HTML reports.

### 2026-09-05 — MMLU-Pro general reasoning benchmark

The completed balanced MMLU-Pro run is in:

- `2026-09-05/local-llm-mmlu-pro-benchmark/runs/2026-09-05_22-56-18/`

It scored 10 local models on 70 deterministically selected test questions: five
questions from each of 14 categories. The run completed all 140 category
batches and 700 scored answers. Reports include overall accuracy, a category
heatmap, CSV, JSON, raw responses, and HTML.

### 2026-09-06 — HumanEval benchmark

The standardized HumanEval pass@1 runner is in:

- `2026-09-06/local-llm-humaneval-benchmark/`

It evaluates all 164 HumanEval tasks against every installed Ollama model,
executes generated code in a bubblewrap sandbox, saves incremental reports,
and supports resuming interrupted runs.

### 2026-09-18 — Devstral P100 tuning harnesses

Context/quant sweep scripts from the CUDA sm_60 build session are in:

- `2026-09-18/devstral-p100-tuning/`

`ctx-sweep.sh`, `q6-sweep.sh`, `kquant-ab.sh` and `prefill-ab.sh` drive `llama-server` at a
given context size or quant and report generation and prefill rates. Their result logs were
lost to a reboot before being filed; the conclusions are recorded in the session notes.

### 2026-09-19 — Devstral P100 memory bandwidth and KV cache

The HBM2 ceiling measurement, multi-GPU split-mode A/B and KV-cache-type A/B are in:

- `2026-09-19/devstral-p100-bandwidth/REPORT.md`

Headline results: the cards stream at 599 GB/s, not the 732 GB/s nameplate; generation reaches
52% of that; `-sm row` is gone from current llama.cpp and `-sm tensor` deadlocks on Pascal; and
f16 KV beats q8_0 at every depth, though not by enough to justify the context it costs.

### 2026-09-19 — qwen3.8-flash-next viability

The only never-benchmarked tag on the shelf, tested during the model review:

- `2026-09-19/qwen3.8-flash-next/REPORT.md`
- `2026-09-19/qwen3.8-flash-next/probe.py`

A 512-expert MoE (10 routed per token, 4.87 GB/token active) whose 70.8 GB of weights exceed the
32 GB of VRAM. It loads without thrashing — ~30 GB across both cards, the rest mmap'd — and reaches
**12.53 tok/s warm**, but **0.66 tok/s cold**, disk-bound at ~150 MB/s with the GPUs idle. Run
`probe.py` twice: the first pass measures cold, the second warm.

### 2026-09-19/20 — round-2 candidate models and speculative decoding

Four newer models found by web search, downloaded and scored against the incumbent, plus the
first working speculative-decoding measurement on this hardware:

- `2026-09-19/candidates-round2/REPORT.md`
- `2026-09-19/candidates-round2/` — drivers (`bench_one2.sh`, `run-queue-*.sh`), per-run JSON, logs
- `2026-09-19/candidates-round2/spec-decoding-VOID-contaminated/` — void first pass, kept with a
  README explaining why the numbers are wrong

**No candidate beat `qwen3.6-27b-abliterated:q5_k_m` on either axis** (Ornith 92.1/61.4,
Nemotron-Cascade-2 89.0/48.6, Xing4.0 —/44.3), though they run 2.9-6.3x faster. The incumbent's
2026-09-06 numbers **reproduced exactly** (96.34% HumanEval, 71.43% MMLU-Pro, 11.1 tok/s).
The real result is speculative decoding: **Qwen3.8-27B Q8_0 + DFlash = 22.72 tok/s, 2.09x**, with
76-79% of drafts accepted. Draft-free `ngram-cache` accepts 11% and is a net loss.

### 2026-09-22 — Devstral agent / tool-call handling (tau-bench retail)

First test of whether devstral drives a multi-turn tool-calling agent loop, not just
single-turn generation:

- `2026-09-22/devstral-tau-scripted/REPORT.md`
- `2026-09-22/devstral-tau-scripted/run.py` — tau-bench's `ToolCallingAgent` with
  `litellm` swapped for a direct call to the `:8080` router, plus a deterministic
  scripted customer

**Tool calling itself is sound: 0 parse failures across 375 tasks and ~4,000 model
calls**, on four architectures (mistral3, gpt-oss, qwen35, g9v3). llama.cpp's `--jinja`
parsers handle every format correctly and the models chain properly off `role: tool`
results. Every failure was reasoning or policy behaviour, not call emission.

| Model | n | Pass | Ceiling | Hours |
|---|---:|---:|---:|---:|
| qwen3.6-27b-abliterated q5_k_m | 115 | 66.1% | 71.3% | 7.80 |
| g9v3-39a5b q4_k_m (partial) | 30 | 56.7% | 86.7% | 1.09 |
| devstral-patched q8_0 | 115 | 53.0% | 57.4% | 3.45 |
| gpt-oss-20b q8_0 | 115 | 45.2% | 57.4% | 1.52 |

**Do not read the pass column alone.** The customer is scripted, not LLM-driven (no
metered API key, and no VRAM for a second model beside a 24-28 GB agent), so it cannot
answer a question. A model that asks never gets an answer and scores zero. *Ceiling* adds
back only the stalls where the model had found the right order and then asked: an upper
bound. Half of gpt-oss's stalls (16/31) never opened the target order, usually asking
for an order ID it could have looked up. So the confound can at most tie it with
devstral, not reverse them. **These scores are not comparable to published tau-bench
numbers.**

The retail policy requires an explicit "yes" before every write, and the scripted user
never gives one: 0 of 560 writes were confirmed. Devstral's low stall rate means it does
not follow that rule in its own system prompt. For an AIOS-style planner, confirmation
has to be enforced in the control plane, not the prompt.

Devstral's own failures are aggregation and state-tracking, not tool-call emission. It
miscounted available product variants (said 11; 12 exist, 10 available). It also
re-issued byte-identical writes 24 times across 14 tasks — the failure class that matters
most for a control plane. The retail backend's state checks rejected 20 of them; a
backend without such guards would not have.

### 2026-09-30 — the incumbent at Q8_K_P (same abliteration, higher quant)

- `2026-09-30/qwen36-q8kp/README.md` — HauhauCS Q8_K_P + Unsloth stock Q8_0; `queue.sh` (both files since deleted)
- `2026-09-30/qwen36-q8kp/REPORT.md`

**Neither higher quant beats the incumbent Q5_K_P** (every paired gap p ≥ 0.25): HumanEval
96.34 / 95.73 (Q8_K_P) / 95.12 (Unsloth stock Q8_0); MMLU-Pro thinking-on 87.14 / **91.43** /
90.00, with neither Q8 losing a question the incumbent got — a lean, not a result. Both run within
~4% of its speed. The Q8_K_P only fits fully on-GPU with `--fit off -ngl 999 -ts 36,28`: this
llama.cpp's default `--fit on` silently left ~2 layers in RAM, which a tok/s floor did not catch.

### 2026-10-01/02 — Aider Polyglot: five models on 25, top 3 on 50

- `2026-10-01/aider-polyglot-10h/REPORT.md` — results, setup, caveats
- `drive.sh` (driver, resume + extension modes), `extend.sh`, `ctr.sh` (podman wrapper), `models.yml`, `order.txt`, `summarise.py`, `validate/`

The first test here that edits existing files across six languages with test feedback for a
second try (aider's own harness, thinking off, one run). **Incumbent qwen3.6-27b-abliterated
28/50, qwen3.6-35b-a3b MoE 24/50 at 3.6x the speed (not separable, p=0.45), qwen3.8-27b Q8
17/50 (worse than the incumbent, p=0.01).** On the first 25: devstral and gpt-oss-20b 4/25
each — devstral lost 12–0 to the incumbent. Runner validated both ways first (96/100 references
pass, 99/100 stubs fail). Resumable: a later run continues from exercise 50 of `order.txt`.

### 2026-10-02 — tensor split and MTP on planner edits

- `2026-10-02/p100-optimize/REPORT.md` — results and caveats
- `bench.sh` (guarded llama-bench wrapper), `serve_bench.sh` (single-model server on :8090 + planner-bench subset), `summ.py`, `phaseB4.sh`, `phaseB5.sh`; raw output in `raw/` and `serve/`

`-sm tensor` hangs on these cards (the 09-18 "deadlock") until `NCCL_P2P_DISABLE=1`; then it
beats layer split everywhere: **planner 35B-A3B 54 → 68 tok/s, dense 27Bs ~11 → 19, gpt-oss
67 → 100**, prefill +50–60 %, same VRAM. **Qwen3.8-27B Q8_0 + tensor + MTP n-max 4 (`-ub 256`)
decodes at ~49 tok/s on planner edits, 9/9 correct, ~99 % acceptance** (15.5 KiB in 151 s, was
598 s). N-gram speculation slows the MoE planner. q8_0 KV costs the planner 12 % at 16k.
Afternoon (REPORT §4): **MTP works on MoE too**. The planner's unsloth MTP twin
(`~/models/_mtp-dl/`) goes 66 → 111 tok/s at n-max 3, Ornith 65 → 100, and the dense 27Bs reach
40–49. Qwen3.8's MTP file works on the Qwen3.6 incumbent (40 tok/s, 95 % acceptance). All correct.

### 2026-10-02 — speed sweep, all local models

- `2026-10-02/speed-sweep/REPORT.md`; `sweep.sh` reruns it (stops/restarts :8080), `table.py`

12 models, layer vs tensor split, one session: +24–30 % MoE, +50–60 % gpt-oss/K2, +66–73 % dense.
Devstral 12.9 → 22.3 tok/s. g9v3 needs `~/llama-cuda12-g9v3`; K2's fork build supports tensor.

### 2026-10-02 — qwen3.8-flash-next IQ2_XXS

- `2026-10-02/flash-next-iq2/REPORT.md`, `probe.py` (48 distinct prompts against a server)

bartowski IQ2_XXS (75 GB) on llama.cpp with default `--fit`: 19.3 tok/s steady, against 5.3 for
the 82 GB IQ3_XXS through Ollama. Quant and runtime both changed. Weights in `~/models/`.

**From 2026-10-02 on, a test with no stated goal is judged on the best all-around model.**

### 2026-10-02/03 — qwen3.8-flash-next IQ2_XXS, full run

- `2026-10-02/flash-next-full/REPORT.md`; the 09-30 harness (`run.sh`) + Aider Polyglot first 50 (`polyglot/phase2.sh`, `polyglot/compare.py`)

HumanEval 97.56% (shelf best, tied), MMLU-Pro thinking-off 68.6%, thinking-on tied with the incumbent
55/60 once two token-capped categories are excluded, 21 tok/s decode. Polyglot 21/50 against the incumbent's 28 (p=0.09) and the MoE
planner's 24 at 3.7x the time per exercise. Not the all-around pick: incumbent ≈ planner MoE > Flash-Next > Qwen3.8-27B.

## Full-stack test rig

`rig/` runs requests through the whole flow instead of one model on one task:
planner, then strict validation, an optional reviewer and reporter, a simulated
human, checks, commit. Scenarios span several transactions, so one mistake
carries into the next. Models, personas and the role assignments are swappable
per config. See `rig/README.md`. Runs are written to `YYYY-MM-DD/rig/<name>/`.

## Reusable benchmark inputs

Training splits were intentionally not downloaded.

| Area | Location | Evaluation material |
|---|---|---:|
| Code generation | `datasets/humaneval/` | HumanEval: 164 test tasks |
| Code generation | `datasets/mbpp/` | MBPP: 500 test tasks + 90 validation tasks |
| General reasoning | `datasets/mmlu_pro/` | MMLU-Pro: 12,032 test questions + 70 validation questions |
| Text-to-image | `tools/geneval/` | GenEval: 553 prompts and evaluator source |
| Text-to-image | `tools/t2i_compbench/` | T2I-CompBench validation prompts: 8 categories, 300 prompts each |
| Text-to-audio support | `datasets/audiocaps/` | AudioCaps: 4,875 test caption prompts/metadata; original clips are external YouTube media |
| Text-to-audio support | `datasets/clotho/` | Clotho: 1,045 test audio clips and five captions per clip |
| Agent / tool calling | `tools/tau_bench/` | tau-bench: retail 115 test tasks + 16 tools, airline domain, MIT |
| Code editing (6 languages) | `tools/polyglot-benchmark/` + `tools/aider/` | Aider Polyglot: 225 Exercism exercises; harness = aider `benchmark/` at 5dc9490, run in the `aider-benchmark` podman image. Gradle/Cargo caches in `tools/polyglot-cache/` |

The local Python environment is `.venv/`; it includes `pyarrow` for reading the
Parquet datasets. Current workspace size is approximately 2 GB for the
reusable inputs and evaluator models; generated results are stored separately
in dated folders.

## Reusable scripts

- `scripts/download_benchmarks.py` — reproducibly downloads selected test and validation material.
- `scripts/comfyui_image_benchmark.py` — resumable ComfyUI API image-generation runner.
- `scripts/image_benchmark_postprocess.py` — CLIP prompt-alignment scorer and graph generator.
- `scripts/llm_benchmark.py` — Ollama throughput benchmark; default output is dated.
- `scripts/plot_llm_benchmark.py` — creates charts from the Ollama report.
- `scripts/gguf_meta.py` — GGUF metadata utility.
- `scripts/gguf_active_bytes.py` — per-token ACTIVE bytes for a GGUF (MoE-aware); the input to `tok/s = bandwidth / active bytes`.
- `scripts/kv_ab.sh` + `scripts/kv_ab.py` — serve devstral under one KV/context config and measure generation at zero and at depth, plus prefill. Stop `llama-devstral.service` first.
- `scripts/build_llama_cuda12.sh` — rebuilds the sm_60 / CUDA 12.6 llama.cpp in `~/llama-cuda12` (rootless container; `OUT=` overrides the destination, `REPO=`/`REF=` build an out-of-tree architecture branch such as an open PR). Needed because the host CUDA dropped Pascal.
- `scripts/spec_ab.sh` + `scripts/spec_ab.py` — serve one model on :8082 under one `--spec-type` config and measure generation on six distinct realistic prompts, reporting draft acceptance. Stop the bench router first: `--models-max 1` leaves its model resident and the A/B then measures a GPU that is already half full.
- `scripts/hbm_bandwidth.cu` — raw HBM2 read/copy ceiling per GPU. Build for Pascal in the CUDA 12.6 container: `nvcc -O3 -arch=sm_60 -cudart static -o hbm_bandwidth hbm_bandwidth.cu`.
- `scripts/polyglot_order.py` — fixed, language-stratified order of all 225 Aider Polyglot exercises, so any prefix is a miniature of the suite.
- `scripts/polyglot_run.py` — runs Polyglot exercises in that order against the :8081 router inside the podman image, calling aider's own `run_test()` unmodified; stops before an exercise it cannot finish by `--deadline`. `validate` mode runs the reference solutions instead, to prove the test runner first.
- `scripts/think_probe_openai.py` — A/B `enable_thinking: false` on llama-server's OpenAI endpoint, over a tool call, and say whether thinking actually stopped. Companion to `think_probe.py`, which asks the same question through `ollama_shim.py` and the Ollama-shaped `"think": False` body; the two flags are not interchangeable and neither probe covers the other's path. Reads `reasoning_content`, which the shim does not surface. Qualify a reasoning model with this before committing to a long thinking-off run.

The dated copy `scripts/llm_benchmark_2026-09-01.py` is retained for historical
reference; the active reusable copy is `scripts/llm_benchmark.py`.

## Running reusable tests later

The scripts use the current date when choosing default output locations. For
example:

```fish
cd ~/Projects/Tests
.venv/bin/python scripts/download_benchmarks.py
.venv/bin/python scripts/comfyui_image_benchmark.py --dataset geneval --limit 10
.venv/bin/python scripts/image_benchmark_postprocess.py 2026-09-02/image-generation/realvisxl_full --skip-clip
```

For the local Ollama throughput benchmark:

```fish
cd ~/Projects/Tests
.venv/bin/python scripts/llm_benchmark.py
```

For the coding benchmark, follow the instructions in
`2026-09-04/local-llm-coding-benchmark/README.md`.

For the compact MMLU-Pro benchmark, follow the instructions in
`2026-09-05/local-llm-mmlu-pro-benchmark/README.md`.

For HumanEval, including run and resume commands, see
`2026-09-06/local-llm-humaneval-benchmark/README.md`.

## Licensing notes

The dataset cards/repos should be retained with this workspace. HumanEval,
MMLU-Pro, GenEval, T2I-CompBench, and tau-bench are released under MIT terms;
MBPP is CC BY 4.0. AudioCaps metadata is MIT-tagged, but its source audio comes from
YouTube and has separate source-media terms. Clotho and any bundled source
media must be used according to their upstream terms. Check the included
`README.md` files before redistribution.
