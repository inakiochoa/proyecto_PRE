# Main.py
import pygame
import sys
import math
from constantes import *
import motor
import graficos
import ia

pygame.init()

# --- CONFIGURACIÓN DE NOMBRE DE LA APP ---
TITULO_APP = "PathFinder"

# --- CONFIGURACIÓN DE VENTANA ---
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption(f"{TITULO_APP} v7.5 - Alineación de Ejes Absoluta")
reloj = pygame.time.Clock()

# --- FUENTES ---
fuente_titulo = pygame.font.SysFont("Segoe UI", 20, bold=True)
fuente_subtitulo = pygame.font.SysFont("Segoe UI", 11, bold=True)
fuente_ui = pygame.font.SysFont("Segoe UI", 13, bold=True)
fuente_mono = pygame.font.SysFont("Consolas", 13)
fuente_mono_lg = pygame.font.SysFont("Consolas", 18, bold=True)
fuente_menu_tit = pygame.font.SysFont("Segoe UI", 24, bold=True)

# Elementos Interactivos - SIMULACIÓN
rect_escala = pygame.Rect(ANCHO - UI_LATERAL + 20, 480, 260, 30)
btn_centrar = pygame.Rect(ANCHO - UI_LATERAL + 20, 525, 260, 35)
btn_iniciar = pygame.Rect(ANCHO - UI_LATERAL + 20, 570, 260, 35)
btn_borrar = pygame.Rect(ANCHO - UI_LATERAL + 20, 615, 260, 35)
btn_volver = pygame.Rect(ANCHO - UI_LATERAL + 20, 660, 260, 35)
btn_guardar = pygame.Rect(ANCHO - UI_LATERAL + 20, 710, 125, 34)
btn_cargar = pygame.Rect(ANCHO - UI_LATERAL + 155, 710, 125, 34)

# Elementos Interactivos - MENÚ INICIAL
rect_menu_pred = pygame.Rect(ANCHO // 2 - 270, ALTO // 2 - 40, 250, 130)
rect_menu_auto = pygame.Rect(ANCHO // 2 + 20, ALTO // 2 - 40, 250, 130)

herramientas_limpias = [
    {"id": M_MURO, "txt": "1. MURO", "color": C_BASE_MURO},
    {"id": M_BORRAR, "txt": "2. BORRAR", "color": (200, 100, 100)},
    {"id": M_A, "txt": "3. INICIO (A)", "color": C_BASE_INICIO},
    {"id": M_B, "txt": "4. META (B)", "color": C_BASE_FIN}
]

# Animación y Físicas
robot_en_movimiento = False
VELOCIDAD_FRAME = 0.08
angulo_robot = 0

textura_suelo = graficos.generar_textura_ruido(ANCHO, ALTO, factor=8)


def verificar_viabilidad_ruta():
    if motor.pos_A and motor.pos_B:
        ruta_test = ia.calcular_camino_directo(motor.pos_A, motor.pos_B, motor.mapa_celdas, "OMNISCIENTE")
        motor.ruta_imposible = (ruta_test is None or len(ruta_test) == 0)
    else:
        motor.ruta_imposible = False


# --- BUCLE PRINCIPAL ---
while True:
    mx, my = pygame.mouse.get_pos()
    reloj.tick(60)

    if motor.escala_texto.replace('.', '', 1).isdigit() and float(motor.escala_texto) > 0:
        motor.metros_por_celda = float(motor.escala_texto)
    else:
        motor.metros_por_celda = 1.0

    if motor.estado_pantalla == "MENU":
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if rect_menu_pred.collidepoint(mx, my):
                    motor.algoritmo_modo = "OMNISCIENTE"
                    motor.estado_pantalla = "SIMULACION"
                    motor.metros_recorridos = 0.0
                    motor.rastro_fluido = []
                    motor.camino_actual = []
                    verificar_viabilidad_ruta()

                elif rect_menu_auto.collidepoint(mx, my):
                    motor.algoritmo_modo = "REACTIVO"
                    motor.estado_pantalla = "SIMULACION"
                    motor.metros_recorridos = 0.0
                    motor.rastro_fluido = []
                    motor.camino_actual = []
                    verificar_viabilidad_ruta()

        pantalla.blit(textura_suelo, (0, 0))

        rect_bloque = pygame.Rect(ANCHO // 2 - 320, ALTO // 2 - 160, 640, 320)
        pygame.draw.rect(pantalla, C_PANEL_FONDO, rect_bloque, border_radius=12)
        pygame.draw.rect(pantalla, C_BORDE, rect_bloque, 2, border_radius=12)

        t_menu = fuente_menu_tit.render("ARQUITECTURA DE PROCESAMIENTO", True, C_TXT)
        pantalla.blit(t_menu, t_menu.get_rect(centerx=ANCHO // 2, y=ALTO // 2 - 130))
        sub_menu = fuente_subtitulo.render("SELECCIONE EL MODO OPERATIVO DE LA INTELIGENCIA", True, C_TXT_ATENUADO)
        pantalla.blit(sub_menu, sub_menu.get_rect(centerx=ANCHO // 2, y=ALTO // 2 - 90))

        hvr_pred = rect_menu_pred.collidepoint(mx, my)
        pygame.draw.rect(pantalla, (45, 55, 75) if hvr_pred else C_PANEL_CLARO, rect_menu_pred, border_radius=8)
        pygame.draw.rect(pantalla, C_ACENTO if hvr_pred else C_BORDE, rect_menu_pred, 2 if hvr_pred else 1,
                         border_radius=8)
        lbl1 = fuente_titulo.render("MODO PREDEFINIDO", True, C_TXT)
        sub_lbl1 = fuente_subtitulo.render("Mapeo global (Omnisciente)", True, C_TXT_ATENUADO)
        pantalla.blit(lbl1, lbl1.get_rect(centerx=rect_menu_pred.centerx, y=rect_menu_pred.y + 35))
        pantalla.blit(sub_lbl1, sub_lbl1.get_rect(centerx=rect_menu_pred.centerx, y=rect_menu_pred.y + 70))

        hvr_auto = rect_menu_auto.collidepoint(mx, my)
        pygame.draw.rect(pantalla, (45, 55, 75) if hvr_auto else C_PANEL_CLARO, rect_menu_auto, border_radius=8)
        pygame.draw.rect(pantalla, C_ACENTO if hvr_auto else C_BORDE, rect_menu_auto, 2 if hvr_auto else 1,
                         border_radius=8)
        lbl2 = fuente_titulo.render("MODO AUTÓNOMO", True, C_TXT)
        sub_lbl2 = fuente_subtitulo.render("Descubrimiento en ruta (Reactivo)", True, C_TXT_ATENUADO)
        pantalla.blit(lbl2, lbl2.get_rect(centerx=rect_menu_auto.centerx, y=rect_menu_auto.y + 35))
        pantalla.blit(sub_lbl2, sub_lbl2.get_rect(centerx=rect_menu_auto.centerx, y=rect_menu_auto.y + 70))

        pygame.draw.rect(pantalla, C_PANEL_FONDO, (0, ALTO - UI_INFERIOR, ANCHO, UI_INFERIOR))
        pygame.draw.rect(pantalla, C_BORDE, (0, ALTO - UI_INFERIOR, ANCHO, 1))
        pantalla.blit(fuente_subtitulo.render("FUNDACIÓN PROBOT© - 2026", True, C_TXT_ATENUADO),
                      (ANCHO - 220, ALTO - 24))

    elif motor.estado_pantalla == "SIMULACION":
        en_lienzo = (mx < ANCHO - UI_LATERAL) and (UI_SUPERIOR < my < ALTO - UI_INFERIOR)

        real_x_m = ((mx + motor.camara_x) / motor.tamano_celda) * motor.metros_por_celda
        real_y_m = -((my - UI_SUPERIOR + motor.camara_y) / motor.tamano_celda) * motor.metros_por_celda

        # Mapeo de cuadrícula estricto
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
                    if evento.key == pygame.K_2: motor.modo_actual = M_BORRAR
                    if evento.key == pygame.K_3: motor.modo_actual = M_A
                    if evento.key == pygame.K_4: motor.modo_actual = M_B
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

                if btn_volver.collidepoint(mx, my):
                    robot_en_movimiento = False
                    motor.estado_pantalla = "MENU"
                    motor.modo_actual = None  # Resetea la herramienta al volver al menú

                if btn_iniciar.collidepoint(mx, my) and not motor.ruta_imposible:
                    ia.reiniciar_memoria()
                    motor.metros_recorridos = 0.0
                    motor.rastro_fluido = []

                    if motor.pos_A and motor.pos_B:
                        motor.camino_actual = ia.calcular_camino_directo(motor.pos_A, motor.pos_B, motor.mapa_celdas, motor.algoritmo_modo)
                        robot_en_movimiento = True

                if btn_guardar.collidepoint(mx, my):
                    motor.guardar_mapa_disco()

                if btn_cargar.collidepoint(mx, my):
                    motor.cargar_mapa_disco()
                    robot_en_movimiento = False # Mantenemos el robot quieto al cargar
                    motor.rastro_fluido = []

                    if motor.pos_A:
                        motor.robot_visual_x = float(motor.pos_A[1])  # columna (X)
                        motor.robot_visual_y = float(motor.pos_A[0])  # fila (Y)
                        motor.rastro_fluido.append((motor.robot_visual_x, motor.robot_visual_y))

                if btn_borrar.collidepoint(mx, my):
                    robot_en_movimiento = False
                    motor.pos_A, motor.pos_B = None, None
                    motor.camino_actual, motor.rastro_fluido = [], []
                    motor.metros_recorridos = 0.0
                    motor.robot_visual_x, motor.robot_visual_y = None, None
                    motor.mapa_celdas.clear()
                    motor.ruta_imposible = False
                    ia.reiniciar_memoria()

                if my < UI_SUPERIOR:
                    for i, h in enumerate(herramientas_limpias):
                        btn_rect = pygame.Rect(300 + i * 135, 22, 125, 30)
                        if btn_rect.collidepoint(mx, my):
                            motor.modo_actual = h["id"]
                            if h["id"] == M_A:
                                motor.rastro_fluido = []

                if en_lienzo and not motor.editando_escala:
                    if motor.modo_actual == M_A:
                        motor.mapa_celdas.pop((w_fila, w_col), None)
                        motor.pos_A = (w_fila, w_col)
                        motor.robot_visual_x, motor.robot_visual_y = float(w_col), float(w_fila)
                        verificar_viabilidad_ruta()
                    elif motor.modo_actual == M_B:
                        motor.mapa_celdas.pop((w_fila, w_col), None)
                        motor.pos_B = (w_fila, w_col)
                        verificar_viabilidad_ruta()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 2 and en_lienzo:
                motor.desplazando = True
                motor.inicio_desplazamiento = (mx, my)
                motor.inicio_camara = (motor.camara_x, motor.camara_y)

            if evento.type == pygame.MOUSEBUTTONUP and evento.button == 2: motor.desplazando = False

        botones_raton = pygame.mouse.get_pressed()
        if motor.desplazando:
            motor.camara_x = motor.inicio_camara[0] - (mx - motor.inicio_desplazamiento[0])
            motor.camara_y = motor.inicio_camara[1] - (my - motor.inicio_desplazamiento[1])
        elif botones_raton[0] and en_lienzo and not motor.editando_escala:
            mapa_modificado = False
            if motor.modo_actual == M_MURO:
                if (w_fila, w_col) != motor.pos_A and (w_fila, w_col) != motor.pos_B:
                    if motor.mapa_celdas.get((w_fila, w_col)) != motor.modo_actual:
                        motor.mapa_celdas[(w_fila, w_col)] = motor.modo_actual
                        mapa_modificado = True
            elif motor.modo_actual == M_BORRAR:
                if (w_fila, w_col) in motor.mapa_celdas:
                    motor.mapa_celdas.pop((w_fila, w_col), None)
                    mapa_modificado = True

            if mapa_modificado:
                verificar_viabilidad_ruta()
                if robot_en_movimiento and motor.algoritmo_modo == "OMNISCIENTE":
                    motor.camino_actual = ia.calcular_camino_directo(motor.pos_A, motor.pos_B, motor.mapa_celdas,
                                                                     motor.algoritmo_modo)
                    if not motor.camino_actual: robot_en_movimiento = False

        # --- MOTOR CINEMÁTICO ---
        if robot_en_movimiento and motor.camino_actual:
            obj_fila, obj_col = motor.camino_actual[0]
            objetivo_x, objetivo_y = float(obj_col), float(obj_fila)

            dx = objetivo_x - motor.robot_visual_x
            dy = objetivo_y - motor.robot_visual_y
            distancia = math.hypot(dx, dy)

            if distancia > VELOCIDAD_FRAME:
                motor.robot_visual_x += (dx / distancia) * VELOCIDAD_FRAME
                motor.robot_visual_y += (dy / distancia) * VELOCIDAD_FRAME
                angulo_robot = math.degrees(math.atan2(dy, dx))

                motor.metros_recorridos += VELOCIDAD_FRAME * motor.metros_por_celda

                ultimo_rastro = motor.rastro_fluido[-1] if motor.rastro_fluido else (
                    motor.robot_visual_x, motor.robot_visual_y)
                if math.hypot(motor.robot_visual_x - ultimo_rastro[0], motor.robot_visual_y - ultimo_rastro[1]) >= 0.1:
                    motor.rastro_fluido.append((motor.robot_visual_x, motor.robot_visual_y))
            else:
                motor.robot_visual_x = objetivo_x
                motor.robot_visual_y = objetivo_y

                motor.metros_recorridos += distancia * motor.metros_por_celda

                motor.pos_A = (int(obj_fila), int(obj_col))
                motor.rastro_fluido.append((motor.robot_visual_x, motor.robot_visual_y))

                motor.pos_A, motor.camino_actual = ia.actualizar_movimiento(
                    motor.pos_A, motor.pos_B, motor.camino_actual, motor.mapa_celdas, motor.algoritmo_modo
                )

                if not motor.camino_actual and motor.pos_A != motor.pos_B:
                    robot_en_movimiento = False
                    verificar_viabilidad_ruta()
                elif motor.pos_A == motor.pos_B:
                    robot_en_movimiento = False

        # --- RENDERING ---
        pantalla.blit(textura_suelo, (0, 0))

        col_inicio, fila_inicio = motor.camara_x // motor.tamano_celda, motor.camara_y // motor.tamano_celda
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

        for c, f, sx, sy in celdas_visibles:
            if motor.mapa_celdas.get((f, c), -1) == M_MURO:
                graficos.dibujar_muro_realista(pantalla, (sx, sy, motor.tamano_celda, motor.tamano_celda))


        def logico_a_pantalla(col_l, fila_l):
            return (
                int(col_l * motor.tamano_celda - motor.camara_x + motor.tamano_celda / 2),
                int(fila_l * motor.tamano_celda - motor.camara_y + UI_SUPERIOR + motor.tamano_celda / 2)
            )


        if motor.camino_actual:
            puntos_pantalla_futuros = [logico_a_pantalla(motor.robot_visual_x, motor.robot_visual_y)]
            for f, c in motor.camino_actual:
                puntos_pantalla_futuros.append(logico_a_pantalla(c, f))
            if len(puntos_pantalla_futuros) > 1:
                pygame.draw.lines(pantalla, (40, 90, 150), False, puntos_pantalla_futuros,
                                  max(2, motor.tamano_celda // 8))

        if len(motor.rastro_fluido) > 1:
            puntos_pantalla_pasado = [logico_a_pantalla(px, py) for px, py in motor.rastro_fluido]
            pygame.draw.lines(pantalla, (0, 180, 255), False, puntos_pantalla_pasado, max(4, motor.tamano_celda // 5))

        if motor.pos_A is not None and motor.robot_visual_x is not None:
            rx = int(motor.robot_visual_x * motor.tamano_celda - motor.camara_x)
            ry = int(motor.robot_visual_y * motor.tamano_celda - motor.camara_y + UI_SUPERIOR)

            centro_robot_x = rx + motor.tamano_celda // 2
            centro_robot_y = ry + motor.tamano_celda // 2

            if UI_SUPERIOR - motor.tamano_celda < ry < ALTO - UI_INFERIOR + motor.tamano_celda and rx < ANCHO - UI_LATERAL + motor.tamano_celda:
                graficos.dibujar_robot_realista(pantalla, (centro_robot_x, centro_robot_y), motor.tamano_celda,
                                                angulo_robot)

        if motor.pos_B:
            bx = int(motor.pos_B[1] * motor.tamano_celda - motor.camara_x)
            by = int(motor.pos_B[0] * motor.tamano_celda - motor.camara_y + UI_SUPERIOR)

            centro_meta_x = bx + motor.tamano_celda // 2
            centro_meta_y = by + motor.tamano_celda // 2

            if UI_SUPERIOR - motor.tamano_celda < by < ALTO - UI_INFERIOR + motor.tamano_celda and bx < ANCHO - UI_LATERAL + motor.tamano_celda:
                graficos.dibujar_meta_realista(pantalla, (centro_meta_x, centro_meta_y), motor.tamano_celda)

        # --- COMPONENTES DE INTERFAZ ---
        if motor.ruta_imposible and motor.pos_B:
            w_alerta, h_alerta = 450, 44
            rect_alerta = pygame.Rect((ANCHO - UI_LATERAL) // 2 - w_alerta // 2, UI_SUPERIOR + 15, w_alerta, h_alerta)
            pygame.draw.rect(pantalla, (40, 10, 10), rect_alerta, border_radius=8)
            pygame.draw.rect(pantalla, (255, 60, 60), rect_alerta, 2, border_radius=8)
            t_alerta = fuente_ui.render("⚠️ ALERTA: RUTA IMPOSIBLE - META BLOQUEADA", True, (255, 100, 100))
            pantalla.blit(t_alerta, t_alerta.get_rect(center=rect_alerta.center))

        graficos.dibujar_panel_industrial(pantalla, (0, 0, ANCHO, UI_SUPERIOR), es_superior=True)
        pantalla.blit(fuente_titulo.render(TITULO_APP, True, C_TXT), (20, 14))
        modo_txt = "PREDEFINIDO (OMNISCIENTE)" if motor.algoritmo_modo == "OMNISCIENTE" else "AUTÓNOMO (REACTIVO)"
        pantalla.blit(fuente_subtitulo.render(f"ARQUITECTURA ACTIVA: {modo_txt}", True, C_ACENTO), (20, 42))

        for i, h in enumerate(herramientas_limpias):
            btn_rect = pygame.Rect(300 + i * 135, 22, 125, 30)
            es_activo = (h["id"] == motor.modo_actual)
            bg_col = C_PANEL_CLARO if es_activo else (
                C_PANEL_FONDO if not btn_rect.collidepoint(mx, my) or my >= UI_SUPERIOR else C_BORDE)
            pygame.draw.rect(pantalla, bg_col, btn_rect, border_radius=5)
            pygame.draw.rect(pantalla, h["color"] if es_activo else C_BORDE, btn_rect, 2 if es_activo else 1,
                             border_radius=5)
            txt_s = fuente_ui.render(h["txt"], True, C_TXT if (
                    es_activo or (btn_rect.collidepoint(mx, my) and my < UI_SUPERIOR)) else C_TXT_ATENUADO)
            pantalla.blit(txt_s, txt_s.get_rect(center=btn_rect.center))

        panel_x = ANCHO - UI_LATERAL
        graficos.dibujar_panel_industrial(pantalla, (panel_x, UI_SUPERIOR, UI_LATERAL, ALTO - UI_SUPERIOR),
                                          es_superior=False)
        pantalla.blit(fuente_titulo.render("DATOS GENERALES", True, C_TXT), (panel_x + 20, UI_SUPERIOR + 20))
        pygame.draw.line(pantalla, C_BORDE, (panel_x + 20, UI_SUPERIOR + 50), (ANCHO - 20, UI_SUPERIOR + 50), 1)

        num_muros = sum(1 for v in motor.mapa_celdas.values() if v == M_MURO)
        estadisticas = [
            ("Zoom Visual:", f"{motor.tamano_celda} px/celda", C_TXT),
            ("Muros del Escenario:", f"{num_muros} bloques", C_BASE_MURO),
        ]
        for idx, (etiqueta, val, col) in enumerate(estadisticas):
            y_pos = UI_SUPERIOR + 65 + idx * 25
            pygame.draw.rect(pantalla, col, (panel_x + 20, y_pos + 3, 10, 10), border_radius=2)
            pantalla.blit(fuente_ui.render(etiqueta, True, C_TXT_ATENUADO), (panel_x + 38, y_pos))
            val_surf = fuente_mono.render(val, True, C_ACENTO)
            pantalla.blit(val_surf, val_surf.get_rect(topright=(ANCHO - 20, y_pos)))

        y_telemetria = UI_SUPERIOR + 125
        pygame.draw.line(pantalla, C_BORDE, (panel_x + 20, y_telemetria), (ANCHO - 20, y_telemetria), 1)
        pantalla.blit(fuente_subtitulo.render("TELEMETRÍA Y CONTROL DE ODÓMETRO", True, C_ACENTO),
                      (panel_x + 20, y_telemetria + 10))

        ha_llegado = (motor.pos_A == motor.pos_B and motor.pos_B is not None)
        rect_odo = pygame.Rect(panel_x + 20, y_telemetria + 30, 260, 45)

        if ha_llegado:
            col_bg, col_brd, col_val = (20, 45, 30), (50, 180, 100), (100, 255, 150)
        elif motor.ruta_imposible:
            col_bg, col_brd, col_val = (40, 15, 15), (180, 50, 50), (255, 100, 100)
        else:
            col_bg, col_brd, col_val = C_PANEL_CLARO, C_BORDE, C_TXT

        pygame.draw.rect(pantalla, col_bg, rect_odo, border_radius=6)
        pygame.draw.rect(pantalla, col_brd, rect_odo, 1, border_radius=6)

        lbl_odo = fuente_ui.render("DISTANCIA TOTAL RECORRIDA:", True,
                                   C_TXT if (ha_llegado or motor.ruta_imposible) else C_TXT_ATENUADO)
        val_odo = fuente_mono_lg.render(f"{motor.metros_recorridos:.2f} m", True, col_val)
        pantalla.blit(lbl_odo, (rect_odo.x + 10, rect_odo.y + 5))
        pantalla.blit(val_odo, val_odo.get_rect(right=rect_odo.right - 10, y=rect_odo.y + 20))

        y_cinematica = y_telemetria + 85
        pygame.draw.line(pantalla, C_BORDE, (panel_x + 20, y_cinematica), (ANCHO - 20, y_cinematica), 1)

        str_A = f"X:{motor.robot_visual_x * motor.metros_por_celda:.2f} Y:{-motor.robot_visual_y * motor.metros_por_celda:.2f}" if motor.pos_A else "PENDIENTE"
        str_B = f"X:{motor.pos_B[1] * motor.metros_por_celda:.2f} Y:{-motor.pos_B[0] * motor.metros_por_celda:.2f}" if motor.pos_B else "PENDIENTE"

        pantalla.blit(fuente_ui.render("Cinemática Robot (A):", True, C_TXT_ATENUADO),
                      (panel_x + 20, y_cinematica + 10))
        pantalla.blit(fuente_mono_lg.render(str_A, True, C_BASE_INICIO if motor.pos_A else (150, 80, 80)),
                      (panel_x + 20, y_cinematica + 26))
        pantalla.blit(fuente_ui.render("Meta Objetivo (B):", True, C_TXT_ATENUADO), (panel_x + 20, y_cinematica + 55))
        pantalla.blit(fuente_mono_lg.render(str_B, True, C_BASE_FIN if motor.pos_B else (150, 80, 80)),
                      (panel_x + 20, y_cinematica + 71))

        y_metrologia = y_cinematica + 110
        pygame.draw.line(pantalla, C_BORDE, (panel_x + 20, y_metrologia), (ANCHO - 20, y_metrologia), 1)
        pygame.draw.rect(pantalla, C_ACENTO if motor.editando_escala else C_VACIO, rect_escala, border_radius=4)
        pygame.draw.rect(pantalla, C_BORDE, rect_escala, 1, border_radius=4)
        pantalla.blit(
            fuente_mono.render(motor.escala_texto + ("_" if motor.editando_escala else "") + " m / celda", True, C_TXT),
            (rect_escala.x + 15, rect_escala.y + 7))

        botones_ui = [
            (btn_centrar, "AUTO CENTRAR CAMARA", (50, 60, 75), (70, 85, 105), C_ACENTO),
            (btn_iniciar, "INICIAR SIMULACIÓN" if not motor.camino_actual else "DETENER RUTA", (40, 150, 90), (50, 180, 110), (100, 220, 150)),
            (btn_borrar, "REINICIAR ESCENARIO", (150, 50, 65), (190, 65, 80), (250, 120, 130)),
            (btn_volver, "VOLVER AL MENÚ", (50, 60, 75), (70, 85, 105), C_ACENTO),
            (btn_guardar, "GUARDAR", (40, 120, 80), (50, 150, 100), (90, 200, 140)),
            (btn_cargar, "CARGAR", (40, 90, 140), (50, 115, 170), (100, 170, 240))
        ]

        for btn, txt, col_std, col_hvr, col_brd in botones_ui:
            hvr = btn.collidepoint(mx, my) and panel_x < mx
            if btn == btn_iniciar and motor.ruta_imposible: col_std, col_hvr, col_brd = (40, 40, 40), (40, 40, 40), (
                80, 80, 80)

            pygame.draw.rect(pantalla, col_hvr if hvr else col_std, btn, border_radius=6)
            pygame.draw.rect(pantalla, col_brd, btn, 2 if hvr else 1, border_radius=6)
            txt_f = fuente_ui.render(txt, True,
                                     C_TXT if not (btn == btn_iniciar and motor.ruta_imposible) else C_TXT_ATENUADO)
            pantalla.blit(txt_f, txt_f.get_rect(center=btn.center))

        pygame.draw.rect(pantalla, C_PANEL_FONDO, (0, ALTO - UI_INFERIOR, ANCHO, UI_INFERIOR))
        pygame.draw.rect(pantalla, C_BORDE, (0, ALTO - UI_INFERIOR, ANCHO, 1))
        txt_coord = fuente_mono.render(f"ABS X:{real_x_m:.2f} m │ ABS Y:{real_y_m:.2f} m", True,
                                       C_ACENTO) if en_lienzo else fuente_mono.render(
            "SISTEMA NOMINAL │ CURSOR FUERA DE LÍMITES", True, C_TXT_ATENUADO)
        pantalla.blit(txt_coord, (20, ALTO - 24))
        pantalla.blit(fuente_subtitulo.render("FUNDACIÓN PROBOT© - 2026", True, C_TXT_ATENUADO),
                      (ANCHO - UI_LATERAL - 200, ALTO - 24))

    pygame.display.flip()