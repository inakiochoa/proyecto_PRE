# Motor.py
from constantes import *

# --- ESTADO GLOBAL DEL SIMULADOR ---
estado_pantalla = "MENU"  # "MENU" o "SIMULACION"
algoritmo_modo = "OMNISCIENTE"  # "OMNISCIENTE" o "REACTIVO"
modo_actual = M_MURO

# Estructura del mapa: {(fila, col): M_MURO}
mapa_celdas = {}
pos_A = None  # Guardado como (fila, col)
pos_B = None  # Guardado como (fila, col)

# Cámara y Zoom
tamano_celda = 45
camara_x = 0
camara_y = 0

# Desplazamiento de cámara con botón central
desplazando = False
inicio_desplazamiento = (0, 0)
inicio_camara = (0, 0)

# Métrica y escala
escala_texto = "1.0"
metros_por_celda = 1.0
editando_escala = False
mostrar_cuadricula = True

# Cinemática del Robot
robot_visual_x = None  # Flotante posicionado en Columnas (X)
robot_visual_y = None  # Flotante posicionado en Filas (Y)
rastro_fluido = []  # Lista de tuplas (x, y) visuales pasadas
camino_actual = []  # Lista de tuplas (fila, col) planificadas por la IA
metros_recorridos = 0.0
ruta_imposible = False


def auto_centrar_mapa():
    """Calcula los límites de los elementos actuales y ajusta el zoom y la cámara para mostrarlos todos."""
    global camara_x, camara_y, tamano_celda

    puntos = []
    if pos_A: puntos.append(pos_A)
    if pos_B: puntos.append(pos_B)
    for (f, c) in mapa_celdas.keys():
        puntos.append((f, c))

    # Si el mapa está completamente vacío, devolvemos un centro estándar por defecto
    if not puntos:
        nuevo_tamano = 45
        nueva_cx = -((ANCHO - UI_LATERAL) // 2) + 200
        nueva_cy = -((ALTO - UI_SUPERIOR - UI_INFERIOR) // 2)
        return nueva_cx, nueva_cy, nuevo_tamano

    # 1. Encontrar los extremos del contenido activo (Bounding Box)
    min_f = min(p[0] for p in puntos)
    max_f = max(p[0] for p in puntos)
    min_c = min(p[1] for p in puntos)
    max_c = max(p[1] for p in puntos)

    filas = max_f - min_f + 1
    cols = max_c - min_c + 1

    # 2. Calcular el nuevo tamaño de celda (zoom) con un margen de seguridad de 120px para que respire
    area_ancho = ANCHO - UI_LATERAL - 120
    area_alto = ALTO - UI_SUPERIOR - UI_INFERIOR - 120

    tam_ancho = area_ancho / max(1, cols)
    tam_alto = area_alto / max(1, filas)

    # Acotamos el zoom para evitar deformaciones microscópicas o gigantescas
    nuevo_tamano = max(20, min(150, int(min(tam_ancho, tam_alto))))

    # 3. Calcular el centro matemático indexado
    centro_c = (min_c + max_c) / 2
    centro_f = (min_f + max_f) / 2

    # 4. Calcular el centro físico útil del lienzo de simulación
    pantalla_cx = (ANCHO - UI_LATERAL) / 2
    pantalla_cy = (ALTO - UI_SUPERIOR - UI_INFERIOR) / 2

    # 5. Ajustar cámara compensando el desplazamiento del medio bloque local de las funciones de renderizado
    nueva_cx = int((centro_c + 0.5) * nuevo_tamano - pantalla_cx)
    nueva_cy = int((centro_f + 0.5) * nuevo_tamano - pantalla_cy)

    return nueva_cx, nueva_cy, nuevo_tamano