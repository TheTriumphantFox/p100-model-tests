#!/usr/bin/env python3
"""Second-pass combinations based on the winning no-MMVQ configuration."""

import benchmark as bench

bench.OUT = bench.OUT / "phase2"
base = {"GGML_VK_DISABLE_MMVQ": "1"}
bench.VARIANTS = [
    {"name": "no-mmvq-layer-50-50", "env": base, "args": ["--split-mode", "layer", "--tensor-split", "1,1"]},
    {"name": "no-mmvq-layer-45-55", "env": base, "args": ["--split-mode", "layer", "--tensor-split", "45,55"]},
    {"name": "no-mmvq-layer-55-45", "env": base, "args": ["--split-mode", "layer", "--tensor-split", "55,45"]},
    {"name": "no-mmvq-layer-60-40", "env": base, "args": ["--split-mode", "layer", "--tensor-split", "60,40"]},
    {"name": "no-mmvq-disable-fusion", "env": {**base, "GGML_VK_DISABLE_FUSION": "1"}, "args": ["--split-mode", "layer", "--tensor-split", "1,1"]},
    {"name": "no-mmvq-disable-async", "env": {**base, "GGML_VK_DISABLE_ASYNC": "1"}, "args": ["--split-mode", "layer", "--tensor-split", "1,1"]},
    {"name": "no-mmvq-disable-multi-add", "env": {**base, "GGML_VK_DISABLE_MULTI_ADD": "1"}, "args": ["--split-mode", "layer", "--tensor-split", "1,1"]},
    {"name": "no-mmvq-disable-graph-opt", "env": {**base, "GGML_VK_DISABLE_GRAPH_OPTIMIZE": "1"}, "args": ["--split-mode", "layer", "--tensor-split", "1,1"]},
    {"name": "no-mmvq-disable-int-dot", "env": {**base, "GGML_VK_DISABLE_INTEGER_DOT_PRODUCT": "1"}, "args": ["--split-mode", "layer", "--tensor-split", "1,1"]},
    {"name": "no-mmvq-transfer-queue", "env": {**base, "GGML_VK_ASYNC_USE_TRANSFER_QUEUE": "1"}, "args": ["--split-mode", "layer", "--tensor-split", "1,1"]},
    {"name": "no-mmvq-serialize", "env": {**base, "GGML_VK_SERIALIZE_SUBMISSIONS": "1"}, "args": ["--split-mode", "layer", "--tensor-split", "1,1"]},
]

bench.main()
