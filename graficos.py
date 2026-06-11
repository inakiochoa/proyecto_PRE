# graficos.py
import pygame
import random
from constantes import *

def generar_textura_ruido(ancho, alto, factor=8):
    textura = pygame.Surface((ancho, alto)).convert()
    for x in range(ancho):
        for y in range(alto):
            ruido = random.randint(-factor, factor)
            r = max(0, min(255, C_VACIO[0] + ruido))
            g = max(0, min(255, C_VACIO[1] + ruido))
            b = max(0, min(255, C_VACIO[2] + ruido))
            textura.set_at((x, y), (r, g, b))
    return textura

def dibujar_muro_realista(superficie, rect):
    pygame.draw.rect(superficie, C_BASE_MURO, rect)
    x, y, w, h = rect
    t = max(1, w // 10)

    color_claro = (min(255, C_BASE_MURO[0] + 30), min(255, C_BASE_MURO[1] + 30), min(255, C_BASE_MURO[2] + 30))
    pygame.draw.polygon(superficie, color_claro, [(x, y), (x + w, y), (x + w - t, y + t), (x + t, y + t), (x, y)])
    pygame.draw.polygon(superficie, color_claro, [(x, y), (x + t, y + t), (x + t, y + h - t), (x, y + h), (x, y)])

    color_oscuro = (max(0, C_BASE_MURO[0] - 40), max(0, C_BASE_MURO[1] - 40), max(0, C_BASE_MURO[2] - 40))
    pygame.draw.polygon(superficie, color_oscuro,
                        [(x, y + h), (x + t, y + h - t), (x + w - t, y + h - t), (x + w, y + h), (x, y + h)])
    pygame.draw.polygon(superficie, color_oscuro,
                        [(x + w, y), (x + w, y + h), (x + w - t, y + h - t), (x + w - t, y + t), (x + w, y)])

    if w > 20:
        pygame.draw.line(superficie, color_oscuro, (x + w // 2, y + t), (x + w // 2, y + h - t), 1)
        pygame.draw.line(superficie, color_oscuro, (x + t, y + h // 2), (x + w - t, y + h // 2), 1)

def dibujar_zona_baja_friccion(superficie, rect, col, fila):
    x, y, w, h = rect
    charco = pygame.Surface((w, h), pygame.SRCALPHA).convert_alpha()
    pygame.draw.rect(charco, list(C_BASE_FRIC_BAJA) + [100], (0, 0, w, h))

    random.seed(col * 100 + fila)
    for _ in range(max(1, w // 8)):
        sx = random.randint(w // 6, w - w // 6)
        sy = random.randint(h // 6, h - h // 6)
        color_mancha = (min(255, C_BASE_FRIC_BAJA[0] + 100), min(255, C_BASE_FRIC_BAJA[1] + 100), 255, 180)
        pygame.draw.circle(charco, color_mancha, (sx, sy), random.randint(1, max(2, w // 15)))
    superficie.blit(charco, (x, y))

def dibujar_zona_rugosa(superficie, rect, col, fila):
    x, y, w, h = rect
    parche = pygame.Surface((w, h), pygame.SRCALPHA).convert_alpha()
    pygame.draw.rect(parche, list(C_BASE_LENTO) + [180], (0, 0, w, h))

    random.seed(col * 50 + fila + 999)
    for _ in range(max(15, w * 2)):
        gx = random.randint(1, w - 2)
        gy = random.randint(1, h - 2)
        es_oscuro = random.choice([True, False])
        color_grano = (40, 25, 10, 130) if es_oscuro else (220, 180, 130, 110)
        pygame.draw.circle(parche, color_grano, (gx, gy), random.randint(1, 2))

    intervalo = max(8, w // 6)
    for i in range(-w // intervalo, (w + h) // intervalo + 1):
        offset_x = i * intervalo
        pygame.draw.line(parche, (80, 55, 25, 75), (offset_x, 0), (offset_x + h, h), 2)
    superficie.blit(parche, (x, y))

def dibujar_robot_realista(superficie, centro, tamano, angulo = 0):
    
    x, y = centro
    r = tamano // 2 - 2
    
    # 1. Creamos una superficie auxiliar transparente del tamaño del robot
    robot_surf = pygame.Surface((tamano, tamano), pygame.SRCALPHA).convert_alpha()
    
    # El centro local de esta nueva superficie será justo la mitad de su tamaño
    cx, cy = tamano // 2, tamano // 2

    # 2. Dibujamos el cuerpo del robot centrado en esta superficie local (cx, cy)
    pygame.draw.circle(robot_surf, (C_BASE_INICIO[0] - 40, C_BASE_INICIO[1] - 40, C_BASE_INICIO[2] - 40), (cx, cy), r)
    pygame.draw.circle(robot_surf, C_BORDE, (cx, cy), r, 2)
    pygame.draw.circle(robot_surf, C_BASE_INICIO, (cx, cy), r - 3)

    # Sensor central
    sensor_r = r // 2.5
    pygame.draw.circle(robot_surf, (20, 25, 30), (cx, cy), int(sensor_r))
    pygame.draw.circle(robot_surf, (150, 180, 200, 150), (cx - int(sensor_r) // 2, cy - int(sensor_r) // 2), 2)

    # Frente/Dirección del robot (Mirando a la derecha por defecto)
    rect_frente = pygame.Rect(cx + sensor_r, cy - sensor_r // 2, r - sensor_r - 1, sensor_r)
    pygame.draw.rect(robot_surf, (40, 45, 50), rect_frente, border_radius=2)
    pygame.draw.circle(robot_surf, C_BASE_INICIO, (cx + r - 4, cy), 1)

    # 3. Aplicamos la rotación matemática a toda la superficie junta
    # Usamos signo negativo porque Pygame rota en sentido antihorario
    robot_rotado = pygame.transform.rotate(robot_surf, -angulo)
    rect_rotado = robot_rotado.get_rect(center=(x, y))

    # 4. Dibujamos primero la sombra en la pantalla absoluta
    sup_sombra = pygame.Surface((tamano, tamano), pygame.SRCALPHA).convert_alpha()
    pygame.draw.circle(sup_sombra, (0, 0, 0, 80), (cx + 3, cy + 3), r)
    sombra_rotada = pygame.transform.rotate(sup_sombra, -angulo)
    superficie.blit(sombra_rotada, sombra_rotated := sombra_rotada.get_rect(center=(x + 3, y + 3)))

    # 5. Estampamos el robot rotado final encima de la sombra
    superficie.blit(robot_rotado, rect_rotado)

def dibujar_meta_realista(superficie, centro, tamano):
    x, y = centro
    r = tamano // 2 - 2

    sombra = pygame.Surface((tamano, tamano), pygame.SRCALPHA).convert_alpha()
    pygame.draw.circle(sombra, (0, 0, 0, 90), (tamano // 2 + 3, tamano // 2 + 3), r)
    superficie.blit(sombra, (x - tamano // 2, y - tamano // 2))

    pygame.draw.circle(superficie, (45, 48, 55), centro, r)
    pygame.draw.circle(superficie, (85, 90, 100), centro, r, 2)

    pygame.draw.line(superficie, (70, 75, 85), (x - r + 3, y), (x + r - 3, y), 1)
    pygame.draw.line(superficie, (70, 75, 85), (x, y - r + 3), (x, y + r - 3), 1)
    pygame.draw.circle(superficie, (60, 65, 75), centro, r // 2, 1)

    longitud_aspa = int(r * 0.65)
    grosor_aspa = max(5, tamano // 7)

    pygame.draw.line(superficie, C_BASE_FIN, (x - longitud_aspa, y - longitud_aspa),
                     (x + longitud_aspa, y + longitud_aspa), grosor_aspa)
    pygame.draw.line(superficie, C_BASE_FIN, (x - longitud_aspa, y + longitud_aspa),
                     (x + longitud_aspa, y - longitud_aspa), grosor_aspa)
    pygame.draw.circle(superficie, (255, 130, 140), centro, max(2, grosor_aspa // 2))

def dibujar_panel_industrial(superficie, rect, es_superior=True):
    x, y, w, h = rect
    for i in range(h):
        factor = i / h
        if es_superior: factor = 1.0 - factor
        r = int(C_PANEL_FONDO[0] * (1 - factor) + C_PANEL_CLARO[0] * factor)
        g = int(C_PANEL_FONDO[1] * (1 - factor) + C_PANEL_CLARO[1] * factor)
        b = int(C_PANEL_FONDO[2] * (1 - factor) + C_PANEL_CLARO[2] * factor)
        pygame.draw.line(superficie, (r, g, b), (x, y + i), (x + w, y + i))
    if es_superior:
        pygame.draw.rect(superficie, C_ACENTO, (x, y + h - 2, w, 2))
    else:
        pygame.draw.rect(superficie, C_BORDE, (x, y, 1, h))