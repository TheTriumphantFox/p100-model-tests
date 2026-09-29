# Local LLM HumanEval benchmark

This runner evaluates every locally installed Ollama model on all 164 standard
OpenAI HumanEval test tasks.

## Method

- One deterministic generation per model and task (pass@1)
- Temperature 0, seed 42, thinking disabled
- 8,192-token context and 1,024-token output cap
- Dataset tests remain hidden from the models
- Generated Python executes in a bubblewrap sandbox with no network, a
  read-only runtime, resource limits, and a per-task timeout
- Models run sequentially and unload between models
- Results and reports are saved after every task
- Interrupted runs can resume without repeating completed tasks

With the current 10 Ollama tags, a full run is 1,640 generations.

## Active run

The full run started at 2026-09-06 09:42 EDT as the user service
`local-humaneval-benchmark.service`:

```text
runs/2026-09-06_09-42-24/
runs/2026-09-06_09-42-24.log
```

Its initial measured ETA was approximately 9–10 hours. Results are saved after
every task and can be resumed if the service is interrupted.

## Outputs

Each run contains `report.html`, pass@1 and speed SVG graphs, CSV and JSON
results, extracted solutions, and raw model responses. The adjacent `.log`
file records terminal progress.

## Run manually

```fish
cd ~/Projects/Tests/2026-09-06/local-llm-humaneval-benchmark
/home/hm/Projects/Tests/.venv/bin/python benchmark.py run
```

Resume an interrupted run:

```fish
/home/hm/Projects/Tests/.venv/bin/python benchmark.py run --resume runs/YYYY-MM-DD_HH-MM-SS/results.json
```

Rebuild a report without contacting Ollama:

```fish
/home/hm/Projects/Tests/.venv/bin/python benchmark.py report runs/YYYY-MM-DD_HH-MM-SS/results.json
```
