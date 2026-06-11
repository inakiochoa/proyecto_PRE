# main.py
import pygame
import sys
import math
from constantes import *
import motor
import graficos
import ia 

pygame.init()

# --- CONFIGURACIÓN DE VENTANA ---
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption(f"{TITULO_APP} v4.2 - Sistema Cartesiano Modular")
reloj = pygame.time.Clock()

# --- FUENTES PREMIUM ---
fuente_titulo = pygame.font.SysFont("Segoe UI", 20, bold=True)
fuente_subtitulo = pygame.font.SysFont("Segoe UI", 11, bold=True)
fuente_ui = pygame.font.SysFont("Segoe UI", 13, bold=True)
fuente_mono = pygame.font.SysFont("Consolas", 13)
fuente_mono_lg = pygame.font.SysFont("Consolas", 18, bold=True)

# Elementos estáticos interactivas
rect_escala = pygame.Rect(ANCHO - UI_LATERAL + 20, 570, 260, 30)
btn_centrar = pygame.Rect(ANCHO - UI_LATERAL + 20, 615, 260, 38)
btn_iniciar = pygame.Rect(ANCHO - UI_LATERAL + 20, 665, 260, 38)
btn_borrar = pygame.Rect(ANCHO - UI_LATERAL + 20, 715, 260, 38)

# Animación del robot
robot_en_movimiento = False
ultimo_movimiento_ticket = 0
INTERVALO_MOVIMIENTO = 500
angulo_robot = 0

# Textura procedural de fondo
textura_suelo = graficos.generar_textura_ruido(ANCHO, ALTO, factor=8)

# --- BUCLE PRINCIPAL ---
while True:
    mx, my = pygame.mouse.get_pos()

    if motor.escala_texto.replace('.', '', 1).isdigit() and float(motor.escala_texto) > 0:
        motor.metros_por_celda = float(motor.escala_texto)
    else:
        motor.metros_por_celda = 1.0

    en_lienzo = (mx < ANCHO - UI_LATERAL) and (UI_SUPERIOR < my < ALTO - UI_INFERIOR)

    # Coordenadas cartesianas
    real_x_m = ((mx + motor.camara_x) / motor.tamano_celda) * motor.metros_por_celda
    real_y_m = -((my - UI_SUPERIOR + motor.camara_y) / motor.tamano_celda) * motor.metros_por_celda

    w_col = (mx + motor.camara_x) // motor.tamano_celda
    w_fila = (my - UI_SUPERIOR + motor.camara_y) // motor.tamano_celda

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if motor.editando_escala:
                if evento.key == pygame.K_RETURN:
                    motor.editando_escala = False
                elif evento.key == pygame.K_BACKSPACE:
                    motor.escala_texto = motor.escala_texto[:-1]
                elif evento.unicode.isdigit() or (evento.unicode == '.' and '.' not in motor.escala_texto):
                    motor.escala_texto += evento.unicode
            else:
                if evento.key == pygame.K_1: motor.modo_actual = M_MURO
                if evento.key == pygame.K_2: motor.modo_actual = M_FRIC
                if evento.key == pygame.K_3: motor.modo_actual = M_LENTO
                if evento.key == pygame.K_4: motor.modo_actual = M_BORRAR
                if evento.key == pygame.K_5: motor.modo_actual = M_A
                if evento.key == pygame.K_6: motor.modo_actual = M_B
                if evento.key == pygame.K_g: motor.mostrar_cuadricula = not motor.mostrar_cuadricula
                if evento.key == pygame.K_c:
                    motor.camara_x, motor.camara_y, motor.tamano_celda = motor.auto_centrar_mapa()

        if evento.type == pygame.MOUSEWHEEL and en_lienzo:
            motor.tamano_celda = max(20, min(200, motor.tamano_celda + evento.y * 3))

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if rect_escala.collidepoint(mx, my):
                motor.editando_escala = True
            else:
                motor.editando_escala = False

            if btn_centrar.collidepoint(mx, my):
                motor.camara_x, motor.camara_y, motor.tamano_celda = motor.auto_centrar_mapa()

            # Hace que el botón de iniciar ruta funcione
            if btn_iniciar.collidepoint(mx, my):
                ia.reiniciar_memoria()
                motor.camino_actual = ia.calcular_camino_directo(motor.pos_A, motor.pos_B)

                # Activa el movimiento del robot
                if motor.camino_actual:
                    robot_en_movimiento = True 
                    ultimo_movimiento_ticket = pygame.time.get_ticks()

            if btn_borrar.collidepoint(mx, my):

                robot_en_movimiento = False

                motor.pos_A = None
                motor.pos_B = None
            
                motor.camino_actual = []
                motor.mapa_celdas.clear()

            if my < UI_SUPERIOR:
                for i, h in enumerate(herramientas):
                    btn_rect = pygame.Rect(300 + i * 135, 22, 125, 30)
                    if btn_rect.collidepoint(mx, my):
                        motor.modo_actual = h["id"]
            
            # Colocar Robot o Meta al hacer clic en el lienzo
            if en_lienzo and not motor.editando_escala:
                if motor.modo_actual == M_A:
                    motor.mapa_celdas.pop((w_col, w_fila), None)
                    motor.pos_A = (w_col, w_fila)
                elif motor.modo_actual == M_B:
                    motor.mapa_celdas.pop((w_col, w_fila), None)
                    motor.pos_B = (w_col, w_fila)

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 2 and en_lienzo:
            motor.desplazando = True
            motor.inicio_desplazamiento = (mx, my)
            motor.inicio_camara = (motor.camara_x, motor.camara_y)

        if evento.type == pygame.MOUSEBUTTONUP and evento.button == 2:
            motor.desplazando = False

    botones_raton = pygame.mouse.get_pressed()
    if motor.desplazando:
        motor.camara_x = motor.inicio_camara[0] - (mx - motor.inicio_desplazamiento[0])
        motor.camara_y = motor.inicio_camara[1] - (my - motor.inicio_desplazamiento[1])
    elif botones_raton[0] and en_lienzo and not motor.editando_escala:
        if motor.modo_actual in [M_MURO, M_FRIC, M_LENTO]:
            if (w_col, w_fila) not in (motor.pos_A, motor.pos_B):
                motor.mapa_celdas[(w_col, w_fila)] = motor.modo_actual
        elif motor.modo_actual == M_BORRAR:
            motor.mapa_celdas.pop((w_col, w_fila), None)

    # Se comprueban los movimientos segundo a segundo
    if robot_en_movimiento:
        tiempo_actual = pygame.time.get_ticks()
        
        if tiempo_actual - ultimo_movimiento_ticket >= INTERVALO_MOVIMIENTO:
            if motor.camino_actual:
                # Guardamos la posición antes de delegar en la IA
                pos_antigua = motor.pos_A

                # 1. La IA decide si avanza o si se detiene y recalcula por un choque
                motor.pos_A, motor.camino_actual = ia.actualizar_movimiento(
                    motor.pos_A, motor.pos_B, motor.camino_actual, motor.mapa_celdas
                )

                # 2. Si la IA permitió avanzar, calculamos la orientación con la posición antigua
                if motor.pos_A and pos_antigua and motor.pos_A != pos_antigua:
                    dx = motor.pos_A[0] - pos_antigua[0]
                    dy = motor.pos_A[1] - pos_antigua[1]

                    if dx > 0: angulo_robot = 0
                    elif dx < 0: angulo_robot = 180
                    elif dy > 0: angulo_robot = 90
                    elif dy < 0: angulo_robot = 270

                ultimo_movimiento_ticket = tiempo_actual
            
            # 3. COMPROBACIÓN POST-MOVIMIENTO:
            if motor.pos_A == motor.pos_B:
                robot_en_movimiento = False
                motor.pos_B = None
            
            # 4. COMPROBACIÓN POST-MOVIMIENTO:
            # Si el robot ya está físicamente en la misma casilla que la meta,
            # detenemos la simulación y hacemos desaparecer el objetivo.
            if motor.pos_A == motor.pos_B:
                robot_en_movimiento = False
                motor.pos_B = None  

    # --- RENDERING MAPA ---
    pantalla.blit(textura_suelo, (0, 0))

    col_inicio = motor.camara_x // motor.tamano_celda
    fila_inicio = motor.camara_y // motor.tamano_celda
    cols_visibles = ((ANCHO - UI_LATERAL) // motor.tamano_celda) + 2
    filas_visibles = ((ALTO - UI_SUPERIOR - UI_INFERIOR) // motor.tamano_celda) + 2

    celdas_visibles = []
    for c in range(col_inicio, col_inicio + cols_visibles):
        for f in range(fila_inicio, fila_inicio + filas_visibles):
            sx = c * motor.tamano_celda - motor.camara_x
            sy = f * motor.tamano_celda - motor.camara_y + UI_SUPERIOR
            if 0 <= sx < ANCHO - UI_LATERAL and UI_SUPERIOR <= sy < ALTO - UI_INFERIOR:
                celdas_visibles.append((c, f, sx, sy))

    if motor.mostrar_cuadricula:
        for c, f, sx, sy in celdas_visibles:
            pygame.draw.rect(pantalla, C_CUADRICULA, (sx, sy, motor.tamano_celda, motor.tamano_celda), 1)

    # Ejes Cartesianos Auxiliares (0,0)
    orig_x = 0 * motor.tamano_celda - motor.camara_x
    orig_y = 0 * motor.tamano_celda - motor.camara_y + UI_SUPERIOR
    if 0 < orig_x < ANCHO - UI_LATERAL:
        s = pygame.Surface((2, ALTO - UI_SUPERIOR - UI_INFERIOR), pygame.SRCALPHA)
        s.fill((100, 100, 110, 100))
        pantalla.blit(s, (orig_x, UI_SUPERIOR))
    if UI_SUPERIOR < orig_y < ALTO - UI_INFERIOR:
        s = pygame.Surface((ANCHO - UI_LATERAL, 2), pygame.SRCALPHA)
        s.fill((100, 100, 110, 100))
        pantalla.blit(s, (0, orig_y))

    # Dibujar Terrenos
    for c, f, sx, sy in celdas_visibles:
        rect = (sx, sy, motor.tamano_celda, motor.tamano_celda)
        tipo = motor.mapa_celdas.get((c, f), -1)
        if tipo == M_FRIC:
            graficos.dibujar_zona_baja_friccion(pantalla, rect, c, f)
        elif tipo == M_LENTO:
            graficos.dibujar_zona_rugosa(pantalla, rect, c, f)

    # Dibujar Muros
    for c, f, sx, sy in celdas_visibles:
        if motor.mapa_celdas.get((c, f), -1) == M_MURO:
            graficos.dibujar_muro_realista(pantalla, (sx, sy, motor.tamano_celda, motor.tamano_celda))

    # Dibujar Entidades (Robot y Meta)
    # (Cambio esta parte a ver como sale)
    if motor.camino_actual:
        for cx, cy in motor.camino_actual:
            # Calculamos dónde cae la celda en la pantalla en píxeles (con cámara y zoom)
            sx = cx * motor.tamano_celda - motor.camara_x
            sy = cy * motor.tamano_celda - motor.camara_y + UI_SUPERIOR
            
            # Solo lo dibujamos si cae dentro del lienzo visible de la pantalla
            if 0 <= sx < ANCHO - UI_LATERAL and UI_SUPERIOR <= sy < ALTO - UI_INFERIOR:
                # Dibujamos un cuadrado azul eléctrico un poco más pequeño que la celda como rastro
                rect_camino = (sx + 4, sy + 4, motor.tamano_celda - 8, motor.tamano_celda - 8)
                pygame.draw.rect(pantalla, (0, 150, 255), rect_camino, border_radius=4)
            

    if motor.pos_A:
        ax = motor.pos_A[0] * motor.tamano_celda - motor.camara_x + motor.tamano_celda // 2
        ay = motor.pos_A[1] * motor.tamano_celda - motor.camara_y + UI_SUPERIOR + motor.tamano_celda // 2
        if UI_SUPERIOR - motor.tamano_celda < ay < ALTO - UI_INFERIOR + motor.tamano_celda and ax < ANCHO - UI_LATERAL + motor.tamano_celda:
            graficos.dibujar_robot_realista(pantalla, (ax, ay), motor.tamano_celda, angulo_robot)

    if motor.pos_B:
        bx = motor.pos_B[0] * motor.tamano_celda - motor.camara_x + motor.tamano_celda // 2
        by = motor.pos_B[1] * motor.tamano_celda - motor.camara_y + UI_SUPERIOR + motor.tamano_celda // 2
        if UI_SUPERIOR - motor.tamano_celda < by < ALTO - UI_INFERIOR + motor.tamano_celda and bx < ANCHO - UI_LATERAL + motor.tamano_celda:
            graficos.dibujar_meta_realista(pantalla, (bx, by), motor.tamano_celda)

    # --- RENDERING INTERFAZ DE USUARIO ---
    graficos.dibujar_panel_industrial(pantalla, (0, 0, ANCHO, UI_SUPERIOR), es_superior=True)
    pantalla.blit(fuente_titulo.render(TITULO_APP, True, C_TXT), (20, 14))
    pantalla.blit(fuente_subtitulo.render("ENTORNO DE INGENIERÍA v4.2", True, (160, 170, 180)), (20, 42))

    # Botones superiores
    for i, h in enumerate(herramientas):
        btn_rect = pygame.Rect(300 + i * 135, 22, 125, 30)
        es_activo = (h["id"] == motor.modo_actual)
        esta_encima = btn_rect.collidepoint(mx, my) and my < UI_SUPERIOR
        bg_col = C_PANEL_CLARO if es_activo else (C_PANEL_FONDO if not esta_encima else C_BORDE)
        pygame.draw.rect(pantalla, bg_col, btn_rect, border_radius=5)
        pygame.draw.rect(pantalla, h["color"] if es_activo else C_BORDE, btn_rect, 2 if es_activo else 1,
                         border_radius=5)
        txt_s = fuente_ui.render(h["txt"], True, C_TXT if (es_activo or esta_encima) else C_TXT_ATENUADO)
        pantalla.blit(txt_s, txt_s.get_rect(center=btn_rect.center))

    # Panel lateral derecho
    panel_x = ANCHO - UI_LATERAL
    graficos.dibujar_panel_industrial(pantalla, (panel_x, UI_SUPERIOR, UI_LATERAL, ALTO - UI_SUPERIOR),
                                      es_superior=False)
    pantalla.blit(fuente_titulo.render("DATOS GENERALES", True, C_TXT), (panel_x + 20, UI_SUPERIOR + 20))
    pygame.draw.line(pantalla, C_BORDE, (panel_x + 20, UI_SUPERIOR + 50), (ANCHO - 20, UI_SUPERIOR + 50), 1)

    # Estadísticas
    num_muros = sum(1 for v in motor.mapa_celdas.values() if v == M_MURO)
    num_fric = sum(1 for v in motor.mapa_celdas.values() if v == M_FRIC)
    num_lento = sum(1 for v in motor.mapa_celdas.values() if v == M_LENTO)

    estadisticas = [
        ("Zoom Visual:", f"{motor.tamano_celda} px/celda", C_TXT),
        ("Entidades de Muro:", f"{num_muros} u", C_BASE_MURO),
        ("Fricción Baja (\u03bc\u2193):", f"{num_fric} u", C_BASE_FRIC_BAJA),
        ("Fricción Alta (\u03bc\u2191):", f"{num_lento} u", C_BASE_LENTO),
    ]
    for idx, (etiqueta, val, col) in enumerate(estadisticas):
        y_pos = UI_SUPERIOR + 75 + idx * 30
        pygame.draw.rect(pantalla, col, (panel_x + 20, y_pos + 3, 10, 10), border_radius=2)
        pantalla.blit(fuente_ui.render(etiqueta, True, C_TXT_ATENUADO), (panel_x + 38, y_pos))
        val_surf = fuente_mono.render(val, True, C_ACENTO)
        val_rect = val_surf.get_rect(topright=(ANCHO - 20, y_pos))
        pantalla.blit(val_surf, val_rect)

    # Coordenadas cinemáticas
    y_cinematica = UI_SUPERIOR + 215
    pygame.draw.line(pantalla, C_BORDE, (panel_x + 20, y_cinematica), (ANCHO - 20, y_cinematica), 1)
    pantalla.blit(fuente_subtitulo.render("COORDENADAS DEL SISTEMA (CARTESIANO)", True, C_ACENTO),
                  (panel_x + 20, y_cinematica + 15))

    str_A = f"X:{motor.pos_A[0] * motor.metros_por_celda:.2f} Y:{-motor.pos_A[1] * motor.metros_por_celda:.2f}" if motor.pos_A else "PENDIENTE"
    str_B = f"X:{motor.pos_B[0] * motor.metros_por_celda:.2f} Y:{-motor.pos_B[1] * motor.metros_por_celda:.2f}" if motor.pos_B else "PENDIENTE"

    pantalla.blit(fuente_ui.render("Origen del Robot (A):", True, C_TXT_ATENUADO), (panel_x + 20, y_cinematica + 40))
    pantalla.blit(fuente_mono_lg.render(str_A, True, C_BASE_INICIO if motor.pos_A else (150, 80, 80)),
                  (panel_x + 20, y_cinematica + 60))

    pantalla.blit(fuente_ui.render("Objetivo / Meta (B):", True, C_TXT_ATENUADO), (panel_x + 20, y_cinematica + 95))
    pantalla.blit(fuente_mono_lg.render(str_B, True, C_BASE_FIN if motor.pos_B else (150, 80, 80)),
                  (panel_x + 20, y_cinematica + 115))

    pantalla.blit(fuente_ui.render("Distancia Vectorial Lineal A\u2794B:", True, C_TXT_ATENUADO),
                  (panel_x + 20, y_cinematica + 155))
    if motor.pos_A and motor.pos_B:
        dist_euclidea = math.sqrt(
            (motor.pos_B[0] - motor.pos_A[0]) ** 2 + (motor.pos_B[1] - motor.pos_A[1]) ** 2) * motor.metros_por_celda
        txt_dist = f"{dist_euclidea:.2f} m"
        col_dist = C_TXT
    else:
        txt_dist, col_dist = "PENDIENTE", (150, 80, 80)
    pantalla.blit(fuente_mono_lg.render(txt_dist, True, col_dist), (panel_x + 20, y_cinematica + 175))

    # Regulación de Escala
    y_metrologia = y_cinematica + 215
    pygame.draw.line(pantalla, C_BORDE, (panel_x + 20, y_metrologia), (ANCHO - 20, y_metrologia), 1)
    pantalla.blit(fuente_titulo.render("REGULACIÓN DE ESCALA", True, C_TXT), (panel_x + 20, y_metrologia + 15))
    pantalla.blit(fuente_ui.render("Escala Real del Entorno:", True, C_TXT_ATENUADO), (panel_x + 20, y_metrologia + 45))

    color_caja = C_ACENTO if motor.editando_escala else C_VACIO
    pygame.draw.rect(pantalla, color_caja, rect_escala, border_radius=4)
    pygame.draw.rect(pantalla, C_BORDE, rect_escala, 1, border_radius=4)
    pantalla.blit(
        fuente_mono.render(motor.escala_texto + ("_" if motor.editando_escala else "") + " m / celda", True, C_TXT),
        (rect_escala.x + 15, rect_escala.y + 7))

    # Botón centrar
    hvr_centrar = btn_centrar.collidepoint(mx, my) and panel_x < mx
    pygame.draw.rect(pantalla, (60, 50, 100) if not hvr_centrar else (80, 70, 130), btn_centrar, border_radius=6)
    pygame.draw.rect(pantalla, C_CENTRO, btn_centrar, 1 if not hvr_centrar else 2, border_radius=6)
    txt_c_btn = fuente_ui.render("CENTRAR MAPA [C]", True, C_TXT)
    pantalla.blit(txt_c_btn, txt_c_btn.get_rect(center=btn_centrar.center))

    # Botón iniciar ruta
    hvr_iniciar = btn_iniciar.collidepoint(mx, my) and panel_x < mx
    color_btn_iniciar = (40, 140, 80) if not hvr_iniciar else (50, 180, 100)
    pygame.draw.rect(pantalla, color_btn_iniciar, btn_iniciar, border_radius=6)
    pygame.draw.rect(pantalla, C_BASE_INICIO, btn_iniciar, 1 if not hvr_iniciar else 2, border_radius=6)
    txt_i_btn = fuente_ui.render("INICIAR RUTA", True, C_TXT)
    pantalla.blit(txt_i_btn, txt_i_btn.get_rect(center=btn_iniciar.center))

    # Botón borrar todo
    hvr_borrar = btn_borrar.collidepoint(mx, my) and panel_x < mx
    color_btn_borrar = (180, 40, 40) if not hvr_borrar else (220, 50, 50)
    pygame.draw.rect(pantalla, color_btn_borrar, btn_borrar, border_radius=6)
    pygame.draw.rect(pantalla, (220, 120, 120), btn_borrar, 1 if not hvr_borrar else 2, border_radius=6)
    txt_b_btn = fuente_ui.render("BORRAR TODO", True, C_TXT)
    pantalla.blit(txt_b_btn, txt_b_btn.get_rect(center=btn_borrar.center))
    
    # Barra inferior
    pygame.draw.rect(pantalla, C_PANEL_FONDO, (0, ALTO - UI_INFERIOR, ANCHO, UI_INFERIOR))
    pygame.draw.rect(pantalla, C_BORDE, (0, ALTO - UI_INFERIOR, ANCHO, 1))

    txt_coord = fuente_mono.render(f"ABS X:{real_x_m:.2f} m \u2502 ABS Y:{real_y_m:.2f} m", True,
                                   C_ACENTO) if en_lienzo else fuente_mono.render(
        "SISTEMA NOMINAL \u2502 CURSOR FUERA DE LÍMITES", True, C_TXT_ATENUADO)
    pantalla.blit(txt_coord, (20, ALTO - 24))
    pantalla.blit(fuente_subtitulo.render("FUNDACIÓN PROBOT\u00a9 - 2026", True, C_TXT_ATENUADO),
                  (ANCHO - UI_LATERAL - 200, ALTO - 24))

    pygame.display.flip()
    reloj.tick(60)