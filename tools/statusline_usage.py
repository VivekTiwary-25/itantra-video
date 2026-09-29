"""statusline_usage.py - Claude Code status-line command.

Reads the status-line JSON from stdin, saves rate_limits and context_window to local/claude-usage.json
(the lead reads that file to watch its own usage), and prints a one-line status.
The rate_limits fields only appear after the first response in a session.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "local" / "claude-usage.json"


def pct(d, *path):
    for k in path:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def fmt(v):
    return f"{v:.0f}%" if isinstance(v, (int, float)) else "--"


def main() -> None:
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        data = {}
    five = pct(data, "rate_limits", "five_hour", "used_percentage")
    seven = pct(data, "rate_limits", "seven_day", "used_percentage")
    ctx = pct(data, "context_window", "used_percentage")
    model = pct(data, "model", "display_name") or pct(data, "model", "id") or "?"
    try:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps({
            "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "model": model,
            "rate_limits": data.get("rate_limits"),
            "context_window": data.get("context_window"),
        }, indent=2), encoding="utf-8")
    except OSError:
        pass
    print(f"{model} | 5h {fmt(five)} | 7d {fmt(seven)} | ctx {fmt(ctx)}")


if __name__ == "__main__":
    main()
