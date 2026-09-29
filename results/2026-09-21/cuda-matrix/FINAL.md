# Which local model should we use?

*Test run finished 21 September 2026. Two Tesla P100s, 32 GB of video memory total.*

## The answer

**Keep the incumbent, `qwen3.6-27b-abliterated`. Nothing displaced it.**

It has the best score in every accuracy test, and it is the only model that finishes
every reasoning question instead of running out of budget partway through.

Four things changed, and none of them is "switch models":

- **The fast-and-accurate combination we were chasing does not exist.** A Qwen3.8 file
  runs at twice the incumbent's speed, but its coding score is no better — so the speed
  is real and the accuracy gain was wishful.
- **Our best reasoning score was a fluke.** `gpt-oss-20b` was recorded at 77.1. Repeated
  five times, it scores 71.4 in four of them — the same as the incumbent, not ahead of it.
- **Three models on the shelf cannot run on this machine at all.** Not "scored badly" —
  they fail to load.
- **`devstral`, the model production actually runs, is now measured.** It is
  **measurably worse at coding than the incumbent** — 84.8 against 96.3, a gap solid
  enough to call (p<0.001) — and lower on the quick exam too, though that second gap
  is not big enough to be sure of. It has no thinking mode at all. **This is not an
  argument for replacing it**: nothing here tests what production actually uses it
  *for*. See "What these tests do not cover" — the most important section in this
  document for that decision.

---

## How to read the numbers

| column | what it means | higher is |
|---|---|---|
| **Speed** | tokens per second — roughly words per second, as you feel it typing out | better |
| **Reasoning (quick)** | general-knowledge exam, model answers immediately | better |
| **Reasoning (thinking)** | same exam, model allowed to think first | better |
| **Coding** | 164 programming problems, % that actually run correctly | better |

**none** in the thinking column means the model has **no thinking mode** — there is no
such run to report, which is different from scoring badly at it.

An asterisk `*` means **the real score is higher than shown**. The model spent its whole
thinking budget and never wrote an answer down, which the exam counts as wrong. So a
starred number is a floor, and cannot be fairly compared with an unstarred one.

All scores come from the same questions for every model, so they are directly comparable.

## The results

| model | | Speed | Reasoning (quick) | Reasoning (thinking) | Coding |
|---|---|---:|---:|---:|---:|
| `qwen3.6-27b-abliterated` | the incumbent | 11.1–11.5 | **71.4** | **87.1** | 96.3 |
| `devstral-patched` | **what production runs today** | 12.9–13.1 | 58.6 | none | 84.8 |
| `qwen3.8-27b-unsloth` | Qwen3.8, Unsloth Q8_0 | 10.9–11.2 | 68.6 | 77.1* | **97.6** |
| `qwen3.8-27b-ggmlorg` | Qwen3.8, ggml-org Q8_0 — has the 2× drafters | 10.9–11.2 | 68.6 | 78.6* | 95.7 |
| `qwen3.8-27b-uncensored-hauhaucs` | Qwen3.8, uncensored | 9.9–10.3 | 68.6 | 82.9* | 95.7 |
| `qwen3.8-27b-stock` | Qwen3.8, stock | 12.1–12.6 | 67.1 | 82.9* | 93.3 |
| `gpt-oss-20b` | small and very fast | 66.0–67.5 | **71.4** | 72.9* | 95.1 |
| `ornith-1.5-35b-a3b` | MoE, fast | 47.8–49.6 | 61.4 | 81.4* | 92.1 |
| `g9v3-39a5b` | MoE, fast, cheap context | 39.0–40.2 | 67.1 | 68.6* | 93.9 |

**Bold** is the best in that column. Speed is tokens per second.

### Models that produced no numbers

| model | why |
|---|---|
| `qwen3.6-27b-opus-distill` | won't load — it is a vision model |
| `qwen3.6-35b-a3b-abliterated-vl` | won't load — vision model |
| `gemma4-e4b-abliterated` | won't load — unsupported architecture |

## Which gaps are real, and which are noise?

A 70-question exam cannot tell apart two models a few points apart — the difference is
as likely to be luck as skill. So each model was compared against the incumbent
question by question, and only differences that pass a statistical test are listed here.

### Real differences — all of them are the incumbent winning

Models still on the shelf come first; the rest were deleted after earlier rounds and
are shown only because they were measured on the same questions.

| test | model | behind the incumbent by | confidence |
|---|---|---:|---|
| Reasoning (thinking) | `g9v3-39a5b` | 18.6 points | p=0.002 |
| Reasoning (thinking) | `gpt-oss-20b` | 14.3 points | p=0.006 |
| Coding | `devstral-patched` | 11.6 points | p < 0.001 |
| Reasoning (thinking) | `qwen3.8-27b-unsloth` | 10.0 points | p=0.039 |
| Reasoning (thinking) | `xing4.0-29b-a4b` *(deleted)* | 47.1 points | p < 0.001 |
| Reasoning (quick) | `xing4.0-29b-a4b` *(deleted)* | 27.1 points | p < 0.001 |
| Reasoning (quick) | `nemotron-cascade-2-30b-a3b` *(deleted)* | 22.9 points | p < 0.001 |
| Reasoning (quick) | `glm-4.7-flash` *(deleted)* | 17.1 points | p=0.017 |
| Reasoning (thinking) | `nemotron-cascade-2-30b-a3b` *(deleted)* | 15.7 points | p=0.003 |
| Coding | `xing4.0-29b-a4b` *(deleted)* | 12.8 points | p < 0.001 |
| Coding | `glm-4.7-flash` *(deleted)* | 11.6 points | p < 0.001 |
| Coding | `nemotron-cascade-2-30b-a3b` *(deleted)* | 7.3 points | p < 0.001 |

### Everything else is a tie (21 comparisons)

No other model beat the incumbent on any test, and no other gap is big enough to call.
**"We can't tell them apart" is not the same as "it's as good as the incumbent"** —
and the brief asked for something better, which nothing delivered.

The closest calls, all statistically indistinguishable from the incumbent:

- `gpt-oss-20b` on reasoning (quick): an exact tie (p=1.00)
- `qwen3.8-27b-ggmlorg` on coding: -0.6 points (p=1.00)
- `qwen3.8-27b-uncensored-hauhaucs` on coding: -0.6 points (p=1.00)
- `qwen3.8-27b-unsloth` on reasoning (quick): -2.9 points (p=0.73)
- `qwen3.8-27b-ggmlorg` on reasoning (quick): -2.9 points (p=0.73)

## Can we trust these numbers?

Yes — with one named exception. The same test was repeated several times to see whether
it gives the same answer twice.

| what was repeated | times run | scores | same answers each time? |
|---|---:|---|---|
| incumbent, quick exam | 3 | 71.4, 71.4, 71.4 | **yes, identical** |
| gpt-oss, quick exam | 5 | 71.4, 77.1, 71.4, 71.4, 71.4 | **no** |
| gpt-oss, settings changed | 1 | 60.0 | only ran once |
| **incumbent, thinking exam** | 3 | 87.1, 87.1, 87.1 | **yes, identical** |

**The thinking test is perfectly repeatable.** The incumbent's 44,000-token thinking run
was done three times across two days and gave an identical result every time, down to
the individual question. So the thinking scores in the table above are solid.

**`gpt-oss-20b` is the exception.** It is the only model that gives different answers on
identical repeat runs. Its old 77.1 record could not be reproduced under any setting we
tried — including deliberately letting it think much harder, which made it *worse* (60.0).
Treat its numbers as approximate in a way no other model's are.

## How much context fits?

Context is the model's working memory for a conversation. The worry was that big models
could not hold a useful amount. **They can, easily.**

| model | biggest context tested | still fit in memory? | speed penalty |
|---|---:|---|---|
| `g9v3` | 32,768 tokens | yes, 7,783 MiB spare | none |
| `ggmlorg-q8` | 32,768 tokens | yes, 3,043 MiB spare | none |
| `incumbent` | 32,768 tokens | yes, 10,377 MiB spare | none |
| `uncensored-q6kp` | 32,768 tokens | yes, 5,687 MiB spare | none |
| `unsloth-q8` | 32,768 tokens | yes, 3,043 MiB spare | none |

Nothing ran out of memory at any size tested, and speed did not drop at all as context
grew. Two numbers in our earlier notes were simply wrong:

- We recorded that these models cost **260 KB of memory per token** of context. Measured,
  it is **72 KB** — three and a half times cheaper. The incumbent has room for roughly
  **180,000 tokens** of context, not the ~8,000 we have been running.
- We recorded `g9v3` as having **seven times** cheaper context than the others, which was
  the main reason to keep it. Measured, it is **1.6 times** cheaper. Still cheapest, but
  that is not a reason to keep a model on its own.

The one caveat: 32,768 tokens was the largest size we *tried*, not the largest that fits.
The real ceiling is higher and has not been found.

### Production has room to roughly double its context, for free

`devstral` was loaded at two context sizes during this round, which measures its
context cost directly:

| context | memory used | note |
|---:|---:|---|
| 8,192 | 25,679 MiB | the size we benchmark at |
| 16,384 | 27,023 MiB | the thinking-exam size |

That is **168 KB per token** — more than twice the 72 KB the Qwen models cost, so the
"room for 180,000 tokens" figure above is about the incumbent and does **not** carry
over to devstral. Production halves that cost again by storing its context compressed
(`q8_0`), giving roughly **84 KB per token**.

At that rate, production's current 49,152-token setting leaves about **4,400 MB unused**,
and the ceiling is roughly **100,000 tokens**. Raising production to **65,536** would
still leave ~3,000 MB of headroom and costs nothing — no new model, no new hardware, no
accuracy trade. On the evidence in this document that is worth more than any model
swap on the shelf: every win this box has produced has come from configuration —
thinking on (+15.7 points), Q8_0 over Q4_K_M (+4.27), and context — and none from
choosing a different model.

One honest caveat: the 84 KB figure is the measured 168 KB halved, not separately
measured. `ctx-ladder.sh` would confirm it in about twenty minutes, and should be run
before the change is made.

## What these tests do not cover

**All four columns are single-turn question-and-answer.** A question goes in, one
answer comes back, and it is marked right or wrong. Nothing here involves the model
calling a tool, reading the result, and deciding what to do next.

That matters most for `devstral`, because **agentic tool use is the entire job it does
in production**. Its scores above therefore say almost nothing about whether it is the
right model for that job. The evidence is in the model file itself: devstral's prompt
template carries a tool-calling section, and the local patch that gives it the
`-patched` name is a fix to that section for agentic clients. It is built for a task
none of these four tests administers.

So: **do not read "devstral scores below the incumbent" as "replace devstral".** The
honest statement is that on general knowledge and on one-shot coding problems the
incumbent is better, and on the thing production actually does, we have no measurement
at all. Getting one needs a tool-use harness, which does not exist here yet.

The same gap applies to refusal behaviour, and this round sharpened why: the quick exam
cannot even tell an uncensored model from a stock one — three versions of Qwen3.8 gave
*identical* answers to all 70 questions — so it is no evidence either way.

## What is still not done

1. **No harness measures agentic tool use**, which is the gap above and the most
   valuable one to close.
2. **Three models cannot be tested on this machine** without a newer or patched runtime.
   Worth knowing: `opus-distill` was kept on the shelf specifically to verify its claimed
   75.7 reasoning score. That claim cannot be checked here at all — the file is a vision
   model, not the text model our notes describe.
3. **The bigger 280-question exam is built but not run**, waiting on your choice of which
   models deserve it. It will need the incumbent re-run as a fresh baseline, because it
   draws different questions and its scores cannot be compared to the ones above.
4. **`devstral` has no thinking mode**, so its thinking-exam cell is not a low score —
   there is no such run to report. Its prompt template contains no thinking path at all,
   and the thinking-on attempt returned the thinking-off answers exactly.

---

## Reference

**Settings** — every score above: 70 exam questions (5 per category × 14), fixed random
seed 42, temperature 0. Quick exam: 8,192 context. Thinking exam: 16,384 context and a
12,288-token thinking budget. Coding: all 164 HumanEval problems. Identical to the
settings used in the previous two rounds, so old and new numbers are comparable.

**Data** — 65 benchmark runs on disk, each storing its own settings, question set
and per-question results.

| file | what it holds |
|---|---|
| `FINAL.md` | this document — regenerate with `./make_final.py > FINAL.md` |
| `REPORT.md` | the technical write-up: method, every finding, the bugs found |
| `DATASET.txt` | complete raw dump — regenerate with `./DATASET.sh` |
| `inventory.py` | every run with its settings and provenance |
| `pairs.py`, `mcnemar.py` | the statistical comparisons |
| `ctx-ladder/` | the context measurements |
| `WATCHDOG.log` | what the run monitor saw overnight |

**The statistics**, for anyone checking: comparisons are McNemar's exact test on paired
per-question results, not a two-proportion test — every model answers the same questions,
and discarding that pairing would both lose power and, at 70 questions, be capable of
calling a genuine 15-point gap noise. Gaps are reported as significant only at p<0.05.
