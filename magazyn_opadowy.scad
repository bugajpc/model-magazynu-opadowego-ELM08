// ==============================================================================
// MODEL 12: MAGAZYN OPADOWY (PODAJNIK DETALI) - ZADANIE EGZAMINACYJNE
// Parametryczny model CAD do druku 3D (OpenSCAD) - WERSJA BEZSZCZELINOWA (ZERO GAP)
// ==============================================================================

$fn = 64; // Jakość zaokrągleń

// --- GŁÓWNE PARAMETRY GEOMETRYCZNE ---
cube_size     = 30.0;  // Wymiar detalu manipulacyjnego (kostki) [mm]
clearance     = 1.5;   // Całkowity luz rynny (0.75 mm na stronę) [mm]
chute_width   = cube_size + clearance; // Szerokość wewnętrzna koryta = 31.5 mm
wall_thick    = 4.5;   // Grubość ścianek bocznych rynny [mm]
bed_thick     = 5.0;   // Grubość dna rynny [mm]
wall_height   = 35.0;  // Wysokość bocznych ścianek rynny [mm]
chute_angle   = 45.0;  // Kąt nachylenia zsuwni [stopnie]
chute_length  = 155.0; // Długość koryta rynny (mieści 3-4 kostki) [mm]

// Szerokość zewnętrzna rynny i wspornika:
total_chute_w = chute_width + 2 * wall_thick; // 40.5 mm

// --- PARAMETRY PODSTAWY (COKOŁU) ---
flange_length = 144.0; // Długość dolnego kołnierza montażowego [mm]
flange_width  = 68.0;  // Szerokość kołnierza [mm]
flange_thick  = 4.0;   // Grubość kołnierza [mm]
flange_r      = 6.0;   // Promień zaokrąglenia narożników kołnierza [mm]

pedestal_l    = 110.0; // Długość cokołu [mm]
pedestal_w    = 50.0;  // Szerokość cokołu [mm]
pedestal_h    = 28.0;  // Wysokość cokołu nad kołnierzem [mm] (łączna wys. = 32mm)

// --- PARAMETRY ZDERZAKA I CZUJNIKA ---
stopper_thick = 6.0;   // Grubość zderzaka końcowego [mm]
stopper_h     = 32.0;  // Wysokość zderzaka [mm]
sensor_dia    = 12.5;  // Średnica otworu pod czujnik indukcyjny/optyczny M12 [mm]

// --- WYCIĘCIE NA CHWYTAK ROBOTA ---
cutout_len    = 33.0;  // Długość strefy wycięcia wzdłuż rynny [mm]
cutout_lip    = 4.0;   // Wysokość pozostawionej dolnej krawędzi prowadzącej [mm]

// ==============================================================================
// MODUŁY SKŁADOWE
// ==============================================================================

// 1. DOLNA PODSTAWA Z COKOŁEM (Kolor niebieski)
module podstawa() {
    color([0.2, 0.55, 0.9]) {
        difference() {
            union() {
                // Dolny kołnierz montażowy z zaokrąglonymi narożnikami
                hull() {
                    translate([-16 + flange_r, -flange_width/2 + flange_r, 0])
                        cylinder(r=flange_r, h=flange_thick);
                    translate([128 - flange_r, -flange_width/2 + flange_r, 0])
                        cylinder(r=flange_r, h=flange_thick);
                    translate([-16 + flange_r, flange_width/2 - flange_r, 0])
                        cylinder(r=flange_r, h=flange_thick);
                    translate([128 - flange_r, flange_width/2 - flange_r, 0])
                        cylinder(r=flange_r, h=flange_thick);
                }
                
                // Cokół wynoszący
                translate([0, -pedestal_w/2, flange_thick])
                    cube([pedestal_l, pedestal_w, pedestal_h]);
            }
            
            // 6 otworów montażowych fi 5.5 mm (pod śruby M5 do stołu roboczego)
            translate([-8, -26, -1]) cylinder(d=5.5, h=flange_thick+2);
            translate([-8,  26, -1]) cylinder(d=5.5, h=flange_thick+2);
            translate([56, -26, -1]) cylinder(d=5.5, h=flange_thick+2);
            translate([56,  26, -1]) cylinder(d=5.5, h=flange_thick+2);
            translate([120, -26, -1]) cylinder(d=5.5, h=flange_thick+2);
            translate([120,  26, -1]) cylinder(d=5.5, h=flange_thick+2);
            
            // 4 otwory gwintowane/pod wkręty M4 w górnej powierzchni cokołu
            translate([12, -18, flange_thick + pedestal_h - 15]) cylinder(d=3.8, h=16);
            translate([12,  18, flange_thick + pedestal_h - 15]) cylinder(d=3.8, h=16);
            translate([98, -18, flange_thick + pedestal_h - 15]) cylinder(d=3.8, h=16);
            translate([98,  18, flange_thick + pedestal_h - 15]) cylinder(d=3.8, h=16);
        }
    }
}

// 2. GÓRNA RYDNA ZE WSPORNIKIEM I ZDERZAKIEM (Kolor zielony - BEZSZCZELINOWA)
module rynna_magazynu() {
    h_base = flange_thick + pedestal_h; // 32.0 mm
    
    color([0.3, 0.75, 0.35]) {
        difference() {
            union() {
                // Płyta montażowa łącząca z cokołem (grubość 6 mm: Z=32 do 38 mm)
                translate([0, -pedestal_w/2, h_base])
                    cube([pedestal_l, pedestal_w, 6.0]);
                
                // Ciągły, pełny wspornik pionowy pod rynną (szerokość 40.5 mm = pełna szerokość rynny)
                // Kąt dokładnie 45.0° - idealne, bezszczelinowe połączenie z dnem rynny!
                translate([0, -total_chute_w/2, h_base + 6.0])
                    polyhedron(
                        points=[
                            [0, 0, 3.33], [110, 0, 0], [110, 0, 113.33], [0, 0, 0],
                            [0, total_chute_w, 3.33], [110, total_chute_w, 0], [110, total_chute_w, 113.33], [0, total_chute_w, 0]
                        ],
                        faces=[
                            [0, 1, 2], [3, 1, 0],      // bok lewy
                            [6, 5, 4], [4, 5, 7],      // bok prawy
                            [3, 7, 5, 1],              // spód
                            [1, 5, 6, 2],              // tył pionowy
                            [0, 4, 6, 2],              // góra pod kątem dokładnie 45.0°
                            [3, 0, 4, 7]               // przód pionowy
                        ]
                    );

                // Zespół koryta rynny nachylony pod kątem 45 stopni
                translate([-3.0, 0, 45.4])
                rotate([0, chute_angle, 0]) {
                    // Profil zewnętrzny rynny (dno + ścianki)
                    translate([-stopper_thick, -(chute_width/2 + wall_thick), -bed_thick])
                        cube([chute_length + stopper_thick, chute_width + 2*wall_thick, wall_height + bed_thick]);
                }
            }
            
            // --- ODCINANIE ZBĘDNYCH CZĘŚCI I DRĄŻENIE KORYTA ---
            // Odcięcie dołu pod poziomem płyty montażowej Z = h_base
            translate([-50, -60, 0])
                cube([250, 120, h_base]);

            // Odcięcie tyłu za pionową krawędzią cokołu (X > 110)
            translate([110, -60, h_base])
                cube([150, 120, 250]);

            // Wnętrze koryta rynny (tunel na kostki)
            translate([-3.0, 0, 45.4])
            rotate([0, chute_angle, 0]) {
                // Kanał przelotowy dla kostki
                translate([0, -chute_width/2, 0])
                    cube([chute_length + 10, chute_width, wall_height + 50]);

                // Wycięcie boczne na chwytak robota (odsłaniające kostkę)
                translate([0, -(chute_width/2 + wall_thick + 1), cutout_lip])
                    cube([cutout_len, chute_width + 2*wall_thick + 2, wall_height + 20]);
                
                // Otwór na czujnik obecności detalu M12 w zderzaku
                translate([-stopper_thick - 1, 0, cube_size/2])
                    rotate([0, 90, 0])
                        cylinder(d=sensor_dia, h=stopper_thick + 2);
                
                // Zaokrąglenie wlotu na górze rynny
                translate([chute_length - 5, -(chute_width/2 + wall_thick + 1), wall_height - 5])
                    cube([15, chute_width + 2*wall_thick + 2, 20]);
            }
            
            // 4 otwory pod śruby montażowe M4 z pogłębieniem walcowym pod łeb DIN 912
            for (pos = [[12, -18], [12, 18], [98, -18], [98, 18]]) {
                translate([pos[0], pos[1], h_base - 1])
                    cylinder(d=4.5, h=10);
                translate([pos[0], pos[1], h_base + 3])
                    cylinder(d=8.0, h=10);
            }
        }
    }
}

// 3. DETAL MANIPULACYJNY - KOSTKA TESTOWA (Kolor czerwony)
module detal() {
    color([0.9, 0.15, 0.15]) {
        translate([-3.0, 0, 45.4])
        rotate([0, chute_angle, 0]) {
            translate([0, -cube_size/2, 0])
                cube([cube_size, cube_size, cube_size]);
        }
    }
}

// 4. CZUJNIK ZBLIŻENIOWY M12 (Kolor czarny / mosiądz)
module czujnik_m12() {
    color([0.2, 0.2, 0.2]) {
        translate([-3.0, 0, 45.4])
        rotate([0, chute_angle, 0]) {
            translate([-stopper_thick - 35, 0, cube_size/2])
            rotate([0, 90, 0]) {
                cylinder(d=12.0, h=45); // Korpus M12
                translate([0, 0, 10]) cylinder(d=18, h=4, $fn=6); // Nakrętka kontrująca
                translate([0, 0, 40]) color([0.9, 0.6, 0.1]) cylinder(d=10.5, h=5); // Czoło optyczne/indukcyjne
            }
        }
    }
}

// 5. WIZUALIZACJA PUNKTU POBIERANIA ORAZ PUNKTU 60 MM
module wektor_najazdu() {
    p_pickup = [-3.0 + 15*cos(45) - 30*sin(45), 0, 45.4 + 15*sin(45) + 30*cos(45)];
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
calosc_zlozenie(); // Pełne złożenie demonstracyjne

module calosc_zlozenie() {
    podstawa();
    rynna_magazynu();
    detal();
    czujnik_m12();
    wektor_najazdu();
}
