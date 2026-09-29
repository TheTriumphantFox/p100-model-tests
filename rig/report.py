"""REPORT.md for one rig run folder (results.jsonl + run.json)."""
from __future__ import annotations

import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

STATUS_MARK = {"COMMITTED": "C", "NO_CHANGE": "N", "VALIDATION_FAILED": "V", "PLANNER_DEADLINE": "D",
               "REVIEW_REJECTED": "R", "HUMAN_REJECTED": "H", "CHECK_FAILED": "K", "SKIPPED": "-"}
LEGEND = ("Transaction marks: `.` ok, `C` committed but wrong, `N` no change when one was needed (or the "
          "reverse), `V` validation failed, `D` planner deadline, `R` reviewer rejected, `H` human rejected, "
          "`K` check failed, `-` skipped after an earlier failure.")


def _pct(a: int, b: int) -> str:
    return f"{a}/{b}" if b else "–"


def _med(xs: List[float]) -> str:
    return f"{statistics.median(xs):.0f}" if xs else "–"


def _p90(xs: List[float]) -> str:
    if not xs:
        return "–"
    xs = sorted(xs)
    return f"{xs[min(len(xs) - 1, int(round(0.9 * (len(xs) - 1))))]:.0f}"


def build(run_dir: Path) -> str:
    meta = json.loads((run_dir / "run.json").read_text())
    rows = [json.loads(l) for l in (run_dir / "results.jsonl").read_text().splitlines() if l.strip()]
    groups: Dict[tuple, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        groups[(r["config"], r["policy"])].append(r)
    keys = sorted(groups)
    cfg_by_name = {c["name"]: c for c in meta["configs"]}

    out = [f"# Rig run: {run_dir.name}", "",
           f"Started {meta['started']}. Suites: {', '.join(meta['suites'])}. "
           f"Response cache {'on' if meta['cache'] else 'off'}.", "", "## Configs", "",
           "| Config | Planner | Reviewer | Reporter | Deadline |", "|---|---|---|---|---|"]
    for name, c in cfg_by_name.items():
        def role(r):
            s = c.get(r)
            if not s:
                return "–"
            extra = f", {s.get('mode', 'gate')}" if r == "reviewer" else ""
            extra += ", checks pinned" if r == "planner" and s.get("pin", True) and \
                meta["personas"].get(s["persona"], {}).get("style") != "loop" else ""
            return f"{s['model']} / {s['persona']}{extra}"
        dl = f"{c.get('deadline_s', 240)} s" + ("" if c.get("enforce_deadline", True) else " (not enforced)")
        out.append(f"| {name} | {role('planner')} | {role('reviewer')} | {role('reporter')} | {dl} |")

    # ---------------------------------------------------------------- headline
    out += ["", "## Headline", "",
            "*Final state* compares the lab after the whole scenario with what a perfect system would have "
            "left. *Committed wrong* is the dangerous number: a wrong change that reached the lab. Under "
            "`oracle` it is always 0 by construction, and *human catches* counts what the human had to stop "
            "instead.", "",
            "| Config | Policy | Final state exact (+equiv) | Transactions ok | Committed wrong | Human catches "
            "| Escalation-eligible | Injection followed / committed | Model s per scenario (median) |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for k in keys:
        g = groups[k]
        tx = [t for r in g for t in r["transactions"]]
        ran = [t for t in tx if t["status"] != "SKIPPED"]
        exact = sum(r["final_state"] == "exact" for r in g)
        equiv = sum(r["final_state"] == "equivalent" for r in g)
        inj = [t for t in ran if t.get("injection_followed") is not None]
        out.append(
            f"| {k[0]} | {k[1]} | {exact}{f' (+{equiv})' if equiv else ''}/{len(g)} "
            f"| {_pct(sum(t['ok'] for t in tx), len(tx))} | {sum(t.get('committed_wrong', False) for t in ran)} "
            f"| {sum(t.get('status') == 'HUMAN_REJECTED' for t in ran)} "
            f"| {sum(t.get('escalation_eligible', False) for t in ran)} "
            f"| {sum(bool(t['injection_followed']) for t in inj)} / {sum(t['injection_committed'] for t in inj)} of {len(inj)} "
            f"| {_med([r['model_seconds'] for r in g])} |")

    # ------------------------------------------------------------ where it ended
    out += ["", "## Where each transaction ended", "",
            "| Config | Policy | Committed | No change | Validation failed | Deadline | Reviewer rejected "
            "| Human rejected | Check failed | Skipped |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    reasons: Dict[tuple, Counter] = {}
    for k in keys:
        tx = [t for r in groups[k] for t in r["transactions"]]
        c = Counter(t["status"] for t in tx)
        out.append(f"| {k[0]} | {k[1]} | {c['COMMITTED']} | {c['NO_CHANGE']} | {c['VALIDATION_FAILED']} "
                   f"| {c['PLANNER_DEADLINE']} | {c['REVIEW_REJECTED']} | {c['HUMAN_REJECTED']} "
                   f"| {c['CHECK_FAILED']} | {c['SKIPPED']} |")
        reasons[k] = Counter(t["validation"]["reason"] for t in tx
                             if t.get("validation", {}).get("outcome") == "validation_failed")
    if any(reasons.values()):
        out += ["", "Validation failures by reason (including any the deadline preempted):", ""]
        for k in keys:
            if reasons[k]:
                out.append(f"- {k[0]} / {k[1]}: " + ", ".join(f"`{r}` {n}" for r, n in reasons[k].most_common()))

    # ---------------------------------------------------------------- reviewer
    rk = [k for k in keys if cfg_by_name[k[0]].get("reviewer")]
    if rk:
        out += ["", "## Reviewer", "",
                "Proposals that reached the reviewer, by whether the proposal was actually right. "
                "*Unusable* means the review could not be parsed; in gate mode it blocks.", "",
                "| Config | Policy | Wrong, rejected (caught) | Wrong, approved (missed) | Right, rejected (false alarm) "
                "| Right, approved | Unusable | Injected plans let through | Median s |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
        for k in rk:
            tx = [t for r in groups[k] for t in r["transactions"] if "reviewer" in t]
            good = lambda t: t["verdict"] in ("correct", "equivalent")
            rej = lambda t: t["reviewer"]["verdict"] == "reject"
            out.append(
                f"| {k[0]} | {k[1]} | {sum(not good(t) and rej(t) for t in tx)} "
                f"| {sum(not good(t) and t['reviewer']['verdict'] == 'approve' for t in tx)} "
                f"| {sum(good(t) and rej(t) for t in tx)} | {sum(good(t) and t['reviewer']['verdict'] == 'approve' for t in tx)} "
                f"| {sum(t['reviewer']['verdict'] is None for t in tx)} "
                f"| {sum(bool(t.get('injection_followed')) and t['reviewer']['verdict'] == 'approve' for t in tx)} "
                f"| {_med([t['reviewer']['seconds'] for t in tx])} |")

    # ---------------------------------------------------------------- reporter
    pk = [k for k in keys if cfg_by_name[k[0]].get("reporter")]
    if pk:
        out += ["", "## Reporter", "",
                "Does the explanation shown to the human match the diff? *Missed* counts real changed fields the "
                "report left out; *phantom* counts reported changes that are not in the diff. A recommendation "
                "to approve a wrong proposal is the case that misleads the human.", "",
                "| Config | Policy | Reports | Complete and exact | Missed fields | Phantom changes "
                "| Approve on wrong | Reject on right | Unusable | Median s |",
                "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for k in pk:
            tx = [t for r in groups[k] for t in r["transactions"] if "reporter" in t]
            sc = [t for t in tx if t["reporter"]["score"]]
            good = lambda t: t["verdict"] in ("correct", "equivalent")
            rec = lambda t: (t["reporter"]["report"] or {}).get("recommendation")
            out.append(
                f"| {k[0]} | {k[1]} | {len(tx)} "
                f"| {sum(not t['reporter']['score']['missed'] and not t['reporter']['score']['phantom'] for t in sc)} "
                f"| {sum(len(t['reporter']['score']['missed']) for t in sc)} | {sum(t['reporter']['score']['phantom'] for t in sc)} "
                f"| {sum(not good(t) and rec(t) == 'approve' for t in tx)} | {sum(good(t) and rec(t) == 'reject' for t in tx)} "
                f"| {sum(t['reporter']['report'] is None for t in tx)} | {_med([t['reporter']['seconds'] for t in tx])} |")

    # -------------------------------------------------------------------- time
    out += ["", "## Time", "",
            "Model seconds are the server's prompt + generation time per call (a cached call reports the "
            "time it took when it ran), so a model load is never charged to a role or to the deadline. "
            "*Model switches* count uncached calls served by a different model from the last uncached "
            "call, which on one pair of GPUs means an unload and a load; *load overhead* is wall time the server did not "
            "spend on prompt or generation, summed over uncached calls.", "",
            "| Config | Policy | Planner median | Planner p90 | Over 120 s | Over 240 s | Loop steps (median) "
            "| Model switches | Load overhead s |", "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for k in keys:
        tx = [t for r in groups[k] for t in r["transactions"] if "planner" in t]
        ps = [t["planner"]["seconds"] for t in tx]
        calls = [c for t in tx for role in ("planner", "reviewer", "reporter") if role in t for c in t[role]["calls"]]
        # Physical switches, from call order: only uncached calls reach the server and change
        # which model is resident. (Stored model_switch flags from early runs counted cached calls.)
        switches, resident = 0, None
        for t in tx:
            for role in ("planner", "reviewer", "reporter"):
                for c in t.get(role, {}).get("calls", []):
                    if c.get("cached") or c.get("mock"):
                        continue
                    if resident is not None and resident != t[role]["model"]:
                        switches += 1
                    resident = t[role]["model"]
        loop = cfg_by_name[k[0]]["planner"]["persona"]
        steps = _med([t["planner"]["steps"] for t in tx]) if meta["personas"].get(loop, {}).get("style") == "loop" else "–"
        out.append(f"| {k[0]} | {k[1]} | {_med(ps)} | {_p90(ps)} | {sum(t['over_deadline']['120'] for t in tx)} "
                   f"| {sum(t['over_deadline']['240'] for t in tx)} | {steps} "
                   f"| {switches} "
                   f"| {sum(c.get('load_overhead_s') or 0 for c in calls):.0f} |")

    # ------------------------------------------------------------ per scenario
    out += ["", "## Per scenario", "", LEGEND, "Final state: `=` exact, `~` equivalent, `x` diverged.", ""]
    scen = sorted({r["scenario"] for r in rows}, key=lambda s: (next(r["suite"] for r in rows if r["scenario"] == s), s))
    out.append("| Scenario | " + " | ".join(f"{c}<br>{p}" for c, p in keys) + " |")
    out.append("|---|" + "---|" * len(keys))
    idx = {(r["config"], r["policy"], r["scenario"]): r for r in rows}
    for s in scen:
        cells = []
        for k in keys:
            r = idx.get((k[0], k[1], s))
            if not r:
                cells.append("")
                continue
            marks = "".join("." if t["ok"] else STATUS_MARK.get(t["status"], "?") for t in r["transactions"])
            cells.append(f"`{marks}` {dict(exact='=', equivalent='~', diverged='x')[r['final_state']]}")
        out.append(f"| {s} | " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"
