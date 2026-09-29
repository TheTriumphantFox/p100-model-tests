# Ollama runner validation

Qwen3.8 27B Q4_K_M, dual P100 Vulkan, 4096 context, one short warm-up,
then one uncached long-prompt request per server instance.

| Configuration | Prompt tokens | Prompt tok/s | Generation tok/s |
|---|---:|---:|---:|
| `baseline` | 1055 | 34.47 | 61.03 |
| `p100-flags` | 1055 | 256.68 | 60.93 |
