#!/usr/bin/env python3
"""Generate the animated splain logo GIF from the static PNG.

    python3 scripts/make-splain-logo-gif.py

Reads  content/software/splain/splain_logo.png  (818x904 RGBA hex logo) and
writes content/software/splain/splain_logo.gif. Needs Pillow, numpy and scipy.

Animation (3 s loop): the frog + magnifier bob gently, the highlighted (orange)
exon in the top isoform and the square inside the lens pulse together, and the
frog blinks once. Element coordinates are found from the PNG's colours, so the
script only assumes the logo's layout, not exact pixel positions.
"""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "content/software/splain/splain_logo.png"
OUT = ROOT / "content/software/splain/splain_logo.gif"

OUT_WIDTH = 300          # card logo is 130 CSS px; 300 keeps it sharp on retina
FRAMES = 60
FRAME_MS = 50
# Source pixels shrink ~6x at the 130px card size, so keep these generous.
BOB_PX = 22              # how far the frog/magnifier rise (source pixels, upward only)
EXON_PULSE = 0.26        # max extra scale of the highlighted exon
LENS_PULSE = 0.10        # max extra scale of the square in the lens
BLINK = (0.70, 0.82)     # fraction of the loop the eyes are closed

MINT = (201, 247, 224, 255)
NAVY = (6, 0, 69, 255)
ORANGE = (255, 178, 2, 255)
SS = 4                   # supersampling for redrawn shapes


def components(mask):
    lab, _ = ndimage.label(mask)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        out.append((sl, lab == i))
    return out


def bbox(sl):
    ys, xs = sl
    return xs.start, ys.start, xs.stop, ys.stop


def aa_shape(size, draw_fn):
    """Draw a shape supersampled and return an antialiased RGBA layer."""
    w, h = size
    big = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(big), SS)
    return big.resize((w, h), Image.LANCZOS)


def rounded_rect_layer(size, box, radius, color):
    x0, y0, x1, y1 = box
    return aa_shape(size, lambda d, s: d.rounded_rectangle(
        (x0 * s, y0 * s, x1 * s, y1 * s), radius=radius * s, fill=color))


def scaled_box(box, k):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hw, hh = (x1 - x0) / 2 * k, (y1 - y0) / 2 * k
    return cx - hw, cy - hh, cx + hw, cy + hh


def main():
    base = Image.open(SRC).convert("RGBA")
    arr = np.array(base)
    W, H = base.size

    # --- locate elements -------------------------------------------------
    orange = (arr[..., 0] > 200) & (arr[..., 1] > 140) & (arr[..., 1] < 210) & (arr[..., 2] < 80)
    oranges = sorted(components(orange), key=lambda c: bbox(c[0])[1])
    lens_sq, exon = bbox(oranges[0][0]), bbox(oranges[1][0])   # upper = lens, lower = exon

    dark = (arr[..., 0] < 60) & (arr[..., 2] > 30) & (arr[..., 3] > 128)
    darks = [c for c in components(dark) if c[1].sum() > 300]
    # pupils: small, roughly square blobs just above the lens square
    pupils = [c for c in darks
              if 25 < bbox(c[0])[2] - bbox(c[0])[0] < 50
              and 25 < bbox(c[0])[3] - bbox(c[0])[1] < 50
              and bbox(c[0])[3] < lens_sq[1]]
    pupils = sorted(pupils, key=lambda c: c[1].sum(), reverse=True)[:2]
    assert len(pupils) == 2, "could not find the frog's eyes"

    # frog + magnifier group: everything dark between the title and the exon rows
    group_top = min(bbox(p[0])[1] for p in pupils) - 40
    group_bot = exon[1] - 12
    border = max(darks, key=lambda c: c[1].sum())[1]          # the hexagon outline
    inner = dark & ~border
    group_cols = np.nonzero(inner[group_top:group_bot].any(axis=0))[0]
    group_box = (int(group_cols.min()) - 8, group_top, int(group_cols.max()) + 8, group_bot)

    # --- static pieces ---------------------------------------------------
    # background with the frog/magnifier group removed
    bg = base.copy()
    bg.paste(Image.new("RGBA", (group_box[2] - group_box[0], group_box[3] - group_box[1]), MINT),
             group_box[:2])
    group = base.crop(group_box)

    # closed-eye version of the group: erase pupils, draw a short lid line
    group_closed = group.copy()
    ga = np.array(group_closed)
    lids = []
    for sl, m in pupils:
        m = ndimage.binary_dilation(m, iterations=3)
        gx0, gy0 = group_box[:2]
        sub = m[gy0:group_box[3], gx0:group_box[2]]
        ga[sub] = MINT
        x0, y0, x1, y1 = bbox(sl)
        lids.append((x0 - gx0, y0 - gy0, x1 - gx0, y1 - gy0))
    group_closed = Image.fromarray(ga)

    def lid_draw(d, s):
        for x0, y0, x1, y1 in lids:
            cy = (y0 + y1) / 2 + 4
            t = 8
            d.rounded_rectangle(((x0 - 2) * s, (cy - t / 2) * s, (x1 + 2) * s, (cy + t / 2) * s),
                                radius=t / 2 * s, fill=NAVY)
    group_closed.alpha_composite(aa_shape(group_closed.size, lid_draw))

    exon_r = 0.18 * (exon[3] - exon[1])
    lens_r = 0.15 * (lens_sq[3] - lens_sq[1])

    # --- frames ----------------------------------------------------------
    frames = []
    for i in range(FRAMES):
        t = i / FRAMES
        pulse = 0.5 - 0.5 * math.cos(2 * math.pi * t)          # 0 -> 1 -> 0
        dy = round(-BOB_PX * pulse)       # rise while the exon grows (never moves down)
        closed = BLINK[0] <= t < BLINK[1]

        g = (group_closed if closed else group).copy()
        lsq = tuple(v - o for v, o in zip(lens_sq, group_box[:2] * 2))
        g.alpha_composite(rounded_rect_layer(g.size, scaled_box(lsq, 1 + LENS_PULSE * pulse),
                                             lens_r, ORANGE))
        # make the group's plain background transparent so the shifted layer
        # never paints a mint rectangle over the title or the exon rows
        ga = np.array(g)
        ga[(ga[..., :3] == MINT[:3]).all(-1)] = (0, 0, 0, 0)
        g = Image.fromarray(ga)

        f = bg.copy()
        f.alpha_composite(g, (group_box[0], group_box[1] + dy))
        f.alpha_composite(rounded_rect_layer((W, H), scaled_box(exon, 1 + EXON_PULSE * pulse),
                                             exon_r, ORANGE))
        frames.append(f.resize((OUT_WIDTH, round(H * OUT_WIDTH / W)), Image.LANCZOS))

    # --- GIF encode: shared palette, 1-bit transparency -------------------
    sample = Image.new("RGB", (frames[0].width, frames[0].height * 3))
    for k, f in enumerate(frames[::FRAMES // 3][:3]):
        sample.paste(f.convert("RGB"), (0, k * f.height))
    pal = sample.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    TRANSP = 255
    out = []
    for f in frames:
        p = f.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE)
        pa = np.array(p)
        pa[np.array(f)[..., 3] < 128] = TRANSP
        q = Image.fromarray(pa, "P")
        q.putpalette(pal.getpalette()[:765] + [0, 0, 0])
        out.append(q)
    out[0].save(OUT, save_all=True, append_images=out[1:], duration=FRAME_MS, loop=0,
                transparency=TRANSP, disposal=1, optimize=True)
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
