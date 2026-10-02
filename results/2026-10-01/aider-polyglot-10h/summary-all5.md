Common prefix: **25 exercises** (cpp 3, go 4, java 5, javascript 6, python 4, rust 3)

| Model | pass@1 | pass@2 | malformed replies | exceptions | output tok/exercise | wall s/exercise | scored total |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-oss-20b_q8_0 | 2/25 (8%) | **4/25 (16%)** | 0 | 0 | 1957 | 58 | 25 |
| qwen3.6-35b-a3b_ud-q6_k | 4/25 (16%) | **13/25 (52%)** | 1 | 0 | 2660 | 88 | 50 |
| devstral-patched_q8_0 | 1/25 (4%) | **4/25 (16%)** | 0 | 0 | 1542 | 183 | 25 |
| qwen3.6-27b-abliterated_q5_k_m | 6/25 (24%) | **16/25 (64%)** | 0 | 0 | 1759 | 278 | 50 |
| qwen3.8-27b-unsloth_q8_0 | 5/25 (20%) | **10/25 (40%)** | 0 | 0 | 2216 | 442 | 50 |

**pass@2 by language** (passed/attempted on the common prefix)

| Model | cpp | go | java | javascript | python | rust |
|---|---:|---:|---:|---:|---:|---:|
| gpt-oss-20b_q8_0 | 0/3 | 1/4 | 1/5 | 1/6 | 1/4 | 0/3 |
| qwen3.6-35b-a3b_ud-q6_k | 3/3 | 2/4 | 1/5 | 4/6 | 2/4 | 1/3 |
| devstral-patched_q8_0 | 1/3 | 0/4 | 1/5 | 1/6 | 1/4 | 0/3 |
| qwen3.6-27b-abliterated_q5_k_m | 2/3 | 2/4 | 2/5 | 4/6 | 3/4 | 3/3 |
| qwen3.8-27b-unsloth_q8_0 | 2/3 | 1/4 | 1/5 | 3/6 | 2/4 | 1/3 |

**Paired comparison (exact McNemar, pass@2)**: row passed & column failed / reverse, p

| | gpt-oss-20b_q8_0 | qwen3.6-35b-a3b_ud-q6_k | devstral-patched_q8_0 | qwen3.6-27b-abliterated_q5_k_m | qwen3.8-27b-unsloth_q8_0 |
|---|---|---|---|---|---|
| gpt-oss-20b_q8_0 | — | 3/12 p=0.04 | 3/3 p=1.00 | 2/14 p=0.00 | 2/8 p=0.11 |
| qwen3.6-35b-a3b_ud-q6_k | 12/3 p=0.04 | — | 10/1 p=0.01 | 2/5 p=0.45 | 5/2 p=0.45 |
| devstral-patched_q8_0 | 3/3 p=1.00 | 1/10 p=0.01 | — | 0/12 p=0.00 | 2/8 p=0.11 |
| qwen3.6-27b-abliterated_q5_k_m | 14/2 p=0.00 | 5/2 p=0.45 | 12/0 p=0.00 | — | 7/1 p=0.07 |
| qwen3.8-27b-unsloth_q8_0 | 8/2 p=0.11 | 2/5 p=0.45 | 8/2 p=0.11 | 1/7 p=0.07 | — |

Passed by every model: 0. Passed by none: 5.
