"""Model registry, persona loading, and the chat client (with a response cache).

A *model* is an endpoint plus a served model name (models.json). A *persona*
is a system prompt plus sampling settings for one role (personas/*.md). A
config assigns a model and a persona to each role, so either can be swapped
without touching the other.

Every request is sent at temperature 0, top_k 1 and a fixed seed unless the
persona says otherwise, and responses are cached by the exact request body.
Re-running a scenario under the second approval policy therefore costs GPU
time only where the lab state has diverged. The spec forbids relying on
bit-for-bit determinism in production (R57); the rig relies on it only to
avoid paying twice for an identical request, and `--no-cache` turns it off.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

RIG = Path(__file__).resolve().parent
CACHE = RIG / "cache"


# ------------------------------------------------------------------ personas


@dataclass
class Persona:
    name: str
    role: str                      # planner / reviewer / reporter
    prompt: str                    # system prompt, placeholders already filled
    style: str = "oneshot"         # planners only: oneshot / loop
    thinking: bool = False
    temperature: float = 0.0
    max_tokens: int = 0            # 0 = no cap
    max_steps: int = 12            # loop planners only
    description: str = ""
    sha256: str = ""


def load_persona(name: str, placeholders: Dict[str, str]) -> Persona:
    """personas/<name>.md: `---` frontmatter of `key: value` lines, then the prompt."""
    text = (RIG / "personas" / f"{name}.md").read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError(f"persona {name}: missing frontmatter")
    meta: Dict[str, Any] = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        k, _, v = line.partition(":")
        v = v.strip()
        try:
            meta[k.strip()] = json.loads(v)
        except ValueError:
            meta[k.strip()] = v
    prompt = m.group(2).strip() + "\n"
    for k, v in placeholders.items():
        prompt = prompt.replace("{" + k + "}", v)
    known = {f for f in Persona.__dataclass_fields__} - {"name", "prompt", "sha256"}
    unknown = set(meta) - known
    if unknown:
        raise ValueError(f"persona {name}: unknown frontmatter keys {sorted(unknown)}")
    return Persona(name=name, prompt=prompt, sha256=hashlib.sha256(text.encode()).hexdigest(), **meta)


# -------------------------------------------------------------------- models


@dataclass
class Model:
    key: str
    backend: str                   # openai (llama.cpp router, or any compatible server) / mock
    url: str = ""
    model: str = ""
    extra_body: Dict[str, Any] = field(default_factory=dict)
    api_key_env: str = ""          # for a hosted endpoint; the key never enters results
    behaviour: str = ""            # mock only
    timeout_s: int = 900
    notes: str = ""


def load_models() -> Dict[str, Model]:
    raw = json.loads((RIG / "models.json").read_text())
    return {k: Model(key=k, **{kk: vv for kk, vv in v.items() if not kk.startswith("_")})
            for k, v in raw.items() if not k.startswith("_")}


# -------------------------------------------------------------------- client


class ServerGone(Exception):
    """The endpoint is unreachable. The run stops so a resume can retry."""


@dataclass
class Reply:
    content: Optional[str]
    reasoning: str
    tool_calls: List[Dict[str, Any]]
    finish_reason: Optional[str]
    wall_s: float
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    server_s: Optional[float]      # prompt + generation time reported by the server
    cached: bool
    http_error: Optional[str] = None
    model_switch: bool = False     # a different model served the previous call

    def record(self) -> Dict[str, Any]:
        overhead = None
        if self.server_s is not None and not self.cached:
            overhead = round(max(0.0, self.wall_s - self.server_s), 2)
        # compute_s is what the deadline and model-seconds use: the server's own prompt +
        # generation time, so a model load (160 s cold from the spinning disk) is never
        # charged to the planner. The load shows up in load_overhead_s instead.
        compute = round(self.server_s, 2) if self.server_s is not None else round(self.wall_s, 2)
        return {"wall_s": round(self.wall_s, 2), "compute_s": compute, "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens, "finish_reason": self.finish_reason,
                "cached": self.cached, "http_error": self.http_error, "model_switch": self.model_switch,
                "load_overhead_s": overhead, "reasoning_chars": len(self.reasoning or "")}


class Client:
    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache
        # The model the server last actually ran. Cached replies never touch the server,
        # so they neither count as a switch nor change what is resident.
        self.last_model: Optional[str] = None

    def chat(self, model: Model, persona: Persona, messages: List[Dict[str, Any]],
             response_format: Optional[Dict[str, Any]] = None,
             tools: Optional[List[Dict[str, Any]]] = None) -> Reply:
        if model.backend == "mock":
            raise RuntimeError("mock models are answered by the role, not the client")
        body: Dict[str, Any] = {
            "model": model.model, "messages": messages,
            "temperature": persona.temperature, "top_k": 1, "seed": 42, "cache_prompt": False,
            "chat_template_kwargs": {"enable_thinking": persona.thinking},
        }
        if persona.max_tokens:
            body["max_tokens"] = persona.max_tokens
        if response_format:
            body["response_format"] = response_format
        if tools:
            body["tools"] = tools
        body.update(model.extra_body)

        switch = self.last_model is not None and self.last_model != model.key  # only if uncached
        key = hashlib.sha256(json.dumps({"url": model.url, "body": body}, sort_keys=True).encode()).hexdigest()
        path = CACHE / re.sub(r"[^A-Za-z0-9_.-]", "_", model.key) / f"{key}.json"
        if self.use_cache and path.exists():
            rec = json.loads(path.read_text())
            return _reply(rec["response"], rec["wall_s"], cached=True)

        headers = {"Content-Type": "application/json"}
        if model.api_key_env:
            headers["Authorization"] = "Bearer " + os.environ[model.api_key_env]
        req = urllib.request.Request(model.url, data=json.dumps(body).encode(), headers=headers)
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=model.timeout_s) as r:
                resp = json.loads(r.read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")[:600]
            self.last_model = model.key
            return Reply(None, "", [], None, time.monotonic() - t0, None, None, None, False,
                         http_error=f"{e.code}: {msg}", model_switch=switch)
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as e:
            raise ServerGone(f"{model.key} at {model.url}: {e}") from e
        wall = time.monotonic() - t0
        self.last_model = model.key
        if self.use_cache:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps({"wall_s": wall, "response": resp}))
            os.replace(tmp, path)
        reply = _reply(resp, wall, cached=False)
        reply.model_switch = switch
        return reply


def _reply(resp: Dict[str, Any], wall: float, cached: bool) -> Reply:
    choice = resp["choices"][0]
    msg = choice.get("message") or {}
    t = resp.get("timings") or {}
    u = resp.get("usage") or {}
    server = None
    if t.get("prompt_ms") is not None and t.get("predicted_ms") is not None:
        server = (t["prompt_ms"] + t["predicted_ms"]) / 1000
    return Reply(
        content=msg.get("content"), reasoning=msg.get("reasoning_content") or "",
        tool_calls=msg.get("tool_calls") or [], finish_reason=choice.get("finish_reason"),
        wall_s=wall, prompt_tokens=t.get("prompt_n", u.get("prompt_tokens")),
        completion_tokens=t.get("predicted_n", u.get("completion_tokens")),
        server_s=server, cached=cached)
