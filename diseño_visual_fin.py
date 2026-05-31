import pygame, sys, math, random

pygame.init()

# --- CONFIGURACIÓN DE PANTALLA Y NOMBRE DE LA APLICACIÓN ---
ANCHO, ALTO = 1200, 850
pantalla = pygame.display.set_mode((ANCHO, ALTO))
TITULO_APP = "PROBOT PATHFINDER IDE"
pygame.display.set_caption(f"{TITULO_APP} v4.2 - Sistema Cartesiano")
reloj = pygame.time.Clock()

# --- FUENTES PREMIUM ---
fuente_titulo = pygame.font.SysFont("Segoe UI", 20, bold=True)
fuente_subtitulo = pygame.font.SysFont("Segoe UI", 11, bold=True)
fuente_ui = pygame.font.SysFont("Segoe UI", 13, bold=True)
fuente_mono = pygame.font.SysFont("Consolas", 13)
fuente_mono_lg = pygame.font.SysFont("Consolas", 18, bold=True)

# --- PALETA DE COLORES "INDUSTRIAL REALISTA" ---
C_VACIO = (25, 28, 35)
C_CUADRICULA = (40, 45, 55)
C_PANEL_FONDO = (35, 38, 45)
C_PANEL_CLARO = (50, 55, 65)
C_BORDE = (60, 65, 75)
C_TXT = (230, 235, 240)
C_TXT_ATENUADO = (130, 140, 150)
C_ACENTO = (0, 200, 255)
C_CENTRO = (100, 130, 210)

C_BASE_MURO = (100, 105, 115)
C_BASE_FRIC_BAJA = (30, 150, 200)
C_BASE_LENTO = (150, 110, 60)
C_BASE_INICIO = (50, 220, 120)
C_BASE_FIN = (240, 50, 65)

# --- DIMENSIONES DE LA INTERFAZ ---
UI_SUPERIOR = 70
UI_LATERAL = 300
UI_INFERIOR = 35

# --- ESTADO DEL SIMULADOR ---
camara_x, camara_y = -50, -680
tamano_celda = 55
mostrar_cuadricula = True
escala_texto = "0.5"  # Ahora son metros, 0.5m = 50cm
metros_por_celda = 0.5
editando_escala = False

mapa_celdas = {}
pos_A, pos_B = None, None
modo_actual = 1

M_BORRAR, M_MURO, M_FRIC, M_LENTO, M_A, M_B = 0, 1, 2, 3, 4, 5
herramientas = [
    {"id": M_MURO, "txt": "MURO [1]", "color": C_BASE_MURO},
    {"id": M_FRIC, "txt": "FRICCIÓN ↓ [2]", "color": C_BASE_FRIC_BAJA},
    {"id": M_LENTO, "txt": "FRICCIÓN ↑  [3]", "color": C_BASE_LENTO},
    {"id": M_BORRAR, "txt": "BORRAR [4]", "color": (180, 50, 50)},
    {"id": M_A, "txt": "ROBOT [5]", "color": C_BASE_INICIO},
    {"id": M_B, "txt": "META [6]", "color": C_BASE_FIN},
]

desplazando = False
inicio_desplazamiento, inicio_camara = (0, 0), (0, 0)

rect_escala = pygame.Rect(ANCHO - UI_LATERAL + 20, 570, 260, 30)
btn_centrar = pygame.Rect(ANCHO - UI_LATERAL + 20, 615, 260, 38)


# ==========================================
# --- TEXTURAS Y RENDERIZADO PROCEDURAL ---
# ==========================================
def generar_textura_ruido(ancho, alto, factor=8):
    textura = pygame.Surface((ancho, alto)).convert()
    for x in range(ancho):
        for y in range(alto):
            ruido = random.randint(-factor, factor)
            r = max(0, min(255, C_VACIO[0] + ruido))
            g = max(0, min(255, C_VACIO[1] + ruido))
            b = max(0, min(255, C_VACIO[2] + ruido))
            textura.set_at((x, y), (r, g, b))
    return textura


textura_suelo = generar_textura_ruido(ANCHO, ALTO, factor=8)


def dibujar_muro_realista(superficie, rect):
    pygame.draw.rect(superficie, C_BASE_MURO, rect)
    x, y, w, h = rect
    t = max(1, w // 10)

    color_claro = (min(255, C_BASE_MURO[0] + 30), min(255, C_BASE_MURO[1] + 30), min(255, C_BASE_MURO[2] + 30))
    pygame.draw.polygon(superficie, color_claro, [(x, y), (x + w, y), (x + w - t, y + t), (x + t, y + t), (x, y)])
    pygame.draw.polygon(superficie, color_claro, [(x, y), (x + t, y + t), (x + t, y + h - t), (x, y + h), (x, y)])

    color_oscuro = (max(0, C_BASE_MURO[0] - 40), max(0, C_BASE_MURO[1] - 40), max(0, C_BASE_MURO[2] - 40))
    pygame.draw.polygon(superficie, color_oscuro,
                        [(x, y + h), (x + t, y + h - t), (x + w - t, y + h - t), (x + w, y + h), (x, y + h)])
    pygame.draw.polygon(superficie, color_oscuro,
                        [(x + w, y), (x + w, y + h), (x + w - t, y + h - t), (x + w - t, y + t), (x + w, y)])

    if w > 20:
        pygame.draw.line(superficie, color_oscuro, (x + w // 2, y + t), (x + w // 2, y + h - t), 1)
        pygame.draw.line(superficie, color_oscuro, (x + t, y + h // 2), (x + w - t, y + h // 2), 1)


def dibujar_zona_baja_friccion(superficie, rect, col, fila):
    x, y, w, h = rect
    charco = pygame.Surface((w, h), pygame.SRCALPHA).convert_alpha()
    pygame.draw.rect(charco, list(C_BASE_FRIC_BAJA) + [100], (0, 0, w, h))

    random.seed(col * 100 + fila)
    for _ in range(max(1, w // 8)):
        sx = random.randint(w // 6, w - w // 6)
        sy = random.randint(h // 6, h - h // 6)
        color_mancha = (min(255, C_BASE_FRIC_BAJA[0] + 100), min(255, C_BASE_FRIC_BAJA[1] + 100), 255, 180)
        pygame.draw.circle(charco, color_mancha, (sx, sy), random.randint(1, max(2, w // 15)))
    superficie.blit(charco, (x, y))


def dibujar_zona_rugosa(superficie, rect, col, fila):
    x, y, w, h = rect
    parche = pygame.Surface((w, h), pygame.SRCALPHA).convert_alpha()
    pygame.draw.rect(parche, list(C_BASE_LENTO) + [180], (0, 0, w, h))

    random.seed(col * 50 + fila + 999)
    for _ in range(max(15, w * 2)):
        gx = random.randint(1, w - 2)
        gy = random.randint(1, h - 2)
        es_oscuro = random.choice([True, False])
        color_grano = (40, 25, 10, 130) if es_oscuro else (220, 180, 130, 110)
        pygame.draw.circle(parche, color_grano, (gx, gy), random.randint(1, 2))

    intervalo = max(8, w // 6)
    for i in range(-w // intervalo, (w + h) // intervalo + 1):
        offset_x = i * intervalo
        pygame.draw.line(parche, (80, 55, 25, 75), (offset_x, 0), (offset_x + h, h), 2)
    superficie.blit(parche, (x, y))


def dibujar_robot_realista(superficie, centro, tamano):
    x, y = centro
    r = tamano // 2 - 2
    sup_sombra = pygame.Surface((tamano, tamano), pygame.SRCALPHA).convert_alpha()
    pygame.draw.circle(sup_sombra, (0, 0, 0, 80), (tamano // 2 + 3, tamano // 2 + 3), r)
    superficie.blit(sup_sombra, (x - tamano // 2, y - tamano // 2))

    pygame.draw.circle(superficie, (C_BASE_INICIO[0] - 40, C_BASE_INICIO[1] - 40, C_BASE_INICIO[2] - 40), centro, r)
    pygame.draw.circle(superficie, C_BORDE, centro, r, 2)
    pygame.draw.circle(superficie, C_BASE_INICIO, centro, r - 3)

    sensor_r = r // 2.5
    pygame.draw.circle(superficie, (20, 25, 30), centro, int(sensor_r))
    pygame.draw.circle(superficie, (150, 180, 200, 150), (x - int(sensor_r) // 2, y - int(sensor_r) // 2), 2)

    rect_frente = pygame.Rect(x + sensor_r, y - sensor_r // 2, r - sensor_r - 1, sensor_r)
    pygame.draw.rect(superficie, (40, 45, 50), rect_frente, border_radius=2)
    pygame.draw.circle(superficie, C_BASE_INICIO, (x + r - 4, y), 1)


def dibujar_meta_realista(superficie, centro, tamano):
    x, y = centro
    r = tamano // 2 - 2

    sombra = pygame.Surface((tamano, tamano), pygame.SRCALPHA).convert_alpha()
    pygame.draw.circle(sombra, (0, 0, 0, 90), (tamano // 2 + 3, tamano // 2 + 3), r)
    superficie.blit(sombra, (x - tamano // 2, y - tamano // 2))

    pygame.draw.circle(superficie, (45, 48, 55), centro, r)
    pygame.draw.circle(superficie, (85, 90, 100), centro, r, 2)

    pygame.draw.line(superficie, (70, 75, 85), (x - r + 3, y), (x + r - 3, y), 1)
    pygame.draw.line(superficie, (70, 75, 85), (x, y - r + 3), (x, y + r - 3), 1)
    pygame.draw.circle(superficie, (60, 65, 75), centro, r // 2, 1)

    longitud_aspa = int(r * 0.65)
    grosor_aspa = max(5, tamano // 7)

    pygame.draw.line(superficie, C_BASE_FIN, (x - longitud_aspa, y - longitud_aspa),
                     (x + longitud_aspa, y + longitud_aspa), grosor_aspa)
    pygame.draw.line(superficie, C_BASE_FIN, (x - longitud_aspa, y + longitud_aspa),
                     (x + longitud_aspa, y - longitud_aspa), grosor_aspa)
    pygame.draw.circle(superficie, (255, 130, 140), centro, max(2, grosor_aspa // 2))


def dibujar_panel_industrial(superficie, rect, es_superior=True):
    x, y, w, h = rect
    for i in range(h):
        factor = i / h
        if es_superior: factor = 1.0 - factor
        r = int(C_PANEL_FONDO[0] * (1 - factor) + C_PANEL_CLARO[0] * factor)
        g = int(C_PANEL_FONDO[1] * (1 - factor) + C_PANEL_CLARO[1] * factor)
        b = int(C_PANEL_FONDO[2] * (1 - factor) + C_PANEL_CLARO[2] * factor)
        pygame.draw.line(superficie, (r, g, b), (x, y + i), (x + w, y + i))
    if es_superior:
        pygame.draw.rect(superficie, C_ACENTO, (x, y + h - 2, w, 2))
    else:
        pygame.draw.rect(superficie, C_BORDE, (x, y, 1, h))


def auto_centrar_mapa():
    coords_activas = list(mapa_celdas.keys())
    if pos_A: coords_activas.append(pos_A)
    if pos_B: coords_activas.append(pos_B)

    if not coords_activas:
        return -50, -680, 55

    coords_activas.append((0, 0))

    min_c = min(c[0] for c in coords_activas)
    max_c = max(c[0] for c in coords_activas)
    min_f = min(c[1] for c in coords_activas)
    max_f = max(c[1] for c in coords_activas)

    ancho_celdas = (max_c - min_c + 1) + 4
    alto_celdas = (max_f - min_f + 1) + 4
    espacio_w = ANCHO - UI_LATERAL
    espacio_h = ALTO - UI_SUPERIOR - UI_INFERIOR

    nuevo_tamano_celda = int(min(espacio_w / ancho_celdas, espacio_h / alto_celdas))
    nuevo_tamano_celda = max(25, min(150, nuevo_tamano_celda))

    centro_logico_x = (min_c + max_c + 1) / 2
    centro_logico_y = (min_f + max_f + 1) / 2
    nueva_camara_x = (centro_logico_x * nuevo_tamano_celda) - (espacio_w / 2)
    nueva_camara_y = (centro_logico_y * nuevo_tamano_celda) - (espacio_h / 2)
    return int(nueva_camara_x), int(nueva_camara_y), nuevo_tamano_celda


# ==========================================
# --- BUCLE PRINCIPAL ---
# ==========================================
while True:
    mx, my = pygame.mouse.get_pos()
    metros_por_celda = float(escala_texto) if escala_texto.replace('.', '', 1).isdigit() and float(
        escala_texto) > 0 else 1.0
    en_lienzo = (mx < ANCHO - UI_LATERAL) and (UI_SUPERIOR < my < ALTO - UI_INFERIOR)

    # CÁLCULO DE COORDENADAS CARTESIANAS (INVERSIÓN DEL EJE Y)
    real_x_m = ((mx + camara_x) / tamano_celda) * metros_por_celda
    real_y_m = -((my - UI_SUPERIOR + camara_y) / tamano_celda) * metros_por_celda

    w_col = (mx + camara_x) // tamano_celda
    w_fila = (my - UI_SUPERIOR + camara_y) // tamano_celda

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit();
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if editando_escala:
                if evento.key == pygame.K_RETURN:
                    editando_escala = False
                elif evento.key == pygame.K_BACKSPACE:
                    escala_texto = escala_texto[:-1]
                elif evento.unicode.isdigit() or (evento.unicode == '.' and '.' not in escala_texto):
                    escala_texto += evento.unicode
            else:
                if evento.key == pygame.K_1: modo_actual = M_MURO
                if evento.key == pygame.K_2: modo_actual = M_FRIC
                if evento.key == pygame.K_3: modo_actual = M_LENTO
                if evento.key == pygame.K_4: modo_actual = M_BORRAR
                if evento.key == pygame.K_5: modo_actual = M_A
                if evento.key == pygame.K_6: modo_actual = M_B
                if evento.key == pygame.K_g: mostrar_cuadricula = not mostrar_cuadricula
                if evento.key == pygame.K_c: camara_x, camara_y, tamano_celda = auto_centrar_mapa()

        if evento.type == pygame.MOUSEWHEEL and en_lienzo:
            tamano_celda = max(20, min(200, tamano_celda + evento.y * 3))

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if rect_escala.collidepoint(mx, my):
                editando_escala = True
            else:
                editando_escala = False

            if btn_centrar.collidepoint(mx, my):
                camara_x, camara_y, tamano_celda = auto_centrar_mapa()

            for i, h in enumerate(herramientas):
                btn_rect = pygame.Rect(300 + i * 135, 22, 125, 30)
                if btn_rect.collidepoint(mx, my): modo_actual = h["id"]

            if en_lienzo and not editando_escala:
                if modo_actual == M_A:
                    mapa_celdas.pop((w_col, w_fila), None);
                    pos_A = (w_col, w_fila)
                elif modo_actual == M_B:
                    mapa_celdas.pop((w_col, w_fila), None);
                    pos_B = (w_col, w_fila)

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 2 and en_lienzo:
            desplazando = True
            inicio_desplazamiento = (mx, my);
            inicio_camara = (camara_x, camara_y)

        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 2:
            desplazando = False

    botones_raton = pygame.mouse.get_pressed()
    if desplazando:
        camara_x = inicio_camara[0] - (mx - inicio_desplazamiento[0])
        camara_y = inicio_camara[1] - (my - inicio_desplazamiento[1])
    elif botones_raton[0] and en_lienzo and not editando_escala:
        if modo_actual in [M_MURO, M_FRIC, M_LENTO]:
            if (w_col, w_fila) not in (pos_A, pos_B): mapa_celdas[(w_col, w_fila)] = modo_actual
        elif modo_actual == M_BORRAR:
            mapa_celdas.pop((w_col, w_fila), None)

    # ==========================================
    # --- RENDERIZADO VISUAL ---
    # ==========================================
    pantalla.blit(textura_suelo, (0, 0))

    col_inicio = camara_x // tamano_celda
    fila_inicio = camara_y // tamano_celda
    cols_visibles = ((ANCHO - UI_LATERAL) // tamano_celda) + 2
    filas_visibles = ((ALTO - UI_SUPERIOR - UI_INFERIOR) // tamano_celda) + 2

    celdas_visibles = []
    for c in range(col_inicio, col_inicio + cols_visibles):
        for f in range(fila_inicio, fila_inicio + filas_visibles):
            sx = c * tamano_celda - camara_x
            sy = f * tamano_celda - camara_y + UI_SUPERIOR
            if 0 <= sx < ANCHO - UI_LATERAL and UI_SUPERIOR <= sy < ALTO - UI_INFERIOR:
                celdas_visibles.append((c, f, sx, sy))

    if mostrar_cuadricula:
        for c, f, sx, sy in celdas_visibles:
            pygame.draw.rect(pantalla, C_CUADRICULA, (sx, sy, tamano_celda, tamano_celda), 1)

    orig_x = 0 * tamano_celda - camara_x
    orig_y = 0 * tamano_celda - camara_y + UI_SUPERIOR
    if 0 < orig_x < ANCHO - UI_LATERAL:
        s = pygame.Surface((2, ALTO - UI_SUPERIOR - UI_INFERIOR), pygame.SRCALPHA);
        s.fill((100, 100, 110, 100));
        pantalla.blit(s, (orig_x, UI_SUPERIOR))
    if UI_SUPERIOR < orig_y < ALTO - UI_INFERIOR:
        s = pygame.Surface((ANCHO - UI_LATERAL, 2), pygame.SRCALPHA);
        s.fill((100, 100, 110, 100));
        pantalla.blit(s, (0, orig_y))

    for c, f, sx, sy in celdas_visibles:
        rect = (sx, sy, tamano_celda, tamano_celda)
        tipo = mapa_celdas.get((c, f), -1)
        if tipo == M_FRIC:
            dibujar_zona_baja_friccion(pantalla, rect, c, f)
        elif tipo == M_LENTO:
            dibujar_zona_rugosa(pantalla, rect, c, f)

    for c, f, sx, sy in celdas_visibles:
        if mapa_celdas.get((c, f), -1) == M_MURO:
            dibujar_muro_realista(pantalla, (sx, sy, tamano_celda, tamano_celda))

    if pos_A:
        ax, ay = pos_A[0] * tamano_celda - camara_x + tamano_celda // 2, pos_A[
            1] * tamano_celda - camara_y + UI_SUPERIOR + tamano_celda // 2
        if UI_SUPERIOR - tamano_celda < ay < ALTO - UI_INFERIOR + tamano_celda and ax < ANCHO - UI_LATERAL + tamano_celda: dibujar_robot_realista(
            pantalla, (ax, ay), tamano_celda)
    if pos_B:
        bx, by = pos_B[0] * tamano_celda - camara_x + tamano_celda // 2, pos_B[
            1] * tamano_celda - camara_y + UI_SUPERIOR + tamano_celda // 2
        if UI_SUPERIOR - tamano_celda < by < ALTO - UI_INFERIOR + tamano_celda and bx < ANCHO - UI_LATERAL + tamano_celda: dibujar_meta_realista(
            pantalla, (bx, by), tamano_celda)

    # ==========================================
    # --- INTERFAZ INDUSTRIAL CARTESIANA ---
    # ==========================================
    dibujar_panel_industrial(pantalla, (0, 0, ANCHO, UI_SUPERIOR), es_superior=True)
    pantalla.blit(fuente_titulo.render(TITULO_APP, True, C_TXT), (20, 14))
    pantalla.blit(fuente_subtitulo.render("ENTORNO DE INGENIERÍA v4.2", True, (160, 170, 180)), (20, 42))

    for i, h in enumerate(herramientas):
        btn_rect = pygame.Rect(300 + i * 135, 22, 125, 30)
        es_activo = (h["id"] == modo_actual)
        esta_encima = btn_rect.collidepoint(mx, my) and my < UI_SUPERIOR
        bg_col = C_PANEL_CLARO if es_activo else (C_PANEL_FONDO if not esta_encima else C_BORDE)
        pygame.draw.rect(pantalla, bg_col, btn_rect, border_radius=5)
        pygame.draw.rect(pantalla, h["color"] if es_activo else C_BORDE, btn_rect, 2 if es_activo else 1,
                         border_radius=5)
        txt_s = fuente_ui.render(h["txt"], True, C_TXT if (es_activo or esta_encima) else C_TXT_ATENUADO)
        pantalla.blit(txt_s, txt_s.get_rect(center=btn_rect.center))

    panel_x = ANCHO - UI_LATERAL
    dibujar_panel_industrial(pantalla, (panel_x, UI_SUPERIOR, UI_LATERAL, ALTO - UI_SUPERIOR), es_superior=False)
    pantalla.blit(fuente_titulo.render("DATOS GENERALES", True, C_TXT), (panel_x + 20, UI_SUPERIOR + 20))
    pygame.draw.line(pantalla, C_BORDE, (panel_x + 20, UI_SUPERIOR + 50), (ANCHO - 20, UI_SUPERIOR + 50), 1)

    num_muros = sum(1 for v in mapa_celdas.values() if v == M_MURO)
    num_fric = sum(1 for v in mapa_celdas.values() if v == M_FRIC)
    num_lento = sum(1 for v in mapa_celdas.values() if v == M_LENTO)
    estadisticas = [
        ("Zoom Visual:", f"{tamano_celda} px/celda", C_TXT),
        ("Entidades de Muro:", f"{num_muros} u", C_BASE_MURO),
        ("Fricción Baja (μ↓):", f"{num_fric} u", C_BASE_FRIC_BAJA),
        ("Fricción Alta (μ↑):", f"{num_lento} u", C_BASE_LENTO),
    ]
    for idx, (etiqueta, val, col) in enumerate(estadisticas):
        y_pos = UI_SUPERIOR + 75 + idx * 30
        pygame.draw.rect(pantalla, col, (panel_x + 20, y_pos + 3, 10, 10), border_radius=2)
        pantalla.blit(fuente_ui.render(etiqueta, True, C_TXT_ATENUADO), (panel_x + 38, y_pos))
        val_surf = fuente_mono.render(val, True, C_ACENTO)
        val_rect = val_surf.get_rect(topright=(ANCHO - 20, y_pos))
        pantalla.blit(val_surf, val_rect)

    y_cinematica = UI_SUPERIOR + 215
    pygame.draw.line(pantalla, C_BORDE, (panel_x + 20, y_cinematica), (ANCHO - 20, y_cinematica), 1)
    pantalla.blit(fuente_subtitulo.render("COORDENADAS DEL SISTEMA (CARTESIANO)", True, C_ACENTO),
                  (panel_x + 20, y_cinematica + 15))

    str_A = f"X:{pos_A[0] * metros_por_celda:.2f} Y:{-pos_A[1] * metros_por_celda:.2f}" if pos_A else "PENDIENTE"
    str_B = f"X:{pos_B[0] * metros_por_celda:.2f} Y:{-pos_B[1] * metros_por_celda:.2f}" if pos_B else "PENDIENTE"

    pantalla.blit(fuente_ui.render("Origen del Robot (A):", True, C_TXT_ATENUADO), (panel_x + 20, y_cinematica + 40))
    pantalla.blit(fuente_mono_lg.render(str_A, True, C_BASE_INICIO if pos_A else (150, 80, 80)),
                  (panel_x + 20, y_cinematica + 60))

    pantalla.blit(fuente_ui.render("Objetivo / Meta (B):", True, C_TXT_ATENUADO), (panel_x + 20, y_cinematica + 95))
    pantalla.blit(fuente_mono_lg.render(str_B, True, C_BASE_FIN if pos_B else (150, 80, 80)),
                  (panel_x + 20, y_cinematica + 115))

    pantalla.blit(fuente_ui.render("Distancia Vectorial Lineal A➔B:", True, C_TXT_ATENUADO),
                  (panel_x + 20, y_cinematica + 155))
    if pos_A and pos_B:
        dist_euclidea = math.sqrt((pos_B[0] - pos_A[0]) ** 2 + (pos_B[1] - pos_A[1]) ** 2) * metros_por_celda
        txt_dist = f"{dist_euclidea:.2f} m"
        col_dist = C_TXT
    else:
        txt_dist, col_dist = "PENDIENTE", (150, 80, 80)
    pantalla.blit(fuente_mono_lg.render(txt_dist, True, col_dist), (panel_x + 20, y_cinematica + 175))

    y_metrologia = y_cinematica + 215
    pygame.draw.line(pantalla, C_BORDE, (panel_x + 20, y_metrologia), (ANCHO - 20, y_metrologia), 1)

    pantalla.blit(fuente_titulo.render("REGULACIÓN DE ESCALA", True, C_TXT), (panel_x + 20, y_metrologia + 15))
    pantalla.blit(fuente_ui.render("Escala Real del Entorno:", True, C_TXT_ATENUADO), (panel_x + 20, y_metrologia + 45))

    color_caja = C_ACENTO if editando_escala else C_VACIO
    pygame.draw.rect(pantalla, color_caja, rect_escala, border_radius=4)
    pygame.draw.rect(pantalla, C_BORDE, rect_escala, 1, border_radius=4)
    pantalla.blit(fuente_mono.render(escala_texto + ("_" if editando_escala else "") + " m / celda", True, C_TXT),
                  (rect_escala.x + 15, rect_escala.y + 7))

    hvr_centrar = btn_centrar.collidepoint(mx, my) and panel_x < mx
    pygame.draw.rect(pantalla, (60, 50, 100) if not hvr_centrar else (80, 70, 130), btn_centrar, border_radius=6)
    pygame.draw.rect(pantalla, C_CENTRO, btn_centrar, 1 if not hvr_centrar else 2, border_radius=6)
    txt_c_btn = fuente_ui.render("CENTRAR MAPA [C]", True, C_TXT)
    pantalla.blit(txt_c_btn, txt_c_btn.get_rect(center=btn_centrar.center))

    pygame.draw.rect(pantalla, C_PANEL_FONDO, (0, ALTO - UI_INFERIOR, ANCHO, UI_INFERIOR))
    pygame.draw.rect(pantalla, C_BORDE, (0, ALTO - UI_INFERIOR, ANCHO, 1))
    txt_coord = fuente_mono.render(f"ABS X:{real_x_m:.2f} m │ ABS Y:{real_y_m:.2f} m", True,
                                   C_ACENTO) if en_lienzo else fuente_mono.render(
        "SISTEMA NOMINAL │ CURSOR FUERA DE LÍMITES", True, C_TXT_ATENUADO)
    pantalla.blit(txt_coord, (20, ALTO - 24))
    pantalla.blit(fuente_subtitulo.render("FUNDACIÓN PROBOT© - 2026", True, C_TXT_ATENUADO),
                  (ANCHO - UI_LATERAL - 200, ALTO - 24))

    pygame.display.flip()
    reloj.tick(60)