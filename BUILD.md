# Build order

Five printed parts, one OLED panel, one microphone, one spine. Nothing moves.

---

## 1. Print

**Nothing needs splitting for a 180 x 180 x 180 printer.** Every part fits as it
is; the tallest is the spine at 168 mm. Three plates and you are done:

| Plate file | On it | Footprint | Height | ~time |
|---|---|---|---:|---:|
| `plates/plate1_body.stl` | body | 120 x 104 mm | 160 mm | 6 h |
| `plates/plate2_head.stl` | head | 118 x 68 mm | 56 mm | 3 h |
| `plates/plate3_small.stl` | base + spine + head back | 86 x 140 mm | 168 mm | 3 h |

Prefer single parts? `stl/body.stl`, `stl/head.stl` etc. are the same geometry,
one file each. The plate files are just those parts already arranged with a
10 mm gap, so you can drop one file into the slicer and press go.

Orientation matters:

| Part | Sits |
|---|---|
| body | upright, bottom rim on the bed |
| head | **face down** (the screen window on the bed) |
| head back | flat |
| spine | upright, its wide foot on the bed |
| base | flat |

0.2 mm layers, 3 walls, 15 % infill, **no supports**. Add a 5 mm brim to the
spine - it is tall and thin, and a brim stops it wobbling.

If your printer's maximum height is under 168 mm, lay the spine on its side
instead: 168 x 40 x 40 mm footprint, supports under the flanges.

Optional: the body prints in vase mode (1 wall, 0.8 mm) several times faster.

## 2. Head

1. **Screen.** Drop the 2.42" OLED into the box from *inside* the head — glass
   against the 3.3 mm lip, glowing side facing the window. Two dabs of hot glue on
   the board's edges. The connector points down into the cavity.
2. **Microphone.** The three holes on top of the head are the mic. Drop the
   INMP441 into the square pocket under them, port facing **up** at the holes, and
   glue the board's edges. It must sit flat, or the port misses the holes.
3. **Wiring.** Feed the four wires out through the back opening. **Leave the back
   panel off until the robot works.**

## 3. Body

4. **Speaker.** Glue the 40 mm speaker inside the front wall, centred on the
   perforated grille, cone facing out. The three printed blocks are the glue
   points — get it flat against the wall, it is the robot's voice.
5. *(Microphone is already in the head — nothing to do here.)*

## 4. Base

6. **ESP32.** Foam tape or four M3 × 6 into the pilot holes, USB-C end toward the
   back slot — that is where the cable leaves the robot.
7. **Amp.** MAX98357A beside it, foam tape.

## 5. Assemble

8. **Spine to base.** Three M3 × 12 from *underneath* the base plate, up into the
   spine's flange.
9. **Body on.** Slide the shell down over the spine — it passes through the Ø83
   bottom opening and the rim lands on the base plate. **Do not glue it.** The
   shell lifts off for servicing.
10. **Head on.** Feed the screen wires down through the spine's Ø13 bore, then four
    M3 × 8 up through the head's floor into the clevis. Countersunk heads sit
    inside the head.
11. **Connect.** Four wires to the I2C pins, audio to the I2S pins, close the back
    panel, upload, press the button.

---

## Wiring

| Signal | ESP32-S3 pin |
|---|---|
| OLED SDA | GPIO8 |
| OLED SCL | GPIO9 |
| OLED VCC / GND | 3V3 / GND |
| MAX98357A BCLK / LRC / DIN | GPIO4 / GPIO5 / GPIO6 |
| INMP441 SCK / WS / SD | GPIO15 / GPIO16 / GPIO17 |
| Talk button → GND | GPIO18 |
| Mood LED (on board) | GPIO38 |

The OLED is a plain I2C device at address 0x3C. Only four wires leave the head.

## Flash

Arduino IDE → board **ESP32S3 Dev Module**, `PSRAM: OPI`, `Flash: 16MB`,
`Partition: Huge APP`, `USB CDC On Boot: Enabled`. Library: **U8g2** (Library
Manager), and pick the panel with the `#define PANEL_...` at the top of the sketch. Set WiFi and the laptop IP at the top of the sketch, upload.

Then the brain on the laptop:

```bash
python ai_server.py                    # offline demo mode, no key needed
set AI_KEY=sk-...   (Windows)          # real speech + real answers
```

---

## When it does not work

| Symptom | Cause |
|---|---|
| Screen stays black | wrong `#define` for the panel (SSD1309 vs SSD1306/SH1106), or SDA/SCL swapped |
| Screen flickers | long wires, or the 4.7 kΩ pull-ups missing on some modules |
| Eyes flicker while it talks | 5 V supply sagging — the amp pulls ~1 A on peaks |
| It answers itself | the mic is not sealed against the head holes, so it hears the speaker through the shell |
| Nothing on the serial monitor | `USB CDC On Boot` is off |
| Head wobbles | the four clevis screws are loose, or the spine's flange screws |
| Image shifted or wrapped | wrong panel model line in the sketch — 2.42" is `PANEL_242` |
