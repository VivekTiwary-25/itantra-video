"""Regenerate the optional transparent caption compositions and scene SRTs.

Run from the repository root: python film/captions/build.py
Edit captions.json to change caption text, position, or scene timing.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DATA = HERE / "captions.json"
SCENES = ("scene1", "scene2", "scene3")
POSITIONS = {"bottom", "left", "right"}


def srt_time(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    whole_seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{whole_seconds:02},{milliseconds:03}"


def validate(data: dict) -> None:
    if data["fps"] != 30 or data["size"] != [1920, 1080]:
        raise ValueError("Caption compositions must be 1920x1080 at 30 fps")
    durations = data["durations"]
    for scene in SCENES:
        if not 0 < durations[scene]:
            raise ValueError(f"Invalid {scene} duration")
        rows = [r for r in data["captions"] if r["scene"] == scene]
        if not rows:
            raise ValueError(f"No captions for {scene}")
        previous_end = 0.0
        for row in rows:
            start, end = row["start"], row["end"]
            if not 0 <= start < end <= durations[scene]:
                raise ValueError(f"Caption outside {scene}: {row}")
            if start < previous_end - 0.001:
                raise ValueError(f"Overlapping/out-of-order captions in {scene}: {row}")
            previous_end = end
            if row["position"] not in POSITIONS:
                raise ValueError(f"Unknown position: {row}")
            lines = row["text"].split("\n")
            if not 1 <= len(lines) <= 2 or any(not line or len(line) > 42 for line in lines):
                raise ValueError(f"Caption exceeds two lines or 42 characters: {row}")
            if "demo" in row["text"].lower() or "debug" in row["text"].lower():
                raise ValueError(f"Unapproved label in {scene}")
    planned = data["scene3_timing"]
    keys = ("s3_open", "vachana_sos", "sos_in", "sos_sonar", "sos_dive",
            "lab_a", "vivek_sos", "lab_b", "vivek_reply", "vachana_response", "end")
    starts = [planned[key] for key in keys]
    if starts != sorted(starts) or starts[-1] != durations["scene3"]:
        raise ValueError("scene3_timing must increase to the scene3 duration")


def composition_html(scene: str, duration: float, rows: list[dict]) -> str:
    # JSON is embedded in an inline script. Escape the '<' character to keep
    # caption text from ever closing the script tag.
    payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=1920,height=1080">
<script src="./gsap.min.js"></script>
<style>
@font-face{{font-family:CaptionSans;src:local('Segoe UI Variable Display'),local('Segoe UI Variable'),local('Segoe UI');font-weight:100 900}}
*{{box-sizing:border-box}}
html,body{{margin:0;width:1920px;height:1080px;overflow:hidden;background:transparent}}
#root{{position:relative;width:1920px;height:1080px;overflow:hidden;background:transparent}}
#caption{{position:absolute;bottom:42px;left:50%;transform:translateX(-50%);
  max-width:1200px;width:max-content;padding:12px 20px;border-radius:18px;
  color:#f3f5f8;background:rgba(5,7,10,.82);font:600 46px/1.16 CaptionSans,'Segoe UI',sans-serif;
  white-space:pre-line;text-align:center;box-shadow:0 3px 16px rgba(0,0,0,.2);
  visibility:hidden;opacity:0;pointer-events:none}}
#caption.left{{left:42px;right:auto;transform:none;max-width:650px;text-align:left}}
#caption.right{{left:auto;right:42px;transform:none;max-width:650px;text-align:right}}
</style></head><body>
<div id="root" data-composition-id="{scene}_captions" data-start="0" data-duration="{duration}"
  data-width="1920" data-height="1080"><div id="caption" aria-live="off"></div></div>
<script>
const rows={payload};
const caption=document.getElementById('caption');
function render(t){{
  const row=rows.find(r=>t>=r.start&&t<r.end);
  if(!row){{caption.style.visibility='hidden';caption.style.opacity='0';return}}
  caption.className=row.position==='bottom'?'':row.position;
  caption.textContent=row.text;
  caption.style.visibility='visible';
  const alpha=Math.min(1,(t-row.start)/.12,(row.end-t)/.12);
  caption.style.opacity=String(Math.max(0,alpha));
}}
const tl=gsap.timeline({{paused:true,onUpdate:()=>render(tl.time())}});
tl.to({{}},{{duration:{duration}}},0);
window.__timelines=window.__timelines||{{}};
window.__timelines['{scene}_captions']=tl;
window.addEventListener('hf-seek',e=>render(e.detail.time));
render(0);
</script></body></html>
"""


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    validate(data)
    vendor_gsap = REPO / "film/vendor/gsap/gsap.min.js"
    for scene in SCENES:
        folder = HERE / scene
        folder.mkdir(exist_ok=True)
        rows = [r for r in data["captions"] if r["scene"] == scene]
        duration = data["durations"][scene]
        (folder / "index.html").write_text(composition_html(scene, duration, rows), encoding="utf-8")
        (folder / "meta.json").write_text(
            json.dumps({"id": f"{scene}_captions", "name": f"{scene} captions"}, indent=2) + "\n",
            encoding="utf-8",
        )
        (folder / "hyperframes.json").write_text(
            json.dumps({"paths": {"blocks": "compositions", "components": "compositions/components",
                                  "assets": "assets"}, "media": {"autoProxy": False}}, indent=2) + "\n",
            encoding="utf-8",
        )
        shutil.copyfile(vendor_gsap, folder / "gsap.min.js")
        srt = "\n\n".join(
            f"{i}\n{srt_time(row['start'])} --> {srt_time(row['end'])}\n{row['text']}"
            for i, row in enumerate(rows, 1)
        ) + "\n"
        (HERE / f"{scene}.srt").write_text(srt, encoding="utf-8")
        print(f"{scene}: {len(rows)} cues, {duration:.3f} s")


if __name__ == "__main__":
    main()
