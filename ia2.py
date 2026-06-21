# ia2.py
import heapq


def a_star(inicio, fin, mapa_muros):
    """
    Algoritmo A* puro y de alto rendimiento que trabaja de forma estricta
    en formato de matriz (fila, columna).
    """
    if not inicio or not fin:
        return None

    def heuristica(a, b):
        # Usamos distancia Manhattan estándar para movimientos ortogonales en rejilla
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    heapq.heappush(open_set, (0, inicio))

    procedencia = {}
    g_score = {inicio: 0}
    f_score = {inicio: heuristica(inicio, fin)}

    # Direcciones ortogonales directas (Arriba, Abajo, Izquierda, Derecha)
    movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while open_set:
        actual = heapq.heappop(open_set)[1]

        if actual == fin:
            # Reconstrucción reversa del camino óptimo encontrado
            camino = []
            while actual in procedencia:
                camino.append(actual)
                actual = procedencia[actual]
            camino.reverse()
            return camino

        for df, dc in movimientos:
            vecino = (actual[0] + df, actual[1] + dc)

            # Verificación estricta de colisión con muros indexados en memoria
            if mapa_muros.get(vecino) == 1:  # 1 representa M_MURO
                continue

            tentative_g = g_score[actual] + 1

            if tentative_g < g_score.get(vecino, float('inf')):
                procedencia[vecino] = actual
                g_score[vecino] = tentative_g
                f_score[vecino] = tentative_g + heuristica(vecino, fin)
                heapq.heappush(open_set, (f_score[vecino], vecino))

    return None  # No existe un camino viable libre de colisiones