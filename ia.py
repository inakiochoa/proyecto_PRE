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

    # Si no se coloca el robot o la meta no hace nada
    if not inicio or not fin:
        return []

    # Si seleccionamos el modo OMNISCIENTE se activa
    if modo == "OMNISCIENTE":
        # Conoce todos los muros de antemano
        return ia2.a_star(inicio, fin, mapa_real)

    # En caso contrario se activa el modo REACTIVO
    else:
        # MODO REACTIVO: Escanea el entorno en busca de muros

        # Comprueba que no haya muros en la posición inicial
        # Si lo encuentra lo anota en muros descubiertos
        actualizar_radar_reactivo(inicio, mapa_real)

        # Aquí le pasamos los muros descubiertos, no el mapa_real
        # Calcula la ruta teniendo en cuenta solo los muros descubiertos
        ruta = ia2.a_star(inicio, fin, muros_descubiertos_reactivo)

        # Devuelve la ruta solo si no está vacía, de lo contrario devuelveme una lista vacía
        return ruta if ruta else []


def actualizar_radar_reactivo(pos_robot, mapa_real):
    """Escanea las celdas contiguas simulando sensores de rango de corto alcance."""
    global muros_descubiertos_reactivo

    # Posición actual del mapa
    f, c = pos_robot

    # Escáner en anillo de vecindad de radio 2 celdas
    for df in range(-2, 3):
        for dc in range(-2, 3):
            eval_celda = (f + df, c + dc)

            # Cuando el robot detecta un muro le pregunta al mapa_real si hay un muro
            if mapa_real.get(eval_celda) == 1:  # Si hay un muro real en el mapa global
                muros_descubiertos_reactivo[eval_celda] = 1


def actualizar_movimiento(pos_actual, pos_meta, camino_antiguo, mapa_real, modo):
    """
    Evalúa la ruta a cada paso. Si es reactivo y detecta un obstáculo imprevisto en su camino,
    frena la marcha y recalcula una trayectoria de evasión dinámica.
    """

    # Si no se puede encontrar ninguna ruta o el robot ya ha llegado a la meta
    if not camino_antiguo:
        return pos_actual, []

    if modo == "OMNISCIENTE":
        
        # Calcula el siguiente paso y el nuevo camino
        nuevo_camino = camino_antiguo[1:]
        siguiente_paso = camino_antiguo[0]
        return siguiente_paso, nuevo_camino

    else:
        # MODO REACTIVO: Avanza un casillero y comprueba si los sensores revelan bloqueos inminentes
        siguiente_paso = camino_antiguo[0]
        # Antes de avanzar compureba con el radar si hay muros alrededor
        actualizar_radar_reactivo(siguiente_paso, mapa_real)

        # Comprobar si el camino restante colisiona con lo que acaba de descubrir el radar
        colision_detectada = False
        # Comprueba que las casillas por donde va a pasar no contienen muros
        for nodo in camino_antiguo:
            if muros_descubiertos_reactivo.get(nodo) == 1:
                colision_detectada = True
                break

        if colision_detectada:
            # ¡Alerta de choque! Se calcula una nueva ruta con los muros detectados
            camino_recalculado = ia2.a_star(siguiente_paso, pos_meta, muros_descubiertos_reactivo)
            # Avanza a la siguiente casilla y recalcula el camino a no ser que esté encerrado
            return siguiente_paso, (camino_recalculado if camino_recalculado else [])
        # Si no se ha detectado colisió, calcula el siguiente paso y actualiza el camino
        else:
            return siguiente_paso, camino_antiguo[1:]