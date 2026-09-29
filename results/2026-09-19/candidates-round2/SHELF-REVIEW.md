# Shelf review — keep / toss, 2026-09-21

Everything scored across rounds 1 and 2, plus the shelf. ~424 GB of model files in four
places. **Disk is not the constraint** (5.5 TB free on /dev/sda2); the reason to prune is that
a crowded shelf makes it easy to benchmark the wrong file. VRAM (32 GB) is the real limit.

## First: a configuration that probably beats the incumbent, and has never been assembled

`ggml-org/Qwen3.8-27B-GGUF` publishes **matching draft modules** beside the weights. Measured
2026-09-20: `Q8_0 + dflash` runs at **22.72 tok/s**, 2.09x the Q8_0 baseline and **2x the
incumbent's 11.1**. Separately, an Unsloth `Q8_0` of the same base model scored the **best
HumanEval on this box: 97.56%** (160/164).

Those are two different files that have never been tested together:

| file | GB | measured | not measured |
|---|---:|---|---|
| `candidates-r2/Qwen3.8-27B-Q8_0.gguf` (ggml-org) | 28.6 | 22.72 tok/s with `dflash` | accuracy |
| `Downloads/Models/Qwen3.8-27B-Q8_0.gguf` (Unsloth) | 29.0 | 97.56% HE / 68.57% MMLU | speculative decoding |

Both are `file_type 7` (Q8_0) of `Qwen3.8-27B`, so accuracy should transfer. **The clean test is
to benchmark the ggml-org Q8_0 for accuracy** — it already has proven drafters, so this avoids
any cross-quantizer question entirely. ~75 min for HumanEval + MMLU.

If it lands where the Unsloth Q8_0 did, the result is **~97.5% HumanEval at ~22.7 tok/s**:
equal-or-better coding than the incumbent, MMLU within noise (-2.9, p=0.73), at **2x the
speed**. That would be the first configuration to actually improve on the incumbent — and it
comes from quantisation + speculative decoding, not from a new model. Consistent with the
round-2 finding that both robust wins were configuration, not model choice.

**Keep all four Qwen3.8 speculative-decoding files until this is settled** (28.6 + 29.0 + 2.1
dflash + 3.2 mtp = 62.9 GB).

## TOSS — 171 GB, no capability lost

| item | GB | why |
|---|---:|---|
| `qwen3.8-flash-next:ud-iq3_xxs` | 82.0 | Already documented as losing on quality, speed, size AND operating cost at once. MMLU 70.0 where the incumbent gets 72.9 in 20.8 GB; steady state **5.3 tok/s**, half the brief's floor, after ~20 warm-up requests, holding 30 GB VRAM + 35 GB page cache. Biggest single item on the disk. |
| `xing4.0-29b-a4b:iq4_nl` + `~/llama-cuda12-xing` | 21.2 | Worst model measured: 83.54 HE / 44.29 MMLU, -27.1 vs incumbent (p<0.001). Thinking-on it is **unmeasurable** — 8 of 14 batches never terminated within 12288 tokens. Needs a fork runtime to load at all. Nothing recommends it. |
| `nemotron-cascade-2-30b-a3b:q4_k_m` | 24.7 | 89.02 / 48.57, -22.9 vs incumbent (p<0.001). Its only claim was speed (69-70 tok/s, fastest measured) but **gpt-oss-20b does 66.1 tok/s with 77.1 MMLU in half the size**. Strictly dominated. |
| `glm-4.7-flash:q5_k_m` | 21.4 | 84.8 / 55.7 — lost both axes by 11.5 and 15.7 points. The round-1 report already concluded there was no reason to keep it. |
| `Qwen3.8-27B-UD-Q6_K` | 22.0 | Dominated on **both** axes by the Unsloth Q8_0 of the same base model: worse HumanEval (95.73 vs 97.56) *and* slower (9.8 vs 10.9 tok/s) because of the Q6_K penalty on GP100. Nothing it is best at. |

## KEEP — unique role, not replaceable by benchmark score

| item | GB | why |
|---|---:|---|
| `devstral-patched:latest` | 25.1 | Production `:8080`. Do not touch. |
| `qwen3.6-27b-abliterated:q5_k_m` | 20.8 | **Still the champion.** Nothing beat it in either mode. Only model that terminated on all 14 thinking-on batches. |
| `gpt-oss-20b:q8_0` | 12.1 | **Best MMLU-Pro ever scored here (77.1)** at 66 tok/s in 12 GB. Caveats: stock (not abliterated) and cannot be stopped from reasoning. |
| `gemma4-e4b-abliterated:q4_k_m` | 6.3 | Only audio-in model. Benchmarks do not capture this. |
| `qwen3.6-35b-a3b-abliterated-vl:q4_k_m` | 22.1 | Vision + the qwen worker. Different job. |
| Qwen3.8 spec-decoding kit (4 files) | 62.9 | See above — pending the test that may settle the whole brief. |
| `qwen3.8-27b-stock:q4_k_m` | 17.7 | Superseded on quality by Q8_0 (p=0.016) but it is the only unmodified model and the Q4 spec-decoding base. Cheap. |
| `qwen3.6-27b-opus-distill:q4_k_m` | 17.5 | Claims 75.7 MMLU — second best on the box — but that is a **Vulkan-era number never re-run on CUDA**. Keep until verified or refuted; it is a 20-minute test. |

## YOUR CALL — three that benchmarks alone cannot decide

**`ornith-1.5-35b-a3b:q4_k_m` (21.7 GB)** — the only candidate not clearly beaten. Thinking-on
81.43% vs the incumbent's 87.14% is **p=0.219, not distinguishable**, at **4.8x the speed**
(53 vs 11 tok/s). But "not distinguishable from" is not "better than", and the brief says beat.
Keep if you want a fast second opinion; toss if the brief is strict.

**`g9v3-39a5b:q4_k_m` + `~/llama-cuda12-g9v3` (24.7 GB)** — 93.90 / 67.14 at 39-40 tok/s, and
thinking-off it is **not distinguishable from the incumbent** (p=0.581). Its real distinction is
structural: **KV of 38 KiB/token against the incumbent's 256** — nearly 7x cheaper context. It is
the only model here that could hold a genuinely long context in 32 GB. Nothing in this brief
tested long context, so that value is unmeasured. Keep if long context matters; toss otherwise.

**`Qwen3.8-27B-Uncensored-HauhauCS Q6_K_P` (25.9 GB)** — scores identically to UD-Q6_K
(95.73 / 68.57) and carries the same Q6_K speed penalty, so on benchmarks it is a toss. But it is
**uncensored**, and nearly the whole shelf is a deliberate abliteration choice. **No harness here
measures refusal behaviour** — so this is exactly the axis the numbers are blind to. Keep it if
you want an unrestricted Qwen3.8; if so, note that an abliterated **Q8_0** would dominate it, and
be worth looking for.

## What is still unmeasured, and would change these answers

* **Agentic tool use** — what pi actually asks of devstral, and what ornith/xing/nemotron are
  sold on. No harness here covers it.
* **Refusal behaviour** — the shelf is deliberately abliterated; `gpt-oss-20b` and all four
  round-2 candidates are stock. Nothing measured what they refuse.
* **Long context** — g9v3's 38 KiB/token KV is a structural advantage no test exercised.
