# motor.py
from constantes import *

# --- ESTADO DEL SIMULADOR ---
camara_x, camara_y = -50, -680
tamano_celda = 55
mostrar_cuadricula = True
escala_texto = "0.5"  # En metros, 0.5m = 50cm
metros_por_celda = 0.5
editando_escala = False

mapa_celdas = {}
pos_A, pos_B = None, None
modo_actual = 1

desplazando = False
inicio_desplazamiento, inicio_camara = (0, 0), (0, 0)

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