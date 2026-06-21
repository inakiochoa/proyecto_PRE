# motor.py
from constantes import *

# --- ESTADOS DE LA APLICACIÓN ---
estado_pantalla = "MENU"
algoritmo_modo = "OMNISCIENTE"

# --- MAPA Y ENTIDADES ---
mapa_celdas = {}
pos_A = None
pos_B = None

# --- CINEMÁTICA Y RUTAS ---
camino_actual = []
rastro_fluido = []
robot_visual_x = None
robot_visual_y = None
metros_recorridos = 0.0
ruta_imposible = False

# --- METROLOGÍA Y ESCALA ---
escala_texto = "1.0"
metros_por_celda = 1.0
editando_escala = False

# --- CÁMARA Y NAVEGACIÓN ---
camara_x = 0
camara_y = 0
tamano_celda = 40
mostrar_cuadricula = True
modo_actual = M_MURO

# --- CONTROLES DE DESPLAZAMIENTO (PAN) ---
desplazando = False
inicio_desplazamiento = (0, 0)
inicio_camara = (0, 0)


def auto_centrar_mapa():
    """
    Calcula la posición de la cámara y el zoom ideal para centrar
    el contenido dibujado (muros, inicio, meta) en la pantalla.
    Retorna la tupla: (camara_x, camara_y, tamano_celda)
    """
    if not mapa_celdas and not pos_A and not pos_B:
        # Valores por defecto si el lienzo está completamente vacío
        return 0, 0, 40

    min_f, max_f = float('inf'), float('-inf')
    min_c, max_c = float('inf'), float('-inf')

    # Recopilar todos los nodos con información (muros, A y B)
    nodos_activos = list(mapa_celdas.keys())
    if pos_A:
        nodos_activos.append(pos_A)
    if pos_B:
        nodos_activos.append(pos_B)

    # Buscar los límites geográficos
    for f, c in nodos_activos:
        if f < min_f: min_f = f
        if f > max_f: max_f = f
        if c < min_c: min_c = c
        if c > max_c: max_c = c

    # Añadir un margen de respiración (en cantidad de celdas)
    min_f -= 2
    max_f += 2
    min_c -= 2
    max_c += 2

    filas_total = max_f - min_f
    cols_total = max_c - min_c

    # Evitar divisiones por cero si hay un solo bloque
    if filas_total == 0: filas_total = 1
    if cols_total == 0: cols_total = 1

    # Área de visualización real disponible en el lienzo
    w_disp = ANCHO - UI_LATERAL
    h_disp = ALTO - UI_SUPERIOR - UI_INFERIOR

    # Calcular tamaño de celda ideal según el espacio
    zoom_x = w_disp / cols_total
    zoom_y = h_disp / filas_total

    # Limitar el zoom para que no sea ni microscópico ni gigantesco
    nuevo_tamano = max(20, min(200, int(min(zoom_x, zoom_y))))

    # Calcular el centro exacto de la masa de nodos
    centro_c = (min_c + max_c) / 2
    centro_f = (min_f + max_f) / 2

    # Proyectar el centro geométrico al centro de la cámara
    nueva_camara_x = int(centro_c * nuevo_tamano - w_disp / 2)
    nueva_camara_y = int(centro_f * nuevo_tamano - h_disp / 2)

    return nueva_camara_x, nueva_camara_y, nuevo_tamano