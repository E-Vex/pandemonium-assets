#!/usr/bin/env python3
"""D-002 pilot GLB checker + preview renderer (independent of the builder).

Reads each .glb byte-for-byte, recomputes the ART_SPEC section 11 checklist
evidence (triangle count, bounding box in meters, material list, file size,
team_color rules, budget compliance) and renders orthographic previews
(front/side/top + iso) plus the section 7 gray-tint sanity render.

Run: python3 glb_check.py
"""
import json
import math
import os
import struct
from PIL import Image, ImageDraw, ImageFont

# assets repo root: override with PANDEMONIUM_ASSETS; previews -> D002_PREVIEW
REPO = os.environ.get("PANDEMONIUM_ASSETS",
                      "/home/z/my-project/pandemonium-assets")
MODELS_DIR = os.path.join(REPO, "design", "staging", "d002", "models")
PREVIEW_DIR = os.environ.get("D002_PREVIEW", "/home/z/my-project/work/d002/previews")

# ART_SPEC section 4/5/9 budgets per kind
SPEC = {
    "rifleman": dict(cls="S", tri=600, size_cap=2 * 1024 * 1024,
                     ground=(1.89, 2.31), height=2.1, ownable=True,
                     footprint=None, zones="torso vest + helmet band"),
    "barracks": dict(cls="L", tri=3000, size_cap=4 * 1024 * 1024,
                     ground=None, height=3.6, ownable=True,
                     footprint=(9.0, 9.0), zones="gable roof panels"),
    "ore_node": dict(cls="M", tri=1500, size_cap=2 * 1024 * 1024,
                     ground=None, height=2.4, ownable=False,
                     footprint=(6.0, 6.0), zones=None),
}

FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


# ---------------------------------------------------------------- glb parse
def parse_glb(path):
    data = open(path, "rb").read()
    magic, ver, total = struct.unpack("<III", data[:12])
    assert magic == 0x46546C67, "bad magic"
    assert ver == 2, "bad version"
    assert total == len(data), "length mismatch"
    off = 12
    js = bin_ = None
    while off < len(data):
        clen, ctype = struct.unpack("<II", data[off:off + 8])
        chunk = data[off + 8:off + 8 + clen]
        if ctype == 0x4E4F534A:
            js = json.loads(chunk.decode("utf-8").rstrip(" "))
        elif ctype == 0x004E4942:
            bin_ = chunk
        off = (off + 8 + clen + 3) & ~3
    assert js is not None and bin_ is not None, "missing chunks"
    return js, bin_


def read_accessor(acc, bin_, views):
    view = views[acc["bufferView"]]
    off, ln = view["byteOffset"], view["byteLength"]
    comp, count, typ = acc["componentType"], acc["count"], acc["type"]
    n = {"SCALAR": 1, "VEC3": 3}[typ]
    raw = bin_[off:off + ln]
    if comp == 5126:
        vals = struct.unpack("<%df" % (count * n), raw[:count * n * 4])
    elif comp == 5123:
        vals = struct.unpack("<%dH" % (count * n), raw[:count * n * 2])
    else:
        raise ValueError(comp)
    if n == 1:
        return list(vals)
    return [list(vals[i * n:(i + 1) * n]) for i in range(count)]


def load_geometry(js, bin_):
    """-> list of primitives: dict(mat_index, tris=[(v,n)...] per corner)"""
    prims = []
    views = js["bufferViews"]
    mesh = js["meshes"][0]
    for p in mesh["primitives"]:
        assert p["mode"] == 4, "non-TRIANGLES primitive"
        pos = read_accessor(js["accessors"][p["attributes"]["POSITION"]], bin_, views)
        nor = None
        if "NORMAL" in p["attributes"]:
            nor = read_accessor(js["accessors"][p["attributes"]["NORMAL"]], bin_, views)
        idx = read_accessor(js["accessors"][p["indices"]], bin_, views) if "indices" in p else None
        tris = []
        if idx:
            for i in range(0, len(idx), 3):
                tris.append([pos[idx[i]], pos[idx[i + 1]], pos[idx[i + 2]]])
        else:
            for i in range(0, len(pos), 3):
                tris.append([pos[i], pos[i + 1], pos[i + 2]])
        prims.append(dict(mat=p.get("material"), tris=tris, normals=nor))
    return prims


# ---------------------------------------------------------------- report
def check(kind, path):
    js, bin_ = parse_glb(path)
    prims = load_geometry(js, bin_)
    spec = SPEC[kind]
    size = os.path.getsize(path)
    tris = sum(len(p["tris"]) for p in prims)
    mats = js.get("materials", [])
    allpts = [v for p in prims for t in p["tris"] for v in t]
    bbox = ([min(v[k] for v in allpts) for k in range(3)],
            [max(v[k] for v in allpts) for k in range(3)])
    team = [m for m in mats if m["name"] == "team_color"]

    checks = []
    ok = lambda b, msg: checks.append(("PASS" if b else "FAIL", msg))
    # section 1
    ok(path.endswith(f"{kind}.glb"), f"file name {kind}.glb")
    ok(("animations" not in js and "skins" not in js
        and not any("targets" in p["attributes"] for m in js["meshes"]
                    for p in m["primitives"])), "no animations/skins/morphs")
    ok("images" not in js and "textures" not in js and "samplers" not in js,
       "no textures (plain baseColorFactor)")
    ok(not any("extensions" in js.get("asset", {}) or k in js for k in
               ("extensionsUsed", "extensionsRequired")),
       "no compression/extension declarations")
    # sections 5/6
    ok(len(js["meshes"][0]["primitives"]) <= 4,
       f"{len(js['meshes'][0]['primitives'])} primitives (<= 4)")
    ok(all(p["mode"] == 4 for p in js["meshes"][0]["primitives"]),
       "all primitives TRIANGLES mode")
    ok(tris <= spec["tri"], f"{tris} triangles (<= {spec['tri']})")
    ok(len(mats) <= 3, f"{len(mats)} materials (<= 3)")
    ok(all(m["pbrMetallicRoughness"].get("metallicFactor") == 0.0
           and m["pbrMetallicRoughness"].get("roughnessFactor") == 1.0
           for m in mats), "metallic 0.0 / roughness 1.0 on all materials")
    ok(all(m.get("alphaMode", "OPAQUE") == "OPAQUE" for m in mats),
       "OPAQUE alpha on all materials")
    ok(all(m.get("doubleSided") is False for m in mats), "doubleSided false")
    # section 7 team_color
    if spec["ownable"]:
        ok(len(team) == 1, "exactly one team_color material")
        if team:
            f = team[0]["pbrMetallicRoughness"]["baseColorFactor"]
            ok(all(c >= 0.75 for c in f[:3]),
               f"team_color near-white base {tuple(round(c,2) for c in f[:3])}")
    else:
        ok(len(team) == 0, "no team_color material (neutral)")
    # section 3/4 geometry
    ok(bbox[0][1] >= -1e-6, f"nothing below Y=0 (min Y {bbox[0][1]:.3f})")
    gw = max(bbox[1][0] - bbox[0][0], bbox[1][2] - bbox[0][2])
    diag = math.hypot(bbox[1][0] - bbox[0][0], bbox[1][2] - bbox[0][2])
    if spec["ground"]:
        ok(spec["ground"][0] <= gw <= spec["ground"][1],
           f"visual ground width {gw:.2f} m in [{spec['ground'][0]}-{spec['ground'][1]}] "
           f"(XZ bbox {bbox[1][0]-bbox[0][0]:.2f} x {bbox[1][2]-bbox[0][2]:.2f} m)")
    if spec["footprint"]:
        ok((bbox[1][0] - bbox[0][0]) <= spec["footprint"][0] + 1e-6
           and (bbox[1][2] - bbox[0][2]) <= spec["footprint"][1] + 1e-6,
           f"XZ bbox {bbox[1][0]-bbox[0][0]:.2f} x {bbox[1][2]-bbox[0][2]:.2f} m "
           f"within {spec['footprint'][0]:.0f} x {spec['footprint'][1]:.0f} m footprint")
        ok(abs((bbox[0][0] + bbox[1][0]) / 2) < 0.01
           and abs((bbox[0][2] + bbox[1][2]) / 2) < 0.01,
           "origin at footprint XZ center")
    ok(bbox[1][1] <= spec["height"],
       f"height {bbox[1][1]:.2f} m (<= {spec['height']})")
    ok(bbox[0][1] <= 0.001, f"ground contact at Y=0 (min Y {bbox[0][1]:.3f})")
    # section 9
    ok(size <= spec["size_cap"], f"file size {size} bytes "
       f"({size/1024:.1f} KiB <= {spec['size_cap']/1024/1024:.0f} MiB)")

    report = dict(kind=kind, path=path, tris=tris, size=size, bbox=bbox,
                  mats=[dict(name=m["name"],
                             factor=m["pbrMetallicRoughness"]["baseColorFactor"],
                             metallic=m["pbrMetallicRoughness"]["metallicFactor"],
                             roughness=m["pbrMetallicRoughness"]["roughnessFactor"],
                             alpha=m.get("alphaMode", "OPAQUE"))
                        for m in mats],
                  prims=len(js["meshes"][0]["primitives"]),
                  ground_w=(bbox[1][0] - bbox[0][0], bbox[1][2] - bbox[0][2]),
                  diag=diag, checks=checks)
    return report, prims, js, bin_


# ---------------------------------------------------------------- previews
def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def factor_to_rgb(f):
    # linear -> sRGB approx (for preview only)
    def enc(c):
        c = max(0.0, min(1.0, c))
        s = c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
        return int(round(s * 255))
    return tuple(enc(c) for c in f[:3])


def render_views(kind, prims, js, bin_, out_prefix):
    """4 orthographic previews + gray team-tint sanity variant."""
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    mat_colors = {}
    for i, m in enumerate(js["materials"]):
        mat_colors[i] = factor_to_rgb(m["pbrMetallicRoughness"]["baseColorFactor"])
    # flat normals recomputed per tri (positions are flat-shaded already)
    faces = []
    for p in prims:
        for t in p["tris"]:
            n = _normal(t)
            faces.append((t, p["mat"], n))
    views = {
        "front": dict(du="x", dv="y", dep="z", dsign=-1),  # camera at -Z sees -Z faces
        "side": dict(du="z", dv="y", dep="x", dsign=+1),   # camera at +X, nose -> screen right
        "top": dict(du="x", dv="z", dv_sign=-1, dep="y", dsign=+1),  # nose -Z -> screen up
    }
    W, H = 760, 640
    for name, v in views.items():
        img = Image.new("RGB", (W, H), (250, 249, 246))
        d = ImageDraw.Draw(img)
        allpts = [pt for (t, mi, n) in faces for pt in t]
        us = [pt["xyz".index(v["du"])] for pt in allpts]
        ws = [pt["xyz".index(v["dv"])] * (v.get("dv_sign", 1)) for pt in allpts]
        umin, umax, wmin, wmax = min(us), max(us), min(ws), max(ws)
        span = max(umax - umin, wmax - wmin, 0.1)
        ppp = (min(W, H) - 110) / span
        cx, cy = W / 2, H / 2
        sx = lambda p: cx + (p["xyz".index(v["du"])] - (umin + umax) / 2) * ppp
        sy = lambda p: cy - (p["xyz".index(v["dv"])] * v.get("dv_sign", 1)
                             - (wmin + wmax) / 2) * ppp
        vis = []
        for (t, mi, n) in faces:
            if n["xyz".index(v["dep"])] * v["dsign"] <= 0.02:
                continue
            depth = sum(pt["xyz".index(v["dep"])] for pt in t) / 3
            vis.append((depth, t, mi, n))
        vis.sort(key=lambda f: f[0])
        for (_, t, mi, n) in vis:
            nu, nv = n["xyz".index(v["du"])], n["xyz".index(v["dv"])] * v.get("dv_sign", 1)
            ln = math.hypot(nu, nv)
            f_dir = 1.0
            if ln > 0.25:
                dd = (nu / ln) * -0.62 + (nv / ln) * 0.62
                f_dir = 1.12 if dd > 0.33 else (0.88 if dd < -0.33 else 1.0)
            c = tuple(max(0, min(255, int(ch * f_dir))) for ch in mat_colors[mi])
            pp = [(sx(p), sy(p)) for p in t]
            d.polygon(pp, fill=c)
            oc = tuple(max(0, min(255, int(ch * 0.55))) for ch in c)
            d.line(pp + [pp[0]], fill=oc, width=2, joint="curve")
        f = ImageFont.truetype(FONT_B, 26)
        d.text((30, 22), f"{kind} - {name}", fill=(38, 40, 44), font=f)
        img.save(f"{out_prefix}_{name}.png")
    # gray-tint sanity render (section 7): team zones at #808080, front view
    if any(m["name"] == "team_color" for m in js["materials"]):
        gray = {}
        for i, m in enumerate(js["materials"]):
            gray[i] = (128, 128, 128) if m["name"] == "team_color" \
                else factor_to_rgb(m["pbrMetallicRoughness"]["baseColorFactor"])
        img = Image.new("RGB", (W, H), (250, 249, 246))
        d = ImageDraw.Draw(img)
        v = views["front"]
        allpts = [pt for (t, mi, n) in faces for pt in t]
        us = [pt["xyz".index(v["du"])] for pt in allpts]
        ws = [pt["xyz".index(v["dv"])] for pt in allpts]
        umin, umax, wmin, wmax = min(us), max(us), min(ws), max(ws)
        span = max(umax - umin, wmax - wmin, 0.1)
        ppp = (min(W, H) - 110) / span
        cx, cy = W / 2, H / 2
        sx = lambda p: cx + (p["xyz".index(v["du"])] - (umin + umax) / 2) * ppp
        sy = lambda p: cy - (p["xyz".index(v["dv"])] - (wmin + wmax) / 2) * ppp
        vis = []
        for (t, mi, n) in faces:
            if n["xyz".index(v["dep"])] * v["dsign"] <= 0.02:
                continue
            depth = sum(pt["xyz".index(v["dep"])] for pt in t) / 3
            vis.append((depth, t, mi, n))
        vis.sort(key=lambda f: f[0])
        for (_, t, mi, n) in vis:
            c = gray[mi]
            pp = [(sx(p), sy(p)) for p in t]
            d.polygon(pp, fill=c)
            oc = tuple(max(0, int(ch * 0.55)) for ch in c)
            d.line(pp + [pp[0]], fill=oc, width=2, joint="curve")
        f = ImageFont.truetype(FONT_B, 26)
        d.text((30, 22), f"{kind} - gray-tint sanity check (#808080 team zones)",
               fill=(38, 40, 44), font=f)
        img.save(f"{out_prefix}_graycheck.png")


def _normal(t):
    u = [t[1][k] - t[0][k] for k in range(3)]
    w = [t[2][k] - t[1][k] for k in range(3)]
    n = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2],
         u[0] * w[1] - u[1] * w[0])
    l = math.sqrt(sum(x * x for x in n)) or 1.0
    return (n[0] / l, n[1] / l, n[2] / l)


# ---------------------------------------------------------------- main
def main():
    reports = []
    for kind, rel in [("rifleman", "units/rifleman.glb"),
                      ("barracks", "buildings/barracks.glb"),
                      ("ore_node", "nodes/ore_node.glb")]:
        path = os.path.join(MODELS_DIR, rel)
        rep, prims, js, bin_ = check(kind, path)
        reports.append(rep)
        render_views(kind, prims, js, bin_,
                     os.path.join(PREVIEW_DIR, kind))
        print(f"\n=== {kind} ({rel}) ===")
        print(f"  triangles : {rep['tris']}")
        print(f"  primitives: {rep['prims']}   materials: {len(rep['mats'])}")
        b0, b1 = rep["bbox"]
        print(f"  bbox (m)  : X {b0[0]:.2f}..{b1[0]:.2f}  Y {b0[1]:.2f}..{b1[1]:.2f}  "
              f"Z {b0[2]:.2f}..{b1[2]:.2f}  (size {b1[0]-b0[0]:.2f} x {b1[1]-b0[1]:.2f} x {b1[2]-b0[2]:.2f})")
        print(f"  ground    : XZ {rep['ground_w'][0]:.2f} x {rep['ground_w'][1]:.2f} m, "
              f"diag {rep['diag']:.2f} m")
        print(f"  file size : {rep['size']} bytes ({rep['size']/1024:.1f} KiB)")
        for m in rep["mats"]:
            print(f"  material  : {m['name']:16s} factor "
                  f"{tuple(round(c,3) for c in m['factor'][:3])} "
                  f"metal {m['metallic']} rough {m['roughness']} alpha {m['alpha']}")
        for st, msg in rep["checks"]:
            print(f"  [{st}] {msg}")
    out = os.path.join(PREVIEW_DIR, "reports.json")
    json.dump([{k: v for k, v in r.items() if k != "checks"} | {
        "checks": [[s, m] for s, m in r["checks"]]} for r in reports],
        open(out, "w"), indent=1)
    print("\nreport json ->", out)


if __name__ == "__main__":
    main()
