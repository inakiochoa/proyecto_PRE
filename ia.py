# algoritmo.py

def calcular_camino_directo(inicio, fin):
    """
    Calcula el camino más corto en línea recta entre 'inicio' y 'fin'
    sin tener en cuenta obstáculos.
    """
    # Si no se ha colocado el robot o la meta, no hay camino
    if inicio is None or fin is None:
        return []

    camino = []
    
    # Empezamos a calcular desde la posición del robot
    x_actual, y_actual = inicio
    x_destino, y_destino = fin

    # El bucle se repite hasta que el camino llegue a la meta
    while (x_actual, y_actual) != (x_destino, y_destino):
        
        # 1. Decidir movimiento en el eje X
        if x_actual < x_destino:
            x_actual += 1
        elif x_actual > x_destino:
            x_actual -= 1
            
        # 2. Decidir movimiento en el eje Y
        elif y_actual < y_destino:
            y_actual += 1
        elif y_actual > y_destino:
            y_actual -= 1

        # Guardamos la casilla actual en nuestra lista del camino
        if (x_actual, y_actual) != (x_destino, y_destino):
            camino.append((x_actual, y_actual))

    return camino