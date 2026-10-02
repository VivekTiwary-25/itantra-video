"""swarm.py - start, stop and inspect every listener of one project from the lead's PC, over SSH.

Host details are private and live only in the git-ignored file local/swarm/<project>.json:
{
  "project": "itantra-video",
  "github_repo": "<owner>/<repo>",
  "listeners": [
    {"name": "vivek-pc",   "host": null,    "repo": "<absolute path of that listener's clone>"},
    {"name": "yash-pc",    "host": "yash",  "repo": "...", "python": "<optional python.exe path>"}
  ]
}
"host" is an alias from the lead's ~/.ssh/config (null = this PC). One entry per listener clone, so one PC may
appear more than once. "name" must match machine.local.json in that clone.

Usage:
  python tools/swarm.py start  [--project P] [--only NAME]   start every listener that is not running (+ the supervisor)
  python tools/swarm.py stop   [--project P] [--only NAME] [--now]   ask listeners to stop (--now also kills them)
  python tools/swarm.py status [--project P]                 one line per listener, straight from the machines
  python tools/swarm.py keys   [--project P] [--only NAME]   give remote clones a push-only deploy key (see below)
  python tools/swarm.py send   TASK_ID FILE... [--project P] copy private inputs to local/private-in/<id>/ on every clone
  python tools/swarm.py fetch  TASK_ID [--project P]        copy local/private-out/<id>/ back from the clone that ran it

Listeners are launched with WMI (Win32_Process.Create), so they belong to no SSH session and keep running
after the connection drops. They run tools/run-listener.cmd, which restarts the listener whenever it exits.

Why deploy keys: in a key-based SSH login Windows cannot open the user's credential store, so git pushes over
HTTPS fail for anything started over SSH. `keys` makes an ed25519 key inside the clone's git-ignored local/
folder, registers it as a write deploy key for this repo only (gh, on the lead's PC), and sets the clone's
push URL and core.sshCommand (repo-local git config). Fetches stay anonymous HTTPS.
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures as cf
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import NO_WINDOW, REPO_ROOT, read_json  # noqa: E402

SSH_OPTS = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=12", "-o", "LogLevel=ERROR", "-o", "ServerAliveInterval=15"]


# ---------------------------------------------------------------- config
def config_path(project: str | None) -> Path:
    d = REPO_ROOT / "local" / "swarm"
    if project:
        return d / f"{project}.json"
    found = sorted(d.glob("*.json"))
    if len(found) != 1:
        sys.exit(f"Give --project (found {len(found)} project files in local/swarm/).")
    return found[0]


def load_config(project: str | None) -> dict:
    p = config_path(project)
    cfg = read_json(p)
    if not cfg:
        sys.exit(f"Missing or unreadable {p}. See the docstring of tools/swarm.py.")
    return cfg


def pick(cfg: dict, only: str | None) -> list[dict]:
    ls = [l for l in cfg["listeners"] if l.get("repo")]
    if only:
        ls = [l for l in ls if l["name"] == only]
        if not ls:
            sys.exit(f"No listener named {only}.")
    return ls


# ---------------------------------------------------------------- running PowerShell here or over SSH
def ps(host: str | None, script: str, params: dict | None = None, timeout: int = 90) -> tuple[int, str]:
    """Run a PowerShell script locally (host None) or on an SSH host. `params` become variables ($name).
    Returns (exit code, stdout). Exit code 255 from ssh means the machine could not be reached."""
    pre = "$ProgressPreference='SilentlyContinue'\n"
    for k, v in (params or {}).items():
        pre += f"${k} = " + "'" + str(v).replace("'", "''") + "'\n"
    enc = base64.b64encode((pre + script).encode("utf-16-le")).decode()
    cmd = ["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", enc]
    if host:
        cmd = ["ssh", *SSH_OPTS, host, " ".join(cmd)]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout, creationflags=NO_WINDOW)
    except subprocess.TimeoutExpired:
        return 124, ""
    out = (p.stdout or b"").decode("utf-8", "replace")
    return p.returncode, "\n".join(l for l in out.splitlines() if not l.startswith(("#< CLIXML", "<Objs")))


def last_json(out: str) -> dict | None:
    for line in reversed(out.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except ValueError:
                return None
    return None


# Everything the supervisor needs to know about one listener clone, in one round trip.
PROBE = r"""
$ErrorActionPreference = 'SilentlyContinue'
$r = [ordered]@{ reachable = $true; repo_ok = (Test-Path (Join-Path $repo '.git')) }
if (-not $r.repo_ok) { $r | ConvertTo-Json -Compress; exit }
Set-Location $repo
$now = Get-Date
function Age($p) { if (Test-Path $p) { [int]($now - (Get-Item $p -Force).LastWriteTime).TotalSeconds } else { $null } }
$cfg = Get-Content machine.local.json -Raw | ConvertFrom-Json
$r.machine = $cfg.machine
$procs = @(Get-CimInstance Win32_Process)
$r.lock_pid = $null
if (Test-Path local\listener.lock) { $r.lock_pid = [int]((Get-Content local\listener.lock -Raw).Trim()) }
$lp = $procs | Where-Object { $_.ProcessId -eq $r.lock_pid -and $_.CommandLine -match 'listener\.py' }
$r.listener_alive = [bool]$lp
$r.loop_alive = [bool]($procs | Where-Object { $_.Name -eq 'cmd.exe' -and $_.CommandLine -like "*$repo\tools\run-listener.cmd*" })
$kids = @()
if ($lp) {
  $todo = @($r.lock_pid)
  while ($todo.Count) { $p = $todo[0]; $todo = @($todo | Select-Object -Skip 1)
    foreach ($c in ($procs | Where-Object { $_.ParentProcessId -eq $p })) { $kids += "$($c.ProcessId):$($c.Name)"; $todo += $c.ProcessId } }
}
$r.children = $kids
$hbp = "machines\$($cfg.machine)\heartbeat.json"
if (Test-Path $hbp) { $hb = Get-Content $hbp -Raw | ConvertFrom-Json
  $r.hb_time = $hb.time; $r.hb_status = $hb.status; $r.current_task = $hb.current_task
  $r.rate_limited = $hb.rate_limited_until; $r.unpushed = $hb.unpushed_commits; $r.last_push_ok = $hb.last_push_ok }
$r.hb_age = Age $hbp
$r.task_log_age = if ($r.current_task) { Age "local\logs\task-$($r.current_task).log" } else { $null }
$rb = @('.git\rebase-merge', '.git\rebase-apply') | Where-Object { Test-Path $_ } | Select-Object -First 1
$r.rebase_age = if ($rb) { Age $rb } else { $null }
$r.dirty = @(git status --porcelain --untracked-files=no | Select-Object -First 6)
$r.stashes = @(git stash list).Count
$r.autostash_flag = Test-Path local\autostash-left.flag
$r.stop_flag = Test-Path local\listener.stop
$r.push_url = (git remote get-url --push origin) -replace '//[^@/]*@', '//'
$r | ConvertTo-Json -Compress -Depth 3
"""

START = r"""
Set-Location $repo
Remove-Item local\listener.stop -ErrorAction SilentlyContinue
if ($python) { Set-Content -Path local\python.txt -Value $python -Encoding Ascii -NoNewline }
$running = Get-CimInstance Win32_Process -Filter "Name='cmd.exe'" | Where-Object { $_.CommandLine -like "*$repo\tools\run-listener.cmd*" }
if ($running) { "already running (loop pid $($running[0].ProcessId))"; exit }
$si = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ ShowWindow = [uint16]0 }
$res = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
  CommandLine = "cmd.exe /d /c `"$repo\tools\run-listener.cmd`""; CurrentDirectory = $repo; ProcessStartupInformation = $si }
if ($res.ReturnValue -eq 0) { "started (loop pid $($res.ProcessId))" } else { "FAILED to start: WMI code $($res.ReturnValue)" }
"""

STOP = r"""
Set-Location $repo
New-Item -ItemType Directory -Force local | Out-Null
Set-Content -Path local\listener.stop -Value 'swarm stop' -Encoding Ascii
if ($now -eq '1') {
  Get-CimInstance Win32_Process -Filter "Name='cmd.exe'" | Where-Object { $_.CommandLine -like "*$repo\tools\run-listener.cmd*" } |
    ForEach-Object { taskkill /F /T /PID $_.ProcessId | Out-Null }
  if (Test-Path local\listener.lock) { taskkill /F /T /PID ((Get-Content local\listener.lock -Raw).Trim()) | Out-Null }
  "stopped now"
} else { "will stop when idle (local\listener.stop written)" }
"""


def probe(l: dict, timeout: int = 90) -> dict:
    rc, out = ps(l.get("host"), PROBE, {"repo": l["repo"]}, timeout=timeout)
    data = last_json(out)
    if data is None:
        return {"reachable": False, "rc": rc}
    return data


def start_one(l: dict) -> str:
    rc, out = ps(l.get("host"), START, {"repo": l["repo"], "python": l.get("python", "")})
    if rc == 255 or (rc != 0 and not out.strip()):
        return "UNREACHABLE"
    return out.strip().splitlines()[-1] if out.strip() else f"exit {rc}"


def start_supervisor() -> str:
    """The supervisor runs on the lead's PC from this clone, also launched through WMI so it outlives the session."""
    pidf = REPO_ROOT / "local" / "supervisor.pid"
    rc, out = ps(None, r"""
$p = $null; if (Test-Path $pidf) { $p = Get-CimInstance Win32_Process -Filter "ProcessId=$((Get-Content $pidf -Raw).Trim())" }
if ($p -and $p.CommandLine -match 'supervisor\.py') { "supervisor already running (pid $($p.ProcessId))"; exit }
$py = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source; if (-not $py) { $py = (Get-Command python.exe).Source }
$si = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ ShowWindow = [uint16]0 }
$res = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
  CommandLine = "`"$py`" `"$repo\tools\supervisor.py`" --project $project"; CurrentDirectory = $repo; ProcessStartupInformation = $si }
"supervisor started (pid $($res.ProcessId))"
""", {"pidf": str(pidf), "repo": str(REPO_ROOT), "project": CURRENT_PROJECT})
    return out.strip().splitlines()[-1] if out.strip() else f"exit {rc}"


# ---------------------------------------------------------------- deploy keys
KEYGEN = r"""
Set-Location $repo
New-Item -ItemType Directory -Force local | Out-Null
$k = Join-Path $repo 'local\deploy_key'
if (-not (Test-Path $k)) { ssh-keygen -q -t ed25519 -N '""' -C "$name listener" -f $k | Out-Null }
Get-Content "$k.pub" -Raw
"""

KEYUSE = r"""
Set-Location $repo
$k = (Join-Path $repo 'local\deploy_key') -replace '\\', '/'
$kh = (Join-Path $repo 'local\known_hosts') -replace '\\', '/'
git config --local core.sshCommand "ssh -i '$k' -o IdentitiesOnly=yes -o UserKnownHostsFile='$kh' -o StrictHostKeyChecking=accept-new"
git remote set-url --push origin "git@github.com:$ghrepo.git"
$env:GIT_TERMINAL_PROMPT = '0'
$o = git push --dry-run origin HEAD 2>&1
"push test exit $LASTEXITCODE : " + (($o | Out-String).Trim() -replace '\s+', ' ')
"""


def keys_one(l: dict, ghrepo: str) -> str:
    if not l.get("host"):
        return "local clone: uses this PC's normal git credentials"
    rc, out = ps(l["host"], KEYGEN, {"repo": l["repo"], "name": l["name"]})
    pub = next((x for x in out.splitlines() if x.startswith("ssh-ed25519")), None)
    if not pub:
        return f"could not make a key (exit {rc})"
    title = f"{l['name']} listener ({Path(l['repo']).name})"
    listed = subprocess.run(["gh", "repo", "deploy-key", "list", "-R", ghrepo], capture_output=True, text=True).stdout
    if pub.split()[1] not in listed:
        with tempfile.NamedTemporaryFile("w", suffix=".pub", delete=False) as f:
            f.write(pub.strip() + "\n")
        r = subprocess.run(["gh", "repo", "deploy-key", "add", f.name, "--allow-write", "--title", title, "-R", ghrepo],
                           capture_output=True, text=True)
        Path(f.name).unlink(missing_ok=True)
        if r.returncode != 0 and "already in use" not in (r.stderr or ""):
            return "gh could not add the key: " + (r.stderr or r.stdout).strip()[:200]
    rc, out = ps(l["host"], KEYUSE, {"repo": l["repo"], "ghrepo": ghrepo})
    return out.strip().splitlines()[-1] if out.strip() else f"exit {rc}"


# ---------------------------------------------------------------- private files (never in git): PPT inputs and outputs
def scp_target(l: dict, rel: str) -> str:
    return f"{l['host']}:" + (l["repo"].replace("\\", "/") + "/" + rel).replace(" ", "\\ ")


def send(cfg: dict, task_id: str, files: list[str]) -> None:
    for l in pick(cfg, None):
        rel = f"local/private-in/{task_id}"
        if not l.get("host"):
            dest = Path(l["repo"]) / rel
            dest.mkdir(parents=True, exist_ok=True)
            for f in files:
                subprocess.run(["powershell", "-NoProfile", "-Command", f"Copy-Item -Force -LiteralPath '{f}' -Destination '{dest}'"])
            print(f"{l['name']:<18} copied {len(files)} file(s)")
            continue
        ps(l["host"], "New-Item -ItemType Directory -Force (Join-Path $repo $rel) | Out-Null", {"repo": l["repo"], "rel": rel})
        r = subprocess.run(["scp", "-q", *SSH_OPTS, *files, scp_target(l, rel + "/")], capture_output=True, text=True, timeout=300)
        print(f"{l['name']:<18} " + ("copied" if r.returncode == 0 else "FAILED: " + r.stderr.strip()[:150]))


def fetch(cfg: dict, task_id: str) -> Path | None:
    """Copy local/private-out/<id>/ from whichever clone ran the task into this clone's local/private-out/<id>/."""
    started = read_json(REPO_ROOT / "results" / task_id / "STARTED.json") or {}
    l = next((x for x in pick(cfg, None) if x["name"] == started.get("machine")), None)
    if not l:
        print(f"{task_id}: no STARTED.json from a known clone (git pull first)")
        return None
    dest = REPO_ROOT / "local" / "private-out" / task_id
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not l.get("host"):
        src = Path(l["repo"]) / "local" / "private-out" / task_id
        subprocess.run(["powershell", "-NoProfile", "-Command", f"Copy-Item -Recurse -Force -LiteralPath '{src}' -Destination '{dest.parent}'"])
    else:
        r = subprocess.run(["scp", "-q", "-r", *SSH_OPTS, scp_target(l, f"local/private-out/{task_id}"), str(dest.parent)],
                           capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            print(f"{task_id}: fetch failed: {r.stderr.strip()[:200]}")
            return None
    print(f"{task_id}: copied to local/private-out/{task_id}/")
    return dest


# ---------------------------------------------------------------- commands
CURRENT_PROJECT = ""


def fmt_status(name: str, d: dict) -> str:
    if not d.get("reachable"):
        return f"{name:<18} UNREACHABLE (network)"
    if not d.get("repo_ok"):
        return f"{name:<18} repo folder missing"
    bits = ["listener " + ("UP" if d.get("listener_alive") else "DOWN"), "loop " + ("up" if d.get("loop_alive") else "down"),
            f"hb {d.get('hb_status')} {d.get('hb_age')}s ago"]
    if d.get("current_task"):
        bits.append(f"task {d['current_task']} (log {d.get('task_log_age')}s)")
    if d.get("rate_limited"):
        bits.append("RATE-LIMITED")
    if d.get("rebase_age") is not None:
        bits.append(f"REBASE STUCK {d['rebase_age']}s")
    if d.get("dirty"):
        bits.append(f"dirty {len(d['dirty'])}")
    if d.get("autostash_flag"):
        bits.append("AUTOSTASH LEFT")
    if d.get("stop_flag"):
        bits.append("stop requested")
    return f"{name:<18} " + ", ".join(bits)


def main() -> None:
    global CURRENT_PROJECT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["start", "stop", "status", "keys", "send", "fetch"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--project")
    ap.add_argument("--only")
    ap.add_argument("--now", action="store_true")
    ap.add_argument("--no-supervisor", action="store_true")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cfg = load_config(a.project)
    CURRENT_PROJECT = cfg.get("project") or config_path(a.project).stem
    ls = pick(cfg, a.only)
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        if a.cmd == "start":
            for l, res in zip(ls, ex.map(start_one, ls)):
                print(f"{l['name']:<18} {res}")
            if not a.only and not a.no_supervisor:
                print(f"{'supervisor':<18} {start_supervisor()}")
        elif a.cmd == "stop":
            for l, res in zip(ls, ex.map(lambda l: ps(l.get("host"), STOP, {"repo": l["repo"], "now": "1" if a.now else "0"})[1].strip(), ls)):
                print(f"{l['name']:<18} {res or 'UNREACHABLE'}")
        elif a.cmd == "status":
            for l, d in zip(ls, ex.map(probe, ls)):
                print(fmt_status(l["name"], d))
        elif a.cmd == "keys":
            for l, res in zip(ls, ex.map(lambda l: keys_one(l, cfg["github_repo"]), ls)):
                print(f"{l['name']:<18} {res}")
    if a.cmd == "send":
        if len(a.args) < 2:
            sys.exit("usage: swarm.py send TASK_ID FILE...")
        send(cfg, a.args[0], a.args[1:])
    elif a.cmd == "fetch":
        if len(a.args) != 1:
            sys.exit("usage: swarm.py fetch TASK_ID")
        fetch(cfg, a.args[0])


if __name__ == "__main__":
    main()
