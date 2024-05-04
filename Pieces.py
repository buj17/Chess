"""Главные правила, которых мы будем придерживаться:
1. Фигура никак не может двигаться и атаковать, если сейчас не ее ход
2. Никакая фигура не может пойти в клетку, где стоит фигура такого же цвета
3. Никакая фигура не может атаковать клетку, где стоит фигура такого же цвета
4. При проверке, может ли фигура сделать ход, мы не будем проверять появление шахов, все проверяется в классе Board
"""

from colors import WHITE, BLACK, correct_cords, opponent


class Piece:
    """Основная конструкция фигуры"""

    def __init__(self, color):
        self.color: WHITE | BLACK = color

    def get_color(self) -> int:
        """Вернуть цвет фигуры"""
        return self.color

    def can_move(self, board, row, col, row1, col1) -> bool:
        """Проверка может ли фигура походить в данное поле"""

        # Неправильные координаты
        if not correct_cords(row1, col1) or not correct_cords(row, col):
            return False

        # Сейчас ход у другого игрока
        if board.current_player_color() != self.get_color():
            return False

        # Фигура ходит в клетку, где стоит фигура такого же цвета
        if board.get_piece(row1, col1) is not None and board.get_piece(row1, col1).get_color() == self.get_color():
            return False

        # нельзя пойти в ту же клетку
        if row == row1 and col == col1:
            return False

        return True

    def can_attack(self, board, row, col, row1, col1) -> bool:
        """Проверка может ли фигуры атаковать данное поле"""

        # Неправильные координаты
        if not correct_cords(row1, col1) or not correct_cords(row, col):
            return False

        # Сейчас ход у другого игрока
        if board.current_player_color() != self.get_color():
            return False

        # нельзя пойти в ту же клетку
        if row == row1 and col == col1:
            return False

        # Фигура не может атаковать клетку, где стоит фигура такого же цвета
        if board.get_piece(row1, col1) is not None and board.get_piece(row1, col1).get_color() == self.get_color():
            return False

        return True

    def char(self) -> str:
        """Вернуть обозначение фигуры"""
        return self.__class__.__name__[0]

    @staticmethod
    def can_do_any_move(board, row, col):
        """Проверка, может ли фигура сделать хотя бы один ход"""
        for row1 in range(8):
            for col1 in range(8):
                if board.possible_move(row, col, row1, col1):
                    return True

    def __repr__(self):
        return self.char()


class Pawn(Piece):
    """Пешка"""

    def __init__(self, color):
        super().__init__(color)
        self.en_passant = False

    def can_move(self, board, row, col, row1, col1) -> bool:
        """Пешка может ходить только по строкам, а столбец всегда одинаковый"""

        if not super().can_move(board, row, col, row1, col1):
            return False

        # Нельзя сменить вертикаль
        if col != col1:
            return False

        # Задаем, вверх или вниз должна двигаться пешка
        if self.get_color() == WHITE:
            direction = 1
            start_row = 1
        else:
            direction = -1
            start_row = 6

        # Правило хода пешки
        if not (row + direction == row1 or (row == start_row and row + 2 * direction == row1)):
            return False

        # Фигур на пути пешки не должно быть
        if row + direction == row1 and board.get_piece(row + direction, col) is None:
            self.en_passant = False
            return True

        elif not 0 <= row + 2 * direction <= 7:
            return False

        # Ход с первой клетки на две клетки сразу
        elif all((row + 2 * direction == row1,
                  board.get_piece(row + direction, col) is None,
                  board.get_piece(row + 2 * direction, col) is None)):
            self.add_en_passant()
            return True

    def can_attack(self, board, row, col, row1, col1) -> bool:
        """Пешка берет только по диагонали на 1 клетку впереди себя"""

        if not super().can_attack(board, row, col, row1, col1):
            return False

        direction = 1 if (self.color == WHITE) else -1
        return row + direction == row1 and abs(col - col1) == 1

    def can_make_en_passant(self, board, row, col, row1, col1) -> bool:
        """Взятие на проходе"""
        if self.get_color() == WHITE:
            direction = 1
        else:
            direction = -1

        # Неправильное поле хода
        if not (row + direction == row1 and abs(col - col1) == 1):
            return False

        # по диагонали на 1 клетку вперед не должно быть фигуры,
        # должна быть сбоку пешка, которую можно взять на проходе
        if not isinstance(board.get_piece(row, col1), Pawn) or not (board.get_piece(row1, col1) is None):
            return False

        en_passant_condition = (board.get_piece(row, col1).is_en_passant(),
                                board.get_piece(row, col1).get_color() == opponent(self.color))

        return all(en_passant_condition)

    def is_en_passant(self) -> bool:
        """Проверка возможно ли взять пешку на проходе"""
        return self.en_passant

    def add_en_passant(self) -> None:
        """Добавить пешке возможность быть взятой на проходе"""
        self.en_passant = True

    def remove_en_passant(self) -> None:
        """Снять с пешки возможность быть взятой на проходе"""
        self.en_passant = False


class Rook(Piece):
    """Ладья"""

    def __init__(self, color):
        super().__init__(color)
        self.castle = True

    def can_move(self, board, row, col, row1, col1) -> bool:
        """Нельзя менять обе координаты сразу"""

        if not super().can_move(board, row, col, row1, col1):
            return False

        if row != row1 and col != col1:
            return False

        if row != row1:
            step = 1 if (row1 >= row) else -1
            for r in range(row + step, row1, step):
                # Если на пути по горизонтали есть фигура
                if not (board.get_piece(r, col) is None):
                    return False

        else:
            step = 1 if (col1 >= col) else -1
            for c in range(col + step, col1, step):
                # Если на пути по вертикали есть фигура
                if not (board.get_piece(row, c) is None):
                    return False

        return True

    def can_attack(self, board, row, col, row1, col1) -> bool:
        if not super().can_attack(board, row, col, row1, col1):
            return False

        return self.can_move(board, row, col, row1, col1)

    def can_castle(self) -> bool:
        """Проверка может ли ладья рокироваться"""
        return self.castle

    def remove_castle(self) -> None:
        """Удаление у ладьи возможности рокировки"""
        self.castle = False


class Knight(Piece):
    """Конь"""

    def char(self) -> str:
        return 'N'

    def can_move(self, board, row, col, row1, col1) -> bool:
        """Одна координата коня изменится на 1, другая на 2
        Так как конь ходит прыжком, проверять другие фигуры не нужно"""

        if not super().can_move(board, row, col, row1, col1):
            return False

        if {abs(row - row1), abs(col - col1)} == {1, 2}:
            return True

        return False

    def can_attack(self, board, row, col, row1, col1) -> bool:
        if not super().can_attack(board, row, col, row1, col1):
            return False

        return self.can_move(board, row, col, row1, col1)


class Bishop(Piece):
    """Слон"""

    def can_move(self, board, row, col, row1, col1) -> bool:
        if not super().can_move(board, row, col, row1, col1):
            return False

        if abs(row - row1) != abs(col - col1):
            return False

        # Движение по главной диагонали(от левого верхнего угла к правому нижнему и наоборот)
        if (row - row1) // abs(row - row1) == (col - col1) // abs(col - col1):
            step = 1 if row1 >= row else -1
            for i, j in zip(range(row + step, row1, step), range(col + step, col1, step)):
                # Если на пути есть фигура
                if not (board.get_piece(i, j) is None):
                    return False

        # Движение по побочной диагонали(от правого верхнего угла к левому нижнему и наоборот)
        else:
            step = 1 if (row1 >= row) else -1
            for i, j in zip(range(row + step, row1, step), range(col - step, col1, -step)):
                # Если на пути есть фигура
                if not (board.get_piece(i, j) is None):
                    return False

        return True

    def can_attack(self, board, row, col, row1, col1) -> bool:
        if not super().can_attack(board, row, col, row1, col1):
            return False

        return self.can_move(board, row, col, row1, col1)


class Queen(Piece):
    """Ферзь"""

    def can_move(self, board, row, col, row1, col1) -> bool:
        """Объединение ходов слона и ладьи"""

        if not super().can_move(board, row, col, row1, col1):
            return False

        if row != row1 and col != col1:
            if abs(row - row1) != abs(col - col1):
                return False

            # Движение по главной диагонали(от левого верхнего угла к правому нижнему и наоборот)
            if (row - row1) // abs(row - row1) == (col - col1) // abs(col - col1):
                step = 1 if row1 >= row else -1
                for i, j in zip(range(row + step, row1, step), range(col + step, col1, step)):
                    # Если на пути есть фигура
                    if not (board.get_piece(i, j) is None):
                        return False

            # Движение по побочной диагонали(от правого верхнего угла к левому нижнему и наоборот)
            else:
                step = 1 if (row1 >= row) else -1
                for i, j in zip(range(row + step, row1, step), range(col - step, col1, -step)):
                    # Если на пути есть фигура
                    if not (board.get_piece(i, j) is None):
                        return False

        elif row != row1:
            step = 1 if (row1 >= row) else -1
            for r in range(row + step, row1, step):
                # Если на пути по горизонтали есть фигура
                if not (board.get_piece(r, col) is None):
                    return False

        else:
            step = 1 if (col1 >= col) else -1
            for c in range(col + step, col1, step):
                # Если на пути по вертикали есть фигура
                if not (board.get_piece(row, c) is None):
                    return False

        return True

    def can_attack(self, board, row, col, row1, col1) -> bool:
        if not super().can_attack(board, row, col, row1, col1):
            return False

        return self.can_move(board, row, col, row1, col1)


class King(Piece):
    """Король"""

    def __init__(self, color):
        super().__init__(color)
        self.check = False
        self.castle = True

    def can_move(self, board, row, col, row1, col1) -> bool:
        """Не проверяем, ходит ли король под шах, данная проверка осуществляется в классе Board"""

        if not super().can_move(board, row, col, row1, col1):
            return False

        if not (abs(row - row1) < 2 and abs(col - col1) < 2):
            return False

        return True

    def can_attack(self, board, row, col, row1, col1) -> bool:
        if not super().can_attack(board, row, col, row1, col1):
            return False

        return self.can_move(board, row, col, row1, col1)

    def add_check(self) -> None:
        """Сделать короля под шахом"""
        self.check = True

    def remove_check(self) -> None:
        """Убрать с короля шах"""
        self.check = False

    def is_under_check(self) -> bool:
        """Вернуть, находится ли король под шахом"""
        return self.check

    def can_castle(self) -> bool:
        """Проверка может ли король рокироваться"""
        if self.is_under_check():
            return False  # Король под шахом

        return self.castle

    def remove_castle(self) -> None:
        """Удаление у короля возможности рокировки"""
        self.castle = False
