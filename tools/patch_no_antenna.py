"""Remove antennas, move the microphone into the top of the head."""
import re

p = 'cad/five_sides_robot.scad'
s = open(p, encoding='utf-8').read()

# 1. header comment
s = s.replace("one square eye box for\n//  a small OLED panel, twin antennas.  No motors, no wheels.",
              "one square eye box for\n//  a 2.42\" OLED panel, microphone in the top of the head.")

# 2. drop the antenna bosses
old_boss = """            // antenna bosses
            for (s = [-1, 1]) translate([s*24, 6, head_z0 + head_h])
                rotate([0, s*10, 0]) translate([0, 0, -1]) cylinder(d=8, h=11);
"""
assert old_boss in s
s = s.replace(old_boss, "")

# 3. antenna holes -> microphone holes + locating pocket on the roof
old_holes = """        // antenna holes
        for (s = [-1, 1]) translate([s*24, 6, head_z0 + head_h])
            rotate([0, s*10, 0]) translate([0, 0, 1]) cylinder(d=2.3, h=13);
"""
new_holes = """        // microphone: three holes in the top of the head ...
        for (h = [[-4.5, 4], [4.5, 4], [0, 9.5]])
            translate([h[0], h[1], head_z0 + head_h - 3]) cylinder(d=2.0, h=6);
        // ... and a shallow pocket underneath so the mic board sits in the same
        // spot every time, port up against those holes
        translate([0, 5.5, head_z0 + head_h - 6]) cube([17.6, 17.6, 4.2], center=true);
"""
assert old_holes in s
s = s.replace(old_holes, new_holes)

# 4. remove the antenna module and its call
old_mod = """module antennas() {
    for (s = [-1, 1]) translate([s*24, 6, head_z0 + head_h])
        rotate([0, s*10, 0]) union() {
            cylinder(d=2.0, h=62);
            cylinder(d=6.0, h=15);
        }
}

"""
assert old_mod in s
s = s.replace(old_mod, "")
s = s.replace("    color([0.15,0.15,0.17]) antennas();\n", "")

open(p, 'w', encoding='utf-8').write(s)
print("antennas gone, mic moved to the head roof")
