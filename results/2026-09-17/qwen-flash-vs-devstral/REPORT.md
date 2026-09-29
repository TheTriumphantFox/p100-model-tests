# Qwen3.8 Flash Next vs Devstral Small 2

Run date: 2026-09-17

## Method

- Ollama 0.34.0 native `/api/chat` endpoint
- 2,048-token context
- Thinking disabled
- Temperature 0, seed 42
- 160 generated tokens per measured trial
- One 16-token warm-up followed by two measured trials
- Models unloaded between tests
- Dual Tesla P100 16 GB GPUs through Ollama/Vulkan

## Results

| Model | Residency | Cold warm-up wall time | Generation speed | Trial range |
|---|---|---:|---:|---:|
| Qwen3.8 Flash Next 176.9B UD-IQ3_XXS | 52% GPU / 48% CPU | 551.6 s | **2.05 tok/s** | 1.53-2.56 tok/s |
| Devstral Small 2 24B Q8_0 | 100% GPU | 184.8 s | **9.42 tok/s** | 8.67-10.18 tok/s |

Devstral generated about **4.6 times faster** on this machine. Qwen's 81 GB weights cannot fit in the combined 32 GB VRAM, so nearly half of its loaded allocation was CPU-resident. Devstral fit fully in VRAM.

The recorded prompt-evaluation rates are not suitable for comparison because Ollama reused the identical prompt prefix after warm-up. Generation rates and cold warm-up wall times remain useful.

Raw response timings and output previews are in `results.json`.
