# Qwen3.8-27B anti-loop preset: before/after on the batches that looped, 2026-10-04

The fix applied to Flash-Next earlier the same evening (`../flash-next-antiloop/REPORT.md`), now applied to
the `:8080` preset `[qwen3.8-27b-mtp]` (unsloth Q8_0, tensor split, MTP n-max 4, ctx 40960).
`~/llama-cuda12/models.ini` gained, for this section only:

    temp = 1.0 / top-p = 0.95 / top-k = 20 / min-p = 0.0   (Unsloth's Qwen3.8 thinking-mode values)
    reasoning-effort = medium                              (template default xhigh)
    reasoning-budget = 6144 + reasoning-budget-message

Backup from before both changes: `models.ini.bak-2026-10-04`. The router was restarted and the args checked.

## Test

The same harness and questions as the Flash-Next rerun (MMLU-Pro thinking-on, seed 42, 5 per category,
np 12288), on economics, engineering, history and law. On 09-19, engineering and law hit the cap.

- **0**: current production setup, **before** the change. The 09-19 run was a different runtime, so this is the real baseline.
- **A**: new preset, harness temp 0.
- **B**: new preset with the preset's own sampling (`--server-sampling`, as pi gets it).

| batch | 09-19 (round 2) | 0: before | A: after, temp 0 | B: after, preset sampling |
|---|---|---|---|---|
| economics | 5/5, 3917 tok | 5/5, 4540 tok, 4.2 min | 4/5, 1316 tok, 0.8 min | 4/5, 1344 tok, 0.6 min |
| engineering | 2/5, **cap** | 4/5, 8049 tok, 4.1 min | 4/5, 3036 tok, 1.3 min | 4/5, 5272 tok, 2.2 min |
| history | 4/5, 1708 tok | 4/5, 2236 tok, 1.4 min | 4/5, 1299 tok, 0.7 min | 4/5, 2033 tok, 1.0 min |
| law | 0/5, **cap** | **0/5, cap**, 7.1 min | **4/5**, 6175 tok (budget), 3.1 min | 2/5, 6175 tok (budget), 3.2 min |
| **total** | 11/20 | **13/20, 17 min, 16/20 parsed** | **16/20, 6 min** | **14/20, 7 min** |

Generation speed per batch: 30–34 tok/s before, 34–42 after (A) and 32–41 (B).

## Result

**The loop is fixed, but the budget does the work, not the lower effort.** Before the change, law looped
to the cap and gave no answers (4 unparsed). After it, law still ran into the 6,144 budget in both legs,
was cut off, and then answered: 4/5 and 2/5. Flash-Next differs here: medium effort alone kept most of
its batches well under budget. For Qwen3.8, the cap is what matters.

Engineering, economics and history used 40–70% fewer tokens. Overall wall time fell from 17 to
6–7 min. The single-point drop on economics (5/5 → 4/5 in both legs) is inside noise at n = 5. A
larger sample would be needed to tell whether medium effort costs accuracy on questions that
xhigh got right.

## Caveats

The same as the Flash-Next report: one run per leg, 5 questions share one budget in this harness, and
pi tool-call loops are not tested. Sampling sent by a caller overrides the preset's.

## Files

`run.sh` (`LEGS="0:11502"` for the baseline), `compare.py`, `driver.log`, `mmlu-{0,A,B}/`. The shim gained
TAGS `qwen3.8-27b-mtp` → `qwen3.8-27b:mtp-prod`.
