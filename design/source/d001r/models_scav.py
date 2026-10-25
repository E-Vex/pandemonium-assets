#!/usr/bin/env python3
"""D-001R Scavenger faction models (tile units).

Faction language: jagged asymmetric silhouettes, mismatched plates,
tarps, exposed wheels/pipes, rust + canvas weighting.
Every total height matches Art Bible section 6 exactly.
"""
import math
from engine import Model

T = math.pi


def salvager():
    """worker - 0.6 wide, 0.5 tall. Hunched, oversized right tool arm."""
    m = Model('salvager')
    # boots + bent legs
    for s in (-1, 1):
        m.box(s * 0.05, 0.00, 0.10, s * 0.05 + 0.10, 0.05, 0.24, 'leather_brown')
    m.box(-0.08, 0.05, 0.13, -0.02, 0.21, 0.19, 'gunmetal')
    m.box(0.02, 0.05, 0.13, 0.08, 0.21, 0.19, 'rust')
    # hunched torso (leans forward)
    m.box(-0.14, 0.20, 0.00, 0.14, 0.39, 0.21, 'gunmetal')
    m.plate('z', +1, 0.00, 0.30, 0.212, 0.20, 0.10, 'slate_steel')          # chest plate
    m.plate('z', +1, 0.07, 0.25, 0.212, 0.07, 0.06, 'rust', tilt=0.25)     # scrap patch
    # backpack shell (team zone 2) + tarp roll
    m.box(-0.11, 0.22, -0.15, 0.05, 0.37, 0.00, 'team:2')
    m.ngon('x', (-0.16, 0.37, -0.07), 0.045, 0.15, 'canvas_tan', n=8)       # tarp roll
    m.box(-0.05, 0.22, -0.15, 0.05, 0.26, -0.10, 'leather_brown')           # strapped crate
    for i in range(3):
        m.dot((-0.03 + i * 0.03, 0.34, 0.002), 'z', +1, 0.010, 'soot_black')
    # head + hard hat (team zone 1)
    m.box(-0.05, 0.39, 0.07, 0.05, 0.46, 0.16, 'slate_steel')
    m.box(-0.07, 0.46, 0.04, 0.07, 0.50, 0.18, 'team:1')
    m.box(-0.08, 0.46, 0.16, 0.08, 0.48, 0.20, 'team:1')                    # brim
    # oversized RIGHT tool arm
    m.box(0.14, 0.28, 0.05, 0.28, 0.38, 0.15, 'gunmetal')                   # big shoulder
    m.plate('x', +1, 0.282, 0.33, 0.10, 0.09, 0.07, 'rust', tilt=0.3)
    m.box(0.17, 0.19, 0.08, 0.24, 0.29, 0.14, 'slate_steel')                # upper arm
    m.box(0.16, 0.20, 0.13, 0.23, 0.26, 0.31, 'gunmetal')                   # forearm fwd
    m.box(0.15, 0.26, 0.29, 0.24, 0.31, 0.35, 'rust')                       # claw base
    m.box(0.16, 0.31, 0.30, 0.23, 0.36, 0.34, 'slate_steel')                # upper jaw
    m.box(0.17, 0.21, 0.32, 0.22, 0.26, 0.36, 'slate_steel')                # lower jaw
    # slim left arm out for balance
    m.box(-0.27, 0.22, 0.05, -0.19, 0.33, 0.12, 'slate_steel')
    m.box(-0.25, 0.12, 0.08, -0.21, 0.22, 0.14, 'gunmetal')
    # junk: pipe on shoulder, rope coil
    m.ngon('y', (-0.13, 0.39, 0.10), 0.02, 0.11, 'slate_steel', n=6)
    m.ngon('z', (0.11, 0.24, -0.06), 0.05, 0.03, 'leather_brown', n=8)
    return m


def ratter():
    """light infantry - 0.6 wide, 0.7 tall. Pipe rifle held out horizontally."""
    m = Model('ratter')
    for s in (-1, 1):
        m.box(s * 0.06, 0.00, 0.12, s * 0.06 + 0.09, 0.05, 0.26, 'leather_brown')
    m.box(-0.07, 0.05, 0.14, -0.01, 0.27, 0.20, 'gunmetal')
    m.box(0.01, 0.05, 0.14, 0.07, 0.27, 0.20, 'gunmetal')
    # torso + vest (team zone 1)
    m.box(-0.11, 0.26, 0.03, 0.11, 0.50, 0.19, 'olive_drab')
    m.box(-0.12, 0.30, 0.19, 0.12, 0.46, 0.23, 'team:1')
    m.box(-0.12, 0.26, 0.05, 0.12, 0.30, 0.21, 'leather_brown')              # belt
    m.box(-0.10, 0.26, 0.06, -0.02, 0.30, 0.14, 'rust')                     # pouch
    m.box(0.03, 0.26, 0.06, 0.10, 0.30, 0.14, 'rust')
    # head + bucket helmet (team zone 1) + comm whisker to exact 0.7
    m.box(-0.045, 0.50, 0.06, 0.045, 0.58, 0.16, 'slate_steel')
    m.box(-0.075, 0.58, 0.03, 0.075, 0.68, 0.22, 'team:1')
    m.box(-0.09, 0.58, 0.18, 0.09, 0.60, 0.25, 'team:1')                    # brim fwd
    m.box(-0.06, 0.68, 0.08, -0.045, 0.70, 0.10, 'slate_steel')             # comm whisker
    # pipe rifle: one long horizontal line out front
    m.box(0.05, 0.40, -0.02, 0.07, 0.42, 0.46, 'soot_black')                # barrel
    m.box(0.045, 0.42, 0.18, 0.075, 0.45, 0.24, 'rust')                     # pipe fitting
    m.box(0.045, 0.37, 0.34, 0.075, 0.40, 0.42, 'slate_steel')              # front sight
    m.box(0.03, 0.36, -0.08, 0.09, 0.44, 0.00, 'leather_brown')             # stock
    # arms: right forward under barrel, left out
    m.box(0.10, 0.32, 0.10, 0.17, 0.42, 0.24, 'olive_drab')
    m.box(-0.30, 0.30, 0.06, -0.20, 0.44, 0.13, 'olive_drab')
    m.box(-0.28, 0.20, 0.08, -0.24, 0.30, 0.13, 'gunmetal')
    # one shoulder pad (asymmetric) + scrap patch
    m.box(0.10, 0.50, 0.06, 0.17, 0.545, 0.17, 'rust')
    m.plate('z', +1, -0.04, 0.36, 0.232, 0.08, 0.07, 'rust', tilt=-0.2)
    return m


def scrap_hound():
    """fast raider - 0.8 wide, 0.4 tall. Long low wedge buggy, exposed wheels."""
    m = Model('scrap_hound')
    # frame + hull
    m.box(-0.22, 0.16, -0.60, 0.22, 0.28, 0.45, 'gunmetal')
    for s in (-1, 1):
        m.box(s * 0.16, 0.10, -0.55, s * 0.16 + 0.06, 0.16, 0.40, 'soot_black')  # frame rails
    # wedged hood front
    m.box(-0.20, 0.28, 0.45, 0.20, 0.34, 0.56, 'slate_steel')
    m.poly([(-0.20, 0.28, 0.56), (0.20, 0.28, 0.56), (0.16, 0.18, 0.66), (-0.16, 0.18, 0.66)],
           'rust', n=(0.0, 0.58, 0.81))                                       # nose plate
    # jagged ram spikes (heights jittered)
    for i, (hx, hh) in enumerate([(-0.16, 0.36), (-0.08, 0.33), (0.0, 0.38), (0.08, 0.34), (0.16, 0.36)]):
        m.box(hx - 0.025, 0.22, 0.64, hx + 0.025, hh, 0.70, 'slate_steel')
    # engine cowl (team zone 1) rear
    m.box(-0.16, 0.28, -0.60, 0.16, 0.38, -0.34, 'team:1')
    for i in range(4):
        m.dot((0.0, 0.33, -0.37 - i * 0.06), 'z', +1, 0.014, 'soot_black')
    # roll cage to exact 0.4
    for sx in (-1, 1):
        for sz in (-0.28, 0.08):
            m.box(sx * 0.15 - 0.02, 0.28, sz - 0.02, sx * 0.15 + 0.02, 0.37, sz + 0.02, 'slate_steel')
    for sx in (-1, 1):
        m.box(sx * 0.15 - 0.02, 0.37, -0.30, sx * 0.15 + 0.02, 0.40, 0.10, 'slate_steel')  # rails
    m.box(-0.17, 0.37, -0.06, 0.17, 0.40, -0.02, 'slate_steel')
    # seat + tarp scrap
    m.box(-0.08, 0.28, -0.18, 0.08, 0.36, -0.05, 'leather_brown')
    m.tarp((0.0, 0.37, -0.14), 0.24, 0.14, sag=0.02, tilt=0.0)
    # exhaust stack
    m.ngon('y', (0.18, 0.28, -0.26), 0.026, 0.11, 'slate_steel', n=6)
    m.ngon('y', (0.18, 0.39, -0.26), 0.03, 0.012, 'soot_black', n=6)
    # exposed outboard wheels (axle arms)
    for sx in (-1, 1):
        for wz in (0.30, -0.46):
            m.box(sx * 0.22 - (0.0 if sx > 0 else 0.09), 0.13, wz - 0.03,
                  sx * 0.22 + (0.09 if sx > 0 else 0.0), 0.19, wz + 0.03, 'soot_black')
            m.wheel(sx * 0.345, 0.14, wz, 0.14, 0.10, hub='rust')
    # junk: jerry can, chain, patches
    m.box(0.10, 0.28, -0.30, 0.17, 0.36, -0.22, 'olive_drab')
    m.plate('x', +1, 0.222, 0.22, -0.10, 0.14, 0.10, 'rust', tilt=0.2)
    m.plate('x', -1, -0.222, 0.22, 0.05, 0.14, 0.08, 'rust', tilt=-0.15)
    m.plate('z', +1, 0.0, 0.31, 0.562, 0.30, 0.05, 'soot_black', tilt=0.1)   # grille slots
    return m


def ram():
    """improvised heavy - 1.0 wide, 1.2 tall. Armored scrap truck + dozer blade."""
    m = Model('ram')
    # chassis + rails
    m.box(-0.38, 0.30, -0.80, 0.38, 0.42, 0.72, 'gunmetal')
    for s in (-1, 1):
        m.box(s * 0.30, 0.24, -0.72, s * 0.30 + 0.07, 0.30, 0.64, 'soot_black')
    # 3 axles / wheels (same count in every view): front + rear pair
    for wz in (0.45, -0.35, -0.62):
        m.box(-0.44, 0.13, wz - 0.05, 0.44, 0.17, wz + 0.05, 'soot_black')
        for sx in (-1, 1):
            m.wheel(sx * 0.42, 0.15, wz, 0.15, 0.16, hub='slate_steel')
    # hood + grille + headlights
    m.box(-0.36, 0.42, 0.72, 0.36, 0.62, 0.95, 'slate_steel')
    m.plate('z', +1, 0.0, 0.52, 0.952, 0.62, 0.16, 'soot_black')
    for sx in (-1, 1):
        m.ngon('z', (sx * 0.26, 0.48, 0.955), 0.035, 0.012, 'signal_yellow', n=8)
    m.plate('z', +1, 0.24, 0.57, 0.952, 0.10, 0.05, 'rust', tilt=0.3)        # mismatched fender
    m.plate('z', +1, -0.27, 0.50, 0.952, 0.08, 0.07, 'rust', tilt=-0.25)
    # armored cab + roof mantlet (team zone 1) + glass
    m.box(-0.36, 0.42, 0.28, 0.36, 1.02, 0.72, 'gunmetal')
    m.box(-0.30, 1.02, 0.30, 0.30, 1.08, 0.70, 'team:1')
    m.rivets((-0.24, 1.03, 0.705), (0.24, 1.03, 0.705), 'z', +1, 0.012, 'soot_black', 7)
    m.box(-0.28, 0.78, 0.72, 0.28, 1.00, 0.745, 'glass_cyan', 'glass')
    for sx in (-1, 1):                                                       # side window slits
        m.box(sx * 0.36 - (0.0 if sx > 0 else 0.005), 0.78, 0.44,
              sx * 0.36 + (0.005 if sx > 0 else 0.0), 0.98, 0.62, 'glass_cyan', 'glass')
    # cab side door panels (team zone 2)
    for sx in (-1, 1):
        m.plate('x', sx, sx * 0.362, 0.66, 0.50, 0.34, 0.26, 'team:2', tilt=0.0)
    m.plate('x', +1, 0.362, 0.60, 0.50, 0.10, 0.09, 'rust', tilt=0.35)       # bolted patch
    m.plate('x', -1, -0.362, 0.70, 0.55, 0.12, 0.08, 'rust', tilt=-0.3)
    # bed + tarp hoop cover (same tarp in every view)
    m.box(-0.38, 0.42, -0.80, 0.38, 0.50, 0.28, 'slate_steel')
    for s in (-1, 1):
        m.box(s * 0.32, 0.50, -0.76, s * 0.32 + 0.06, 0.56, 0.24, 'gunmetal')
    m.poly([(-0.34, 0.56, -0.76), (0.34, 0.56, -0.76), (0.0, 0.86, -0.26)],
           'canvas_tan', n=(0.0, 0.0, -1))                                   # tarp end cap rear
    m.poly([(-0.34, 0.56, 0.24), (0.34, 0.56, 0.24), (0.0, 0.86, -0.26)],
           'canvas_tan', n=(0.0, 0.0, 1))                                    # tarp end cap front
    for zz in (-0.62, -0.26, 0.10):                                          # hoops
        m.box(-0.36, 0.56, zz - 0.025, 0.36, 0.87, zz + 0.025, 'canvas_tan')
    for sx in (-1, 1):                                                       # tarp slopes
        m.poly([(sx * 0.35, 0.56, -0.76), (sx * 0.35, 0.56, 0.24),
                (sx * 0.02, 0.86, -0.26)], 'canvas_tan',
               n=(sx * 0.67, 0.74, 0.0))
    for zz in (-0.50, 0.02):                                                 # straps
        m.box(-0.37, 0.56, zz - 0.02, 0.37, 0.88, zz + 0.02, 'soot_black')
    # exhaust stack offset LEFT to exact 1.2
    m.ngon('y', (-0.30, 0.50, 0.16), 0.036, 0.66, 'slate_steel', n=6)
    m.ngon('y', (-0.30, 1.16, 0.16), 0.042, 0.04, 'soot_black', n=6)
    # spare tire bolted on right bed side + jerry cans left
    m.ngon('z', (0.40, 0.60, -0.10), 0.14, 0.11, 'soot_black', n=10)
    m.ngon('z', (0.46, 0.60, -0.10), 0.06, 0.015, 'rust', n=8)
    m.box(-0.46, 0.50, -0.52, -0.38, 0.62, -0.36, 'rust')
    m.box(-0.46, 0.50, -0.32, -0.38, 0.62, -0.16, 'olive_drab')
    # ---- DOZER BLADE (improvised: bolted scrap plate, twin hydraulic arms)
    m.poly([(-0.22, 0.12, 1.055), (0.22, 0.12, 1.055), (0.22, 0.66, 0.955), (-0.22, 0.66, 0.955)],
           'rust', n=(0.0, 0.17, 0.985))                                     # center panel
    for sx in (-1, 1):                                                       # wing panels angled back
        m.poly([(sx * 0.22, 0.14, 1.03), (sx * 0.50, 0.14, 0.86), (sx * 0.50, 0.60, 0.78),
                (sx * 0.22, 0.64, 0.95)], 'slate_steel',
               n=(sx * 0.41, 0.12, 0.90 if sx < 0 else 0.90) if sx < 0 else (0.41, 0.12, 0.90))
    m.poly([(-0.22, 0.64, 0.955), (0.22, 0.64, 0.955), (0.22, 0.70, 0.925), (-0.22, 0.70, 0.925)],
           'soot_black', n=(0.0, 0.45, 0.89))                                # top lip
    for i in range(7):                                                       # hazard stripes on lip
        x0 = -0.21 + i * 0.062
        m.poly([(x0, 0.64, 0.953), (x0 + 0.031, 0.64, 0.953), (x0 + 0.031, 0.70, 0.923),
                (x0, 0.70, 0.923)], 'signal_yellow' if i % 2 == 0 else 'soot_black',
               n=(0.0, 0.45, 0.89))
    m.box(-0.22, 0.10, 1.02, 0.22, 0.14, 1.06, 'soot_black')                 # cutting edge
    for sx in (-1, 1):                                                       # twin hydraulic arms
        m.box(sx * 0.26 - 0.035, 0.46, 0.72, sx * 0.26 + 0.035, 0.54, 0.84, 'gunmetal')
        m.box(sx * 0.26 - 0.045, 0.50, 0.84, sx * 0.26 + 0.045, 0.64, 0.92, 'bright_steel')
        m.box(sx * 0.26 - 0.025, 0.44, 0.90, sx * 0.26 + 0.025, 0.66, 0.955, 'gunmetal')
    m.plate('z', +1, 0.10, 0.40, 1.058, 0.10, 0.14, 'slate_steel', tilt=0.18)  # bolted blade patch
    m.plate('z', +1, -0.12, 0.26, 1.052, 0.12, 0.10, 'rust', tilt=-0.22)
    for i in range(4):                                                       # blade bolts
        m.dot((-0.16 + i * 0.10, 0.50, 1.06), 'z', +1, 0.011, 'soot_black')
    return m


def scrap_yard():
    """headquarters - 4x4 tiles, 3.0 tall. Container stack + lattice crane."""
    m = Model('scrap_yard')
    m.box(-2.0, 0.0, -2.0, 2.0, 0.07, 2.0, 'concrete')                       # pad
    # container stack (mismatched)
    m.box(-1.6, 0.07, -0.2, -0.4, 0.45, 1.6, 'rust')
    m.plate('z', +1, -1.0, 0.26, 1.602, 1.1, 0.26, 'slate_steel')
    m.box(-0.3, 0.07, -1.6, 0.9, 0.45, 0.0, 'olive_drab')
    m.box(-1.3, 0.45, -0.4, 0.3, 0.83, 1.2, 'gunmetal')
    m.plate('z', +1, -0.5, 0.64, 1.202, 0.7, 0.22, 'rust', tilt=0.1)
    # office cab on top + roof disc (team zone 1)
    m.box(-0.2, 0.83, -1.2, 0.6, 1.12, -0.2, 'slate_steel')
    m.ngon('y', (0.2, 1.12, -0.7), 0.24, 0.06, 'team:1', n=8)
    # door frame (team zone 2) on container A front
    m.box(-1.55, 0.10, 1.60, -1.43, 0.45, 1.68, 'team:2')
    m.box(-0.57, 0.10, 1.60, -0.45, 0.45, 1.68, 'team:2')
    m.box(-1.55, 0.36, 1.60, -0.45, 0.45, 1.68, 'team:2')
    m.box(-1.43, 0.10, 1.58, -0.57, 0.36, 1.60, 'soot_black')
    # lattice crane at NE corner to exact 3.0
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box(1.52 + sx * 0.07, 0.07, 1.52 + sz * 0.07, 1.52 + sx * 0.07 + 0.06,
                  2.88, 1.52 + sz * 0.07 + 0.06, 'gunmetal')
    for yv in (0.6, 1.4, 2.2):
        m.box(1.50, yv, 1.50, 1.66, yv + 0.05, 1.66, 'slate_steel')
    m.box(1.42, 1.20, 1.42, 1.74, 1.58, 1.74, 'slate_steel')                 # crane cab
    m.plate('z', +1, 1.58, 1.39, 1.742, 0.22, 0.18, 'glass_cyan', tag='glass')
    m.box(-0.6, 2.42, 1.44, 1.52, 2.54, 1.58, 'gunmetal')                    # jib beam
    m.poly([(1.52, 2.54, 1.51), (-0.6, 2.42, 1.51), (-0.6, 2.42, 1.47), (1.52, 2.54, 1.47)],
           'slate_steel', n=(0.0, 0.94, -0.34))                              # tie rod
    m.box(-0.62, 0.90, 1.44, -0.58, 2.42, 1.58, 'soot_black')                # hook cable
    m.box(-0.72, 0.78, 1.38, -0.48, 0.90, 1.64, 'rust')                      # hook block
    m.box(1.44, 2.88, 1.44, 1.72, 3.00, 1.72, 'signal_yellow')               # mast head
    m.box(1.48, 2.94, 1.48, 1.68, 3.00, 1.68, 'soot_black')                   # beacon plate
    # tarp awning between containers
    for (px, pz) in ((-1.5, 1.7), (0.7, 1.7)):
        m.box(px, 0.07, pz, px + 0.06, 1.0, pz + 0.06, 'slate_steel')
    m.tarp((-0.4, 1.02, 1.52), 2.1, 0.85, sag=0.09, tilt=0.06)
    # junk piles
    m.box(1.0, 0.07, -0.6, 1.7, 0.30, 0.1, 'rust')
    m.box(1.1, 0.30, -0.5, 1.5, 0.42, -0.2, 'slate_steel')
    m.ngon('y', (1.25, 0.30, 0.35), 0.16, 0.16, 'soot_black', n=10)          # tire pile
    m.ngon('y', (1.25, 0.46, 0.35), 0.16, 0.14, 'soot_black', n=10)
    m.box(-1.8, 0.07, -1.9, -1.2, 0.25, -1.3, 'leather_brown')               # crate
    for i in range(4):                                                       # hazard stripes at crane base
        m.box(1.46, 0.07 + i * 0.0, 1.62, 1.70, 0.13, 1.66, 'signal_yellow' if i % 2 == 0 else 'soot_black')
    return m


def garage():
    """production - 3x3 tiles, 1.2 tall. Tarp-door corrugated workshop."""
    m = Model('garage')
    m.box(-1.35, 0.0, -1.35, 1.35, 0.06, 1.35, 'concrete')
    # hall
    m.box(-1.15, 0.06, -1.5, 1.15, 0.85, 1.5, 'slate_steel')
    for i in range(11):                                                      # corrugation ribs
        x = -1.05 + i * 0.21
        m.box(x, 0.06, 1.50, x + 0.05, 0.85, 1.53, 'gunmetal')
    # gable roof (team zone 1) to exact 1.2 + ridge
    for sx in (-1, 1):
        m.poly([(sx * 1.25, 0.85, -1.50), (sx * 1.25, 0.85, 1.50), (0.0, 1.20, 1.50),
                (0.0, 1.20, -1.50)], 'team:1', n=(sx * 0.872, 0.49, 0.0))
    m.box(-0.08, 1.16, -1.50, 0.08, 1.20, 1.50, 'team:2')                   # ridge trim
    m.poly([(-1.15, 0.85, 1.50), (0.0, 1.20, 1.50), (1.15, 0.85, 1.50)],
           'gunmetal', n=(0.0, 0.0, 1.0))                                    # gable end wall (front)
    m.poly([(1.15, 0.85, -1.50), (0.0, 1.20, -1.50), (-1.15, 0.85, -1.50)],
           'gunmetal', n=(0.0, 0.0, -1.0))                                   # gable end wall (rear)
    # BIG tarp roll-up door
    m.box(-0.72, 0.06, 1.50, 0.72, 0.76, 1.53, 'soot_black')
    m.ngon('x', (-0.725, 0.79, 1.50), 0.07, 1.45, 'canvas_tan', n=8)          # rolled tarp
    m.box(-0.72, 0.10, 1.53, 0.72, 0.74, 1.55, 'canvas_tan')                # tarp sheet
    for i in range(4):
        m.box(-0.74, 0.16 + i * 0.15, 1.52, 0.74, 0.21 + i * 0.15, 1.56, 'soot_black')
    m.plate('z', +1, -0.90, 0.45, 1.532, 0.18, 0.5, 'rust')                  # door frame scrap
    m.plate('z', +1, 0.90, 0.45, 1.532, 0.18, 0.5, 'rust')
    # lean-to with sloped tarp roof (kept inside the 3x3 rectangle)
    m.box(1.15, 0.06, -0.8, 1.5, 0.45, 0.8, 'gunmetal')
    m.poly([(1.12, 0.58, -0.82), (1.12, 0.58, 0.82), (1.50, 0.42, 0.82), (1.50, 0.42, -0.82)],
           'canvas_tan', n=(-0.39, 0.92, 0.0))
    # exhaust pipe to exact 1.2
    m.ngon('y', (-0.85, 0.06, -1.30), 0.045, 1.14, 'slate_steel', n=6)
    m.box(-0.91, 1.14, -1.36, -0.79, 1.20, -1.24, 'soot_black')
    # junk by the door, inside the footprint: tires, barrel, crate
    m.ngon('y', (0.95, 0.07, 1.25), 0.17, 0.17, 'soot_black', n=10)
    m.ngon('y', (0.95, 0.24, 1.25), 0.17, 0.15, 'soot_black', n=10)
    m.ngon('y', (0.30, 0.07, 1.28), 0.14, 0.40, 'rust', n=8)
    m.box(-1.05, 0.06, 1.08, -0.65, 0.34, 1.42, 'leather_brown')
    m.plate('z', +1, -0.62, 0.62, 1.532, 0.16, 0.1, 'signal_yellow')         # hazard chip
    return m


def stash():
    """supply - 2x2 tiles, 0.9 tall. Crate + drum cache under tarp canopy."""
    m = Model('stash')
    m.box(-0.85, 0.0, -0.85, 0.85, 0.05, 0.85, 'leather_brown')              # pallet
    for i in range(5):
        m.box(-0.85, 0.0, -0.75 + i * 0.38, 0.85, 0.012, -0.71 + i * 0.38, 'soot_black')
    # crate stack
    m.box(-0.62, 0.05, -0.55, -0.18, 0.42, -0.12, 'leather_brown')
    m.box(-0.14, 0.05, -0.55, 0.30, 0.42, -0.12, 'leather_brown')
    m.box(-0.40, 0.42, -0.50, 0.04, 0.74, -0.08, 'leather_brown')
    m.plate('y', +1, -0.40, 0.742, -0.29, 0.42, 0.38, 'slate_steel')         # lid straps
    m.plate('y', +1, -0.18, 0.742, -0.29, 0.30, 0.30, 'rust')
    # fuel drums (caps = team zone 1) + side band (team zone 2)
    for (dx, dz) in ((0.55, -0.45), (0.55, 0.02)):
        m.ngon('y', (dx, 0.05, dz), 0.14, 0.42, 'rust', n=8)
        m.ngon('y', (dx, 0.47, dz), 0.15, 0.02, 'team:1', n=8)
    m.ngon('y', (0.55, 0.47, -0.215), 0.14, 0.37, 'olive_drab', n=8)         # stacked drum
    m.ngon('y', (0.55, 0.84, -0.215), 0.15, 0.02, 'team:1', n=8)
    m.plate('x', +1, 0.70, 0.26, -0.215, 0.72, 0.34, 'team:2')               # drum band
    # canopy posts + tarp to exact 0.9
    for sx in (-1, 1):
        for sz in (-1, 1):
            m.box(sx * 0.82 - 0.03, 0.0, sz * 0.82 - 0.03, sx * 0.82 + 0.03, 0.86, sz * 0.82 + 0.03,
                  'slate_steel')
    for sx in (-1, 1):                                                       # ridge beam + slopes
        m.box(sx * 0.88 - 0.03, 0.84, -0.03, sx * 0.88 + 0.03, 0.88, 0.03, 'gunmetal')
    m.poly([(-0.88, 0.62, -0.90), (0.88, 0.62, -0.90), (0.88, 0.90, 0.0), (-0.88, 0.90, 0.0)],
           'canvas_tan', n=(0.0, 0.447, 0.894))
    m.poly([(-0.88, 0.62, 0.90), (0.88, 0.62, 0.90), (0.88, 0.90, 0.0), (-0.88, 0.90, 0.0)],
           'canvas_tan', n=(0.0, 0.447, -0.894))
    for sx in (-1, 1):                                                       # flapping corner + straps
        m.poly([(sx * 0.88, 0.62, -0.90), (sx * 0.94, 0.66, -0.98), (sx * 0.94, 0.70, -0.94),
                (sx * 0.88, 0.72, -0.88)], 'canvas_tan', n=(0.0, 0.6, -0.8))
    m.box(-0.90, 0.62, -0.30, 0.90, 0.70, -0.26, 'soot_black')
    m.box(-0.90, 0.62, 0.30, 0.90, 0.70, 0.34, 'soot_black')
    # sign + straps
    m.box(0.30, 0.05, 0.55, 0.44, 0.42, 0.68, 'leather_brown')
    m.plate('z', +1, 0.37, 0.24, 0.682, 0.10, 0.18, 'signal_yellow')
    m.box(-0.14, 0.30, -0.335, 0.30, 0.34, -0.30, 'soot_black')
    return m


SCAV_ROSTER = {
    'salvager': dict(kind='worker', view_lineup='front', fp='0.6',
                     zones=['hard hat', 'backpack shell'],
                     notes=['hunched profile, oversized right tool arm - asymmetric on purpose']),
    'ratter': dict(kind='rifleman', view_lineup='side', fp='0.6',
                   zones=['helmet band + vest'],
                   notes=['pipe rifle: one long horizontal line held out front']),
    'scrap_hound': dict(kind='raider', view_lineup='side', fp='0.8',
                        zones=['engine cowl'],
                        notes=['long low wedge, wheels outboard and exposed']),
    'ram': dict(kind='guardian', view_lineup='side', fp='1.0',
                zones=['cab roof mantlet', 'cab door panels'],
                notes=['dozer blade = bolted scrap plate on twin hydraulic arms - improvised, not military',
                       'same 3-axle truck, tarp-covered bed in every view']),
    'scrap_yard': dict(kind='command_center', view_lineup='front', fp='4x4',
                       zones=['roof disc', 'door frame'],
                       notes=['container stack + lattice crane mast = the 3.0-t HQ landmark']),
    'garage': dict(kind='barracks', view_lineup='front', fp='3x3',
                   zones=['gable roof panels', 'ridge trim'],
                   notes=['big tarp roll-up door, corrugated walls - thin and temporary']),
    'stash': dict(kind='supply_depot', view_lineup='front', fp='2x2',
                  zones=['drum caps', 'drum band'],
                  notes=['low chunky stack: crates + fuel drums under a tarp canopy']),
}

BUILDERS = {'salvager': salvager, 'ratter': ratter, 'scrap_hound': scrap_hound, 'ram': ram,
            'scrap_yard': scrap_yard, 'garage': garage, 'stash': stash}
