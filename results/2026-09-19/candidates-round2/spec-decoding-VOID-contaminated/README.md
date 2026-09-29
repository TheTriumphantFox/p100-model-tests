# VOID - do not use these numbers

This first speculative-decoding pass ran while the bench router on :8081 still had
`qwen3.8-27b-stock` resident from the previous HumanEval run (`--models-max 1` keeps a model
loaded; nothing unloaded it). ~17 GB of the 32.5 GB budget was already gone, so:

- `q4-baseline` 5.00 tok/s and `q8-baseline` 2.54 tok/s had layers on the CPU
- `q4-dflash` and `q8-dflash` died in `cudaMalloc` (OOM on 217 MiB and 40 MiB)
- `q4-mtp` 8.67 tok/s ran, but against a handicapped baseline

`q4-ngram-cache` crashed inside `llama_decode` with a backtrace, which may be independent
of the VRAM state - it is re-tested in the clean pass.

Re-run with the router stopped: `../spec-decoding/`.
