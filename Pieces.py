from colors import *


class Piece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def char(self):
        return None

    def get_color(self):
        return self.color

    def can_move(self, row, col):
        def correct_coords(row, col):
            return 0 <= col <= 7 and 0 <= row <= 7

        return correct_coords(row, col)


class Pawn(Piece):
    def char(self):
        return 'P'

    def can_move(self, row, col):
        """Пешка может ходить только по строкам, а столбец всегда одинаковый"""
        if self.col != col:
            return False
        # Задаём изначальное положение для каждого цвета
        if self.color == WHITE:
            direction = 1
            start_row = 1
        else:
            direction = -1
            start_row = 6

        # ...
        if self.row + direction == row:
            return True + super().can_move(row, col)

        # ...
        if self.row == start_row and self.row + 2 * direction == row:
            return True + super().can_move(row, col)


class Rook(Piece):
    def char(self):
        return 'R'

    def can_move(self, row, col):
        """Нельзя менять обе координаты сразу"""
        if self.row != row and self.col != col:
            return False
        return super().can_move(row, col)


class Knight(Piece):
    def char(self):
        return 'N'

    def can_move(self, row, col):
        if {abs(self.row - row), abs(self.col - col)} == {1, 2}:
            return super().can_move(row, col)
        return False


class Bishop(Piece):
    def char(self):
        return 'B'

    def can_move(self, row, col):
        if (self.row - row) ** 2 == (self.col - col) ** 2:
            return super().can_move(row, col)
        return False


class Queen(Piece):
    def char(self):
        return 'Q'

    def can_move(self, row, col):
        if (self.row - row) ** 2 == (self.col - col) ** 2 or self.row == row or self.col == col:
            return super().can_move(row, col)
        return False


class King(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.check = False

    def char(self):
        return 'K'

    def can_move(self, row, col):
        if abs(self.row - row) in range(1) and abs(self.col - col) in range(1):
            return super().can_move(row, col)

    def add_check(self):
        self.check = True

    def remove_ckeck(self):
        self.check = False