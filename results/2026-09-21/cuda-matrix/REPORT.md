# CUDA benchmark matrix — 2026-09-21, in progress

Filling the missing CUDA cells for every model on the shelf, at the **existing** settings
(`--per-category 5`, seed 42, ctx 8192 thinking-off / 16384 thinking-on) so every new number
is **pairable** against the round-1 and round-2 records. The 280-question extended runs are
built and shelved (`queue-extended-pc20.sh.DEFERRED`) pending a decision on which models
earn them.

Raw dump of everything below: `DATASET.txt`, regenerate with `./DATASET.sh`.

## Status

Complete: the priority ggml-org Q8_0 row, the context-ladder method, the process test, and
— as of 2026-09-21 21:52 — the `devstral-patched` row, run in a confirmed production-idle
window (section 7).
Dead: `gemma4-e4b-abliterated` does not load on this runtime at all (see below).

## The matrix

| model | tok/s | MMLU-off | MMLU-ON | HumanEval |
|---|---|---|---|---|
| `qwen3.6-27b-abliterated:q5_k_m` (incumbent) | 11.1–11.5 | **71.43** | **87.14** | 96.34 |
| `qwen3.8-27b-stock:q4_k_m` | 12.1–12.6 | 67.14 | 82.86 (64/70) cap:2 | 93.29 |
| `ornith-1.5-35b-a3b:q4_k_m` | 47.8–49.6 | 61.43 | 81.43 (65/70) cap:1 | 92.07 |
| `g9v3-39a5b:q4_k_m` | 39.0–40.2 | 67.14 | 68.57 (55/70) cap:3 | 93.90 |
| `qwen3.8-27b-unsloth:q8_0` | 10.9–11.2 | 68.57 | pending | **97.56** |
| `qwen3.8-27b-uncensored-hauhaucs:q6_k_p` | 9.9–10.3 | 68.57 | pending | 95.73 |
| `qwen3.8-27b-ggmlorg:q8_0` | 10.9–11.2 | 68.57 | pending | 95.73 |
| `gpt-oss-20b:q8_0` | pending | 77.14 | pending | 95.12 |
| `qwen3.6-27b-opus-distill:q4_k_m` | queued | queued | queued | queued |
| `qwen3.6-35b-a3b-abliterated-vl:q4_k_m` | queued | queued | queued | queued |
| `gemma4-e4b-abliterated:q4_k_m` | — | **cannot load** | **cannot load** | — |
| `devstral-patched:latest` (production) | 12.9–13.1 | 58.57 | **no thinking mode** | 84.76 |
| `qwen3.8-27b-unsloth:ud_q6_k` (deleted) | 9.8–10.2 | 70.00 | — | 95.73 |
| `glm-4.7-flash:q5_k_m` (deleted) | — | 54.29 | — | 84.76 |
| `nemotron-cascade-2-30b-a3b:q4_k_m` (deleted) | 69.0–70.5 | 48.57 | 71.43 (60/70) cap:2 | 89.02 |
| `xing4.0-29b-a4b:iq4_nl` (deleted) | 31.7–32.4 | 44.29 | 40.00 (32/70) cap:8 | 83.54 |

`cap:N` = N thinking batches spent the whole `num_predict` budget and emitted no answer
line. Those score 0/5, so the cell is a **floor**, not a score.

## 1. The priority test: the ggml-org Q8_0 does not deliver the hypothesised win

`SHELF-REVIEW.md` proposed that `ggml-org/Qwen3.8-27B` Q8_0 — the file with published
`dflash` drafters measured at **22.72 tok/s, 2.05× the incumbent** — would score where the
Unsloth Q8_0 scored (97.56% HumanEval), yielding the first configuration to beat the
incumbent. Measured:

| paired comparison | gap | discordant | p | |
|---|---:|---:|---:|---|
| ggml-org Q8_0 vs **Unsloth Q8_0** (MMLU-off) | 0.00 | **0 / 0** | 1.000 | identical answers |
| ggml-org Q8_0 vs Unsloth Q8_0 (HumanEval) | −1.83 | 0 / 3 | 0.250 | underpowered |
| ggml-org Q8_0 vs incumbent (HumanEval) | −0.61 | 4 / 3 | 1.000 | noise |
| ggml-org Q8_0 vs incumbent (MMLU-off) | −2.86 | 5 / 3 | 0.727 | noise |

**The premise fails.** It landed at 95.73%, not 97.56% — fixing **zero** tasks the Unsloth
file passed and breaking three. The 1.83-point gap is not resolvable (3 discordant pairs;
an exact test cannot reach p<0.05 below 6), so the defensible statement is that at 164 tasks
the incumbent, the Unsloth Q8_0 and the ggml-org Q8_0 are **mutually indistinguishable on
coding**. "Q8_0 + DFlash beats the incumbent on coding and speed" reduces to "and speed".

Note the chain never had a resolvable link: the Unsloth file's own 97.56 vs 96.34 was
p=0.73. The brief requires *beating* the incumbent, and nothing here does.

## 2. MMLU-Pro thinking-off is nearly blind to quantisation

All three Qwen3.8 quants — two different quantisers' Q8_0 and an *uncensored* Q6_K_P —
answer **all 70 MMLU questions identically**:

| pair | MMLU-off | HumanEval |
|---|---|---|
| Unsloth Q8_0 vs ggml-org Q8_0 | 0/0 discordant | 3/0 |
| Unsloth Q8_0 vs uncensored Q6_K_P | 0/0 discordant | 3/0 |
| ggml-org Q8_0 vs uncensored Q6_K_P | 0/0 discordant | 1/1 |

The harness is not blind in general — the incumbent differs from these by 5/3 on the same
questions. The cause is output length: **thinking-off MMLU generates ~2 tokens per
question** (`1: A`), so the score is essentially the argmax of one content token, and
quantisation noise rarely flips a confident argmax. HumanEval generates ~180 tokens per
task, and that is where quantisation shows up at all.

Two consequences. Quantisation choice cannot be evaluated on this MMLU configuration —
including the round-2 finding that Q6_K is the wrong quant on GP100, which is a *speed*
result and remains valid. And an abliterated variant scoring identically to stock on MMLU
says nothing about whether abliteration changed the model; it says MMLU cannot see it.

## 3. The KV figure in round 2 is wrong by ~2.6×, and context is not the constraint

`ctx-ladder.sh` walks a model up the context range and records resident VRAM against the
weight-file size plus a real decode rate at every rung, spilled rungs included.
`qwen3.8-27b-ggmlorg:q8_0`, 27,271 MiB of weights, q8_0 KV:

| ctx | VRAM resident | tok/s | status |
|---:|---:|---:|---|
| 16384 | 28,137 MiB | 10.85 | resident |
| 32768 | 28,937 MiB | 10.85 | resident |
| 49152 | 29,737 MiB | 10.85 | resident |

**+800 MiB per +16384 tokens = 50.0 KiB/token**, against the **260 KiB/token** used in
`candidates-round2/REPORT.md`. On that figure SHELF-REVIEW concluded "at 260 KiB/token of KV
this model cannot hold a long context at Q8_0". It holds production's full **49152** context
with **3,031 MiB spare** — room for roughly 62,000 more tokens — and the decode rate is
identical to two decimals at every rung.

**So the binding constraint is decode rate, not memory.** Generating 49152 tokens at
10.85 tok/s takes 75 minutes for a single question. Round 2 chose ctx 16384 as "the window
that holds a 12288-token budget", treating the window as scarce; it never was. This also
locates where speculative decoding's 2× actually pays: it buys *thinking depth*, which is
the only axis where the ggml-org file's speed could convert into accuracy.

The 260 KiB/token figure should be re-derived or dropped wherever it appears.

## 4. Three of the five missing rows cannot be benchmarked on this runtime at all

Not unmeasured — **unrunnable**. All three fail at model load, each with its own error, and
the common factor is that this build's loaders do not handle these variants:

| model | load error | what it means |
|---|---|---|
| `gemma4-e4b-abliterated:q4_k_m` | `done_getting_tensors: wrong number of tensors; expected 2131, got 720` | header declares 2131 and the file has 2131; the `gemma4` loader maps only 720 — an E4B architecture-support gap |
| `qwen3.6-27b-opus-distill:q4_k_m` | `check_tensor_dims: tensor 'blk.0.ssm_dt.bias' not found` | the file carries `qwen35.vision.block_count = 27` and 1292 tensors — it is a **vision** model, not the text distill the shelf notes describe |
| `qwen3.6-35b-a3b-abliterated-vl:q4_k_m` | `qwen35moe.rope.dimension_sections has wrong array length` | mrope sections — multimodal RoPE the text-only loader cannot parse |

The two Qwen models are both **VL variants**, and the incumbent is the control that proves
the point: same `qwen35` architecture, same `block_count 64`, same SSM keys — but **851
tensors and no `vision.block_count`**, and it loads fine. The VL files carry their vision
tower *inside the single GGUF*; their ollama manifests list exactly one model blob with no
separate projector, so this is not a wrong-symlink problem and cannot be fixed by pointing
at a different file.

`opus-distill` being a vision model is itself news: it is on the shelf as a text distill
claiming 75.7 MMLU. **That 75.7 cannot be verified or refuted here**, which was the entire
reason SHELF-REVIEW kept it ("a 20-minute test").

Each cost real time before the cause was found — `qwen36-vl` burned 30 minutes on a
HumanEval where all 164 tasks failed on a 10-second retry loop. `bench_off.sh` should abort
a run once the first N requests all error rather than retrying through the whole set.

### The older sub-finding

#### `gemma4-e4b-abliterated` detail

Every request returns `router 500: failed to load`. The router log gives the reason:

```
llama_model_load: error loading model: done_getting_tensors: wrong number of tensors;
expected 2131, got 720
```

The file is **not** corrupt or truncated — its GGUF header declares 2131 tensors and the
ollama manifest lists exactly one model blob, so nothing is missing. The build's `gemma4`
loader maps only 720 of them: an architecture-support gap for this E4B variant, the same
class of problem as xing4.0 and g9v3 needing fork runtimes in round 2. It presumably works
under ollama's own engine, which is not this rig.

Its row cannot be filled without a newer or forked llama.cpp. Since SHELF-REVIEW keeps it
solely as "the only audio-in model", and benchmarks never captured that anyway, nothing is
lost by leaving the row empty — but it should be recorded as *unrunnable here*, not as
*unmeasured*.

## 5. `gpt-oss-20b` did not reproduce, and that undermines the whole MMLU-ON column

Re-run today at **identical settings** (`--per-category 5`, seed 42, ctx 8192,
`num_predict` 2048, same shim, same router config):

| run | score | generated tokens | tok/s |
|---|---:|---:|---:|
| round 1, 2026-09-19 21:59 | **77.14%** | 7,170 | 65.7 |
| this matrix, 2026-09-21 10:16 | **71.43%** | 5,348 | 65.7 |

Paired: −5.71 points, discordant **0 / 4** — the re-run broke four questions round 1 got
right and fixed none. Per-batch reasoning volume differs substantially (chemistry 1,749 →
1,016; engineering 1,666 → 908), so the model **reasoned less on the second run and scored
lower for it**.

This matters far beyond gpt-oss. **The incumbent reproduced exactly in round 2** — 71.43%,
96.34%, 70/70 parsed, twice — which is why the harness was trusted. But the incumbent
thinking-off generates **280 tokens in total**; gpt-oss reasons unconditionally and
generates 5–7k. The same length effect that makes MMLU-off blind to quantisation
(section 2) makes long generations *unreproducible*: floating-point nondeterminism flips one
argmax, the reasoning path diverges, and the divergence compounds.

**The thinking-on column generates 40,000–120,000 tokens per run and has never been
re-run once.** If a 7k-token run moves 5.7 points between executions, every MMLU-ON figure
in this matrix — including the incumbent's 87.14% and the +15.71 "thinking is worth 15–23
points" finding — carries an unmeasured run-to-run variance that is plausibly larger than
most of the gaps being compared.

Two hypotheses remain open, and they are not equally serious:

* **Run-to-run nondeterminism at temperature 0.** The leading explanation, and the one that
  would invalidate comparisons.
* **A shim change between the two runs.** `reasoning_effort: "low"` in the thinking-off path
  caps gpt-oss's analysis. The earliest surviving backup (2026-09-20 08:20) already contains
  it, ~10 h after the round-1 run, and its comment cites a round-1 observation
  (`num_predict 96` parsed 0/70), so it was most likely already in place — but this cannot
  be proven from what is on disk.

**The decisive test is cheap and should be run before any thinking-on number is used in a
decision:** repeat one MMLU-off run three times on gpt-oss (2 minutes each — a third distinct
value settles nondeterminism), then repeat one *thinking-on* run on a model that terminates
reliably, to measure the variance of the column directly. Until that exists, treat
thinking-on gaps under ~15 points as unresolved regardless of their p-values, since McNemar
assumes the only variation is between models.

## 5b. Round 1's "gpt-oss-20b wins" does not survive a paired test either

`candidates/REPORT.md` concluded gpt-oss-20b beat the incumbent with "+5.7 points of
reasoning". Paired over the same 70 questions: **+5.71, discordant 8/12, p=0.5034.** On the round-1 figure it is
the highest MMLU-off score on the box and still *not* a resolvable win over the incumbent;
on today's re-run it merely ties the incumbent exactly (71.43 vs 71.43).
It remains an extraordinary result per byte and per second — 95.12% HumanEval at 66 tok/s in
12.1 GB — but the reasoning claim is noise at this sample size.

## 6. Process test — thinking-on at a context worth using

Ten questions, one per category, at **ctx 49152 with q8_0 KV** (the `:8080` production
configuration), `num_predict` 4864 sized from the measured decode rate to bound the run.
The point was the paths, not the score.

| path | result |
|---|---|
| batches completed | 10/10 |
| thinking engaged | yes — 1074 tok/batch vs ~2 tok/question thinking-off |
| cap-truncation | **2** — `engineering`, `law` |
| client timeout | 0 — not exercised |
| other errors | 0 |
| unparsed answers | 2 — the same two |
| wall clock | 17.3 min at 10.83 tok/s |

Truncation fired on exactly the categories round 2 recorded for this model family
(`qwen3.8-27b-stock`: "engineering, law"), so the category selection reached the failure
path rather than the easy one. Cap detection, floor-flagging and parse accounting all
behaved. The timeout path stays unexercised — it only fires on a misconfigured
`--api-timeout`.

Score was 80.0% over 10 questions and is **not** a result; it is not in the matrix.

## 7. `devstral-patched` — the production model, measured

Run 2026-09-21 20:18–21:52 in a production-idle window confirmed with the owner beforehand
and re-checked between legs. `prodwatch.sh` sampled `:8080` every 30 s for the whole 94
minutes and logged **no state change**: the production router held pid 1416288 throughout,
spawned no child, and the GPU returned to 37 MiB after each leg. The numbers were taken on
an uncontended box.

Settings are queue-1.sh's, unchanged: `--per-category 5`, seed 42, ctx 8192 thinking-off /
16384 thinking-on, `num_predict` 12288, `--api-timeout 2400`. Every cell is pairable.

| leg | result |
|---|---|
| load, ctx 8192 | 25,679 MiB resident against 23,894 MiB of weights — fully offloaded |
| preflight | OK, 13.7 tok/s |
| MMLU-off `np 96` | 58.57%, parsed 70/70 |
| MMLU-off `np 2048` | 58.57%, parsed 70/70 |
| HumanEval | 84.76%, 164/164 attempted, 45.8 min at 12.9 tok/s |
| throughput | 12.9–13.1 tok/s across all four tests |
| load, ctx 16384 | 27,023 MiB resident — fully offloaded |
| MMLU thinking-on | **did not engage** — see below |

Paired against the incumbent over the same items:

| test | gap | discordant | p | |
|---|---:|---:|---:|---|
| HumanEval | −11.59 | 21 / 2 | 0.0001 | **resolvable — the incumbent wins** |
| MMLU-off | −12.86 | 14 / 5 | 0.0636 | not resolvable at 70 questions |

### It loads, and the separate-mmproj worry was unfounded

`devstral-patched` is `mistral3` with its projector in a **separate** blob (878 MB) from the
model (25.06 GB), unlike the three round-3 failures which pack the vision tower inside one
GGUF. The bench symlink points at the model blob alone, which is what a text-only load
wants, and it loaded on the first attempt from the same runtime that serves `:8080`.
Cold load took ~2.5 min to page 23.9 GiB in; `assert_on_gpu` confirmed full offload at both
context sizes.

### It has no thinking mode — this is an absent capability, not a low score

The thinking-on run completed in 1.5 min and generated **280 tokens — exactly the
thinking-off count**, at exactly the thinking-off score. `bench_think.sh`'s engagement guard
fired on the 1.00× ratio. Paired against its own thinking-off run: **0/0 discordant over all
70 questions.** The two runs are the same run.

The cause is in the file, not the rig. `tokenizer.chat_template` in the GGUF contains
**zero** occurrences of `enable_thinking`, `thinking`, `think`, `reasoning`, `<think>`,
`channel` or `analysis`. The `:11501` shim sets `chat_template_kwargs.enable_thinking = true`
— the same mechanism that produced the incumbent's 87.14 — and the template has nothing to
do with it, so it renders identically to the thinking-off path.

So the MMLU-ON cell is **not** 58.57. There is no thinking run to report. `make_final.py`
now carries `mark_nothink()`, which applies `bench_think.sh`'s own rule (fewer than 2× the
thinking-off tokens = did not engage) and renders the cell as `no thinking mode`, withholds
it from the column leader, and excludes it from the thinking comparisons — comparing
devstral's thinking-off answers against the incumbent's *thinking* run would compare two
different tasks. Without that, FINAL.md and the sheet would have printed a −28.57 point
"thinking" deficit at p<0.0001 for a run in which no thinking happened.

### Its KV is 2.3× the Qwen family's, and production still has room

Two loads at two context sizes measure devstral's context cost directly:

| ctx | resident | note |
|---:|---:|---|
| 8192 | 25,679 MiB | thinking-off leg |
| 16384 | 27,023 MiB | thinking-on leg |

**+1,344 MiB per +8,192 tokens = 168 KiB/token at f16**, against the 72 KiB/token measured
for the Qwen family in section 3. The "room for ~180,000 tokens" conclusion is about the
incumbent and **does not transfer to devstral**. Non-KV overhead solves to ~441 MiB.

Production runs `ctx 49152` with q8_0 KV, which halves the rate to ~84 KiB/token:

| ctx (q8_0 KV) | projected resident | spare of 32,768 MiB |
|---:|---:|---:|
| 49152 *(production today)* | 28,367 MiB | 4,401 |
| 65536 | 29,711 MiB | 3,057 |
| 98304 | 32,399 MiB | 369 |

Production can hold roughly **100,000 tokens**, and **65,536 is a safe raise with ~3 GiB of
headroom**. Caveat, stated because it matters: the 84 KiB figure is the measured f16 number
halved, not separately measured. `ctx-ladder.sh` on devstral would settle it in ~20 minutes
and should run before the change.

This is the round's most actionable result. Every win this box has produced has been
configuration — thinking on (+15.71), Q8_0 over Q4_K_M (+4.27), and context — and none has
been a model swap. Raising production's context is free and is worth more than devstral's
scores are.

### What these four columns do not say about devstral

All four are **single-turn Q&A**: one question in, one answer out, marked right or wrong.
What production asks of devstral is **agentic tool use**, and no harness here measures it.

The model file says so itself. Its chat template carries an `[AVAILABLE_TOOLS]` section, and
the local patch that earns the `-patched` suffix is a fix *to that section* — its own comment
records that the upstream strict user/assistant alternation check "hard-fails agentic
tool-calling clients (pi, opencode, etc.)". The file has been modified specifically for the
workload none of these tests administers.

Therefore: **"devstral scores below the incumbent" is not an argument for replacing it.**
The defensible statement is that on general knowledge and one-shot coding the incumbent is
better, and on the thing production actually does, there is no measurement at all. Closing
that needs a tool-use harness, which does not exist here. That is now the single most
valuable thing to build, because without it none of this matrix bears on the production
decision it was commissioned to inform.

## Method and rig corrections

Settings match round 2 exactly. Router on `:8081` (`--models-max 1`, f16 KV unless stated),
`scripts/ollama_shim.py` on `:11500` thinking-off and `:11501` `--force-think`, harnesses
otherwise unmodified. `:8080` is production and is never touched.

Four defects were found and fixed; each produced a plausible wrong number rather than an
error, which is why they are listed:

1. **`stop_router` would have killed production.** Round 2 matched child servers with
   `[l]lama-server --host 127.0.0.1 --jinja` — the exact prefix the `:8080` router uses for
   its own devstral child. It never bit only because devstral was cold every time. `lib.sh`
   enumerates children by PPID *before* killing the parent (after that they reparent to
   init), asserts the `:8080` pid is unchanged after every stop, and refuses to load onto a
   dirty GPU instead of falling through.
2. **A partial `results.json` is indistinguishable from a finished one.** The harness
   rewrites it after every batch. Read mid-run it showed a confident `82.86%` over 8 of 14
   batches for a run that settled at 68.57. `matrix.py` now checks `metadata.finished`.
3. **"Sub-minute = rig failure" is wrong for thinking-off MMLU.** That column generates ~280
   tokens in total, so a 70 tok/s model finishes honestly in under a minute; the heuristic
   flagged four real round-2 results as failures. The detector now keys on zero generated
   tokens or all-batches-errored.
4. **`env VAR=x py …` returns 127** — `env` cannot run a shell function. This is bug 3 in
   `candidates-round2/REPORT.md`; refactoring `$T/.venv/bin/python` into a `py()` helper
   reintroduced it and cost one throughput run. The call site now carries the reason.

### Harness changes

`benchmark.py` (MMLU-Pro) gained two flags, both defaulting to the previous behaviour so
every pre-2026-09-21 run reproduces byte for byte:

* `--batch-size` — decouples questions-per-request from sample size. Previously
  `--per-category` was *also* the batch size, so widening the sample widened every prompt:
  at `--per-category 20` the model is asked for 20 answers in one response, which does not
  fit in `num_predict 96` (~100 tokens of answer lines) and in thinking mode would have to
  reason about 20 questions inside one budget. That is a different task, not a bigger sample.
* `--categories` — a subset of the 14 categories, the only way to ask for an exact small
  number of questions and to aim a short run at the categories that exercise failure paths.

### Why the extended runs need their own baseline

`random.Random(seed).sample(rows, k)` is **not nested across k**: the 280-question set at
`--per-category 20` shares only **9 of 70** questions with the `--per-category 5` set at the
same seed. No extended number can be paired against any existing record. `mcnemar.py`
refuses mismatched item sets rather than silently scoring over the intersection, and any
extended round must re-run its own baseline or it can be compared to nothing.

## Tooling

| file | what |
|---|---|
| `lib.sh` | router control; PPID child kill, production assertion, VRAM floor, fit check |
| `bench_off.sh` / `bench_think.sh` | the thinking-off and thinking-on legs |
| `ctx-ladder.sh` / `ladder_report.py` | context ladder; measured KV bytes/token, spill cost |
| `probe.py` / `pick_ctx.py` | one-shot decode-rate probe; largest context that served |
| `process-test.sh` | ten-question thinking run with a path-coverage report |
| `matrix.py` | the matrix, keyed by model tag across all three rounds |
| `inventory.py` | every run on disk with settings and provenance |
| `mcnemar.py` / `pairs.py` | exact paired tests; refuse mismatched item sets |
| `DATASET.sh` → `DATASET.txt` | the whole dataset in one dump |
| `queue-1.sh` / `queue-2.sh` / `chain2.sh` | the sweep |
| `queue-devstral.sh` | the production row, one leg per invocation, GPU released after each |
| `prodwatch.sh` → `PRODWATCH.log` | samples `:8080` for contention while a leg holds the GPU |
| `queue-extended-pc20.sh.DEFERRED` | the 280-question plan, on hold |

## Open

* **`gemma4-e4b` needs a runtime that supports it**, or the row stays empty.
* **Production's context can probably be doubled for free** — section 7 measures devstral's
  KV at 168 KiB/token f16, which leaves ~4,400 MiB unused at the production `ctx 49152`.
  Confirm the q8_0 half of that with `ctx-ladder.sh` before changing anything.
* **Agentic tool use and refusal behaviour remain unmeasured** by any harness here — the
  same two gaps round 2 closed with. Section 2 sharpens the second one: MMLU-off cannot see
  an abliteration, so it cannot be used as evidence either way. Section 7 sharpens the first:
  now that the production model has been measured on four single-turn columns, the absence of
  a tool-use harness is no longer a gap in coverage but the gap that decides whether any of
  this applies to production at all.
