# Devstral and three other local models on tau-bench retail — 2026-09-22/23

Can `devstral-cuda` drive a multi-turn tool-calling agent loop on this hardware,
and how does it compare to the rest of the shelf? Full 115-task retail split,
scripted user, four models.

## Headline

**Tool calling is not where these models fail.** Zero tool-call parse failures
across 375 completed tasks and roughly 4,000 model calls, on four different
architectures (mistral3, gpt-oss, qwen35, g9v3). llama.cpp's `--jinja` parsers
handled every format correctly. Every failure in this run was reasoning or
policy behaviour, not call emission.

**The scripted user penalises models that ask, but less than it first appeared.**
A model that stops to ask a question never gets an answer and scores zero. After
splitting those stalls by whether the model had even found the order it was meant
to act on, the stall confound can at most *tie* devstral and gpt-oss; it cannot
reverse them. See "The stall confound" below.

**Every passing write broke the task policy.** The retail system prompt requires an
explicit "yes" before any cancel, modify, return or exchange. The scripted user
never says yes, so 0 of 560 writes across the four runs were confirmed. This
harness scores models on whether they act *without* the confirmation their
instructions demand.

| Model | n | Pass | Stall: lookup | Stall: asking | Ceiling | Unterm. | Err | Parse fail | Hours |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| qwen3.6-27b-abliterated q5_k_m | 115 | **76 (66.1%)** | 2 | 6 | 71.3% | 9 | 8 | 0 | 7.80 |
| g9v3-39a5b q4_k_m *(partial)* | 30 | 17 (56.7%) | 0 | 9 | 86.7% | 0 | 0 | 0 | 1.09 |
| devstral-patched q8_0 | 115 | 61 (53.0%) | 0 | 5 | 57.4% | 3 | 0 | 0 | 3.45 |
| gpt-oss-20b q8_0 | 115 | 52 (45.2%) | **16** | 14 | 57.4% | 0 | 0 | 0 | 1.52 |

All stall columns count *failed*, completed, error-free tasks whose ground truth
contains a write and where the agent made none.
*Stall: lookup* = the agent never opened any order the ground truth acts on, so it
would have failed whatever the user said. A model failure.
*Stall: asking* = it found the right order, then ended on a question (`run.py`'s
`ASKING` regex). This is the only kind of stall the harness can be blamed for.
*Ceiling* = (pass + asking stalls) / n, an upper bound: it assumes every answered
question would lead to a correct write.
gpt-oss and qwen3.6 each had one more stall that found the order and stopped
silently. `summarise.py` prints all of these.

## Setup

- Router: llama.cpp CUDA 12.6 sm_60 build, `--jinja`, ctx 32768, f16 KV,
  `--models-max 1`, one model resident at a time.
- f16 KV is not a preference. The g9v3 fork's graph aborts on a quantized cache
  (`GGML_ASSERT(obj_new)` in `build_arch_graph`) — context size was never the
  problem, q8_0 was. Using f16 everywhere put all four models on one config.
- g9v3 additionally needs the fork build at `~/llama-cuda12-g9v3`; mainline
  reports `unknown model architecture: 'g9v3'`.
- Both Qwen models ran with `enable_thinking: false`, verified rather than
  assumed: `reasoning_content` empty and completion tokens halved (98→52, 95→52)
  with the tool call still correct. Matches the thinking-off basis of every other
  shelf benchmark here. gpt-oss reasons intrinsically via harmony and cannot be
  cleanly switched off; devstral does not reason at all.
- Scoring is tau-bench's own `calculate_reward()`, unmodified: ground-truth
  actions replayed against a fresh database, state hashes compared, plus
  required-output substring checks. No partial credit.

### The user side is scripted, and it is the dominant caveat

Real tau-bench drives the customer with a frontier LLM. No metered API key is
configured on this box, and 24–28 GB of agent weights leave no VRAM for a second
local model. So the customer is deterministic: the full instruction arrives on
turn 1, and every later user turn is a fixed, information-free nudge.

**These numbers are not comparable to published tau-bench results**, and the
reason is worse than "it is easier". It is *differentially* easier.

## The stall confound

A scripted user cannot answer a question. A model that pauses to ask "Option A or
Option B? Confirm the payment method?" never gets an answer, never mutates, and
scores zero — no matter how good its tool use was up to that point.

But not every stall is a model waiting on the user. Many never found the order
the task is about. Each stall is therefore checked against the ground truth: did
the agent call `get_order_details` on any order the correct writes touch?

- **gpt-oss stalled on 31 failed tasks, and 16 of them never opened the target
  order.** In 15 of the 16 it identified the user, never called
  `get_user_details` (which lists every order), and asked the customer for an
  order ID it could have looked up — tasks 6, 58 and 112 stop after a single
  lookup call. That is a tool-use failure, not caution. Only 14 stalls found the
  right order and then asked. Some of those are legitimate by policy: a
  cancellation reason the task script withholds until asked (114), or a second
  payment method when a gift card falls short (49).
- **Its upper-bound ceiling is 57.4%, exactly devstral's.** An earlier draft of
  this report counted every stall ending in a question as harness-caused, giving
  ~61–62%, and concluded the ordering was not safe. With lookup failures removed,
  the harness can at best tie the two models. On observed scores, devstral leads.
- **devstral stalled on only 5 tasks, all after finding the order** — it acts.
  That is why it scores respectably here. The next section explains why "acts" is
  not simply a virtue.
- g9v3's opening was misleading: 0/8 early with a 75% stall rate, which looked
  structural. Over 30 tasks it recovered to 56.7%. The early diagnosis was drawn
  from too small a sample; the 30-task figure is the honest one, and it is still
  partial.

### Failure attribution

Every failure, by cause:

| | devstral | gpt-oss | qwen3.6 | g9v3 (30) |
|---|---:|---:|---:|---:|
| stall — found the order, asked *(harness-attributable)* | 5 | 14 | 6 | 9 |
| stall — never opened the target order | 0 | 16 | 2 | 0 |
| stall — found the order, stopped silently | 0 | 1 | 1 | 0 |
| acted, wrong arguments | 36 | 22 | 19 | 3 |
| acted, required output missed | 10 | 10 | 2 | 1 |
| unterminated | 3 | 0 | 1 | 0 |
| error (TimeoutError) | 0 | 0 | 8 | 0 |
| **total failures** | **54** | **63** | **39** | **13** |
| harness-attributable share | 9.3% | 22.2% | 15.4% | 69.2% |

The stall totals match the earlier draft (5, 31, 9, 9); only the split changed.
The "asking" test is `run.py`'s `ASKING` regex, which matches any final message
ending in a question, so it is generous. The ceilings are upper bounds twice
over.

Two conclusions survive the confound:

- **Devstral's score is mostly real.** Two-thirds of its failures (36/54) are
  writes committed with wrong arguments; only 9.3% is harness. 53.0% is close to
  its true capability under this setup.
- **gpt-oss's caution is half a lookup habit.** It is 2.3x faster than devstral
  and ties it at the upper bound, but 16 of its 31 stalls are it asking the
  customer for something `get_user_details` would have told it. A control plane
  can supply a "yes"; it cannot supply an order ID the model did not think to
  look up. That weakens the case for gpt-oss as a *gated* planner, though it
  does not kill it.

g9v3's 69.2% harness share is the largest here, and on 30 tasks its 86.7%
ceiling is the least reliable number in the report.

### The policy requires a yes the harness never gives

The retail system prompt, verbatim: *"Before taking consequential actions that
update the database (cancel, modify, return, exchange), you have to list the
action detail and obtain explicit user confirmation (yes) to proceed."*

Neither user policy ever says yes. The turn-1 restatement ends "Please go ahead
and complete it", which is a blanket go-ahead given before the agent has listed
anything. That does not satisfy the policy as written. `summarise.py` counts
writes issued before any user turn containing "yes", after removing the task
instruction from each turn:

| | devstral | gpt-oss | qwen3.6 | g9v3 (30) |
|---|---:|---:|---:|---:|
| writes issued | 250 | 125 | 156 | 29 |
| …without a prior "yes" | 250 | 125 | 156 | 29 |
| passes containing an unconfirmed write | 56/61 | 44/52 | 72/76 | 13/17 |

The remaining passes are tasks that needed no write. Under this harness, then,
no model can pass a write task while following its instructions. A model that
lists the action and asks for a yes is complying, and scores zero for it.

This does not separate the models from each other: every write is unconfirmed
by construction. What it changes is how devstral's low stall rate reads. Devstral
is not merely decisive; it treats the blanket go-ahead as enough and **does not
follow the confirmation rule in its own system prompt**. For an AIOS-style
planner, that means a prompt-level "confirm before writing" rule cannot be relied
on to gate devstral. The gate has to live in the control plane: the tool layer
refuses writes that lack a confirmation token. The metric becomes informative
once a real user simulator exists: a user that can say yes turns "unconfirmed
writes" into a per-model policy-violation rate.

Devstral also writes more than the task needs: 250 writes against 178 in the
ground truth. Counted task by task, 87 of its writes exceed what the task called
for, against 10 for gpt-oss and 16 for qwen3.6. See failure mode 2 below.

### Attempted fix: the `confirm` user policy, and why it did not work

`run.py --user-policy confirm` answers a confirmation request affirmatively and
re-states the instruction, instead of the default `nudge` which adds nothing.
A/B on devstral tasks 40-63:

| | nudge | confirm |
|---|---:|---:|
| Pass | 14/24 | 15/24 |
| Stalled | 5 | **0** |
| Mean steps | 10.3 | 15.7 |
| Cost per task | 98 s | 147 s (1.49x) |

Gained 40, 45, 55, 58. **Lost 56, 60, 62.** Net +1 on 24 tasks, and a net *loss*
on the 51-63 sub-block (7/13 -> 6/13). Within noise, at 1.5x the cost.

The stall confound is genuinely eliminated (5 -> 0), but an over-action confound
replaces it. Extra user turns push models to act more and mutation counts rise
across the board. Task 62 is the clearest case: its correct behaviour is to
change **nothing**, and under `confirm` devstral issued a spurious
`cancel_pending_order`. Narrowing the wording to explicitly refuse a wider
mandate ("I'm not adding anything to my original request; if what I asked for
doesn't require a change, don't make one") made task 62 *worse* -- two spurious
mutations instead of one. The driver is the extra turn itself, not its wording.

`nudge` therefore stays the default, the numbers above stand, and pass rate
should be read alongside stall rate rather than either policy being trusted
alone. The structural fix is a real user simulator: a canned reply cannot
distinguish "yes, do the thing you asked about" from "no, that is outside what I
asked for". `gemma4-e4b` (6.0 GB) alongside devstral (23.9 GB) fits in 32 GB with
roughly 2.8 GB left for both KV caches, so a local LLM customer is feasible but
unbuilt.

## Failure modes seen

From the 5-task diagnostic pass (see git history of this folder) and confirmed at
scale:

1. **Miscounting over tool output.** Asked how many T-shirt options are
   available, devstral answered 11. The data holds 12 variants, 10 of them
   `available: true`. It called `get_product_details` correctly, received the
   flags, and miscounted the filter — an aggregation error, not a tool error.
2. **Duplicate mutation.** devstral re-issued a write with byte-identical
   arguments **24 times across 14 tasks** (2, 5, 11, 20, 22, 34, 49, 52, 53, 58,
   75, 78, 91, 97), not recognising that the first call had succeeded. qwen3.6 did
   it twice in one task; gpt-oss and g9v3 never did. It was mostly harmless *here*
   only because the retail backend guards state. 20 of the 24 repeats were
   rejected ("non-delivered order cannot be returned", "non-pending order cannot
   be modified"), and the other 4 were identical `modify_user_address` rewrites.
   5 of the 14 tasks still passed. A backend without those guards would have
   executed every one. The most concerning class for a control plane, and an
   argument for idempotency keys on every write tool.
3. **Wrong variant selection.** Right tool, right order, wrong `new_item_ids`.
4. **Confirmation stall.** Discussed above.

17 tasks were solved by no model. Their required outputs are dominated by long
numeric strings (`746342064230`, `1288.65`, `46.66`), i.e. exact-value reporting
rather than tool sequencing.

## Cost

| Model | Wall clock | vs devstral |
|---|---:|---:|
| gpt-oss-20b | 1.52 h | 0.44x |
| devstral | 3.45 h | 1.00x |
| qwen3.6-27b | 7.80 h | 2.26x |

qwen3.6 buys 13 points over devstral for 2.3x the wall clock, 3x the unterminated
count, and 8 `TimeoutError` tasks that devstral did not have. gpt-oss is 2.3x
faster than devstral and, at the most generous reading of the stall confound,
ties it (57.4% each). It never issued a duplicate write.

## Caveats

- g9v3 is 30/115, stopped deliberately once the early read looked structural.
  Its 56.7% is a partial sample and is not directly rankable against the others.
- qwen3.6 lost 8 tasks to `TimeoutError` — scored as failures. Its true rate is
  somewhat higher than 66.1%.
- Scripted user, as above. The `.PARTIAL-superseded-by-unsloth` files are from
  the abandoned uncensored-Q6_K_P leg and contain no results.
- `qwen3.8-27b-unsloth_q8_0` was pulled from this run to be scheduled separately;
  `drive_unsloth.sh` is staged and unrun.

## Reproducing

```fish
cd ~/Projects/Tests/2026-09-22/devstral-tau-scripted
./drive_all.sh          # devstral, gpt-oss, qwen3.6, g9v3 -- resumable
./drive_unsloth.sh      # qwen3.8 unsloth q8_0, standalone
../../.venv/bin/python summarise.py
```

Each model is skipped if its JSON already holds 115 results, so an interrupted
run resumes at the model boundary.

`summarise.py` is CPU-only and prints every number in this report except the
A/B: pass/cost, stall kinds and ceilings, unconfirmed writes, and writes beyond
the ground truth plus duplicate writes.
