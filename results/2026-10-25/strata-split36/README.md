# Strata + Flash-Next IQ3_S: layer split 36 vs 39 (STRATA_STAGE_TRIM=1), 2026-10-25

Follow-up to `../strata-stagetrim/` (split 39). Same config except `"layer_split": "36"`, same benchmark
(`bench/results/2026-10-06-community-2x-p100/benchmark.py`, 3 serial fresh 127,736-token prompts, 256-token
cap, greedy, reasoning off, after a warm-up). **Split 36 won on both prompt and decode and is kept** in
`~/AI/Strata/strata-iq3_s.json`.

## Experts on the GPUs

| | Split 39 | **Split 36** |
| --- | ---: | ---: |
| GPU0 (layers 0-38 / 0-35) | 4,894 slots | **5,020** |
| GPU1 (layers 39-47 / 36-47) | 4,608 of 4,608 | **5,633** of 6,144 |
| Total | 9,502 | **10,653** (+12%) |
| VRAM used GPU0 / GPU1 | 15,961 / 13,785 MiB | 15,727 / 15,851 MiB |

## Benchmark

| | Split 39 | **Split 36** | Change |
| --- | ---: | ---: | ---: |
| Prompt tok/s, median [range] | 375.7 [375.5-376.3] | **401.7** [400.8-401.8] | +6.9% |
| Decode tok/s, median [range] | 34.7 [34.5-37.9] | **35.7** [35.5-36.6] | +2.9% |
| Client TTFT s, median | 340.1 | **318.1** | -22 s |
| Client total s, median | 347.2 | **325.5** | -22 s |
| Decode hit rate, runs 1-3 | 81.5 / 88.9 / 88.7% | **93.5 / 93.8 / 92.8%** | |
| PCIe share, runs 1-3 | 4.9 / 2.8 / 2.8% | 1.5 / 1.4 / 1.7% | |

| Run | prompt_ms | decode_ms | decode tok/s | drafts accepted | hit rate | TTFT s | total s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 318,709 | 6,993 | 36.6 | 153/219 | 93.5% | 319.0 | 326.5 |
| 2 | 318,027 | 7,171 | 35.7 | 148/225 | 93.8% | 318.1 | 325.2 |
| 3 | 317,937 | 7,214 | 35.5 | 149/217 | 92.8% | 318.1 | 325.5 |

All runs `finish=length`, 0 reused tokens, coherent text. The prompt gain is well outside run-to-run spread;
the decode gain is small (the two ranges overlap), but the hit rate rose ~5 points and PCIe reads halved.
One restart per arm; needles not run. Split 39 started with the shipped expert profile, split 36 with the
learned profile saved during the split-39 session, so the starting cache contents also differ.

Versus the 2026-10-12 first run (no vision / control vector / VRAM reserve): prompt 366.2 -> 401.7 tok/s,
decode 34.9 -> 35.7 tok/s.

## Memory

Watchdog (3 GiB floor, detached): minimum MemAvailable **4.29 GiB**, no kills. Swap peaked at **4.83 GiB**
(3.54 GiB during the split-39 bench); `memory-samples.csv`.

## Files

- `launch.sh` (detached server + watchdog), `ram_watchdog.sh`, `server-*.log`, `watchdog.pid`
- `bench/`: `results.json`, `summary.json`, `benchmark.log`, per-request raw JSON, `engine-startup.log`,
  `initial-status.json`, `strata-iq3_s.json` (config as run)

In this repository: everything above except the per-request raw JSON (the prompts are rebuilt by
`../../2026-10-12/strata-flash-next-iq3s/benchmark.py`; `results.json` keeps every reply).
