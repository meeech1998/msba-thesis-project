"""
recolor_figures.py
Pixel-level recoloring of existing figures to a color-blind-safe Tableau palette.

Preserves layout, text, anti-aliasing, and data exactly — only shifts the dominant
data colors (reds, blues, greens, ambers) into the Tableau CB-safe palette.

Mapping (by hue family of the input pixel):
  Red          -> #E15759 (Tableau red-orange, CB-safe)
  Orange/Amber -> #F28E2B (Tableau orange)
  Yellow/Gold  -> #EDC948 (Tableau gold)
  Green        -> #76B7B2 (Tableau teal)
  Blue         -> #4E79A7 (Tableau blue)
  Purple       -> #A78BFA (Tableau purple)
Grayscale / near-white / near-black pixels are preserved untouched.
"""
import colorsys
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image


# ── Project CB-safe target colors (semantic palette) ──
# Reds in source figures encode severity/warning, which maps to orange #F28E2B.
TARGETS = {
    "red":    (0xF2, 0x8E, 0x2B),  # red → ORANGE (severity/warning)
    "orange": (0xF2, 0x8E, 0x2B),  # orange/amber stays orange
    "gold":   (0xED, 0xC9, 0x48),
    "teal":   (0x59, 0xA8, 0x9E),
    "blue":   (0x4E, 0x79, 0xA7),
    "purple": (0x7F, 0x77, 0xDD),
}

# Hue ranges in [0, 1)
HUE_BINS = [
    # (hue_lo, hue_hi, target_key)
    (0.95, 1.00, "red"),
    (0.00, 0.04, "red"),       # ~0–14°  (red)
    (0.04, 0.13, "orange"),    # ~14–47° (orange / amber)
    (0.13, 0.19, "gold"),      # ~47–68° (yellow / gold)
    (0.19, 0.45, "teal"),      # ~68–162° (green) — remap to teal
    (0.45, 0.72, "blue"),      # ~162–259° (cyan/blue)
    (0.72, 0.85, "purple"),    # ~259–306° (purple)
    (0.85, 0.95, "red"),       # magenta → red family
]


def target_rgb_for_hue(h: float) -> tuple[int, int, int]:
    for lo, hi, key in HUE_BINS:
        if lo <= h < hi:
            return TARGETS[key]
    return TARGETS["blue"]


def recolor_pixel(r: int, g: int, b: int) -> tuple[int, int, int]:
    """
    Recolor a single RGB pixel.
    Pixels close to grayscale or extremes (white/black/near-gray) are left alone
    so axes, text, gridlines, and backgrounds are preserved.
    """
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)

    # Skip near-grayscale, near-white, near-black: preserve text, axes, gridlines.
    if s < 0.18 or l < 0.08 or l > 0.95:
        return r, g, b

    tr, tg, tb = target_rgb_for_hue(h)
    th, tl, ts = colorsys.rgb_to_hls(tr / 255.0, tg / 255.0, tb / 255.0)

    # Preserve the source pixel's lightness so anti-aliased edges keep their gradient.
    nr, ng, nb = colorsys.hls_to_rgb(th, l, ts)
    return int(round(nr * 255)), int(round(ng * 255)), int(round(nb * 255))


def recolor_image(in_path: Path, out_path: Path) -> None:
    img = Image.open(in_path).convert("RGBA")
    arr = np.array(img)
    rgb = arr[..., :3].astype(np.float32) / 255.0
    alpha = arr[..., 3:4]

    # Vectorised RGB->HLS
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    cmax = np.max(rgb, axis=-1)
    cmin = np.min(rgb, axis=-1)
    delta = cmax - cmin
    L = (cmax + cmin) / 2.0

    S = np.zeros_like(L)
    nz = delta > 0
    S[nz] = np.where(L[nz] < 0.5,
                     delta[nz] / (cmax[nz] + cmin[nz] + 1e-12),
                     delta[nz] / (2.0 - cmax[nz] - cmin[nz] + 1e-12))

    H = np.zeros_like(L)
    safe = delta > 0
    rc = np.where(safe, (cmax - r) / (delta + 1e-12), 0.0)
    gc = np.where(safe, (cmax - g) / (delta + 1e-12), 0.0)
    bc = np.where(safe, (cmax - b) / (delta + 1e-12), 0.0)
    H = np.where(r == cmax, bc - gc, H)
    H = np.where(g == cmax, 2.0 + rc - bc, H)
    H = np.where(b == cmax, 4.0 + gc - rc, H)
    H = (H / 6.0) % 1.0
    H[~safe] = 0.0

    # Mask: which pixels to recolor (skip grayscale / near-white / near-black)
    mask = (S >= 0.18) & (L >= 0.08) & (L <= 0.95)

    # For masked pixels, look up target hue & saturation by hue bin.
    target_h = np.zeros_like(H)
    target_s = np.zeros_like(H)
    for lo, hi, key in HUE_BINS:
        tr, tg, tb = TARGETS[key]
        th, tl, ts = colorsys.rgb_to_hls(tr / 255.0, tg / 255.0, tb / 255.0)
        sel = (H >= lo) & (H < hi)
        target_h[sel] = th
        target_s[sel] = ts

    # Compose new HLS = (target_h, original L, target_s)  -> RGB
    new_h = np.where(mask, target_h, H)
    new_s = np.where(mask, target_s, S)

    # HLS -> RGB (vectorised)
    def hue_to_rgb(p, q, t):
        t = t % 1.0
        result = np.where(t < 1/6, p + (q - p) * 6 * t,
                 np.where(t < 1/2, q,
                 np.where(t < 2/3, p + (q - p) * (2/3 - t) * 6, p)))
        return result

    q = np.where(L < 0.5, L * (1 + new_s), L + new_s - L * new_s)
    p = 2 * L - q
    r2 = hue_to_rgb(p, q, new_h + 1/3)
    g2 = hue_to_rgb(p, q, new_h)
    b2 = hue_to_rgb(p, q, new_h - 1/3)

    # Where saturation is 0 (grayscale), HLS->RGB should equal L.
    zero_s = new_s < 1e-6
    r2 = np.where(zero_s, L, r2)
    g2 = np.where(zero_s, L, g2)
    b2 = np.where(zero_s, L, b2)

    out = np.stack([r2, g2, b2], axis=-1)
    out = np.clip(out * 255.0, 0, 255).astype(np.uint8)
    out = np.concatenate([out, alpha], axis=-1)

    Image.fromarray(out, mode="RGBA").save(out_path)


def main():
    if len(sys.argv) >= 3:
        src_dir = Path(sys.argv[1])
        dst_dir = Path(sys.argv[2])
    else:
        project_root = Path(__file__).resolve().parent.parent
        src_dir = project_root / "outputs" / "figures" / "original"
        dst_dir = project_root / "outputs" / "figures" / "cb_safe"

    dst_dir.mkdir(parents=True, exist_ok=True)
    pngs = sorted(src_dir.glob("*.png"))
    print(f"Recoloring {len(pngs)} files: {src_dir} -> {dst_dir}")
    for p in pngs:
        recolor_image(p, dst_dir / p.name)
        print(f"  ✓ {p.name}")


if __name__ == "__main__":
    main()
