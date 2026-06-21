# IA2.py

def calcular_camino_directo(inicio, fin, mapa_celdas=None):
    """
    [BOTÓN INICIAR RUTA] Calcula la ruta óptima de antemano utilizando el algoritmo BFS.
    Analiza el mapa completo y esquiva todos los muros desde el primer segundo.
    """
    if inicio is None or fin is None:
        return []

    # Si por algún motivo no llega el mapa, asumimos que está vacío
    if mapa_celdas is None:
        mapa_celdas = {}

    from constantes import M_MURO

    # Cola de exploración: guarda (casilla_actual, camino_hasta_esta_casilla)
    cola = [(inicio, [])]
    # Conjunto de casillas ya revisadas para no entrar en bucles infinitos
    visitados = {inicio}

    while cola:
        casilla_actual, camino_acumulado = cola.pop(0)

        # Si encontramos la meta, devolvemos la ruta acumulada paso a paso
        if casilla_actual == fin:
            return camino_acumulado

        # Mirar las 4 casillas vecinas (Arriba, Abajo, Izquierda, Derecha)
        x, y = casilla_actual
        vecinos = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

        for vecino in vecinos:
            # Si el vecino no ha sido visitado Y NO contiene un muro, es un camino válido
            if vecino not in visitados and mapa_celdas.get(vecino) != M_MURO:
                visitados.add(vecino)
                # Añadimos a la cola para explorar desde ahí en la siguiente ronda
                cola.append((vecino, camino_acumulado + [vecino]))

    # Si se explora todo y no hay forma de llegar (meta encerrada), devolvemos camino vacío
    return []


def actualizar_movimiento(pos_actual, pos_meta, camino_actual, mapa_celdas):
    """
    [TEMPORIZADOR] Hace avanzar al robot casilla a casilla por la ruta inteligente ya calculada.
    Como el camino ya esquiva los muros de antemano, aquí solo extraemos el siguiente paso.
    """
    if not camino_actual:
        return pos_actual, camino_actual

    # Como la ruta ya es perfecta gracias al BFS del botón, avanzamos de forma segura
    siguiente_casilla = camino_actual.pop(0)
    return siguiente_casilla, camino_actual