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
modo_actual = None

# --- CONTROLES DE DESPLAZAMIENTO (PAN) ---
desplazando = False
inicio_desplazamiento = (0, 0)
inicio_camara = (0, 0)
ignorar_clic_mapa = False

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



def guardar_mapa_disco():
    """Muestra un diálogo nativo para guardar el estado del mapa actual."""
    import tkinter as tk
    from tkinter import filedialog
    import pickle

    # Ocultar la ventana principal de tkinter
    root = tk.Tk()
    root.withdraw()

    # Abrir explorador de archivos para guardar
    ruta_archivo = filedialog.asksaveasfilename(
        title="Guardar Mapa de Probot",
        defaultextension=".probot",
        filetypes=[("Archivos de Mapa Probot", "*.probot"), ("Todos los archivos", "*.*")]
    )

    # Si el usuario no cancela el diálogo
    if ruta_archivo:
        try:
            # Empaquetamos todo el estado relevante del mapa
            datos_mapa = {
                "mapa_celdas": mapa_celdas,
                "pos_A": pos_A,
                "pos_B": pos_B,
                "metros_por_celda": metros_por_celda,
                "escala_texto": escala_texto
            }
            with open(ruta_archivo, "wb") as f:
                pickle.dump(datos_mapa, f)
            print(f"Mapa guardado con éxito en: {ruta_archivo}")
        except Exception as e:
            print(f"Error al guardar el mapa: {e}")

def cargar_mapa_disco():
    """Muestra un diálogo nativo para cargar un archivo de mapa y actualizar el estado."""
    import tkinter as tk
    from tkinter import filedialog
    import pickle

    # Declaramos globales para poder modificar el estado del motor
    global mapa_celdas, pos_A, pos_B, metros_por_celda, escala_texto, camino_actual

    root = tk.Tk()
    root.withdraw()

    # Abrir explorador de archivos para abrir
    ruta_archivo = filedialog.askopenfilename(
        title="Cargar Mapa de Probot",
        filetypes=[("Archivos de Mapa Probot", "*.probot"), ("Todos los archivos", "*.*")]
    )

    if ruta_archivo:
        try:
            with open(ruta_archivo, "rb") as f:
                datos_mapa = pickle.load(f)
            
            # Restauramos las variables del simulador
            mapa_celdas = datos_mapa.get("mapa_celdas", {})
            pos_A = datos_mapa.get("pos_A", None)
            pos_B = datos_mapa.get("pos_B", None)
            metros_por_celda = datos_mapa.get("metros_por_celda", 0.5)
            escala_texto = datos_mapa.get("escala_texto", "0.5")
            
            # Limpiamos cualquier ruta activa que estuviese calculada
            camino_actual.clear()
            
            # Forzamos un recentrado automático para que el mapa cargado se vea de inmediato
            auto_centrar_mapa()
            
            print(f"Mapa cargado con éxito desde: {ruta_archivo}")
        except Exception as e:
            print(f"Error al cargar el mapa: {e}")