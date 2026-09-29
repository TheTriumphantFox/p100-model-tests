# Ollama runner validation

Qwen3.8 27B Q4_K_M, dual P100 Vulkan, 4096 context, one short warm-up,
then one uncached long-prompt request per server instance.

| Configuration | Prompt tokens | Prompt tok/s | Generation tok/s |
|---|---:|---:|---:|
| `batch-256` | 1055 | 163.92 | 14.82 |
| `batch-192` | 1055 | 126.25 | 14.82 |
| `batch-320` | 1055 | 128.40 | 14.82 |
| `batch-384` | 1055 | 138.27 | 14.81 |
| `batch-128` | 1055 | 122.46 | 14.81 |
