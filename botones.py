import pygame
from constantes import C_TXT, C_BORDE

class BotonLateral:
    def __init__(self, x, y, ancho, alto, texto, color_base, color_hover, color_borde):
        """Inicializa las coordenadas, el texto y la paleta de colores del botón."""
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_base = color_base
        self.color_hover = color_hover
        self.color_borde = color_borde

    def comprobar_clic(self, mx, my):
        """Devuelve True si el ratón está haciendo clic dentro del botón."""
        return self.rect.collidepoint(mx, my)

    def dibujar(self, superficie, fuente, mx, my):
        """Se encarga de pintarse a sí mismo en la pantalla gestionando el brillo (hover)."""
        # 1. Detectar si el cursor está sobre el botón para cambiar el color
        esta_encima = self.rect.collidepoint(mx, my)
        color_actual = self.color_hover if esta_encima else self.color_base

        # 2. Dibujar la caja del botón y su contorno
        pygame.draw.rect(superficie, color_actual, self.rect, border_radius=6)
        grosor_borde = 2 if esta_encima else 1
        pygame.draw.rect(superficie, self.color_borde, self.rect, grosor_borde, border_radius=6)

        # 3. Dibujar el texto centrado en el medio del botón
        txt_surf = fuente.render(self.texto, True, C_TXT)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        superficie.blit(txt_surf, txt_rect)