# Local LLM benchmark — 2026-09-01

Historical Ollama performance benchmark artifacts. The full run tested 12
installed model tags against 12 prompts with five iterations per pair (720
requests), then removed one worst run per model/test group.

- `benchmark_results_full_20260901_220432.json` — complete report
- `graphs/index.html` — generated comparison graphs
- `benchmark_results_20260901_215121.json` — earlier failed attempt, retained
- `benchmark_smoke.json` — one-request smoke report, retained
- `llm_benchmark_full_20260901_220432.log` — full run log

The reusable runner is `../../scripts/llm_benchmark.py`. A dated copy is retained
as `../../scripts/llm_benchmark_2026-09-01.py` for historical reference.
