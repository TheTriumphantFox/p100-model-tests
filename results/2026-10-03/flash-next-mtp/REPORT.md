# Flash-Next IQ2_XXS + MTP — 2026-10-03 morning

**MTP works on this box, but only gated, and gains about 11%: 18.6 → 20.7 tok/s at n-max 3,
p-min 0.75, with 91.6% acceptance.** Ungated drafting (no p-min) is *slower* than no drafting.
With the experts in system RAM, every rejected draft token costs an extra pass over experts
read from RAM. The 1.3–1.7× published elsewhere comes from setups whose experts sit in fast
memory.

## How it runs

- **Runtime**: PR [ggml-org/llama.cpp#27836](https://github.com/ggml-org/llama.cpp/pull/27836)
  (`rmonsurate:qwen4exp-mtp` @ `1d8de7c`), built into `~/llama-cuda12-mtp` with
  `scripts/build_llama_cuda12.sh` (`OUT`/`REPO`/`REF`). Production `~/llama-cuda12` is untouched.
- **The PR does not load detached heads.** Given `-md`, it parses the head as a full qwen4exp
  model. ggml-org's `mtp-*-Q4_0.gguf` fails on `output_hc_norm`; adding those 3 tensors then
  fails on `blk.0.*`. unsloth's "shared" head fails on `token_embd`. The PR expects the head
  as a trailing block in the main GGUF.
- **`append_mtp.py`** builds that layout. It rewrites shard 1 only, copying every trunk KV
  and tensor byte-for-byte and appending ggml-org's `blk.48.*` (32 tensors, 1.47 GB, Q4_0).
  Changed keys: block_count 48→49, nextn_predict_layers=1, compress_ratios +[0]. It runs in
  45 s. Shard 2 is a hard link, so it costs no extra space.
  Result: `~/models/qwen3.8-flash-next_iq2_xxs-mtp/` (shard 1 41.5 GB; shard 2 shared with the
  original).
- Serve: `~/llama-cuda12-mtp/bin/llama-server -m …-MTP-00001-of-00002.gguf --spec-type draft-mtp
  --spec-draft-n-max 3 --spec-draft-p-min 0.75 -fa on --jinja` (`--fit` left on).
- **The MTP file needs the PR build.** The :8080 router (stock build) and pi still use the
  original IQ2.

## Numbers (`spec_ab.sh`, 6 distinct prompts × 400 tokens, temp 0, ctx 8192)

| config | tok/s mean (min–max) | acceptance |
|---|---:|---:|
| warm, no drafting (before / after) | 18.52 / 18.67 | — |
| n-max 2, p-min 0.75 | 19.91 (18.3–20.8) | 91.6% |
| **n-max 3, p-min 0.75** | **20.70** (19.0–23.5) | 91.6% |
| n-max 1 / 2 / 3, no p-min (cold, first pass) | 16.0 / 15.8 / 17.3 | 86 / 80 / 76% |
| original IQ2 file, PR build, no drafting | 19.05 | — |

- The first pass (`ab2.out`) ran on a cold page cache for the new 41 GB shard and drifted
  upward over the run (its own baseline was 17.6). The warm pass (`ab3.out`) brackets the MTP
  configs between two baselines, which agree within 0.15 tok/s.
- Without p-min, n-max 1–3 are 2–14% *below* their baseline even allowing for that drift.
  Drafts the verifier rejects are expensive when the experts are in RAM.
- Not measured: p-min other than 0.75, n-max 4, quality (temp-0 MTP output should be
  identical to non-MTP; the PR author reports byte-identical output), long-context decode.

## Files

`append_mtp.py`, `patch_head.py` (the detached-head attempt, kept for the record), `ab.sh` /
`ab-detached-FAILED.out`, `ab2.sh` / `ab2.out`, `ab3.sh` / `ab3.out`, per-config `*.json`
and `*.log`, `build.log`. Heads: `~/models/flash-next-mtp-heads/` (ggml-org Q4_0, unsloth
shared Q4_K_M, the patched copy; all SHA-256 verified against HF).
