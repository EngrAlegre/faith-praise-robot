"""Numeric fit check: does every bought part fit inside the printed shell?"""
import math

BODY_Z0, KY = 4.0, 0.867          # body sits at z=4, y scaled 0.867
# inner profile (z from body bottom, radius) straight out of the SCAD
INNER = [(0, 41.4), (7, 44.4), (18, 49.4), (30, 53.4), (44, 56.4), (58, 57.4),
         (72, 56.8), (86, 55.4), (100, 52.9), (112, 49.4), (124, 44.9),
         (134, 39.4), (144, 33.4), (152, 27.4), (160, 23.4)]

def inner_r(z_world):
    z = z_world - BODY_Z0
    if z <= INNER[0][0]:
        return INNER[0][1]
    for (z0, r0), (z1, r1) in zip(INNER, INNER[1:]):
        if z <= z1:
            t = (z - z0) / (z1 - z0)
            return r0 + (r1 - r0) * t
    return INNER[-1][1]

def utilisation(x, y, z):
    r = inner_r(z)
    return math.hypot(x / r, y / (r * KY))

def check(name, x0, x1, y0, y1, z0, z1):
    worst, at = 0.0, None
    for x in (x0, x1):
        for y in (y0, y1):
            for z in (z0, z1):
                u = utilisation(x, y, z)
                if u > worst:
                    worst, at = u, (x, y, z)
    marg = (1 - worst) * inner_r(at[2])
    ok = "OK" if worst < 1 else "COLLIDES"
    print(f"  {name:20} needs {worst*100:5.1f}% of the space   clearance {marg:+6.1f} mm   {ok}")
    return worst < 1

print("BODY CAVITY (world z, radius)")
for z in (6, 20, 52, 90, 140):
    print(f"   z={z:3}  r={inner_r(z):5.1f}")

print("\nFIT CHECK")
ok = True
ok &= check("ESP32 board",      -31.5, 31.5, -12.7, 12.7,  4, 13)
ok &= check("MAX98357A amp",    -12,   12,   16,    32,    4, 8)
ok &= check("30mm speaker",     -15,   15,  -42,   -36.5,  37, 67)

print("\nHEAD (fixed pockets, from the model)")
print("  OLED module 61.5x39.5x6   pocket 62.7 x 40.7 x 12.4   -> 0.6 / 1.2 / 6.4 mm spare")
print("  INMP441 mic 14x14x3       pocket 17.6 x 17.6 x 4.2     -> 3.6 / 3.6 / 1.2 mm spare")

print("\nSPEAKER GLUE BLOCKS  (5 x 8 x 5 at x=-15/0/+15, y -50..-42, z 49.5..54.5)")
blocks = [("left", -17.5, -12.5), ("centre", -2.5, 2.5), ("right", 12.5, 17.5)]
for nm, bx0, bx1 in blocks:
    ox = min(15, bx1) - max(-15, bx0)
    oy = min(-36.5, -42) - max(-42, -50)      # driver sits y -42..-36.5
    # compare against the driver at the wall position instead
    oy2 = min(-40.9, -42) - max(-46.4, -50)
    print(f"  {nm:7} vs driver at wall  : y-overlap {max(0,oy2):.1f} mm"
          f"   x-overlap {max(0,ox):.1f} mm")

print("\nVERDICT:", "all electronics fit" if ok else "something does not fit")
