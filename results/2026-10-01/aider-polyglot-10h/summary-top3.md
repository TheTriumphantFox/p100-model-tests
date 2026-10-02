Common prefix: **50 exercises** (cpp 6, go 9, java 10, javascript 11, python 7, rust 7)

| Model | pass@1 | pass@2 | malformed replies | exceptions | output tok/exercise | wall s/exercise | scored total |
|---|---:|---:|---:|---:|---:|---:|---:|
| qwen3.6-35b-a3b_ud-q6_k | 10/50 (20%) | **24/50 (48%)** | 1 | 0 | 2301 | 82 | 50 |
| qwen3.6-27b-abliterated_q5_k_m | 12/50 (24%) | **28/50 (56%)** | 0 | 0 | 1856 | 293 | 50 |
| qwen3.8-27b-unsloth_q8_0 | 8/50 (16%) | **17/50 (34%)** | 0 | 0 | 2439 | 424 | 50 |

**pass@2 by language** (passed/attempted on the common prefix)

| Model | cpp | go | java | javascript | python | rust |
|---|---:|---:|---:|---:|---:|---:|
| qwen3.6-35b-a3b_ud-q6_k | 3/6 | 4/9 | 4/10 | 8/11 | 2/7 | 3/7 |
| qwen3.6-27b-abliterated_q5_k_m | 3/6 | 6/9 | 2/10 | 7/11 | 4/7 | 6/7 |
| qwen3.8-27b-unsloth_q8_0 | 2/6 | 2/9 | 2/10 | 6/11 | 2/7 | 3/7 |

**Paired comparison (exact McNemar, pass@2)**: row passed & column failed / reverse, p

| | qwen3.6-35b-a3b_ud-q6_k | qwen3.6-27b-abliterated_q5_k_m | qwen3.8-27b-unsloth_q8_0 |
|---|---|---|---|
| qwen3.6-35b-a3b_ud-q6_k | — | 6/10 p=0.45 | 9/2 p=0.07 |
| qwen3.6-27b-abliterated_q5_k_m | 10/6 p=0.45 | — | 13/2 p=0.01 |
| qwen3.8-27b-unsloth_q8_0 | 2/9 p=0.07 | 2/13 p=0.01 | — |

Passed by every model: 13. Passed by none: 16.
