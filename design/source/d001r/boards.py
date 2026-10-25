#!/usr/bin/env python3
"""D-001R/D-002 board + lineup composer (parametric orthographic renders).

D-002 changes: every view is auto-fitted to its panel (object + footprint
annotation fill ~80% of the panel in the constraining dimension, vertically
centered, dimension annotations kept); the scavengers lineup is a two-row
readability sheet (unit read test at a uniform 160 px height with 48 px
proof copies, true-scale strip below, canvas cropped to content).

Reproduce the committed renders:
  D001R_OUT=<outdir> python3 boards.py      (needs engine.py, models_scav.py,
                                              models_iron.py next to it)
Outputs <outdir>/concepts/{scavengers,ironclad}/<kind>.png + lineup.png.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import engine as E
from engine import Model, Cam, render_entity_layer, model_bbox, PAL, TEAM, mix
import models_scav
import models_iron

FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
INK, MUTED, BG = E.INK, E.MUTED, E.BG
W, H = 1536, 2048
SS = 3
# output dir: override with D001R_OUT; default is ./out next to this script
OUT = os.environ.get("D001R_OUT",
                     os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))

FACTIONS = {
    'scavengers': dict(color=(240, 140, 30), team_word="ORANGE",
                       tagline="cheap - fast - improvised - weak buildings",
                       roster=models_scav.SCAV_ROSTER, builders=models_scav.BUILDERS),
    'ironclad': dict(color=(46, 155, 230), team_word="BLUE",
                     tagline="heavy - slow - expensive - strong static defense",
                     roster=models_iron.IRON_ROSTER, builders=models_iron.BUILDERS),
}

ENTITIES = {
    'scavengers': [
        ('salvager', 'worker', 'scrap-collecting worker drone with crane and claw', 'fast', 'light', 'cheap'),
        ('ratter', 'light infantry', 'pipe-rifle skirmisher in a bucket helmet', 'fast', 'light', 'cheap'),
        ('scrap_hound', 'fast raider', 'spiked scrap buggy, exposed wheels', 'very fast', 'light', 'cheap'),
        ('ram', 'improvised heavy', 'armored scrap truck with dozer blade', 'medium', 'medium', 'cheap'),
        ('scrap_yard', 'headquarters', 'stacked-container HQ with crane', 'building', 'weak armor', 'cheap'),
        ('garage', 'production', 'tarp-door corrugated workshop', 'building', 'weak armor', 'cheap'),
        ('stash', 'supply', 'crate and fuel-drum cache under canopy', 'building', 'weak armor', 'cheap'),
    ],
    'ironclad': [
        ('artificer', 'worker', 'riveted exosuit engineer with steam vents', 'slow', 'heavy', 'expensive'),
        ('legionnaire', 'heavy infantry', 'full-plate line infantry with slab shield', 'slow', 'heavy', 'expensive'),
        ('crawler', 'heavy tank', 'slab-armored crawler with wide treads', 'very slow', 'heavy', 'expensive'),
        ('colossus', 'super-heavy', 'monolithic four-legged siege walker', 'very slow', 'super heavy', 'very expensive'),
        ('citadel', 'headquarters', 'star-fort command keep with flag mast', 'building', 'fortress armor', 'expensive'),
        ('forge', 'production', 'blast-chimney foundry hall with gantry', 'building', 'fortress armor', 'expensive'),
        ('bastion', 'defense turret', 'embedded bastion with one massive gun', 'building', 'fortress armor', 'expensive'),
    ],
}

PW, PH = 440, 1180


def _f(bold, size):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


# ------------------------------------------------------------------ panel
def render_panel(view, model, meta, team_rgb, accent):
    """One orthographic view auto-fitted to its panel: the object (plus its
    footprint annotation in the top view) fills ~80% of the panel in the
    constraining dimension; dimension annotations are kept."""
    x0, x1, y0, y1, z0, z1 = model_bbox(model)
    Wd, Hd, Ld = x1 - x0, y1 - y0, z1 - z0
    u0, u1 = (x0, x1) if view != 'side' else (z0, z1)
    u_ext = u1 - u0
    v_ext = Hd if view != 'top' else Ld

    # usable panel area: 344 px wide (48 px margins clear the H dim line at
    # PW-42), 1000 px tall (object band 40 .. PH-140, above the W dim row)
    # -> filling it puts the object at ~78% / ~85% of the panel = "~80%"
    fp = meta['fp']
    if view == 'top':
        # the footprint annotation must fit too (collision circle / tile rect)
        fp_n = float(fp.split('x')[0]) if 'x' in fp else float(fp)
        pxt = min(344.0 / max(u_ext, fp_n), 1000.0 / v_ext)
    else:
        pxt = min(344.0 / u_ext, 1000.0 / v_ext)

    img = Image.new("RGB", (PW, PH), E.PANEL_BG)
    d = ImageDraw.Draw(img)

    band_top, band_bot = 40.0, PH - 140.0
    if view == 'top':
        v_mid = (band_top + band_bot) / 2.0
        gy = v_mid + (z0 + z1) / 2.0 * pxt
    else:
        # ground line placed so the object block is centered in the band
        gy = band_top + ((band_bot - band_top) + v_ext * pxt) / 2.0
    cx = PW / 2.0 - (u0 + u1) / 2.0 * pxt
    gy_1x = gy

    def sx(u):
        return cx + u * pxt

    def sy(v):
        return gy_1x - v * pxt

    # --- top view: tile grid + footprint
    if view == 'top':
        step = 1.0 if pxt < 260 else (0.5 if pxt < 520 else 0.25)
        k = math.floor(x0 / step - 1) * step
        while k <= x1 + step:
            d.line([sx(k), 30, sx(k), PH - 40], fill=E.GRID, width=1)
            k += step
        k = math.floor(z0 / step - 1) * step
        while k <= z1 + step:
            d.line([34, sy(k), PW - 34, sy(k)], fill=E.GRID, width=1)
            k += step
        if 'x' in fp:
            n = float(fp.split('x')[0])
            fillc = mix(E.PANEL_BG, accent, 0.20)
            d.rectangle([sx(-n / 2), sy(n / 2), sx(n / 2), sy(-n / 2)], fill=fillc,
                        outline=accent, width=2)
        else:
            r = float(fp) / 2.0 * pxt
            fillc = mix(E.PANEL_BG, accent, 0.20)
            d.ellipse([sx(0) - r, sy(0) - r, sx(0) + r, sy(0) + r], fill=fillc,
                      outline=accent, width=2)
    else:
        # --- ground line + tile ticks + cast shadow (toward SE)
        Hpx = Hd * pxt
        off = 0.14 * Hpx
        ov = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.rounded_rectangle([sx(u0) + off, gy_1x - 4, sx(u1) + off + 8, gy_1x + 12],
                             radius=9, fill=(70, 70, 74, 52))
        ov = ov.filter(ImageFilter.GaussianBlur(4))
        img.paste(ov, (0, 0), ov)
        d = ImageDraw.Draw(img)
        d.line([34, gy_1x, PW - 34, gy_1x], fill=E.GROUND, width=2)
        tstep = 0.5 if pxt < 400 else 0.25
        k = math.ceil(u0 / tstep) * tstep
        while k <= u1 + 1e-9:
            big = abs(k - round(k)) < 1e-9
            d.line([sx(k), gy_1x - (5 if big else 2), sx(k), gy_1x + (5 if big else 2)],
                   fill=E.GROUND, width=2 if big else 1)
            k += tstep

    # --- entity (3x supersampled)
    layer = Image.new("RGBA", (PW * SS, PH * SS), (0, 0, 0, 0))
    cam = Cam(view, pxt, cx, gy_1x, SS)
    cam.layer = layer
    ow = max(1.2, min(2.4, pxt * 0.006))
    render_entity_layer(model, view, cam, team_rgb, silhouette=False, ow=ow)
    layer = layer.resize((PW, PH), Image.LANCZOS)
    img.paste(layer, (0, 0), layer)
    d = ImageDraw.Draw(img)

    # --- zone markers (numbered circles at team-zone centroids)
    zone_pts = {}
    if view != 'top' or True:
        acc = {}
        for face in model.faces:
            pts, mat, tag, seq = face[0], face[1], face[2], face[3]
            if not (tag and tag.startswith('team:')):
                continue
            n = cam.face_normal(face)
            if E._get(n, cam.v['dep']) <= 0.02:
                continue
            pp = [(cx + E._get(p, cam.v['du']) * pxt, gy_1x - E._get(p, cam.v['dv']) * pxt) for p in pts]
            area = 0.0
            for i in range(len(pp)):
                a, b = pp[i], pp[(i + 1) % len(pp)]
                area += a[0] * b[1] - b[0] * a[1]
            area = abs(area) / 2.0
            c = ((pp[0][0] + pp[2][0]) / 2, (pp[0][1] + pp[2][1]) / 2)
            if tag not in acc:
                acc[tag] = [0.0, 0.0, 0.0]
            acc[tag][0] += c[0] * area
            acc[tag][1] += c[1] * area
            acc[tag][2] += area
        for tag, (ax, ay, ar) in acc.items():
            if ar <= 0:
                continue
            px_, py_ = ax / ar, ay / ar
            px_ = max(26, min(PW - 26, px_))
            py_ = max(26, min(PH - 70, py_))
            num = tag.split(':')[1]
            zone_pts[num] = (px_, py_)
            d.ellipse([px_ - 13, py_ - 13, px_ + 13, py_ + 13], fill=accent,
                      outline=(255, 255, 255), width=2)
            fnt = _f(True, 15)
            tb = d.textbbox((0, 0), num, font=fnt)
            d.text((px_ - (tb[2] - tb[0]) / 2, py_ - (tb[3] - tb[1]) / 2 - 1), num,
                   fill=(255, 255, 255), font=fnt)

    # --- dimension lines (front: W/H, side: L/H, top: W/L)
    # extension lines tie the (now centered) object to the W/L dim row
    dm = _f(True, 20)
    if view != 'top':
        y_dim = PH - 54
        for xx in (sx(u0), sx(u1)):
            d.line([xx, gy_1x + 8, xx, y_dim - 4], fill=E.GRID, width=1)
        d.line([sx(u0), y_dim, sx(u1), y_dim], fill=MUTED, width=2)
        for xx in (sx(u0), sx(u1)):
            d.line([xx - 5, y_dim + 5, xx + 5, y_dim - 5], fill=MUTED, width=3)
        lab = ("W" if view == 'front' else "L") + " %.2f T" % (Wd if view == 'front' else Ld)
        tb = d.textbbox((0, 0), lab, font=dm)
        d.text(((sx(u0) + sx(u1)) / 2 - (tb[2] - tb[0]) / 2, y_dim - 30), lab, fill=MUTED, font=dm)
        xv = PW - 42
        ytop = sy(y1)
        d.line([xv, ytop, xv, gy_1x], fill=MUTED, width=2)
        for yy in (ytop, gy_1x):
            d.line([xv - 5, yy + 5, xv + 5, yy - 5], fill=MUTED, width=3)
        lab = "H %.2f T" % Hd
        tb = d.textbbox((0, 0), lab, font=dm)
        d.text((xv - (tb[2] - tb[0]) - 10, ytop - 30), lab, fill=MUTED, font=dm)
    else:
        y_dim = PH - 54
        for xx in (sx(x0), sx(x1)):
            d.line([xx, sy(z0) + 8, xx, y_dim - 4], fill=E.GRID, width=1)
        d.line([sx(x0), y_dim, sx(x1), y_dim], fill=MUTED, width=2)
        for xx in (sx(x0), sx(x1)):
            d.line([xx - 5, y_dim + 5, xx + 5, y_dim - 5], fill=MUTED, width=3)
        lab = "W %.2f T" % Wd
        tb = d.textbbox((0, 0), lab, font=dm)
        d.text(((sx(x0) + sx(x1)) / 2 - (tb[2] - tb[0]) / 2, y_dim - 30), lab, fill=MUTED, font=dm)
        xv = 44
        ytop, ybot = sy(z1), sy(z0)
        d.line([xv, ytop, xv, ybot], fill=MUTED, width=2)
        for yy in (ytop, ybot):
            d.line([xv - 5, yy + 5, xv + 5, yy - 5], fill=MUTED, width=3)
        lab = "L %.2f T" % Ld
        tb = d.textbbox((0, 0), lab, font=dm)
        d.text((xv + 12, ytop - 30), lab, fill=MUTED, font=dm)

    info = dict(W=round(Wd, 2), H=round(Hd, 2), L=round(Ld, 2), pxt=round(pxt), zones=zone_pts)
    return img, info


# ------------------------------------------------------------------ board
def chip(d, x, y, label, value, accent):
    f_l, f_v = _f(True, 22), _f(True, 26)
    lw, vw = d.textlength(label, font=f_l), d.textlength(value, font=f_v)
    cw = max(lw, vw) + 44
    d.rounded_rectangle([x, y, x + cw, y + 86], radius=12, fill=(255, 255, 255),
                        outline=accent, width=3)
    d.text((x + 22, y + 8), label, fill=MUTED, font=f_l)
    d.text((x + 22, y + 38), value, fill=INK, font=f_v)
    return x + cw + 18


def board(faction, name):
    fx = FACTIONS[faction]
    meta = fx['roster'][name]
    model = fx['builders'][name]()
    ent = [e for e in ENTITIES[faction] if e[0] == name][0]
    _, role, blurb, speed, mass, cost = ent
    accent = tuple(fx['color'])
    team_rgb = TEAM[faction]

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # header (D-001 wrapper style)
    d.rectangle([0, 0, W, 248], fill=(255, 255, 255))
    d.rectangle([0, 0, 18, 248], fill=accent)
    d.text((64, 40), f"{faction.upper()} - CONCEPT BOARD", fill=accent, font=_f(True, 30))
    d.text((64, 84), name.replace("_", " ").upper(), fill=INK, font=_f(True, 78))
    d.text((64, 178), f"{role} - {blurb}", fill=MUTED, font=_f(False, 28))

    # three matched orthographic views
    infos = {}
    for i, view in enumerate(('front', 'side', 'top')):
        col_x = 76 + i * 472
        panel, info = render_panel(view, model, meta, team_rgb, accent)
        infos[view] = info
        cap = {'front': 'FRONT', 'side': 'SIDE (RIGHT FLANK)', 'top': 'TOP (PLAN)'}[view]
        d.text((col_x + 2, 286), cap, fill=INK, font=_f(True, 28))
        fp = meta['fp']
        fp_s = ("FOOTPRINT %s T" % fp) if 'x' in fp else ("FOOTPRINT %s T DIA" % fp)
        if view == 'front':
            dims = "W %.2f - H %.2f T - %s" % (info['W'], info['H'], fp_s)
        elif view == 'side':
            dims = "L %.2f - H %.2f T" % (info['L'], info['H'])
        else:
            dims = "W %.2f - L %.2f T" % (info['W'], info['L'])
        d.text((col_x + 2, 322), dims, fill=MUTED, font=_f(False, 21))
        img.paste(panel, (col_x, 352))
        d.rectangle([col_x - 1, 351, col_x + PW + 1, 352 + PH + 1], outline=E.FRAME, width=2)
        for (cx_, cy_, dx_, dy_) in [(col_x - 1, 351, 1, 1), (col_x + PW + 1, 351, -1, 1),
                                     (col_x - 1, 352 + PH + 1, 1, -1), (col_x + PW + 1, 352 + PH + 1, -1, -1)]:
            d.line([cx_, cy_, cx_ + dx_ * 40, cy_], fill=accent, width=7)
            d.line([cx_, cy_, cx_, cy_ + dy_ * 40], fill=accent, width=7)

    # team-zone legend
    y = 352 + PH + 26
    d.text((76, y), "TEAM-COLOR ZONES", fill=INK, font=_f(True, 24))
    xcur = 76 + d.textlength("TEAM-COLOR ZONES", font=_f(True, 24)) + 26
    for i, zn in enumerate(meta['zones'], start=1):
        d.ellipse([xcur, y - 1, xcur + 24, y + 23], fill=accent)
        fnt = _f(True, 14)
        tb = d.textbbox((0, 0), str(i), font=fnt)
        d.text((xcur + 12 - (tb[2] - tb[0]) / 2, y + 11 - (tb[3] - tb[1]) / 2), str(i),
               fill=(255, 255, 255), font=fnt)
        xcur += 32
        d.text((xcur, y), zn, fill=INK, font=_f(False, 24))
        xcur += d.textlength(zn, font=_f(False, 24)) + 34

    # notes
    y += 54
    d.text((76, y), "NOTES", fill=accent, font=_f(True, 22))
    xoff = 76 + d.textlength("NOTES", font=_f(True, 22)) + 18
    for j, note in enumerate(meta['notes'][:2]):
        yy = y + j * 30
        d.rectangle([xoff, yy + 8, xoff + 10, yy + 18], fill=accent)
        d.text((xoff + 22, yy), note, fill=MUTED, font=_f(False, 23))

    # footer legend (D-001 wrapper style)
    y = 1666
    d.rectangle([76, y, 108, y + 34], fill=accent)
    d.text((126, y + 2), f"{fx['team_word']} AREAS = TEAM-COLOR ZONES (recolored per player)",
           fill=INK, font=_f(True, 26))
    d.text((126, y + 44), "FRONT / SIDE / TOP - one parametric model, matched proportions - "
                          "each view auto-fit to its panel (1 tile = 3 m)", fill=MUTED, font=_f(False, 26))
    cy = y + 96
    cx = 76
    cx = chip(d, cx, cy, "SPEED", speed, accent)
    cx = chip(d, cx, cy, "MASS", mass, accent)
    cx = chip(d, cx, cy, "COST", cost, accent)
    d.text((76, H - 52), "pandemonium-assets  -  D-001R concept rework  -  "
                         "final geometry arrives in D-002", fill=MUTED, font=_f(False, 22))
    out_dir = os.path.join(OUT, "concepts", faction)
    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, f"{name}.png"))
    print("board:", faction, name, "pxt", infos['front']['pxt'],
          "dims", infos['front']['W'], infos['front']['H'], infos['side']['L'])
    return img


# ------------------------------------------------------------------ lineup
UNIT_KINDS = ('worker', 'rifleman', 'raider', 'guardian')


def lineup(faction):
    """Two-row readability lineup (D-002 fix):
    row 1 - the four units at a uniform 160 px silhouette height (the shape
            read the 48 px rule is judged against, with 48 px proof copies),
    row 2 - the full roster at true shared scale with the 1-tile scale bar.
    The canvas is cropped to the content (no empty frame air)."""
    fx = FACTIONS[faction]
    accent = tuple(fx['color'])
    roster, builders = fx['roster'], fx['builders']
    order = list(roster)
    units = [n for n in order if roster[n]['kind'] in UNIT_KINDS]

    W2 = 1536
    # vertical layout: header 248 | row1 label 292..326 | 160 px row ground 500
    # | names/minis to 640 | row2 label 672..706 | true-scale frame 714..1082
    # | footer to 1120
    H2 = 1120
    img = Image.new("RGB", (W2, H2), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W2, 248], fill=(255, 255, 255))
    d.rectangle([0, 0, 18, 248], fill=accent)
    d.text((64, 40), f"{faction.upper()} - SILHOUETTE ROSTER", fill=accent, font=_f(True, 30))
    d.text((64, 84), "READABILITY LINEUP", fill=INK, font=_f(True, 62))
    d.text((64, 186), f"{fx['tagline']} - every silhouette must read at 48 px",
           fill=MUTED, font=_f(False, 26))

    models = {n: builders[n]() for n in order}

    # ---------- row 1: unit read test, uniform 160 px height
    d.text((88, 292), "UNIT READ TEST", fill=INK, font=_f(True, 24))
    xcur = 88 + d.textlength("UNIT READ TEST", font=_f(True, 24)) + 14
    d.text((xcur, 293), "- every unit scaled to the same 160 px height; "
                        "48 px proof copies below", fill=MUTED, font=_f(False, 22))

    UNI_H = 160.0
    MINI_H = 48.0
    gy1 = 500.0                      # shared ground line for the 160 px row
    uni = []
    for n in units:
        meta = roster[n]
        view = meta['view_lineup']
        x0, x1, y0, y1, z0, z1 = model_bbox(models[n])
        h = y1 - y0
        u0 = x0 if view != 'side' else z0
        u_ext = (x1 - x0) if view != 'side' else (z1 - z0)
        pxt = UNI_H / h
        uni.append([n, view, pxt, u0, u_ext * pxt, h])
    gap = 76
    usable = 1448 - 88
    total_w = sum(u[4] for u in uni)
    block_w = total_w + gap * (len(uni) - 1)
    if block_w > usable:
        k = (usable - gap * (len(uni) - 1)) / total_w
        for u in uni:
            u[2] *= k
            u[4] *= k
        block_w = usable
    x_left = 88.0 + (usable - block_w) / 2.0
    centers = {}
    for (n, view, pxt, u0, wd, h) in uni:
        centers[n] = x_left + wd / 2.0
        x_left += wd + gap

    # names + heights under each silhouette
    for (n, view, pxt, u0, wd, h) in uni:
        cxx = centers[n]
        lab = n.replace("_", " ")
        tb = d.textbbox((0, 0), lab, font=_f(True, 24))
        d.text((cxx - (tb[2] - tb[0]) / 2, 524), lab, fill=INK, font=_f(True, 24))
        htxt = "H %.2f T" % h
        tb = d.textbbox((0, 0), htxt, font=_f(False, 20))
        d.text((cxx - (tb[2] - tb[0]) / 2, 556), htxt, fill=MUTED, font=_f(False, 20))
    # 48 px proof copies on their own mini ground line
    gy_m = 640.0

    # silhouettes: big row + minis on one supersampled layer
    LX, LY, LW2, LH2 = 88, 288, 1360, 400
    layer = Image.new("RGBA", (LW2 * SS, LH2 * SS), (0, 0, 0, 0))
    for (n, view, pxt, u0, wd, h) in uni:
        cxx = centers[n]
        cam = Cam(view, pxt, cxx - u0 * pxt - LX, gy1 - LY, SS)
        cam.layer = layer
        render_entity_layer(models[n], view, cam, TEAM[faction], silhouette=True)
        # 48 px proof copy, standing on the mini ground line
        pxt_m = MINI_H / h
        cam = Cam(view, pxt_m, cxx - u0 * pxt_m - LX, gy_m - LY, SS)
        cam.layer = layer
        render_entity_layer(models[n], view, cam, TEAM[faction], silhouette=True)
    layer = layer.resize((LW2, LH2), Image.LANCZOS)
    img.paste(layer, (LX, LY), layer)
    d = ImageDraw.Draw(img)
    # ground lines for both sub-rows + mini caption
    d.line([88, gy1, 1448, gy1], fill=E.GROUND, width=2)
    d.line([88, gy_m, 1448, gy_m], fill=E.GROUND, width=1)
    cap = "48 PX PROOF COPIES - each silhouette again at exactly 48 px height"
    tb = d.textbbox((0, 0), cap, font=_f(False, 19))
    d.text(((W2 - (tb[2] - tb[0])) / 2, gy_m + 12), cap, fill=MUTED, font=_f(False, 19))

    # ---------- row 2: true-scale strip
    d.text((88, 700), "TRUE SCALE", fill=INK, font=_f(True, 24))
    xcur = 88 + d.textlength("TRUE SCALE", font=_f(True, 24)) + 14
    d.text((xcur, 701), "- all 7 entities at one shared scale - 1 tile = 3 m",
           fill=MUTED, font=_f(False, 22))
    ax0, ay0, ax1, ay1 = 88, 738, 1448, 1064
    d.rectangle([ax0, ay0, ax1, ay1], fill=E.PANEL_BG, outline=E.FRAME, width=3)
    for (cx_, cy_, dx_, dy_) in [(ax0, ay0, 1, 1), (ax1, ay0, -1, 1),
                                 (ax0, ay1, 1, -1), (ax1, ay1, -1, -1)]:
        d.line([cx_, cy_, cx_ + dx_ * 44, cy_], fill=accent, width=8)
        d.line([cx_, cy_, cx_, cy_ + dy_ * 44], fill=accent, width=8)

    extents = {}
    for n in order:
        meta = roster[n]
        x0, x1, y0, y1, z0, z1 = model_bbox(models[n])
        extents[n] = (x1 - x0) if meta['view_lineup'] != 'side' else (z1 - z0)
        extents[n + '_u0'] = x0 if meta['view_lineup'] != 'side' else z0
    total = sum(extents[n] for n in order)
    inner_x0, inner_x1, gap2 = ax0 + 18, ax1 - 18, 18
    pxt = min(94.0, (inner_x1 - inner_x0 - gap2 * (len(order) - 1)) / total)

    LW, LH = ax1 - ax0 - 36, ay1 - ay0 - 36
    layer = Image.new("RGBA", (LW * SS, LH * SS), (0, 0, 0, 0))
    gy_sheet = ay1 - 50
    x_left = inner_x0
    for n in order:
        meta = roster[n]
        view = meta['view_lineup']
        wd = extents[n] * pxt
        u0 = extents[n + '_u0']
        cam = Cam(view, pxt, x_left - u0 * pxt - ax0 - 18, gy_sheet - ay0 - 18, SS)
        cam.layer = layer
        render_entity_layer(models[n], view, cam, TEAM[faction], silhouette=True)
        x_left += wd + gap2
    layer = layer.resize((LW, LH), Image.LANCZOS)
    img.paste(layer, (ax0 + 18, ay0 + 18), layer)

    # discreet scale bar (true scale evidence, not scenery)
    d = ImageDraw.Draw(img)
    yb = gy_sheet + 22
    d.line([ax0 + 20, yb, ax0 + 20 + pxt, yb], fill=MUTED, width=3)
    for xx in (ax0 + 20, ax0 + 20 + pxt):
        d.line([xx, yb - 6, xx, yb + 6], fill=MUTED, width=3)
    d.text((ax0 + 20 + pxt + 16, yb - 12), "1 TILE = 3 M", fill=MUTED, font=_f(False, 20))

    d.text((88, 1082), "7 entities: 4 units + 3 buildings - silhouette-first faction identity",
           fill=MUTED, font=_f(False, 26))
    out_dir = os.path.join(OUT, "concepts", faction)
    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, "lineup.png"))
    print("lineup:", faction, "pxt", round(pxt, 1))
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    lineup('scavengers')
    for faction in ('scavengers', 'ironclad'):
        for name in FACTIONS[faction]['roster']:
            board(faction, name)


if __name__ == "__main__":
    main()
