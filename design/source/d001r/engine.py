#!/usr/bin/env python3
"""D-001R parametric concept-board engine.

Entities are modeled as flat-shaded polygon sets in TILE units:
  x = right, y = up, z = front (nose), ground at y = 0.

Three unmirrored orthographic projections share axes so front, side and
top views provably show the SAME design with matching proportions:
  FRONT: screen_x = +x, screen_up = +y   (camera on +z)
  SIDE : screen_x = +z, screen_up = +y   (camera on +x, right flank, nose -> screen right)
  TOP  : screen_x = +x, screen_up = +z   (camera above, nose -> screen up)
Consequences: entity-right is screen-right in FRONT and TOP; nose is
screen-right in SIDE and screen-up in TOP; height is screen-up in FRONT
and SIDE.  Widths/heights/lengths therefore correspond across views.
"""
import math
from PIL import Image, ImageDraw, ImageFilter

# ---------------------------------------------------------------- palette
def _h(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))

PAL = {
    'soot_black':    _h('#26282C'),
    'gunmetal':      _h('#454A52'),
    'slate_steel':   _h('#6E7681'),
    'bright_steel':  _h('#A6ADB5'),
    'concrete':      _h('#8E8E86'),
    'bone_white':    _h('#D8D3C6'),
    'canvas_tan':    _h('#8A6F4D'),
    'leather_brown': _h('#5B4A3A'),
    'rust':          _h('#9C5B33'),
    'olive_drab':    _h('#3E6C4F'),
    'signal_yellow': _h('#D9A441'),
    'glass_cyan':    _h('#7FB4B8'),
}
TEAM = {'scavengers': _h('#F08C1E'), 'ironclad': _h('#2E9BE6')}
INK = _h('#26282C')
MUTED = _h('#6E7076')
BG = _h('#F2F0EC')
PANEL_BG = _h('#FBFAF7')
GRID = _h('#D9D6CD')
GROUND = _h('#C7C4BB')
FRAME = _h('#DFDCD4')


def mix(c1, c2, t):
    return tuple(max(0, min(255, round(a + (b - a) * t))) for a, b in zip(c1, c2))


def shade_rgb(c, f):
    return tuple(max(0, min(255, round(ch * f))) for ch in c)


# ---------------------------------------------------------------- geometry
def normal_of(pts):
    n = [0.0, 0.0, 0.0]
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        n[0] += (p[1] - q[1]) * (p[2] + q[2])
        n[1] += (p[2] - q[2]) * (p[0] + q[0])
        n[2] += (p[0] - q[0]) * (p[1] + q[1])
    ln = math.sqrt(sum(v * v for v in n)) or 1.0
    return (n[0] / ln, n[1] / ln, n[2] / ln)


class Model:
    """faces: (pts, mat, tag)  dots: (p, axis, sign, r, color, tag)"""

    def __init__(self, name):
        self.name = name
        self.faces = []
        self.dots = []
        self.seq = 0

    def _f(self, pts, mat, tag=None):
        self.faces.append((pts, mat, tag, self.seq))
        self.seq += 1

    def box(self, x0, y0, z0, x1, y1, z1, mat, tag=None):
        """axis-aligned box; outward normals (Newell); insertion order = tie-break"""
        self._f([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], mat, tag)   # +z
        self._f([(x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0)], mat, tag)   # -z
        self._f([(x1, y0, z1), (x1, y0, z0), (x1, y1, z0), (x1, y1, z1)], mat, tag)   # +x
        self._f([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], mat, tag)   # -x
        self._f([(x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0)], mat, tag)   # +y
        self._f([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], mat, tag)   # -y

    def quad(self, p1, p2, p3, p4, mat, tag=None, n=None):
        pts = [p1, p2, p3, p4]
        if n is None:
            n = normal_of(pts)
        # store explicit normal alongside
        self.faces.append((pts, mat, tag, self.seq, n))
        self.seq += 1

    def poly(self, pts, mat, tag=None, n=None):
        if n is None:
            n = normal_of(pts)
        self.faces.append((pts, mat, tag, self.seq, n))
        self.seq += 1

    def dot(self, p, axis, sign, r, color, tag=None):
        self.dots.append((p, axis, sign, r, color, tag))

    def rivets(self, p0, p1, axis, sign, r, color, n, off=0.0):
        """row of n rivets between p0..p1 (3d points on the surface)"""
        for i in range(n):
            t = (i + 0.5) / n if n > 1 else 0.5
            p = (p0[0] + (p1[0] - p0[0]) * t,
                 p0[1] + (p1[1] - p0[1]) * t,
                 p0[2] + (p1[2] - p0[2]) * t)
            self.dots.append((p, axis, sign, r, color, None))

    def plate(self, axis, sign, cx, cy, cz, w, h, mat, tag=None, tilt=0.0, thick=0.012):
        """thin flat plate lying on a face (axis/sign), optional tilt (rad) in-plane.
        Used for bolted-on scrap patches, hazard stripes, trim bands."""
        spans = {'x': ((0, 0, 1), (0, 1, 0)), 'y': ((1, 0, 0), (0, 0, 1)), 'z': ((1, 0, 0), (0, 1, 0))}
        uax = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}[axis]
        a0, b0 = spans[axis]
        u, v = a0, b0
        o = (thick / 2.0 + 0.004) * sign
        # in-plane axes for w/h; tilt rotates them
        ct, st = math.cos(tilt), math.sin(tilt)
        a = (u[0] * ct + v[0] * st, u[1] * ct + v[1] * st, u[2] * ct + v[2] * st)
        b = (-u[0] * st + v[0] * ct, -u[1] * st + v[1] * ct, -u[2] * st + v[2] * st)
        hw, hh = w / 2.0, h / 2.0
        pts = []
        for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            pts.append((cx + a[0] * su * hw + b[0] * sv * hh + uax[0] * o,
                        cy + a[1] * su * hw + b[1] * sv * hh + uax[1] * o,
                        cz + a[2] * su * hw + b[2] * sv * hh + uax[2] * o))
        nvec = (uax[0] * sign, uax[1] * sign, uax[2] * sign)
        self.poly(pts, mat, tag, n=nvec)

    def ngon(self, axis, c, radius, depth, mat, tag=None, n=8, phase=0.0):
        """n-gonal prism along axis; c = center of -face; depth toward +axis.
        phase rotates the polygon in its plane (use pi/8 for flats on the axes)."""
        ax = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}[axis]
        u, v = _perp(axis)
        for s in (1, -1):  # two caps
            pts = []
            for i in range(n):
                t = 2 * math.pi * i / n + phase
                p = [c[0] + u[0] * radius * math.cos(t) + v[0] * radius * math.sin(t) + ax[0] * depth * (s > 0),
                     c[1] + u[1] * radius * math.cos(t) + v[1] * radius * math.sin(t) + ax[1] * depth * (s > 0),
                     c[2] + u[2] * radius * math.cos(t) + v[2] * radius * math.sin(t) + ax[2] * depth * (s > 0)]
                pts.append(tuple(p))
            nv = (ax[0] * s, ax[1] * s, ax[2] * s)
            self.poly(pts, mat, tag, n=nv)
        for i in range(n):
            t0, t1 = 2 * math.pi * i / n + phase, 2 * math.pi * (i + 1) / n + phase
            p0 = [c[k] + (u[k] * radius * math.cos(t0) + v[k] * radius * math.sin(t0)) for k in range(3)]
            p1 = [c[k] + (u[k] * radius * math.cos(t1) + v[k] * radius * math.sin(t1)) for k in range(3)]
            p2 = [p1[k] + ax[k] * depth for k in range(3)]
            p3 = [p0[k] + ax[k] * depth for k in range(3)]
            self.poly([tuple(p0), tuple(p1), tuple(p2), tuple(p3)], mat, tag,
                      n=_norm_cross(p0, p1, p2))

    def wheel(self, cx, cy, cz, radius, width, mat='soot_black', hub=None, n=10, side=+1):
        """wheel along x axis (rolls on z); side=+1 draws hub on +x face"""
        self.ngon('x', (cx - width / 2, cy, cz), radius, width, mat, n=n)
        if hub:
            self.plate('x', side, cx + side * width / 2, cy, cz, radius * 0.52, radius * 0.52, hub, tilt=math.pi / 4)

    def wedge_z(self, x0, y0, z0, x1, y1, z1, mat, tag=None, hi_x=True, hi_z=True):
        """right-triangle prism swept along z: profile in x/y; right angle at
        (hi_x ? x1 : x0, hi_z... ) -- hypotenuse runs between the other two corners."""
        # profile corners: A=(x0,y0) B=(x1,y0) C=(right-angle top corner)
        rx = x1 if hi_x else x0
        pts2 = [(x0, y0), (x1, y0), (rx, y1)]
        for zz, s in ((z0, -1), (z1, +1)):
            pts = [(p[0], p[1], zz) for p in pts2]
            self.poly(pts, mat, tag, n=(0, 0, s))
        # three side quads: bottom y0, vertical at rx, hypotenuse
        a, b, c = pts2
        for (p, q) in ((a, b), (b, c), (c, a)):
            self.poly([(p[0], p[1], z0), (q[0], q[1], z0), (q[0], q[1], z1), (p[0], p[1], z1)],
                      mat, tag, n=_norm_cross((p[0], p[1], z0), (q[0], q[1], z0), (q[0], q[1], z1)))

    def tarp(self, p_center, w, d, mat='canvas_tan', tag=None, sag=0.06, tilt=0.0):
        """loose canvas quad with 4 corners, slight irregular sag (visual)."""
        cx, cy, cz = p_center
        ct, st = math.cos(tilt), math.sin(tilt)
        ex, ez = w / 2 * ct, w / 2 * st
        fx, fz = d / 2 * -st, d / 2 * ct
        pts = [
            (cx - ex - fx, cy, cz - ez - fz),
            (cx + ex - fx, cy + sag * 0.6, cz + ez - fz),
            (cx + ex + fx, cy - sag, cz + ez + fz),
            (cx - ex + fx, cy + sag * 0.4, cz - ez + fz),
        ]
        n = normal_of(pts)
        if n[1] < 0:
            pts = pts[::-1]
            n = normal_of(pts)
        self.poly(pts, mat, tag, n=n)


def _perp(axis):
    # (u, v) right-handed with axis: u x v = +axis
    if axis == 'x':
        return (0, 1, 0), (0, 0, 1)
    if axis == 'y':
        return (0, 0, 1), (1, 0, 0)
    return (1, 0, 0), (0, 1, 0)


def _norm_cross(p0, p1, p2):
    u = [p1[i] - p0[i] for i in range(3)]
    v = [p2[i] - p1[i] for i in range(3)]
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    ln = math.sqrt(sum(t * t for t in n)) or 1.0
    return (n[0] / ln, n[1] / ln, n[2] / ln)


# ---------------------------------------------------------------- views
VIEWS = {
    'front': dict(dep='z', du='x', dv='y'),   # screen_x=x, screen_up=y
    'side':  dict(dep='x', du='z', dv='y'),   # screen_x=z, screen_up=y
    'top':   dict(dep='y', du='x', dv='z'),   # screen_x=x, screen_up=z
}
AXIS_V = {'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}


def _get(p, k):
    return {'x': p[0], 'y': p[1], 'z': p[2]}[k]


class Cam:
    """ortho camera for a view + world->panel transform."""

    def __init__(self, view, px_per_tile, cx_screen, ground_screen_y, ss):
        v = VIEWS[view]
        self.view, self.v = view, v
        self.pxt = px_per_tile
        self.ss = ss
        self.cx, self.gy = cx_screen * ss, ground_screen_y * ss

    def proj(self, p):
        """world -> panel px (supersampled), y down."""
        u = _get(p, self.v['du'])
        w = _get(p, self.v['dv'])
        return (self.cx + u * self.pxt * self.ss, self.gy - w * self.pxt * self.ss)

    def depth(self, p):
        return _get(p, self.v['dep'])

    def face_normal(self, face):
        if len(face) == 5:            # (pts, mat, tag, seq, n)
            return face[4]
        return normal_of(face[0])     # (pts, mat, tag, seq)


def _fill_for(mat, tag, team_rgb, n, cam, y_frac):
    if tag and tag.startswith('team'):
        base = team_rgb if tag == 'team' else mix(team_rgb, (0, 0, 0), 0.28)
        f = 1.0 + 0.07 * y_frac
        return shade_rgb(base, f)
    if mat == 'team':
        return shade_rgb(team_rgb, 1.0 + 0.07 * y_frac)
    base = PAL.get(mat, mat if isinstance(mat, tuple) else (120, 120, 120))
    # 3-value matte shading: bright plane / mid / shadow, light from upper-left of sheet
    nu, nv = _get(n, cam.v['du']), _get(n, cam.v['dv'])
    ln = math.hypot(nu, nv)
    f_dir = 1.0
    if ln > 0.25:  # tilted face: directional value from sheet light NW
        d = (nu / ln) * -0.62 + (nv / ln) * 0.62
        f_dir = 1.12 if d > 0.33 else (0.88 if d < -0.33 else 1.0)
    f_y = 1.0 + 0.07 * y_frac
    return shade_rgb(base, f_dir * f_y)


def _outline_for(fill):
    return mix(fill, PAL['soot_black'], 0.52)


def render_entity_layer(model, view, cam, team_rgb, silhouette=False, ow=2.0):
    """painter-sorted flat-shaded faces (+ rivet dots, depth-merged) onto cam.layer."""
    ss = cam.ss
    vis = []
    for face in model.faces:
        pts, mat, tag, seq = face[0], face[1], face[2], face[3]
        n = cam.face_normal(face)
        if _get(n, cam.v['dep']) <= 0.02:
            continue
        d = sum(cam.depth(p) for p in pts) / len(pts)
        vis.append((round(d, 4), seq, pts, mat, tag, n, None))
    if not silhouette:
        for di, (p, axis, sign, r, color, dtag) in enumerate(model.dots):
            if axis != cam.v['dep'] or sign <= 0:
                continue
            vis.append((round(cam.depth(p) - 0.004, 4), 10 ** 6 + di, None, None, None, None,
                        (p, r, color)))
    vis.sort(key=lambda t: (t[0], t[1]))

    y_lo, y_hi = model_y_range(model)
    dr = ImageDraw.Draw(cam.layer)
    for d, seq, pts, mat, tag, n, dot in vis:
        if dot is not None:
            p, r, color = dot
            x, y = cam.proj(p)
            rr = r * cam.pxt * cam.ss
            if rr < 1.1:
                continue
            c = PAL.get(color, color if isinstance(color, tuple) else (60, 60, 60))
            dr.ellipse([x - rr, y - rr, x + rr, y + rr], fill=c)
            continue
        pp = [cam.proj(p) for p in pts]
        if silhouette:
            dr.polygon(pp, fill=PAL['soot_black'])
            continue
        cy = sum(p[1] for p in pts) / len(pts)
        y_frac = 0.5 if y_hi <= y_lo else max(0.0, min(1.0, (cy - y_lo) / (y_hi - y_lo)))
        fill = _fill_for(mat, tag, team_rgb, n, cam, y_frac)
        dr.polygon(pp, fill=fill)
        if tag == 'glass':
            continue
        oc = _outline_for(fill)
        w = max(2, int(round(ow * ss)))
        dr.line(pp + [pp[0]], fill=oc, width=w, joint='curve')
    return cam.layer


def model_y_range(model):
    ys = [p[1] for f in model.faces for p in f[0]]
    return (min(ys), max(ys))


def model_bbox(model):
    xs = [p[0] for f in model.faces for p in f[0]]
    ys = [p[1] for f in model.faces for p in f[0]]
    zs = [p[2] for f in model.faces for p in f[0]]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))
