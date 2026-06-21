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
camino_actual = []

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

def guardar_mapa_dialogo():
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

def cargar_mapa_dialogo():
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
            camino_actual = []
            
            # Forzamos un recentrado automático para que el mapa cargado se vea de inmediato
            auto_centrar_mapa()
            
            print(f"Mapa cargado con éxito desde: {ruta_archivo}")
        except Exception as e:
            print(f"Error al cargar el mapa: {e}")