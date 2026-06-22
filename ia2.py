# ia2.py
import heapq

def a_star(inicio, fin, mapa_muros):
    if not inicio or not fin:
        return None

    # Calcula la distancia entre la casilla actual (robot) y la meta
    def heuristica(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    # Añade el valor más pequeño al principio
    heapq.heappush(open_set, (0, inicio))

    # Recuerda el camino de regreso
    procedencia = {}
    # Distancia que ha recorrido el robot
    g_score = {inicio: 0}
    # Distancia total que recorrerá el robot
    f_score = {inicio: heuristica(inicio, fin)}

    movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # Límite de seguridad
    MAX_NODOS = 20_000 
    nodos_explorados = 0

    while open_set:
        actual = heapq.heappop(open_set)[1]

        nodos_explorados += 1
        if nodos_explorados > MAX_NODOS:
            return None  # Espacio demasiado grande o meta inaccesible

        if actual == fin:
            camino = []
            # Para reconstuir el camino
            while actual in procedencia:
                camino.append(actual)
                actual = procedencia[actual]
            camino.reverse()
            return camino

        for df, dc in movimientos:
            vecino = (actual[0] + df, actual[1] + dc)

            if mapa_muros.get(vecino) == 1:
                continue

            tentative_g = g_score[actual] + 1

            if tentative_g < g_score.get(vecino, float('inf')):
                procedencia[vecino] = actual
                g_score[vecino] = tentative_g
                f_score[vecino] = tentative_g + heuristica(vecino, fin)
                heapq.heappush(open_set, (f_score[vecino], vecino))

    return None