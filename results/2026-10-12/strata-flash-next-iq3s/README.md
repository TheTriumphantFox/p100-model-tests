# Strata + Qwen3.8-Flash-Next IQ3_S on 2x P100, 61 GiB RAM — first run, 2026-10-12

First launch of Strata v0.1.43.1 (commit `a0116b2`) with `ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF` IQ3_S,
benchmarked the same way as the 2026-10-06 community 2x P100 report
(`~/AI/Strata/bench/results/2026-10-06-community-2x-p100/README.md`), which ran on a 125 GiB host.

## Result

| | This box (61 GiB) | Reference (125 GiB) | Ratio |
| --- | ---: | ---: | ---: |
| Prompt tok/s, median [range] | **366.2** [363.6–368.2] | 531.4 [526.6–532.1] | 0.69x |
| Decode tok/s, median [range] | **34.9** [33.4–37.2] | 31.2 [28.2–31.7] | 1.12x |
| Client TTFT s, median | 348.9 | 350.9 | — |
| Client total s, median | 355.7 | 360.0 | — |
| Needles at ~122k (10/50/90%) | **3 of 3** | 3 of 3 | — |

127,736-token fresh prompts (0 reused), 256-token cap (all runs `finish=length`, coherent text), greedy,
reasoning off, 3 serial runs after a warm-up.

| Run | prompt_ms | decode_ms | decode tok/s | drafts accepted | expert-cache hit rate | client TTFT s | client total s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 351,345 | 7,337 | 34.9 | 145/201 | 88.4% | 351.4 | 358.7 |
| 2 | 348,783 | 6,888 | 37.2 | 155/212 | 92.2% | 348.9 | 355.7 |
| 3 | 346,912 | 7,661 | 33.4 | 143/227 | 91.9% | 347.0 | 354.6 |

Needles (`tools/needle_bench.py --lengths 125k --depths 10,50,90`): `meadow-copper-504`, `falcon-quartz-940`,
`willow-cobalt-696`, all answered exactly; 121,970 prompt tokens, 336 / 332 / 290 s.

## Memory

RAM watchdog (3 GiB floor) ran for the whole session: **minimum MemAvailable 5.55 GiB, swap never touched,
no kills**. The 46.84 GiB expert arena loaded at 2.21 GiB/s in ~32 s; MemAvailable went 57.0 -> ~8.3 GiB
during the load and settled at ~6.6 GiB idle. VRAM peak 15,960 / 15,963 MiB. Baloo was suspended and Firefox
closed beforehand. See `memory-samples.csv` (5 s samples).

## Why prompt is slower and decode faster than the reference

- **GPU1 is on a PCIe 3.0 x4 link** (bus 16:00.0); GPU0 is x16. The engine measured 13.1 GB/s vs 3.3 GB/s and
  the auto split gave CUDA1 only layers 39–47 (reference: 0–22 / 23–47 on two x16 cards).
- **CPU: Ryzen 5 7600X, 6 cores** -> 5 expert-pool workers (reference: Xeon E5-2699 v4, 21 workers).
- Config differences from the reference (setup chose these for 61 GiB):
  - KV streaming off (no `--kv-resident 32768`): KV stays in VRAM; saves ~1.8 GB host RAM.
  - Vision off (reference had GPU vision with a 700 MiB VRAM reserve).
  - `--max-context 131072` (reference 128,000); the benchmark target is identical.
  - No `--remote-expert-opt` (a no-op on a layer split without helper caches).
- Decode still came out ahead: 9,618 resident experts on the GPUs (5,251 + 4,367), ~96.6% of profiled routed mass,
  hit rates 88–92%, and the 7600X's single-thread speed on the host path.

## Software

Engine built for sm_60 with CUDA 12.9.86 (container build, `build.log`), SHA-256 in `bench/engine-sha256.txt`;
NVIDIA driver 580.178.04; kernel 7.2.9-2-cachyos. Model and data on NVMe (`~/models/strata-data`).

## Files

- `launch.sh`, `ram_watchdog.sh` — launcher and watchdog; `server-*.log` — server output
- `bench/` — `results.json`, `summary.json`, per-request raw JSON, `benchmark.log`, `needles.json/.log`,
  `strata-iq3_s.json` (config as run), `engine-startup.log`, `initial-status.json`
- `setup.log`, `build.log` — install and build

After the run, `~/AI/.rootfs-cuda129` (9.7 GB) was deleted; podman works again, so a rebuild with
`~/Projects/Tests/scripts/build_strata_cuda12.sh` will pull `nvidia/cuda:12.9.1-devel-ubuntu24.04` instead.

In this repository: the write-up, `launch.sh`, `ram_watchdog.sh`, `benchmark.py` (copied from Strata's
`bench/results/2026-10-06-community-2x-p100/`, MIT) and `bench/` without the per-request raw JSON. The prompts are
rebuilt by `benchmark.py`, and `results.json` keeps every reply. `build.log`, `setup.log`, the server log and
`memory-samples.csv` stay in the local workspace.
