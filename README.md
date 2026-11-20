# Five Sides — desk companion

Static desk robot. Egg body, floating head, **one wide eye box for a 2.42"
OLED face**, microphone in the roof. It sits on a desk, hears you, answers out
loud, and looks at you. No antennas, no wheels.

This is the only design in this folder. The earlier rolling-chassis version and
the round-goggle version have been removed.

| | |
|---|---|
| Size | 118 mm wide × 236 mm tall |
| Body | printed egg shell, 120 × 104 × 160, U-scoop cut at the front top |
| Head | rounded slab 118 × 68 × 56, floats 4 mm above the rim |
| Face | **one empty box**, 56.2 × 28.7 window, 62.7 × 40.7 pocket — 2.42" OLED |
| Neck | printed spine, Ø20, hollow for the wires |
| Brain | ESP32-S3-DevKitC-1 (N16R8) |
| Voice | INMP441 mic → laptop AI → MAX98357A amp → 40 mm speaker |
| Printing | 5 parts, 293 cm³ of model, ~200 g of PLA, no supports |

## Files

```
cad/five_sides_robot.scad    parametric model — assembly + every part
stl/                         slice-ready: body, head, head_back, spine, base
stl/pos/                     same parts already in robot position (for renders)
renders/                     hero / front / side / back / three-quarter
firmware/five_sides_desk/    Arduino sketch — compiles, 31 % of a 16 MB board
firmware/ai_server.py        the brain on your laptop (stdlib only)
BUILD.md                     print settings, assembly order, wiring, troubleshooting
MATERIALS.md                 what to buy, with specs and prices
```

Every STL is a **single closed solid** (0 open or non-manifold edges), verified
after export.

## The face

One box cut into the head's front face — no round pod, no bezel ring, no bridge:

- **56.2 × 28.7 mm window** through the 4 mm front wall
- **62.7 × 40.7 × 12 mm empty box** behind it, open to the cavity
- **3.3 mm lip** the board rests against
- nothing printed inside it

Sized for the **2.42" 128×64 SSD1309 OLED** (board 61.5 × 39.5 mm, active area
**55.0 × 27.5 mm**). That is 6.4× the lit area of the 0.96" module, so the screen
is the face rather than a badge on it.

| Panel | Active area | Lit area | Price | Notes |
|---|---|---:|---:|---|
| 0.96" 128×64 SSD1306 | 21.7 × 10.9 | 237 mm² | ₱149 | too small for this head |
| 1.3" 128×64 SH1106 | 29.4 × 14.7 | 433 mm² | ₱450 | still small |
| **2.42" 128×64 SSD1309** | **55.0 × 27.5** | **1512 mm²** | **₱520** | this is the one |

Changing panel is one word in the CAD (`panel = "2.42"` → `"1.3"` / `"0.96"`) —
the window, the box and the wall resize to fit — and one `#define` in the sketch
for the driver.

The firmware draws **two eyes and a mouth on that single panel**: blinking,
looking around, six moods.

## Where the microphone is

Three 2 mm holes in the **top of the head**, with a 17.6 mm square pocket under
them. The mic board drops into that pocket, port facing up against the holes, and
two dots of glue hold it. It is as far from the speaker as the robot allows, which
is the whole point — a mic next to a speaker hears the robot talking to itself.

There are no antennas. An earlier version had two wire antennas on the head;
they are gone, and the head is now one clean shell.

## Print

| Part | Qty | Colour | Orientation |
|---|---:|---|---|
| `body.stl` | 1 | white | upright, bottom rim on the bed |
| `head.stl` | 1 | white | **face down** |
| `head_back.stl` | 1 | white | flat |
| `spine.stl` | 1 | any | upright, flange on the bed |
| `base.stl` | 1 | white | flat |

0.2 mm layers, 3 walls, 15 % infill, no supports. The body also prints in vase
mode (1 wall) if you want it several times faster.

## Assembly in one paragraph

Screw the spine to the base from underneath, drop the body shell over it, screw
the head onto the spine's clevis with four M3 from inside, glue the OLED
into the eye box from behind, glue the speaker behind the grille, and feed the
screen wires down the spine's bore. Full steps in `BUILD.md`.

## What it does

Press the button, talk, and it answers with robot chirps while the eyes react.
The laptop server (`ai_server.py`) does the listening and thinking.
