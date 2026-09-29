#!/usr/bin/env python3
"""Speak Ollama's API, forward to a llama.cpp router.

Why: the HumanEval / MMLU-Pro / coding harnesses are written against Ollama
(`/api/tags`, `/api/chat`, `/api/generate`). Re-pointing them at llama-server
would mean forking three scripts and would put the CUDA numbers on a different
code path from the Vulkan baseline they are being compared against. This shim
instead lets all three run UNMODIFIED against the CUDA build, so the only thing
that changes between the two runs is the backend.

    ollama_shim.py --router http://127.0.0.1:8081 --port 11500
    ... then run a harness with --base-url http://127.0.0.1:11500

Model names are reported as the original ollama tags (see TAGS) so reports line
up one-for-one with the Vulkan run.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# router model id  ->  the ollama tag the Vulkan baseline used
TAGS = {
    "qwen3.6-27b-abliterated_q5_k_m": "qwen3.6-27b-abliterated:q5_k_m",
    "qwen3.6-27b-opus-distill_q4_k_m": "qwen3.6-27b-opus-distill:q4_k_m",
    "qwen3.8-27b-stock_q4_k_m": "qwen3.8-27b-stock:q4_k_m",
    "qwen3.6-35b-a3b-abliterated-vl_q4_k_m": "qwen3.6-35b-a3b-abliterated-vl:q4_k_m",
    "gemma4-e4b-abliterated_q4_k_m": "gemma4-e4b-abliterated:q4_k_m",
    "devstral-patched_q8_0": "devstral-patched:latest",
    # candidates evaluated 2026-09-19 against qwen3.6-27b-abliterated:q5_k_m
    "gpt-oss-20b_q8_0": "gpt-oss-20b:q8_0",
    # candidates evaluated 2026-09-19 round 2 (newer models, same brief)
    # glm-4.7-flash, nemotron-cascade-2, xing4.0 and qwen3.8-unsloth:ud_q6_k were
    # deleted 2026-09-21 -- all lost decisively; see candidates-round2/SHELF-REVIEW.md
    "ornith-1.5-35b-a3b_q4_k_m": "ornith-1.5-35b-a3b:q4_k_m",
    "g9v3-39a5b_q4_k_m": "g9v3-39a5b:q4_k_m",
    # round 2b, 2026-09-20: three Qwen3.8-27B quants supplied in ~/Downloads/Models
    "qwen3.8-27b-unsloth_q8_0": "qwen3.8-27b-unsloth:q8_0",
    "qwen3.8-27b-uncensored-hauhaucs_q6_k_p": "qwen3.8-27b-uncensored-hauhaucs:q6_k_p",
    # 2026-09-21 CUDA matrix: the ggml-org Qwen3.8-27B Q8_0, the file that has the
    # published dflash/mtp drafters beside it (22.72 tok/s measured) but was never scored.
    "qwen3.8-27b-ggmlorg_q8_0": "qwen3.8-27b-ggmlorg:q8_0",
}
REVERSE = {v: k for k, v in TAGS.items()}

# general.file_type is LLAMA_FTYPE, NOT the ggml tensor-type enum. Using the
# latter silently mislabels every K-quant (q5_k_m reads as IQ2_XS).
GGUF_TYPES = {0: "F32", 1: "F16", 2: "Q4_0", 3: "Q4_1", 7: "Q8_0", 8: "Q5_0", 9: "Q5_1",
              10: "Q2_K", 11: "Q3_K_S", 12: "Q3_K_M", 13: "Q3_K_L", 14: "Q4_K_S",
              15: "Q4_K_M", 16: "Q5_K_S", 17: "Q5_K_M", 18: "Q6_K", 19: "IQ2_XXS",
              20: "IQ2_XS", 21: "Q2_K_S", 22: "IQ3_XS", 23: "IQ3_XXS", 24: "IQ1_S",
              25: "IQ4_NL", 26: "IQ3_S", 27: "IQ3_M", 28: "IQ2_S", 29: "IQ2_M",
              30: "IQ4_XS", 31: "IQ1_M", 32: "BF16", 33: "TQ1_0", 34: "TQ2_0"}


def gguf_header(path: Path) -> dict:
    """Minimal GGUF metadata read: enough for the report's model card."""
    out: dict = {}
    try:
        with open(path, "rb") as f:
            if f.read(4) != b"GGUF":
                return out
            _ver, _n_tensors, n_kv = struct.unpack("<IQQ", f.read(20))

            def rd_str() -> str:
                (ln,) = struct.unpack("<Q", f.read(8))
                return f.read(ln).decode("utf-8", "replace")

            def skip_val(t: int) -> object:
                sizes = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 1, 10: 8, 11: 8, 12: 8}
                if t == 8:
                    return rd_str()
                if t == 9:
                    (et,) = struct.unpack("<I", f.read(4))
                    (ln,) = struct.unpack("<Q", f.read(8))
                    for _ in range(ln):
                        skip_val(et)
                    return None
                raw = f.read(sizes.get(t, 4))
                fmt = {0: "<b", 1: "<B", 2: "<h", 3: "<H", 4: "<i", 5: "<I",
                       6: "<f", 7: "<?", 10: "<q", 11: "<Q", 12: "<d"}.get(t)
                return struct.unpack(fmt, raw)[0] if fmt else None

            for _ in range(n_kv):
                key = rd_str()
                (vt,) = struct.unpack("<I", f.read(4))
                val = skip_val(vt)
                if key in ("general.name", "general.architecture", "general.size_label",
                           "general.basename", "general.file_type"):
                    out[key] = val
    except Exception:
        pass
    return out


class Shim(BaseHTTPRequestHandler):
    router = "http://127.0.0.1:8081"
    models_dir = Path("/home/hm/llama-bench-models")
    verbose = False
    force_think = False
    omit_effort = False
    _meta_cache: dict = {}
    _lock = threading.Lock()

    def log_message(self, *a):  # quiet unless asked
        if Shim.verbose:
            super().log_message(*a)

    # ---- plumbing -------------------------------------------------------
    def _send(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _router(self, path, payload=None, timeout=3600):
        url = Shim.router.rstrip("/") + path
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(
            url, data, {"Content-Type": "application/json"},
            method="POST" if data else "GET")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)

    def _read_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    # ---- model metadata -------------------------------------------------
    def _meta(self, rid: str) -> dict:
        with Shim._lock:
            if rid in Shim._meta_cache:
                return Shim._meta_cache[rid]
        p = Shim.models_dir / f"{rid}.gguf"
        real = p.resolve() if p.exists() else None
        size = real.stat().st_size if real else 0
        hdr = gguf_header(real) if real else {}
        ft = hdr.get("general.file_type")
        quant = GGUF_TYPES.get(ft if isinstance(ft, int) else -1, "unknown")
        name = TAGS.get(rid, rid)
        # size_label like "27B" / "512x56B" -> parameter_size
        psize = str(hdr.get("general.size_label") or "")
        meta = {
            "name": name, "model": name,
            "digest": (real.name.replace("sha256-", "") if real else ""),
            "size": size,
            "details": {
                "parent_model": "", "format": "gguf",
                "family": str(hdr.get("general.architecture") or ""),
                "families": [str(hdr.get("general.architecture") or "")],
                "parameter_size": psize,
                "quantization_level": quant,
            },
            "modified_at": "2026-09-19T00:00:00Z",
        }
        with Shim._lock:
            Shim._meta_cache[rid] = meta
        return meta

    def _router_ids(self):
        try:
            data = self._router("/models")["data"]
        except Exception:
            return []
        return [m["id"] for m in data]

    # ---- routes ---------------------------------------------------------
    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/api/tags", "/api/ps"):
            ids = [i for i in self._router_ids() if i in TAGS]
            return self._send({"models": [self._meta(i) for i in ids]})
        if path == "/api/version":
            return self._send({"version": "shim-llamacpp"})
        return self._send({"error": "not found"}, 404)

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            body = self._read_body()
        except Exception as e:
            return self._send({"error": str(e)}, 400)

        if path == "/api/show":
            rid = REVERSE.get(body.get("model") or body.get("name"), "")
            m = self._meta(rid)
            return self._send({"details": m["details"], "model_info": {}})

        if path == "/api/generate":
            # harnesses use this only to unload (keep_alive 0) or to warm up
            if body.get("keep_alive") in (0, "0", "0s"):
                rid = REVERSE.get(body.get("model"), body.get("model"))
                try:
                    self._router(f"/models/{rid}/unload", {})
                except Exception:
                    pass
                return self._send({"model": body.get("model"), "response": "", "done": True})
            body = {**body, "messages": [{"role": "user", "content": body.get("prompt") or ""}]}
            path = "/api/chat"

        if path == "/api/chat":
            return self._chat(body)

        return self._send({"error": "not found"}, 404)

    def _chat(self, body):
        tag = body.get("model", "")
        rid = REVERSE.get(tag, tag)
        opts = body.get("options") or {}
        req = {
            "model": rid,
            "messages": body.get("messages") or [],
            "stream": False,
        }
        if "num_predict" in opts:
            req["max_tokens"] = opts["num_predict"]
        if "temperature" in opts:
            req["temperature"] = opts["temperature"]
        if "seed" in opts:
            req["seed"] = opts["seed"]
        if "top_p" in opts:
            req["top_p"] = opts["top_p"]
        # Ollama's think:false -> Qwen/Jinja template switch + hard reasoning budget.
        # Both are needed: the kwarg drives the template, the budget stops a model
        # that ignores it. The Vulkan baseline ran with thinking disabled.
        if Shim.force_think:
            # --force-think: the harnesses hard-code "think": False, which scored every
            # reasoning model in round 2 with its chain of thought switched off (the tell
            # was MMLU-Pro @96 and @2048 landing on the same hundredth). This flag ignores
            # that field and turns thinking ON instead. It exists ONLY for the separate
            # thinking-on column; the default (flag absent) path below is unchanged, and is
            # the only one comparable to the thinking-disabled shelf baselines.
            req["chat_template_kwargs"] = {"enable_thinking": True}
            # Deliberately do NOT set reasoning_effort. It is not portable: the Qwen3.8
            # family's template VALIDATES it against ('xhigh','medium','low') and raises a
            # Jinja exception -> router 500 -> the harness records 0.0% in 94 seconds. The
            # value "high" is not in that set. Meanwhile ornith/nemotron/xing/g9v3 and the
            # qwen3.6 incumbent do not reference reasoning_effort in their templates at all,
            # so it was a no-op for every run that succeeded. Omitting it therefore changes
            # nothing for those five and lets each model use its own default thinking depth
            # (xhigh for Qwen3.8) -- which is what the other five were already doing.
        elif body.get("think") is False:
            req["chat_template_kwargs"] = {"enable_thinking": False}
            req["reasoning_budget"] = 0
            # gpt-oss reasons unconditionally (harmony format) -- enable_thinking
            # and reasoning_budget do not switch it off. The nearest equivalent is
            # the lowest reasoning effort. Without this it burns the whole token
            # budget on analysis and never emits its answer channel: MMLU-Pro at
            # num_predict 96 parsed 0/70. Harmless for models that ignore it.
            if not Shim.omit_effort:
                req["reasoning_effort"] = "low"

        t0 = time.time()
        try:
            r = self._router("/v1/chat/completions", req, timeout=3600)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:400]
            return self._send({"error": f"router {e.code}: {detail}"}, 502)
        except Exception as e:
            return self._send({"error": f"router: {e!r}"}, 502)
        wall_ns = int((time.time() - t0) * 1e9)

        choice = (r.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        content = msg.get("content") or ""
        # llama.cpp splits a reasoning model's analysis channel into
        # reasoning_content and leaves `content` as the clean answer. ollama with
        # think:false returns only the answer, so return only `content` to match.
        # Prepending reasoning_content (an earlier version of this shim did)
        # corrupts code extraction badly for models whose reasoning is intrinsic,
        # e.g. gpt-oss's harmony format. Use it ONLY as a fallback when the model
        # returned nothing else, so a request never comes back empty.
        if not content.strip() and msg.get("reasoning_content"):
            content = msg["reasoning_content"]

        t = r.get("timings") or {}
        usage = r.get("usage") or {}
        pn = int(t.get("prompt_n") or usage.get("prompt_tokens") or 0)
        en = int(t.get("predicted_n") or usage.get("completion_tokens") or 0)
        pms = float(t.get("prompt_ms") or 0.0)
        ems = float(t.get("predicted_ms") or 0.0)

        return self._send({
            "model": tag,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "message": {"role": "assistant", "content": content},
            "done": True,
            "done_reason": choice.get("finish_reason") or "stop",
            "total_duration": wall_ns,
            "load_duration": max(0, wall_ns - int((pms + ems) * 1e6)),
            "prompt_eval_count": pn,
            "prompt_eval_duration": int(pms * 1e6),
            "eval_count": en,
            "eval_duration": int(ems * 1e6),
        })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--router", default="http://127.0.0.1:8081")
    ap.add_argument("--models-dir", default="/home/hm/llama-bench-models")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=11500)
    ap.add_argument("--verbose", action="store_true")
    # --omit-effort exists for one experiment: gpt-oss-20b scored 77.14% on 2026-09-19 and
    # 71.43% on 2026-09-21 at otherwise identical settings, generating 7170 vs 5348 tokens.
    # Two explanations fit -- run-to-run nondeterminism, or the reasoning_effort:"low" below
    # having been added between the runs. Serving one shim without it discriminates them.
    ap.add_argument("--omit-effort", action="store_true",
                    help="thinking-off path: do not send reasoning_effort at all")
    ap.add_argument("--force-think", action="store_true",
                    help="ignore the harness's think:False and enable thinking instead "
                         "(separate thinking-on column only -- never the baseline)")
    a = ap.parse_args()
    Shim.router = a.router
    Shim.models_dir = Path(a.models_dir)
    Shim.verbose = a.verbose
    Shim.force_think = a.force_think
    Shim.omit_effort = a.omit_effort
    srv = ThreadingHTTPServer((a.host, a.port), Shim)
    mode = "THINKING FORCED ON" if a.force_think else "thinking as requested by caller"
    print(f"shim: ollama API on http://{a.host}:{a.port} -> router {a.router} [{mode}]", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
