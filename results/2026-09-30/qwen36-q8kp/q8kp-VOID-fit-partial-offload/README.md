# VOID: Q8_K_P first attempt, 2026-10-01 00:00 -- partially offloaded to CPU

Stopped one minute into the first MMLU leg. Not a result.

llama.cpp in ~/llama-cuda12 defaults to `-ngl auto --fit on` with a 1024 MiB per-device
margin. For the 31.96 GB Q8_K_P that margin cannot be met fully on-GPU, so --fit silently
put ~2 layers in system RAM. Evidence: 29979 MiB resident at ctx 8192 against 29184 MiB of
non-embedding weights = ~800 MiB overhead, where the fully-offloaded incumbent and Unsloth
Q8_0 both show 1658 MiB at the same ctx. Decode 8.97-9.02 tok/s.

The run.sh TPS_FLOOR (8.0) did not catch it: a 2-layer spill costs ~15%, not the ~60% of
the spills that floor was sized against. run.sh now also checks VRAM against
non-embedding weights + overhead, and the rerun forces `--fit off -ngl 999`.

## Attempts 2 and 3 (also stopped, also not results)

2. `--fit off -ngl 999`: cudaMalloc OOM on device 1 (16257 MiB asked). The default layer
   split ignores that the last device also holds the 2.4 GB F16 output tensor.
3. `-ts 35,29`: fully resident (30841 MiB vs 30842 expected, **10.64 tok/s**), but device 1
   at 16072/16384 MiB -- too little room for the extra KV at ctx 16384. Stopped after one
   minute and rerun as `-ts 36,28`. Its ladder row is in `attempt3-ts35-29/`.
