#!/usr/bin/env python3
"""Check that global P100 Vulkan flags do not regress the current Qwen worker."""

import benchmark_ollama as bench

bench.OUT = bench.OUT.parent / "regression-qwen36-a3b"
bench.MODEL = "qwen3.6-35b-a3b-abliterated-vl:q4_k_m"
bench.VARIANTS = [
    ("baseline", {}),
    ("p100-flags", {"GGML_VK_DISABLE_MMVQ": "1", "GGML_VK_DISABLE_INTEGER_DOT_PRODUCT": "1"}),
]
bench.main()
