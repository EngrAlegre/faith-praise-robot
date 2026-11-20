// ================================================================
//  FIVE SIDES  ·  desk companion  ·  Faith & Praise build
//  Static desk robot: egg body, floating head, one square eye box for
//  a 2.42" OLED panel, microphone in the top of the head.
//
//  Units mm.  +X right, +Y back, +Z up.  Z=0 = the table.
//  Print: FDM 0.4 nozzle, 0.2 layers, no supports.
//
//  part: body | base | spine | head | head_back
//        (anything else renders the assembly)
// ================================================================

part = "assembly";
$fn = 72;

// ---------------- bought parts ----------------
oled_w = 29.5; oled_h = 29.5; oled_t = 1.6;    // 1.3" I2C OLED module
esp_l  = 63;   esp_w  = 25.5; esp_t = 1.6;     // ESP32-S3-DevKitC-1
spk_d  = 30;                                   // 30 mm driver, face exposed
spk_mount = "grid";   // "grid" = perforated plate (the printed part, keep it)
                      // "open" = one clean 28.6 hole, no plate
spk_hole  = 28.6;     // opening: smaller than the driver, so its rim lands on
                      // the inside of the shell and the cone fires through
with_button = false;  // printed body has no button hole - drill 12 mm
                      // through the belly at z=24, or set true for a future print

// ---------------- body ----------------
body_z0 = 4;            // sits on the base plate
body_h  = 160;
body_ky = 0.867;        // 120 wide -> 104 deep
body_op = 23.4;         // top opening radius
base_d  = 86;

// ---------------- head ----------------
head_w = 118; head_d = 56; head_h = 68;   // tightened: one 0.96" screen is the whole face
head_r = 26;                              // corner radius seen from the front
head_z0 = body_z0 + body_h + 4;                 // 168, floats 4 mm above the rim
// ---- display: change this one word and the window resizes itself ----
//   "0.96"  0.96" 128x64 I2C   board 26.7 x 27.3   active 21.7 x 10.9   ~P150
//   "1.3"   1.3"  128x64 I2C   board 33.5 x 36.0   active 29.4 x 14.7   ~P450
//   "2.42"  2.42" 128x64 I2C   board 61.5 x 39.5   active 55.0 x 27.5   ~P520
panel = "2.42";

_p = panel == "0.96" ? [26.7, 27.3, 21.7, 10.9] :
     panel == "1.3"  ? [33.5, 36.0, 29.42, 14.70] :
                       [61.5, 39.5, 55.01, 27.49];
panel_w = _p[0]; panel_h = _p[1]; panel_aw = _p[2]; panel_ah = _p[3];

eye_win_w    = panel_aw + 1.2;    // window through the front face
eye_win_h    = panel_ah + 1.2;
eye_pocket_w = panel_w + 1.2;     // empty box behind it, module drops in from inside
eye_pocket_h = panel_h + 1.2;
eye_boss_w   = eye_pocket_w + 6;  // wall around that box
eye_boss_h   = eye_pocket_h + 6;
eye_z  = head_z0 + head_h/2;                     // 202, centre of the face
eye_y  = -head_d/2;                             // front face

// ---------------- spine ----------------
spine_r  = 10;
collar_z = head_z0 - 12;
clevis_z = head_z0;

// ---------------- helpers ----------------
module box(w, d, h) { cube([w, d, h], center=true); }
module rrect(w, d, r) { offset(r=r) square([w-2*r, d-2*r], center=true); }
module plate(w, d, h, r=7) { linear_extrude(h) rrect(w, d, r); }

// ================================================================
//  BODY  — egg shell, U-scoop at the front top
// ================================================================
outer_pts = [
  [0,0],[44,0],[47,7],[52,18],[56,30],[59,44],[60,58],[59.4,72],
  [58,86],[55.5,100],[52,112],[47.5,124],[42,134],[36,144],[30,152],[26,160],[0,160]
];
inner_pts = [
  [0,-2],[41.4,-2],[44.4,7],[49.4,18],[53.4,30],[56.4,44],[57.4,58],[56.8,72],
  [55.4,86],[52.9,100],[49.4,112],[44.9,124],[39.4,134],[33.4,144],[27.4,152],[body_op,160],[0,160]
];

module body() {
    translate([0, 0, body_z0]) difference() {
        union() {
            scale([1, body_ky, 1]) rotate_extrude($fn=110) polygon(outer_pts);
            // speaker glue blocks - present on the printed body
            if (spk_mount == "grid")
                for (a = [-1, 0, 1])
                    translate([a*15, -46, 52]) cube([5, 8, 5], center=true);
        }
        scale([1, body_ky, 1]) rotate_extrude($fn=110) polygon(inner_pts);
        // U-scoop across the front top
        translate([0, -58, 208]) sphere(r=82, $fn=90);
        // speaker opening, front wall, centred at z=52
        if (spk_mount == "open") {
            translate([0, -60, 52]) rotate([-90, 0, 0])
                cylinder(d=spk_hole, h=30, center=true);
        } else {
            for (i = [-2:2], j = [-2:2])
                if (abs(i) + abs(j) <= 3)
                    translate([i*6.4 + ((j+4) % 2)*3.2, -60, 52 + j*5.5])
                        rotate([-90, 0, 0]) cylinder(d=3.4, h=30, center=true);
        }
        // push button, belly, below the speaker
        if (with_button) translate([0, -60, 24]) rotate([-90, 0, 0])
            cylinder(d=12.2, h=30, center=true);
        // USB-C slot, back, low
        translate([0, 50, 20]) rotate([90, 0, 0]) box(13, 7, 26);
        // relief so the base plate seats flush
        translate([0, 0, -0.5]) scale([1, body_ky, 1]) cylinder(r=41.2, h=1.0);
    }
}

// ================================================================
//  BASE PLATE — closes the egg, carries the ESP32 and the spine
// ================================================================
module base() {
    difference() {
        union() {
            scale([1, body_ky, 1]) cylinder(d=base_d, h=4);
            translate([0, 0, 3]) scale([1, body_ky, 1]) difference() {
                cylinder(d=81, h=10);                                          // skirt into the body
                translate([0, 0, 2]) cylinder(d=75, h=9);
            }
        }
        // spine screws, from underneath
        for (a = [90, 210, 330]) rotate([0, 0, a]) {
            translate([15, 0, -0.1]) cylinder(d=3.4, h=8);
            translate([15, 0, -0.1]) cylinder(d1=7, d2=3.4, h=1.8);
        }
        translate([0, 0, -0.1]) cylinder(d=14, h=8);                             // wire pass-through
        // ESP32 standoff holes
        for (x = [-24, 24]) for (y = [-26, 26]) translate([x, y, 2]) cylinder(d=2.7, h=8);
        // speaker cable slot
        translate([0, -30, 3]) box(10, 30, 12);
        // rubber feet recesses
        for (a = [45, 135, 225, 315]) rotate([0, 0, a]) translate([30, 0, -0.1]) cylinder(d=9, h=1.4);
    }
}

// ================================================================
//  SPINE — bolts to the base, carries the head, hollow for wires
// ================================================================
module spine() {
    difference() {
        union() {
            translate([0, 0, 4]) cylinder(d=40, h=6);                        // flange z 4..10
            translate([0, 0, 10]) cylinder(d=spine_r*2, h=clevis_z - 10);    // tube
            translate([0, 0, collar_z]) cylinder(d=26, h=7);                 // collar
            translate([0, 0, clevis_z]) cylinder(d=32, h=4);                 // clevis plate
        }
        translate([0, 0, 3]) cylinder(d=13, h=clevis_z + 6);                 // wire bore
        for (a = [45, 135, 225, 315]) rotate([0, 0, a]) translate([13, 0, clevis_z - 1]) cylinder(d=2.6, h=6);
        for (a = [90, 210, 330]) rotate([0, 0, a]) translate([15, 0, 3]) cylinder(d=3.4, h=8);
    }
}

// ================================================================
//  HEAD — rounded slab, the eye box, microphone in the roof
// ================================================================
module head() {
    difference() {
        union() {
            difference() {
                // shell: a rounded rectangle seen from the FRONT, extruded through the depth
                translate([0, -head_d/2, head_z0 + head_h/2]) rotate([-90, 0, 0])
                    linear_extrude(head_d) rrect(head_w, head_h, head_r);
                // cavity: 4 mm front and back walls
                translate([0, -head_d/2 + 4, head_z0 + head_h/2]) rotate([-90, 0, 0])
                    linear_extrude(head_d - 8) rrect(head_w - 6, head_h - 8, head_r - 4);
                // open back
                translate([0, head_d/2 - 1, head_z0 + head_h/2]) box(head_w - 44, 14, head_h - 34);
                // clevis recess and wire hole underneath
                translate([0, 0, head_z0 - 0.1]) cylinder(d=32.6, h=4.2);
                translate([0, 0, head_z0 - 0.1]) cylinder(d=11, h=6);
                // head screws through the floor, countersunk from inside
                for (a = [45, 135, 225, 315]) {
                    rotate([0, 0, a]) translate([13, 0, head_z0]) cylinder(d=3.4, h=5);
                    rotate([0, 0, a]) translate([13, 0, head_z0 + 3]) cylinder(d1=3.4, d2=6.4, h=1.6);
                }
            }
            // the eye box: this tube behind the window is the module pocket
            translate([0, eye_y + 3.6, eye_z]) rotate([-90, 0, 0])
                linear_extrude(11.9) rrect(eye_boss_w, eye_boss_h, 7);   // bites into the front wall
        }
        // one window through the front wall
        translate([0, eye_y - 1, eye_z]) rotate([-90, 0, 0])
            linear_extrude(5.8) rrect(eye_win_w, eye_win_h, 4);
        // the empty box behind it — nothing in it until the screen goes in
        translate([0, eye_y + 3.2, eye_z]) rotate([-90, 0, 0])
            linear_extrude(12.4) rrect(eye_pocket_w, eye_pocket_h, 5);
        // microphone: three holes in the top of the head ...
        for (h = [[-4.5, 4], [4.5, 4], [0, 9.5]])
            translate([h[0], h[1], head_z0 + head_h - 3]) cylinder(d=2.0, h=6);
        // ... and a shallow pocket underneath so the mic board sits in the same
        // spot every time, port up against those holes
        translate([0, 5.5, head_z0 + head_h - 6]) cube([17.6, 17.6, 4.2], center=true);
    }
}

// ================================================================
//  HEAD BACK PANEL — press fit, glued
// ================================================================
module head_back() {
    translate([0, head_d/2 - 1.4, head_z0 + head_h/2]) union() {
        cube([head_w - 36, 3, head_h - 26], center=true);                  // face
        translate([0, -2.6, 0]) cube([head_w - 46, 3.2, head_h - 36], center=true); // locating lip
    }
}

// ================================================================
//  ELECTRONICS — proxy solids, used only to check fit
// ================================================================
module electronics() {
    // ============== ESP32-S3-DevKitC-1 : 63 x 25.4 ==============
    color([0.09,0.30,0.26]) translate([0, 0, 7.4]) box(63, 25.4, 1.6);        // PCB
    color([0.04,0.04,0.05])
        for (yy = [-11.3, 11.3]) translate([0, yy, 5.3]) box(60, 2.5, 2.6);   // pin headers
    color([0.66,0.68,0.70]) translate([20, 0, 9.9]) box(13, 13, 3.2);         // RF shield
    color([0.86,0.86,0.88]) translate([-33.0, 0, 8.4]) box(10, 7.8, 3.4);     // USB-C
    color([0.04,0.04,0.05]) translate([-8, 0, 8.6]) box(7, 7, 1.2);           // module

    // ============== MAX98357A I2S amp : 24 x 16 ==============
    color([0.09,0.30,0.26]) translate([0, 24, 4.8]) box(24, 16, 1.6);         // PCB
    color([0.05,0.05,0.06]) translate([-4, 24, 6.4]) box(7, 7, 1.6);          // chip
    color([0.16,0.35,0.55]) translate([6, 30, 7.6]) box(9, 7, 5.6);           // speaker terminal
    color([0.85,0.86,0.88])
        for (x = [-9:6:9]) translate([x, 18, 6.4]) cylinder(d=2.5, h=2.4);    // header pins

    // ============== 30 mm speaker, face in the opening ==============
    translate([0, -46.2, 52]) rotate([-90, 0, 0]) {   // flat disc vs curved wall: 3 mm gap, filled with glue
        color([0.14,0.14,0.16]) cylinder(d=30, h=2.0);                        // frame
        color([0.20,0.20,0.22]) translate([0,0,2.0]) cylinder(d=26, h=2.2);   // cone
        color([0.10,0.10,0.12]) translate([0,0,4.2]) cylinder(d=12, h=1.3);   // magnet
        color([0.75,0.72,0.66])
            for (a=[0:120:359]) rotate([0,0,a])
                translate([12.6,0,0]) cylinder(d=1.6, h=0.7);                 // frame holes
    }

    // ============== 2.42" OLED in the head pocket ==============
    translate([0, eye_y + 3.2, eye_z]) rotate([-90, 0, 0]) {
        color([0.06,0.06,0.07]) linear_extrude(1.2) rrect(panel_aw + 1.0, panel_ah + 1.0, 2);
        color([0.09,0.30,0.26]) translate([0,0,1.2]) linear_extrude(1.6)
            rrect(panel_w, panel_h, 2);
        color([0.04,0.04,0.05]) translate([0,0,2.8]) linear_extrude(2.4)
            rrect(30, 12, 2);                                                 // header
    }

    // ============== INMP441 microphone, head roof ==============
    color([0.28,0.18,0.45]) translate([0, 5.5, 229.4]) box(14, 14, 3);
    color([0.72,0.74,0.76]) translate([0, 5.5, 231.0]) cylinder(d=3.2, h=1.4);

    // ============== 12 mm tactile button, belly ==============
    color([0.10,0.10,0.12]) translate([0, -38, 24]) box(12, 12, 7.5);
    color([0.62,0.16,0.16]) translate([0, -44.2, 24]) rotate([90,0,0])
        cylinder(d=6, h=2.4);
}

// ================================================================
//  ASSEMBLY
// ================================================================
if (part == "assembly") {
    color([0.94,0.94,0.93]) body();
    color([0.90,0.90,0.89]) base();
    color([0.74,0.74,0.77]) spine();
    color([0.97,0.97,0.96]) head();
    color([0.92,0.92,0.91]) head_back();
    // the OLED, sitting inside the empty box
    color([0.06,0.06,0.07]) translate([0, eye_y + 3.3, eye_z]) rotate([-90, 0, 0])
        linear_extrude(1.6) rrect(panel_w, panel_h, 2);
    color([0.85,0.90,1.0]) translate([0, eye_y + 3.2, eye_z]) rotate([-90, 0, 0])
        linear_extrude(0.5) rrect(panel_aw, panel_ah, 1);
} else if (part == "cut") {
    // assembly with the front half sliced away, for fit checks
    difference() {
        union() { body(); base(); spine(); head(); head_back(); }
        translate([0, -260, -20]) cube([260, 520, 420]);   // slice away x > 0
    }
} else if (part == "electronics") {
    electronics();
} else if (part == "electronics_cut") {
    difference() {
        electronics();
        translate([0, -260, -20]) cube([260, 520, 420]);   // slice away x > 0
    }
} else if (part == "shell") {
    union() { body(); base(); spine(); head(); head_back(); }
} else if (part == "body") {
    translate([0, 0, -body_z0]) body();
} else if (part == "base") {
    base();
} else if (part == "spine") {
    spine();
} else if (part == "head") {
    translate([0, 0, head_d/2]) rotate([90, 0, 0]) translate([0, 0, -(head_z0 + head_h/2)]) head();
} else if (part == "head_back") {
    translate([0, -head_d/2 + 1.4, -(head_z0 + head_h/2)]) head_back();
}

// ---- parts already in robot position, for renders ----
if (part == "body_pos") body();
if (part == "base_pos") base();
if (part == "spine_pos") spine();
if (part == "head_pos") head();
if (part == "head_back_pos") head_back();
