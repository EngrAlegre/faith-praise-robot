"""Add the 180 mm plate-plan slide to the deck, and document the plates."""
NL = chr(92) + 'n'

# ---------------- deck: one new slide after "which way up" ----------------
p = 'build_deck.py'
s = open(p, encoding='utf-8').read()
marker = "    # ---------------------------------------------------------------- 10 check print"
assert marker in s
new_slide = '''    # ---------------------------------------------------------------- 9b plates
    idx += 1
    s = slide()
    kicker('day 1 · fitting the printer')
    h1('Three plates, that is all', y=0.7)
    add_picture_fit(f'{ASSETS}/plates.png', 0.55, 1.5, 12.2, 4.5)
    txt(0.78, 6.2, 11.8, 0.9,
        'Every piece already fits a 180 x 180 mm printer. Nothing gets cut in half.' + NL +
        'The spine is 168 mm tall - that is the only piece that must fit your printer height.',
        size=19, color=GREY)
    finish(s, idx)

'''
s = s.replace(marker, new_slide + marker)
open(p, 'w', encoding='utf-8').write(s)

# ---------------- BUILD.md: plate plan ----------------
b = open('BUILD.md', encoding='utf-8').read()
old_start = b.index("## 1. Print")
old_end = b.index("## 2. Head")
new = """## 1. Print

**Nothing needs splitting for a 180 × 180 × 180 printer.** Every part fits as it
is; the tallest is the spine at 168 mm. Three plates and you are done:

| Plate file | On it | Footprint | Height | ~time |
|---|---|---|---:|---:|
| `plates/plate1_body.stl` | body | 120 × 104 mm | 160 mm | 6 h |
| `plates/plate2_head.stl` | head | 118 × 68 mm | 56 mm | 3 h |
| `plates/plate3_small.stl` | base + spine + head back | 86 × 140 mm | 168 mm | 3 h |

Prefer single parts? `stl/body.stl`, `stl/head.stl` etc. are the same geometry,
one file each. The plate files are just those parts already arranged with a 10 mm
gap, so you can drop one file into the slicer and press go.

Orientation matters:

| Part | Sits |
|---|---|
| body | upright, bottom rim on the bed |
| head | **face down** (the screen window on the bed) |
| head back | flat |
| spine | upright, its wide foot on the bed |
| base | flat |

0.2 mm layers, 3 walls, 15 % infill, **no supports**. Add a 5 mm brim to the
spine — it is tall and thin, and a brim keeps it from wobbling.

If your printer's maximum height is under 168 mm, lay the spine on its side
instead: 168 × 40 × 40 mm footprint, supports under the flanges.

Optional: the body prints in vase mode (1 wall, 0.8 mm) several times faster.

"""
b = b[:old_start] + new + b[old_end:]
open('BUILD.md', 'w', encoding='utf-8').write(b)
print("deck slide + build doc updated")
