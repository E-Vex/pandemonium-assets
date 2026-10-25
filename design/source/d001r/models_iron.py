#!/usr/bin/env python3
"""D-001R Ironclad faction models (tile units).

Faction language: monolithic slab, thick symmetric riveted plating,
fortress architecture, gunmetal + bone_white with brass fittings.
Every total height matches Art Bible section 6 exactly.
"""
import math
from engine import Model


def artificer():
    """worker - 0.6 wide, 0.5 tall. Riveted exosuit engineer, steam vents."""
    m = Model('artificer')
    for s in (-1, 1):
        m.box(s * 0.10, 0.00, 0.08, s * 0.10 + 0.11, 0.06, 0.24, 'gunmetal')   # wide boots
        m.box(s * 0.08, 0.06, 0.10, s * 0.08 + 0.07, 0.19, 0.22, 'slate_steel')  # thick legs
    # boiler torso + trim band + rivets
    m.box(-0.17, 0.19, 0.02, 0.17, 0.41, 0.21, 'gunmetal')
    m.plate('z', +1, 0.0, 0.31, 0.212, 0.30, 0.06, 'bone_white')
    m.rivets((-0.14, 0.36, 0.212), (0.14, 0.36, 0.212), 'z', +1, 0.011, 'soot_black', 6)
    m.rivets((-0.14, 0.24, 0.212), (0.14, 0.24, 0.212), 'z', +1, 0.011, 'soot_black', 6)
    # boiler backpack shell (team zone 2) + steam vents
    m.box(-0.13, 0.21, -0.15, 0.13, 0.41, 0.01, 'team:2')
    m.ngon('y', (0.0, 0.41, -0.07), 0.13, 0.03, 'team:2', n=8)
    for sx in (-1, 1):
        m.ngon('y', (sx * 0.15, 0.28, -0.06), 0.024, 0.13, 'bright_steel', n=6)
        m.ngon('y', (sx * 0.15, 0.41, -0.06), 0.03, 0.015, 'soot_black', n=6)
    # dome helm (team zone 1) to exact 0.5
    m.box(-0.06, 0.41, 0.06, 0.06, 0.46, 0.17, 'slate_steel')
    m.ngon('y', (0.0, 0.44, 0.115), 0.095, 0.06, 'team:1', n=8)
    m.box(-0.10, 0.44, 0.05, 0.10, 0.46, 0.18, 'bone_white')                 # brow band
    # symmetric tool arms: wrench right, torch left
    m.box(0.18, 0.30, 0.04, 0.27, 0.40, 0.15, 'gunmetal')
    m.box(0.21, 0.18, 0.07, 0.25, 0.30, 0.12, 'slate_steel')
    m.box(0.19, 0.13, 0.05, 0.27, 0.18, 0.14, 'bright_steel')                # wrench head
    m.box(-0.27, 0.30, 0.04, -0.18, 0.40, 0.15, 'gunmetal')
    m.box(-0.25, 0.18, 0.07, -0.21, 0.30, 0.12, 'slate_steel')
    m.box(-0.24, 0.10, 0.06, -0.22, 0.18, 0.13, 'leather_brown')             # torch grip
    m.dot((-0.23, 0.09, 0.10), 'z', +1, 0.015, 'signal_yellow')
    # brass fittings + under-layer
    m.dot((0.0, 0.415, 0.115), 'z', +1, 0.012, 'signal_yellow')
    m.plate('z', +1, 0.0, 0.20, 0.212, 0.26, 0.05, 'slate_steel')
    return m


def legionnaire():
    """heavy infantry - 0.6 wide, 0.7 tall. Full-plate line infantry + slab shield."""
    m = Model('legionnaire')
    for s in (-1, 1):
        m.box(s * 0.07, 0.00, 0.10, s * 0.07 + 0.09, 0.06, 0.26, 'gunmetal')
    m.box(-0.07, 0.06, 0.12, -0.01, 0.27, 0.20, 'slate_steel')
    m.box(0.01, 0.06, 0.12, 0.07, 0.27, 0.20, 'slate_steel')
    m.box(-0.12, 0.27, 0.04, 0.12, 0.32, 0.20, 'gunmetal')                   # plate skirt
    m.box(-0.02, 0.27, 0.04, 0.02, 0.32, 0.20, 'soot_black')                 # skirt slit
    # torso + breastplate (team zone 1)
    m.box(-0.12, 0.32, 0.02, 0.12, 0.56, 0.19, 'gunmetal')
    m.plate('z', +1, 0.0, 0.44, 0.192, 0.22, 0.18, 'team:1')
    m.rivets((-0.10, 0.52, 0.194), (0.10, 0.52, 0.194), 'z', +1, 0.011, 'soot_black', 5)
    m.rivets((-0.10, 0.36, 0.194), (0.10, 0.36, 0.194), 'z', +1, 0.011, 'soot_black', 5)
    # pauldrons (shield side heavier)
    m.box(-0.21, 0.54, 0.04, -0.12, 0.63, 0.18, 'gunmetal')
    m.box(0.12, 0.54, 0.04, 0.19, 0.60, 0.18, 'gunmetal')
    m.plate('y', +1, -0.165, 0.632, 0.11, 0.16, 0.06, 'bone_white')
    # helm + crest (team zone 1) to exact 0.7
    m.box(-0.07, 0.56, 0.04, 0.07, 0.64, 0.18, 'slate_steel')
    m.box(-0.11, 0.58, 0.05, 0.11, 0.60, 0.19, 'bone_white')                 # brow band
    m.box(-0.025, 0.64, 0.02, 0.025, 0.70, 0.14, 'team:1')                   # crest
    # slab shield on LEFT arm
    m.box(-0.35, 0.26, 0.05, -0.25, 0.64, 0.17, 'slate_steel')
    m.plate('x', -1, -0.352, 0.45, 0.11, 0.16, 0.34, 'bone_white')
    m.dot((-0.36, 0.45, 0.11), 'x', -1, 0.03, 'gunmetal')
    m.rivets((-0.33, 0.60, 0.172), (-0.27, 0.60, 0.172), 'z', +1, 0.011, 'soot_black', 4)
    # rifle over the shield rim, held right (arm chain connects in every view)
    m.box(0.09, 0.47, -0.04, 0.11, 0.49, 0.50, 'soot_black')
    m.box(0.08, 0.44, 0.44, 0.12, 0.52, 0.54, 'gunmetal')                    # muzzle
    m.box(0.07, 0.40, -0.10, 0.13, 0.48, 0.00, 'leather_brown')
    m.box(0.12, 0.38, 0.06, 0.19, 0.48, 0.18, 'slate_steel')                 # right arm
    m.box(0.08, 0.40, 0.18, 0.16, 0.47, 0.30, 'slate_steel')                 # forearm fwd
    m.box(-0.23, 0.32, 0.08, -0.19, 0.42, 0.16, 'slate_steel')               # shield arm
    return m


def crawler():
    """heavy tank - 0.8 wide, 0.4 tall. Slab-armored crawler, wide treads."""
    m = Model('crawler')
    # hull + wedge glacis
    m.box(-0.30, 0.18, -0.62, 0.30, 0.30, 0.55, 'gunmetal')
    m.poly([(-0.30, 0.30, 0.55), (0.30, 0.30, 0.55), (0.24, 0.19, 0.76), (-0.24, 0.19, 0.76)],
           'slate_steel', n=(0.0, 0.33, 0.94))
    m.plate('z', +1, 0.0, 0.26, 0.762, 0.34, 0.10, 'bone_white')             # trim stripe
    # wide full-length tracks + tread links
    for sx in (-1, 1):
        m.box(sx * 0.30, 0.05, -0.70, sx * 0.30 + (0.13 if sx > 0 else 0.0) * sx * 0 + 0.13 * (1 if sx > 0 else -1) * 0 + 0.0,
              0.19, 0.70, 'slate_steel') if False else None
    for sx in (-1, 1):
        x0, x1 = (0.30, 0.43) if sx > 0 else (-0.43, -0.30)
        m.box(x0, 0.04, -0.70, x1, 0.19, 0.70, 'slate_steel')
        for i in range(12):
            z = -0.66 + i * 0.12
            m.box(x0, 0.0, z, x1, 0.055, z + 0.05, 'soot_black')
            m.box(x0, 0.185, z + 0.03, x1, 0.235, z + 0.08, 'soot_black')
        for zz in (-0.70, 0.70):
            m.dot((sx * 0.365, 0.115, zz + (0.02 if zz > 0 else -0.02)), 'x', sx, 0.045, 'gunmetal')
    # casemate to exact 0.4 + mantlet
    m.box(-0.22, 0.30, -0.28, 0.22, 0.40, 0.28, 'gunmetal')
    m.plate('y', +1, 0.0, 0.39, 0.0, 0.40, 0.50, 'bone_white')
    m.rivets((-0.18, 0.401, -0.24), (0.18, 0.401, -0.24), 'y', +1, 0.011, 'soot_black', 6)
    m.rivets((-0.18, 0.401, 0.20), (0.18, 0.401, 0.20), 'y', +1, 0.011, 'soot_black', 6)
    # gun barrel over the glacis
    m.box(-0.045, 0.31, 0.28, 0.045, 0.355, 0.82, 'soot_black')
    m.box(-0.06, 0.30, 0.24, 0.06, 0.375, 0.32, 'gunmetal')                  # mantlet block
    m.box(-0.055, 0.305, 0.82, 0.055, 0.36, 0.90, 'slate_steel')             # muzzle
    # engine deck cowl (team zone 1) + grille
    m.box(-0.24, 0.30, -0.62, 0.24, 0.36, -0.36, 'team:1')
    for i in range(4):
        m.dot((0.0, 0.33, -0.40 - i * 0.055), 'y', +1, 0.014, 'soot_black')
    # exhausts + rivet band + trim
    for sx in (-1, 1):
        m.ngon('y', (sx * 0.27, 0.30, -0.30), 0.022, 0.09, 'bright_steel', n=6)
    m.plate('x', +1, 0.302, 0.24, -0.1, 0.5, 0.06, 'bone_white')
    m.plate('x', -1, -0.302, 0.24, -0.1, 0.5, 0.06, 'bone_white')
    return m


def colossus():
    """super-heavy walker - 1.0 wide, 1.2 tall. Monolithic 4-legged siege walker."""
    m = Model('colossus')
    # monolithic torso + counterweight
    m.box(-0.34, 0.55, -0.35, 0.34, 0.95, 0.30, 'gunmetal')
    m.box(-0.30, 0.55, -0.52, 0.30, 0.82, -0.35, 'slate_steel')
    m.plate('z', +1, 0.0, 0.75, 0.302, 0.55, 0.28, 'bone_white')             # frontal trim
    m.rivets((-0.28, 0.88, 0.302), (0.28, 0.88, 0.302), 'z', +1, 0.012, 'soot_black', 7)
    m.rivets((-0.28, 0.62, 0.302), (0.28, 0.62, 0.302), 'z', +1, 0.012, 'soot_black', 7)
    # shoulder mantlets (team zone 1)
    for sx in (-1, 1):
        m.box(sx * 0.34, 0.75, -0.20, sx * 0.46, 0.98, 0.18, 'team:1')
        m.rivets((sx * 0.40, 0.965, -0.16), (sx * 0.40, 0.965, 0.14), 'y', +1, 0.012, 'soot_black', 5)
    # siege mortar tube to exact 1.2 + mount block
    m.ngon('y', (0.0, 0.95, 0.05), 0.095, 0.25, 'gunmetal', n=8)
    m.ngon('y', (0.0, 1.13, 0.05), 0.115, 0.07, 'slate_steel', n=8)
    m.box(-0.15, 0.88, -0.05, 0.15, 1.00, 0.15, 'gunmetal')                 # mortar mount
    m.box(-0.06, 1.00, -0.06, 0.06, 1.07, 0.16, 'slate_steel')               # collar
    # small head slit front-top (embedded into the torso mass - reads attached in side view)
    m.box(-0.10, 0.86, 0.20, 0.10, 1.04, 0.36, 'slate_steel')
    m.plate('z', +1, 0.0, 1.00, 0.362, 0.14, 0.025, 'glass_cyan', tag='glass')
    # four stumpy legs, splayed to exactly 1.0 wide
    for sx in (-1, 1):
        m.box(sx * 0.30, 0.45, -0.28, sx * 0.46, 0.55, 0.24, 'gunmetal')      # hips
        m.box(sx * 0.36, 0.18, -0.30, sx * 0.48, 0.45, 0.26, 'slate_steel')   # thighs out
        m.box(sx * 0.38, 0.05, -0.28, sx * 0.50, 0.18, 0.24, 'gunmetal')      # shins
        m.box(sx * 0.30, 0.0, -0.28, sx * 0.50, 0.06, 0.26, 'slate_steel')    # foot pads
        m.plate('y', +1, sx * 0.40, 0.062, -0.02, 0.16, 0.44, 'bone_white')
    # rear vents + hazard-free brass dot
    for sx in (-1, 1):
        m.ngon('y', (sx * 0.20, 0.62, -0.36), 0.02, 0.08, 'bright_steel', n=6)
    m.dot((0.0, 0.955, 0.05), 'y', +1, 0.02, 'signal_yellow')
    return m


def citadel():
    """headquarters - 4x4 tiles, 3.0 tall. Star-fort octagon keep + flag mast."""
    m = Model('citadel')
    P8 = math.pi / 8
    # octagon base ring (flats on the axes -> exactly 4.0 wide)
    m.ngon('y', (0.0, 0.0, 0.0), 2.165, 0.70, 'concrete', n=8, phase=P8)
    for i in range(8):
        a = math.pi / 8 + i * math.pi / 4
        gx, gz = 1.90 * math.cos(a), 1.90 * math.sin(a)
        m.box(gx - 0.09, 0.70, gz - 0.09, gx + 0.09, 0.84, gz + 0.09, 'gunmetal')  # crenels
    m.dot((0.0, 0.36, 2.005), 'z', +1, 0.05, 'soot_black')                   # gun slots
    m.dot((1.38, 0.36, 1.38), 'z', +1, 0.04, 'soot_black')
    m.dot((-1.38, 0.36, 1.38), 'z', +1, 0.04, 'soot_black')
    # mid keep + trim + rivet band
    m.ngon('y', (0.0, 0.70, 0.0), 1.35, 1.05, 'gunmetal', n=8, phase=P8)
    m.ngon('y', (0.0, 1.68, 0.0), 1.37, 0.07, 'bone_white', n=8, phase=P8)
    for i in range(8):
        a = math.pi / 8 + i * math.pi / 4
        m.dot((1.30 * math.cos(a), 1.2, 1.30 * math.sin(a)), 'z', +1, 0.013, 'soot_black')
    # gate + door frame (team zone 2)
    m.box(-0.30, 0.70, 1.10, 0.30, 1.40, 1.34, 'soot_black')
    m.box(-0.36, 0.70, 1.34, -0.28, 1.44, 1.42, 'team:2')
    m.box(0.28, 0.70, 1.34, 0.36, 1.44, 1.42, 'team:2')
    m.box(-0.36, 1.36, 1.34, 0.36, 1.44, 1.42, 'team:2')
    m.dot((0.0, 1.05, 1.42), 'z', +1, 0.03, 'signal_yellow')
    # top keep + crenellation
    m.ngon('y', (0.0, 1.75, 0.0), 0.85, 0.70, 'slate_steel', n=8, phase=P8)
    for i in range(8):
        a = math.pi / 8 + i * math.pi / 4
        gx, gz = 0.85 * math.cos(a), 0.85 * math.sin(a)
        m.box(gx - 0.07, 2.45, gz - 0.07, gx + 0.07, 2.60, gz + 0.07, 'gunmetal')
    # roof disc (team zone 1) + mast to exact 3.0 + flag
    m.ngon('y', (0.0, 2.60, 0.0), 0.56, 0.09, 'team:1', n=8, phase=P8)
    m.ngon('y', (0.0, 2.69, 0.0), 0.60, 0.03, 'bone_white', n=8, phase=P8)
    m.box(-0.025, 2.69, -0.025, 0.025, 3.00, 0.025, 'gunmetal')
    m.poly([(0.025, 2.86, 0.0), (0.30, 2.92, 0.0), (0.30, 3.00, 0.0), (0.025, 2.94, 0.0)],
           'team:2', n=(0.0, 0.0, 1.0))
    # corner bastion guns on base ring
    for (bx, bz) in ((1.45, 1.45), (-1.45, 1.45)):
        m.box(bx - 0.14, 0.70, bz - 0.14, bx + 0.14, 0.94, bz + 0.14, 'gunmetal')
        m.box(bx - 0.04, 0.76, bz + 0.14, bx + 0.04, 0.84, bz + 0.38, 'soot_black')
    return m


def forge():
    """production - 3x3 tiles, 1.2 body. Blast-chimney foundry hall + gantry."""
    m = Model('forge')
    m.box(-1.4, 0.0, -1.4, 1.4, 0.06, 1.4, 'concrete')
    # hall to 1.0 + parapet to 1.14 + team roof deck to 1.2
    m.box(-1.3, 0.06, -1.3, 1.3, 1.00, 1.3, 'gunmetal')
    for s in (-1, 1):
        m.box(-1.3, 1.00, s * 1.24, 1.3, 1.14, s * 1.30, 'slate_steel')      # parapets
        m.box(s * 1.24, 1.00, -1.3, s * 1.30, 1.14, 1.3, 'slate_steel')
    m.box(-1.05, 1.00, -1.05, 1.05, 1.14, 1.05, 'slate_steel')               # roof slab
    m.box(-0.95, 1.14, -0.95, 0.95, 1.20, 0.95, 'team:1')                    # roof deck panels
    m.rivets((-0.8, 1.202, -0.8), (0.8, 1.202, -0.8), 'y', +1, 0.014, 'soot_black', 8)
    m.rivets((-0.8, 1.202, 0.8), (0.8, 1.202, 0.8), 'y', +1, 0.014, 'soot_black', 8)
    # blast chimney to 1.5 with team cap band
    m.ngon('y', (0.85, 1.00, -0.75), 0.30, 0.44, 'slate_steel', n=8)
    m.ngon('y', (0.85, 1.44, -0.75), 0.32, 0.06, 'team:1', n=8)
    m.ngon('y', (0.85, 1.50, -0.75), 0.22, 0.02, 'soot_black', n=8)
    # gantry portal + trolley + hook
    for sx in (-1, 1):
        m.box(sx * 1.08 - 0.05, 1.14, -0.35, sx * 1.08 + 0.05, 1.30, -0.25, 'gunmetal')
    m.box(-1.2, 1.30, -0.33, 1.2, 1.38, -0.27, 'slate_steel')
    m.box(-0.16, 1.24, -0.36, 0.16, 1.32, -0.24, 'gunmetal')
    m.box(-0.025, 0.70, -0.315, 0.025, 1.24, -0.275, 'soot_black')
    m.box(-0.09, 0.62, -0.35, 0.09, 0.70, -0.24, 'bright_steel')
    # bay door (production signature): dark opening + slats + interior glow strip
    m.box(-0.80, 0.06, 1.28, 0.80, 0.92, 1.31, 'soot_black')
    m.box(-0.80, 0.66, 1.27, 0.80, 0.92, 1.30, 'slate_steel')
    for i in range(4):
        m.box(-0.80, 0.70 + i * 0.055, 1.28, 0.80, 0.74 + i * 0.055, 1.32, 'slate_steel')
    m.box(-0.70, 0.50, 1.285, 0.70, 0.56, 1.295, 'glass_cyan', 'glass')      # interior beacon
    m.plate('z', +1, -0.90, 0.5, 1.312, 0.16, 0.8, 'bone_white')             # door trim
    m.plate('z', +1, 0.90, 0.5, 1.312, 0.16, 0.8, 'bone_white')
    # wall trim band + vents + rivets
    m.plate('z', +1, 0.0, 0.30, 1.302, 2.4, 0.10, 'bone_white')
    for i in range(2):
        m.ngon('y', (-0.75, 1.00, -1.0 + i * 0.55), 0.05, 0.10, 'bright_steel', n=6)
    m.rivets((-1.2, 0.5, 1.302), (-0.4, 0.5, 1.302), 'z', +1, 0.013, 'soot_black', 5)
    m.rivets((0.4, 0.5, 1.302), (1.2, 0.5, 1.302), 'z', +1, 0.013, 'soot_black', 5)
    # corner buttresses
    for sx in (-1, 1):
        m.poly([(sx * 1.30, 0.06, 1.30), (sx * 1.30, 1.00, 1.30), (sx * 1.52, 0.06, 1.52),
                (sx * 1.30, 0.06, 1.30)], 'concrete', n=(0.0, 0.0, 0.0)) if False else None
        m.box(sx * 1.24, 0.06, 1.24, sx * 1.44, 0.72, 1.44, 'concrete')
    return m


def bastion():
    """defense turret - 2x2 tiles, 1.5 tall. Octagon base + one massive gun."""
    m = Model('bastion')
    P8 = math.pi / 8
    m.ngon('y', (0.0, 0.0, 0.0), 1.083, 0.55, 'concrete', n=8, phase=P8)      # flats = 2.0
    for i in range(8):
        a = math.pi / 8 + i * math.pi / 4
        m.dot((1.02 * math.cos(a), 0.28, 1.02 * math.sin(a)), 'z', +1, 0.016, 'soot_black')
    m.plate('z', +1, 0.0, 0.16, 1.005, 1.3, 0.10, 'bone_white')               # frontal trim
    # pedestal + ammo hatch
    m.box(-0.60, 0.55, -0.60, 0.60, 0.80, 0.60, 'gunmetal')
    m.box(0.34, 0.80, -0.50, 0.56, 0.92, -0.28, 'slate_steel')
    m.rivets((-0.5, 0.68, 0.602), (0.5, 0.68, 0.602), 'z', +1, 0.014, 'soot_black', 6)
    # mantlet ring (team zone 1) + trunnion
    m.ngon('y', (0.0, 0.80, 0.0), 0.52, 0.30, 'team:1', n=8, phase=P8)
    for i in range(8):
        a = P8 + i * math.pi / 4
        m.dot((0.50 * math.cos(a), 0.95, 0.50 * math.sin(a)), 'z', +1, 0.015, 'soot_black')
    m.box(-0.22, 1.10, -0.22, 0.22, 1.38, 0.30, 'gunmetal')
    # massive gun: barrel tip at exact 1.5
    m.box(-0.11, 1.32, 0.30, 0.11, 1.50, 0.62, 'soot_black')
    m.box(-0.14, 1.29, 0.62, 0.14, 1.50, 0.78, 'slate_steel')
    m.box(-0.09, 1.31, 0.78, 0.09, 1.49, 1.24, 'soot_black')
    m.box(-0.13, 1.27, 1.24, 0.13, 1.50, 1.40, 'gunmetal')                   # muzzle brake
    m.box(-0.05, 1.32, 1.40, 0.05, 1.50, 1.46, 'soot_black')
    # rear counterweight + vents
    m.box(-0.40, 1.05, -0.72, 0.40, 1.40, -0.36, 'slate_steel')
    m.plate('z', -1, 0.0, 1.22, -0.722, 0.6, 0.24, 'bone_white')
    for sx in (-1, 1):
        m.ngon('y', (sx * 0.30, 0.62, 0.55), 0.025, 0.10, 'bright_steel', n=6)
    return m


IRON_ROSTER = {
    'artificer': dict(kind='worker', view_lineup='front', fp='0.6',
                      zones=['dome helm', 'boiler shell'],
                      notes=['symmetric riveted exosuit - boiler backpack, steam vents']),
    'legionnaire': dict(kind='rifleman', view_lineup='front', fp='0.6',
                        zones=['breastplate + helm crest'],
                        notes=['slab shield carries the read; crest marks the height']),
    'crawler': dict(kind='raider', view_lineup='side', fp='0.8',
                    zones=['engine deck cowl'],
                    notes=['full-length wide treads, slab glacis, one gun axis']),
    'colossus': dict(kind='guardian', view_lineup='side', fp='1.0',
                     zones=['shoulder mantlets'],
                     notes=['boulder mass, four stumpy legs, siege mortar tube to 1.2 t']),
    'citadel': dict(kind='command_center', view_lineup='front', fp='4x4',
                    zones=['roof disc', 'gate door frame'],
                    notes=['stepped octagon keep; mast to 3.0 t - nothing builds taller']),
    'forge': dict(kind='barracks', view_lineup='front', fp='3x3',
                  zones=['roof deck panels'],
                  notes=['barn hall + one blast chimney (1.5 t protrusion, turret-line)']),
    'bastion': dict(kind='turret', view_lineup='front', fp='2x2',
                    zones=['mantlet ring'],
                    notes=['pedestal + one gun axis; barrel tip at 1.5 t']),
}

BUILDERS = {'artificer': artificer, 'legionnaire': legionnaire, 'crawler': crawler,
            'colossus': colossus, 'citadel': citadel, 'forge': forge, 'bastion': bastion}
