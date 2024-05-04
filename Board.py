"""При проектировании работы доски будем опираться на следующие правила:
1. Каждый ход в первую должен проверяться на то, может ли ходить так фигура
2. Каждый ход во вторую очередь должен проверяться на то, подставляется король под шах
(Данный порядок важен, т.к. если происходит нелегальный ход, но король защищается от шаха,
то будут появляться баги)
3. До передачи хода можно только проверить, поставили ли мы шах противнику,
все остальные изменения должны проводиться строго после передачи хода
(Данный порядок также важен из-за специфичности работы методов,
они не могут правильно проверять доску до и после передачи хода)
4. При проверке легальности хода, создается копия доски во избежание изменений в основной доске
"""
from copy import deepcopy

from Pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King
from colors import WHITE, BLACK, opponent, correct_cords


class Board:
    """Доска хранит информацию о положении фигур и контролирует игровой процесс"""
    def __init__(self):

        self.color = WHITE
        self.field: list[list[None | Piece]] = [[None] * 8 for _ in range(8)]

        self.field[0] = [Rook(WHITE), Knight(WHITE), Bishop(WHITE), Queen(WHITE),
                         King(WHITE), Bishop(WHITE), Knight(WHITE), Rook(WHITE)]

        for i in range(8):
            self.field[1][i] = Pawn(WHITE)

        for i in range(8):
            self.field[6][i] = Pawn(BLACK)

        self.field[7] = [Rook(BLACK), Knight(BLACK), Bishop(BLACK), Queen(BLACK),
                         King(BLACK), Bishop(BLACK), Knight(BLACK), Rook(BLACK)]

        self.end = False
        self.stalemate = False
        self.winner = None

    def __str__(self):
        res = ['     +----+----+----+----+----+----+----+----+']
        for row in range(7, -1, -1):
            res.append('  ' + str(row) + '  ')
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

    def get_piece(self, row, col) -> Piece | None:
        """Вернуть клетку с координатами row col"""
        return self.field[row][col]

    def current_player_color(self):
        """Вернуть цвет игрока, который сейчас ходит"""
        return self.color

    def cell(self, row, col):
        """Возвращает строку из двух символов. Если в клетке (row, col)
                находится фигура, символы цвета и фигуры. Если клетка пуста,
                то два пробела."""
        piece: Piece | None = self.field[row][col]
        if piece is None:
            return '  '
        c = 'w' if piece.get_color() == WHITE else 'b'
        return c + piece.char()

    def game_over(self) -> bool:
        """Вернуть, закончилась ли игра"""
        return self.end

    def get_winner(self) -> None | int:
        """Вернуть победителя в партии"""
        return self.winner

    def end_by_stalemate(self) -> bool:
        """Вернуть, закончилась ли игра патом"""
        return self.stalemate

    def remove_en_passant(self) -> None:
        """После передачи хода с пешек удаляется возможность быть взятыми на проходе"""
        for row in range(8):
            for col in range(8):
                piece: Piece | None = self.get_piece(row, col)

                if not isinstance(piece, Pawn):
                    continue

                piece: Pawn

                if self.current_player_color() == piece.get_color():
                    piece.remove_en_passant()

    def update(self) -> None:
        """Обновление доски: С пешек снимается возможность быть взятой на проходе;
        Проверяется появление шаха после хода;
        Проверяется, закончилась ли игра;
        Все действия проводятся строго после передачи хода, ход передается в первую очередь
        Исключение: Проверка, получил ли шах игрок, которому переходит ход, происходит до передачи хода"""
        self.add_check_to_opponent_player()
        self.color = opponent(self.color)
        self.update_check_for_resembled_player()
        self.update_game_over()
        self.remove_en_passant()

    def move_piece(self, row, col, row1, col1) -> None:
        """Перемещает фигуру из клетки (row, col) в клетку (row1, col1), если это возможно"""

        # Если игрок передвинул короля на две клетки по горизонтали, будет предпринята попытка рокировки
        castling7_condition = ({row, row1} < {0, 7},
                               row == row1,
                               col == 4,
                               col1 == 6)

        castling0_condition = ({row, row1} < {0, 7},
                               row == row1,
                               col == 4,
                               col1 == 2)

        if all(castling7_condition):
            self.castling7()

        if all(castling0_condition):
            self.castling0()

        if not self.possible_move(row, col, row1, col1):
            return None

        piece: Piece = self.field[row][col]

        if isinstance(piece, Pawn):
            piece: Pawn
            if piece.can_make_en_passant(self, row, col, row1, col1):
                if not (self.player_checks_himself(row, col, row1, col1)):
                    self.field[row][col] = None
                    self.field[row1][col1] = piece
                    self.field[row][col1] = None
                    self.update()
                return None
            elif abs(row - row1) == 2:
                piece.add_en_passant()

        self.field[row][col] = None  # Снять фигуру.
        self.field[row1][col1] = piece  # Поставить на новое место.

        # Если походила ладья или король, удаляем возможность рокироваться
        if isinstance(piece, (King, Rook)):
            piece: King | Rook
            piece.remove_castle()

        self.update()

    def possible_move(self, row, col, row1, col1) -> bool:
        """Возвращает, возможно ли сделать ход из клетки (row, col) в клетку (row1, col1)"""

        if self.game_over():
            return False  # Игра уже закончилась

        if not correct_cords(row, col) or not correct_cords(row1, col1):
            return False  # Неправильные координаты

        board_copy = self.get_full_copy()

        piece: Piece | None = board_copy.field[row][col]
        if piece is None:
            return False  # нельзя пойти без фигуры

        if piece.get_color() != board_copy.color:
            return False  # игрок ходит не своим цветом

        target_cell = board_copy.get_piece(row1, col1)
        if not (target_cell is None) and target_cell.get_color() == board_copy.current_player_color():
            return False  # игрок пытается взять фигуру своего цвета

        if isinstance(piece, Pawn):
            piece: Pawn
            if piece.can_make_en_passant(board_copy, row, col, row1, col1):
                if board_copy.player_checks_himself(row, col, row1, col1):
                    return False  # игрок подставляет своего короля под шах
                else:
                    return True

        if not piece.can_move(board_copy, row, col, row1, col1) and board_copy.get_piece(row1, col1) is None:
            return False  # фигура не может пойти по своему правилу

        elif not piece.can_attack(board_copy, row, col, row1, col1) and not (board_copy.get_piece(row1, col1) is None):
            return False  # фигура не может атаковать по своему правилу

        if board_copy.player_checks_himself(row, col, row1, col1):
            return False  # игрок подставляет своего короля под шах

        return True

    def move_and_promote_pawn(self, row, col, row1, col1, char) -> None:
        """Превращение пешки"""

        promotes = {'Q': Queen, 'N': Knight, 'R': Rook, 'B': Bishop}
        if char not in promotes:
            return None  # Выбрана неправильная фигура для превращения

        if not self.possible_move(row, col, row1, col1):
            return None  # Невозможный ход

        self.field[row1][col1] = promotes[char](self.get_piece(row, col).get_color())
        self.field[row][col] = None
        self.update()

    def is_under_attack(self, row1, col1) -> bool:
        """Проверка на то, что как минимум одна фигура цвета color может атаковать данную клетку"""
        # (Так как мы условились, что фигура не может атаковать в свой ход, то параметр color утратил смысл)
        for row in range(8):
            for col in range(8):

                if row == row1 and col == col1:
                    continue

                piece = self.get_piece(row, col)

                if piece is None:
                    continue  # В данной клетке нет фигуры

                if piece.can_attack(self, row, col, row1, col1):
                    return True

        return False

    def possible_castling0(self) -> bool:
        """Возвращает, возможно ли выполнить длинную рокировку"""
        if self.game_over():
            return False

        board_copy = self.get_full_copy()

        row = 0 if board_copy.current_player_color() == WHITE else 7
        rook: Rook | None = board_copy.get_piece(row, 0)
        king: King | None = board_copy.get_piece(row, 4)

        # на 0 вертикали нет ладьи или она не может рокироваться
        if not isinstance(rook, Rook) or not rook.can_castle():
            return False

        # на 4 вертикали нет короля или он не может рокироваться
        if not isinstance(king, King) or not king.can_castle():
            return False

        board_copy.color = opponent(board_copy.color)
        # Между королем и ладьей не должно быть фигур, и поля не должны быть атакованы
        conditions = (board_copy.get_piece(row, 1) is None,
                      board_copy.get_piece(row, 2) is None,
                      board_copy.get_piece(row, 3) is None,
                      not board_copy.is_under_attack(row, 1),
                      not board_copy.is_under_attack(row, 2),
                      not board_copy.is_under_attack(row, 3))

        if not all(conditions):
            return False

        return True

    def castling0(self) -> None:
        """Рокировка на ферзевом фланге"""
        if not self.possible_castling0():
            return None

        row = 0 if self.current_player_color() == WHITE else 7
        rook: Rook | None = self.get_piece(row, 0)
        king: King | None = self.get_piece(row, 4)

        self.field[row][4] = None
        self.field[row][0] = None
        self.field[row][2] = king
        self.field[row][3] = rook

        king.remove_castle()
        rook.remove_castle()
        self.update()

    def possible_castling7(self) -> bool:
        """Возвращает, возможно ли выполнить короткую рокировку"""
        if self.game_over():
            return False

        board_copy = self.get_full_copy()

        row = 0 if board_copy.current_player_color() == WHITE else 7
        rook: Rook | None = board_copy.get_piece(row, 7)
        king: King | None = board_copy.get_piece(row, 4)

        # на 7 вертикали нет ладьи или она не может рокироваться
        if not isinstance(rook, Rook) or not rook.can_castle():
            return False

        # на 4 вертикали нет короля или он не может рокироваться
        if not isinstance(king, King) or not king.can_castle():
            return False

        board_copy.color = opponent(board_copy.color)
        # Между королем и ладьей не должно быть фигур, и поля не должны быть атакованы
        conditions = (board_copy.get_piece(row, 5) is None,
                      board_copy.get_piece(row, 6) is None,
                      not board_copy.is_under_attack(row, 5),
                      not board_copy.is_under_attack(row, 6))

        if not all(conditions):
            return False

        return True

    def castling7(self) -> None:
        """Рокировка на королевском фланге"""
        if not self.possible_castling7():
            return None

        row = 0 if self.current_player_color() == WHITE else 7
        rook: Rook | None = self.get_piece(row, 7)
        king: King | None = self.get_piece(row, 4)

        self.field[row][4] = None
        self.field[row][7] = None
        self.field[row][6] = king
        self.field[row][5] = rook
        king.remove_castle()
        rook.remove_castle()

        self.update()

    def add_check_to_opponent_player(self) -> None:
        """Наложить шах на игрока, которому после хода он переходит
        Примечание: Метод должен выполняться до передачи хода"""
        for row in range(8):
            for col in range(8):
                piece: Piece | None = self.get_piece(row, col)

                if not isinstance(piece, King):
                    continue

                piece: King

                if piece.get_color() == self.current_player_color():
                    continue

                # После того как мы нашли клетку, где стоит король нужного цвета, проверяем, атакован ли он
                if self.is_under_attack(row, col):
                    piece.add_check()

                # Так как король нужного цвета уже был найден, дальнейшая работа функции не имеет смысла
                return None

    def update_check_for_resembled_player(self) -> None:
        """Обновить шах у игрока, который передал ход
        Примечание: Метод должен выполняться после передачи хода"""

        for row in range(8):
            for col in range(8):
                piece: Piece | None = self.get_piece(row, col)

                if not isinstance(piece, King):
                    continue

                piece: King

                if piece.get_color() == self.current_player_color():
                    continue

                # На этом моменте найден король нужного цвета
                if self.is_under_attack(row, col) and not piece.is_under_check():
                    # Если игрок подставил своего короля под шах, добавляем шах
                    piece.add_check()
                elif not self.is_under_attack(row, col) and piece.is_under_check():
                    # Если игрок убрал своего короля из-под шаха, удаляем шах
                    piece.remove_check()

                # Если король был под шахом и под ним остался, метод ничего не изменит, король так и останется под шахом
                # Так как король нужного цвета уже был найден, дальнейшая работа функции не имеет смысла
                return None

    def check_on_board(self) -> bool:
        """Проверка, находится ли король игрока, которому перешел ход, под шахом"""
        for row in range(8):
            for col in range(8):
                piece: Piece | None = self.get_piece(row, col)

                if not isinstance(piece, King):
                    continue

                piece: King

                if piece.get_color() == opponent(self.current_player_color()):
                    continue

                if piece.is_under_check():
                    return True
                else:
                    return False

    def player_checks_himself(self, row, col, row1, col1) -> bool:
        """Проверка, подставляет ли игрок своим ходом своего короля под шах
        Примечание: в данный метод должен передаваться ход, который фигура может сделать по своему правилу"""

        # Сохраняем старое поле и делаем ход

        piece: Piece | None = self.get_piece(row, col)

        if piece is None:
            return False

        new_board = self.get_full_copy()

        new_board.field[row1][col1] = piece
        new_board.field[row][col] = None
        new_board.color = opponent(new_board.color)
        new_board.update_check_for_resembled_player()

        for row2 in range(8):
            for col2 in range(8):
                piece: Piece | None = new_board.get_piece(row2, col2)

                if not isinstance(piece, King):
                    continue

                piece: King

                if piece.get_color() == new_board.current_player_color():
                    continue

                # Проверяем, находится ли король игрока, передавшего ход, под шахом в новом поле
                if piece.is_under_check():
                    return True
                else:
                    return False

    def current_player_can_do_any_move(self) -> bool:
        """Проверка, может ли игрок, которому перешел ход, сделать его"""
        board_copy = self.get_full_copy()
        for row in range(8):
            for col in range(8):
                piece = board_copy.get_piece(row, col)

                if piece is None:
                    continue

                if piece.get_color() != board_copy.current_player_color():
                    continue

                if piece.can_do_any_move(board_copy, row, col):
                    return True

        return False

    def update_game_over(self) -> None:
        """Если после передачи хода игра по правилам заканчивается, объявляем победителя или пат"""

        if self.current_player_can_do_any_move():
            return None  # У игрока еще есть допустимые ходы

        # Объявляем конец игры вместе с победителем или патом
        self.end = True
        if self.check_on_board():
            self.winner = opponent(self.current_player_color())
        else:
            self.stalemate = True

    def get_full_copy(self):
        """Возвращает копию доски"""
        new_board = Board()
        for row in range(8):
            for col in range(8):
                new_board.field[row][col] = deepcopy(self.get_piece(row, col))
        new_board.color = deepcopy(self.color)
        new_board.end = deepcopy(self.end)
        new_board.stalemate = deepcopy(self.stalemate)
        new_board.winner = deepcopy(self.winner)
        return new_board
