"""Build the kids' build deck (pptx) and a matching PIL preview of every slide."""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image, ImageDraw, ImageFont

OUT_PPTX = '../Five_Sides_Build_Club_v2.pptx'
PREVIEW = '../renders_deck/preview'
ASSETS = '../renders_deck'
RENDERS = '../renders'

INK = RGBColor(0x2B, 0x2B, 0x33)
GREY = RGBColor(0x77, 0x77, 0x84)
CORAL = RGBColor(0xE8, 0x55, 0x3D)
TEAL = RGBColor(0x1F, 0x9E, 0x8F)
YELLOW = RGBColor(0xF2, 0xC1, 0x4E)
NAVY = RGBColor(0x1F, 0x3F, 0x63)
PAPER = RGBColor(0xFF, 0xF9, 0xF2)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CREAM = RGBColor(0xFC, 0xEE, 0xE0)

PF = 'C:/Windows/Fonts/segoeui.ttf'
PFB = 'C:/Windows/Fonts/segoeuib.ttf'
CF = 'C:/Windows/Fonts/consola.ttf'
SCALE = 120  # preview px per inch

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

_cmd = []          # preview draw commands for the current slide
_pv = None


def _font(px, bold=False, mono=False):
    path = CF if mono else (PFB if bold else PF)
    return ImageFont.truetype(path, px)


def wrap(text, fnt, maxw):
    lines = []
    for raw in text.split('\n'):
        words, cur = raw.split(' '), ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if fnt.getlength(t) <= maxw or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def rect(x, y, w, h, fill=None, outline=None, radius=0.0):
    _cmd.append(('rect', x, y, w, h, fill, outline, radius))


def txt(x, y, w, h, s, size=24, bold=False, color=INK, align='l',
        anchor='t', spacing=1.18, mono=False):
    _cmd.append(('text', x, y, w, h, s, size, bold, color, align, anchor, spacing, mono))


def pic(path, x, y, w, h):
    _cmd.append(('pic', path, x, y, w, h))


def badge(x, y, d, s, fill=CORAL, color=WHITE, size=30):
    _cmd.append(('badge', x, y, d, s, fill, color, size))


def slide(bg=PAPER):
    global _cmd
    s = prs.slides.add_slide(BLANK)
    bgr = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bgr.fill.solid(); bgr.fill.fore_color.rgb = bg
    bgr.line.fill.background()
    bgr.shadow.inherit = False
    _cmd = [('rect', 0, 0, 13.333, 7.5, bg, None, 0)]
    return s


def flush_preview(idx):
    W, H = int(13.333 * SCALE), int(7.5 * SCALE)
    im = Image.new('RGB', (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for c in _cmd:
        if c[0] == 'rect':
            _, x, y, w, h, fill, outline, radius = c
            box = [x * SCALE, y * SCALE, (x + w) * SCALE, (y + h) * SCALE]
            if radius:
                d.rounded_rectangle(box, radius=radius * SCALE, fill=fill,
                                    outline=outline, width=2 if outline else 0)
            else:
                d.rectangle(box, fill=fill, outline=outline, width=2 if outline else 0)
        elif c[0] == 'badge':
            _, x, y, dd, s, fill, color, size = c
            d.ellipse([x * SCALE, y * SCALE, (x + dd) * SCALE, (y + dd) * SCALE], fill=fill)
            f = _font(int(size * SCALE / 72 * 1.0), True)
            d.text(((x + dd / 2) * SCALE, (y + dd / 2) * SCALE), str(s), font=f,
                   fill=color, anchor='mm')
        elif c[0] == 'text':
            _, x, y, w, h, s, size, bold, color, align, anchor, spacing, mono = c
            px = int(size * SCALE / 72)
            f = _font(px, bold, mono)
            lines = wrap(s, f, w * SCALE - 8)
            lh = px * spacing
            total = lh * len(lines)
            if anchor == 'm':
                ty = y * SCALE + (h * SCALE - total) / 2
            elif anchor == 'b':
                ty = y * SCALE + h * SCALE - total
            else:
                ty = y * SCALE
            for ln in lines:
                if align == 'c':
                    d.text(((x + w / 2) * SCALE, ty), ln, font=f, fill=color, anchor='ma')
                elif align == 'r':
                    d.text(((x + w) * SCALE, ty), ln, font=f, fill=color, anchor='ra')
                else:
                    d.text((x * SCALE, ty), ln, font=f, fill=color, anchor='la')
                ty += lh
        elif c[0] == 'pic':
            _, path, x, y, w, h = c
            sub = Image.open(path).convert('RGB').resize(
                (max(1, int(w * SCALE)), max(1, int(h * SCALE))), Image.LANCZOS)
            im.paste(sub, (int(x * SCALE), int(y * SCALE)))
    im.save(f'{PREVIEW}/s{idx:02d}.png')


# ------------------------------------------------------------------ primitives
def h1(s, y=0.75, size=42, color=INK, w=11.8, x=0.78):
    txt(x, y, w, 1.0, s, size=size, bold=True, color=color)


def kicker(s, y=0.42, color=CORAL, x=0.78):
    txt(x, y, 10.0, 0.34, s.upper(), size=15, bold=True, color=color)


def body(s, y=1.85, size=23, color=INK, w=11.4, x=0.78, h=3.6):
    txt(x, y, w, h, s, size=size, color=color)


def add_picture_fit(path, x, y, maxw, maxh):
    im = Image.open(path)
    ar = im.width / im.height
    w, h = maxw, maxw / ar
    if h > maxh:
        h, w = maxh, maxh * ar
    px, py = x + (maxw - w) / 2, y + (maxh - h) / 2
    pic(path, px, py, w, h)


def add_image_shape(s, path, x, y, w, h):
    s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))


def flush_pictures(s):
    """Add every pic command to the pptx slide (preview already drew it)."""
    for c in _cmd:
        if c[0] == 'pic':
            _, path, x, y, w, h = c
            s.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))


def emit_text(s):
    for c in _cmd:
        if c[0] != 'text':
            continue
        _, x, y, w, h, text, size, bold, color, align, anchor, spacing, mono = c
        tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE,
                              'b': MSO_ANCHOR.BOTTOM}[anchor]
        for i, line in enumerate(text.split('\n')):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER,
                           'r': PP_ALIGN.RIGHT}[align]
            p.line_spacing = spacing
            r = p.add_run()
            r.text = line
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.name = 'Consolas' if mono else 'Segoe UI'
            r.font.color.rgb = color


def emit_rects(s):
    for c in _cmd:
        if c[0] != 'rect':
            continue
        _, x, y, w, h, fill, outline, radius = c
        if fill is None and outline is None:
            continue
        shp = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
            Inches(x), Inches(y), Inches(w), Inches(h))
        if radius:
            try:
                shp.adjustments[0] = min(0.5, (radius / min(w, h)) if min(w, h) else 0.2)
            except Exception:
                pass
        if fill is None:
            shp.fill.background()
        else:
            shp.fill.solid(); shp.fill.fore_color.rgb = fill
        if outline:
            shp.line.color.rgb = outline; shp.line.width = Pt(2)
        else:
            shp.line.fill.background()
        shp.shadow.inherit = False
        shp.text_frame.text = ''


def finish(s, idx, bg_note=True):
    emit_rects(s)
    flush_pictures(s)
    emit_text(s)
    flush_preview(idx)


def section(title, sub, color, idx, num=None):
    s = slide(color)
    txt(0.9, 2.35, 11.5, 1.4, title, size=64, bold=True, color=WHITE)
    txt(0.95, 3.75, 10.8, 1.2, sub, size=26, color=RGBColor(0xF2, 0xEE, 0xE8))
    finish(s, idx)


def step_cards(items, y=2.05, idx=0, s=None, colors=(CORAL, TEAL, RGBColor(0x6C, 0x56, 0xBE))):
    n = len(items)
    w, gap = (11.8 - 0.35 * (n - 1)) / n, 0.35
    for i, (head, text) in enumerate(items):
        x = 0.78 + i * (w + gap)
        rect(x, y, w, 3.95, WHITE, RGBColor(0xEC, 0xE2, 0xD6), 0.18)
        rect(x, y, w, 0.12, colors[i % len(colors)], None, 0.0)
        badge(x + 0.3, y + 0.38, 0.58, i + 1, colors[i % len(colors)], WHITE, 24)
        txt(x + 0.3, y + 1.12, w - 0.55, 0.6, head, size=23, bold=True)
        txt(x + 0.3, y + 1.78, w - 0.55, 2.0, text, size=18, color=GREY)


def build():
    os.makedirs(PREVIEW, exist_ok=True)
    idx = 0
    HERO = f'{RENDERS}/hero.png'
    FRONT = f'{RENDERS}/front.png'
    HEADPR = f'{RENDERS}/head_printed.png'
    PARTS = f'{ASSETS}/parts.png'
    FLOW = f'{ASSETS}/flow.png'
    WSCREEN = f'{ASSETS}/wiring_screen.png'
    WSOUND = f'{ASSETS}/wiring_sound.png'
    EXPLODED = f'{ASSETS}/exploded.png'

    # ---------------------------------------------------------------- 1 cover
    idx += 1
    s = slide(NAVY)
    txt(0.9, 1.5, 7.2, 0.4, 'THE BUILD CLUB', size=17, bold=True, color=YELLOW)
    txt(0.85, 2.0, 7.4, 2.2, 'Five Sides', size=86, bold=True, color=WHITE)
    txt(0.95, 3.55, 6.5, 1.8, 'A robot that listens,\nthinks, and talks back.', size=30,
        color=RGBColor(0xD8, 0xE2, 0xEE))
    txt(0.95, 6.5, 6.0, 0.5, 'Faith & Praise  ·  step-by-step build book', size=17,
        color=RGBColor(0x8F, 0xA8, 0xC4))
    add_picture_fit(HERO, 7.4, 0.8, 5.4, 5.9)
    finish(s, idx)

    # ---------------------------------------------------------------- 2 what
    idx += 1
    s = slide()
    kicker('first, look at it')
    h1('This is what you\nare going to build')
    txt(0.78, 3.05, 6.0, 2.6,
        'It sits on your desk.\nIt is 24 cm tall.\nIt hears you, it thinks, and it answers out loud.',
        size=24)
    add_picture_fit(FRONT, 7.0, 1.0, 5.7, 5.6)
    finish(s, idx)

    # ---------------------------------------------------------------- 3 can do
    idx += 1
    s = slide()
    kicker('four superpowers')
    h1('What it can do')
    step_cards([('It hears you', 'A tiny microphone\nlistens.\nPress the button,\nthen talk.'),
                ('It thinks', 'The robot sends\nwhat you said\nto a laptop.\nThe laptop thinks.'),
                ('It talks', 'A small speaker\nanswers you in\nrobot chirps.'),
                ('It has a face', 'A glowing screen\nshows eyes and\na mouth.')],
               y=2.1)
    finish(s, idx)

    # ---------------------------------------------------------------- 4 flow
    idx += 1
    s = slide()
    kicker('the big secret')
    h1('How it works', y=0.7)
    txt(0.78, 1.55, 11.6, 0.5, 'Nothing magical. Five steps, then you hear it.', size=22, color=GREY)
    add_picture_fit(FLOW, 0.5, 2.25, 12.3, 4.3)
    finish(s, idx)

    # ---------------------------------------------------------------- 5 plan
    idx += 1
    s = slide()
    kicker('the plan')
    h1('Five build days')
    days = [('DAY 1', 'Print the parts', CORAL), ('DAY 2', 'Build the head', TEAL),
            ('DAY 3', 'Build the body', RGBColor(0x6C, 0x56, 0xBE)),
            ('DAY 4', 'Add the wires', RGBColor(0xC9, 0x7A, 0x0E)),
            ('DAY 5', 'Make it talk', NAVY)]
    for i, (d, t, c) in enumerate(days):
        x = 0.78 + i * 2.42
        rect(x, 2.2, 2.2, 3.1, WHITE, RGBColor(0xEC, 0xE2, 0xD6), 0.2)
        rect(x, 2.2, 2.2, 0.5, c, None, 0.0)
        txt(x, 2.32, 2.2, 0.35, d, size=18, bold=True, color=WHITE, align='c')
        txt(x + 0.2, 3.05, 1.8, 1.6, t, size=24, bold=True, align='c')
    finish(s, idx)

    # ---------------------------------------------------------------- 6 section day1
    idx += 1
    section('DAY 1', 'Print the five parts. This is the slow part, so start it first.', CORAL, idx)

    # ---------------------------------------------------------------- 7 parts
    idx += 1
    s = slide()
    kicker('day 1 · the parts')
    h1('Five pieces, all plastic')
    add_picture_fit(PARTS, 0.4, 1.75, 12.5, 3.1)
    txt(0.78, 5.0, 11.8, 0.5, 'base  ·  spine  ·  body  ·  head  ·  head back',
        size=22, bold=True, align='c')
    txt(0.78, 5.95, 11.6, 0.5, 'Each piece has a job. Do not lose the small ones.', size=20, color=GREY)
    finish(s, idx)

    # ---------------------------------------------------------------- 8 print rules
    idx += 1
    s = slide()
    kicker('day 1 · printing')
    h1('Three settings only')
    step_cards([('0.2 mm layers', 'Not 0.1, not 0.3.\n0.2 mm is the\nright thickness.'),
                ('No supports', 'Every part is\nmade to print\nwithout help.'),
                ('3 walls, 15%', 'A little hollow\nin the middle,\nstrong outside.')],
               y=2.1)
    finish(s, idx)

    # ---------------------------------------------------------------- 9 orientation
    idx += 1
    s = slide()
    kicker('day 1 · which way up')
    h1('How each part sits', y=0.7)
    rows = [('body', 'stands up, round bottom on the bed'),
            ('head', 'lies on its FACE, screen hole down'),
            ('base', 'flat, like a plate'),
            ('spine', 'stands up, wide foot on the bed'),
            ('head back', 'lies flat')]
    y = 1.95
    for a, b in rows:
        rect(0.78, y, 4.1, 0.72, WHITE, RGBColor(0xEC, 0xE2, 0xD6), 0.12)
        txt(0.95, y + 0.14, 3.9, 0.5, a, size=22, bold=True)
        txt(5.1, y + 0.16, 6.2, 0.5, b, size=21, color=GREY)
        y += 0.86
    add_picture_fit(HEADPR, 10.4, 1.8, 2.6, 4.4)
    finish(s, idx)

    # ---------------------------------------------------------------- 9b plates
    idx += 1
    s = slide()
    kicker('day 1 · fitting the printer')
    h1('Three plates, that is all', y=0.7)
    add_picture_fit(f'{ASSETS}/plates.png', 0.55, 1.5, 12.2, 4.5)
    txt(0.78, 6.2, 11.8, 0.9,
        'Every piece already fits a 180 x 180 mm printer. Nothing gets cut in half.\nThe spine is 168 mm tall - that is the only piece that must fit your printer height.',
        size=19, color=GREY)
    finish(s, idx)

    # ---------------------------------------------------------------- 10 check print
    idx += 1
    s = slide()
    kicker('day 1 · check')
    h1('When it comes off the printer')
    step_cards([('Look inside', 'The screen hole must\ngo all the way\nthrough. Shine a\nlight through it.'),
                ('Wiggle it', 'Nothing should\nrattle or fall off.'),
                ('Clean it', 'Pick off the little\nstrings with your\nfingers, gently.')],
               y=2.1)
    finish(s, idx)

    # ---------------------------------------------------------------- 11 section day2
    idx += 1
    section('DAY 2', 'Build the head. The screen goes in from the inside.', TEAL, idx)

    # ---------------------------------------------------------------- 12 need
    idx += 1
    s = slide()
    kicker('day 2 · you need')
    h1('On the table')
    items = [('head', 'printed'), ('2.42" screen', 'the big one'), ('microphone', 'tiny board'),
             ('glue gun', 'ask a grown-up')]
    for i, (a, b) in enumerate(items):
        x = 0.78 + i * 2.9
        rect(x, 2.2, 2.6, 2.4, WHITE, RGBColor(0xEC, 0xE2, 0xD6), 0.18)
        txt(x + 0.2, 2.55, 2.2, 0.9, a, size=24, bold=True, align='c')
        txt(x + 0.2, 3.5, 2.2, 0.6, b, size=18, color=GREY, align='c')
    txt(0.78, 5.15, 11.6, 0.6, 'Wash your hands first. Glue does not stick to oily plastic.', size=21, color=GREY)
    finish(s, idx)

    # ---------------------------------------------------------------- 13 find box
    idx += 1
    s = slide()
    kicker('day 2 · step 1')
    h1('Find the box')
    txt(0.78, 1.9, 5.6, 2.4, 'Turn the head around.\nOn the front there is one\nsquare hole with a box\nbehind it.', size=24)
    txt(0.78, 4.5, 5.6, 1.6, 'That box is empty.\nWe will put the screen in it.', size=21, color=GREY)
    add_picture_fit(HEADPR, 6.9, 1.2, 5.8, 5.4)
    finish(s, idx)

    # ---------------------------------------------------------------- 14 screen in
    idx += 1
    s = slide()
    kicker('day 2 · step 2')
    h1('Put the screen in')
    step_cards([('From the back', 'Push the screen in\nfrom INSIDE the\nhead, not from\nthe front.'),
                ('Glass forward', 'The shiny side\nfaces the hole\nyou want to see.'),
                ('It stops', 'The screen rests\non the little ledge.\nDo not push hard.')],
               y=2.05)
    finish(s, idx)

    # ---------------------------------------------------------------- 15 glue
    idx += 1
    s = slide()
    kicker('day 2 · step 3')
    h1('Two dots of glue')
    txt(0.78, 1.9, 6.0, 2.6, 'Not a lake. Two small dots\non the edges of the screen.\n\nWait 1 minute. Then wiggle it.', size=24)
    rect(0.78, 4.55, 5.4, 1.5, CREAM, RGBColor(0xE2, 0xCE, 0xB8), 0.15)
    txt(1.0, 4.75, 5.0, 1.2, 'Careful: glue on the glass\ncannot be cleaned off.', size=20, color=CORAL, bold=True)
    txt(7.0, 2.6, 5.4, 2.4, 'Hold the screen with two\nfingers while the glue\nsets. That is the whole step.',
        size=22, color=GREY)
    finish(s, idx)

    # ---------------------------------------------------------------- 16 microphone
    idx += 1
    s = slide()
    kicker('day 2 · step 4')
    h1('The microphone goes ON TOP')
    step_cards([('Find 3 holes', 'On the top of the\nhead there are\nthree little\nholes.'),
                ('Look inside', 'Under them is a\nshallow square\nbox. That is the\nmic\'s seat.'),
                ('Glue it in', 'Port facing UP,\nagainst the holes.\nTwo dots of glue.')],
               y=2.05)
    finish(s, idx)

    # ---------------------------------------------------------------- 17 check head
    idx += 1
    s = slide()
    kicker('day 2 · check')
    h1('Test the head')
    step_cards([('Shake it', 'Gently. The screen\nmust not rattle.'),
                ('Look in', 'No glue on the\nshiny glass.'),
                ('Press', 'The mic sits flat\nunder the holes.\nIt must not move.')],
               y=2.1)
    finish(s, idx)

    # ---------------------------------------------------------------- 18 section day3
    idx += 1
    section('DAY 3', 'Build the body. Speaker, microphone, spine.', RGBColor(0x6C, 0x56, 0xBE), idx)

    # ---------------------------------------------------------------- 19 need
    idx += 1
    s = slide()
    kicker('day 3 · you need')
    h1('On the table')
    items = [('body', 'the big egg'), ('base plate', 'the foot'),
             ('spine', 'the neck post'), ('speaker', '40 mm round')]
    for i, (a, b) in enumerate(items):
        x = 0.78 + i * 2.9
        rect(x, 2.2, 2.6, 2.5, WHITE, RGBColor(0xEC, 0xE2, 0xD6), 0.18)
        txt(x + 0.2, 2.55, 2.2, 0.9, a, size=22, bold=True, align='c')
        txt(x + 0.2, 3.6, 2.2, 0.6, b, size=17, color=GREY, align='c')
    finish(s, idx)

    # ---------------------------------------------------------------- 20 speaker
    idx += 1
    s = slide()
    kicker('day 3 · step 5')
    h1('The speaker goes here')
    txt(0.78, 1.9, 5.8, 2.8,
        'Inside the body, where the\nlittle holes are.\n\nGlue it flat against the wall,\nround side facing the holes.', size=24)
    txt(0.78, 4.9, 5.8, 1.2, 'The 3 printed blocks are\nyour glue spots.', size=20, color=GREY)
    add_picture_fit(PARTS, 6.6, 1.4, 6.2, 2.6)
    txt(6.6, 4.3, 6.2, 1.4, 'Body, seen from the front: those dots are the speaker holes.',
        size=19, color=GREY)
    finish(s, idx)

    # ---------------------------------------------------------------- 22 spine
    idx += 1
    s = slide()
    kicker('day 3 · step 6')
    h1('Spine onto the base')
    txt(0.78, 1.9, 6.2, 2.8, 'Turn the base plate upside down.\n\nThree screws go UP through\nthe plate into the spine.', size=24)
    txt(0.78, 4.9, 6.2, 1.2, 'Screwdriver, not your fingers.', size=20, color=GREY)
    add_picture_fit(EXPLODED, 7.3, 1.0, 5.0, 5.6)
    finish(s, idx)

    # ---------------------------------------------------------------- 23 body on
    idx += 1
    s = slide()
    kicker('day 3 · step 7')
    h1('Slide the body over it')
    txt(0.78, 1.9, 6.0, 2.6, 'The spine goes up through\nthe hole in the bottom.\n\nThe body sits on the plate.', size=24)
    rect(0.78, 4.3, 6.2, 1.6, RGBColor(0xE9, 0xF4, 0xF2), TEAL, 0.15)
    txt(1.0, 4.55, 5.8, 1.3, 'DO NOT GLUE IT.\nThe body lifts off like a hat.', size=21, color=TEAL, bold=True)
    finish(s, idx)

    # ---------------------------------------------------------------- 24 head on
    idx += 1
    s = slide()
    kicker('day 3 · step 8')
    h1('Head onto the spine')
    txt(0.78, 1.9, 6.0, 2.8, 'Four screws from inside\nthe head go DOWN into\nthe top of the spine.\n\nFeed the screen wires\ndown the spine first.', size=23)
    txt(0.78, 5.15, 6.2, 0.8, 'Tight, but do not crush the plastic.', size=20, color=GREY)
    finish(s, idx)

    # ---------------------------------------------------------------- 25 check body
    idx += 1
    s = slide()
    kicker('day 3 · check')
    h1('Test the body')
    step_cards([('Wobble', 'Push the head.\nIt must not lean.'),
                ('Lift', 'The shell comes\noff in one piece.'),
                ('Inside', 'Nothing loose\nrattling around.')],
               y=2.1)
    finish(s, idx)

    # ---------------------------------------------------------------- 26 section day4
    idx += 1
    section('DAY 4', 'Add the wires. Four for the screen, six for the sound.', RGBColor(0xC9, 0x7A, 0x0E), idx)

    # ---------------------------------------------------------------- 27 wiring screen
    idx += 1
    s = slide()
    kicker('day 4 · wire 1')
    h1('The screen: 4 wires', y=0.65)
    add_picture_fit(WSCREEN, 0.5, 1.55, 12.3, 5.3)
    finish(s, idx)

    # ---------------------------------------------------------------- 28 colours
    idx += 1
    s = slide()
    kicker('day 4 · say it out loud')
    h1('Say the colours')
    pairs = [('GND', 'GND', 'black'), ('VCC', '3V3', 'red'),
             ('SCL', 'GPIO9', 'yellow'), ('SDA', 'GPIO8', 'blue')]
    y = 2.0
    for a, b, c in pairs:
        rect(0.78, y, 5.2, 0.8, WHITE, RGBColor(0xEC, 0xE2, 0xD6), 0.12)
        txt(1.0, y + 0.16, 2.0, 0.5, a, size=22, bold=True)
        txt(3.1, y + 0.16, 2.6, 0.5, 'goes to  ' + b, size=21, color=GREY)
        y += 0.95
    rect(6.5, 2.0, 5.9, 3.5, WHITE, RGBColor(0xEC, 0xE2, 0xD6), 0.15)
    txt(6.8, 2.25, 5.3, 3.0, 'Two wires are power.\nTwo wires are talking.\n\nIf the screen stays black,\nswap SDA and SCL.',
        size=21)
    finish(s, idx)

    # ---------------------------------------------------------------- 29 wiring sound
    idx += 1
    s = slide()
    kicker('day 4 · wire 2')
    h1('The sound: 6 wires', y=0.65)
    add_picture_fit(WSOUND, 0.5, 1.55, 12.3, 5.4)
    finish(s, idx)

    # ---------------------------------------------------------------- 30 button
    idx += 1
    s = slide()
    kicker('day 4 · the button')
    h1('One button, two wires')
    step_cards([('Wire 1', 'From the button\nto GPIO18.'),
                ('Wire 2', 'From the button\nto GND.'),
                ('Press it', 'That is how you\ntell the robot:\n“now listen”.')],
               y=2.1)
    finish(s, idx)

    # ---------------------------------------------------------------- 31 check wires
    idx += 1
    s = slide()
    kicker('day 4 · check')
    h1('Before you power it up')
    step_cards([('Tug gently', 'Each wire.\nNone should\nslide out.'),
                ('Nothing touching', 'No bare metal\ntouching other\nmetal.'),
                ('Grounds', 'All black wires\nend up together.')],
               y=2.1)
    finish(s, idx)

    # ---------------------------------------------------------------- 32 section day5
    idx += 1
    section('DAY 5', 'Give it a brain. Code, upload, talk.', NAVY, idx)

    # ---------------------------------------------------------------- 33 install
    idx += 1
    s = slide()
    kicker('day 5 · step 10')
    h1('Install three things')
    step_cards([('Arduino IDE', 'Download it.\nIt is free.\nIt is where we\nwrite the code.'),
                ('ESP32 boards', 'In the IDE:\nBoards Manager,\ntype ESP32,\nclick install.'),
                ('U8g2 library', 'Library Manager,\ntype U8g2,\nclick install.')],
               y=2.1)
    finish(s, idx)

    # ---------------------------------------------------------------- 34 change 3 lines
    idx += 1
    s = slide(NAVY)
    txt(0.78, 0.7, 11.8, 0.4, 'DAY 5 · STEP 11', size=15, bold=True, color=YELLOW)
    txt(0.78, 1.1, 11.8, 0.8, 'Change three lines', size=40, bold=True, color=WHITE)
    rect(0.78, 2.05, 11.8, 2.85, RGBColor(0x14, 0x2B, 0x45), None, 0.12)
    code = [
        'const char* WIFI_SSID = "YOUR_WIFI";     // your wifi name',
        'const char* WIFI_PASS = "YOUR_PASSWORD"; // your wifi password',
        'const char* AI_HOST   = "http://192.168.1.50:8080";  // laptop address',
    ]
    y = 2.3
    for line in code:
        txt(1.05, y, 11.2, 0.4, line, size=15, color=RGBColor(0xC9, 0xE4, 0xFF), mono=True)
        y += 0.72
    txt(0.78, 5.2, 11.8, 0.8, 'Ask a grown-up for the wifi name and password.\nThe laptop address comes later, in step 15.',
        size=19, color=RGBColor(0xA9, 0xC0, 0xD8))
    finish(s, idx)

    # ---------------------------------------------------------------- 35 panel define
    idx += 1
    s = slide(NAVY)
    txt(0.78, 0.7, 11.8, 0.4, 'DAY 5 · STEP 12', size=15, bold=True, color=YELLOW)
    txt(0.78, 1.1, 11.8, 0.8, 'Tell it which screen you have', size=38, bold=True, color=WHITE)
    rect(0.78, 2.15, 11.8, 2.2, RGBColor(0x14, 0x2B, 0x45), None, 0.12)
    txt(1.05, 2.4, 11.2, 1.8,
        '#define PANEL_242    // 2.42 inch  <-- ours\n// #define PANEL_13     // 1.3 inch\n// #define PANEL_096    // 0.96 inch',
        size=17, color=RGBColor(0xC9, 0xE4, 0xFF), mono=True, spacing=1.5)
    txt(0.78, 4.75, 11.8, 1.4, 'One of these is on. The other two have // in front, which means “ignore me”.\nOurs is the 2.42 inch one.',
        size=21, color=RGBColor(0xA9, 0xC0, 0xD8))
    finish(s, idx)

    # ---------------------------------------------------------------- 36 upload
    idx += 1
    s = slide()
    kicker('day 5 · step 13')
    h1('Press the arrow')
    txt(0.78, 1.9, 6.1, 2.4, 'Plug the robot into the laptop\nwith the USB cable.\n\nPick the board:\nESP32S3 Dev Module.', size=23)
    txt(0.78, 4.6, 6.1, 1.4, 'Then press Upload.\nIt takes about a minute.', size=21, color=GREY)
    rect(7.1, 2.0, 5.3, 3.4, WHITE, RGBColor(0xEC, 0xE2, 0xD6), 0.15)
    txt(7.4, 2.25, 4.8, 3.0, 'When it is done:\nthe screen lights up\nand two eyes look\nat you.', size=22, bold=True)
    finish(s, idx)

    # ---------------------------------------------------------------- 37 black screen
    idx += 1
    s = slide()
    kicker('day 5 · if it does not work')
    h1('Screen is black?')
    step_cards([('Check power', 'Two wires for\npower: GND and\n3V3. Not 5V.'),
                ('Swap two', 'SDA and SCL\nare easy to\nmix up.'),
                ('Wrong define', 'Is PANEL_242\nthe one without\n// in front?')],
               y=2.1)
    finish(s, idx)

    # ---------------------------------------------------------------- 38 server
    idx += 1
    s = slide(NAVY)
    txt(0.78, 0.7, 11.8, 0.4, 'DAY 5 · STEP 14', size=15, bold=True, color=YELLOW)
    txt(0.78, 1.1, 11.8, 0.9, 'Wake up the brain', size=40, bold=True, color=WHITE)
    txt(0.8, 2.1, 11.6, 0.6, 'On the laptop, in the robot folder:', size=21, color=RGBColor(0xA9, 0xC0, 0xD8))
    rect(0.78, 2.75, 8.2, 0.9, RGBColor(0x14, 0x2B, 0x45), None, 0.1)
    txt(1.05, 3.0, 7.8, 0.5, 'python ai_server.py', size=22, color=RGBColor(0xC9, 0xE4, 0xFF), mono=True)
    txt(0.8, 3.95, 11.6, 2.2,
        'It prints a number like  http://192.168.1.50:8080\n\nPut that number in the code, in AI_HOST, and upload again.\nThat is the address the robot calls when you talk to it.',
        size=21, color=RGBColor(0xD8, 0xE2, 0xEE))
    finish(s, idx)

    # ---------------------------------------------------------------- 39 talk
    idx += 1
    s = slide()
    kicker('day 5 · step 15')
    h1('Press the button and talk')
    step_cards([('Press', 'The face says\nit is listening.'),
                ('Talk', 'Say “hello”\nclearly.'),
                ('Wait', '3 seconds.\nThen it thinks.'),
                ('It answers', 'Chirps + a face\nthat matches.')],
               y=2.1, colors=(CORAL, TEAL, RGBColor(0x6C, 0x56, 0xBE), YELLOW))
    finish(s, idx)

    # ---------------------------------------------------------------- 40 trouble
    idx += 1
    s = slide()
    kicker('when something is wrong')
    h1('Ask these four questions')
    rows = [('Nothing lights up', 'Is the USB cable in?  Is it a data cable?'),
            ('It never answers', 'Is the laptop server running?  Same wifi?'),
            ('It answers itself', 'Is the mic too close to the speaker?'),
            ('The face is upside down', 'Change U8G2_R0 to U8G2_R2 at the top of the sketch.')]
    y = 1.95
    for a, b in rows:
        rect(0.78, y, 5.4, 0.95, WHITE, RGBColor(0xEC, 0xE2, 0xD6), 0.12)
        txt(1.0, y + 0.22, 4.9, 0.5, a, size=21, bold=True)
        txt(6.5, y + 0.22, 6.0, 0.6, b, size=20, color=GREY)
        y += 1.1
    finish(s, idx)

    # ---------------------------------------------------------------- 41 next
    idx += 1
    s = slide()
    kicker('what comes next')
    h1('Three more ideas')
    step_cards([('Eyes that blink', 'Change one number\nin the code.\nWatch it blink\nfaster.'),
                ('A wake word', 'No button.\nJust say\n“hey robot”.'),
                ('It sees you', 'Add a distance\nsensor. It stops\nbefore the wall.')],
               y=2.1)
    finish(s, idx)

    # ---------------------------------------------------------------- 42 end
    idx += 1
    s = slide(CORAL)
    txt(0.9, 2.35, 7.0, 0.45, 'AND THAT IS IT', size=17, bold=True,
        color=RGBColor(0xFF, 0xE0, 0xD6))
    txt(0.85, 2.85, 7.4, 2.1, 'You built\na robot.', size=62, bold=True, color=WHITE)
    txt(0.9, 5.5, 6.6, 1.4,
        'You printed it, you wired it,\n\nand you taught it to talk.\n\nFaith and Praise - Five Sides',
        size=21, color=RGBColor(0xFF, 0xE8, 0xE2))
    add_picture_fit(FRONT, 8.0, 1.3, 5.0, 5.2)
    finish(s, idx)

    prs.save(OUT_PPTX)
    print(f'{idx} slides -> {OUT_PPTX}')


if __name__ == '__main__':
    build()
