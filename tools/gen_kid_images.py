"""Diagrams for the kids' build deck: wiring (split in two), the signal flow,
a parts line-up and an exploded view."""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import mesh

OUT = '../renders_deck'
F = 'C:/Windows/Fonts/segoeui.ttf'
FB = 'C:/Windows/Fonts/segoeuib.ttf'
INK = (43, 43, 51)
GREY = (130, 130, 142)
CORAL = (232, 85, 61)
TEAL = (31, 158, 143)
YELLOW = (242, 193, 78)
BLUE = (52, 120, 210)
RED = (214, 69, 69)
BLACK = (40, 40, 45)
PAPER = (255, 249, 242)


def font(size, bold=False):
    return ImageFont.truetype(FB if bold else F, size)


def rbox(d, xy, r, fill, outline=None, w=3):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=w)


def label(d, xy, text, size=22, bold=False, fill=INK, anchor='la'):
    d.text(xy, text, font=font(size, bold), fill=fill, anchor=anchor)


def centred(d, cx, cy, text, size=22, bold=False, fill=INK):
    d.text((cx, cy), text, font=font(size, bold), fill=fill, anchor='mm')


# ---------------------------------------------------------------- wiring: OLED
def wiring_screen():
    W, H = 1600, 760
    im = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(im)

    # ESP32 board
    rbox(d, (620, 150, 980, 680), 26, (31, 63, 99), (18, 38, 62), 4)
    centred(d, 800, 210, "ESP32-S3", 34, True, (255, 255, 255))
    centred(d, 800, 252, "the brain", 22, False, (168, 192, 220))

    # OLED
    rbox(d, (90, 220, 520, 620), 22, (28, 28, 32), (10, 10, 12), 4)
    rbox(d, (130, 270, 436, 520), 8, (208, 224, 245), None)
    centred(d, 305, 390, "2.42\" screen", 30, True, (60, 80, 110))
    centred(d, 305, 580, "the face", 24, False, (170, 170, 180))

    order = [("GND", "GND", BLACK), ("VCC", "3V3", RED),
             ("SCL", "GPIO9", YELLOW), ("SDA", "GPIO8", BLUE)]
    for i, (lp, ep, col) in enumerate(order):
        y = 300 + i * 60
        d.line([(520, y), (620, y)], fill=col, width=9)
        d.text((514, y), lp, font=font(19, True), fill=(255, 255, 255), anchor='rm')
        d.text((636, y), ep, font=font(20, True), fill=(205, 224, 244), anchor='lm')

    # note
    rbox(d, (1030, 220, 1520, 610), 22, (255, 255, 255), (225, 225, 232), 3)
    label(d, (1062, 250), "Say it out loud:", 26, True, CORAL)
    for i, t in enumerate(["GND  goes to  GND", "VCC  goes to  3V3",
                           "SCL  goes to  GPIO9", "SDA  goes to  GPIO8"]):
        label(d, (1062, 306 + i * 52), t, 24, False, INK)
    label(d, (1062, 530), "Not 5V! The screen wants 3V3.", 22, True, RED)

    im.save(f'{OUT}/wiring_screen.png')


# ---------------------------------------------------------------- wiring: sound
def wiring_sound():
    W, H = 1600, 900
    im = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(im)

    rbox(d, (600, 130, 980, 760), 26, (31, 63, 99), (18, 38, 62), 4)
    centred(d, 790, 190, "ESP32-S3", 34, True, (255, 255, 255))

    # speaker amp
    rbox(d, (60, 140, 520, 350), 22, (242, 193, 78), (208, 158, 50), 4)
    centred(d, 290, 190, "SPEAKER AMP", 28, True, (90, 62, 10))
    centred(d, 290, 235, "MAX98357A", 22, False, (110, 80, 20))
    centred(d, 290, 300, "makes the voice loud", 20, False, (120, 92, 30))
    for i, (nm, gp) in enumerate([("BCLK", "4"), ("LRC", "5"), ("DIN", "6")]):
        y1 = 340 + i * 26
        d.line([(520, 260 + i * 26), (600, 220 + i * 34)], fill=TEAL, width=7)
        label(d, (470, y1 - 26), nm, 17, True, (110, 80, 20), anchor='ra')

    # mic
    rbox(d, (60, 540, 520, 750), 22, (31, 158, 143), (18, 112, 100), 4)
    centred(d, 290, 590, "MICROPHONE", 28, True, (255, 255, 255))
    centred(d, 290, 632, "INMP441", 22, False, (200, 240, 235))
    centred(d, 290, 695, "lets the robot hear you", 20, False, (205, 240, 235))
    for i, nm in enumerate(["SCK", "WS", "SD"]):
        d.line([(520, 620 + i * 40), (600, 610 + i * 40)], fill=TEAL, width=7)
        label(d, (470, 594 + i * 40), nm, 17, True, (255, 255, 255), anchor='ra')

    # pins on the board
    for i, (nm, gp) in enumerate([("BCLK", "GPIO4"), ("LRC", "GPIO5"), ("DIN", "GPIO6")]):
        label(d, (612, 188 + i * 34), gp, 20, True, (200, 220, 240))
    for i, (nm, gp) in enumerate([("SCK", "GPIO15"), ("WS", "GPIO16"), ("SD", "GPIO17")]):
        label(d, (612, 578 + i * 40), gp, 20, True, (200, 220, 240))

    # button
    rbox(d, (1080, 540, 1500, 750), 22, (255, 255, 255), (225, 225, 232), 3)
    centred(d, 1290, 592, "BUTTON", 28, True, CORAL)
    centred(d, 1290, 636, "one wire to GPIO18", 21, False, INK)
    centred(d, 1290, 680, "one wire to GND", 21, False, INK)
    d.line([(1080, 645), (980, 645)], fill=CORAL, width=8)

    rbox(d, (1080, 170, 1500, 390), 22, (255, 255, 255), (225, 225, 232), 3)
    label(d, (1110, 202), "Remember:", 26, True, TEAL)
    for i, t in enumerate(["All grounds join together.", "AMP wants 5V,", "MIC wants 3V3.",
                           "Keep the mic away", "from the speaker."]):
        label(d, (1110, 242 + i * 30), t, 20, False, INK)

    im.save(f'{OUT}/wiring_sound.png')


# ---------------------------------------------------------------- flow
def flow():
    W, H = 1900, 520
    im = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(im)
    steps = [("YOU", "talk to it", (255, 255, 255)),
             ("MIC", "catches your voice", (31, 158, 143)),
             ("ESP32", "sends it on WiFi", (31, 63, 99)),
             ("LAPTOP", "AI thinks", (108, 86, 190)),
             ("SPEAKER", "answers out loud", (242, 193, 78))]
    bw, bh, gap = 300, 250, 70
    x = 60
    for i, (t1, t2, col) in enumerate(steps):
        dark = col in ((31, 158, 143), (31, 63, 99), (108, 86, 190))
        fg = (255, 255, 255) if dark else INK
        rbox(d, (x, 130, x + bw, 130 + bh), 24, col, (200, 200, 210) if not dark else None, 3)
        centred(d, x + bw // 2, 200, t1, 40, True, fg)
        centred(d, x + bw // 2, 275, t2, 24, False, fg if dark else GREY)
        if i < len(steps) - 1:
            ax = x + bw + 12
            d.line([(ax, 255), (ax + gap - 24, 255)], fill=CORAL, width=9)
            d.polygon([(ax + gap - 24, 242), (ax + gap - 2, 255), (ax + gap - 24, 268)], fill=CORAL)
        x += bw + gap
    label(d, (60, 430), "You hear it. That is the whole trick.", 30, False, GREY)
    im.save(f'{OUT}/flow.png')


# ---------------------------------------------------------------- parts
STL = '../stl/pos'
P = {k: mesh.load_stl(os.path.join(STL, k + '.stl')) for k in
     ['body', 'base', 'spine', 'head', 'head_back']}


def _minz(tris):
    return tris.reshape(-1, 3)[:, 2].min()


def parts_lineup():
    s = mesh.Scene(w=2000, h=760, bg=PAPER)
    white = (0.94, 0.94, 0.93)
    order = [('base', (0.88, 0.88, 0.87), 0),
             ('spine', (0.72, 0.72, 0.75), 95),
             ('body', white, 190),
             ('head', (0.96, 0.96, 0.95), 330),
             ('head_back', (0.90, 0.90, 0.89), 440)]
    for name, col, dx in order:
        s.add(P[name], col, translate=(dx, 0, -_minz(P[name])))
    s.save(f'{OUT}/parts.png', azim=-18, elev=16, pad=0.06)


def exploded():
    s = mesh.Scene(w=1400, h=1600, bg=PAPER)
    white = (0.94, 0.94, 0.93)
    # natural assembly positions, lifted apart
    s.add(P['base'], (0.88, 0.88, 0.87), translate=(0, 0, 0))
    s.add(P['spine'], (0.72, 0.72, 0.75), translate=(0, 0, 20))
    s.add(P['body'], white, translate=(0, 0, 70))
    s.add(P['head'], (0.96, 0.96, 0.95), translate=(0, 0, 175))
    s.add(P['head_back'], (0.90, 0.90, 0.89), translate=(0, 0, 240))
    s.save(f'{OUT}/exploded.png', azim=-22, elev=12, pad=0.07)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    wiring_screen(); wiring_sound(); flow(); parts_lineup(); exploded()
    print('images done:', sorted(os.listdir(OUT)))
