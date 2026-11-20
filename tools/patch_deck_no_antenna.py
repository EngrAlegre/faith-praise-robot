"""Update the deck for: no antennas, microphone in the top of the head."""

p = 'build_deck.py'
s = open(p, encoding='utf-8').read()

# 1. size line on slide 2
s = s.replace("'It sits on your desk.\\nIt is as tall as a school ruler.\\nIt hears you, it thinks, and it answers out loud.'",
              "'It sits on your desk.\\nIt is 24 cm tall.\\nIt hears you, it thinks, and it answers out loud.'")

# 2. Day 2 "you need": antennas -> microphone
s = s.replace("""    items = [('head', 'printed'), ('2.42" screen', 'the big one'), ('2 antennas', 'thin wire'),
             ('glue gun', 'ask a grown-up')]""",
              """    items = [('head', 'printed'), ('2.42" screen', 'the big one'), ('microphone', 'tiny board'),
             ('glue gun', 'ask a grown-up')]""")

# 3. Day 2 step 4: antennas -> microphone
old16 = s[s.index("    # ---------------------------------------------------------------- 16 antennas"):
          s.index("    # ---------------------------------------------------------------- 17 check head")]
new16 = '''    # ---------------------------------------------------------------- 16 microphone
    idx += 1
    s = slide()
    kicker('day 2 · step 4')
    h1('The microphone goes ON TOP')
    step_cards([('Find 3 holes', 'On the top of the\\nhead there are\\nthree little\\nholes.'),
                ('Look inside', 'Under them is a\\nshallow square\\nbox. That is the\\nmic\\'s seat.'),
                ('Glue it in', 'Port facing UP,\\nagainst the holes.\\nTwo dots of glue.')],
               y=2.05)
    finish(s, idx)

'''
s = s.replace(old16, new16)

# 4. Day 2 check: antenna pull -> mic
s = s.replace("""                ('Pull', 'One finger on an\\nantenna. It holds.')],""",
              """                ('Press', 'The mic sits flat\\nunder the holes.\\nIt must not move.')],""")

# 5. Day 3 "you need": drop the microphone
s = s.replace("""    items = [('body', 'the big egg'), ('base plate', 'the foot'), ('spine', 'the neck post'),
             ('speaker', '40 mm round'), ('microphone', 'tiny board')]
    for i, (a, b) in enumerate(items):
        x = 0.78 + i * 2.42
        rect(x, 2.2, 2.2, 2.5, WHITE, RGBColor(0xEC, 0xE2, 0xD6), 0.18)""",
              """    items = [('body', 'the big egg'), ('base plate', 'the foot'),
             ('spine', 'the neck post'), ('speaker', '40 mm round')]
    for i, (a, b) in enumerate(items):
        x = 0.78 + i * 2.9
        rect(x, 2.2, 2.6, 2.5, WHITE, RGBColor(0xEC, 0xE2, 0xD6), 0.18)""")
s = s.replace("""        txt(x + 0.15, 2.55, 1.9, 0.9, a, size=22, bold=True, align='c')
        txt(x + 0.15, 3.6, 1.9, 0.6, b, size=17, color=GREY, align='c')""",
              """        txt(x + 0.2, 2.55, 2.2, 0.9, a, size=22, bold=True, align='c')
        txt(x + 0.2, 3.6, 2.2, 0.6, b, size=17, color=GREY, align='c')""")

# 6. delete the old Day 3 step 6 (microphone in the body) and renumber
old21 = s[s.index("    # ---------------------------------------------------------------- 21 mic"):
          s.index("    # ---------------------------------------------------------------- 22 spine")]
s = s.replace(old21, "")
s = s.replace("kicker('day 3 · step 7')", "kicker('day 3 · step 6')")
s = s.replace("kicker('day 3 · step 8')", "kicker('day 3 · step 7')")
s = s.replace("kicker('day 3 · step 9')", "kicker('day 3 · step 8')")

open(p, 'w', encoding='utf-8').write(s)
print("deck source updated")
