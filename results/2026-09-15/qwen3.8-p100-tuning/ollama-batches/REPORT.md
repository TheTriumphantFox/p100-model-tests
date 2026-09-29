# Ollama runner validation

Qwen3.8 27B Q4_K_M, dual P100 Vulkan, 4096 context, one short warm-up,
then one uncached long-prompt request per server instance.

| Configuration | Prompt tokens | Prompt tok/s | Generation tok/s |
|---|---:|---:|---:|
| `batch-256` | 1055 | 163.58 | 14.82 |
| `batch-1024` | 1055 | 144.96 | 14.81 |
| `batch-2048` | 1055 | 139.97 | 14.80 |
| `batch-512` | 1055 | 139.26 | 14.76 |
