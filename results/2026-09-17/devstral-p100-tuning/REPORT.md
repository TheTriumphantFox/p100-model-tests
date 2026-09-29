# Devstral Small 2 Q8_0 P100 Vulkan tuning

Run date: 2026-09-17

## Test setup

- Model: `hf.co/lmstudio-community/Devstral-Small-2-24B-Instruct-2512-GGUF:q8_0`
- Ollama 0.34.0 with two Tesla P100 16 GB cards through Vulkan
- 2,048-token context, deterministic sampling
- Two uncached 1,189-1,194-token prompt trials and 128 generated tokens per configuration
- Model was 100% GPU-resident

## Vulkan kernel flags

| Configuration | Prompt tok/s | Generation tok/s |
|---|---:|---:|
| No workarounds | 11.02 | **12.42** |
| Disable integer dot product | 255.98 | 10.18 |
| Disable MMVQ | 11.06 | 10.07 |
| Disable both (current service) | 255.83 | 10.18 |

The integer-dot-product workaround is essential for coding-agent workloads: it makes uncached prompt evaluation about 23 times faster. Removing it raises generation speed about 22%, but makes a typical multi-thousand-token Pi request dramatically slower overall. The existing service flags are therefore retained.

## Batch-size sweep with current service flags

| `num_batch` | Prompt tok/s | Generation tok/s |
|---:|---:|---:|
| 128 | 223.27 | 10.10 |
| 192 | 231.70 | 10.15 |
| **256** | **278.34** | 10.12 |
| 320 | 235.51 | 10.01 |
| 384 | 250.77 | 10.00 |
| 512 (old default) | 255.06 | **10.18** |
| 1024 | 223.15 | 10.01 |

`num_batch 256` improves uncached prompt processing by **9.1%** versus 512 while changing generation speed by less than 1%. It is now stored in Devstral's Ollama manifest alongside the existing 32K context setting.

Raw results and server logs are in this directory.
