# Local Ollama model speed test

Run started: `2026-09-15T17:53:52.606622-04:00`

- Context: 4096 tokens
- Output cap: 160 tokens per trial
- Trials: 2 per model after a 16-token warm-up
- Temperature: 0, seed: 42, thinking disabled
- Models tested sequentially through Ollama and unloaded between models
- Generation speed is Ollama `eval_count / eval_duration`

| Rank | Model | Quant | Size | Generation tok/s | Range | Load |
|---:|---|---|---:|---:|---:|---:|
| 1 | `qwen3.6-35b-a3b-abliterated-vl:q4_k_m` | Q4_K_M | 22.1 GB | **61.90** | 61.89-61.92 | 16.5s |
| 2 | `qwen3.6-35b-a3b-abliterated:q6_k` | Q6_K | 30.6 GB | **56.20** | 56.13-56.26 | 21.5s |
| 3 | `gemma4-e4b-abliterated:q4_k_m` | Q4_K_M | 6.3 GB | **54.95** | 54.94-54.96 | 5.8s |
| 4 | `qwen3.6-35b-a3b-abliterated:q5_k_m` | Q5_K_M | 28.0 GB | **52.82** | 52.82-52.82 | 19.3s |
| 5 | `qwen3.5-9b-opus-distill:q4_k_m` | Q4_K_M | 6.5 GB | **40.67** | 40.63-40.70 | 6.8s |
| 6 | `qwen3.6-35b-a3b-abliterated:q8_0` | Q8_0 | 43.6 GB | **32.55** | 32.37-32.74 | 33.3s |
| 7 | `thinkingcap-qwen3.6-27b-q6_k:latest` | Q6_K | 22.4 GB | **12.34** | 12.34-12.34 | 16.8s |
| 8 | `qwen3.8-27b-stock:q4_k_m` | Q4_K_M | 17.7 GB | **11.15** | 11.15-11.15 | 13.5s |
| 9 | `qwen3.6-27b-opus-distill:q4_k_m` | Q4_K_M | 17.5 GB | **11.07** | 11.07-11.07 | 14.0s |
| 10 | `qwen3.6-27b-abliterated:q5_k_m` | Q5_K_M | 20.8 GB | **9.57** | 9.57-9.57 | 15.5s |
