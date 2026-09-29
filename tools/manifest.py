"""manifest.py - make sure the footage is in the standard layout, then write machines/<machine>/footage-manifest.json.

THE LAYOUT (same on every machine). footage_root contains exactly two folders, with the original file names:
    Video/   the .mp4 clips
    Audio/   the .mp3 files
Clip paths in tasks are therefore always FOOTAGE:Video/<name> or FOOTAGE:Audio/<name>.
Machines are compared by these paths plus sha256, not by how the files arrived.

If .zip files are sitting in footage_root, their media files are unpacked straight into Video/ and Audio/
(any folder names inside the zip are dropped; the zips are never deleted or changed). If you downloaded the
folders by hand from Drive, there is nothing to unpack and this just scans them.

Usage: python tools/manifest.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import AUDIO_EXT, MEDIA_EXT, REPO_ROOT, load_machine_config, now_iso, run, which, write_json  # noqa: E402

HDR_TRANSFERS = {"smpte2084", "arib-std-b67"}
FOLDERS = {"Video": "video", "Audio": "audio"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def target_folder(name: str) -> str | None:
    ext = PurePosixPath(name).suffix.lower()
    if ext not in MEDIA_EXT:
        return None
    return "Audio" if ext in AUDIO_EXT else "Video"


def extract_zip(zpath: Path, root: Path, log: list[str]) -> None:
    """Unpack the media files of one zip into root/Video and root/Audio, keeping the original file names."""
    done = skipped = ignored = 0
    with zipfile.ZipFile(zpath) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            rel = PurePosixPath(info.filename)
            if rel.is_absolute() or ".." in rel.parts:
                log.append(f"skipped unsafe path in {zpath.name}: {info.filename}")
                continue
            folder = target_folder(rel.name)
            if folder is None:
                ignored += 1
                continue
            target = root / folder / rel.name
            # Windows file names are case-insensitive: an existing Normalpart6.mp3 counts as present.
            if target.exists() and target.stat().st_size == info.file_size:
                skipped += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, open(target, "wb") as dst:
                while chunk := src.read(1024 * 1024):
                    dst.write(chunk)
            done += 1
    log.append(f"{zpath.name}: unpacked {done}, already present {skipped}, non-media ignored {ignored}")


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
    """'Video/Normalpart6.mp4' and 'Audio/normalpart6.mp3' both give 'normalpart6' (names match ignoring case)."""
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
    warnings: list[str] = []
    zips = sorted(root.glob("*.zip"), key=lambda p: p.name.lower())
    for z in zips:
        print(f"Checking {z.name} ...")
        extract_zip(z, root, log)

    # Layout check: exactly Audio/ and Video/ (zips may sit beside them).
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if child.is_dir() and child.name not in FOLDERS:
            warnings.append(f"unexpected folder in footage_root (not part of the standard layout, not scanned): {child.name}")
        elif child.is_file() and child.suffix.lower() in MEDIA_EXT:
            warnings.append(f"media file loose in footage_root (should be in Video/ or Audio/, not scanned): {child.name}")
    for folder in FOLDERS:
        if not (root / folder).is_dir():
            warnings.append(f"missing folder: {folder}/")

    files = []
    for folder, kind in FOLDERS.items():
        d = root / folder
        if not d.is_dir():
            continue
        for p in sorted(d.iterdir(), key=lambda p: p.name.lower()):
            if p.is_dir():
                warnings.append(f"subfolder inside {folder}/ (not scanned): {p.name}")
                continue
            if p.suffix.lower() not in MEDIA_EXT:
                warnings.append(f"non-media file in {folder}/ (ignored): {p.name}")
                continue
            if target_folder(p.name) != folder:
                warnings.append(f"{folder}/{p.name} looks like it belongs in {target_folder(p.name)}/")
            rel = f"{folder}/{p.name}"
            print(f"  scanning {rel}")
            entry = {"path": rel, "kind": kind, "size": p.stat().st_size, "sha256": sha256(p)}
            entry.update(probe(ffprobe, p))
            files.append(entry)

    archives = [{"path": z.name, "size": z.stat().st_size, "sha256": sha256(z)} for z in zips]

    videos = {pair_key(f["path"]): f["path"] for f in files if f["kind"] == "video"}
    audios = {pair_key(f["path"]): f["path"] for f in files if f["kind"] == "audio"}
    pairs = {k: {"video": videos.get(k), "audio": audios.get(k)} for k in sorted(set(videos) | set(audios))}

    total = round(sum(f.get("duration_s") or 0 for f in files), 3)
    manifest = {
        "machine": machine,
        "generated_at": now_iso(),
        "layout": "footage_root/Video/<name> and footage_root/Audio/<name>; compare machines by path + sha256",
        "summary": {
            "file_count": len(files),
            "video_files": sum(f["kind"] == "video" for f in files),
            "audio_files": sum(f["kind"] == "audio" for f in files),
            "total_duration_s": total,
            "hdr_files": [f["path"] for f in files if f.get("hdr")],
            "errors": [f["path"] for f in files if "error" in f],
            "video_without_audio": [k for k, v in pairs.items() if v["video"] and not v["audio"]],
            "audio_without_video": [k for k, v in pairs.items() if v["audio"] and not v["video"]],
            "layout_warnings": warnings,
        },
        "pairs": pairs,
        "files": files,
        "archives_info_only": archives,
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
    if warnings:
        print("LAYOUT WARNINGS (fix these so every machine matches):")
        for w in warnings:
            print("  -", w)
    else:
        print("Layout OK: exactly Video/ and Audio/.")


if __name__ == "__main__":
    main()
