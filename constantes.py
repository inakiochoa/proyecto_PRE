# constantes.py

# --- CONFIGURACIÓN DE PANTALLA ---
ANCHO, ALTO = 1200, 850
TITULO_APP = "PROBOT PATHFINDER IDE"

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

# --- MODOS DE EDICIÓN ---
M_BORRAR, M_MURO, M_FRIC, M_LENTO, M_A, M_B = 0, 1, 2, 3, 4, 5

herramientas = [
    {"id": M_MURO, "txt": "MURO [1]", "color": C_BASE_MURO},
    {"id": M_FRIC, "txt": "FRICCIÓN ↓ [2]", "color": C_BASE_FRIC_BAJA},
    {"id": M_LENTO, "txt": "FRICCIÓN ↑  [3]", "color": C_BASE_LENTO},
    {"id": M_BORRAR, "txt": "BORRAR [4]", "color": (180, 50, 50)},
    {"id": M_A, "txt": "ROBOT [5]", "color": C_BASE_INICIO},
    {"id": M_B, "txt": "META [6]", "color": C_BASE_FIN},
]