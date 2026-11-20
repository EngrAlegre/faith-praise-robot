"""Repair the broken txt() call on the new plates slide."""
p = 'build_deck.py'
s = open(p, encoding='utf-8').read()

start = s.index("    txt(0.78, 6.2, 11.8, 0.9,")
end = s.index("size=19, color=GREY)", start) + len("size=19, color=GREY)")

NL = chr(92) + 'n'
replacement = (
    "    txt(0.78, 6.2, 11.8, 0.9,\n"
    "        'Every piece already fits a 180 x 180 mm printer. Nothing gets cut in half." + NL +
    "The spine is 168 mm tall - that is the only piece that must fit your printer height.',\n"
    "        size=19, color=GREY)"
)
s = s[:start] + replacement + s[end:]
open(p, 'w', encoding='utf-8').write(s)
print('repaired')
