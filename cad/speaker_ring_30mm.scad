// ---------------------------------------------------------------------------
// speaker_ring_30mm.scad
// Seals a 30 mm driver onto the 40 mm speaker grille in the body.
// Glue the flat back face onto the three existing glue blocks (inside the
// front wall, x = -15 / 0 / +15, z = 52), then glue the driver into the bore.
// Without this ring a 30 mm speaker leaks sound sideways into the hollow body
// and loses roughly half its volume.
// ---------------------------------------------------------------------------

$fn = 96;

ring_od = 40.0;   // matches the grille + glue-block spread
ring_id = 30.4;   // 30 mm driver, slip fit + glue
ring_h  = 3.0;

module ring() {
    difference() {
        cylinder(d = ring_od, h = ring_h);
        translate([0, 0, -0.1])
            cylinder(d = ring_id, h = ring_h + 0.2);
    }
}

ring();
