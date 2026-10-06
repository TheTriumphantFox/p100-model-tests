# Flash-Next IQ2_XXS anti-loop preset: rerun of the batches that looped, 2026-10-04

The user reported Qwen3.8 Flash-Next IQ2_XXS falling into "death loops". In the 2026-10-02 full run
(`2026-10-02/flash-next-full`), three MMLU-Pro thinking-on batches (economics, history, law)
spent the whole 12,288-token cap on "maybe the question asks…" self-checking and never answered.
Engineering finished at 11,849.

## Change (production `:8080`, `~/llama-cuda12/models.ini`, backup `models.ini.bak-2026-10-04`)

Added to `[qwen3.8-flash-next-iq2]`, following the Unsloth card and community reports (Qwen3.8-27B
HF discussion #178, ryan4yin's Flash-Next gist):

    temp = 1.0 / top-p = 0.95 / top-k = 20 / min-p = 0.0          (Qwen thinking-mode sampling)
    reasoning-effort = medium                                     (template default is xhigh)
    reasoning-budget = 6144 + reasoning-budget-message            (hard thinking cap)

Presence penalty was left at 0, as the card recommends for thinking mode. The router was
restarted, and the spawned args were checked against `/models`.

## Test

Same harness, questions and limits as 10-02 (seed 42, 5 per category, np 12288, ctx 16384,
thinking forced on), restricted to the 4 categories that came close to or hit the cap. Run via
`run.sh` through new shims on :11502/:11503 → :8080.

- **A**: harness sampling (temp 0, as on 10-02). This isolates effort plus budget.
- **B**: `--server-sampling` (new shim flag). It forwards no temperature/top_p, so the preset's
  sampling applies, as it does for pi.

| batch | 10-02, no preset | A: preset, temp 0 | B: preset sampling |
|---|---|---|---|
| economics | 4/5, **12288 cap**, 11.5 min | 4/5, 608 tok, 1.3 min | 4/5, 781 tok, 0.7 min |
| engineering | 4/5, 11849 tok, 11.2 min | 5/5, 1571 tok, 1.6 min | 4/5, 6175 tok (budget), 5.8 min |
| history | 0/5, **12288 cap**, 11.7 min | 4/5, 6175 tok (budget), 6.0 min | 4/5, 1407 tok, 1.5 min |
| law | 0/5, **12288 cap**, 12.0 min | 2/5, 1858 tok, 2.1 min | 2/5, 2843 tok, 2.7 min |
| **total** | **8/20, 46 min** | **15/20, 11 min** | **14/20, 11 min** |

Decode was 17.8–18.4 tok/s in every batch, unchanged. 20/20 answers parsed in both legs.

## Result

**No loops: 0 of 8 batches hit the cap, against 3 of 4 before.** Most batches now finish
thinking well under budget at medium effort. The budget had to stop one batch in each leg
(6,175 tokens = 6,144 + answer), and both still scored 4/5. History and law together score
6/10 in both legs, against 0/10 before. The incumbent's 10-02 pairing also had them at 6/10.
That matches the 10-02 report's estimate that the thinking-on gap was entirely down to the cap.

## Caveats

- One run per leg, 20 questions. This shows the loop is gone on these prompts. It does not
  establish an accuracy difference between A and B (15 vs 14).
- In this harness one request holds 5 questions, so the 6,144 budget is shared by five
  answers. A single pi turn gets the whole budget.
- **Not tested: pi tool-call loops** (repeating the same tool call across turns, as in
  gufo #388). That loop is outside the thinking, and the budget does not touch it. If the loop
  in pi is of that kind, it needs a separate repro.
- The preset sampling applies only when a client sends none. Any caller that sends its own
  temperature overrides it; effort and budget still apply.

## Files

`run.sh`, `compare.py`, `driver.log`, `mmlu-A/`, `mmlu-B/`, `shim-*.log`. Shim change:
`scripts/ollama_shim.py` adds a TAGS entry `qwen3.8-flash-next-iq2` → `qwen3.8-flash-next:iq2-prod`
and the `--server-sampling` flag (backup `.bak-2026-10-04`).
