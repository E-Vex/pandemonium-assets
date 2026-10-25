#!/usr/bin/env python3
"""D-002 pilot GLB model builder (ART_SPEC compliant, docs/ART_SPEC.md).

Builds the three pilot models as glTF 2.0 binary (.glb):
  rifleman  models/units/rifleman.glb     S unit    (AB section 6 + ART_SPEC section 4)
  barracks  models/buildings/barracks.glb L building
  ore_node  models/nodes/ore_node.glb     M neutral node (no team_color)

Rules honored here (checked independently by glb_check.py):
  1 glTF unit = 1 m; +Y up; forward = -Z; origin at footprint center, Y=0
  ground contact; no geometry below Y=0; static meshes only (no animations/
  skins/morphs); TRIANGLES mode; <=4 primitives; <=3 materials (one named
  exactly 'team_color' with a white baseColorFactor on ownable kinds, absent
  on ore_node); metallic 0.0 / roughness 1.0; OPAQUE alpha; no textures
  (plain baseColorFactor from palette.json); palette colors only.

Run: python3 build_models.py
Output: <repo>/design/staging/d002/models/{units,buildings,nodes}/<kind>.glb
"""
import json
import math
import os
import struct

# assets repo root: override with PANDEMONIUM_ASSETS
REPO = os.environ.get("PANDEMONIUM_ASSETS",
                      "/home/z/my-project/pandemonium-assets")
OUT = os.path.join(REPO, "design", "staging", "d002", "models")
PALETTE = json.load(open(os.path.join(REPO, "design", "art-bible", "palette.json")))
HEXES = {c["id"]: c["hex"] for c in PALETTE["base_colors"]}


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def srgb_factor(rgb):
    """8-bit sRGB -> glTF baseColorFactor linear float (approx per spec)."""
    def lin(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return [lin(c) for c in rgb] + [1.0]


def vsub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vadd(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def vscale(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def vdot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vcross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def vnorm(a):
    l = math.sqrt(vdot(a, a)) or 1.0
    return (a[0] / l, a[1] / l, a[2] / l)


def newell(pts):
    n = [0.0, 0.0, 0.0]
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        n[0] += (p[1] - q[1]) * (p[2] + q[2])
        n[1] += (p[2] - q[2]) * (p[0] + q[0])
        n[2] += (p[0] - q[0]) * (p[1] + q[1])
    return vnorm(n)


class GlbBuilder:
    """Flat-shaded geometry -> one .glb (1 mesh, 1 node, 1 scene)."""

    def __init__(self, name):
        self.name = name
        self.mats = []          # (name, hex)
        self.mat_index = {}
        self.verts = []         # per material: [(x,y,z), ...]
        self.norms = []
        self.faces = []         # per material: [tri vertex indices]

    # ---------------- materials
    def material(self, name, pal_id):
        if name in self.mat_index:
            return self.mat_index[name]
        self.mat_index[name] = len(self.mats)
        self.mats.append((name, pal_id))
        self.verts.append([])
        self.norms.append([])
        self.faces.append([])
        return self.mat_index[name]

    # ---------------- primitives (winding auto-corrected via an interior point)
    def _emit_tri(self, mi, pts, interior):
        n = newell(pts)
        c = (tuple(sum(p[k] for p in pts) / 3.0 for k in range(3)))
        if vdot(n, vsub(c, interior)) < 0:
            pts = pts[::-1]
            n = newell(pts)
        base = len(self.verts[mi])
        for p in pts:
            self.verts[mi].append(p)
            self.norms[mi].append(n)
        self.faces[mi].append((base, base + 1, base + 2))

    def _emit_quad(self, mi, pts, interior):
        n = newell(pts)
        c = (tuple(sum(p[k] for p in pts) / 4.0 for k in range(3)))
        if vdot(n, vsub(c, interior)) < 0:
            pts = pts[::-1]
            n = newell(pts)
        base = len(self.verts[mi])
        for p in pts:
            self.verts[mi].append(p)
            self.norms[mi].append(n)
        self.faces[mi].append((base, base + 1, base + 2))
        self.faces[mi].append((base, base + 2, base + 3))

    def tri(self, mat_name, pal_id, p1, p2, p3, interior):
        self._emit_tri(self.material(mat_name, pal_id), [p1, p2, p3], interior)

    def quad(self, mat_name, pal_id, p1, p2, p3, p4, interior):
        self._emit_quad(self.material(mat_name, pal_id), [p1, p2, p3, p4], interior)

    # ---------------- solids
    def box(self, mat_name, pal_id, c, h, yaw=0.0, pitch=0.0):
        """Axis-aligned or yaw/pitch-rotated box. c=(cx,cy,cz), h=(hx,hy,hz)."""
        mi = self.material(mat_name, pal_id)
        cy_, sy_ = math.cos(yaw), math.sin(yaw)
        cp, sp = math.cos(pitch), math.sin(pitch)
        # R = Ry(yaw) * Rx(pitch)
        def R(v):
            x, y, z = v
            # Rx(pitch)
            y2, z2 = y * cp - z * sp, y * sp + z * cp
            # Ry(yaw)
            x3 = x * cy_ + z2 * sy_
            z3 = -x * sy_ + z2 * cy_
            return (x3, y2, z3)
        corners = [vadd(c, R((sx * h[0], sy * h[1], sz * h[2])))
                   for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
        # corners index: (i>>2)&1=x+, (i>>1)&1=y+, i&1=z+
        def C(ix, iy, iz):
            return corners[(0 if ix else 4) | (0 if iy else 2) | (0 if iz else 1)]
        faces = [
            [C(1, 0, 1), C(1, 0, 0), C(1, 1, 0), C(1, 1, 1)],   # +x
            [C(0, 0, 0), C(0, 0, 1), C(0, 1, 1), C(0, 1, 0)],   # -x
            [C(0, 1, 1), C(1, 1, 1), C(1, 1, 0), C(0, 1, 0)],   # +y
            [C(0, 0, 0), C(1, 0, 0), C(1, 0, 1), C(0, 0, 1)],   # -y
            [C(0, 0, 1), C(1, 0, 1), C(1, 1, 1), C(0, 1, 1)],   # +z
            [C(1, 0, 0), C(0, 0, 0), C(0, 1, 0), C(1, 1, 0)],   # -z
        ]
        for f in faces:
            self._emit_quad(mi, f, c)

    def seg_box(self, mat_name, pal_id, a, b, hw, ht):
        """Box whose long axis runs a->b; cross-section hw x ht (approx)."""
        mi = self.material(mat_name, pal_id)
        u = vnorm(vsub(b, a))
        ref = (0.0, 1.0, 0.0)
        w = vcross(ref, u)
        if vdot(w, w) < 1e-6:
            ref = (1.0, 0.0, 0.0)
            w = vcross(ref, u)
        w = vnorm(w)
        v = vnorm(vcross(u, w))
        c = vscale(vadd(a, b), 0.5)
        L = math.sqrt(vdot(vsub(b, a), vsub(b, a))) / 2.0
        def P(su, sw, sv):
            return (c[0] + u[0] * (su * L) + w[0] * (sw * hw) + v[0] * (sv * ht),
                    c[1] + u[1] * (su * L) + w[1] * (sw * hw) + v[1] * (sv * ht),
                    c[2] + u[2] * (su * L) + w[2] * (sw * hw) + v[2] * (sv * ht))
        faces = [
            [P(1, -1, -1), P(1, 1, -1), P(1, 1, 1), P(1, -1, 1)],
            [P(-1, -1, -1), P(-1, -1, 1), P(-1, 1, 1), P(-1, 1, -1)],
            [P(-1, 1, -1), P(-1, 1, 1), P(1, 1, 1), P(1, 1, -1)],
            [P(-1, -1, -1), P(1, -1, -1), P(1, -1, 1), P(-1, -1, 1)],
            [P(-1, -1, 1), P(1, -1, 1), P(1, 1, 1), P(-1, 1, 1)],
            [P(1, -1, -1), P(-1, -1, -1), P(-1, 1, -1), P(1, 1, -1)],
        ]
        for f in faces:
            self._emit_quad(mi, f, c)

    def spike(self, mat_name, pal_id, base, radius, height, tilt=0.0, yaw=0.0, n=6):
        """Tapered n-gon crystal: hexagonal base ring + apex, tilted from +Y."""
        mi = self.material(mat_name, pal_id)
        axis = (math.sin(tilt) * math.cos(yaw), math.cos(tilt),
                math.sin(tilt) * math.sin(yaw))
        axis = vnorm(axis)
        ref = (0.0, 1.0, 0.0)
        w = vcross(ref, axis)
        if vdot(w, w) < 1e-6:
            ref = (1.0, 0.0, 0.0)
            w = vcross(ref, axis)
        w = vnorm(w)
        v = vnorm(vcross(axis, w))
        ring = []
        for i in range(n):
            t = 2 * math.pi * i / n + math.pi / 6
            ring.append(vadd(vadd(base, vscale(w, radius * math.cos(t))),
                             vscale(v, radius * math.sin(t))))
        apex = vadd(base, vscale(axis, height))
        interior = vadd(base, vscale(axis, height * 0.4))
        for i in range(n):
            self._emit_tri(mi, [ring[i], ring[(i + 1) % n], apex], interior)
        # base cap (fan)
        for i in range(1, n - 1):
            self._emit_tri(mi, [ring[0], ring[i], ring[i + 1]],
                           vadd(base, vscale(axis, -0.05)))

    def wedge_prism(self, mat_name, pal_id, x0, x1, y_base, y_apex, z_span):
        """Gable end: triangular prism along X (caps at x0/x1, apex at z=0)."""
        mi = self.material(mat_name, pal_id)
        z0, z1 = z_span
        a = (x0, y_base, z0); b = (x0, y_base, z1); apex_l = (x0, y_apex, 0)
        c = (x1, y_base, z1); dd = (x1, y_base, z0); apex_r = (x1, y_apex, 0)
        interior = ((x0 + x1) / 2, (y_base + y_apex) / 2, 0)
        self._emit_tri(mi, [a, apex_l, b], interior)          # cap at x0
        self._emit_tri(mi, [dd, apex_r, c], interior)         # cap at x1 (mirror)
        self._emit_quad(mi, [a, b, c, dd], interior)          # base
        self._emit_quad(mi, [a, apex_l, apex_r, dd], interior)  # -z slope
        self._emit_quad(mi, [b, apex_l, apex_r, c], interior)   # +z slope

    # ---------------- export
    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        accessors = []
        bufferviews = []
        bin_blob = bytearray()

        def add_view(data, target):
            off = len(bin_blob)
            bin_blob.extend(data)
            while len(bin_blob) % 4:
                bin_blob.append(0)
            bufferviews.append({"buffer": 0, "byteOffset": off,
                                "byteLength": len(data), "target": target})
            return len(bufferviews) - 1

        used = [i for i in range(len(self.mats)) if self.faces[i]]
        mat_pos = {mi: pos for pos, mi in enumerate(used)}
        primitives = []
        for mi in used:
            vv = self.verts[mi]
            nn = self.norms[mi]
            ff = self.faces[mi]
            pos = b"".join(struct.pack("<fff", *p) for p in vv)
            nor = b"".join(struct.pack("<fff", *p) for p in nn)
            idx = b"".join(struct.pack("<3H", *t) for t in ff)
            pv = add_view(pos, 34962)
            nv = add_view(nor, 34962)
            iv = add_view(idx, 34963)
            mins = [min(p[k] for p in vv) for k in range(3)]
            maxs = [max(p[k] for p in vv) for k in range(3)]
            accessors.append({"bufferView": pv, "componentType": 5126,
                              "count": len(vv), "type": "VEC3",
                              "min": mins, "max": maxs})
            pa = len(accessors) - 1
            accessors.append({"bufferView": nv, "componentType": 5126,
                              "count": len(nn), "type": "VEC3"})
            na = len(accessors) - 1
            accessors.append({"bufferView": iv, "componentType": 5123,
                              "count": len(ff) * 3, "type": "SCALAR"})
            ia = len(accessors) - 1
            primitives.append({"attributes": {"POSITION": pa, "NORMAL": na},
                               "indices": ia, "material": mat_pos[mi], "mode": 4})

        materials = []
        for mi in used:
            name, pal_id = self.mats[mi]
            if name == "team_color":
                # ART_SPEC section 7: near-white base so the per-player tint
                # multiplies predictably
                factor = [1.0, 1.0, 1.0, 1.0]
            else:
                factor = srgb_factor(hex_rgb(HEXES[pal_id]))
            materials.append({
                "name": name,
                "pbrMetallicRoughness": {
                    "baseColorFactor": factor,
                    "metallicFactor": 0.0,
                    "roughnessFactor": 1.0,
                },
                "alphaMode": "OPAQUE",
                "doubleSided": False,
            })

        gltf = {
            "asset": {"version": "2.0",
                      "generator": "pandemonium D-002 pilot builder (design/source/d002)"},
            "scene": 0,
            "scenes": [{"name": self.name, "nodes": [0]}],
            "nodes": [{"name": self.name, "mesh": 0}],
            "meshes": [{"name": self.name, "primitives": primitives}],
            "materials": materials,
            "accessors": accessors,
            "bufferViews": bufferviews,
            "buffers": [{"byteLength": len(bin_blob)}],
        }
        js = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
        while len(js) % 4:
            js += b" "
        total = 12 + 8 + len(js) + 8 + len(bin_blob)
        with open(path, "wb") as f:
            f.write(struct.pack("<III", 0x46546C67, 2, total))
            f.write(struct.pack("<II", len(js), 0x4E4F534A))
            f.write(js)
            f.write(struct.pack("<II", len(bin_blob), 0x004E4942))
            f.write(bytes(bin_blob))
        tris = sum(len(self.faces[i]) for i in range(len(self.mats)))
        print(f"{self.name:10s} -> {path}  ({os.path.getsize(path)} bytes, "
              f"{tris} tris, {len(primitives)} primitives, {len(materials)} materials)")
        return path


# ===================================================================== models
def model_rifleman():
    """S unit. Collision dia 2.1 m -> visual ground width 1.89-2.31 m.
    Height <= 2.1 m. Tris <= 600. team_color zones: torso vest + helmet band."""
    m = GlbBuilder("rifleman")
    GM, DK, TC = "gunmetal_body", "soot_dark", "team_color"
    gm, dk, tc = "gunmetal", "soot_black", None  # palette ids; team = white factor

    # material order: body neutrals first, team last
    m.material(GM, "gunmetal")
    m.material(DK, "soot_black")

    # boots (ground contact Y=0)
    for s in (-1, 1):
        m.box(DK, dk, (s * 0.40, 0.11, 0.05), (0.21, 0.11, 0.28))
    # legs + hips + belt
    for s in (-1, 1):
        m.box(GM, gm, (s * 0.36, 0.47, 0.05), (0.13, 0.25, 0.16))
    m.box(GM, gm, (0, 0.80, 0.05), (0.55, 0.10, 0.26))
    m.box(DK, dk, (0, 0.93, 0.05), (0.58, 0.05, 0.28))
    # torso
    m.box(GM, gm, (0, 1.21, 0.02), (0.55, 0.26, 0.28))
    # team vest (upper-mass primary zone): front/back/side plates
    m.material(TC, "gunmetal")  # pal id unused: team_color factor is white
    m.box(TC, gm, (0, 1.22, -0.305), (0.43, 0.22, 0.05))
    m.box(TC, gm, (0, 1.22, 0.325), (0.43, 0.22, 0.05))
    for s in (-1, 1):
        m.box(TC, gm, (s * 0.545, 1.22, 0.02), (0.05, 0.22, 0.24))
    # pouches on the vest front
    for s in (-1, 1):
        m.box(DK, dk, (s * 0.20, 1.10, -0.39), (0.11, 0.07, 0.04))
    # shoulder pads (wide chunky stance)
    for s in (-1, 1):
        m.box(GM, gm, (s * 0.76, 1.55, 0), (0.21, 0.11, 0.24))
    # arms (dark sleeves: contrast against the gunmetal torso)
    m.seg_box(DK, dk, (0.74, 1.36, 0.05), (0.84, 1.26, -0.10), 0.10, 0.10)
    m.seg_box(DK, dk, (0.84, 1.26, -0.10), (0.40, 1.19, 0.06), 0.085, 0.085)
    m.box(DK, dk, (0.36, 1.19, 0.08), (0.07, 0.07, 0.07))
    m.seg_box(DK, dk, (-0.74, 1.36, 0.05), (-0.88, 1.26, -0.12), 0.10, 0.10)
    m.seg_box(DK, dk, (-0.88, 1.26, -0.12), (-0.36, 1.15, -0.28), 0.085, 0.085)
    m.box(DK, dk, (-0.32, 1.15, -0.30), (0.07, 0.065, 0.07))
    # rifle: diagonal across the chest, muzzle forward-left (-Z), butt back-right
    m.seg_box(DK, dk, (0.55, 1.18, 0.25), (-0.62, 1.18, -0.50), 0.055, 0.075)
    m.seg_box(DK, dk, (-0.62, 1.18, -0.50), (-0.80, 1.18, -0.61), 0.05, 0.055)
    m.seg_box(DK, dk, (0.55, 1.18, 0.25), (0.70, 1.13, 0.35), 0.06, 0.09)
    m.box(DK, dk, (0.10, 1.06, -0.04), (0.05, 0.10, 0.07))
    m.box(DK, dk, (-0.05, 1.29, -0.10), (0.045, 0.05, 0.05))
    # backpack
    m.box(DK, dk, (0.06, 1.20, 0.435), (0.34, 0.24, 0.115))
    m.box(DK, dk, (0.06, 1.51, 0.44), (0.22, 0.08, 0.09))
    # head + visor + helmet + brim
    m.box(GM, gm, (0, 1.61, 0.02), (0.21, 0.15, 0.19))
    m.box(DK, dk, (0, 1.60, -0.185), (0.15, 0.09, 0.02))
    m.box(GM, gm, (0, 1.88, 0.02), (0.26, 0.14, 0.24))
    m.box(DK, dk, (0, 1.78, -0.245), (0.24, 0.05, 0.075))
    # helmet band (team zone 2)
    m.box(TC, gm, (0, 1.875, -0.225), (0.245, 0.045, 0.02))
    m.box(TC, gm, (0, 1.875, 0.265), (0.245, 0.045, 0.02))
    for s in (-1, 1):
        m.box(TC, gm, (s * 0.275, 1.875, 0.02), (0.02, 0.045, 0.24))
    return m


def model_barracks():
    """L building. Footprint 3x3 tiles = 9x9 m; base plate inside it, centered.
    Height <= 3.6 m. Tris <= 3000. team_color: gable roof panels + door lintel."""
    m = GlbBuilder("barracks")
    CW, GD, TC = "concrete_walls", "gunmetal_details", "team_color"
    cw, gd = "concrete", "gunmetal"

    m.material(CW, "concrete")
    m.material(GD, "gunmetal")
    # foundation slab + plinth
    m.box(CW, cw, (0, 0.175, 0), (4.4, 0.175, 3.7))
    m.box(GD, gd, (0, 0.39, 0), (4.15, 0.055, 3.45))
    # walls (hall 8.6 x 6.9, y 0.4..2.5)
    m.box(CW, cw, (0, 1.45, -3.275), (4.3, 1.05, 0.175))
    m.box(CW, cw, (0, 1.45, 3.275), (4.3, 1.05, 0.175))
    m.box(CW, cw, (-4.125, 1.45, 0), (0.175, 1.05, 3.275))
    m.box(CW, cw, (4.125, 1.45, 0), (0.175, 1.05, 3.275))
    # door on the -Z (forward) wall + frame + team lintel + steps
    m.box(GD, gd, (0, 1.42, -3.53), (0.85, 1.02, 0.06))
    for s in (-1, 1):
        m.box(GD, gd, (s * 1.0, 1.45, -3.50), (0.09, 1.05, 0.10))
    m.box(GD, gd, (0, 2.52, -3.50), (1.09, 0.09, 0.10))
    m.box(TC, gd, (0, 2.73, -3.50), (1.15, 0.11, 0.09))
    m.box(CW, cw, (0, 0.09, -3.70), (1.05, 0.09, 0.22))
    m.box(CW, cw, (0, 0.24, -3.58), (0.95, 0.075, 0.18))
    # windows
    for x in (-3.15, -1.9, 1.9, 3.15):
        m.box(GD, gd, (x, 1.55, -3.49), (0.55, 0.42, 0.05))
        m.box(GD, gd, (x, 1.55, 3.49), (0.55, 0.42, 0.05))
    for z in (-2.2, 0, 2.2):
        for s in (-1, 1):
            m.box(GD, gd, (s * 4.31, 1.55, z), (0.05, 0.42, 0.55))
    # corner pylons
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box(GD, gd, (sx * 4.05, 1.65, sz * 3.15), (0.26, 1.30, 0.26))
    # gable roof (team panels): ridge along X at y 3.35, eaves y 2.55 at z +-3.85
    ridge_l, ridge_r = (0, 3.35, 0), (0, 3.35, 0)
    for sz in (-1, 1):
        a = (0, 3.35 + 0.03, -0.03 * sz)
        b = (0, 2.55, sz * 3.85)
        # extend slightly past ridge and eaves
        d = vnorm(vsub(b, a))
        a2 = vadd(a, vscale(d, -0.10))
        b2 = vadd(b, vscale(d, 0.10))
        m.seg_box(TC, gd, (a2[0], a2[1], a2[2]), (b2[0], b2[1], b2[2]), 2.15, 0.075)
    # ridge cap
    m.box(GD, gd, (0, 3.335, 0), (4.33, 0.06, 0.16))
    # gable end prisms (dark: frames the tinted roof panels so the zone
    # stays distinct under any team color, incl. the gray sanity check)
    m.wedge_prism(GD, gd, -4.30, -3.95, 2.50, 3.26, (-3.275, 3.275))
    m.wedge_prism(GD, gd, 3.95, 4.30, 2.50, 3.26, (-3.275, 3.275))
    # dark fascia strips under both eaves
    for sz in (-1, 1):
        m.box(GD, gd, (0, 2.47, sz * 3.80), (4.32, 0.14, 0.09))
    # vents on the -Z roof slope
    for x in (-2.6, 0, 2.6):
        t = 0.45
        pt = (x, 3.35 - 0.80 * t, -3.85 * t)
        d = vnorm(vsub((0, 2.55, -3.85), (0, 3.35, 0)))
        a = vsub(pt, vscale(d, 0.25))
        b = vadd(pt, vscale(d, 0.25))
        m.seg_box(GD, gd, a, b, 0.30, 0.22)
    return m


def model_ore_node():
    """M neutral node. Footprint 2x2 tiles = 6x6 m visual width; height <= 2.4.
    Tris <= 1500. NO team_color (neutral amber ore per AB section 2)."""
    m = GlbBuilder("ore_node")
    RL, RD, OA = "rock_light", "rock_dark", "ore_amber"
    rl, rd, oa = "concrete", "gunmetal", "signal_yellow"

    m.material(RL, "concrete")
    m.material(RD, "gunmetal")
    m.material(OA, "signal_yellow")
    # rock mound (yaw-rotated boxes, all touching Y=0)
    m.box(RL, rl, (0.15, 0.55, 0.10), (1.55, 0.55, 1.35), yaw=math.radians(8))
    m.box(RD, rd, (-1.60, 0.38, 0.35), (0.85, 0.38, 0.75), yaw=math.radians(-14))
    m.box(RD, rd, (1.70, 0.42, -0.25), (0.75, 0.42, 0.80), yaw=math.radians(11))
    m.box(RL, rl, (0.1, 0.30, -1.55), (0.95, 0.30, 0.65), yaw=math.radians(-6))
    m.box(RL, rl, (-0.5, 0.26, 1.38), (0.9, 0.26, 0.70), yaw=math.radians(16))
    # rubble
    m.box(RD, rd, (-0.8, 0.12, -1.1), (0.35, 0.12, 0.30), yaw=math.radians(25))
    m.box(RL, rl, (1.15, 0.10, 0.95), (0.30, 0.10, 0.28), yaw=math.radians(-20))
    m.box(RL, rl, (-1.9, 0.09, -0.7), (0.28, 0.09, 0.25), yaw=math.radians(40))
    m.box(RD, rd, (0.9, 0.08, -1.6), (0.25, 0.08, 0.22), yaw=math.radians(-33))
    m.box(RD, rd, (-0.3, 0.07, 2.00), (0.24, 0.07, 0.20), yaw=math.radians(12))
    # amber crystal spikes (main mass tilted toward -Z)
    m.spike(OA, oa, (0.10, 0.90, 0.00), 0.55, 1.25,
            tilt=math.radians(12), yaw=math.radians(180))
    m.spike(OA, oa, (-1.10, 0.55, 0.50), 0.35, 0.90,
            tilt=math.radians(20), yaw=math.radians(20))
    m.spike(OA, oa, (1.30, 0.60, -0.50), 0.32, 0.85,
            tilt=math.radians(18), yaw=math.radians(180))
    m.spike(OA, oa, (0.60, 0.95, -0.80), 0.28, 0.70,
            tilt=math.radians(15), yaw=math.radians(270))
    m.spike(OA, oa, (-0.50, 0.90, -0.40), 0.24, 0.60, tilt=0.0)
    m.spike(OA, oa, (0.30, 0.70, 0.90), 0.18, 0.35,
            tilt=math.radians(10), yaw=math.radians(80))
    return m


def main():
    os.makedirs(OUT, exist_ok=True)
    paths = {
        "rifleman": model_rifleman().save(os.path.join(OUT, "units", "rifleman.glb")),
        "barracks": model_barracks().save(os.path.join(OUT, "buildings", "barracks.glb")),
        "ore_node": model_ore_node().save(os.path.join(OUT, "nodes", "ore_node.glb")),
    }
    return paths


if __name__ == "__main__":
    main()
