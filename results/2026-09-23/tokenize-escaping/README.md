# Raw vs JSON-escaped tokenization of planner replacement content — 2026-09-23

Question: would a v7.3 grammar that emits the replacement file as a raw delimited block,
instead of a JSON string, buy meaningful planner throughput?

Method: the ideal plan's `expected_content` for all 40 planner-bench tasks, tokenized with
each candidate's own tokenizer through `llama-server /tokenize` (CPU only, `--device none`,
no warmup, port 8093; about 2 minutes per model, dominated by loading from the spinning disk).
`run.sh` drives it and `measure.py` measures. `plan_json` is the plan as `selftest.py` renders it (compact); `plan_block`
is the same plan with `content` moved into a `<<<CONTENT … CONTENT>>>` block.

| model | raw B/tok | escaped B/tok | escaped / raw tokens | whole-plan tokens saved by raw block |
|---|---|---|---|---|
| devstral | 3.06 | 2.44 | 1.25 | 18.3 % |
| g9v3 | 3.16 | 2.51 | 1.26 | 19.2 % |
| gpt-oss | 3.27 | 2.67 | 1.22 | 16.9 % |
| ornith | 2.72 | 2.62 | 1.04 | 3.6 % |
| qwen3.6 | 2.72 | 2.62 | 1.04 | 3.6 % |
| qwen3.8 | 2.72 | 2.62 | 1.04 | 3.6 % |

ornith, qwen3.6 and qwen3.8 share the Qwen tokenizer, so their results are identical.
`ensure_ascii` makes no difference, because the content is almost all ASCII. The `escaping`
family (JSON inside JSON) is no worse than the other families.
`activation` files are hash-heavy and tokenize at about 1.7 B/tok either way.

## Findings

1. **The escaping penalty is about 22–26 % extra content tokens for the Mistral, gpt-oss and g9v3
   tokenizers, and about 4 % for the Qwen tokenizer.** The Qwen vocabulary encodes `\n`, `\"` and
   indentation runs almost as cheaply as their raw forms.
2. **The earlier "1.85 bytes/token" figure was not an escaping measurement.** It was 1,437
   content bytes ÷ 777 total completion tokens from the devstral smoke run
   (`../planner-bench/smoke/`). That total includes the pretty-printed plan scaffolding (handle,
   64-hex hash, check calls, indentation), about 150–250 tokens of fixed overhead, which dominates a 1.4 KiB file.
   Content-only escaped devstral is 2.44 B/tok.
3. **Capacity, content only, prefill ignored** (size family, measured decode rates):

   | model | tok/s | 120 s escaped → raw | 240 s escaped → raw |
   |---|---|---|---|
   | devstral | 12 | 3.5 → 4.3 KiB | 6.9 → 8.7 KiB |
   | qwen3.6 / 3.8 | 12 | 3.7 → 3.9 KiB | 7.4 → 7.7 KiB |
   | g9v3 | 39 | 11.5 → 14.6 KiB | 23.0 → 29.1 KiB |
   | ornith | 48 | 14.8 → 15.5 KiB | 29.7 → 31.0 KiB |
   | gpt-oss | 66 | 20.8 → 25.5 KiB | 41.6 → 51.0 KiB |

   Ignoring prefill overstates these limits: in the smoke run, 1,112 prompt tokens took 5.6 s,
   so a large source selection can take tens of seconds of the deadline before the first output token.

## Verdict

A raw-block grammar is not worth a spec amendment for the likely planner. The binding
case is the dense 27B models at 12 tok/s, and the Qwen ones gain about 4 %. Devstral would gain
about 0.8 KiB at 120 s. The MoE models gain more tokens, but they already fit the 16 KiB write
limit within 240 s, apart from g9v3 at 120 s. The amendment would also bring its own parser
risks (a sentinel collision inside the content). Keep the JSON grammar.
