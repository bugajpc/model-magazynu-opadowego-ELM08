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
        # CCW quad outwards
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

    def add_hole_plate(self, cx, cy, z0, z1, r_hole, box_half_w, box_half_h, n_circle=16):
        """Creates a plate with a cylindrical through hole"""
        circle_pts = []
        for i in range(n_circle):
            angle = 2.0 * math.pi * i / n_circle
            circle_pts.append((cx + r_hole * math.cos(angle), cy + r_hole * math.sin(angle)))
        
        outer_pts = []
        for i in range(4):
            outer_pts.append((cx - box_half_w + 2*box_half_w*(i/4.0), cy - box_half_h))
        for i in range(4):
            outer_pts.append((cx + box_half_w, cy - box_half_h + 2*box_half_h*(i/4.0)))
        for i in range(4):
            outer_pts.append((cx + box_half_w - 2*box_half_w*(i/4.0), cy + box_half_h))
        for i in range(4):
            outer_pts.append((cx - box_half_w, cy + box_half_h - 2*box_half_h*(i/4.0)))
            
        for i in range(16):
            i_next = (i + 1) % 16
            # Bottom face (facing -Z)
            self.add_tri((outer_pts[i][0], outer_pts[i][1], z0),
                         (circle_pts[i_next][0], circle_pts[i_next][1], z0),
                         (outer_pts[i_next][0], outer_pts[i_next][1], z0))
            self.add_tri((outer_pts[i][0], outer_pts[i][1], z0),
                         (circle_pts[i][0], circle_pts[i][1], z0),
                         (circle_pts[i_next][0], circle_pts[i_next][1], z0))
            # Top face (facing +Z)
            self.add_tri((outer_pts[i][0], outer_pts[i][1], z1),
                         (outer_pts[i_next][0], outer_pts[i_next][1], z1),
                         (circle_pts[i_next][0], circle_pts[i_next][1], z1))
            self.add_tri((outer_pts[i][0], outer_pts[i][1], z1),
                         (circle_pts[i_next][0], circle_pts[i_next][1], z1),
                         (circle_pts[i][0], circle_pts[i][1], z1))
            # Hole inner wall (normals pointing inward toward center)
            self.add_quad((circle_pts[i][0], circle_pts[i][1], z0),
                          (circle_pts[i][0], circle_pts[i][1], z1),
                          (circle_pts[i_next][0], circle_pts[i_next][1], z1),
                          (circle_pts[i_next][0], circle_pts[i_next][1], z0))

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
        print(f"[{self.name}] -> {filepath}: {count} tris, {len(self.vertices)} verts ({size_kb:.1f} KB)")


# Coordinate transformation for Chute
COS45 = math.cos(math.radians(45.0))
SIN45 = math.sin(math.radians(45.0))
X0 = -3.0
Y0 = 0.0
Z0 = 45.4

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
    c = 1.0 # 1 mm chamfer
    m.add_box(-s/2 + c, -s/2 + c, 0, s/2 - c, s/2 - c, s)
    m.add_box(-s/2, -s/2 + c, c, -s/2 + c, s/2 - c, s - c)
    m.add_box(s/2 - c, -s/2 + c, c, s/2, s/2 - c, s - c)
    m.add_box(-s/2 + c, -s/2, c, s/2 - c, -s/2 + c, s - c)
    m.add_box(-s/2 + c, s/2 - c, c, s/2 - c, s/2, s - c)
    m.add_box(-s/2 + c, -s/2 + c, 0, s/2 - c, s/2 - c, c)
    m.add_box(-s/2 + c, -s/2 + c, s - c, s/2 - c, s/2 - c, s)
    return m


# ------------------------------------------------------------------------------
# 2. BUILD BASE PEDESTAL (Podstawa - Cokół)
# ------------------------------------------------------------------------------
def build_base():
    m = STLMesh("Podstawa_Cokol")
    
    # Flange Z: [0, 4], X in [-16, 128], Y in [-34, 34]
    hole_coords = [(-8, -26), (-8, 26), (56, -26), (56, 26), (120, -26), (120, 26)]
    for hx, hy in hole_coords:
        m.add_hole_plate(hx, hy, 0.0, 4.0, 2.75, 7.0, 7.0, n_circle=16)
        m.add_quad((hx - 7, hy + 7, 0), (hx - 7, hy - 7, 0), (hx - 7, hy - 7, 4), (hx - 7, hy + 7, 4))
        m.add_quad((hx + 7, hy - 7, 0), (hx + 7, hy + 7, 0), (hx + 7, hy + 7, 4), (hx + 7, hy - 7, 4))
        m.add_quad((hx - 7, hy - 7, 0), (hx + 7, hy - 7, 0), (hx + 7, hy - 7, 4), (hx - 7, hy - 7, 4))
        m.add_quad((hx + 7, hy + 7, 0), (hx - 7, hy + 7, 0), (hx - 7, hy + 7, 4), (hx + 7, hy + 7, 4))

    # Flange solid core:
    m.add_box(-16.0, -19.0, 0.0, 128.0, 19.0, 4.0)
    
    # Outer side strips along Y:
    m.add_box(-16.0, -34.0, 0.0, -15.0, -19.0, 4.0)
    m.add_box(-1.0, -34.0, 0.0, 49.0, -19.0, 4.0)
    m.add_box(63.0, -34.0, 0.0, 113.0, -19.0, 4.0)
    m.add_box(127.0, -34.0, 0.0, 128.0, -19.0, 4.0)
    
    m.add_box(-16.0, 19.0, 0.0, -15.0, 34.0, 4.0)
    m.add_box(-1.0, 19.0, 0.0, 49.0, 34.0, 4.0)
    m.add_box(63.0, 19.0, 0.0, 113.0, 34.0, 4.0)
    m.add_box(127.0, 19.0, 0.0, 128.0, 34.0, 4.0)

    # Pedestal block: X in [0, 110], Y in [-25, 25], Z in [4, 32]
    m.add_box(0.0, -25.0, 4.0, 110.0, 25.0, 32.0)
    
    return m


# ------------------------------------------------------------------------------
# 3. BUILD CHUTE MODULE - ZERO GAP SOLID GEOMETRY
# ------------------------------------------------------------------------------
def build_chute():
    m = STLMesh("Rynna_Magazynu")
    
    # 1. Baseplate of chute module (resting directly on pedestal top Z=32 to 38):
    # X in [0, 110], Y in [-25, 25], Z in [32, 38]
    m.add_box(0.0, -25.0, 32.0, 110.0, 25.0, 38.0)
    
    # 2. Continuous Solid Support Wedge (Klin nośny pod rynną):
    # Fills the space between baseplate top (Z=38) and the chute bed underside (Z = X + 41.33)
    # Width matches full chute width: Y in [-20.25, 20.25]
    # At X=0: Z from 38.0 to 41.33 mm
    # At X=110: Z from 38.0 to 151.33 mm
    # Slope = 1.000 (Angle = EXACTLY 45.000°) - 100% SEAMLESS ZERO GAP!
    wy0 = -20.25
    wy1 = +20.25
    z_front_top = 41.33
    z_back_top  = 151.33
    
    # Front vertical face (X = 0, Z in [38, 41.33])
    m.add_quad((0.0, wy1, 38.0), (0.0, wy0, 38.0), (0.0, wy0, z_front_top), (0.0, wy1, z_front_top))
    # Rear vertical face (X = 110, Z in [38, 151.33])
    m.add_quad((110.0, wy0, 38.0), (110.0, wy1, 38.0), (110.0, wy1, z_back_top), (110.0, wy0, z_back_top))
    # Left side face (Y = -20.25)
    m.add_quad((0.0, wy0, 38.0), (110.0, wy0, 38.0), (110.0, wy0, z_back_top), (0.0, wy0, z_front_top))
    # Right side face (Y = +20.25)
    m.add_quad((110.0, wy1, 38.0), (0.0, wy1, 38.0), (0.0, wy1, z_front_top), (110.0, wy1, z_back_top))
    # Bottom face (Z = 38.0, X in [0, 110])
    m.add_quad((0.0, wy1, 38.0), (110.0, wy1, 38.0), (110.0, wy0, 38.0), (0.0, wy0, 38.0))
    # Top inclined face: matches underside of chute bed perfectly
    m.add_quad((0.0, wy0, z_front_top), (110.0, wy0, z_back_top), (110.0, wy1, z_back_top), (0.0, wy1, z_front_top))

    # Helper function for adding boxes in chute local coordinates (u, v, n):
    def add_chute_box(u0, u1, v0, v1, n0, n1):
        p000 = c2w(u0, v0, n0)
        p100 = c2w(u1, v0, n0)
        p110 = c2w(u1, v1, n0)
        p010 = c2w(u0, v1, n0)
        p001 = c2w(u0, v0, n1)
        p101 = c2w(u1, v0, n1)
        p111 = c2w(u1, v1, n1)
        p011 = c2w(u0, v1, n1)
        # Bottom (-n)
        m.add_quad(p010, p110, p100, p000)
        # Top (+n)
        m.add_quad(p001, p101, p111, p011)
        # Left (-v)
        m.add_quad(p000, p100, p101, p001)
        # Right (+v)
        m.add_quad(p110, p010, p011, p111)
        # Front (-u)
        m.add_quad(p010, p000, p001, p011)
        # Back (+u)
        m.add_quad(p100, p110, p111, p101)

    # 3. Chute Bed:
    # Extends from u=0 to u=155 mm, width v in [-20.25, 20.25], thickness n in [-5, 0]
    add_chute_box(0.0, 155.0, -20.25, 20.25, -5.0, 0.0)

    # 4. Stopper plate with Sensor Hole M12 (radius 6.25 mm at v=0, n=15):
    add_chute_box(-6.0, 0.0, -20.25, 20.25, -5.0, 8.75)
    add_chute_box(-6.0, 0.0, -20.25, 20.25, 21.25, 32.0)
    add_chute_box(-6.0, 0.0, -20.25, -6.25, 8.75, 21.25)
    add_chute_box(-6.0, 0.0, 6.25, 20.25, 8.75, 21.25)
    
    # Cylindrical inner wall of sensor hole:
    n_hole_segs = 16
    for i in range(n_hole_segs):
        a1 = 2 * math.pi * i / n_hole_segs
        a2 = 2 * math.pi * (i + 1) / n_hole_segs
        v1, n1 = 6.25 * math.cos(a1), 15.0 + 6.25 * math.sin(a1)
        v2, n2 = 6.25 * math.cos(a2), 15.0 + 6.25 * math.sin(a2)
        p_u0_1 = c2w(-6.0, v1, n1)
        p_u0_2 = c2w(-6.0, v2, n2)
        p_u1_1 = c2w(0.0, v1, n1)
        p_u1_2 = c2w(0.0, v2, n2)
        m.add_quad(p_u0_1, p_u1_1, p_u1_2, p_u0_2)

    # 5. Left Chute Wall (v in [-20.25, -15.75]):
    # Pickup zone: u in [0, 33.0], lowered to n in [0, 4.0] (robot gripper cutout)
    add_chute_box(0.0, 33.0, -20.25, -15.75, 0.0, 4.0)
    # Main wall: u in [38.0, 155.0], full height n in [0.0, 35.0]
    add_chute_box(38.0, 155.0, -20.25, -15.75, 0.0, 35.0)
    # Transition wedge: u in [33.0, 38.0]
    p_a0 = c2w(33.0, -20.25, 0.0); p_a1 = c2w(38.0, -20.25, 0.0)
    p_b0 = c2w(33.0, -15.75, 0.0); p_b1 = c2w(38.0, -15.75, 0.0)
    p_c0 = c2w(33.0, -20.25, 4.0); p_c1 = c2w(38.0, -20.25, 35.0)
    p_d0 = c2w(33.0, -15.75, 4.0); p_d1 = c2w(38.0, -15.75, 35.0)
    m.add_quad(p_b0, p_b1, p_a1, p_a0)
    m.add_quad(p_c0, p_c1, p_d1, p_d0)
    m.add_quad(p_a0, p_a1, p_c1, p_c0)
    m.add_quad(p_b1, p_b0, p_d0, p_d1)

    # 6. Right Chute Wall (v in [15.75, 20.25]):
    # Pickup zone: u in [0, 33.0], lowered to n in [0, 4.0]
    add_chute_box(0.0, 33.0, 15.75, 20.25, 0.0, 4.0)
    # Main wall: u in [38.0, 155.0], full height n in [0.0, 35.0]
    add_chute_box(38.0, 155.0, 15.75, 20.25, 0.0, 35.0)
    # Transition wedge: u in [33.0, 38.0]
    q_a0 = c2w(33.0, 15.75, 0.0); q_a1 = c2w(38.0, 15.75, 0.0)
    q_b0 = c2w(33.0, 20.25, 0.0); q_b1 = c2w(38.0, 20.25, 0.0)
    q_c0 = c2w(33.0, 15.75, 4.0); q_c1 = c2w(38.0, 15.75, 35.0)
    q_d0 = c2w(33.0, 20.25, 4.0); q_d1 = c2w(38.0, 20.25, 35.0)
    m.add_quad(q_b0, q_b1, q_a1, q_a0)
    m.add_quad(q_c0, q_c1, q_d1, q_d0)
    m.add_quad(q_a0, q_a1, q_c1, q_c0)
    m.add_quad(q_b1, q_b0, q_d0, q_d1)

    return m


# ------------------------------------------------------------------------------
# 4. BUILD COMPLETE MONOLITHIC FEEDER (Podajnik w całości - 1 wydruk)
# ------------------------------------------------------------------------------
def build_monolithic():
    m = STLMesh("Magazyn_Opadowy_Calosc")
    base_m = build_base()
    chute_m = build_chute()
    
    for i1, i2, i3 in base_m.triangles:
        p1 = base_m.vertices[i1]
        p2 = base_m.vertices[i2]
        p3 = base_m.vertices[i3]
        m.add_tri(p1, p2, p3)
        
    for i1, i2, i3 in chute_m.triangles:
        p1 = chute_m.vertices[i1]
        p2 = chute_m.vertices[i2]
        p3 = chute_m.vertices[i3]
        m.add_tri(p1, p2, p3)

    return m


# ------------------------------------------------------------------------------
# 5. BUILD 3MF MULTI-PART PROJECT FOR BAMBU STUDIO
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
    out_dir = "/Users/bartoszbugajski/Documents/projects/tests/podajnik_detali_3d"
    os.makedirs(out_dir, exist_ok=True)
    
    print("Regenerating 3D Models with Seamless Zero-Gap Geometry...")
    cube = build_cube()
    cube.export_stl(os.path.join(out_dir, "03_detal_kostka_30mm.stl"))
    
    base = build_base()
    base.export_stl(os.path.join(out_dir, "01_podstawa_dolna.stl"))
    
    chute = build_chute()
    chute.export_stl(os.path.join(out_dir, "02_rynna_magazynu.stl"))
    
    mono = build_monolithic()
    mono.export_stl(os.path.join(out_dir, "magazyn_opadowy_calosc.stl"))
    
    # Detail placed inside the chute for 3MF assembly:
    cube_in_chute = STLMesh("Detal_W_Magazynie")
    p000 = c2w(0, -15, 0); p100 = c2w(30, -15, 0); p110 = c2w(30, 15, 0); p010 = c2w(0, 15, 0)
    p001 = c2w(0, -15, 30); p101 = c2w(30, -15, 30); p111 = c2w(30, 15, 30); p011 = c2w(0, 15, 30)
    cube_in_chute.add_quad(p010, p110, p100, p000)
    cube_in_chute.add_quad(p001, p101, p111, p011)
    cube_in_chute.add_quad(p000, p100, p101, p001)
    cube_in_chute.add_quad(p110, p010, p011, p111)
    cube_in_chute.add_quad(p010, p000, p001, p011)
    cube_in_chute.add_quad(p100, p110, p111, p101)
    
    build_3mf(os.path.join(out_dir, "magazyn_opadowy.3mf"), {
        "Base": base,
        "Chute": chute,
        "Cube": cube_in_chute
    })
    
    print("All models regenerated with ZERO GAP!")
