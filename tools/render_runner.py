"""render_runner.py - lets a foreman without SSH start renders on utkarsh-pc through git (runs on vivek-pc).

A request is `queue/render/<id>.md` (written by claude-lead or the acting lead) with front matter:
    segs: s2a,intro            # names known by local/rendering/render_utk.ps1 (intro, s2a, s2b, s3, exploded, cards)
    assemble: draft|final|no   # then run film/final/assemble_v3.py (draft adds --draft)
The runner (every 60 s, in the read-only watch clone) runs each new request once, over SSH, in the render
clone on utkarsh-pc, then pushes results/<id>/REPORT.md (status, render log tail, assembly/QC summary) and
results/<id>/contact_960.jpg if QC made one. State: local/render-runner-state.json (ids already run).

    python tools/render_runner.py --clone ..\\itantra-watch [--loop]
"""
import argparse, json, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import NO_WINDOW, push_files_direct  # noqa: E402

LEAD = Path(__file__).resolve().parent.parent
STATE = LEAD / "local" / "render-runner-state.json"
PS1 = LEAD / "local" / "rendering" / "render_utk.ps1"
HOST, RDIR = "utkarsh", r"D:\Presentation_Itantra\itantra-render"
SEGS = {"intro", "s2a", "s2b", "s3", "exploded", "cards"}


def sh(cmd, timeout=7200):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace",
                       creationflags=NO_WINDOW)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def front(text):
    out = {}
    if text.startswith("---"):
        for line in text.split("---", 2)[1].splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip()
    return out


def clean(s):
    return "\n".join(l for l in s.splitlines() if "post-quantum" not in l and "vulnerable" not in l and "upgraded" not in l)


def run(rid, fm):
    segs = [s.strip() for s in fm.get("segs", "").split(",") if s.strip()]
    bad = [s for s in segs if s not in SEGS]
    if bad:
        return "failed", f"unknown segments: {bad}", None
    log = []
    sh(["scp", "-q", str(PS1), f"{HOST}:D:/Presentation_Itantra/render_utk.ps1"], 120)
    if segs:
        code, out = sh(["ssh", HOST, f"powershell -NoProfile -ExecutionPolicy Bypass -File D:\\Presentation_Itantra\\render_utk.ps1 -SegList {','.join(segs)}"])
        _, tail = sh(["ssh", HOST, f"powershell -NoProfile -Command \"Get-Content {RDIR}\\local\\render-log.txt -Tail {3 * len(segs) + 2}\""], 120)
        log.append("## Render log\n```\n" + clean(tail) + "\n```")
        if "exit 0" not in tail and segs:
            log.append("(check: no segment reported exit 0)")
    asm = fm.get("assemble", "no").lower()
    jpg = None
    if asm in ("draft", "final"):
        flag = " --draft" if asm == "draft" else ""
        code, out = sh(["ssh", HOST, f"cd /d {RDIR} && python film\\final\\assemble_v3.py{flag}"])
        log.append(f"## Assembly ({asm}), exit {code}\n```\n" + clean(out)[-3500:] + "\n```")
        rd = r"D:\Presentation_Itantra\itantra-video\local\renders"
        name = "full_film_v3_draft_contact_960.jpg" if asm == "draft" else "full_film_v3_contact_960.jpg"
        tmp = LEAD / "local" / "tmp" / f"{rid}_contact.jpg"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        c2, _ = sh(["scp", "-q", f"{HOST}:{rd}\\{name}".replace("\\", "/"), str(tmp)], 300)
        if c2 == 0 and tmp.exists() and tmp.stat().st_size < 3_000_000:
            jpg = tmp.read_bytes()
        status = "done" if code == 0 else "failed"
    else:
        status = "done"
    return status, "\n\n".join(log), jpg


def once(clone):
    subprocess.run(["git", "-C", str(clone), "pull", "--ff-only", "-q"], capture_output=True, timeout=120, creationflags=NO_WINDOW)
    state = json.loads(STATE.read_text()) if STATE.exists() else {"done": []}
    for f in sorted((clone / "queue" / "render").glob("*.md")):
        rid = f.stem
        if rid in state["done"] or (clone / "results" / rid / "REPORT.md").exists():
            continue
        state["done"].append(rid)
        STATE.write_text(json.dumps(state))
        fm = front(f.read_text(encoding="utf-8", errors="replace"))
        push_files_direct({f"results/{rid}/STARTED.json": json.dumps({"by": "render_runner", "time": time.strftime("%Y-%m-%dT%H:%M:%S")}).encode()}, f"render runner: start {rid}")
        try:
            status, body, jpg = run(rid, fm)
        except Exception as e:  # noqa: BLE001
            status, body, jpg = "failed", f"runner error: {e}", None
        files = {f"results/{rid}/REPORT.md": f"---\nstatus: {status}\n---\n# {rid} (render runner on vivek-pc, renders on utkarsh-pc)\n\n{body}\n".encode("utf-8")}
        if jpg:
            files[f"results/{rid}/contact_960.jpg"] = jpg
        push_files_direct(files, f"render runner: {rid} {status}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", required=True)
    ap.add_argument("--loop", action="store_true")
    a = ap.parse_args()
    clone = Path(a.clone).resolve()
    while True:
        try:
            once(clone)
        except Exception as e:  # noqa: BLE001
            print("render_runner error:", e, flush=True)
        if not a.loop:
            break
        time.sleep(60)


if __name__ == "__main__":
    main()
