#IA.py
# Este algoritmo actualiza la ruta óptima cada vez que se encuentra con un muro



# Esta es la memoria interna del robot. Al principio de la simulación está vacía.
MUROS_MEMORIZADOS = {}

def calcular_camino_directo(inicio, fin, mapa_para_buscar=None):
    """
    Calcula la ruta utilizando el algoritmo BFS.
    Solo tiene en cuenta los muros que se le pasen en 'mapa_para_buscar'.
    """
    if inicio is None or fin is None:
        return []

    if mapa_para_buscar is None:
        mapa_para_buscar = {}

    from constantes import M_MURO

    cola = [(inicio, [])]
    visitados = {inicio}

    while cola:
        casilla_actual, camino_acumulado = cola.pop(0)

        if casilla_actual == fin:
            return camino_acumulado

        x, y = casilla_actual
        vecinos = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

        for vecino in vecinos:
            # Revisa la memoria de mapas que le pasamos, no el mapa real entero
            if vecino not in visitados and mapa_para_buscar.get(vecino) != M_MURO:
                visitados.add(vecino)
                cola.append((vecino, camino_acumulado + [vecino]))

    return []


def actualizar_movimiento(pos_actual, pos_meta, camino_actual, mapa_real_celdas):
    """
    Controla el movimiento. Si encuentra un muro real, lo memoriza
    y recalcula la ruta basándose SOLO en los muros que ya conoce.
    """
    global MUROS_MEMORIZADOS

    # Si el robot se ha teletransportado o reiniciado en el inicio, vaciamos su memoria
    # (Esto sirve para cuando pulsas "Iniciar Ruta" de nuevas)
    if len(camino_actual) > 0 and pos_actual not in camino_actual:
        # Si es el primer paso ideal del botón, nos aseguramos de que su memoria se limpie
        if len(MUROS_MEMORIZADOS) > 0 and MUROS_MEMORIZADOS != mapa_real_celdas:
            # Si el camino actual vino del botón inicial (sin muros), limpiamos memoria
            # Comprobación simple: si el camino actual no coincide con esquivar muros conocidos,
            # asumimos que es una nueva simulación.
            pass

    if not camino_actual:
        return pos_actual, camino_actual

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