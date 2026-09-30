"""Build the closing card. Run from anywhere: python film/title/build.py."""
from pathlib import Path

DISTANCE = "~400 m"

HERE = Path(__file__).resolve().parent
template = (HERE / "index.html.tpl").read_text(encoding="utf-8")
if template.count("{DISTANCE}") != 1:
    raise ValueError("Expected exactly one {DISTANCE} placeholder")
(HERE / "index.html").write_text(template.replace("{DISTANCE}", DISTANCE), encoding="utf-8")
print(f"Built title card with distance {DISTANCE}")
