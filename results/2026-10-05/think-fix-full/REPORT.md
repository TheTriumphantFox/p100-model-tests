# Thinking-on MMLU-Pro with the anti-loop fix: Qwen3.8-27B UD-Q6_K and Flash-Next, 2026-10-05 21:00–22:17

The full 70 questions (seed 42, 5 per category, 14 categories, np 12288, ctx 16384 requested, api
timeout 2400) were run thinking-on through the `:8080` production router. Both presets carry the
2026-10-04 anti-loop fix: temp 1.0, top-p 0.95, top-k 20, min-p 0, `reasoning-effort = medium`, and
`reasoning-budget = 6144` with a cut-off message. Thinking-off legs were left out on purpose, because
the fix can't change them: the shim sends `enable_thinking:false` and a 0 budget, and the harness's
temp 0 overrides the preset sampling.

- **A**: harness sampling (temp 0). It pairs with the earlier no-fix thinking-on runs.
- **B**: `--server-sampling`, so the preset's own sampling applies, as it does for pi.

Unattended run (`night.sh`, systemd user timer `think-fix-night`). Each model had to pass a
`think_probe.py` preflight on both shims first; both showed REASONED and answered 2/2. A host-RAM
watchdog with a 6 GiB floor never fired (lowest available: 45.7 GB). Every leg returned 70/70
results.

## Results

| run | fix | accuracy | parsed | gen tokens | batches at a limit | wall |
|---|---|---:|---:|---:|---|---:|
| Qwen3.8-27B stock Q4_K_M, 09-19 (Vulkan) | no | 82.86% | 64 | 44,659 | 2 at the 12288 cap (engineering, law) | 65 min |
| qwen3.6-27b-abl Q5_K_M incumbent, 09-19 | — | 87.14% | 70 | 44,201 | 0 | 71 min |
| Flash-Next IQ2_XXS, 10-02 (`:8081`) | no | 78.57% | 59 | 67,919 | 3 at the 12288 cap (economics, history, law) | 65 min |
| **Q6_K A** (temp 0) | yes | **88.57%** | 70 | 25,130 | 2 at the 6144 budget (engineering, law) | 14 min |
| **Q6_K B** (preset sampling) | yes | **87.14%** | 70 | 25,922 | 2 at the budget (engineering, law) | 15 min |
| **Flash-Next A** (temp 0) | yes | **87.14%** | 70 | 21,023 | 1 at the budget (history) | 23 min |
| **Flash-Next B** (preset sampling) | yes | **84.29%** | 70 | 24,115 | 1 at the budget (engineering) | 23 min |

A batch "at the budget" used 6,175 tokens: the 6,144 thinking tokens, then the cut-off message,
then the answer. Every budget-hit batch still produced 5 parsed answers. Under the old 12,288 cap, a
batch that ran out produced nothing and scored 0/5.

## Paired (exact McNemar, same 70 questions)

| A vs B | gap | discordant (A-only / B-only) | p |
|---|---:|---|---:|
| Flash-Next 10-02 (no fix) vs Flash-Next A | −8.57 | 2 / 8 | 0.11 |
| Q4_K_M 09-19 (no fix) vs Q6_K A | −5.71 | 1 / 5 | 0.22 |
| incumbent vs Q6_K A | −1.43 | 1 / 2 | 1.00 |
| incumbent vs Flash-Next A | 0.00 | 3 / 3 | 1.00 |
| Q6_K A vs Q6_K B | +1.43 | 1 / 0 | 1.00 |
| Flash-Next A vs Flash-Next B | +2.86 | 5 / 3 | 0.73 |
| Q6_K B vs Flash-Next B | +2.86 | 4 / 2 | 0.69 |

## Answer

**The fix works as intended: no batch runs away any more, and every question gets an answer.**
Flash-Next went from 59 to 70 of 70 answered. It used 3.2× fewer thinking tokens (67.9k → 21.0k),
and the three categories that used to burn the whole 12,288 cap now finish. History went from
0/5 to 4/5, and economics finished in 608 tokens instead of 12,288. Its score rose from 78.57% to 87.14%. That gain is
p = 0.11, so it is not resolvable at n = 70, but all of it comes from batches that used to produce
no answers.

**Accuracy: everything with the fix ties the incumbent.** Q6_K A is 88.57%, Q6_K B and Flash-Next A
are 87.14%, and Flash-Next B is 84.29%. The incumbent is 87.14%. No pair separates (every p ≥ 0.11);
this harness only resolves gaps of ~15–20 points.

**Preset sampling (B, what pi gets) vs temp 0 (A):** 1 and 3 points lower. Neither gap is
resolvable, and both are within one or two questions. The cost of temp 1.0 sampling on this test is
not measurable at this size.

**Speed:** the Q6_K finished a thinking-on pass in 14–15 min and Flash-Next in 23 min. The 09-19
and 10-02 runs took 65–71 min. Part of that is the fix (about half the tokens), and part is the
runtime: 09-19 was Vulkan, and today's Q6_K uses tensor split plus MTP. The wall-time ratio is not a
measure of the fix alone.

## Caveats

- **Before/after is confounded.** The Flash-Next baseline ran on the `:8081` bench router at ctx
  16384; tonight it ran on the `:8080` production preset (ctx 131072, both with `--fit`). The Qwen3.8
  baseline is a different quant (Q4_K_M vs UD-Q6_K) on a different runtime (ollama/Vulkan). No
  before-run of the Q6_K without the fix exists. The 10-04 anti-loop report covers the Q8_0
  before/after on 4 categories.
- One run per leg. Leg B samples at temp 1.0, so a rerun would move by a question or two.
- The budget is shared by 5 questions per batch in this harness. pi's per-turn use is different, and
  pi's tool-calling loops are still untested.
- Law stays the weak spot (2–3/5), as it is for every model on the shelf. Only on the Q6_K did
  it run into the budget.

## Files

`night.sh`, `summarize.py` → `summary.md` (per-category tokens, full McNemar output), `driver.log`,
`preflight-*.txt`, `mmlu-{q6k,flashnext}-{A,B}/`, `watchdog.log`, `shim-1150{4,5}.log`.
