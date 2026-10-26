# Strata + Flash-Next IQ3_S: fixed split 39 + STRATA_STAGE_TRIM=1, 2026-10-25

Restart of the :8090 Strata server with three config changes, then the same benchmark as
`../../2026-10-12/strata-flash-next-iq3s/` (`bench/results/2026-10-06-community-2x-p100/benchmark.py`,
3 serial fresh 127,736-token prompts, 256-token cap, greedy, reasoning off, after a warm-up).

Config changes (`~/AI/Strata/strata-iq3_s.json`; backup `strata-iq3_s.json.bak-pre-stagetrim-2026-10-25`):

- `"layer_split": "39"` (was `"auto"`, which also chose 39; K=36 was a near tie)
- `"env": {"STRATA_STAGE_TRIM": "1"}`: each card loads only its own layers' dense weights
- `"expert_profile_save": "expert-profile-learned.bin"`: first save written 19:41 (196 KB)

## Experts on the GPUs

| | 2026-10-12 first run | 2026-10-25 before restart | **2026-10-25 now** |
| --- | ---: | ---: | ---: |
| GPU0 slots (layers 0-38) | 5,251 | 4,538 | **4,894** |
| GPU1 slots (layers 39-47) | 4,367 | 4,251 of 4,608 | **4,608 of 4,608** |
| Total | 9,618 | 8,789 | **9,502** |
| VRAM used GPU0 / GPU1 | 15,960 / ~15,960 MiB | 15,977 / 15,961 MiB | 15,961 / 13,785 MiB |

The 2026-10-12 run had no vision, no control vector and no `--vram-reserve-mib 700`; vision (added
2026-10-18) cost ~830 slots. Trimming won back ~710 of them. GPU1 now caches every expert of its 9 layers
and leaves ~2 GiB of VRAM unused, so a split giving GPU1 more layers (36-37) may help further.

## Benchmark

| | 2026-10-12 | **2026-10-25** |
| --- | ---: | ---: |
| Prompt tok/s, median [range] | 366.2 [363.6-368.2] | **375.7** [375.5-376.3] |
| Decode tok/s, median [range] | 34.9 [33.4-37.2] | **34.7** [34.5-37.9] |
| Client TTFT s, median | 348.9 | **340.1** |
| Client total s, median | 355.7 | **347.2** |
| Decode hit rate, runs 1-3 | 88.4 / 92.2 / 91.9% | 81.5 / 88.9 / 88.7% |

| Run | prompt_ms | decode_ms | decode tok/s | drafts accepted | hit rate | PCIe share | TTFT s | total s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 340,007 | 7,368 | 34.7 | 152/215 | 81.5% | 4.9% | 340.1 | 347.4 |
| 2 | 340,200 | 6,756 | 37.9 | 158/203 | 88.9% | 2.8% | 340.3 | 347.2 |
| 3 | 339,413 | 7,427 | 34.5 | 143/214 | 88.7% | 2.8% | 339.5 | 347.0 |

All runs `finish=length`, 0 reused tokens, coherent text. Prompt +2.6%, decode unchanged within run-to-run
spread. The 2026-10-25 config also carries vision, the control vector and a 700 MiB reserve, so the two columns
are not an identical-config A/B; the before-restart config (8,789 slots) was not benchmarked. Needles not run.

## Memory

Watchdog (3 GiB floor, detached): minimum MemAvailable **4.24 GiB**, no kills. Swap held 2.38 GiB from before the
start, peaked at 3.54 GiB and settled at 2.95 GiB. `memory-samples.csv` (5 s samples).

## Files

- `launch.sh` (detached server + watchdog; stop with `kill $(cat watchdog.pid)` and SIGTERM server.py), `ram_watchdog.sh`
- `server-*.log`; `bench/`: `results.json`, `summary.json`, `benchmark.log`, per-request raw JSON,
  `engine-startup.log`, `initial-status.json`, `strata-iq3_s.json` (config as run)

In this repository: everything above except the per-request raw JSON (the prompts are rebuilt by
`../../2026-10-12/strata-flash-next-iq3s/benchmark.py`; `results.json` keeps every reply).
