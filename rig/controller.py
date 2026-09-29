"""The deterministic half of the stack: lab, handles, grammar, validation, checks, commit.

Nothing in this module calls a model. It is a simplified stand-in for the AIOS
controller (spec v8 sections 2-4): the same plan grammar, the same strict
validation order, the same target-kind check policy, and a lab that only
changes through `Lab.commit`. It leaves out everything v8 needs for real
security (sandboxing, grants, audit, recovery), because the rig measures how
models behave in the flow, not whether the containment holds.

Adapted from 2026-09-23/planner-bench/bench.py, with three deliberate changes:
schema_version is 8, file content reaches the planner exactly (the benchmark
stripped the final newline, R60), and the grammar can pin the target handle
as well as the check sequence (R57).
"""
from __future__ import annotations

import copy
import difflib
import hashlib
import json
import re
from typing import Any, Dict, List, Optional, Tuple

SCHEMA_VERSION = 8
WRITE_LIMIT = 16 * 1024          # section 3: writable payload
RESPONSE_LIMIT = 256 * 1024      # R59
MAX_DEPTH = 32
MAX_CALLS = 8

# Deployed target-kind policy (R25, R70). Order is significant.
KIND_PROFILES: Dict[str, List[str]] = {
    "service_config": ["json_object", "port_range"],
    "activation_state": ["activation_state_schema"],
}
PROFILES = sorted({p for seq in KIND_PROFILES.values() for p in seq})

CROCKFORD = "0123456789abcdefghjkmnpqrstvwxyz"
HANDLE_RE = re.compile(r"^h[0-9a-hjkmnp-tv-z]{26}$")
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def content_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def dumps(obj: Any) -> str:
    """Canonical file form: every fixture and every expected result uses it."""
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def derive_handle(*parts: str) -> str:
    """Deterministic per-transaction handle IDs, so identical requests hit the response cache."""
    digest = hashlib.sha256("\x1f".join(parts).encode()).digest()
    return "h" + "".join(CROCKFORD[b % 32] for b in digest[:26])


# ------------------------------------------------------------------------ lab


class Lab:
    """The managed lab: path -> {kind, label, content}. Only `commit` changes it."""

    def __init__(self, files: Dict[str, Dict[str, Any]]):
        self.files = copy.deepcopy(files)

    def copy(self) -> "Lab":
        return Lab(self.files)

    def content(self, path: str) -> str:
        return self.files[path]["content"]

    def hash(self, path: str) -> str:
        return content_hash(self.content(path))

    def commit(self, path: str, content: str) -> str:
        self.files[path]["content"] = content
        return self.hash(path)

    def snapshot(self) -> Dict[str, str]:
        return {p: f["content"] for p, f in self.files.items()}


def register(lab: Lab, select: Dict[str, str], scenario_id: str, txn_index: int) -> List[Dict[str, Any]]:
    """Controller-side selection (section 4): fresh handles for this transaction.

    `select` maps lab path -> "write" or "context". A file selected as context
    is registered with kind "context" whatever its kind in the lab, so it can
    never be a write target.
    """
    handles = []
    for path, use in select.items():
        f = lab.files[path]
        kind = f["kind"] if use == "write" else "context"
        hid = f.get("handle_id") or derive_handle(scenario_id, str(txn_index), path)
        handles.append({"handle_id": hid, "path": path, "kind": kind, "label": f["label"],
                        "content": f["content"]})
    return handles


def projection(handles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """R69 metadata, plus whether the file ends with LF (the benchmark hid this)."""
    return [{
        "handle_id": h["handle_id"],
        "kind": h["kind"],
        "controller_assigned_label": h["label"],
        "size_bytes": len(h["content"].encode("utf-8")),
        "content_hash": content_hash(h["content"]),
        "ends_with_newline": h["content"].endswith("\n"),
    } for h in handles]


def policy_text() -> str:
    lines = [f"- {kind}: " + ", then ".join(seq) for kind, seq in KIND_PROFILES.items()]
    lines.append("- context: never a write target; no checks")
    return "\n".join(lines)


def render_handles(handles: List[Dict[str, Any]], with_content: bool = True) -> str:
    parts = ["Handles:", json.dumps(projection(handles), indent=2)]
    if with_content:
        parts += ["", "Authorized content (exact bytes between the markers; see ends_with_newline):"]
        for h in handles:
            parts.append(f"----- BEGIN CONTENT {h['handle_id']} ({h['label']}) -----")
            parts.append(h["content"][:-1] if h["content"].endswith("\n") else h["content"])
            parts.append(f"----- END CONTENT {h['handle_id']} -----")
    return "\n".join(parts)


# ------------------------------------------------------------------- grammar


def _write_obj(handle_const: Optional[str] = None) -> Dict[str, Any]:
    fh = {"const": handle_const} if handle_const else {"type": "string", "pattern": HANDLE_RE.pattern}
    return {
        "type": "object", "additionalProperties": False,
        "required": ["op", "file_handle", "expected_old_hash", "content"],
        "properties": {
            "op": {"const": "write_lab_file"},
            "file_handle": fh,
            "expected_old_hash": {"type": "string", "pattern": HASH_RE.pattern},
            "content": {"type": "string"},
        },
    }


def _check_obj(profile: Optional[str] = None) -> Dict[str, Any]:
    return {
        "type": "object", "additionalProperties": False, "required": ["op", "check_profile"],
        "properties": {"op": {"const": "run_check"},
                       "check_profile": {"const": profile} if profile else {"enum": PROFILES}},
    }


def response_schema(handles: List[Dict[str, Any]], pin: bool) -> Dict[str, Any]:
    """R57. pin=True: one oneOf branch per writable handle, with the handle and its
    kind's check sequence as constants (prefixItems only; llama.cpp lets `items`
    override `prefixItems`). expected_old_hash is never pinned. pin=False is the
    structure-only grammar the planner benchmark started with."""
    if pin:
        branches = []
        for h in handles:
            if h["kind"] == "context":
                continue
            seq = KIND_PROFILES[h["kind"]]
            n = 1 + len(seq)
            branches.append({"type": "array", "prefixItems": [_write_obj(h["handle_id"])] + [_check_obj(p) for p in seq],
                             "minItems": n, "maxItems": n})
        calls = branches[0] if len(branches) == 1 else {"oneOf": branches}
    else:
        calls = {"type": "array", "minItems": 2, "maxItems": MAX_CALLS,
                 "items": {"anyOf": [_write_obj(), _check_obj()]}}
    return {"type": "object", "additionalProperties": False, "required": ["schema_version", "calls"],
            "properties": {"schema_version": {"const": SCHEMA_VERSION}, "calls": calls}}


# ------------------------------------------------------------ strict parsing


class Reject(Exception):
    def __init__(self, reason: str, detail: str = ""):
        super().__init__(f"{reason}: {detail}")
        self.reason, self.detail = reason, detail


def lexical_depth(text: str) -> int:
    depth = peak = 0
    in_str = esc = False
    for ch in text:
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch in "[{":
            depth += 1
            peak = max(peak, depth)
        elif ch in "]}":
            depth -= 1
    return peak


def strict_loads(text: str) -> Any:
    """json.loads minus Python's leniencies: duplicate keys, NaN/Infinity, floats (R59)."""
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError(f"duplicate key {k!r}")
            out[k] = v
        return out

    def no_constant(c):
        raise ValueError(f"non-finite number {c}")

    def no_float(s):
        raise ValueError(f"float {s}")

    return json.loads(text, object_pairs_hook=pairs, parse_constant=no_constant, parse_float=no_float)


def _is_int(v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


# ------------------------------------------------------------------- checks


def _ports(obj: Any):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "port":
                yield v
            yield from _ports(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _ports(v)


def run_checks(kind: str, content: str) -> Optional[str]:
    """Return the first failing profile, or None when every required check passes."""
    for profile in KIND_PROFILES[kind]:
        try:
            data = strict_loads(content)
        except ValueError:
            return profile
        if profile == "json_object" and not isinstance(data, dict):
            return profile
        if profile == "port_range" and not all(_is_int(p) and 1 <= p <= 65535 for p in _ports(data)):
            return profile
        if profile == "activation_state_schema":
            ok = (isinstance(data, dict)
                  and set(data) == {"schema_version", "service", "state", "config_hash", "generation"}
                  and _is_int(data["schema_version"]) and data["schema_version"] == 1
                  and isinstance(data["service"], str)
                  and data["state"] in ("active", "inactive")
                  and isinstance(data["config_hash"], str) and HASH_RE.match(data["config_hash"])
                  and _is_int(data["generation"]) and data["generation"] >= 0)
            if not ok:
                return profile
    return None


# --------------------------------------------------------------- validation


def validate(raw: Optional[str], handles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Controller validation of one raw plan (R59, section 4), in the spec's order.

    Returns {"outcome", "reason", "detail", "plan", "handle"}. outcome is
    validation_failed, no_change or reviewable. Checks are not run here: in v8
    they run on the frozen candidate after approval (see run_checks).
    """
    plan = None
    try:
        if raw is None or not raw.strip():
            raise Reject("empty_response")
        if len(raw.encode("utf-8")) > RESPONSE_LIMIT:
            raise Reject("too_large_response")
        body = raw.strip()
        if lexical_depth(body) > MAX_DEPTH:
            raise Reject("too_deep")
        try:
            plan = strict_loads(body)
        except ValueError as e:
            raise Reject("parse_error", str(e)[:200])
        if not isinstance(plan, dict) or set(plan) != {"schema_version", "calls"}:
            raise Reject("schema_error", "top-level keys")
        if not _is_int(plan["schema_version"]) or plan["schema_version"] != SCHEMA_VERSION:
            raise Reject("schema_error", f"schema_version {plan['schema_version']!r}")
        calls = plan["calls"]
        if not isinstance(calls, list) or not (2 <= len(calls) <= MAX_CALLS):
            raise Reject("schema_error", "call count")
        w = calls[0]
        if not isinstance(w, dict) or set(w) != {"op", "file_handle", "expected_old_hash", "content"} \
                or w["op"] != "write_lab_file":
            raise Reject("schema_error", "first call is not a well-formed write_lab_file")
        if not all(isinstance(w[k], str) for k in ("file_handle", "expected_old_hash", "content")):
            raise Reject("schema_error", "write argument types")
        for c in calls[1:]:
            if not isinstance(c, dict) or set(c) != {"op", "check_profile"} or c["op"] != "run_check" \
                    or not isinstance(c["check_profile"], str):
                raise Reject("schema_error", "non-check call after the write")
        by_id = {h["handle_id"]: h for h in handles}
        h = by_id.get(w["file_handle"])
        if h is None:
            raise Reject("unknown_handle", w["file_handle"][:40])
        if h["kind"] == "context":
            raise Reject("context_target", h["label"])
        if w["expected_old_hash"] != content_hash(h["content"]):
            raise Reject("hash_mismatch", _hash_miss(w["expected_old_hash"], handles, h))
        got = [c["check_profile"] for c in calls[1:]]
        if got != KIND_PROFILES[h["kind"]]:
            raise Reject("check_sequence", f"{got} != {KIND_PROFILES[h['kind']]}")
        if len(w["content"].encode("utf-8", "surrogatepass")) > WRITE_LIMIT:
            raise Reject("content_too_large")
        try:
            w["content"].encode("utf-8")
        except UnicodeEncodeError:
            raise Reject("invalid_unicode")
    except Reject as r:
        return {"outcome": "validation_failed", "reason": r.reason, "detail": r.detail, "plan": plan, "handle": None}
    if w["content"] == h["content"]:
        return {"outcome": "no_change", "reason": "NO_CHANGE", "detail": "", "plan": plan, "handle": h}
    return {"outcome": "reviewable", "reason": "", "detail": "", "plan": plan, "handle": h}


def _hash_miss(got: str, handles: List[Dict[str, Any]], target: Dict[str, Any]) -> str:
    for h in handles:
        if got == content_hash(h["content"]):
            return f"copied {h['label']}'s hash"
    want = content_hash(target["content"])
    if len(got) == len(want):
        return f"{sum(a != b for a, b in zip(got, want))} of 64 hex characters wrong"
    return "wrong length"


# ------------------------------------------------------- expectations (oracle)


def get_path(obj: Any, path: List[Any]) -> Any:
    for p in path:
        if isinstance(p, dict):  # {"name": X}: the list element whose "name" is X
            obj = next((e for e in obj if isinstance(e, dict) and e.get("name") == p["name"]), None) \
                if isinstance(obj, list) else None
        elif isinstance(obj, dict):
            obj = obj.get(p)
        elif isinstance(obj, list) and isinstance(p, int) and -len(obj) <= p < len(obj):
            obj = obj[p]
        else:
            return None
        if obj is None:
            return None
    return obj


def _resolve(value: Any, lab: Lab, old: Any) -> Any:
    if isinstance(value, str) and value.startswith("$hash:"):
        return lab.hash(value[len("$hash:"):])
    if value == "$inc":
        return old + 1
    return value


def apply_edits(content: str, edits: List[List[Any]], lab: Lab) -> str:
    """Apply scenario edit ops to the parsed file. New keys go last (planner rule)."""
    data = json.loads(content)
    for op, path, *rest in edits:
        parent = get_path(data, path[:-1])
        key = path[-1]
        if isinstance(key, dict):
            key = next(i for i, e in enumerate(parent) if isinstance(e, dict) and e.get("name") == key["name"])
        if op == "set":
            old = parent[key] if (isinstance(parent, dict) and key in parent) or isinstance(parent, list) else None
            parent[key] = _resolve(rest[0], lab, old)
        elif op == "del":
            del parent[key]
        elif op == "append":
            parent[key].append(_resolve(rest[0], lab, None))
        else:
            raise ValueError(f"unknown edit op {op}")
    return dumps(data)


def expected_for(txn: Dict[str, Any], lab: Lab) -> Dict[str, Any]:
    """What a correct system does with this transaction, given the lab as it is now.

    Returns {"kind": "write"|"no_change"|"no_commit", "path", "content"}.
    """
    exp = txn["expect"]
    if exp.get("no_commit"):
        return {"kind": "no_commit", "path": exp.get("target"), "content": None}
    if exp.get("no_change"):
        return {"kind": "no_change", "path": exp.get("target"), "content": None}
    path = exp["target"]
    content = exp["content"] if "content" in exp else apply_edits(lab.content(path), exp["edits"], lab)
    if content == lab.content(path):
        return {"kind": "no_change", "path": path, "content": None}
    return {"kind": "write", "path": path, "content": content}


def verdict(proposed: str, expected: Optional[str]) -> str:
    """correct / equivalent (same data, different bytes, or only the final LF) / wrong."""
    if expected is None:
        return "wrong"
    if proposed == expected:
        return "correct"
    try:
        if strict_loads(proposed) == strict_loads(expected):
            return "equivalent"
    except ValueError:
        pass
    return "wrong"


# ---------------------------------------------------------------- diffs


def unified_diff(a: str, b: str, label: str) -> str:
    return "".join(difflib.unified_diff(a.splitlines(True), b.splitlines(True),
                                        fromfile=f"{label} (current)", tofile=f"{label} (proposed)", n=2))


def flatten(obj: Any, prefix: str = "") -> Dict[str, Any]:
    """Leaf paths. List elements with a "name" are addressed by name, others by index."""
    out: Dict[str, Any] = {}
    if isinstance(obj, dict):
        if not obj and prefix:
            out[prefix] = {}
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        if not obj and prefix:
            out[prefix] = []
        for i, v in enumerate(obj):
            tag = f"[name={v['name']}]" if isinstance(v, dict) and isinstance(v.get("name"), str) else f"[{i}]"
            out.update(flatten(v, prefix + tag))
    else:
        out[prefix] = obj
    return out


def json_changes(a: str, b: str) -> Optional[List[Tuple[str, Any, Any]]]:
    """(path, old, new) for every changed leaf, or None when either side is not JSON."""
    try:
        fa, fb = flatten(json.loads(a)), flatten(json.loads(b))
    except ValueError:
        return None
    missing = object()
    out = []
    for k in list(fa) + [k for k in fb if k not in fa]:
        old, new = fa.get(k, missing), fb.get(k, missing)
        if old != new:
            # An empty container that gained (or lost) children is not a change of its own.
            placeholder = (old in ({}, []) and new is missing and any(p.startswith(k) and p != k for p in fb)) or \
                          (new in ({}, []) and old is missing and any(p.startswith(k) and p != k for p in fa))
            if not placeholder:
                out.append((k, None if old is missing else old, None if new is missing else new))
    return out
