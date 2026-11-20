"""Docs follow the model: no antennas, mic in the head."""
import re

# ---------------- README ----------------
r = open('README.md', encoding='utf-8').read()
r = r.replace("| Size | 126 mm wide × 232 mm tall (318 mm with antennas) |",
              "| Size | 118 mm wide × 236 mm tall |")
r = r.replace("**one wide eye box for a 2.42\"\nOLED face**", "**one wide eye box for a 2.42\"\nOLED face**")
r = r.replace("It sits on a desk, hears you, answers out loud, and\nlooks at you.",
              "It sits on a desk, hears you, answers out loud, and\nlooks at you. No antennas, no wheels — the microphone lives in the top of the head.")
r = r.replace("## The face", "## The face")
# add a mic note after the face section
r = r.replace("The firmware draws **two eyes and a mouth on that single panel**: blinking,\nlooking around, six moods.",
              "The firmware draws **two eyes and a mouth on that single panel**: blinking,\nlooking around, six moods.\n\n"
              "## Where the microphone is\n\nThree 2 mm holes in the **top of the head**, with a 17.6 mm square pocket under\nthem. The mic board drops into that pocket, port facing up against the holes, and\ntwo dots of glue hold it. It is as far from the speaker as the robot allows, which\nis the whole point — a mic next to a speaker hears the robot talking to itself.\n\n"
              "There are no antennas. An earlier version had two wire antennas on the head;\nthey are gone, and the head is now one clean shell.")
open('README.md', 'w', encoding='utf-8').write(r)

# ---------------- MATERIALS ----------------
m = open('MATERIALS.md', encoding='utf-8').read()
m = m.replace("| 1 | **INMP441** I2S mic | 24-bit, 3.3 V | 180 |",
              "| 1 | **INMP441** I2S mic | 24-bit, 3.3 V. Sits inside the **top of the head** | 180 |")
m = m.replace("| 2 | Antenna wire | 2 mm piano wire / stiff coat-hanger, 65 mm each | 20 |\n", "")
m = m.replace("| 2 | Springs, optional | 5 mm OD × 15 mm (from a ballpen) for the coil at the antenna base | 20 |\n", "")
m = m.replace("| | **Total** | | **≈ ₱1 900** |", "| | **Total** | | **≈ ₱1 860** |")
m = m.replace("| `head.stl` | 1 | 118 × 68 × 56 | 60 g | **face down** |",
              "| `head.stl` | 1 | 118 × 68 × 56 | 60 g | **face down** |")
m = m.replace("Nothing else goes in the box. No bezel, no ring, no glass.",
              "Nothing else goes in the box. No bezel, no ring, no glass.\n\n"
              "## Where the microphone goes\n\nThree holes in the **top of the head**, with a 17.6 × 17.6 mm pocket underneath.\nThe mic board drops into the pocket with its little port facing up at the holes.\nNo antennas anywhere — that idea is retired.")
open('MATERIALS.md', 'w', encoding='utf-8').write(m)

# ---------------- BUILD ----------------
b = open('BUILD.md', encoding='utf-8').read()
b = b.replace("Five printed parts, one OLED panel, one spine.",
              "Five printed parts, one OLED panel, one microphone, one spine.")
b = b.replace("""2. **Antennas.** A drop of glue in each Ø2.3 socket on top, push the 2 mm wire in
   12 mm deep, splay them out 10°. Slide the pen spring over the base for the coil.""",
              """2. **Microphone.** The three holes on top of the head are the mic. Drop the
   INMP441 into the square pocket under them, port facing **up** at the holes, and
   glue the board's edges. It must sit flat, or the port misses the holes.""")
b = b.replace("""5. **Microphone.** Glue the INMP441 high up near the scoop, as far from the
   speaker as the wires allow. Next to the speaker it will hear itself.""",
              """5. *(Microphone is already in the head — nothing to do here.)*""")
b = b.replace("| It answers itself | mic too close to the speaker, or the mic's `L/R` pad not tied to GND |",
              "| It answers itself | the mic is not sealed against the head holes, so it hears the speaker through the shell |")
open('BUILD.md', 'w', encoding='utf-8').write(b)
print("docs updated")
