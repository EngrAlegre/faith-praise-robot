"""Lay the five printed parts out on 180 x 180 mm plates and write plate STLs."""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import mesh

STL = '../stl'
OUTP = '../plates'
F, FB = 'C:/Windows/Fonts/segoeui.ttf', 'C:/Windows/Fonts/segoeuib.ttf'
INK, GREY, CORAL, TEAL = (43, 43, 51), (130, 130, 142), (232, 85, 61), (31, 158, 143)

P = {k: mesh.load_stl(os.path.join(STL, k + '.stl')) for k in
     ['body', 'head', 'base', 'spine', 'head_back']}


def size(t):
    v = t.reshape(-1, 3)
    return v.max(0) - v.min(0)


def drop(t):
    """sit the part on z=0, centred on x/y about 0."""
    v = t.reshape(-1, 3)
    lo, hi = v.min(0), v.max(0)
    off = np.array([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
    return t + off


# plate 3: base + spine + head_back, laid out with 10 mm gaps
LAYOUT = {
    'plate1_body':   [('body', 0, 0)],
    'plate2_head':   [('head', 0, 0)],
    'plate3_small':  [('base', 0, 0), ('spine', 0, 84), ('head_back', 0, 134)],
}


def build():
    os.makedirs(OUTP, exist_ok=True)
    report = []
    for plate, items in LAYOUT.items():
        tris = []
        for name, dx, dy in items:
            t = drop(P[name])
            sz = size(t)
            v = t.reshape(-1, 3)
            # centre each part on its own slot, then offset by the layout
            t = t + np.array([dx + sz[0] / 2, dy + sz[1] / 2, 0])
            tris.append(t)
        allt = np.vstack(tris)
        mesh.save_stl(f'{OUTP}/{plate}.stl', allt)
        v = allt.reshape(-1, 3)
        w, d = v.max(0)[0] - v.min(0)[0], v.max(0)[1] - v.min(0)[1]
        h = v.max(0)[2]
        report.append((plate, [i[0] for i in items], w, d, h))
    return report


def diagram(report):
    """Three bed outlines drawn to scale next to each other."""
    W, H = 1800, 760
    im = Image.new('RGB', (W, H), (255, 249, 242))
    d = ImageDraw.Draw(im)
    f_t = ImageFont.truetype(FB, 30)
    f_s = ImageFont.truetype(F, 21)
    f_l = ImageFont.truetype(FB, 19)

    bed = 180.0
    scale = 330 / bed          # px per mm
    x0, y0 = 90, 230
    gap = 90
    for i, (plate, parts, w, dpt, h) in enumerate(report):
        bx = x0 + i * (330 + gap)
        d.rectangle([bx, y0, bx + 330, y0 + 330], outline=(210, 200, 190), width=3)
        # grid
        for g in range(1, 4):
            xx = bx + 330 * g / 4
            yy = y0 + 330 * g / 4
            d.line([xx, y0, xx, y0 + 330], fill=(240, 234, 226))
            d.line([bx, yy, bx + 330, yy], fill=(240, 234, 226))
        # parts
        for name, dx, dy_ in LAYOUT[plate]:
            t = P[name]
            v = t.reshape(-1, 3)
            lo, hi = v.min(0), v.max(0)
            pw, pd = hi[0] - lo[0], hi[1] - lo[1]
            px = bx + dx * scale
            py = y0 + (330 - (dy_ + pd) * scale)
            col = CORAL if name == 'body' else (TEAL if name == 'head' else (108, 86, 190))
            d.rounded_rectangle([px, py, px + pw * scale, py + pd * scale],
                                radius=8, fill=col + (255,) if False else col,
                                outline=(255, 255, 255), width=2)
            label = name.replace('_', ' ')
            tw = d.textlength(label, font=f_l)
            if pw * scale > tw + 12:
                d.text((px + pw * scale / 2, py + pd * scale / 2), label,
                       font=f_l, fill=(255, 255, 255), anchor='mm')
        d.text((bx + 165, y0 - 40), plate.replace('_', ' '), font=f_t,
               fill=INK, anchor='mm')
        d.text((bx + 165, y0 + 348), '%.0f x %.0f mm  ·  %.0f mm tall' % (w, dpt, h),
               font=f_s, fill=GREY, anchor='ma')
        d.text((bx + 165, y0 + 378), ', '.join(x.replace('_', ' ') for x in parts),
               font=ImageFont.truetype(FB, 18), fill=(150, 150, 160), anchor='ma')

    d.text((90, 52), 'Every part on a 180 x 180 bed', font=ImageFont.truetype(FB, 46), fill=INK)
    d.text((92, 112), 'No piece needs splitting. Three plates and you are done.',
           font=ImageFont.truetype(F, 26), fill=GREY)
    d.text((90, 690), 'Drawn to scale. Grey square = the 180 x 180 mm bed.',
           font=ImageFont.truetype(F, 21), fill=(160, 160, 170))
    im.save('../renders_deck/plates.png')


if __name__ == '__main__':
    rep = build()
    diagram(rep)
    for plate, parts, w, d, h in rep:
        print('%-14s %-34s %.0f x %.0f mm, %.0f tall' % (plate, ', '.join(parts), w, d, h))
    print('wrote plates/ and renders_deck/plates.png')
