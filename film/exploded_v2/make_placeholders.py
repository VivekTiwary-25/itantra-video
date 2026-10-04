"""Write PLACEHOLDER layers for the exploded view until F0030's real images exist.

    python film/exploded_v2/make_placeholders.py [--force]

Writes RENDERS:exploded_v2/layer_screen.png, layer_mid.png, layer_back.png (2048 x 2048, transparent) and
RENDERS:exploded_v2/parts_placeholder.json, in the same format build.py reads from results/F0030/parts.json.
Simple grey shapes sheared into a rough three-quarter view, only so the motion and layout can be judged.
Never overwrites a real layer unless --force is given.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = Path(json.loads((REPO / "machine.local.json").read_text(encoding="utf-8"))["renders_dir"]) / "exploded_v2"
OUT.mkdir(parents=True, exist_ok=True)
N = 2048
# phone body in "flat" coordinates (portrait), then a shear + squash fakes a 3/4 top view
X0, Y0, X1, Y1 = 724, 324, 1324, 1724          # 600 x 1400 px
SHEAR, SQUASH = 0.38, 0.78                     # x += SHEAR * (y - cy); y squashed around cy
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2


def warp(x, y):
    return x + SHEAR * (y - CY), CY + (y - CY) * SQUASH


def flat_canvas():
    return Image.new("RGBA", (N, N), (0, 0, 0, 0))


def finish(img):
    # inverse affine for PIL: output (u,v) -> input (x,y)
    # v = CY + (y-CY)*SQUASH  -> y = CY + (v-CY)/SQUASH ; u = x + SHEAR*(y-CY) -> x = u - SHEAR*(y-CY)
    a = 1 / SQUASH
    coeffs = (1, -SHEAR * a, SHEAR * a * CY - SHEAR * a * CY + 0,  # x = u - SHEAR*a*(v-CY)
              0, a, CY - a * CY)
    coeffs = (1, -SHEAR * a, SHEAR * a * CY, 0, a, CY - a * CY)
    return img.transform((N, N), Image.AFFINE, coeffs, resample=Image.BICUBIC)


def rr(d, box, r, **kw):
    d.rounded_rectangle(box, radius=r, **kw)


def screen():
    img = flat_canvas(); d = ImageDraw.Draw(img)
    rr(d, (X0, Y0, X1, Y1), 70, fill=(18, 20, 24, 255), outline=(120, 128, 140, 255), width=6)
    rr(d, (X0 + 18, Y0 + 18, X1 - 18, Y1 - 18), 56, fill=(6, 8, 11, 255))
    d.ellipse((CX - 16, Y0 + 44, CX + 16, Y0 + 76), fill=(30, 33, 38, 255))
    sheen = Image.new("RGBA", (N, N), (0, 0, 0, 0)); s = ImageDraw.Draw(sheen)
    s.polygon([(X0 + 40, Y0 + 40), (X0 + 260, Y0 + 40), (X0 + 40, Y0 + 520)], fill=(255, 255, 255, 34))
    img = Image.alpha_composite(img, sheen.filter(ImageFilter.GaussianBlur(18)))
    return finish(img)


PARTS_FLAT = {
    "microphone": (CX - 150, Y1 - 34, 22, 14),
    "processor": (CX + 20, Y0 + 420, 150, 150),
    "bluetooth_chip": (CX + 170, Y0 + 230, 70, 56),
    "antenna": (X1 - 40, Y0 + 150, 10, 10),
    "loudspeaker": (CX + 120, Y1 - 120, 220, 70),
    "battery": (CX, Y0 + 960, 440, 560),
}


def mid():
    img = flat_canvas(); d = ImageDraw.Draw(img)
    rr(d, (X0, Y0, X1, Y1), 70, fill=(150, 156, 162, 255), outline=(205, 210, 214, 255), width=8)
    rr(d, (X0 + 30, Y0 + 30, X1 - 30, Y1 - 30), 50, fill=(72, 78, 84, 255))
    rr(d, (X0 + 50, Y0 + 60, X1 - 50, Y0 + 640), 26, fill=(28, 84, 52, 255))            # board
    for name, (cx, cy, w, h) in PARTS_FLAT.items():
        box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
        if name == "processor":
            rr(d, box, 10, fill=(170, 176, 182, 255), outline=(220, 224, 228, 255), width=4)
        elif name == "bluetooth_chip":
            rr(d, box, 6, fill=(30, 32, 36, 255), outline=(200, 170, 90, 255), width=3)
        elif name == "battery":
            rr(d, box, 24, fill=(40, 44, 50, 255), outline=(110, 116, 124, 255), width=4)
        elif name == "loudspeaker":
            rr(d, box, 16, fill=(24, 26, 30, 255))
            for k in range(9):
                x = box[0] + 20 + k * 22
                d.ellipse((x - 5, cy - 5, x + 5, cy + 5), fill=(70, 74, 80, 255))
        elif name == "microphone":
            d.ellipse(box, fill=(10, 10, 12, 255))
    d.line([(X1 - 40, Y0 + 70), (X1 - 40, Y0 + 300), (CX + 210, Y0 + 300)], fill=(200, 170, 90, 255), width=5)
    return finish(img)


def back():
    img = flat_canvas(); d = ImageDraw.Draw(img)
    rr(d, (X0, Y0, X1, Y1), 70, fill=(52, 55, 60, 255), outline=(96, 100, 108, 255), width=6)
    rr(d, (X0 + 60, Y0 + 60, X0 + 300, Y0 + 360), 46, fill=(38, 40, 44, 255), outline=(90, 94, 100, 255), width=5)
    for k, (x, y) in enumerate(((X0 + 130, Y0 + 140), (X0 + 230, Y0 + 140), (X0 + 130, Y0 + 270))):
        d.ellipse((x - 38, y - 38, x + 38, y + 38), fill=(14, 15, 18, 255), outline=(120, 124, 130, 255), width=4)
    return finish(img)


def main():
    force = "--force" in sys.argv
    for name, fn in (("layer_screen.png", screen), ("layer_mid.png", mid), ("layer_back.png", back)):
        p = OUT / name
        if p.exists() and not force:
            print(f"kept existing {name}")
            continue
        fn().save(p)
        print(f"wrote PLACEHOLDER RENDERS:exploded_v2/{name}")
    parts = {}
    for name, (cx, cy, w, h) in PARTS_FLAT.items():
        corners = [warp(cx + sx * w / 2, cy + sy * h / 2) for sx in (-1, 1) for sy in (-1, 1)]
        xs, ys = [c[0] for c in corners], [c[1] for c in corners]
        c = warp(cx, cy)
        parts[name] = {"center": [round(c[0]), round(c[1])],
                       "bbox": [round(min(xs)), round(min(ys)), round(max(xs) - min(xs)), round(max(ys) - min(ys))]}
    (OUT / "parts_placeholder.json").write_text(json.dumps({"image": "layer_mid.png", "size": [N, N],
                                                          "placeholder": True, "parts": parts}, indent=2),
                                                encoding="utf-8")
    print("wrote RENDERS:exploded_v2/parts_placeholder.json")


if __name__ == "__main__":
    main()
