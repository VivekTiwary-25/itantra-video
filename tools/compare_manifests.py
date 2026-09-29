"""compare_manifests.py - compare every machine's footage manifest by path + size + sha256.

Reads machines/*/footage-manifest.json (run `git pull` first). Paths must be exactly
Video/<name> and Audio/<name> with the original file names. How the files arrived (zip or by hand) does not matter.
Prints every difference. Exit code 0 = all machines identical, 1 = differences or a machine is missing.

Usage: python tools/compare_manifests.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO_ROOT, read_json  # noqa: E402


def main() -> int:
    reg = read_json(REPO_ROOT / "machines" / "registry.json", {})
    machines = {}
    missing = []
    for m in reg.get("machines", {}):
        man = read_json(REPO_ROOT / "machines" / m / "footage-manifest.json")
        if not man:
            missing.append(m)
            continue
        machines[m] = {f["path"]: (f["size"], f["sha256"]) for f in man.get("files", [])}
        warns = man.get("summary", {}).get("layout_warnings") or []
        if warns:
            print(f"[{m}] layout warnings: {warns}")
    if missing:
        print("No manifest yet from:", ", ".join(missing))
    if len(machines) < 2:
        print("Need at least two manifests to compare.")
        return 1

    names = sorted(machines)
    ref = names[0]
    print(f"Comparing {', '.join(names)} (reference: {ref})")
    problems = 0
    for path in sorted(set().union(*[set(v) for v in machines.values()])):
        vals = {m: machines[m].get(path) for m in names}
        if len(set(vals.values())) == 1 and vals[ref] is not None:
            continue
        problems += 1
        print(f"\nDIFFERENT: {path}")
        for m in names:
            v = vals[m]
            print(f"  {m:<12} " + ("MISSING" if v is None else f"size {v[0]}  sha256 {v[1][:16]}..."))
    total = len(set().union(*[set(v) for v in machines.values()]))
    if problems == 0 and not missing:
        print(f"\nAll {len(names)} machines are identical: {total} files, same paths, sizes and sha256.")
        return 0
    print(f"\n{problems} file(s) differ across machines" + (f"; {len(missing)} machine(s) have no manifest yet" if missing else "") + ".")
    return 1


if __name__ == "__main__":
    sys.exit(main())
