"""Tiny STL toolkit: load, weld, split into connected solids, render orthographic views.
No external deps beyond numpy + PIL (both present in the Python 3.12 install)."""
import numpy as np, struct, os
from PIL import Image, ImageDraw, ImageFilter

# ---------------------------------------------------------------- IO
def load_stl(path):
    with open(path, 'rb') as f:
        head = f.read(84)
        if head[:5] == b'solid' and b'facet' in head:
            f.seek(0)
            txt = f.read().decode('ascii', 'replace')
            v = []
            for line in txt.splitlines():
                line = line.strip()
                if line.startswith('vertex'):
                    v.append([float(x) for x in line.split()[1:4]])
            return np.array(v, dtype=np.float64).reshape(-1, 3, 3)
        n = struct.unpack('<I', head[80:84])[0]
        data = f.read(n * 50)
    a = np.frombuffer(data, dtype=np.uint8).reshape(n, 50)
    v = a[:, 12:48].copy().view('<f4').reshape(n, 3, 3).astype(np.float64)
    return v

def weld(tris, tol=1e-4):
    """Map every vertex to a unique welded index."""
    p = tris.reshape(-1, 3)
    key = np.round(p / tol).astype(np.int64)
    _, inv = np.unique(key, axis=0, return_inverse=True)
    return inv.reshape(-1, 3), p

def components(tris):
    """Split a triangle soup into connected solids. Returns list of triangle index arrays."""
    idx, p = weld(tris)
    nv = idx.max() + 1
    parent = np.arange(nv)
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b, c in idx:
        for u, v in ((a, b), (b, c), (a, c)):
            ru, rv = find(u), find(v)
            if ru != rv:
                parent[ru] = rv
    roots = np.array([find(i) for i in range(nv)])
    tri_root = roots[idx[:, 0]]
    out = []
    for r in np.unique(tri_root):
        out.append(np.where(tri_root == r)[0])
    return out, p

def solid_volume(tris):
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    return float(np.einsum('ij,ij->i', a, np.cross(b, c)).sum() / 6.0)

def report(path):
    tris = load_stl(path)
    comps, p = components(tris)
    print(f"{os.path.basename(path)}: {len(tris)} tris, {len(comps)} solid(s), total vol {solid_volume(tris)/1000:.1f} cm3")
    for i, c in enumerate(comps):
        sub = tris[c]
        pts = sub.reshape(-1, 3)
        lo, hi = pts.min(0), pts.max(0)
        print(f"   #{i}: vol {solid_volume(sub)/1000:7.2f} cm3  bbox x[{lo[0]:7.1f},{hi[0]:7.1f}] "
              f"y[{lo[1]:7.1f},{hi[1]:7.1f}] z[{lo[2]:7.1f},{hi[2]:7.1f}]")
    return tris, comps

# ---------------------------------------------------------------- render
def rot_matrix(rx, ry, rz):
    rx, ry, rz = np.radians([rx, ry, rz])
    Rx = np.array([[1,0,0],[0,np.cos(rx),-np.sin(rx)],[0,np.sin(rx),np.cos(rx)]])
    Ry = np.array([[np.cos(ry),0,np.sin(ry)],[0,1,0],[-np.sin(ry),0,np.cos(ry)]])
    Rz = np.array([[np.cos(rz),-np.sin(rz),0],[np.sin(rz),np.cos(rz),0],[0,0,1]])
    return Rz @ Ry @ Rx

class Scene:
    def __init__(self, w=1400, h=1000, bg=(250, 249, 246)):
        self.w, self.h, self.bg = w, h, bg
        self.parts = []            # (tris, color, transform 4x4)
    def add(self, tris, color, translate=(0,0,0), rot=(0,0,0), scale=1.0, alpha=1.0):
        T = np.eye(4)
        T[:3, :3] = rot_matrix(*rot) * scale
        T[:3, 3] = translate
        self.parts.append((tris, np.array(color, float), T, alpha))
    def render(self, azim=35, elev=22, roll=0, pad=0.07, light=None,
               bg_grad=True, fname=None):
        def basis(az, el):
            a, e = np.radians(az), np.radians(el)
            v = np.array([np.sin(a)*np.cos(e), -np.cos(a)*np.cos(e), np.sin(e)])
            r = np.cross([0.0, 0.0, 1.0], v); r /= np.linalg.norm(r)
            u = np.cross(v, r)
            return v, r, u
        v, R, U = basis(azim, elev)
        pts = []
        for tris, _, T, _ in self.parts:
            p = tris.reshape(-1, 3)
            pts.append(p @ T[:3, :3].T + T[:3, 3])
        pts = np.vstack(pts)
        sx, sy, dep = pts @ R, pts @ U, pts @ v
        S = (1 - 2*pad) * min(self.w / (sx.max() - sx.min()), self.h / (sy.max() - sy.min()))
        cx, cy = (sx.min() + sx.max())/2, (sy.min() + sy.max())/2

        if bg_grad:
            top = np.array(self.bg, float)
            bot = np.clip(top*0.88, 0, 255)
            g = np.linspace(top, bot, self.h).reshape(self.h, 1, 3)
            frame = np.repeat(g, self.w, axis=1)
        else:
            frame = np.tile(np.array(self.bg, float), (self.h, self.w, 1))
        zbuf = np.full((self.h, self.w), -1e18)
        if light is None:
            light = (-0.45, -0.62, 0.65)     # from front-left, above
        L = np.array(light, float); L /= np.linalg.norm(L)

        for tris, col, T, alpha in self.parts:
            q = tris.reshape(-1, 3) @ T[:3, :3].T + T[:3, 3]      # (3N,3)
            p = q.reshape(-1, 3, 3)
            n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
            n /= (np.linalg.norm(n, axis=1)[:, None] + 1e-12)
            lam = np.abs(n @ L)                              # two-sided shading
            shade = 0.48 + 0.52 * lam
            base = 255.0 * np.array(col, float)[None, :] * shade[:, None]
            X = (((q @ R) - cx)*S + self.w/2).reshape(-1, 3)
            Y = (self.h/2 - ((q @ U) - cy)*S).reshape(-1, 3)
            D = (q @ v).reshape(-1, 3)
            for t in range(len(p)):
                xs, ys, zs = X[t], Y[t], D[t]
                x0, x1 = int(np.floor(xs.min())), int(np.ceil(xs.max()))
                y0, y1 = int(np.floor(ys.min())), int(np.ceil(ys.max()))
                if x1 < 0 or y1 < 0 or x0 >= self.w or y0 >= self.h:
                    continue
                x0, y0 = max(x0, 0), max(y0, 0)
                x1, y1 = min(x1, self.w-1), min(y1, self.h-1)
                if x1 <= x0 or y1 <= y0:
                    continue
                Xg, Yg = np.meshgrid(np.arange(x0, x1+1)+0.5, np.arange(y0, y1+1)+0.5)
                d = (ys[1]-ys[2])*(xs[0]-xs[2]) + (xs[2]-xs[1])*(ys[0]-ys[2])
                if abs(d) < 1e-12:
                    continue
                l0 = ((ys[1]-ys[2])*(Xg-xs[2]) + (xs[2]-xs[1])*(Yg-ys[2]))/d
                l1 = ((ys[2]-ys[0])*(Xg-xs[2]) + (xs[0]-xs[2])*(Yg-ys[2]))/d
                l2 = 1 - l0 - l1
                m = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
                if not m.any():
                    continue
                zi = l0*zs[0] + l1*zs[1] + l2*zs[2]
                sub = zbuf[y0:y1+1, x0:x1+1]
                upd = m & (zi > sub)
                if not upd.any():
                    continue
                sub[upd] = zi[upd]
                fr = frame[y0:y1+1, x0:x1+1]
                fr[upd] = base[t]*alpha + fr[upd]*(1-alpha)
        return frame, S

    def save(self, fname, **kw):
        frame = self.render(**kw)[0]
        out = Image.fromarray(np.clip(frame, 0, 255).astype(np.uint8))
        out.save(fname, quality=95)
        return fname

def render_turntable(scene, fname, views=((-35, 18), (0, 8), (35, 18), (125, 22)), **kw):
    imgs = []
    for az, el in views:
        f = scene.render(azim=az, elev=el, **kw)[0]
        imgs.append(Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)))
    w, h = imgs[0].size
    sheet = Image.new('RGB', (w*2, h*2), (255,255,255))
    for i, im in enumerate(imgs):
        sheet.paste(im, ((i % 2)*w, (i//2)*h))
    sheet = sheet.resize((w, h), Image.LANCZOS)
    sheet.save(fname)
    return fname


# ---------------------------------------------------------------- write
def save_stl(path, tris, name=b"hermes"):
    """Binary STL writer for a triangle soup."""
    import struct
    tris = np.asarray(tris, dtype=np.float32).reshape(-1, 3, 3)
    n = tris.reshape(-1, 3)
    with open(path, 'wb') as f:
        f.write(name.ljust(80, b' ')[:80])
        f.write(struct.pack('<I', len(tris)))
        for t in tris:
            v0, v1, v2 = t
            nrm = np.cross(v1 - v0, v2 - v0)
            ln = np.linalg.norm(nrm)
            nrm = nrm / ln if ln > 1e-12 else np.zeros(3)
            f.write(struct.pack('<3f', *nrm))
            for v in t:
                f.write(struct.pack('<3f', *v))
            f.write(struct.pack('<H', 0))
    return path
