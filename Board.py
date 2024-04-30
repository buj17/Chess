from Pieces import Piece, Pawn, Rook, Knight, Bishop, Queen, King
from colors import WHITE, BLACK, opponent


class Board:
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

    def cell(self, row, col):
        """Возвращает строку из двух символов. Если в клетке (row, col)
                находится фигура, символы цвета и фигуры. Если клетка пуста,
                то два пробела."""
        piece: Piece | None = self.field[row][col]
        if piece is None:
            return '  '
        c = 'w' if piece.get_color() == WHITE else 'b'
        return c + piece.char()

    def current_player_color(self):
        """Вернуть цвет игрока, который сейчас ходит"""
        return self.color

    def possible_move(self, row, col, row1, col1):
        """Возвращает, возможно ли сделать ход, без изменений в доске"""

        if self.end:
            return None

        piece: Piece | None = self.field[row][col]

        if piece is None:
            return False  # нельзя пойти без фигуры

        if piece.get_color() != self.color:
            return False  # игрок ходит не своим цветом

        if self.cancel_move(row, col, row1, col1):
            return False

        if isinstance(piece, Pawn):
            piece: Pawn

            if piece.make_en_passant(self, row, col, row1, col1):
                return True

            elif (piece.can_attack(self, row, col, row1, col1) and
                  self.get_piece(row1, col1) is not None or
                  piece.can_move(self, row, col, row1, col1)):
                return True

            else:
                return False

        if isinstance(piece, King):
            piece: King
            if not piece.can_move(self, row, col, row1, col1):
                return False
            else:
                return True

        piece: Queen | Rook | Knight | Bishop

        if self.get_piece(row1, col1) is None:
            if not piece.can_move(self, row, col, row1, col1):
                return False  # неправильный ход

        elif self.field[row1][col1].get_color() == opponent(piece.get_color()):
            if not piece.can_attack(self, row, col, row1, col1):
                return False

        else:
            return False

        return True

    def move_piece(self, row, col, row1, col1):
        """Переместить фигуру из точки (row, col) в точку (row1, col1).
                Если перемещение возможно, метод выполнит его и вернет True.
                Если нет --- вернет False"""

        castling7_condition = ({row, row1} < {0, 7},
                               row == row1,
                               col == 4,
                               col1 == 6)

        castling0_condition = ({row, row1} < {0, 7},
                               row == row1,
                               col == 4,
                               col1 == 2)

        if all(castling7_condition):
            if self.castling7():
                return True

        if all(castling0_condition):
            if self.castling0():
                return True

        if not self.possible_move(row, col, row1, col1):
            return False

        piece: Piece = self.field[row][col]

        self.field[row][col] = None  # Снять фигуру.
        self.field[row1][col1] = piece  # Поставить на новое место.
        self.update()

        # Если походила ладья или король, удаляем возможность рокироваться
        if isinstance(piece, (King, Rook)):
            piece: King | Rook
            piece.remove_castle()

        return True

    def is_under_attack(self, row, col, color):
        """Проверка на то, что как минимум одна фигура цвета color может атаковать данную клетку"""
        for i, lst in enumerate(self.field):
            for j, element in enumerate(lst):
                element: Piece
                if i == row and j == col or self.get_piece(i, j) is None:
                    continue
                if element.can_attack(self, i, j, row, col) and color == element.get_color():
                    return True
        return False

    def get_piece(self, row, col) -> Piece | None:
        """Вернуть клетку с координатами row col"""
        return self.field[row][col]

    def update(self):
        """Удаление после хода возможности в дальнейшем взять пешку на проходе и проверка появления шахов"""
        for i, lst in enumerate(self.field):
            for j, element in enumerate(lst):
                if isinstance(element, Pawn) and self.color == opponent(element.get_color()):
                    element.remove_en_passant()
                    self.field[i][j] = element

        self.scan_checks()
        self.checkmate_on_board()
        self.color = opponent(self.current_player_color())

    def move_and_promote_pawn(self, row, col, row1, col1, char):
        """Превращение пешки"""
        pieces = {'Q': Queen, 'N': Knight, 'R': Rook, 'B': Bishop}
        if char not in pieces:
            return False

        if (self.get_piece(row1, col1) is not None and
                self.get_piece(row, col).get_color() == self.get_piece(row1, col1).get_color()):
            return False

        if not isinstance(self.get_piece(row, col), Pawn):
            return False

        if self.cancel_move(row, col, row1, col1):
            return False

        if self.possible_move(row, col, row1, col1):
            self.field[row1][col1] = pieces[char](self.get_piece(row, col).get_color())
            self.field[row][col] = None

            self.update()

            return True

        return False

    def possible_castling0(self):
        """Возвращает, возможно ли выполнить длинную рокировку"""
        if self.end:
            return None

        row = 0 if self.current_player_color() == WHITE else 7
        rook: Rook | None = self.get_piece(row, 0)
        king: King | None = self.get_piece(row, 4)

        # на 0 вертикали нет ладьи или она не может рокироваться
        if not isinstance(rook, Rook) or not rook.can_castle():
            return False

        # на 4 вертикали нет короля или он не может рокироваться
        if not isinstance(king, King) or not king.can_castle():
            return False

        # Между королем и ладьей не должно быть фигур, и поля не должны быть атакованы
        conditions = (self.get_piece(row, 1) is None,
                      self.get_piece(row, 2) is None,
                      self.get_piece(row, 3) is None,
                      not self.is_under_attack(row, 1, opponent(self.current_player_color())),
                      not self.is_under_attack(row, 2, opponent(self.current_player_color())),
                      not self.is_under_attack(row, 3, opponent(self.current_player_color())),
                      not self.is_under_attack(row, 4, opponent(self.current_player_color())))

        if not all(conditions):
            return False

        return True

    def castling0(self):
        """Рокировка на ферзевом фланге"""
        if not self.possible_castling0():
            return False

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

        return True

    def possible_castling7(self):
        """Возвращает, возможно ли выполнить короткую рокировку"""
        if self.end:
            return None

        row = 0 if self.current_player_color() == WHITE else 7
        rook: Rook | None = self.get_piece(row, 7)
        king: King | None = self.get_piece(row, 4)

        # на 7 вертикали нет ладьи или она не может рокироваться
        if not isinstance(rook, Rook) or not rook.can_castle():
            return False

        # на 4 вертикали нет короля или он не может рокироваться
        if not isinstance(king, King) or not king.can_castle():
            return False

        # Между королем и ладьей не должно быть фигур, и поля не должны быть атакованы
        conditions = (self.get_piece(row, 5) is None,
                      self.get_piece(row, 6) is None,
                      not self.is_under_attack(row, 4, opponent(self.current_player_color())),
                      not self.is_under_attack(row, 5, opponent(self.current_player_color())),
                      not self.is_under_attack(row, 6, opponent(self.current_player_color()))
                      )

        if not all(conditions):
            return False

        return True

    def castling7(self):
        """Рокировка на королевском фланге"""
        if not self.possible_castling7():
            return False

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

        return True

    def check_on_board(self):
        """Проверка на то, находится ли король цвета ходящего игрока под шахом"""
        for i, lst in enumerate(self.field):
            for j, element in enumerate(lst):
                if isinstance(element, King):
                    element: King

                    if element.is_under_check() and element.get_color() == self.current_player_color():
                        return True

        return False

    def scan_checks(self):
        """Наложить на короля шах, если он появляется после хода, и наоборот"""
        for i, lst in enumerate(self.field):
            for j, element in enumerate(lst):
                if isinstance(element, King):
                    element: King

                    # Условие для наложения шаха на короля противника
                    condition1 = (element.get_color() == opponent(self.current_player_color()),
                                  self.is_under_attack(i, j, self.current_player_color()))

                    # Условие для снятия шаха со своего короля
                    condition2 = (element.get_color() == self.current_player_color(),
                                  not self.is_under_attack(i, j, opponent(self.current_player_color())))

                    # Условие для наложения шаха на своего короля
                    # Нужно, чтобы проверять возможность хода
                    condition3 = (element.get_color() == self.current_player_color(),
                                  self.is_under_attack(i, j, opponent(self.current_player_color())))

                    if all(condition1):
                        element.add_check()

                    elif all(condition2):
                        element.remove_check()

                    elif all(condition3):
                        element.add_check()

    def checkmate_on_board(self):
        """Проверка появления мата после хода. Если мат обнаружен, игра заканчивается"""
        for i, lst in enumerate(self.field):
            for j, element in enumerate(lst):
                if isinstance(element, King):
                    element: King

                    if element.is_under_check() and element.get_color() == opponent(self.current_player_color()):
                        moves = (element.can_move(self, i, j, i + 1, j),
                                 element.can_move(self, i, j, i - 1, j),
                                 element.can_move(self, i, j, i, j + 1),
                                 element.can_move(self, i, j, i, j - 1),
                                 element.can_move(self, i, j, i + 1, j + 1),
                                 element.can_move(self, i, j, i + 1, j - 1),
                                 element.can_move(self, i, j, i - 1, j + 1),
                                 element.can_move(self, i, j, i - 1, j - 1))
                        if any(moves):
                            return False
                        else:
                            self.end = True
                            return True

    def cancel_move(self, row, col, row1, col1):
        """Отменить ход, если король ходящего игрока попадает или остается под шахом"""
        piece: Piece = self.get_piece(row, col)
        piece1: Piece | None = self.get_piece(row1, col1)

        self.field[row][col] = None
        self.field[row1][col1] = piece
        self.scan_checks()

        if self.check_on_board():
            self.field[row][col] = piece
            self.field[row1][col1] = piece1
            return True

        self.field[row][col] = piece
        self.field[row1][col1] = piece1
        return False

    def game_over(self):
        """Вернуть, закончилась ли игра"""
        return self.end

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
