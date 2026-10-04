"""Prepare only local, licensed assets for the exploded-view composition."""
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ASSETS = HERE / "assets"
GLASS = ASSETS / "glass"
GLASS.mkdir(parents=True, exist_ok=True)

for source, target in (
    (REPO / "film/vendor/three/three.min.js", HERE / "three.min.js"),
    (REPO / "film/vendor/gsap/gsap.min.js", HERE / "gsap.min.js"),
    (REPO / "film/common/glass/glass.css", GLASS / "glass.css"),
    (REPO / "film/common/glass/glass.js", GLASS / "glass.js"),
    (REPO / "film/common/glass/noise.png", GLASS / "noise.png"),
):
    shutil.copyfile(source, target)

private_screen = REPO / "local/private-in/F0007/home.png"
screen = ASSETS / "home.png"
if private_screen.exists():
    shutil.copyfile(private_screen, screen)
    print("Private home screen prepared locally (ignored by Git).")
else:
    screen.unlink(missing_ok=True)
    print("No private home screen found; composition uses a neutral dark screen.")

