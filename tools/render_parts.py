"""Labeled assembly renders: every bought part, numbered, with a legend."""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import mesh

R = lambda p: os.path.join(os.path.dirname(__file__), '..', p)
OUT = R('renders')

shell = mesh.load_stl(R('stl/asm_shell.stl'))
elec  = mesh.load_stl(R('stl/asm_electronics.stl'))
shell_cut = mesh.load_stl(R('stl/asm_cut.stl'))
elec_cut  = mesh.load_stl(R('stl/asm_elec_cut.stl'))

PLA, BOARD = (0.935, 0.930, 0.915), (0.13, 0.42, 0.52)

W = H = 1700
PAD = 0.06

def basis(az, el):
    a, e = np.radians(az), np.radians(el)
    v = np.array([np.sin(a)*np.cos(e), -np.cos(a)*np.cos(e), np.sin(e)])
    r = np.cross([0.0, 0.0, 1.0], v); r /= np.linalg.norm(r)
    u = np.cross(v, r)
    return v, r, u

def projector(scene, az, el, pad=PAD):
    """Same maths as mesh.Scene.render, so labels land on the parts."""
    v, Rm, U = basis(az, el)
    pts = []
    for tris, _, T, _ in scene.parts:
        p = tris.reshape(-1, 3)
        pts.append(p @ T[:3, :3].T + T[:3, 3])
    pts = np.vstack(pts)
    sx, sy = pts @ Rm, pts @ U
    S = (1 - 2*pad) * min(W/(sx.max()-sx.min()), H/(sy.max()-sy.min()))
    cx, cy = (sx.min()+sx.max())/2, (sy.min()+sy.max())/2
    def proj(q):
        q = np.asarray(q, float)
        return ((q @ Rm - cx)*S + W/2, H/2 - (q @ U - cy)*S)
    return proj

LABELS = [
    ("ESP32-S3",    ( 10,   6, 9.5),  "ESP32-S3 DevKitC-1 - the brain"),
    ("AMP",         (  0,  24, 8.0),  "MAX98357A I2S amplifier"),
    ("SPEAKER",     (  0, -44, 52),   "30 mm speaker - face in the opening"),
    ("DISPLAY",     (  0, -20, 202),  "2.42\" OLED - the face"),
    ("MIC",         (  0,  5.5, 232), "INMP441 microphone - head roof"),
    ("BUTTON",      (  0, -44, 24),   "12 mm push button - belly"),
]

def draw_labels(frame, proj, color=(30, 30, 34)):
    img = Image.fromarray(np.clip(frame, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 30)
    except Exception:
        f = ImageFont.load_default()
    for i, (name, pos, _) in enumerate(LABELS, 1):
        x, y = proj(pos)
        r = 21
        d.ellipse([x-r-3, y-r-3, x+r+3, y+r+3], fill=(255, 255, 255))
        d.ellipse([x-r, y-r, x+r, y+r], fill=(214, 72, 60))
        t = str(i)
        tw = d.textlength(t, font=f)
        d.text((x - tw/2, y - 19), t, font=f, fill=(255, 255, 255))
    # legend
    lf = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 26) if os.path.exists(
        "C:/Windows/Fonts/arial.ttf") else ImageFont.load_default()
    y0 = 24
    d.rounded_rectangle([24, y0-10, 690, y0 + 8 + 34*len(LABELS)],
                        radius=14, fill=(255, 255, 255, 235))
    for i, (name, _, desc) in enumerate(LABELS, 1):
        d.text((44, y0 + 34*(i-1)), f"{i}.  {desc}", font=lf, fill=color)
    return img

# ---------- 1. ghost, every part visible through the shell ----------
g = mesh.Scene(w=W, h=H, bg=(248, 247, 244))
g.add(elec, BOARD)
g.add(shell, PLA, alpha=0.30)
frame = g.render(azim=28, elev=12, pad=PAD)[0]
draw_labels(frame, projector(g, 28, 12)).save(os.path.join(OUT, 'parts_ghost.png'))
print('ghost   ->  parts_ghost.png')

# ---------- 2. front, speaker visible in the opening ----------
f2 = mesh.Scene(w=W, h=H, bg=(248, 247, 244))
f2.add(elec, BOARD)
f2.add(shell, PLA, alpha=0.32)
f2.save(os.path.join(OUT, 'parts_front.png'), azim=0, elev=4, pad=PAD)
print('front   ->  parts_front.png')

# ---------- 3. side section, labelled ----------
s3 = mesh.Scene(w=W, h=H, bg=(247, 245, 242))
s3.add(shell_cut, PLA)
s3.add(elec_cut, BOARD)
fr = s3.render(azim=90, elev=3, pad=PAD)[0]
draw_labels(fr, projector(s3, 90, 3)).save(os.path.join(OUT, 'parts_section.png'))
print('section ->  parts_section.png')
