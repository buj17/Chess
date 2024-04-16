WHITE = 1
BLACK = 0


# Удобная функция для вычисления цвета противника
def opponent(color):
    if color == WHITE:
        return BLACK
    return WHITE
