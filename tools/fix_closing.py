"""One-off: rewrite the closing slide block with safe newline handling."""
NL = chr(92) + 'n'   # write the two characters backslash-n
p = 'build_deck.py'
s = open(p, encoding='utf-8').read()

start = s.index("    # ---------------------------------------------------------------- 42 end")
end = s.index("    prs.save(OUT_PPTX)")

new = '''    # ---------------------------------------------------------------- 42 end
    idx += 1
    s = slide(CORAL)
    txt(0.9, 2.35, 7.0, 0.45, 'AND THAT IS IT', size=17, bold=True,
        color=RGBColor(0xFF, 0xE0, 0xD6))
    txt(0.85, 2.85, 7.4, 2.1, 'You built@NLa robot.', size=62, bold=True, color=WHITE)
    txt(0.9, 5.5, 6.6, 1.4,
        'You printed it, you wired it,@NL@NLand you taught it to talk.@NL@NLFaith and Praise - Five Sides',
        size=21, color=RGBColor(0xFF, 0xE8, 0xE2))
    add_picture_fit(FRONT, 8.0, 1.3, 5.0, 5.2)
    finish(s, idx)

'''.replace('@NL', NL)

s = s[:start] + new + s[end:]
open(p, 'w', encoding='utf-8').write(s)
print('closing rewritten safely')
