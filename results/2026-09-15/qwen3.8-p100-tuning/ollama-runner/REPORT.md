# Ollama runner validation

Qwen3.8 27B Q4_K_M, dual P100 Vulkan, 4096 context, one short warm-up,
then one uncached long-prompt request per server instance.

| Configuration | Prompt tokens | Prompt tok/s | Generation tok/s |
|---|---:|---:|---:|
| `disable-int-dot` | 1055 | 118.14 | 14.81 |
| `disable-mmvq` | 1055 | 11.71 | 14.80 |
| `disable-both` | 1055 | 139.28 | 14.79 |
| `baseline` | 1055 | 11.71 | 11.09 |
