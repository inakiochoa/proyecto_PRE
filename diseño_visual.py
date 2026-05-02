import pygame, sys

pygame.init()

screen_W = 800
screen_H = 880
offset_top = 80

blanco = (255,255,255)
gris = (200, 200, 200)
azul = (0,150,180)
rojo = (192, 64, 0)
verde = (87, 149, 50)

screen = pygame.display.set_mode((screen_W, screen_H))
pygame.display.set_caption("Path Finder")

clock = pygame.time.Clock()

cell_size = 40
columnas = screen_W // cell_size
filas = (screen_H - offset_top) // cell_size


class Player:
    def __init__(self):
        self.x = 0
        self.y = filas - 1
        self.color = (azul)
        self.rastro = []

    def draw(self):
        for huella in self.rastro:
            rect_rastro = pygame.Rect(huella[0] * cell_size + 10,
                                      huella[1] * cell_size + offset_top + 10, 
                                      cell_size - 20, cell_size - 20)
            pygame.draw.rect(screen, (220, 220, 220), rect_rastro)
        
        rect = pygame.Rect(self.x * cell_size,
                           self.y * cell_size + offset_top,
                           cell_size, cell_size)
        pygame.draw.rect(screen, self.color, rect)

class Mapa:
    def draw(self, superficie):
        for x in range(0, screen_W + 1, cell_size):
            pygame.draw.line(superficie, gris, (x, offset_top), (x, screen_H))
        for y in range(offset_top, screen_H + 1, cell_size):
            pygame.draw.line(superficie, gris, (0, y), (screen_W, y))

mapa = Mapa()
player = Player()
pygame.font.init()
fuente_titulo = pygame.font.SysFont("Times New Roman", 48, bold = True)
fuente_marcador = pygame.font.SysFont("Times New Roman", 30, bold = False)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            player.rastro.append((player.x, player.y))

            if event.key == pygame.K_UP and player.y > 0:
                player.y -= 1
            if event.key == pygame.K_DOWN and player.y < filas - 1:
                player.y += 1
            if event.key == pygame.K_LEFT and player.x > 0:
                player.x -= 1
            if event.key == pygame.K_RIGHT and player.x < columnas - 1:
                player.x += 1

    screen.fill(blanco) 

    superficie_texto = fuente_titulo.render("PATH FINDER", True, (rojo))
    screen.blit(superficie_texto, (20, 12))

    texto_pasos = f"Movimientos: {len(player.rastro)}"
    superficie_pasos = fuente_marcador.render(texto_pasos, True, (verde))
    screen.blit(superficie_pasos, (500, 25))

    mapa.draw(screen)
    player.draw()

    pygame.display.flip()
    clock.tick(60)        

