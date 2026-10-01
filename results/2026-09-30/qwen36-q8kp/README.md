# Incumbent at a higher quant: Qwen3.6-27B Q8_K_P (HauhauCS) and Q8_0 (Unsloth, stock) vs Q5_K_P

Question: does the incumbent `qwen3.6-27b-abliterated:q5_k_m` get better at a higher quant?
On Qwen3.8-27B, Q4_K_M -> Q8_0 fixed 7 HumanEval tasks and broke none (p=0.016).

## The file

The incumbent is HauhauCS `Qwen3.6-27B-Uncensored-HauhauCS-Aggressive` **Q5_K_P** (byte size
matches the v2 upload exactly; `general.version v2`). That repo has **no Q8_0** -- its top
quant is `Q8_K_P`, a custom mixed quant at 10.06 bpw, **31.96 GB**, pinned in `download.sh`
to revision `f2db94d0` with its sha256.

Second candidate, at the owner's request: Unsloth's **stock** `Qwen3.6-27B-Q8_0.gguf`
(28.60 GB, revision `82d411ac`, `download-unsloth-q8.sh`). It is not abliterated, so a gap
against the incumbent mixes quant with abliteration, and refusal behaviour is unmeasured.

Caveats carried into the result:
- the incumbent's sha256 (`9200d792...`) matches neither published Q5_K_P revision, so
  "same revision" is inferred from size + metadata, not proven;
- 31.96 GB of weights on 32 GB of VRAM: whether ctx 8192 / 16384 fit is the first thing
  `run.sh` measures. A partial CPU spill is caught by decode rate (`TPS_FLOOR`, 8 tok/s),
  not by VRAM, because the VRAM-90% check would pass a ~3 GB spill.

## Files

- `download.sh` -- resumable, size + sha256 verified, to `~/models/` (NVMe), symlinked into
  `~/llama-bench-models/`
- `queue.sh` -- runs both (Unsloth Q8_0 first; it is known to fit)
- `run.sh [rid tag slug]` -- one model: refuses a busy GPU, starts both shims + watchdog, ctx ladder,
  thinking-off legs at 8192, thinking-on at 16384, McNemar against the incumbent
- `bench_off.sh`, `bench_think.sh`, `probe.py`, `watchdog.py` -- dated copies of the
  2026-09-21 cuda-matrix harness, retargeted at this folder; settings unchanged
- baselines paired against: `2026-09-19/candidates-round2/{humaneval,mmlu}-qwen36-rerun*`

Results: `pairs-<slug>.txt`, `ctx-ladder.jsonl`, `driver.log`; write-up in `REPORT.md`.
