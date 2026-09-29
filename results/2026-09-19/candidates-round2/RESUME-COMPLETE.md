# Round 2b — COMPLETE 2026-09-21 03:17

All requested work is finished. Rig idle, GPU free, production devstral router on :8080
never touched. Results are in REPORT.md.

## What was asked, and what happened

1. **G9v3 row filled, INCOMPLETE banner dropped.** 93.90% HumanEval / 67.14% MMLU-Pro /
   39–40 tok/s. MoE, 32-of-320 experts, 2.66 GB/token active, KV 38 KiB/token.
2. **Thinking-on MMLU-Pro re-run**, reported as its own column, thinking-off untouched.
   Extended to the incumbent and shelf qwen3.8 (user-approved) so the column has a baseline.
3. **Three new Qwen3.8-27B quants** benchmarked thinking-off at ctx 8192.

## The three conclusions that survive a paired (McNemar) test

* **Thinking mode is worth ~+15.7 points** (incumbent 71.43 -> 87.14, p=0.013).
* **Q8_0 beats Q4_K_M** on HumanEval: 7 tasks fixed, 0 broken (p=0.016).
* **Nemotron, Xing and G9v3 are genuinely worse** than the incumbent in thinking mode
  (p=0.003 / <0.001 / 0.002). Ornith and shelf qwen3.8 are *not distinguishable* from it.

**No model beat the incumbent, in either mode.** The closest, `qwen3.8-27b-unsloth:q8_0`,
ties it (HumanEval +2 tasks p=0.73, MMLU -2 questions p=0.73) at 10.9 vs 11.1 tok/s and
29.0 GB vs 20.8 GB. Both robust wins are configuration changes, not model swaps.

## Rig facts learned — all cost time, all now encoded in the scripts

* **`bc` is not installed.** A `gpu_mib()` piping through it returns empty and its numeric
  guard silently never fires. Use `awk`.
* **`stop_router` must kill the per-model CHILD servers and POLL until VRAM frees.** The
  child holds the model ~20s after the parent dies. Loading onto a dirty GPU makes
  llama.cpp leave most layers in system RAM and run on CPU at a quarter speed, silently.
* **Load looks exactly like a CPU spill for ~150s** (RSS climbs to model size, VRAM ~0,
  then one upload burst). Only judge spill past 300s. A real spill keeps RSS high AND VRAM
  low indefinitely.
* **`--api-timeout` defaults to 900s and is too short for thinking-on.** Needs
  `num_predict / tok_s` seconds: 232s at 53 tok/s, 1024s at 12 tok/s. A timeout yields
  `eval_count=0`; cap-truncation yields exactly num_predict. Different causes, different
  fixes, and easy to confuse.
* **`reasoning_effort` is not portable.** Qwen3.8 templates validate it against
  ('xhigh','medium','low') and raise a Jinja exception otherwise -> router 500 -> 0.0% in
  94 seconds. Other models ignore the field entirely. The shim omits it.
* **num_predict 4096 is far too small for thinking-on**; 12288 still truncates `law` on
  every candidate. Always read a thinking-on score together with its parsed count.
* **"Among answered" does not extrapolate.** Measured: a 93.33%-among-answered run came in
  at 82.86% once the missing batches actually ran (they scored 2/10).
* **A guard that can crash is not a guard.** `dict.get(k, 0)` returns None when the key
  exists with a None value; the f-string then raised TypeError and killed the whole summary
  *including its RIG-FAIL line*, so a fully-failed run logged as a bare "think DONE".
* **`pgrep`/`pkill -f <pattern>` matches any shell whose argv contains the pattern**,
  including the watcher you started and the command doing the killing. Bracket the first
  letter (`'[l]lama-server'`); track drivers by PID from `$!`, never by grepping ps.
* **Never edit a running bash script** — bash reads by offset and executes fragments of the
  edit. `run-queue-6.sh.ABANDONED-corrupted-live-edit` is the wreckage.
* **`driver.log` accumulates across abandoned attempts.** Anchor reads to the run's own
  `QUEUE-n START` marker.
* **The MMLU harness writes `results.json` incrementally** — existence != finished. Check
  `total == 70`.

## The change worth making before the next round

`--per-category 5` gives 70 questions, which resolves MMLU-Pro gaps of ~15-20 points and
nothing smaller. Most of round 2's margins are below that. Use `--per-category 20` (280
questions) before asking this harness to rank models that are close.

## Files

    REPORT.md                              the result
    bench_think.sh                         thinking-on MMLU; asserts thinking engaged,
                                           full 70-question coverage, flags timeouts
    summarise_think.py                     prints the thinking-on column
    run-queue-{7,8,9}.sh                   the drivers that produced it
    mmlu-*-think12288/                     thinking-on raw results
    mmlu-ornith-think4096-TRUNCATED/       evidence: budget too small
    mmlu-qwen38-27b-think12288-TIMEDOUT/   evidence: client timeout
    scripts/ollama_shim.py.bak-2026-09-20  pre-force-think backup
    scripts/think_probe.py                 one request, confirms a --force-think shim is
                                           really reasoning BEFORE committing hours to a run
