# Qwen3.8 27B Q4_K_M tuning for dual Tesla P100

## Final configuration

- Backend: Ollama 0.34.0 Vulkan, both 16 GB P100s
- Context: 32,768 tokens
- Full GPU offload: 66/66 layers, 100% GPU
- Flash attention: enabled automatically
- Logical and physical batch: 256
- Vulkan MMVQ: disabled
- Vulkan integer dot-product path: disabled
- Tensor split: Ollama automatic layer split (about 7.25/7.84 GiB of model buffers)

The active `qwen3.8-27b-stock:q4_k_m` Ollama manifest now includes `num_batch 256` and `num_ctx 32768`. Its pre-tuning Modelfile is backed up at:

`~/qwen/context-backups/20260915-p100-tuning/qwen3.8-27b-stock_q4_k_m.Modelfile`

## Measured result

A 1,055-token uncached prompt followed by 128 generated tokens at 32K context:

| Configuration | Prompt tok/s | Generation tok/s |
|---|---:|---:|
| Ollama defaults (`num_batch 512`) | 11.71 | 11.09 |
| P100 Vulkan flags (`num_batch 512`) | 139.28 | 14.79 |
| **Final P100 tuning (`num_batch 256`)** | **164.01** | **14.82** |

Improvement over defaults:

- Prompt processing: about **14.0x**
- Token generation: about **33.6%**

`ollama ps` confirmed the final model at 32K context is **100% GPU** and occupies about 18 GB across the two cards. After installing the systemd drop-in, the live system service reproduced **165.64 prompt tok/s** and **14.85 generation tok/s** after warm-up, with both GPUs at 43–44°C and zero volatile uncorrected ECC errors.

## Why these settings

On GP100 through NVIDIA's Vulkan driver, llama.cpp's default integer dot-product path makes Qwen3.8 prompt processing extremely slow. Disabling it restores the faster fallback shader. Disabling MMVQ improves dense Q4 token decoding. A batch of 256 was consistently faster for prompt ingestion than 128, 192, 320, 384, 512, 1024, or 2048.

Layer splits from 45/55 through 60/40 made no meaningful difference. Vulkan row splitting is unsupported. Flash attention was already enabled, and disabling fusion or asynchronous submission did not help.

The two global Vulkan flags were also regression-tested on the existing Qwen3.6 35B-A3B Q4 worker:

| Configuration | Prompt tok/s | Generation tok/s |
|---|---:|---:|
| Default | 34.47 | 61.03 |
| P100 flags | 256.68 | 60.93 |

Prompt processing improved 7.4x while generation changed by less than 0.2%.

## Installed service configuration

The active systemd drop-in is `/etc/systemd/system/ollama.service.d/override.conf`, sourced from:

`~/qwen/ollama-p100-override.conf`

The service environment was verified to contain both measured Vulkan flags and the existing 30-minute keep-alive. To reinstall it later, run:

```bash
~/qwen/install-p100-ollama-tuning.sh
```

Raw benchmark data and scripts are in this directory.
