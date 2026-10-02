# Aider Polyglot: five local models, 10-hour cap + overnight top-3 extension

2026-10-01 14:32 → 2026-10-02 05:48 (paused 19:34–21:30 at the owner's request).

The first test on this box that measures what pi actually asks of a coding model: edit an
existing file to a spec, in six languages, run the real unit tests, and get the failures back
for a second try. HumanEval could not do this job any more — the whole shelf scores 92–97.6%
there and every gap is inside noise.

## Headline

**qwen3.6-27b-abliterated (the incumbent) is the best coder on the shelf, the
qwen3.6-35b-a3b MoE is statistically level with it at 3.6x the speed, and devstral — pi's
coding model — ties for last.**

Top 3 on 50 exercises (pass@2 = solved within two tries; pass@1 = first try):

| Model | pass@2 | pass@1 | s/exercise | output tok/exercise |
|---|---:|---:|---:|---:|
| **qwen3.6-27b-abliterated q5_k_m** | **28/50 (56%)** | 12 | 293 | 1,856 |
| **qwen3.6-35b-a3b UD-Q6_K** | **24/50 (48%)** | 10 | **82** | 2,301 |
| qwen3.8-27b-unsloth Q8_0 | 17/50 (34%) | 8 | 424 | 2,439 |

Paired exact McNemar on the 50 (row passed & column failed / reverse):

| | 35b-a3b | 27b-abliterated | 3.8 Q8 |
|---|---|---|---|
| 35b-a3b | — | 6/10, p=0.45 | 9/2, p=0.07 |
| 27b-abliterated | 10/6, p=0.45 | — | **13/2, p=0.01** |
| 3.8 Q8 | 2/9, p=0.07 | 2/13, p=0.01 | — |

All five on the first 25 (the 10-hour run):

| Model | pass@2 | pass@1 | s/exercise |
|---|---:|---:|---:|
| qwen3.6-27b-abliterated q5_k_m | **16/25 (64%)** | 6 | 278 |
| qwen3.6-35b-a3b UD-Q6_K | 13/25 (52%) | 4 | 88 |
| qwen3.8-27b-unsloth Q8_0 | 10/25 (40%) | 5 | 442 |
| devstral-patched Q8_0 | 4/25 (16%) | 1 | 183 |
| gpt-oss-20b Q8_0 | 4/25 (16%) | 2 | 58 |

Incumbent vs devstral **12/0, p<0.001**; incumbent vs gpt-oss 14/2, p=0.004; MoE vs devstral
10/1, p=0.01; MoE vs gpt-oss 12/3, p=0.04. Devstral vs gpt-oss 3/3 — a tie at the bottom.
Full tables: `summary-all5.md`, `summary-top3.md`.

## What it means

1. **The coding seat in pi deserves a look.** Devstral lost 12–0 to the incumbent and 10–1
   to the MoE. Its failures are genuine wrong code — zero malformed replies, zero lazy
   placeholders, the tests ran and failed on logic (e.g. `go/pov` re-rooted trees wrong) — and
   it writes the shortest solutions of the five. This matches tau-bench retail (2026-09-22:
   devstral 53.0% vs incumbent 66.1%). Caveat below: this is aider's loop, not pi's.
2. **The MoE is the practical pick on this hardware.** Not separable from the incumbent
   (6/10, p=0.45) at 82 s vs 293 s per exercise, and it is already the AIOS planner. The
   incumbent's lead is consistent (ahead in both halves: 16 vs 13, then 12 vs 11) but small.
3. **qwen3.8-27b Q8 is not the coder its HumanEval said.** Best HumanEval on the box (97.6)
   and significantly worse than the incumbent here (2/13, p=0.01), while also the slowest.
   HumanEval ranks single-function recall; it does not rank editing with feedback.
4. **The second try is where the points are.** Every model at least doubled from pass@1 to
   pass@2 (incumbent 12 → 28). HumanEval only ever measured the first try.
5. **gpt-oss-20b is fast and not a coder here** (4/25 at 58 s) — consistent with its
   tau-bench last place.

## Setup

- **Harness:** aider `benchmark/` at commit 5dc9490, its `run_test()` called **unmodified** by
  `scripts/polyglot_run.py`. Exercises: `Aider-AI/polyglot-benchmark` at 7e0611e (225
  Exercism exercises). Runs in the `localhost/aider-benchmark` podman image built from aider's
  own Dockerfile (Python 3.11, Go 1.21, Rust, JDK 21, Node 20 + jest, CMake), `--network host`.
- **Backend:** llama.cpp CUDA 12.6 sm_60 router on :8081, `--jinja`, ctx 16384, f16 KV,
  flash-attn, layer split, `--models-max 1`.
- **Model settings** (`models.yml`): whole-file edit format, temperature 0, max_tokens 4096,
  **thinking off** (`chat_template_kwargs.enable_thinking: false`; gpt-oss
  `reasoning_effort: low`) — the same basis as every other shelf benchmark. Verified: no
  reasoning traces in any transcript.
- **Order:** `order.txt`, a fixed seeded order of all 225 interleaved by language
  (`scripts/polyglot_order.py`), so every prefix keeps suite proportions. Every model ran the
  same prefix, so all comparisons are paired. The 50: cpp 6, go 9, java 10, javascript 11,
  python 7, rust 7.
- **Budget control** (`drive.sh`): 6 calibration exercises per model, then the remaining
  budget split on *measured* seconds per exercise so all models reach the same index; no
  exercise is started that is not expected to finish before its deadline; hard stop at the
  cap. The pause was not counted. The extension (`extend.sh`) picked the top 3 by pass@2 on
  the 25 and ran them to index 50 before 06:00.

## Runner validation (before any model ran)

- **96/100 reference solutions pass** on the first 100 exercises in the order. The four that
  do not: three Rust references depend on outside crates (`regex`, `num-bigint`,
  `itertools`) while the stub's Cargo.toml has none and models are told to use std only; and
  Exercism's own `javascript/resistor-color-trio` reference fails 1 of its 6 current tests.
  None is a runner fault; all four are solvable.
- **99/100 unsolved stubs fail.** The exception is `go/ledger`, a refactoring exercise whose
  stub already passes — a free point in the official suite too. It is #49 in the order, so it
  is in the 50 (the incumbent broke it on try 1 and fixed it on try 2).
- Records: `validate/refs-000-100.jsonl`, `validate/negative-000-100.txt`.

## Caveats

- **One run per model, and temperature 0 is not deterministic here.** During setup the same
  exercise flipped pass/fail between identical runs for both gpt-oss and the MoE. Read
  gaps under ~5 exercises as noise; the McNemar p-values are the guide.
- **This is aider's loop, not pi's.** Whole-file edits with test output pasted back. pi gives
  devstral tools and its own agent loop; a model tuned for that could do better there. The
  gap here (12–0) is too large for format alone to explain, but the direct test is a pi-driven
  repo task set.
- **Thinking off for everyone.** Thinking was worth ~+15.7 MMLU-Pro points to the incumbent;
  a thinking-on run would cost ~2–3x the tokens and could reorder the Qwens.
- **50 of 225 exercises.** Enough to separate the bottom two from the top two and the
  incumbent from qwen3.8; not enough to separate the incumbent from the MoE.
- **Test timeouts** (model code that hung for 180 s): incumbent 2, qwen3.8 3, devstral 1.
  Each counts as a failed try, as in the official harness.
- Container log timestamps are UTC; host logs (`driver.log`) are local EDT.

## Cost

10-hour run used 301 + ~157 min; the extension 5h38m. Per model, total wall time across the
50: MoE 1.14 h, incumbent 4.06 h, qwen3.8 5.89 h. A full 225 for the top 3 would be ~25 h; a
full 225 for the MoE alone ~5 h.

## Next

- **pi-driven coding tasks** — a dozen fixed tasks on a real repo, run through pi itself,
  graded by hidden tests. The only way to settle devstral fairly.
- **Finish the 225 for the incumbent and the MoE** to separate them (resumes from 50;
  ~23 h, or ~5 h for the MoE alone).
- **Thinking on** for the two Qwens on the same 50, now that the baseline exists.

## Files

- `REPORT.md` — this file; `summary-all5.md`, `summary-top3.md`, `summary*.json`
- `driver.log` — full timeline incl. pause, resume, extension; `preflight.jsonl`
- `runs/<model>/` — per-exercise aider transcripts (`.aider.chat.history.md`), aider results
  (`.aider.results.json`), `progress.jsonl`, the container's `driver.log`
- `drive.sh`, `extend.sh`, `ctr.sh`, `probe.py`, `models.yml`, `model-metadata.json`,
  `order.txt`, `summarise.py`, `negative_control.py`; `drive.sh.before-resume`
- `validate/` — runner validation; `smoke/`, `drytest/` — setup smoke tests and driver dry
  runs (not results)
