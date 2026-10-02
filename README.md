# P100 model tests

Which local LLM is the best all-around model on two Tesla P100-PCIE-16GB cards (32 GB VRAM,
llama.cpp CUDA 12.6 sm_60 build)? Accuracy, editing, tool use, speed and tuning, plus the AIOS
planner tests, September–October 2026. Unless a test says otherwise, it is judged on
all-around usefulness.

**Browse the results:** https://thetriumphantfox.github.io/p100-model-tests/

## Layout

| Path | What |
|---|---|
| `index.html` | The results page (GitHub Pages). |
| `results/YYYY-MM-DD/<subject>/` | One folder per test: write-up (`REPORT.md`, `RESULTS.md` or `FINAL.md`), per-run JSON, drivers and logs. |
| `results/WORKSPACE-README.md` | The original workspace index, with notes on every run. |
| `rig/` | The full-stack planner / reviewer / reporter rig. |
| `scripts/` | Reusable benchmark scripts, the HBM bandwidth kernel, and the CUDA 12.6 sm_60 llama.cpp build script. |
| `dataset_manifest.json` | Sources and licences of the benchmark datasets. |

## Not included

- **Model weights** (GGUF, 2–82 GB each). They are too big for Git. The results page has the full inventory.
- **Datasets.** Download them with `scripts/download_benchmarks.py`; sources are in `dataset_manifest.json`.
- **Most generated images** from the 2 September RealVisXL run (2,953 PNGs, 1.1 GB). Their CLIP
  scores and manifests are kept, and a best/worst sample per category is in `site/gallery/`.

The 1–6 September runs predate the P100s. Their speed figures are not comparable with the later ones.

Dataset content (HumanEval, MMLU-Pro, tau-bench, GenEval, T2I-CompBench) remains under its upstream licences.
