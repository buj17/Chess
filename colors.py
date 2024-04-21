"""Задаем константы"""
WHITE = 1
BLACK = 0


def opponent(color):
    """Удобная функция для вычисления цвета противника"""
    if color == WHITE:
        return BLACK
    return WHITE


def correct_cords(row, col):
    """Проверка корректности координат"""
    return 0 <= col <= 7 and 0 <= row <= 7
