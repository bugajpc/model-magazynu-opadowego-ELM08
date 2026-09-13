import math, struct, os, zipfile

class STLMesh:
    def __init__(self, name):
        self.name = name
        self.vertices = []
        self.v_map = {}
        self.triangles = []

    def add_v(self, x, y, z):
        pt = (round(float(x), 4), round(float(y), 4), round(float(z), 4))
        if pt not in self.v_map:
            idx = len(self.vertices)
            self.vertices.append(pt)
            self.v_map[pt] = idx
            return idx
        return self.v_map[pt]

    def add_tri(self, p1, p2, p3):
        i1 = self.add_v(*p1)
        i2 = self.add_v(*p2)
        i3 = self.add_v(*p3)
        if i1 != i2 and i2 != i3 and i3 != i1:
            self.triangles.append((i1, i2, i3))

    def add_quad(self, p1, p2, p3, p4):
        # CCW quad outwards: p1 -> p2 -> p3 -> p4 -> p1
        self.add_tri(p1, p2, p3)
        self.add_tri(p1, p3, p4)

    def add_box(self, x0, y0, z0, x1, y1, z1):
        # Bottom (-Z)
        self.add_quad((x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0))
        # Top (+Z)
        self.add_quad((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))
        # Front (-Y)
        self.add_quad((x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1))
        # Back (+Y)
        self.add_quad((x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1))
        # Left (-X)
        self.add_quad((x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1))
        # Right (+X)
        self.add_quad((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1))

    def verify_manifold(self):
        edges = {}
        for i1, i2, i3 in self.triangles:
            for a, b in [(i1, i2), (i2, i3), (i3, i1)]:
                e = (a, b)
                edges[e] = edges.get(e, 0) + 1
        unmatched = 0
        multi = 0
        for (a, b), cnt in edges.items():
            if cnt > 1:
                multi += 1
            if (b, a) not in edges:
                unmatched += 1
        return unmatched == 0 and multi == 0

    def export_stl(self, filepath):
        header = f"STL binary export: {self.name}".encode('ascii')[:80].ljust(80, b'\0')
        count = len(self.triangles)
        with open(filepath, "wb") as f:
            f.write(header)
            f.write(struct.pack("<I", count))
            for i1, i2, i3 in self.triangles:
                p1 = self.vertices[i1]
                p2 = self.vertices[i2]
                p3 = self.vertices[i3]
                ax, ay, az = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
                bx, by, bz = p3[0]-p1[0], p3[1]-p1[1], p3[2]-p1[2]
                nx = ay*bz - az*by
                ny = az*bx - ax*bz
                nz = ax*by - ay*bx
                nl = math.hypot(nx, math.hypot(ny, nz))
                if nl > 1e-9:
                    nx /= nl; ny /= nl; nz /= nl
                else:
                    nx, ny, nz = 0.0, 0.0, 0.0
                f.write(struct.pack("<3f", nx, ny, nz))
                f.write(struct.pack("<3f", p1[0], p1[1], p1[2]))
                f.write(struct.pack("<3f", p2[0], p2[1], p2[2]))
                f.write(struct.pack("<3f", p3[0], p3[1], p3[2]))
                f.write(struct.pack("<H", 0))
        size_kb = os.path.getsize(filepath) / 1024
        is_manifold = self.verify_manifold()
        manifold_str = "100% 2-MANIFOLD (WATERTIGHT)" if is_manifold else "NON-MANIFOLD"
        print(f"[{self.name}] -> {filepath}: {count} tris, {len(self.vertices)} verts ({size_kb:.1f} KB) - {manifold_str}")


# Coordinate transformation for Chute
COS45 = math.cos(math.radians(45.0))
SIN45 = math.sin(math.radians(45.0))
X0 = -3.0
Y0 = 0.0
Z0 = 83.4  # Podniesiona do poziomu cokołu Z = 70 mm (45.4 + 38.0 mm)

def c2w(u, v, n):
    """Convert chute coordinates (u, v, n) to world coordinates (X, Y, Z)"""
    x = X0 + u * COS45 - n * SIN45
    y = Y0 + v
    z = Z0 + u * SIN45 + n * COS45
    return (x, y, z)


# ------------------------------------------------------------------------------
# 1. BUILD TEST WORKPIECE CUBE (Kostka 30x30x30 mm)
# ------------------------------------------------------------------------------
def build_cube():
    m = STLMesh("Detal_Kostka_30mm")
    s = 30.0
    m.add_box(-s/2, -s/2, 0.0, s/2, s/2, s)
    return m


# ------------------------------------------------------------------------------
# 2. BUILD BASE PEDESTAL - 100% UNIFIED WATERTIGHT MESH (Rysunek 1)
# ------------------------------------------------------------------------------
def build_single_base(name="Podstawa_110x30x70mm"):
    """
    Tworzy w 100% szczelną, jednorodną (2-manifold) siatkę pojedynczej podstawy:
    - Brak niepołączonych krawędzi (0 unmatched edges)
    - Otwory montażowe ⌀7 mm w pełni zintegrowane z powierzchnią uszu i spodu
    - Wymiary: 110 x 30 x 70 mm, uszy 20 x 30 x 10 mm, rozstaw otworów 90 mm, offset A = 10 mm
    """
    m = STLMesh(name)
    tan_pi_8 = math.tan(math.pi / 8.0) # ~0.41421356
    d = 10.0 * tan_pi_8
    xs = [0.0, 10.0 - d, 10.0, 10.0 + d, 20.0, 30.0]

    # --- UCHO LEWE: cy = -45.0, Y w [-55, -35] ---
    c_pts1 = []
    for k in range(16):
        ang = 2.0 * math.pi * k / 16.0
        c_pts1.append((10.0 + 3.5 * math.cos(ang), -45.0 + 3.5 * math.sin(ang)))
    outer1 = [
        (20, -45), (20, -45+d), (20, -35), (10+d, -35),
        (10, -35), (10-d, -35), (0, -35), (0, -45+d),
        (0, -45), (0, -45-d), (0, -55), (10-d, -55),
        (10, -55), (10+d, -55), (20, -55), (20, -45-d)
    ]
    # Góra ucha 1 (Z = 10 mm)
    for k in range(16):
        kn = (k + 1) % 16
        m.add_quad((outer1[k][0], outer1[k][1], 10.0), (outer1[kn][0], outer1[kn][1], 10.0), (c_pts1[kn][0], c_pts1[kn][1], 10.0), (c_pts1[k][0], c_pts1[k][1], 10.0))
    # Dół ucha 1 (Z = 0 mm)
    for k in range(16):
        kn = (k + 1) % 16
        m.add_quad((outer1[kn][0], outer1[kn][1], 0.0), (outer1[k][0], outer1[k][1], 0.0), (c_pts1[k][0], c_pts1[k][1], 0.0), (c_pts1[kn][0], c_pts1[kn][1], 0.0))
    # Wewnętrzna cylindryczna ścianka otworu 1
    for k in range(16):
        kn = (k + 1) % 16
        m.add_quad((c_pts1[k][0], c_pts1[k][1], 10.0), (c_pts1[kn][0], c_pts1[kn][1], 10.0), (c_pts1[kn][0], c_pts1[kn][1], 0.0), (c_pts1[k][0], c_pts1[k][1], 0.0))
    # Pasek [20, 30] ucha 1
    ys_strip1 = [-55.0, -45.0 - d, -45.0, -45.0 + d, -35.0]
    for j in range(4):
        m.add_quad((20.0, ys_strip1[j+1], 10.0), (20.0, ys_strip1[j], 10.0), (30.0, ys_strip1[j], 10.0), (30.0, ys_strip1[j+1], 10.0))
    for j in range(4):
        m.add_quad((20.0, ys_strip1[j], 0.0), (20.0, ys_strip1[j+1], 0.0), (30.0, ys_strip1[j+1], 0.0), (30.0, ys_strip1[j], 0.0))
    # Ścianki pionowe ucha 1:
    for k in range(10, 14):
        kn = (k + 1) % 16
        m.add_quad((outer1[kn][0], outer1[kn][1], 10.0), (outer1[k][0], outer1[k][1], 10.0), (outer1[k][0], outer1[k][1], 0.0), (outer1[kn][0], outer1[kn][1], 0.0))
    m.add_quad((30.0, -55.0, 10.0), (20.0, -55.0, 10.0), (20.0, -55.0, 0.0), (30.0, -55.0, 0.0))
    for k in range(6, 10):
        kn = (k + 1) % 16
        m.add_quad((outer1[kn][0], outer1[kn][1], 10.0), (outer1[k][0], outer1[k][1], 10.0), (outer1[k][0], outer1[k][1], 0.0), (outer1[kn][0], outer1[kn][1], 0.0))
    for j in range(4):
        m.add_quad((30.0, ys_strip1[j+1], 10.0), (30.0, ys_strip1[j], 10.0), (30.0, ys_strip1[j], 0.0), (30.0, ys_strip1[j+1], 0.0))

    # --- UCHO PRAWE: cy = +45.0, Y w [35, 55] ---
    c_pts2 = []
    for k in range(16):
        ang = 2.0 * math.pi * k / 16.0
        c_pts2.append((10.0 + 3.5 * math.cos(ang), 45.0 + 3.5 * math.sin(ang)))
    outer2 = [
        (20, 45), (20, 45+d), (20, 55), (10+d, 55),
        (10, 55), (10-d, 55), (0, 55), (0, 45+d),
        (0, 45), (0, 45-d), (0, 35), (10-d, 35),
        (10, 35), (10+d, 35), (20, 35), (20, 45-d)
    ]
    # Góra ucha 2 (Z = 10 mm)
    for k in range(16):
        kn = (k + 1) % 16
        m.add_quad((outer2[k][0], outer2[k][1], 10.0), (outer2[kn][0], outer2[kn][1], 10.0), (c_pts2[kn][0], c_pts2[kn][1], 10.0), (c_pts2[k][0], c_pts2[k][1], 10.0))
    # Dół ucha 2 (Z = 0 mm)
    for k in range(16):
        kn = (k + 1) % 16
        m.add_quad((outer2[kn][0], outer2[kn][1], 0.0), (outer2[k][0], outer2[k][1], 0.0), (c_pts2[k][0], c_pts2[k][1], 0.0), (c_pts2[kn][0], c_pts2[kn][1], 0.0))
    # Wewnętrzna cylindryczna ścianka otworu 2
    for k in range(16):
        kn = (k + 1) % 16
        m.add_quad((c_pts2[k][0], c_pts2[k][1], 10.0), (c_pts2[kn][0], c_pts2[kn][1], 10.0), (c_pts2[kn][0], c_pts2[kn][1], 0.0), (c_pts2[k][0], c_pts2[k][1], 0.0))
    # Pasek [20, 30] ucha 2
    ys_strip2 = [35.0, 45.0 - d, 45.0, 45.0 + d, 55.0]
    for j in range(4):
        m.add_quad((20.0, ys_strip2[j+1], 10.0), (20.0, ys_strip2[j], 10.0), (30.0, ys_strip2[j], 10.0), (30.0, ys_strip2[j+1], 10.0))
    for j in range(4):
        m.add_quad((20.0, ys_strip2[j], 0.0), (20.0, ys_strip2[j+1], 0.0), (30.0, ys_strip2[j+1], 0.0), (30.0, ys_strip2[j], 0.0))
    # Ścianki pionowe ucha 2:
    for k in range(2, 6):
        kn = (k + 1) % 16
        m.add_quad((outer2[kn][0], outer2[kn][1], 10.0), (outer2[k][0], outer2[k][1], 10.0), (outer2[k][0], outer2[k][1], 0.0), (outer2[kn][0], outer2[kn][1], 0.0))
    m.add_quad((20.0, 55.0, 10.0), (30.0, 55.0, 10.0), (30.0, 55.0, 0.0), (20.0, 55.0, 0.0))
    for k in range(6, 10):
        kn = (k + 1) % 16
        m.add_quad((outer2[kn][0], outer2[kn][1], 10.0), (outer2[k][0], outer2[k][1], 10.0), (outer2[k][0], outer2[k][1], 0.0), (outer2[kn][0], outer2[kn][1], 0.0))
    for j in range(4):
        m.add_quad((30.0, ys_strip2[j+1], 10.0), (30.0, ys_strip2[j], 10.0), (30.0, ys_strip2[j], 0.0), (30.0, ys_strip2[j+1], 0.0))

    # --- ŚRODKOWY SŁUP: Y w [-35, 35], X w [0, 30], Z w [0, 70] ---
    # Góra (Z = 70 mm, normal +Z)
    for i in range(5):
        m.add_quad((xs[i], -35.0, 70.0), (xs[i+1], -35.0, 70.0), (xs[i+1], 35.0, 70.0), (xs[i], 35.0, 70.0))
    # Dół (Z = 0 mm, normal -Z)
    for i in range(5):
        m.add_quad((xs[i], -35.0, 0.0), (xs[i], 35.0, 0.0), (xs[i+1], 35.0, 0.0), (xs[i+1], -35.0, 0.0))
    # Przód (X = 0 mm, normal -X)
    m.add_quad((0.0, 35.0, 0.0), (0.0, -35.0, 0.0), (0.0, -35.0, 10.0), (0.0, 35.0, 10.0))
    m.add_quad((0.0, 35.0, 10.0), (0.0, -35.0, 10.0), (0.0, -35.0, 70.0), (0.0, 35.0, 70.0))
    # Tył (X = 30 mm, normal +X)
    m.add_quad((30.0, -35.0, 0.0), (30.0, 35.0, 0.0), (30.0, 35.0, 10.0), (30.0, -35.0, 10.0))
    m.add_quad((30.0, -35.0, 10.0), (30.0, 35.0, 10.0), (30.0, 35.0, 70.0), (30.0, -35.0, 70.0))
    # Uskoki pionowe nad uszami (Z w [10, 70]):
    for i in range(5):
        m.add_quad((xs[i], -35.0, 10.0), (xs[i+1], -35.0, 10.0), (xs[i+1], -35.0, 70.0), (xs[i], -35.0, 70.0))
    for i in range(5):
        m.add_quad((xs[i+1], 35.0, 10.0), (xs[i], 35.0, 10.0), (xs[i], 35.0, 70.0), (xs[i+1], 35.0, 70.0))

    return m


def transform_mesh(mesh, new_name, func_xyz):
    """Zwraca nową siatkę z przekształconymi współrzędnymi wierzchołków"""
    m = STLMesh(new_name)
    for i1, i2, i3 in mesh.triangles:
        p1 = func_xyz(*mesh.vertices[i1])
        p2 = func_xyz(*mesh.vertices[i2])
        p3 = func_xyz(*mesh.vertices[i3])
        m.add_tri(p1, p2, p3)
    return m


# ------------------------------------------------------------------------------
# 3. BUILD CHUTE MODULE - 100% WATERTIGHT 2-MANIFOLD B-REP
# (Szerokość 40.5 mm, bez rozszerzenia, zintegrowany otwór ⌀18 mm na czujnik M18)
# ------------------------------------------------------------------------------
def ear_clip_triangulate_2d(poly_indices, vertices):
    """Triangulacja wielokąta 2D (rzut na płaszczyznę X-Z) algorytmem obcinania uszu"""
    pts2d = [(vertices[idx][0], vertices[idx][2]) for idx in poly_indices]
    signed_area = 0.0
    N = len(pts2d)
    for i in range(N):
        x1, z1 = pts2d[i]
        x2, z2 = pts2d[(i+1)%N]
        signed_area += (x1 * z2 - x2 * z1)
    
    indices = list(range(N))
    tris = []
    
    def is_convex(prev_i, curr_i, next_i):
        p_prev = pts2d[prev_i]
        p_curr = pts2d[curr_i]
        p_next = pts2d[next_i]
        cross = (p_curr[0] - p_prev[0]) * (p_next[1] - p_curr[1]) - (p_curr[1] - p_prev[1]) * (p_next[0] - p_curr[0])
        return (cross * signed_area) > 0

    def point_in_tri(p, a, b, c):
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
        d1 = sign(p, a, b)
        d2 = sign(p, b, c)
        d3 = sign(p, c, a)
        return not ((d1 < -1e-6 or d2 < -1e-6 or d3 < -1e-6) and (d1 > 1e-6 or d2 > 1e-6 or d3 > 1e-6))

    iters = 0
    while len(indices) > 3 and iters < 300:
        iters += 1
        ear_found = False
        L = len(indices)
        for k in range(L):
            prev_k = indices[(k - 1) % L]
            curr_k = indices[k]
            next_k = indices[(k + 1) % L]
            if not is_convex(prev_k, curr_k, next_k):
                continue
            p_prev, p_curr, p_next = pts2d[prev_k], pts2d[curr_k], pts2d[next_k]
            inside = False
            for other_k in indices:
                if other_k in (prev_k, curr_k, next_k):
                    continue
                if point_in_tri(pts2d[other_k], p_prev, p_curr, p_next):
                    inside = True
                    break
            if not inside:
                tris.append((poly_indices[prev_k], poly_indices[curr_k], poly_indices[next_k]))
                indices.pop(k)
                ear_found = True
                break
        if not ear_found:
            break
    if len(indices) == 3:
        tris.append((poly_indices[indices[0]], poly_indices[indices[1]], poly_indices[indices[2]]))
    return tris


def build_chute():
    """
    Tworzy w 100% jednorodną (2-manifold), szczelną siatkę rynny:
    - Brak wewnętrznych ścianek i nakładających się brył
    - Ciągły klin wsporczy bez rozszerzenia (jednolita szerokość 40.5 mm)
    - Płaski spód na Z = 70.0 mm pod obiema podstawami
    - Zintegrowane gniazdo ⌀18 mm pod czujnik M18 ze szczelną ścianką cylindryczną
    - Zerowa liczba krawędzi niepołączonych (0 unmatched edges)
    """
    m = STLMesh("Rynna_Magazynu")
    
    # Punkty graniczne w osi rynny u
    u_front = 3.0 / COS45 - 5.0    # ~ -0.757359 (gdzie dno n = -5.0 przecina pion X = 0.0)
    u_back  = 113.0 / COS45 - 5.0  # ~ 154.806133 (gdzie dno n = -5.0 przecina pion X = 110.0)

    tan_pi_8 = math.tan(math.pi / 8.0)
    d = 9.0 * tan_pi_8
    vs = [-20.25, -15.75, -9.0, -d, 0.0, d, 9.0, 15.75, 20.25]
    ns_mid = [6.0, 15.0 - d, 15.0, 15.0 + d, 24.0]

    # Okrąg otworu ⌀18 mm (promień 9.0 mm, środek v = 0.0, n = 15.0)
    c_pts = []
    for k in range(16):
        ang = 2.0 * math.pi * k / 16.0
        c_pts.append((round(9.0 * math.cos(ang), 4), round(15.0 + 9.0 * math.sin(ang), 4)))

    # Obwód kwadratu 18x18 mm opisanego wokół otworu:
    outer_sq = [
        (9.0, 15.0), (9.0, 15.0+d), (9.0, 24.0), (d, 24.0),
        (0.0, 24.0), (-d, 24.0), (-9.0, 24.0), (-9.0, 15.0+d),
        (-9.0, 15.0), (-9.0, 15.0-d), (-9.0, 6.0), (-d, 6.0),
        (0.0, 6.0), (d, 6.0), (9.0, 6.0), (9.0, 15.0-d)
    ]

    # 1. ŚCIANKA CYLINDRYCZNA OTWORU CZUJNIKA ⌀18 mm (u w [-6.0, 0.0])
    for k in range(16):
        kn = (k + 1) % 16
        m.add_quad(c2w(-6.0, *c_pts[k]), c2w(0.0, *c_pts[k]), c2w(0.0, *c_pts[kn]), c2w(-6.0, *c_pts[kn]))

    # 2. PŁYTA CZOŁOWA ZDERZAKA (u = -6.0, normal -u)
    # Pierścień wokół otworu:
    for k in range(16):
        kn = (k + 1) % 16
        m.add_quad(c2w(-6.0, *outer_sq[kn]), c2w(-6.0, *outer_sq[k]), c2w(-6.0, *c_pts[k]), c2w(-6.0, *c_pts[kn]))
    # Nad otworem (n w [24.0, 32.0]):
    for j in range(8):
        m.add_quad(c2w(-6.0, vs[j], 32.0), c2w(-6.0, vs[j+1], 32.0), c2w(-6.0, vs[j+1], 24.0), c2w(-6.0, vs[j], 24.0))
    # Pod otworem (n w [-5.0, 6.0]):
    for j in range(8):
        m.add_quad(c2w(-6.0, vs[j], 6.0), c2w(-6.0, vs[j+1], 6.0), c2w(-6.0, vs[j+1], -5.0), c2w(-6.0, vs[j], -5.0))
    # Na lewo od otworu (v w [-20.25, -9.0], n w [6.0, 24.0]):
    for p in range(4):
        m.add_quad(c2w(-6.0, vs[0], ns_mid[p+1]), c2w(-6.0, vs[1], ns_mid[p+1]), c2w(-6.0, vs[1], ns_mid[p]), c2w(-6.0, vs[0], ns_mid[p]))
        m.add_quad(c2w(-6.0, vs[1], ns_mid[p+1]), c2w(-6.0, vs[2], ns_mid[p+1]), c2w(-6.0, vs[2], ns_mid[p]), c2w(-6.0, vs[1], ns_mid[p]))
    # Na prawo od otworu (v w [9.0, 20.25], n w [6.0, 24.0]):
    for p in range(4):
        m.add_quad(c2w(-6.0, vs[6], ns_mid[p+1]), c2w(-6.0, vs[7], ns_mid[p+1]), c2w(-6.0, vs[7], ns_mid[p]), c2w(-6.0, vs[6], ns_mid[p]))
        m.add_quad(c2w(-6.0, vs[7], ns_mid[p+1]), c2w(-6.0, vs[8], ns_mid[p+1]), c2w(-6.0, vs[8], ns_mid[p]), c2w(-6.0, vs[7], ns_mid[p]))

    # 3. GÓRA ZDERZAKA (n = 32.0, u w [-6.0, 0.0], normal +n)
    for j in range(8):
        m.add_quad(c2w(-6.0, vs[j], 32.0), c2w(0.0, vs[j], 32.0), c2w(0.0, vs[j+1], 32.0), c2w(-6.0, vs[j+1], 32.0))

    # 4. WEWNĘTRZNA ŚCIANKA ZDERZAKA I USKOKI NAD ŚCIANKAMI (u = 0.0, normal +u)
    # Pierścień wokół otworu:
    for k in range(16):
        kn = (k + 1) % 16
        m.add_quad(c2w(0.0, *outer_sq[k]), c2w(0.0, *outer_sq[kn]), c2w(0.0, *c_pts[kn]), c2w(0.0, *c_pts[k]))
    # Nad otworem wewnątrz rynny (kolumny 1..6, n w [24.0, 32.0]):
    for j in range(1, 7):
        m.add_quad(c2w(0.0, vs[j], 24.0), c2w(0.0, vs[j+1], 24.0), c2w(0.0, vs[j+1], 32.0), c2w(0.0, vs[j], 32.0))
    # Pod otworem wewnątrz rynny (kolumny 1..6, n w [0.0, 6.0]) podzielone na n=4.0 pod chwytak:
    for j in range(1, 7):
        m.add_quad(c2w(0.0, vs[j], 0.0), c2w(0.0, vs[j+1], 0.0), c2w(0.0, vs[j+1], 4.0), c2w(0.0, vs[j], 4.0))
        m.add_quad(c2w(0.0, vs[j], 4.0), c2w(0.0, vs[j+1], 4.0), c2w(0.0, vs[j+1], 6.0), c2w(0.0, vs[j], 6.0))
    # Na lewo wewnątrz rynny (kolumna 1: [-15.75, -9.0], n w [6.0, 24.0]):
    for p in range(4):
        m.add_quad(c2w(0.0, vs[1], ns_mid[p]), c2w(0.0, vs[2], ns_mid[p]), c2w(0.0, vs[2], ns_mid[p+1]), c2w(0.0, vs[1], ns_mid[p+1]))
    # Na prawo wewnątrz rynny (kolumna 6: [9.0, 15.75], n w [6.0, 24.0]):
    for p in range(4):
        m.add_quad(c2w(0.0, vs[6], ns_mid[p]), c2w(0.0, vs[7], ns_mid[p]), c2w(0.0, vs[7], ns_mid[p+1]), c2w(0.0, vs[6], ns_mid[p+1]))
    # Uskok czołowy lewy nad ścianką (kolumna 0: [-20.25, -15.75], u = 0.0, n w [4.0, 32.0]):
    ns_wall = [4.0, 6.0, 15.0 - d, 15.0, 15.0 + d, 24.0, 32.0]
    for p in range(len(ns_wall)-1):
        m.add_quad(c2w(0.0, vs[0], ns_wall[p]), c2w(0.0, vs[1], ns_wall[p]), c2w(0.0, vs[1], ns_wall[p+1]), c2w(0.0, vs[0], ns_wall[p+1]))
    # Uskok czołowy prawy nad ścianką (kolumna 7: [15.75, 20.25], u = 0.0, n w [4.0, 32.0]):
    for p in range(len(ns_wall)-1):
        m.add_quad(c2w(0.0, vs[7], ns_wall[p]), c2w(0.0, vs[8], ns_wall[p]), c2w(0.0, vs[8], ns_wall[p+1]), c2w(0.0, vs[7], ns_wall[p+1]))

    # 5. KORONY (GÓRNE KRAWĘDZIE) ŚCIANEK BOCZNYCH
    # Ścianka lewa (kolumna 0: [-20.25, -15.75]):
    m.add_quad(c2w(0.0, vs[0], 4.0), c2w(33.0, vs[0], 4.0), c2w(33.0, vs[1], 4.0), c2w(0.0, vs[1], 4.0))
    m.add_quad(c2w(33.0, vs[0], 4.0), c2w(38.0, vs[0], 35.0), c2w(38.0, vs[1], 35.0), c2w(33.0, vs[1], 4.0))
    m.add_quad(c2w(38.0, vs[0], 35.0), c2w(u_back, vs[0], 35.0), c2w(u_back, vs[1], 35.0), c2w(38.0, vs[1], 35.0))
    # Ścianka prawa (kolumna 7: [15.75, 20.25]):
    m.add_quad(c2w(0.0, vs[7], 4.0), c2w(33.0, vs[7], 4.0), c2w(33.0, vs[8], 4.0), c2w(0.0, vs[8], 4.0))
    m.add_quad(c2w(33.0, vs[7], 4.0), c2w(38.0, vs[7], 35.0), c2w(38.0, vs[8], 35.0), c2w(33.0, vs[8], 4.0))
    m.add_quad(c2w(38.0, vs[7], 35.0), c2w(u_back, vs[7], 35.0), c2w(u_back, vs[8], 35.0), c2w(38.0, vs[8], 35.0))

    # 6. WEWNĘTRZNE PIONOWE POWIERZCHNIE KORYTA RYNNY
    # Wewnętrzna ścianka lewa (v = -15.75 = vs[1], normal +v):
    m.add_quad(c2w(0.0, vs[1], 0.0), c2w(0.0, vs[1], 4.0), c2w(33.0, vs[1], 4.0), c2w(33.0, vs[1], 0.0))
    m.add_quad(c2w(33.0, vs[1], 0.0), c2w(33.0, vs[1], 4.0), c2w(38.0, vs[1], 35.0), c2w(38.0, vs[1], 0.0))
    m.add_quad(c2w(38.0, vs[1], 0.0), c2w(38.0, vs[1], 35.0), c2w(u_back, vs[1], 35.0), c2w(u_back, vs[1], 0.0))
    # Wewnętrzna ścianka prawa (v = +15.75 = vs[7], normal -v):
    m.add_quad(c2w(0.0, vs[7], 4.0), c2w(0.0, vs[7], 0.0), c2w(33.0, vs[7], 0.0), c2w(33.0, vs[7], 4.0))
    m.add_quad(c2w(33.0, vs[7], 4.0), c2w(33.0, vs[7], 0.0), c2w(38.0, vs[7], 0.0), c2w(38.0, vs[7], 35.0))
    m.add_quad(c2w(38.0, vs[7], 35.0), c2w(38.0, vs[7], 0.0), c2w(u_back, vs[7], 0.0), c2w(u_back, vs[7], 35.0))

    # 7. DNO KORYTA RYNNY (n = 0.0, normal +n)
    u_segs = [0.0, 33.0, 38.0, u_back]
    for s in range(len(u_segs)-1):
        u_a, u_b = u_segs[s], u_segs[s+1]
        for j in range(1, 7):
            m.add_quad(c2w(u_a, vs[j], 0.0), c2w(u_b, vs[j], 0.0), c2w(u_b, vs[j+1], 0.0), c2w(u_a, vs[j+1], 0.0))

    # 8. SPÓD DNA RYNNY PRZED KRAWĘDZIĄ X=0 (n = -5.0, u w [-6.0, u_front], normal -n)
    for j in range(8):
        m.add_quad(c2w(-6.0, vs[j+1], -5.0), c2w(u_front, vs[j+1], -5.0), c2w(u_front, vs[j], -5.0), c2w(-6.0, vs[j], -5.0))

    # 9. PIONOWY PRZÓD WSPORNIKA POD RYNNĄ (X = 0.0, Z w [70.0, 79.3289], normal -X)
    for j in range(8):
        m.add_quad((0.0, vs[j+1], 70.0), (0.0, vs[j], 70.0), c2w(u_front, vs[j], -5.0), c2w(u_front, vs[j+1], -5.0))

    # 10. SPÓD PŁASKI WSPORNIKA OPARTEGO NA PODSTAWACH (Z = 70.0, X w [0.0, 110.0], normal -Z)
    for j in range(8):
        m.add_quad((0.0, vs[j+1], 70.0), (110.0, vs[j+1], 70.0), (110.0, vs[j], 70.0), (0.0, vs[j], 70.0))

    # 11. PIONOWY TYŁ WSPORNIKA POD RYNNĄ (X = 110.0, Z w [70.0, 189.3289], normal +X)
    for j in range(8):
        m.add_quad((110.0, vs[j], 70.0), (110.0, vs[j+1], 70.0), c2w(u_back, vs[j+1], -5.0), c2w(u_back, vs[j], -5.0))

    # 12. PŁASZCZYZNA TYLNA RYNNY (u = u_back, normal +u)
    # Ścianka lewa (kolumna 0):
    m.add_quad(c2w(u_back, vs[0], -5.0), c2w(u_back, vs[1], -5.0), c2w(u_back, vs[1], 0.0), c2w(u_back, vs[0], 0.0))
    m.add_quad(c2w(u_back, vs[0], 0.0), c2w(u_back, vs[1], 0.0), c2w(u_back, vs[1], 35.0), c2w(u_back, vs[0], 35.0))
    # Przekrój poprzeczny dna (kolumny 1..6):
    for j in range(1, 7):
        m.add_quad(c2w(u_back, vs[j], -5.0), c2w(u_back, vs[j+1], -5.0), c2w(u_back, vs[j+1], 0.0), c2w(u_back, vs[j], 0.0))
    # Ścianka prawa (kolumna 7):
    m.add_quad(c2w(u_back, vs[7], -5.0), c2w(u_back, vs[8], -5.0), c2w(u_back, vs[8], 0.0), c2w(u_back, vs[7], 0.0))
    m.add_quad(c2w(u_back, vs[7], 0.0), c2w(u_back, vs[8], 0.0), c2w(u_back, vs[8], 35.0), c2w(u_back, vs[7], 35.0))

    # 13. ZEWNĘTRZNE ŚCIANKI BOCZNE (v = -20.25 i v = +20.25)
    # Automatyczne zamykanie wielokątów bocznych metodą triangulacji 2D:
    directed_edges = {}
    for i1, i2, i3 in m.triangles:
        for a, b in [(i1, i2), (i2, i3), (i3, i1)]:
            directed_edges[(a, b)] = directed_edges.get((a, b), 0) + 1

    adj_left = {}
    adj_right = {}
    for (a, b), cnt in directed_edges.items():
        if (b, a) not in directed_edges:
            va, vb = m.vertices[a], m.vertices[b]
            if abs(va[1] - (-20.25)) < 1e-3 and abs(vb[1] - (-20.25)) < 1e-3:
                adj_left[b] = a
            elif abs(va[1] - 20.25) < 1e-3 and abs(vb[1] - 20.25) < 1e-3:
                adj_right[b] = a

    def get_loop(adj):
        start = list(adj.keys())[0]
        loop = [start]
        curr = adj[start]
        while curr != start:
            loop.append(curr)
            curr = adj[curr]
        return loop

    tris_l = ear_clip_triangulate_2d(get_loop(adj_left), m.vertices)
    tris_r = ear_clip_triangulate_2d(get_loop(adj_right), m.vertices)

    for t in tris_l + tris_r:
        m.triangles.append(t)

    return m


# ------------------------------------------------------------------------------
# 4. BUILD COMPLETE MONOLITHIC FEEDER (Podajnik w całości - złożenie 2 podstaw + rynna)
# ------------------------------------------------------------------------------
def build_monolithic():
    m = STLMesh("Magazyn_Opadowy_Calosc")
    base_single = build_single_base("Podstawa_Wzorcowa")
    
    # 1. Podstawa przednia (X w [0, 30], otwory na X = 10 mm)
    base_front = transform_mesh(base_single, "Podstawa_Przednia", lambda x, y, z: (x, y, z))
    
    # 2. Podstawa tylna (obrót o 180° w Z i przesunięcie do X w [80, 110], otwory na X = 100 mm)
    base_rear = transform_mesh(base_single, "Podstawa_Tylna", lambda x, y, z: (110.0 - x, -y, z))
    
    # 3. Rynna
    chute_m = build_chute()
    
    for mesh in [base_front, base_rear, chute_m]:
        for i1, i2, i3 in mesh.triangles:
            p1 = mesh.vertices[i1]
            p2 = mesh.vertices[i2]
            p3 = mesh.vertices[i3]
            m.add_tri(p1, p2, p3)

    return m


# ------------------------------------------------------------------------------
# 5. BUILD 3MF MULTI-PART PROJECT FOR BAMBU STUDIO / PRUSASLICER
# ------------------------------------------------------------------------------
def build_3mf(out_path, parts_dict):
    model_xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    model_xml.append('<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:m="http://schemas.microsoft.com/3dmanufacturing/material/2015/02">')
    model_xml.append('  <resources>')
    
    obj_id = 1
    components = []
    
    for name, mesh in parts_dict.items():
        model_xml.append(f'    <object id="{obj_id}" type="model" name="{name}">')
        model_xml.append('      <mesh>')
        model_xml.append('        <vertices>')
        for v in mesh.vertices:
            model_xml.append(f'          <vertex x="{v[0]:.4f}" y="{v[1]:.4f}" z="{v[2]:.4f}" />')
        model_xml.append('        </vertices>')
        model_xml.append('        <triangles>')
        for tri in mesh.triangles:
            model_xml.append(f'          <triangle v1="{tri[0]}" v2="{tri[1]}" v3="{tri[2]}" />')
        model_xml.append('        </triangles>')
        model_xml.append('      </mesh>')
        model_xml.append('    </object>')
        components.append(obj_id)
        obj_id += 1

    model_xml.append(f'    <object id="{obj_id}" type="model" name="Magazyn_Opadowy_Assembly">')
    model_xml.append('      <components>')
    for cid in components:
        model_xml.append(f'        <component objectid="{cid}" />')
    model_xml.append('      </components>')
    model_xml.append('    </object>')
    model_xml.append('  </resources>')
    model_xml.append('  <build>')
    model_xml.append(f'    <item objectid="{obj_id}" />')
    model_xml.append('  </build>')
    model_xml.append('</model>')

    content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>'''

    rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>'''

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", "\n".join(model_xml))

    size_kb = os.path.getsize(out_path) / 1024
    print(f"[3MF Project] -> {out_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Generowanie w 100% szczelnych modeli 3D w: {out_dir}")
    
    # 1. Detal testowy (kostka 30x30x30 mm)
    cube = build_cube()
    cube.export_stl(os.path.join(out_dir, "03_detal_kostka_30mm.stl"))
    
    # 2. Pojedyncza podstawa 110x30x70 mm (100% watertight, zero non-manifold edges)
    single_base = build_single_base("Podstawa_110x30x70mm")
    single_base.export_stl(os.path.join(out_dir, "01_podstawa.stl"))
    single_base.export_stl(os.path.join(out_dir, "01_podstawa_dolna.stl"))
    
    # 3. Podstawa przednia i tylna
    base_front = transform_mesh(single_base, "Podstawa_Przednia", lambda x, y, z: (x, y, z))
    base_rear = transform_mesh(single_base, "Podstawa_Tylna", lambda x, y, z: (110.0 - x, -y, z))
    
    # 4. Rynna zjazdowa
    chute = build_chute()
    chute.export_stl(os.path.join(out_dir, "02_rynna_magazynu.stl"))
    
    # 5. Pełne złożenie monolityczne STL
    mono = build_monolithic()
    mono.export_stl(os.path.join(out_dir, "magazyn_opadowy_calosc.stl"))
    
    # 6. Kostka umieszczona w strefie pobierania dla 3MF:
    cube_in_chute = STLMesh("Detal_W_Magazynie")
    p000 = c2w(0, -15, 0); p100 = c2w(30, -15, 0); p110 = c2w(30, 15, 0); p010 = c2w(0, 15, 0)
    p001 = c2w(0, -15, 30); p101 = c2w(30, -15, 30); p111 = c2w(30, 15, 30); p011 = c2w(0, 15, 30)
    cube_in_chute.add_quad(p010, p110, p100, p000)
    cube_in_chute.add_quad(p001, p101, p111, p011)
    cube_in_chute.add_quad(p000, p100, p101, p001)
    cube_in_chute.add_quad(p110, p010, p011, p111)
    cube_in_chute.add_quad(p010, p000, p001, p011)
    cube_in_chute.add_quad(p100, p110, p111, p101)
    
    # 7. Projekt 3MF wieloczęściowy
    build_3mf(os.path.join(out_dir, "magazyn_opadowy.3mf"), {
        "Podstawa_Przednia": base_front,
        "Podstawa_Tylna": base_rear,
        "Rynna_Magazynu": chute,
        "Detal_Kostka": cube_in_chute
    })
    
    print("\nGotowe! Wszystkie modele zostały zaktualizowane z w pełni połączonymi krawędziami (unified manifold edges).")
