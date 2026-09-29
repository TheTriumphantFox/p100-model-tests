"""Raw vs JSON-escaped tokenization of the planner-bench replacement files.

For every planner-bench task, the ideal plan's replacement content is tokenized three ways
with each candidate model's own tokenizer (llama-server /tokenize, CPU only, no weights
touched beyond mmap, no warmup):

  raw      the file bytes as they are
  escaped  the same bytes as the body of a JSON string (ensure_ascii=False), which is
           what a section 4 plan makes the model emit today
  ascii    the same, with ensure_ascii=True (\\uXXXX for non-ASCII); a grammar allows it

and the whole plan two ways:

  plan_json   json.dumps(ideal plan, ensure_ascii=False), exactly as selftest.py renders it
  plan_block  the same plan with "content" removed, followed by a raw delimited block

Usage: measure.py <slug> <port>   (the caller starts and stops the server)
"""
import json
import sys
import urllib.request
from pathlib import Path

BENCH = Path(__file__).resolve().parent.parent / "planner-bench"
sys.path.insert(0, str(BENCH))
from selftest import ideal  # noqa: E402

OPEN, CLOSE = "<<<CONTENT\n", "\nCONTENT>>>\n"


def ntok(port: int, text: str) -> int:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/tokenize",
        data=json.dumps({"content": text, "add_special": False}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return len(json.load(r)["tokens"])


def plan_block(plan: dict) -> str:
    header = json.loads(json.dumps(plan))
    content = header["calls"][0].pop("content")
    return json.dumps(header, ensure_ascii=False) + "\n" + OPEN + content + CLOSE


def main() -> int:
    slug, port = sys.argv[1], int(sys.argv[2])
    tasks = json.load(open(BENCH / "tasks.json"))["tasks"]
    rows = []
    for t in tasks:
        plan = ideal(t)
        c = t["expected_content"]
        rows.append({
            "id": t["id"], "family": t["family"],
            "bytes": len(c.encode("utf-8")),
            "raw": ntok(port, c),
            "escaped": ntok(port, json.dumps(c, ensure_ascii=False)[1:-1]),
            "ascii": ntok(port, json.dumps(c)[1:-1]),
            "plan_json": ntok(port, json.dumps(plan, ensure_ascii=False)),
            "plan_block": ntok(port, plan_block(plan)),
        })
    out = Path(__file__).resolve().parent / "results" / f"{slug}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"model": slug, "rows": rows}, indent=1))
    b = sum(r["bytes"] for r in rows)
    print(f"{slug}: {len(rows)} tasks, raw {b / sum(r['raw'] for r in rows):.2f} B/tok, "
          f"escaped {b / sum(r['escaped'] for r in rows):.2f} B/tok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
