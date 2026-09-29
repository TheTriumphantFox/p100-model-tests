#!/usr/bin/env python3
"""Export every model ever tested on this box as one JSON record, for the HTML sheet.

Includes models deleted after earlier rounds and models that cannot load, so the sheet
doubles as a record of what has already been tried.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Reuse make_final.py's data layer without running its presentation half. exec'ing the
# source needs __file__ injected, since the module computes its own paths from it.
src = (HERE / "make_final.py").read_text()
src = src[:src.index("# ------")]
ns = {"__file__": str(HERE / "make_final.py"), "__name__": "mf_data"}
exec(compile(src, "make_final.py", "exec"), ns)

cells = ns["collect"]()
lad = ns["ladders"]()
pair, REF = ns["pair"], ns["REF"]

# provenance: quantizer / origin / where the file lives / what it is
META = {
 "qwen3.6-27b-abliterated:q5_k_m": dict(full="Qwen3.6-27B-Uncensored-HauhauCS-Aggressive Q5_K_M", quant="Q5_K_M", origin="HauhauCS (abliterated)", arch="qwen35", status="shelf", role="INCUMBENT — the model to beat"),
 "qwen3.6-27b-opus-distill:q4_k_m": dict(full="Qwen3.6-27B Opus-Distill Q4_K_M", quant="Q4_K_M", origin="Claude/GLM/Kimi distill datasets", arch="qwen35 + vision", status="unrunnable", role="claims 75.7 reasoning — unverifiable here"),
 "qwen3.6-35b-a3b-abliterated-vl:q4_k_m": dict(full="Qwen3.6-35B-A3B-Abliterated-VL Q4_K_M", quant="Q4_K_M", origin="abliterated, vision-language", arch="qwen35moe + vision", status="unrunnable", role="vision + the qwen worker"),
 "qwen3.8-27b-stock:q4_k_m": dict(full="Qwen3.8-27B (stock) Q4_K_M", quant="Q4_K_M", origin="stock, unmodified", arch="qwen35", status="shelf", role="the only unmodified Qwen3.8"),
 "qwen3.8-27b-unsloth:q8_0": dict(full="Qwen3.8-27B Q8_0 — Unsloth", quant="Q8_0", origin="Unsloth", arch="qwen35", status="shelf", role="best coding score measured"),
 "qwen3.8-27b-unsloth:ud_q6_k": dict(full="Qwen3.8-27B UD-Q6_K — Unsloth", quant="UD-Q6_K", origin="Unsloth (dynamic)", arch="qwen35", status="deleted", role="dominated by the Unsloth Q8_0 on both axes"),
 "qwen3.8-27b-uncensored-hauhaucs:q6_k_p": dict(full="Qwen3.8-27B-Uncensored-HauhauCS-Aggressive Q6_K_P", quant="Q6_K_P", origin="HauhauCS (uncensored)", arch="qwen35", status="shelf", role="the uncensored Qwen3.8"),
 "qwen3.8-27b-ggmlorg:q8_0": dict(full="Qwen3.8-27B Q8_0 — ggml-org", quant="Q8_0", origin="ggml-org", arch="qwen35", status="shelf", role="has matching DFlash/MTP drafters: 22.7 tok/s"),
 "gpt-oss-20b:q8_0": dict(full="GPT-OSS-20B Q8_0", quant="Q8_0 (MXFP4 experts)", origin="stock", arch="gpt-oss", status="shelf", role="fastest useful model; reasons unconditionally"),
 "gemma4-e4b-abliterated:q4_k_m": dict(full="Gemma4-E4B-Abliterated Q4_K_M", quant="Q4_K_M", origin="abliterated", arch="gemma4 (E4B)", status="unrunnable", role="only audio-in model on the shelf"),
 "devstral-patched:latest": dict(full="Devstral-Small-2 24B Instruct 2512 Q8_0 (patched)", quant="Q8_0", origin="patched local build — tool-calling fix for agentic clients", arch="mistral3", status="production", role="live on :8080; measured 2026-09-21 — no thinking mode"),
 "ornith-1.5-35b-a3b:q4_k_m": dict(full="Ornith-1.5-35B-A3B Q4_K_M", quant="Q4_K_M", origin="stock", arch="qwen35moe", status="shelf", role="closest MoE candidate; 4.8x speed"),
 "g9v3-39a5b:q4_k_m": dict(full="G9v3-39A5B Q4_K_M", quant="Q4_K_M", origin="stock", arch="g9v3 (fork runtime)", status="shelf", role="cheapest context measured"),
 "nemotron-cascade-2-30b-a3b:q4_k_m": dict(full="Nemotron-Cascade-2-30B-A3B Q4_K_M", quant="Q4_K_M", origin="stock", arch="nemotron_h_moe", status="deleted", role="fastest measured, but strictly dominated"),
 "xing4.0-29b-a4b:iq4_nl": dict(full="Xing4.0-29B-A4B IQ4_NL", quant="IQ4_NL", origin="stock (only quant published)", arch="xing4_0 (fork runtime)", status="deleted", role="worst measured; never terminates thinking"),
 "glm-4.7-flash:q5_k_m": dict(full="GLM-4.7-Flash Q5_K_M", quant="Q5_K_M", origin="stock", arch="glm4", status="deleted", role="lost both axes decisively"),
}
SIZES = {
 "qwen3.6-27b-abliterated:q5_k_m": 20.8, "qwen3.6-27b-opus-distill:q4_k_m": 17.5,
 "qwen3.6-35b-a3b-abliterated-vl:q4_k_m": 22.1, "qwen3.8-27b-stock:q4_k_m": 16.8,
 "qwen3.8-27b-unsloth:q8_0": 29.0, "qwen3.8-27b-unsloth:ud_q6_k": 22.0,
 "qwen3.8-27b-uncensored-hauhaucs:q6_k_p": 25.9, "qwen3.8-27b-ggmlorg:q8_0": 28.6,
 "gpt-oss-20b:q8_0": 12.1, "gemma4-e4b-abliterated:q4_k_m": 6.3,
 "devstral-patched:latest": 25.1, "ornith-1.5-35b-a3b:q4_k_m": 21.7,
 "g9v3-39a5b:q4_k_m": 23.6, "nemotron-cascade-2-30b-a3b:q4_k_m": 24.7,
 "xing4.0-29b-a4b:iq4_nl": 20.1, "glm-4.7-flash:q5_k_m": 21.4,
}
LAD_KEY = {"qwen3.6-27b-abliterated:q5_k_m": "incumbent", "qwen3.8-27b-ggmlorg:q8_0": "ggmlorg-q8",
           "qwen3.8-27b-unsloth:q8_0": "unsloth-q8", "g9v3-39a5b:q4_k_m": "g9v3",
           "qwen3.8-27b-uncensored-hauhaucs:q6_k_p": "uncensored-q6kp"}

out = []
for tag, m in META.items():
    c = cells.get(tag, {})
    rec = dict(tag=tag, size_gb=SIZES.get(tag), **m)
    for k, key in (("off", "reason_quick"), ("on", "reason_think"), ("he", "coding")):
        r = c.get(k)
        # A model with no thinking mode produces a complete thinking-on results.json whose
        # answers are its thinking-off answers. Emitting that number under "reasoning --
        # thinking" would report a run that did not happen, so the score is withheld and the
        # reason is carried instead. See mark_nothink() in make_final.py.
        if r is not None and r.get("nothink"):
            rec[key] = None
            rec[key + "_floor"] = 0
            rec[key + "_tok"] = r["tok"]
            rec[key + "_nothink"] = True
        elif r is None or r["dead"]:
            rec[key] = None
            rec[key + "_floor"] = 0
            rec[key + "_tok"] = None
        else:
            rec[key] = round(r["acc"], 2)
            rec[key + "_floor"] = r["cap"]
            rec[key + "_tok"] = r["tok"]
            ref = cells.get(REF, {}).get(k)
            if ref and tag != REF:
                got = pair(r, ref)
                if got:
                    rec[key + "_p"] = round(got[2], 4)
                    rec[key + "_disc"] = f"{got[1]}/{got[0]}"
    rec["tput"] = c.get("tput")
    lk = LAD_KEY.get(tag)
    if lk and lk in lad:
        rec["kv_kib"] = round(lad[lk]["kv"], 1) if lad[lk]["kv"] else None
        rec["ctx_max"] = lad[lk]["top"]
        rec["vram_spare"] = 32768 - lad[lk]["vram_top"]
    out.append(rec)

repro = [dict(arm=k, label=l, runs=n, tok_lo=lo, tok_hi=hi, scores=a,
              spread=round(sp, 2), identical=i) for k, l, n, lo, hi, a, sp, i in ns["repro"]()]
print(json.dumps(dict(models=out, repro=repro,
                      generated=__import__("time").strftime("%Y-%m-%d %H:%M")), indent=1))
