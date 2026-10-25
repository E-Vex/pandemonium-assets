#!/usr/bin/env python3
"""D-002: regenerate design/art-bible/scale_chart.png with the corrected
unit widths (rifleman 0.7 tile, raider 0.6 tile — content data A-149 /
report A-016 §9 P1).

Reads the committed role silhouettes from the assets repo, lays every kind
on the tile grid at true relative scale, and downscales to the repo's
2048 px PNG limit. Run from anywhere; paths are absolute.

Usage: python3 regen_scale_chart.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

# assets repo root: override with PANDEMONIUM_ASSETS
REPO = os.environ.get("PANDEMONIUM_ASSETS",
                      "/home/z/my-project/pandemonium-assets")
ROLES_DIR = os.path.join(REPO, "design", "roles")
OUTS = [
    os.path.join(REPO, "design", "art-bible", "scale_chart.png"),
]

FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SIL_COLOR = (26, 28, 32)

MAX_PX = 2048  # repo PNG limit

# kind -> footprint in tiles (buildings: footprint edge). Widths mirror
# content/entities/*.ron: worker r300=0.6, rifleman r350=0.7, raider
# r300=0.6, guardian r500=1.0 (re-derived 2026-10-25).
ENTITIES = [
    ("worker", 0.6), ("rifleman", 0.7), ("raider", 0.6), ("guardian", 1.0),
    ("turret", 2.0), ("ore_node", 2.0), ("supply_depot", 2.0), ("barracks", 3.0),
    ("command_center", 4.0),
]


def ore_node_silhouette(tile_px):
    """Procedural ore node silhouette (no AI render exists for it)."""
    w = int(tile_px * 2)
    h = int(tile_px * 1.3)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(int(w*0.05), h), (int(w*0.25), int(h*0.45)), (int(w*0.45), int(h*0.3)),
               (int(w*0.6), int(h*0.5)), (int(w*0.8), int(h*0.4)), (int(w*0.95), h)],
              fill=SIL_COLOR + (255,))
    d.polygon([(int(w*0.35), int(h*0.5)), (int(w*0.42), int(h*0.05)), (int(w*0.50), int(h*0.5))],
              fill=SIL_COLOR + (255,))
    d.polygon([(int(w*0.5), int(h*0.55)), (int(w*0.62), int(h*0.12)), (int(w*0.7), int(h*0.6))],
              fill=SIL_COLOR + (255,))
    d.polygon([(int(w*0.2), int(h*0.62)), (int(w*0.28), int(h*0.3)), (int(w*0.33), int(h*0.65))],
              fill=SIL_COLOR + (255,))
    return im


def build():
    TILE = 120
    gap_tiles = 1.1
    total_tiles = sum(f for _, f in ENTITIES) + gap_tiles * (len(ENTITIES) - 1)
    W = int(total_tiles * TILE) + 160
    H = int(4.6 * TILE) + 320
    chart = Image.new("RGB", (W, H), (246, 245, 242))
    d = ImageDraw.Draw(chart)
    f_title = ImageFont.truetype(FONT_B, 44)
    f_sub = ImageFont.truetype(FONT_R, 26)
    f_lab = ImageFont.truetype(FONT_B, 26)
    f_small = ImageFont.truetype(FONT_R, 22)

    d.text((40, 30), "Pandemonium - Scale & Footprint Chart", fill=(38, 40, 44), font=f_title)
    d.text((40, 84), "1 tile = 3 m - units 0.6 to 1.0 tiles wide - dashed boxes mark building footprints",
           fill=(90, 90, 95), font=f_sub)

    ground_y = int(3.9 * TILE) + 150
    x = 80
    for name, foot in ENTITIES:
        wpx = int(foot * TILE)
        if name == "ore_node":
            sil = ore_node_silhouette(TILE)
        else:
            sil = Image.open(os.path.join(ROLES_DIR, f"{name}_silhouette.png"))
        bbox = sil.getchannel("A").getbbox()
        sw = bbox[2] - bbox[0]
        sh = bbox[3] - bbox[1]
        scale = wpx / sw
        nh = max(1, int(sh * scale))
        sil = sil.crop(bbox).resize((wpx, nh), Image.LANCZOS)
        chart.paste(sil, (x, ground_y - nh), sil)

        if foot >= 2:
            d.rectangle([x, ground_y - 8, x + wpx, ground_y + 10],
                        outline=(150, 150, 150), width=3)
            for t in range(1, int(foot)):
                d.line([x + t * TILE, ground_y - 8, x + t * TILE, ground_y + 10],
                       fill=(150, 150, 150), width=2)

        d.text((x + wpx // 2, ground_y + 22), name.replace("_", " "),
               fill=(38, 40, 44), font=f_lab, anchor="ma")
        fp = f"{foot:g} tile" if foot < 2 else f"{int(foot)}x{int(foot)} tiles"
        d.text((x + wpx // 2, ground_y + 56), fp, fill=(110, 110, 115),
               font=f_small, anchor="ma")
        x += wpx + int(gap_tiles * TILE)

    d.line([40, ground_y, W - 40, ground_y], fill=(120, 120, 125), width=4)
    ruler_x = 46
    for t in range(0, 4):
        y = ground_y - t * TILE
        d.line([ruler_x, y, ruler_x + 18, y], fill=(120, 120, 125), width=3)
        d.text((ruler_x - 8, y - 16), f"{t}", fill=(120, 120, 125), font=f_small, anchor="ra")
        if t > 0:
            d.line([ruler_x + 18, y, W - 40, y], fill=(215, 215, 215), width=1)
    d.text((ruler_x + 4, ground_y - 4 * TILE - 34), "height (tiles)",
           fill=(120, 120, 125), font=f_small)

    if chart.width > MAX_PX:  # repo PNG limit
        k = MAX_PX / chart.width
        chart = chart.resize((MAX_PX, max(1, int(chart.height * k))), Image.LANCZOS)
    for out in OUTS:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        chart.save(out)
        print("scale chart ->", out, chart.size)


if __name__ == "__main__":
    build()
