"""Render the assembly with the front half cut away, electronics inside."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import mesh

R = lambda p: os.path.join(os.path.dirname(__file__), '..', p)

shell = mesh.load_stl(R('stl/asm_cut.stl'))
elec  = mesh.load_stl(R('stl/asm_electronics.stl'))

s = mesh.Scene(w=1500, h=1500, bg=(247, 245, 242))
s.add(shell, (0.935, 0.930, 0.915))      # PLA
s.add(elec,  (0.13, 0.42, 0.52))         # electronics

out = R('renders')
s.save(os.path.join(out, 'assembly_cut_front.png'), azim=6, elev=10)
print('front ok')
s.save(os.path.join(out, 'assembly_cut_3q.png'), azim=42, elev=16)
print('3q ok')
s.save(os.path.join(out, 'assembly_cut_head.png'), azim=-14, elev=6, pad=0.02)
print('head ok')
