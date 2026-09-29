"""manifest.py - extract footage zips (never deleting them) and write machines/<machine>/footage-manifest.json.

Zips are extracted next to themselves, keeping the paths inside the zip, so the relative paths in the
manifest are the same on every machine no matter what the zips were called when downloaded.
A zip whose files are not all inside one top-level folder is extracted into a folder named after the zip
(minus Google Drive's "-2026...Z-1-001" suffix).

Usage: python tools/manifest.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import AUDIO_EXT, MEDIA_EXT, REPO_ROOT, load_machine_config, now_iso, run, which, write_json  # noqa: E402

DRIVE_SUFFIX = re.compile(r"-\d{8}T\d{6}Z-\d+-\d+$")
HDR_TRANSFERS = {"smpte2084", "arib-std-b67"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_zip(zpath: Path, log: list[str]) -> None:
    with zipfile.ZipFile(zpath) as z:
        entries = [i for i in z.infolist() if not i.is_dir()]
        tops = {PurePosixPath(i.filename).parts[0] for i in entries if len(PurePosixPath(i.filename).parts) > 1}
        single_top = len(tops) == 1 and all(len(PurePosixPath(i.filename).parts) > 1 for i in entries)
        base = zpath.parent if single_top else zpath.parent / DRIVE_SUFFIX.sub("", zpath.stem)
        done = skipped = 0
        for info in entries:
            rel = PurePosixPath(info.filename)
            if rel.is_absolute() or ".." in rel.parts:
                log.append(f"skipped unsafe path in {zpath.name}: {info.filename}")
                continue
            target = base.joinpath(*rel.parts)
            if target.exists() and target.stat().st_size == info.file_size:
                skipped += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, open(target, "wb") as dst:
                while chunk := src.read(1024 * 1024):
                    dst.write(chunk)
            done += 1
        log.append(f"{zpath.name}: extracted {done}, already present {skipped}")


def probe(ffprobe: str, path: Path) -> dict:
    code, out = run([ffprobe, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)], timeout=120)
    if code != 0:
        return {"error": out.strip()[:300]}
    try:
        data = json.loads(out)
    except ValueError:
        return {"error": "ffprobe returned bad JSON"}
    streams = []
    hdr = False
    for s in data.get("streams", []):
        item = {"type": s.get("codec_type"), "codec": s.get("codec_name")}
        if s.get("codec_type") == "video":
            item.update(width=s.get("width"), height=s.get("height"), fps=s.get("avg_frame_rate"),
                        pix_fmt=s.get("pix_fmt"), color_transfer=s.get("color_transfer"),
                        color_primaries=s.get("color_primaries"), color_space=s.get("color_space"))
            if s.get("color_transfer") in HDR_TRANSFERS:
                hdr = True
            rot = next((sd.get("rotation") for sd in s.get("side_data_list", []) if "rotation" in sd), None)
            if rot is not None:
                item["rotation"] = rot
        elif s.get("codec_type") == "audio":
            item.update(sample_rate=s.get("sample_rate"), channels=s.get("channels"))
        streams.append(item)
    dur = data.get("format", {}).get("duration")
    return {"duration_s": round(float(dur), 3) if dur else None, "streams": streams, "hdr": hdr}


def pair_key(rel: str) -> str:
    """'sih video clip/Normalpart6.mp4' and 'sih audio clips/normalpart6.mp3' both give 'normalpart6'."""
    return PurePosixPath(rel).stem.lower().strip()


def main() -> None:
    cfg = load_machine_config()
    machine = cfg["machine"]
    root = Path(cfg["footage_root"])
    if not root.is_dir():
        sys.exit(f"footage_root does not exist: {root}")
    ffprobe = which("ffprobe")
    if not ffprobe:
        sys.exit("ffprobe not found. Run tools/doctor.py for install hints.")

    log: list[str] = []
    zips = sorted(root.rglob("*.zip"), key=lambda p: p.name.lower())
    for z in zips:
        print(f"Checking {z.name} ...")
        extract_zip(z, log)

    files, archives = [], []
    for p in sorted(root.rglob("*"), key=lambda p: str(p).lower()):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if p.suffix.lower() == ".zip":
            archives.append({"path": rel, "size": p.stat().st_size, "sha256": sha256(p)})
            continue
        if p.suffix.lower() not in MEDIA_EXT:
            continue
        print(f"  scanning {rel}")
        entry = {"path": rel, "kind": "audio" if p.suffix.lower() in AUDIO_EXT else "video",
                 "size": p.stat().st_size, "sha256": sha256(p)}
        entry.update(probe(ffprobe, p))
        files.append(entry)

    videos = {pair_key(f["path"]): f["path"] for f in files if f["kind"] == "video"}
    audios = {pair_key(f["path"]): f["path"] for f in files if f["kind"] == "audio"}
    pairs = {k: {"video": videos.get(k), "audio": audios.get(k)} for k in sorted(set(videos) | set(audios))}

    total = round(sum(f.get("duration_s") or 0 for f in files), 3)
    manifest = {
        "machine": machine,
        "generated_at": now_iso(),
        "summary": {
            "file_count": len(files),
            "video_files": sum(f["kind"] == "video" for f in files),
            "audio_files": sum(f["kind"] == "audio" for f in files),
            "total_duration_s": total,
            "hdr_files": [f["path"] for f in files if f.get("hdr")],
            "errors": [f["path"] for f in files if "error" in f],
            "video_without_audio": [k for k, v in pairs.items() if v["video"] and not v["audio"]],
            "audio_without_video": [k for k, v in pairs.items() if v["audio"] and not v["video"]],
        },
        "pairs": pairs,
        "files": files,
        "archives": archives,
        "extraction_log": log,
    }
    out = REPO_ROOT / "machines" / machine / "footage-manifest.json"
    write_json(out, manifest)
    s = manifest["summary"]
    print(f"\nWrote {out}")
    print(f"{s['file_count']} media files ({s['video_files']} video, {s['audio_files']} audio), total {total} s ({total / 60:.1f} min)")
    print(f"HDR files: {s['hdr_files'] or 'none'}")
    print(f"Videos with no matching audio: {s['video_without_audio'] or 'none'}")
    print(f"Audio with no matching video: {s['audio_without_video'] or 'none'}")
    if s["errors"]:
        print(f"ffprobe errors: {s['errors']}")


if __name__ == "__main__":
    main()
