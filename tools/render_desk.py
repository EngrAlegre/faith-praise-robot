"""Render the desk robot (3rd design, square eye boxes) from the STLs."""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import mesh

STL = '../stl/pos'
P = {k: mesh.load_stl(os.path.join(STL, k + '.stl')) for k in
     ['body', 'base', 'spine', 'head', 'head_back']}

EYE_Z = 202.0


def cylinder(r, h, seg=64, caps=True):
    a = np.linspace(0, 2*np.pi, seg, endpoint=False)
    bot = np.stack([r*np.cos(a), r*np.sin(a), np.full(seg, -h/2)], 1)
    top = bot.copy(); top[:, 2] = h/2
    tris = []
    for i in range(seg):
        j = (i+1) % seg
        tris += [[bot[i], bot[j], top[j]], [bot[i], top[j], top[i]]]
        if caps:
            cb = np.array([0, 0, -h/2]); ct = np.array([0, 0, h/2])
            tris += [[cb, bot[j], bot[i]], [ct, top[i], top[j]]]
    return np.array(tris)


def box(w, d, h):
    x, y, z = w/2, d/2, h/2
    v = np.array([[sx*x, sy*y, sz*z] for sx in (-1,1) for sy in (-1,1) for sz in (-1,1)])
    idx = [(0,1,3),(0,3,2),(4,6,7),(4,7,5),(0,4,5),(0,5,1),(2,3,7),(2,7,6),(0,2,6),(0,6,4),(1,5,7),(1,7,3)]
    return np.array([[v[a], v[b], v[c]] for a,b,c in idx])


def scene():
    s = mesh.Scene(w=1500, h=1500, bg=(247, 245, 242))
    white = (0.945, 0.945, 0.935)
    s.add(P['body'], white)
    s.add(P['base'], (0.88, 0.88, 0.87))
    s.add(P['spine'], (0.70, 0.70, 0.73))
    s.add(P['head'], (0.965, 0.965, 0.955))
    s.add(P['head_back'], (0.93, 0.93, 0.92))
    # the 2.42" OLED sitting inside the eye box
    s.add(box(61.5, 1.6, 39.5), (0.06, 0.06, 0.07), translate=(0, -24.0, EYE_Z))
    s.add(box(55.01, 0.5, 27.49), (0.90, 0.94, 1.0), translate=(0, -25.0, EYE_Z))
    return s


if __name__ == '__main__':
    os.makedirs('../renders', exist_ok=True)
    sc = scene()
    sc.save('../renders/hero.png', azim=-18, elev=8, pad=0.09)
    sc.save('../renders/front.png', azim=0, elev=2, pad=0.09)
    sc.save('../renders/side.png', azim=88, elev=4, pad=0.09)
    sc.save('../renders/back.png', azim=170, elev=12, pad=0.09)
    sc.save('../renders/top3q.png', azim=-40, elev=35, pad=0.09)
    print('renders written')
