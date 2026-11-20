"""Labeled assembly renders: every bought part, in its own colour, numbered."""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import mesh

R = lambda p: os.path.join(os.path.dirname(__file__), '..', p)
OUT = R('renders')

W = H = 1700
PAD = 0.06

COL = {                      # colour, legend text
    'esp':  ((0.10, 0.36, 0.30), "ESP32-S3 DevKitC-1  -  the brain"),
    'amp':  ((0.17, 0.35, 0.63), "MAX98357A I2S amp  -  makes the sound"),
    'spk':  ((0.13, 0.13, 0.16), "30 mm speaker  -  face in the opening"),
    'oled': ((0.05, 0.05, 0.08), "2.42\" OLED  -  the face"),
    'mic':  ((0.36, 0.20, 0.56), "INMP441 microphone  -  head roof"),
    'btn':  ((0.72, 0.18, 0.16), "12 mm push button  -  belly"),
}
ORDER = ['esp', 'amp', 'spk', 'oled', 'mic', 'btn']

ANCHOR = {
    'esp':  (-20, 0, 10),
    'amp':  (10, 30, 9),
    'spk':  (0, -44, 52),
    'oled': (0, -20, 202),
    'mic':  (0, 6, 232),
    'btn':  (0, -44, 24),
}

def split_by_part(tris):
    """Separate the electronics STL into the six bought parts by position."""
    idx, _p = mesh.components(tris)
    groups = {k: [] for k in ORDER}
    for iarr in idx:
        t = tris[iarr]
        x, y, z = t.reshape(-1, 3).mean(axis=0)
        if   z > 220:                        k = 'mic'
        elif z > 170:                        k = 'oled'
        elif y < -35 and 40 < z < 66:        k = 'spk'
        elif y < -30 and 16 < z < 32:        k = 'btn'
        elif y > 14:                         k = 'amp'
        else:                                k = 'esp'
        groups[k].append(t)
    return {k: (np.concatenate(v) if v else None) for k, v in groups.items()}

def build(elec_tris, shell_tris, shell_alpha):
    s = mesh.Scene(w=W, h=H, bg=(248, 247, 245))
    for k in ORDER:
        t = elec_tris.get(k)
        if t is not None:
            s.add(t, COL[k][0])
    if shell_tris is not None:
        s.add(shell_tris, (0.94, 0.935, 0.92), alpha=shell_alpha)
    return s

def basis(az, el):
    a, e = np.radians(az), np.radians(el)
    v = np.array([np.sin(a)*np.cos(e), -np.cos(a)*np.cos(e), np.sin(e)])
    r = np.cross([0.0, 0.0, 1.0], v); r /= np.linalg.norm(r)
    return v, r, np.cross(v, r)

def projector(scene, az, el):
    """Same maths as mesh.Scene.render, so the dots land on the parts."""
    v, Rm, U = basis(az, el)
    pts = []
    for tris, _, T, _ in scene.parts:
        p = tris.reshape(-1, 3)
        pts.append(p @ T[:3, :3].T + T[:3, 3])
    pts = np.vstack(pts)
    sx, sy = pts @ Rm, pts @ U
    S = (1 - 2*PAD) * min(W/(sx.max()-sx.min()), H/(sy.max()-sy.min()))
    cx, cy = (sx.min()+sx.max())/2, (sy.min()+sy.max())/2
    def proj(q):
        q = np.asarray(q, float)
        return ((q @ Rm - cx)*S + W/2, H/2 - (q @ U - cy)*S)
    return proj

def annotate(frame, proj):
    img = Image.fromarray(np.clip(frame, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    nf = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 30)
    lf = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 27)
    for i, k in enumerate(ORDER, 1):
        x, y = proj(ANCHOR[k])
        r = 22
        d.ellipse([x-r-4, y-r-4, x+r+4, y+r+4], fill=(255, 255, 255))
        d.ellipse([x-r, y-r, x+r, y+r], fill=(214, 72, 60))
        t = str(i); tw = d.textlength(t, font=nf)
        d.text((x-tw/2, y-19), t, font=nf, fill=(255, 255, 255))
    d.rounded_rectangle([24, 18, 665, 50 + 38*len(ORDER)], radius=16,
                        fill=(255, 255, 255), outline=(212, 208, 198), width=2)
    for i, k in enumerate(ORDER, 1):
        y = 42 + 38*(i-1)
        d.rounded_rectangle([44, y-2, 66, y+20], radius=4,
                            fill=tuple(int(255*v) for v in COL[k][0]))
        d.text((80, y-6), f"{i}.  {COL[k][1]}", font=lf, fill=(35, 35, 40))
    return img

if __name__ == '__main__':
    elec   = split_by_part(mesh.load_stl(R('stl/asm_electronics.stl')))
    elec_c = split_by_part(mesh.load_stl(R('stl/asm_elec_cut.stl')))
    shell   = mesh.load_stl(R('stl/asm_shell.stl'))
    shell_c = mesh.load_stl(R('stl/asm_cut.stl'))

    s = build(elec, shell, 0.26)
    f = s.render(azim=32, elev=20, pad=PAD)[0]
    annotate(f, projector(s, 32, 20)).save(os.path.join(OUT, 'parts_ghost.png'))
    print('parts_ghost.png')

    s2 = build(elec_c, shell_c, 1.0)
    f2 = s2.render(azim=90, elev=3, pad=PAD)[0]
    annotate(f2, projector(s2, 90, 3)).save(os.path.join(OUT, 'parts_section.png'))
    print('parts_section.png')

    s3 = build(elec, shell, 0.28)
    s3.save(os.path.join(OUT, 'parts_front.png'), azim=0, elev=6, pad=PAD)
    print('parts_front.png')
