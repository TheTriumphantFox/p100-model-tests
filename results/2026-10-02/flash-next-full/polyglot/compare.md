Flash-Next scored 50 exercises.

| model | n (common) | pass@2 | pass@1 | mean s/exercise | Flash-Next only / model only | p |
|---|---:|---:|---:|---:|---:|---:|
| **qwen3.8-flash-next IQ2_XXS** | 50 | **21/50 (42%)** | 12 | 306 | — | — |
| qwen3.6-27b-abliterated_q5_k_m | 50 | 28/50 (56%) | 12 | 293 (FN 306) | 3 / 10 | 0.09 |
| qwen3.6-35b-a3b_ud-q6_k | 50 | 24/50 (48%) | 10 | 82 (FN 306) | 5 / 8 | 0.58 |
| qwen3.8-27b-unsloth_q8_0 | 50 | 17/50 (34%) | 8 | 424 (FN 306) | 8 / 4 | 0.39 |
| devstral-patched_q8_0 | 25 | 4/25 (16%) | 1 | 183 (FN 287) | 7 / 0 | 0.02 |
| gpt-oss-20b_q8_0 | 25 | 4/25 (16%) | 2 | 58 (FN 287) | 9 / 2 | 0.07 |

Flash-Next prompt tokens per exercise: median 6051, max 80302; exceptions 0, malformed 0, test timeouts 0
