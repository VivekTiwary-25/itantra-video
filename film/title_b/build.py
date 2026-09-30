"""Build title option B. Run: python film/title_b/build.py [distance]."""
from pathlib import Path
import sys

DISTANCE = "~400 m"

here = Path(__file__).resolve().parent
distance = sys.argv[1] if len(sys.argv) > 1 else DISTANCE
if not distance.strip():
    raise ValueError("Distance must not be empty")
template = (here / "index.html.tpl").read_text(encoding="utf-8")
if template.count("{DISTANCE}") != 1:
    raise ValueError("Expected exactly one {DISTANCE} placeholder")
(here / "index.html").write_text(template.replace("{DISTANCE}", distance), encoding="utf-8")
print(f"Built title option B with distance {distance}")
