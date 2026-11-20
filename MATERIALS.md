# Materials

Static desk robot. No motors, no wheels, no driver, no servo — it sits on a desk,
hears you, talks, and looks at you with two small square OLED eyes.

---

## Buy

| Qty | Item | Spec that matters | ≈ ₱ |
|---:|---|---|---:|
| 1 | **ESP32-S3-DevKitC-1** | **N16R8** — 16 MB flash, 8 MB PSRAM, USB-C | 650 |
| 1 | **2.42" OLED 128×64, I2C** | **SSD1309**, board 61.5 × 39.5 mm, active 55.0 × 27.5 mm, address 0x3C | 520 |
| 1 | **INMP441** I2S mic | 24-bit, 3.3 V. Sits inside the **top of the head** | 180 |
| 1 | **MAX98357A** I2S amp | 3 W, 5 V | 180 |
| 1 | Speaker | 40 mm, 8 Ω, 3 W | 60 |
| 3 | **M3 × 12 pan head** | spine up into the base, from underneath | 15 |
| 4 | **M3 × 8 countersunk** | head down onto the spine's clevis | 15 |
| 1 | USB-C cable + 5 V 2 A adapter | a desk robot can live on a cable | 150 |
| 1 | Hot glue + 2 sticks | OLEDs, speaker, back panel | 60 |
| | **Total** | | **≈ ₱1 860** |

Plus about **200 g of PLA** (or a print shop, ≈₱800 for the set).

### Why the 2.42"
The 0.96" module lights only 21.7 × 10.9 mm — on a 118 mm head that is a badge,
not a face. Active areas, for scale:

| Panel | Active area | Lit area | vs 0.96" | Price |
|---|---|---:|---:|---:|
| 0.96" SSD1306 (Makerlab) | 21.7 × 10.9 | 237 mm² | 1× | ₱149 |
| 1.3" SH1106 (Makerlab, 33.5 × 36 board) | 29.4 × 14.7 | 433 mm² | 1.8× | ₱450 |
| **2.42" SSD1309 (Shopee PH)** | **55.0 × 27.5** | **1512 mm²** | **6.4×** | **₱520** |

The 2.42" is the only one that fills the head. It is a 20-pin/7-pin board about
61.5 × 39.5 × 10 mm — it fits the printed box with the connector pointing into
the head's cavity.

Buy: search **"2.42 inch 128x64 OLED SSD1309 I2C"** on Shopee PH (about ₱520) —
take the 7-pin SPI/I2C version and wire it as I2C. Local alternative if you want
to order from Makerlab instead: the 1.3" (₱450), which still fits this head, just
with a smaller screen — set `panel = "1.3"` in the CAD and `#define PANEL_13` in
the sketch.

---

## Printed parts — 5 files, 298 cm³ of model

| File | Qty | Size (mm) | ~PLA | Print orientation |
|---|---:|---|---:|---|
| `body.stl` | 1 | 120 × 104 × 160 | 100 g | upright, bottom rim on the bed |
| `head.stl` | 1 | 118 × 68 × 56 | 60 g | **face down** |
| `head_back.stl` | 1 | 90 × 52 × 6 | 8 g | flat |
| `spine.stl` | 1 | Ø20 × 168 | 30 g | upright, flange on the bed |
| `base.stl` | 1 | Ø86 × 13 | 20 g | flat |

0.2 mm layers, 3 walls, 15 % infill, no supports, white PLA. **The body can be
printed in vase mode** (spiralise, 1 wall, 0.8 mm) — about four times faster, at
the cost of a slightly flexible shell.

---

## Fasteners

| Where | Screw | Note |
|---|---|---|
| Base → spine | 3 × M3 × 12 pan | from **under** the base, into the spine flange |
| Head → spine | 4 × M3 × 8 countersunk | from **inside** the head, down into the clevis |
| OLED panels | glue | into the eye boxes, no screws |
| Head back panel | glue | press in, 2 dabs |

No nuts, no heat-set inserts — every screw bites into printed plastic.

---

## The eye box

One **56.2 × 28.7 mm window** through the head's front face, with an **empty
62.7 × 40.7 × 12 mm box** behind it. The panel drops into that box from inside
the head and rests on the 3.3 mm lip at the front.

The 2.42" board is 61.5 × 39.5 mm — about 0.6 mm clearance all round, so it
self-locates. Only its 55.0 × 27.5 mm glowing area shows through the window.

Nothing else goes in the box. No bezel, no ring, no glass.

## Where the microphone goes

Three holes in the **top of the head**, with a 17.6 × 17.6 mm pocket underneath.
The mic board drops into the pocket with its little port facing up at the holes.
No antennas anywhere — that idea is retired.
