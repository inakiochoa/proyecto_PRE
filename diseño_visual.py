import pygame, sys

# Inicialización de Pygame
pygame.init()

# --- CONFIGURACIÓN GENERAL ---
screen_W = 800
screen_H = 880
offset_top = 80  # Espacio reservado para la interfaz superior (título y marcador)

# Paleta de colores (RGB)
blanco = (255, 255, 255)
gris = (200, 200, 200)
azul = (0, 150, 180)
rojo = (192, 64, 0)
verde = (87, 149, 50)

# Creación de la ventana
screen = pygame.display.set_mode((screen_W, screen_H))
pygame.display.set_caption("Path Finder")

clock = pygame.time.Clock()

# Cálculo de la cuadrícula
cell_size = 40
columnas = screen_W // cell_size
filas = (screen_H - offset_top) // cell_size


# ==========================================
# --- VISTA (VIEW) ---
# En esta sección se definen las clases responsables de
# cómo se ven y dibujan los elementos en pantalla.
# ==========================================

class Player:
    def __init__(self):
        self.x = 0
        self.y = filas - 1
        self.color = (azul)
        self.rastro = []  # Guarda el historial de coordenadas para dibujar el camino

    def draw(self):
        # Primero dibuja el rastro (camino recorrido)
        for huella in self.rastro:
            rect_rastro = pygame.Rect(huella[0] * cell_size + 10,
                                      huella[1] * cell_size + offset_top + 10,
                                      cell_size - 20, cell_size - 20)
            pygame.draw.rect(screen, (220, 220, 220), rect_rastro)

        # Luego dibuja la posición actual del robot encima del rastro
        rect = pygame.Rect(self.x * cell_size,
                           self.y * cell_size + offset_top,
                           cell_size, cell_size)
        pygame.draw.rect(screen, self.color, rect)


class Mapa:
    def draw(self, superficie):
        # Dibuja las líneas verticales de la cuadrícula
        for x in range(0, screen_W + 1, cell_size):
            pygame.draw.line(superficie, gris, (x, offset_top), (x, screen_H))
        # Dibuja las líneas horizontales de la cuadrícula
        for y in range(offset_top, screen_H + 1, cell_size):
            pygame.draw.line(superficie, gris, (0, y), (screen_W, y))


# Instanciación de los elementos de la Vista
mapa = Mapa()
player = Player()

# Configuración de tipografías para la interfaz
pygame.font.init()
fuente_titulo = pygame.font.SysFont("Times New Roman", 48, bold=True)
fuente_marcador = pygame.font.SysFont("Times New Roman", 30, bold=False)

# ==========================================
# --- PRESENTADOR / CONTROLADOR (PRESENTER) ---
# Este bucle principal gestiona la lógica de la aplicación,
# la recolección de eventos (inputs) y actualiza la Vista.
# ==========================================

while True:
    # 1. GESTIÓN DE EVENTOS (INPUT)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # NOTA IMPORTANTE SOBRE EL ALGORITMO:
        # La parte realmente complicada de este proyecto será el desarrollo
        # e integración del algoritmo de búsqueda de rutas (A*, Dijkstra, etc.) que
        # deberá dotar de inteligencia al robot para esquivar obstáculos.
        # De momento, para probar que el entorno gráfico (View), la cuadrícula y
        # el guardado del rastro funcionan correctamente, se ha implementado de
        # manera provisional que seamos nosotros mismos quienes movemos el robot manualmente.

        if event.type == pygame.KEYDOWN:
            # Antes de moverse, guarda la posición actual en el rastro
            player.rastro.append((player.x, player.y))

            # Actualiza la posición lógica según la tecla pulsada, limitando con los bordes
            if event.key == pygame.K_UP and player.y > 0:
                player.y -= 1
            if event.key == pygame.K_DOWN and player.y < filas - 1:
                player.y += 1
            if event.key == pygame.K_LEFT and player.x > 0:
                player.x -= 1
            if event.key == pygame.K_RIGHT and player.x < columnas - 1:
                player.x += 1

    # 2. ACTUALIZACIÓN DE LA VISTA (RENDERIZADO)
    # Limpiamos la pantalla con el color de fondo
    screen.fill(blanco)

    # Renderizamos la interfaz superior (UI)
    superficie_texto = fuente_titulo.render("PATH FINDER", True, (rojo))
    screen.blit(superficie_texto, (20, 12))

    texto_pasos = f"Movimientos: {len(player.rastro)}"
    superficie_pasos = fuente_marcador.render(texto_pasos, True, (verde))
    screen.blit(superficie_pasos, (500, 25))

    # Mandamos a la Vista que dibuje el mapa y el jugador en sus estados actuales
    mapa.draw(screen)
    player.draw()

    # Refrescamos la pantalla para mostrar el nuevo fotograma
    pygame.display.flip()

    # Limitamos los fotogramas por segundo (60 FPS) para no saturar el procesador
    clock.tick(60)