"""Record a phone screen to match an over-shoulder take; run --dry-run first."""

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NAMES = ("quick_settings", "airplane_mode", "close_quick_settings", "open_itantra", "ptt_down")


def commands(taps):
    events = []
    for name in NAMES:
        item = taps[name]
        xy = [str(item[k]) for k in ("x", "y")]
        if name in ("quick_settings", "close_quick_settings"):
            cmd = ["shell", "input", "swipe", *xy, str(item["end_x"]), str(item["end_y"]), str(item["duration_ms"])]
        elif name == "ptt_down":
            hold_ms = round((taps["ptt_up"]["time"] - item["time"]) * 1000)
            cmd = ["shell", "input", "swipe", *xy, *xy, str(hold_ms)]
        else:
            cmd = ["shell", "input", "tap", *xy]
        events.append((name, item["time"], cmd))
    times = [t for _, t, _ in events] + [taps["ptt_up"]["time"]]
    cutoff = times[-1] - taps["cut_before_release_ms"] / 1000
    if times[0] < 0 or any(b <= a for a, b in zip(times, times[1:])) or cutoff <= times[-2]:
        raise ValueError("Times must increase, and recording must stop after PTT starts but before release")
    if any(taps[n].get("x", 0) <= 0 or taps[n].get("y", 0) <= 0 for n in ("airplane_mode", "open_itantra", "ptt_down")):
        return events, cutoff, False
    return events, cutoff, True


def find_tool(name):
    candidates = [ROOT / "local" / "tools" / name, ROOT / "local" / "tools" / "scrcpy" / name]
    return next((str(p) for p in candidates if p.is_file()), shutil.which(name))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print commands; no phone or files needed")
    parser.add_argument("--taps", type=Path, default=HERE / "taps.json")
    args = parser.parse_args()
    taps = json.loads(args.taps.read_text(encoding="utf-8"))
    events, cutoff, coordinates_ready = commands(taps)
    if args.dry_run:
        for name, at, cmd in events:
            print(f"{at:.3f}s {name}: adb {' '.join(cmd)}")
        print(f"{cutoff:.3f}s stop scrcpy; PTT release scheduled at {taps['ptt_up']['time']:.3f}s")
        if not coordinates_ready:
            print("Replace zero coordinate placeholders before recording.")
        return
    if not coordinates_ready:
        parser.error("Replace zero coordinate placeholders in taps.json before recording")
    scrcpy, adb = find_tool("scrcpy.exe"), find_tool("adb.exe")
    if not scrcpy or not adb:
        parser.error("scrcpy.exe and adb.exe must be in local/tools, local/tools/scrcpy, or PATH")
    machine = json.loads((ROOT / "machine.local.json").read_text(encoding="utf-8"))
    out_dir = Path(machine["renders_dir"]) / "intro30" / "screen"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    video = out_dir / f"screen-{stamp}.mkv"
    log = out_dir / f"screen-{stamp}.log"
    recorder = subprocess.Popen([scrcpy, "--no-audio", "--max-size=2400", f"--record={video}"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    hold = None
    real = []
    try:
        deadline = time.monotonic() + 15
        while not video.exists() or video.stat().st_size == 0:
            if recorder.poll() is not None:
                raise RuntimeError("scrcpy exited before recording started")
            if time.monotonic() >= deadline:
                raise RuntimeError("scrcpy did not start recording within 15 seconds")
            time.sleep(0.05)
        zero = time.monotonic()
        for name, at, cmd in events:
            while time.monotonic() - zero < at:
                if recorder.poll() is not None:
                    raise RuntimeError("scrcpy stopped during recording")
                time.sleep(0.005)
            actual = time.monotonic() - zero
            if name == "ptt_down":
                hold = subprocess.Popen([adb, *cmd], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            else:
                subprocess.run([adb, *cmd], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            real.append((name, at, actual))
        while time.monotonic() - zero < cutoff:
            if recorder.poll() is not None:
                raise RuntimeError("scrcpy stopped during PTT hold")
            time.sleep(0.005)
        recorder.terminate()
        recorder.wait(timeout=10)
        stopped = time.monotonic() - zero
        if hold:
            hold.wait(timeout=15)
            released = time.monotonic() - zero
            if hold.returncode:
                raise RuntimeError("ADB PTT hold failed")
        with log.open("w", encoding="utf-8") as f:
            f.write("seconds from scrcpy recording ready; timing file is relative to over-shoulder clip\n")
            for name, planned, actual in real:
                f.write(f"{name} planned={planned:.3f} actual={actual:.3f}\n")
            f.write(f"recording_stopped actual={stopped:.3f}\n")
            f.write(f"ptt_up planned={taps['ptt_up']['time']:.3f} actual={released:.3f} (after recording stopped)\n")
        print(video)
        print(log)
    finally:
        if recorder.poll() is None:
            recorder.terminate()
            recorder.wait(timeout=10)
        if hold and hold.poll() is None:
            hold.wait(timeout=15)


if __name__ == "__main__":
    main()
