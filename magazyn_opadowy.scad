// ==============================================================================
// MODEL 12: MAGAZYN OPADOWY (PODAJNIK DETALI) - ZADANIE EGZAMINACYJNE
// Parametryczny model CAD do druku 3D (OpenSCAD) - WERSJA Z 2 PODSTAWAMI I OTWOREM ⌀18
// ==============================================================================

$fn = 64; // Jakość zaokrągleń

// --- GŁÓWNE PARAMETRY GEOMETRYCZNE RYNNY ---
cube_size     = 30.0;  // Wymiar detalu manipulacyjnego (kostki) [mm]
clearance     = 1.5;   // Całkowity luz rynny (0.75 mm na stronę) [mm]
chute_width   = cube_size + clearance; // Szerokość wewnętrzna koryta = 31.5 mm
wall_thick    = 4.5;   // Grubość ścianek bocznych rynny [mm]
bed_thick     = 5.0;   // Grubość dna rynny [mm]
wall_height   = 35.0;  // Wysokość bocznych ścianek rynny [mm]
chute_angle   = 45.0;  // Kąt nachylenia zsuwni [stopnie]
chute_length  = 155.0; // Długość koryta rynny (mieści 3-4 kostki) [mm]

// Szerokość zewnętrzna rynny i wspornika (jednolita, bez rozszerzania na dole):
total_chute_w = chute_width + 2 * wall_thick; // 40.5 mm

// --- PARAMETRY PODSTAW (ZGODNE Z RYSUNKAMI 1 I 2) ---
base_l        = 110.0; // Długość całkowita podstawy [mm]
base_w        = 30.0;  // Szerokość (głębokość) podstawy [mm]
base_h        = 70.0;  // Wysokość całkowita podstawy [mm]

base_center_l = 70.0;  // Długość środkowego słupa [mm]
base_flange_l = 20.0;  // Długość ucha montażowego z każdej strony [mm] (20 + 70 + 20 = 110)
base_flange_h = 10.0;  // Grubość/wysokość ucha [mm]

base_hole_dia = 7.0;   // Średnica otworów montażowych [mm] (otwory ⌀7 pod śruby M6)
base_hole_spacing_y = 90.0; // Rozstaw otworów wzdłuż długości podstawy [mm] (10 + 70 + 10 = 90)
base_hole_offset_x  = 10.0; // Wymiar A = 10 mm (od krawędzi zewnętrznej w osi X, asymetryczny)

// Położenie montażowe rynny nad stołem:
h_base        = base_h; // 70.0 mm
chute_z0      = 83.4;   // Wysokość punktu bazowego rynny (45.4 + 38.0 mm) [mm]

// --- PARAMETRY ZDERZAKA I CZUJNIKA ZBLIŻENIOWEGO ---
stopper_thick = 6.0;   // Grubość zderzaka końcowego [mm]
stopper_h     = 32.0;  // Wysokość zderzaka [mm]
sensor_dia    = 18.0;  // Średnica otworu pod czujnik zbliżeniowy M18 [mm] (zgodnie z wytycznymi: ⌀18)

// --- WYCIĘCIE NA CHWYTAK ROBOTA ---
cutout_len    = 33.0;  // Długość strefy wycięcia wzdłuż rynny [mm]
cutout_lip    = 4.0;   // Wysokość pozostawionej dolnej krawędzi prowadzącej [mm]

// ==============================================================================
// MODUŁY SKŁADOWE
// ==============================================================================

// 1. JEDNOSTKOWA PODSTAWA DO DRUKU 3D (Wymiary z Rysunku 1)
module podstawa_jedna() {
    color([0.2, 0.55, 0.9]) {
        difference() {
            union() {
                // Środkowy słup główny: 70 mm długości, 30 mm szerokości, 70 mm wysokości
                translate([0, -base_center_l/2, 0])
                    cube([base_w, base_center_l, base_h]);
                
                // Lewe ucho montażowe (20 mm długości, 30 mm szerokości, 10 mm grubości)
                translate([0, -base_l/2, 0])
                    cube([base_w, base_flange_l, base_flange_h]);
                
                // Prawe ucho montażowe (20 mm długości, 30 mm szerokości, 10 mm grubości)
                translate([0, base_center_l/2, 0])
                    cube([base_w, base_flange_l, base_flange_h]);
            }
            
            // 2 otwory ⌀7 mm pod śruby M6:
            // Rozstaw wzdłuż podstawy = 90 mm (Y = -45 mm oraz Y = +45 mm)
            // Wymiar A = 10 mm od przedniej krawędzi (X = 10 mm)
            translate([base_hole_offset_x, -base_hole_spacing_y/2, -1])
                cylinder(d=base_hole_dia, h=base_flange_h + 2);
            
            translate([base_hole_offset_x, base_hole_spacing_y/2, -1])
                cylinder(d=base_hole_dia, h=base_flange_h + 2);
        }
    }
}

// 2. ZESPÓŁ DWÓCH PODSTAW POD RYNNĄ (Układ z Rysunku 2: siatka otworów 90x90 mm)
module podstawy() {
    // Podstawa 1 (przednia): X od 0 do 30 mm, otwory na X = 10 mm
    translate([0, 0, 0])
        podstawa_jedna();
    
    // Podstawa 2 (tylna): identyczny detal obrócony o 180° w osi Z i przesunięty
    // X od 80 do 110 mm, otwory na X = 100 mm (rozstaw otworów w X = 90 mm!)
    translate([110, 0, 0])
        rotate([0, 0, 180])
            podstawa_jedna();
}

// 3. GÓRNA RYNNA ZE WSPORNIKIEM I ZDERZAKIEM (Bez rozszerzenia na dole, otwór ⌀18)
module rynna_magazynu() {
    color([0.3, 0.75, 0.35]) {
        difference() {
            union() {
                // Ciągły, pełny wspornik pionowy pod rynną (szerokość 40.5 mm = pełna szerokość rynny)
                // Kąt dokładnie 45.0° - idealne, bezszczelinowe połączenie z dnem rynny!
                // Spód spoczywa na Z = 70.0 mm (na obu podstawach o wysokości 70 mm)
                translate([0, -total_chute_w/2, h_base])
                    polyhedron(
                        points=[
                            [0, 0, 9.33], [110, 0, 0], [110, 0, 119.33], [0, 0, 0],
                            [0, total_chute_w, 9.33], [110, total_chute_w, 0], [110, total_chute_w, 119.33], [0, total_chute_w, 0]
                        ],
                        faces=[
                            [0, 1, 2], [3, 1, 0],      // bok lewy
                            [6, 5, 4], [4, 5, 7],      // bok prawy
                            [3, 7, 5, 1],              // spód (płaski na Z=70)
                            [1, 5, 6, 2],              // tył pionowy (X=110)
                            [0, 4, 6, 2],              // góra pod kątem dokładnie 45.0°
                            [3, 0, 4, 7]               // przód pionowy (X=0)
                        ]
                    );

                // Zespół koryta rynny nachylony pod kątem 45 stopni
                translate([-3.0, 0, chute_z0])
                rotate([0, chute_angle, 0]) {
                    // Profil zewnętrzny rynny (dno + ścianki)
                    translate([-stopper_thick, -(chute_width/2 + wall_thick), -bed_thick])
                        cube([chute_length + stopper_thick, chute_width + 2*wall_thick, wall_height + bed_thick]);
                }
            }
            
            // --- ODCINANIE ZBĘDNYCH CZĘŚCI I DRĄŻENIE KORYTA ---
            // Odcięcie dołu pod poziomem podstaw Z = h_base (70 mm)
            translate([-50, -60, 0])
                cube([250, 120, h_base]);

            // Odcięcie tyłu za pionową krawędzią podstawy tylnej (X > 110)
            translate([110, -60, h_base])
                cube([150, 120, 250]);

            // Wnętrze koryta rynny (tunel na kostki)
            translate([-3.0, 0, chute_z0])
            rotate([0, chute_angle, 0]) {
                // Kanał przelotowy dla kostki
                translate([0, -chute_width/2, 0])
                    cube([chute_length + 10, chute_width, wall_height + 50]);

                // Wycięcie boczne na chwytak robota (odsłaniające kostkę)
                translate([0, -(chute_width/2 + wall_thick + 1), cutout_lip])
                    cube([cutout_len, chute_width + 2*wall_thick + 2, wall_height + 20]);
                
                // Otwór ⌀18 mm na czujnik obecności detalu w zderzaku
                translate([-stopper_thick - 1, 0, cube_size/2])
                    rotate([0, 90, 0])
                        cylinder(d=sensor_dia, h=stopper_thick + 2);
                
                // Zaokrąglenie wlotu na górze rynny
                translate([chute_length - 5, -(chute_width/2 + wall_thick + 1), wall_height - 5])
                    cube([15, chute_width + 2*wall_thick + 2, 20]);
            }
        }
    }
}

// 4. DETAL MANIPULACYJNY - KOSTKA TESTOWA (Kolor czerwony)
module detal() {
    color([0.9, 0.15, 0.15]) {
        translate([-3.0, 0, chute_z0])
        rotate([0, chute_angle, 0]) {
            translate([0, -cube_size/2, 0])
                cube([cube_size, cube_size, cube_size]);
        }
    }
}

// 5. CZUJNIK ZBLIŻENIOWY M18 (Kolor ciemnoszary / mosiądz)
module czujnik_m18() {
    color([0.2, 0.2, 0.2]) {
        translate([-3.0, 0, chute_z0])
        rotate([0, chute_angle, 0]) {
            translate([-stopper_thick - 45, 0, cube_size/2])
            rotate([0, 90, 0]) {
                cylinder(d=18.0, h=55); // Korpus M18 (⌀18 mm)
                translate([0, 0, 12]) cylinder(d=24, h=5, $fn=6); // Nakrętka M18
                translate([0, 0, 50]) color([0.9, 0.6, 0.1]) cylinder(d=16.0, h=5); // Czoło aktywne
            }
        }
    }
}

// 6. WIZUALIZACJA PUNKTU POBIERANIA ORAZ PUNKTU 60 MM
module wektor_najazdu() {
    p_pickup = [-3.0 + 15*cos(45) - 30*sin(45), 0, chute_z0 + 15*sin(45) + 30*cos(45)];
    v_norm   = [-sin(45), 0, cos(45)];
    p_60mm   = [p_pickup[0] + 60*v_norm[0], 0, p_pickup[2] + 60*v_norm[2]];
    
    // Punkt pobierania (czerwona kropka)
    color([1, 0, 0]) translate(p_pickup) sphere(r=2.5);
    
    // Linia najazdu 60 mm
    color([0.1, 0.1, 0.1])
        hull() {
            translate(p_pickup) sphere(r=0.6);
            translate(p_60mm) sphere(r=0.6);
        }
        
    // Punkt 60 mm nad detalem (czarna kropka)
    color([0, 0, 0]) translate(p_60mm) sphere(r=2.5);
}

// ==============================================================================
// WYBÓR WIDOKU / RENDEROWANIA
// ==============================================================================
// Domyślnie: pełne złożenie. Aby wyeksportować pojedynczy detal do druku,
// odkomentuj odpowiednią linię poniżej:

calosc_zlozenie();       // Pełne złożenie montażowe
// podstawa_jedna();     // Pojedyncza podstawa (drukuj x2)
// rynna_magazynu();     // Sama rynna zjazdowa

module calosc_zlozenie() {
    podstawy();
    rynna_magazynu();
    detal();
    czujnik_m18();
    wektor_najazdu();
}
