# Incumbent at a higher quant — Q8_K_P and Unsloth Q8_0 vs Q5_K_P

*Run 2026-09-30 21:30 → 2026-10-01 02:40. Two Tesla P100s, 32 GB VRAM, `~/llama-cuda12`.*

## Answer

**Neither higher quant beats the incumbent `qwen3.6-27b-abliterated:q5_k_m` (HauhauCS
Aggressive Q5_K_P) by a margin this rig can resolve.** Every paired gap is p ≥ 0.25.
Both are within ~4% of its speed, so they also cost nothing much except context headroom.

The one consistent signal is thinking-on MMLU-Pro: **neither Q8 file got a single question
wrong that the incumbent got right** (0/2 and 0/3 discordant), and the Q8_K_P's 91.43% is
the highest thinking-on score recorded on this box. Three questions is a lean, not a result;
it would take ~280 questions (`--per-category 20`) to test it.

Unlike Qwen3.8 (Q4_K_M → Q8_0: +7 HumanEval tasks, p=0.016), going up from **Q5**_K_P buys
nothing measurable on coding. The Qwen3.8 gain was from a lower starting quant.

## Results

All three answered the same seeded questions (MMLU-Pro per-category 5 = 70 questions, seed 42;
HumanEval 164). Incumbent numbers are the 2026-09-19 runs of the same blob (sha256 `9200d792…`).

| | incumbent Q5_K_P | **Q8_K_P** (HauhauCS, abliterated) | Unsloth Q8_0 (**stock**) |
|---|---:|---:|---:|
| file | 20.8 GB | 31.96 GB | 28.60 GB |
| HumanEval | **96.34** | 95.73 | 95.12 |
| MMLU-Pro, thinking off (np 96 / 2048) | 71.43 | 71.43 | **74.29** |
| MMLU-Pro, thinking on (np 12288, ctx 16384) | 87.14 | **91.43** | 90.00 |
| decode tok/s (brief / medium / long / coding) | 11.5 / 11.1 / 11.1 / 11.1 | 11.0 / 10.6 / 10.6 / 10.6 | 11.3 / 10.9 / 10.9 / 10.9 |
| max ctx measured fully resident (f16 KV) | ~180k est. | **16384** (32768 OOM) | 32768 (3.4 GB spare) |

Thinking-on: every batch parsed, none hit the 12288 cap, so these are scores, not floors.

### Paired against the incumbent (exact McNemar, `pairs-*.txt`)

| test | Q8_K_P: incumbent-only / Q8-only | p | Unsloth Q8_0: incumbent-only / Q8-only | p |
|---|---:|---:|---:|---:|
| HumanEval | 2 / 1 | 1.00 | 4 / 2 | 0.69 |
| MMLU off | 1 / 1 | 1.00 | 0 / 2 | 0.50 |
| MMLU think | 0 / 3 | 0.25 | 0 / 2 | 0.50 |

Q8_K_P vs Unsloth Q8_0 directly: HumanEval 1/2, MMLU-think 1/2 — indistinguishable.

## The files

- **Q8_K_P is Q8_0 + F16**, no BF16: 21.80 GiB Q8_0 (398 tensors) + 6.69 GiB F16 (99 tensors),
  token embedding 1.26 GiB kept in system RAM. P100 does F16 natively, so it costs 12% more
  bytes per token than a plain Q8_0 and ~2-4% in measured speed.
- **Unsloth Q8_0 is stock Qwen3.6-27B**, not abliterated. Its gaps mix quant with abliteration,
  and refusal behaviour — the reason the shelf is abliterated — is not measured by any of this.
- The incumbent's sha256 matches neither published Q5_K_P revision of the HauhauCS repo, though
  its size matches v2 exactly and it reports `general.version v2`. Same release is inferred, not
  proven.

## What went wrong, and is fixed (the Q8_K_P took four starts)

1. **`--fit on` is the default in this llama.cpp and partially offloads silently.** It keeps a
   1024 MiB margin per device; for a file that nearly fills the cards it meets that by putting
   a few layers in system RAM. The first Q8_K_P start had ~2 layers on CPU: 29979 MiB resident
   (expected 30842), 9.0 tok/s. The 8 tok/s floor did not catch it — a 2-layer spill costs ~15%,
   not the ~60% that floor was sized for. **`run.sh` now also checks VRAM against
   non-embedding weights + 1082 MiB + 72 KiB/token**, which matches every fully-resident run
   here to within 3 MiB.
2. **`--fit off -ngl 999` then OOM'd on device 1**: the default layer split ignores that the
   last device also holds the 2.4 GB F16 output tensor (16257 MiB asked of device 1).
3. **`-ts 35,29` fit but left device 1 with 312 MiB** — not enough for ctx 16384.
4. **`-ts 36,28`**: 15603 / 15606 MiB, balanced; used for every Q8_K_P number above.

Starts 1-3 were stopped within a minute of their first leg; their partial output is in
`q8kp-VOID-fit-partial-offload/` with a README. Nothing from them is in the tables.

## Recommendation

Keep the Q5_K_P. If the thinking-on lean matters, the next step is MMLU-Pro at
`--per-category 20` (280 questions) for the incumbent and Q8_K_P, ~4.5 h each thinking-on.
If it is ever adopted, the Q8_K_P needs `--fit off -ngl 999 -ts 36,28` and tops out at ctx
16384-ish, against the incumbent's ~180k.

Raw results are in this directory: `driver.log`, `pairs-*.txt`, `ctx-ladder.jsonl`,
`humaneval-*/`, `mmlu-*/`, `throughput/`.

**Outcome (2026-10-01):** both GGUFs deleted at the owner's call — the Q5_K_P's context
headroom outweighs a gain this rig cannot resolve. `download.sh` / `download-unsloth-q8.sh`
re-fetch them byte-identically (revision- and sha256-pinned) if ever needed.
