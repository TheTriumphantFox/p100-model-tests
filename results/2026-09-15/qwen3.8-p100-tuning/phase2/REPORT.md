# Qwen3.8 27B Q4_K_M P100 Vulkan tuning

Direct llama-server test, 4096 context, flash attention enabled, 32-token warm-up,
then two deterministic 128-token generation trials per configuration.
The x16 P100 is Vulkan0 and the x4 P100 is Vulkan1.

| Rank | Configuration | Generation tok/s | Prompt tok/s | Load to ready (s) |
|---:|---|---:|---:|---:|
| 1 | `no-mmvq-layer-50-50` | 14.813 | 5.771 | 5.5 |
| 2 | `no-mmvq-layer-45-55` | 14.803 | 5.743 | 5.5 |
| 3 | `no-mmvq-layer-55-45` | 14.800 | 5.756 | 5.3 |
| 4 | `no-mmvq-disable-multi-add` | 14.791 | 5.762 | 5.5 |
| 5 | `no-mmvq-transfer-queue` | 14.786 | 5.772 | 5.5 |
| 6 | `no-mmvq-disable-async` | 14.785 | 5.742 | 5.5 |
| 7 | `no-mmvq-disable-int-dot` | 14.777 | 19.447 | 5.5 |
| 8 | `no-mmvq-layer-60-40` | 14.771 | 5.780 | 5.0 |
| 9 | `no-mmvq-disable-graph-opt` | 14.688 | 5.660 | 5.5 |
| 10 | `no-mmvq-disable-fusion` | 14.560 | 5.758 | 5.5 |
| 11 | `no-mmvq-serialize` | 12.583 | 5.609 | 5.5 |
