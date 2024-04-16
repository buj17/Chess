from functools import reduce

from Pieces import *
from colors import *


class Board:
    def __init__(self):
        self.color = WHITE
        self.field: list[list[Piece | None]] = [[None] * 8 for _ in range(8)]

        for i in range(8):
            self.field[1][i] = Pawn(1, i, WHITE)

        for i in range(8):
            self.field[6][i] = Pawn(6, i, BLACK)



    def cell(self, row, col):
        """Возвращает строку из двух символов. Если в клетке (row, col)
                находится фигура, символы цвета и фигуры. Если клетка пуста,
                то два пробела."""
        piece: Piece | None = self.field[row][col]
        if piece is None:
            return '  '
        color = piece.get_color()
        c = 'w' if color == WHITE else 'b'
        return c + piece.char()

    def current_player_color(self):
        return self.color

    def move_piece(self, row, col, row1, col1):
        """Переместить фигуру из точки (row, col) в точку (row1, col1).
                Если перемещение возможно, метод выполнит его и вернет True.
                Если нет --- вернет False"""
        if row == row1 and col == col1:
            return False  # нельзя пойти в ту же клетку
        piece: Piece | None = self.field[row][col]
        if piece is None:
            return False  # нельзя пойти без фигуры
        if piece.get_color() != self.color:
            return False  # игрок хоидт не своим цветом
        if not piece.can_move(row1, col1):
            return False  # неправильный ход
        self.field[row][col] = None  # Снять фигуру.
        self.field[row1][col1] = piece  # Поставить на новое место.
        piece.set_position(row1, col1)
        self.color = opponent(self.color)
        return True

    def is_under_attack(self, row, col, color):
        return any((map(lambda x: x is not None and x.can_move(row, col) and x.get_color() == color,
                        reduce(lambda x, y: x + y, self.field, []))))

    def __str__(self):
        res = ['     +----+----+----+----+----+----+----+----+']
        for row in range(7, -1, -1):
            res.append(' ' + str(row) + '   ')
            for col in range(8):
                res[-1] += '| '
                res[-1] += self.cell(row, col)
                res[-1] += ' '
            res[-1] += '|'
            res.append('     +----+----+----+----+----+----+----+----+')
        res.append('        ')
        for col in range(8):
            res[-1] += str(col)
            res[-1] += '    '
        return '\n'.join(res)

    # def print_board(self):  # Распечатать доску в текстовом виде
    #     print('     +----+----+----+----+----+----+----+----+')
    #     for row in range(7, -1, -1):
    #         print(' ', row, end='  ')
    #         for col in range(8):
    #             print('|', self.cell(row, col), end=' ')
    #         print('|')
    #         print('     +----+----+----+----+----+----+----+----+')
    #     print(end='        ')
    #     for col in range(8):
    #         print(col, end='    ')
    #     print()


a = Board()
print(a)
