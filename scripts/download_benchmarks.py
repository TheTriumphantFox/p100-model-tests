#!/usr/bin/env python3
"""Download reusable local-generation benchmark inputs into ~/Projects/Tests.

Only evaluation/test material is downloaded; training splits are intentionally
omitted. Hugging Face snapshots are copied into this directory rather than
left only in the global cache.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from huggingface_hub import snapshot_download


BASE = Path.home() / "Projects" / "Tests"
DATASETS = BASE / "datasets"
TOOLS = BASE / "tools"


DOWNLOADS = [
    {
        "name": "HumanEval",
        "repo": "openai/openai_humaneval",
        "target": DATASETS / "humaneval",
        "patterns": ["README.md", "openai_humaneval/test-*.parquet"],
    },
    {
        "name": "MBPP",
        "repo": "google-research-datasets/mbpp",
        "target": DATASETS / "mbpp",
        "patterns": ["README.md", "full/test-*.parquet", "full/validation-*.parquet"],
    },
    {
        "name": "MMLU-Pro",
        "repo": "TIGER-Lab/MMLU-Pro",
        "target": DATASETS / "mmlu_pro",
        "patterns": ["README.md", "data/test-*.parquet", "data/validation-*.parquet"],
    },
    {
        "name": "AudioCaps test metadata",
        "repo": "d0rj/audiocaps",
        "target": DATASETS / "audiocaps",
        "patterns": ["README.md", "data/test-*.parquet"],
    },
    {
        "name": "Clotho test audio",
        "repo": "gijs/clotho",
        "target": DATASETS / "clotho",
        "patterns": ["README.md", "data/test-*.parquet"],
    },
]

GIT_REPOS = [
    {
        "name": "GenEval evaluator and prompts",
        "url": "https://github.com/djghosh13/geneval.git",
        "target": TOOLS / "geneval",
    },
    {
        "name": "T2I-CompBench evaluator and prompts",
        "url": "https://github.com/Karine-Huang/T2I-CompBench.git",
        "target": TOOLS / "t2i_compbench",
    },
]


def download_snapshot(item: dict[str, object]) -> None:
    target = Path(item["target"])
    target.mkdir(parents=True, exist_ok=True)
    print(f"\n==> {item['name']} ({item['repo']})", flush=True)
    snapshot_download(
        repo_id=str(item["repo"]),
        repo_type="dataset",
        local_dir=str(target),
        allow_patterns=list(item["patterns"]),
    )


def clone_repo(item: dict[str, str]) -> None:
    target = Path(item["target"])
    print(f"\n==> {item['name']} ({item['url']})", flush=True)
    if (target / ".git").exists():
        subprocess.run(["git", "-C", str(target), "pull", "--ff-only"], check=True)
        return
    if target.exists() and any(target.iterdir()):
        print(f"    Already exists; leaving it unchanged: {target}", flush=True)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--depth", "1", str(item["url"]), str(target)],
        check=True,
    )


def main() -> None:
    DATASETS.mkdir(parents=True, exist_ok=True)
    TOOLS.mkdir(parents=True, exist_ok=True)
    for item in DOWNLOADS:
        download_snapshot(item)
    for item in GIT_REPOS:
        clone_repo(item)
    print(f"\nAll benchmark inputs are under: {BASE}", flush=True)


if __name__ == "__main__":
    main()
