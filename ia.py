# Este algoritmo actualiza la ruta óptima cada vez que se encuentra con un muro

# Esta es la memoria interna del robot. Al principio de la simulación está vacía.

MUROS_MEMORIZADOS = {}

def calcular_camino_directo(inicio, fin, mapa_para_buscar=None):
    """
    Calcula la ruta utilizando el algoritmo BFS.
    Solo tiene en cuenta los muros que se le pasen en 'mapa_para_buscar'.
    """

    # Evita que al pulsar "Iniciar Ruta" sin colocar la meta o el robot haya errores
    if inicio is None or fin is None:
        return []

    # Crea un mapa vacío al iniciar la ruta
    if mapa_para_buscar is None:
        mapa_para_buscar = {}

    from constantes import M_MURO

    # Guarda las casillas por las que se ha pasado
    cola = [(inicio, [])]
    visitados = {inicio}

    # Seguro para meta encerrada
    iteraciones = 0
    MAX_ITERACIONES = 10000  # Límite seguro para evitar que el bucle explore el infinito

    # Mientras existan elementos dentro de cola...
    while cola:
        # Si damos demasiadas vueltas buscando una salida imposible, abortamos
        iteraciones += 1
        if iteraciones > MAX_ITERACIONES:
            return []

        # Extrae los elementos de cola
        casilla_actual, camino_acumulado = cola.pop(0)

        # El robot ha llegado a la meta
        if casilla_actual == fin:
            return camino_acumulado

        # Asinga a x e y los valores de la casilla actual
        x, y = casilla_actual

        # Crea una lista con las casillas vecinas a la actual
        vecinos = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

        for vecino in vecinos:
            # Revisa la memoria de mapas que le pasamos, no el mapa real entero
            # Si la casilla no ha sido visitada y no es un muro...
            if vecino not in visitados and mapa_para_buscar.get(vecino) != M_MURO:
                # Se añade a visitados y a cola
                visitados.add(vecino)
                cola.append((vecino, camino_acumulado + [vecino]))

    return []

def actualizar_movimiento(pos_actual, pos_meta, camino_actual, mapa_real_celdas):
    """
    Controla el movimiento. Si encuentra un muro real, lo memoriza
    y recalcula la ruta basándose SOLO en los muros que ya conoce.
    """
    global MUROS_MEMORIZADO

    siguiente_casilla = camino_actual[0]
    from constantes import M_MURO
    
    # 1. Comprobamos si hay un muro REAL en el mapa del juego
    if mapa_real_celdas.get(siguiente_casilla) == M_MURO:
        print(f"¡CHOQUE! Muro descubierto en {siguiente_casilla}. Añadiendo a la memoria...")
        
        # 2. El robot aprende: Guarda este muro específico en su memoria
        MUROS_MEMORIZADOS[siguiente_casilla] = M_MURO
        
        camino_actual.clear()
        
        # 3. Recalcula la ruta usando UNICAMENTE su memoria acumulada de choques
        nueva_ruta = calcular_camino_directo(pos_actual, pos_meta, MUROS_MEMORIZADOS)
        return pos_actual, nueva_ruta
    else:
        # Camino libre: avanza de forma normal
        camino_actual.pop(0)
        return siguiente_casilla, camino_actual

def reiniciar_memoria():
    """Limpia los muros guardados por el robot para una nueva simulación."""
    global MUROS_MEMORIZADOS
    MUROS_MEMORIZADOS.clear()