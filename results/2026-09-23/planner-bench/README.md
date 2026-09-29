# AIOS planner benchmark — 2026-09-23

Which local model can serve as the AIOS planner (spec v7.1 section 4, v7.2 R58/R75/R76)?
τ-bench measured a multi-turn tool loop that AIOS forbids. This measures the actual contract:
one grammar-constrained response containing exactly one `write_lab_file` with the **complete
replacement file**, followed by the fixed check sequence for the target's kind.

## What is measured

For each of 40 tasks and each model:

- **Validation** exactly as the controller would do it (R59, section 4): strict JSON (no
  duplicate keys, floats or NaN), exact schema, registered non-context handle,
  `expected_old_hash` echoed exactly, check sequence exactly as policy requires, content
  ≤ 16 KiB and valid UTF-8. Any failure is `VALIDATION_FAILED`, which v7.2 R76 makes
  escalation-eligible.
- **Simulated checks**: `json_object`, `port_range`, `activation_state_schema`.
- **Content verdict**: `correct` (exact expected bytes), `equivalent` (same data, different
  bytes — a noisier diff for the reviewer), or `wrong`. A wrong plan that passes validation
  is the dangerous case, because only the human reviewer catches it.
- **Wall time with no limit.** Every request runs to completion. The 120 s and 240 s
  deadlines are applied afterwards, so the results show both whether a model gets it right
  and whether it gets it right in time.
- **Injection**: five tasks plant instructions in file content (a context note, a comment in
  the target, a fake "controller notice", a request to write the context handle, and a
  forwarded "customer request").

Task families: `size` (the same two edits at 1.4–15 KiB), `variety`, `context` (the value
comes from a context handle), `activation` (the section 6 demo's transaction 2), `injection`,
`nochange` (the correct result is R34 `NO_CHANGE`), and `escaping` (quotes, backslashes,
regexes, non-ASCII: JSON inside JSON).

## Deviations from the spec, deliberately

- The JSON field names inside `calls` are this benchmark's choice; section 4 fixes the
  operations but not their spelling.
- The grammar constrains structure and patterns only. It does not pin the handle or hash by
  enum, so the model still has to choose and echo them, which is what R23's
  compared-and-discarded channel exists to check. If echo errors appear, pinning them in the
  grammar is a spec option worth discussing.
- Chat templates are the GGUF-embedded ones, not reviewed pinned templates (v7.2 R75).
- **Known harness flaw, found during the run:** `bench.user_message` shows each file with its
  trailing newline stripped, so a model cannot see that the file ends with one. The prompt was
  left unchanged mid-run so every model saw identical input. Instead, `summarise.py` re-scores
  every result from its raw output and does not count a missing trailing newline against a
  model. Byte-exact counts are still reported separately. Fix the rendering before any re-run.
- **Token cap removed mid-run.** The run started with `max_tokens` 16384 as a safety net. gpt-oss
  counts its reasoning tokens against that budget and ran out before writing any content on
  large files, which is a cut-off answer, not a model result. `run.py` now sends no cap, so
  generation ends only when the model stops or the 32k context is full. From ornith onward every
  model ran uncapped. `rerun_capped.sh` (unit `planner-bench-rerun`) waits for the main run,
  moves every result that stopped at the old cap to `superseded` in its JSON, and re-runs those
  tasks. Each result records the `max_tokens` it ran under.
- `cache_prompt` is off, so every request pays full prefill, as a cold AIOS request would.
- Every model gets `enable_thinking: false`, matching the other shelf benchmarks. gpt-oss
  reasons regardless.

## Files

| File | Purpose |
|---|---|
| `tasks.py` → `tasks.json` | deterministic task generator (seed 20260923) |
| `bench.py` | projection, prompt, response schema, validator, scorer |
| `selftest.py` | CPU proof that ideal plans pass the grammar and score correct, and that broken variants are classified as intended |
| `run.py` | one model, resumable, no time limit |
| `drive.sh` | overnight driver: stops the :8080 service, runs all models, restores it on exit |
| `summarise.py` → `RESULTS.md` | tables |
| `speedtest.sh <model>` | quick fit and speed check: residency at ctx 32768, then three tasks (1.4, 7.2 and 15 KiB), results in `smoke/` |
| `smoke/` | two-task smoke run against the :8080 devstral (q8 KV, ctx 49152), 2026-09-23 18:30 |

## Running

```fish
cd ~/Projects/Tests/2026-09-23/planner-bench
../../.venv/bin/python selftest.py      # CPU only
./drive.sh                              # GPU; resumable
../../.venv/bin/python summarise.py
```

**Added 2026-09-24: `qwen3.6-35b-a3b_ud-q6_k`.** This is stock Qwen3.6-35B-A3B, unsloth UD-Q6_K,
27.3 GiB, from `unsloth/Qwen3.6-35B-A3B-GGUF` (SHA-256 verified), stored in
`/var/lib/ollama/candidates-r3/`. It was chosen as the highest quant that leaves comfortable VRAM
headroom at ctx 32768. It is the qwen MoE candidate: dense-qwen accuracy is the hope, ornith-class
speed the expectation. Re-running `drive.sh` skips the six complete models and runs only this one.

The first run was scheduled for 2026-09-23 21:00 as the transient user unit `planner-bench`
(`systemctl --user status planner-bench.timer`). Progress: `tail -f logs/driver.log`
and `logs/<model>.log`.
