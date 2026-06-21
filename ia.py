# ia.py
import ia2

# Memoria local para el modo de exploración Reactiva
muros_descubiertos_reactivo = {}


def reiniciar_memoria():
    """Limpia los sensores del robot al reiniciar la simulación."""
    global muros_descubiertos_reactivo
    muros_descubiertos_reactivo.clear()


def calcular_camino_directo(inicio, fin, mapa_real, modo):
    """
    Calcula la ruta basándose en el nivel de acceso del algoritmo seleccionado.
    Retorna una lista de tuplas (fila, col).
    """
    if not inicio or not fin:
        return []

    if modo == "OMNISCIENTE":
        # Conoce todos los muros de antemano
        return ia2.a_star(inicio, fin, mapa_real)
    else:
        # MODO REACTIVO: Escanea el entorno local inmediato en busca de amenazas
        actualizar_radar_reactivo(inicio, mapa_real)
        ruta = ia2.a_star(inicio, fin, muros_descubiertos_reactivo)
        return ruta if ruta else []


def actualizar_radar_reactivo(pos_robot, mapa_real):
    """Escanea las celdas contiguas simulando sensores de rango de corto alcance."""
    global muros_descubiertos_reactivo
    f, c = pos_robot
    # Escáner en anillo de vecindad de radio 2 celdas
    for df in range(-2, 3):
        for dc in range(-2, 3):
            eval_celda = (f + df, c + dc)
            if mapa_real.get(eval_celda) == 1:  # Si hay un muro real en el mapa global
                muros_descubiertos_reactivo[eval_celda] = 1


def actualizar_movimiento(pos_actual, pos_meta, camino_antiguo, mapa_real, modo):
    """
    Evalúa la ruta a cada paso. Si es reactivo y detecta un obstáculo imprevisto en su camino,
    frena la marcha y recalcula una trayectoria de evasión dinámica.
    """
    if not camino_antiguo:
        return pos_actual, []

    if modo == "OMNISCIENTE":
        # Sigue el vector calculado sin vacilar
        nuevo_camino = camino_antiguo[1:]
        siguiente_paso = camino_antiguo[0]
        return siguiente_paso, nuevo_camino
    else:
        # MODO REACTIVO: Avanza un casillero y comprueba si los sensores revelan bloqueos inminentes
        siguiente_paso = camino_antiguo[0]
        actualizar_radar_reactivo(siguiente_paso, mapa_real)

        # Comprobar si el camino restante colisiona con lo que acaba de descubrir el radar
        colision_detectada = False
        for nodo in camino_antiguo:
            if muros_descubiertos_reactivo.get(nodo) == 1:
                colision_detectada = True
                break

        if colision_detectada:
            # ¡Alerta de colisión! Forzar recálculo inmediato desde la posición del siguiente paso
            camino_recalculado = ia2.a_star(siguiente_paso, pos_meta, muros_descubiertos_reactivo)
            return siguiente_paso, (camino_recalculado if camino_recalculado else [])
        else:
            return siguiente_paso, camino_antiguo[1:]