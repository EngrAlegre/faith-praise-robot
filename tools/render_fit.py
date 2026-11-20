"""Fit-check renders: half section + translucent ghost + head close-up."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import mesh

R = lambda p: os.path.join(os.path.dirname(__file__), '..', p)
OUT = R('renders')

shell_cut = mesh.load_stl(R('stl/asm_cut.stl'))
elec_cut  = mesh.load_stl(R('stl/asm_elec_cut.stl'))
shell     = mesh.load_stl(R('stl/asm_shell.stl'))
elec      = mesh.load_stl(R('stl/asm_electronics.stl'))

PLA  = (0.935, 0.930, 0.915)
BOARD = (0.13, 0.42, 0.52)

# --- 1. side section: shell AND electronics cut on the same plane (x > 0) ---
for tag, az in (('a', -90), ('b', 90)):
    s = mesh.Scene(w=1500, h=1500, bg=(247, 245, 242))
    s.add(shell_cut, PLA)
    s.add(elec_cut, BOARD)
    s.save(os.path.join(OUT, 'fit_side_%s.png' % tag), azim=az, elev=4)
    print('side', tag, 'ok')

# --- 2. ghost: whole shell as glass, electronics solid inside --------------
g = mesh.Scene(w=1500, h=1500, bg=(248, 247, 244))
g.add(elec, BOARD)                  # drawn first so the shell veils it
g.add(shell, PLA, alpha=0.30)
g.save(os.path.join(OUT, 'fit_ghost_3q.png'), azim=28, elev=12)
g.save(os.path.join(OUT, 'fit_ghost_side.png'), azim=88, elev=6)
print('ghost ok')
