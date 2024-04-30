import tkinter as tk

from Board import Board
from Pieces import Piece, Pawn
from colors import WHITE, BLACK

images = {(WHITE, 'P'): 'WhitePawn.png',
          (WHITE, 'R'): 'WhiteRook.png',
          (WHITE, 'N'): 'WhiteKnight.png',
          (WHITE, 'B'): 'WhiteBishop.png',
          (WHITE, 'Q'): 'WhiteQueen.png',
          (WHITE, 'K'): 'WhiteKing.png',
          (BLACK, 'P'): 'BlackPawn.png',
          (BLACK, 'R'): 'BlackRook.png',
          (BLACK, 'N'): 'BlackKnight.png',
          (BLACK, 'B'): 'BlackBishop.png',
          (BLACK, 'Q'): 'BlackQueen.png',
          (BLACK, 'K'): 'BlackKing.png'}


class TkPiece:
    def __init__(self, canvas: tk.Canvas, piece: Piece, row, col):
        self.piece = piece
        self.image = tk.PhotoImage(file=images[(self.piece.color, self.piece.char())])
        self.row = row
        self.col = col
        self.canvas = canvas
        self.piece_id = self.create_image_on_canvas()

    def create_image_on_canvas(self):
        """Создаем изображение на холсте self.canvas и возвращаем идентификатор данного изображения"""
        x, y = self.col * 75 + 37.5, (7 - self.row) * 75 + 37.5
        return self.canvas.create_image((x, y), image=self.image)

    def get_piece(self):
        """Возвращает фигуру"""
        return self.piece


class TkBoard:
    def __init__(self):
        self.board = Board()

        self.master = tk.Tk()
        self.master.geometry('600x600')
        self.master.resizable(False, False)
        self.master.title('Chess')

        self.canvas = tk.Canvas(self.master, height=600, width=600)

        self.board_image = tk.PhotoImage(file='Board.png')
        self.wQ = tk.PhotoImage(file=images[(WHITE, 'Q')])
        self.wR = tk.PhotoImage(file=images[(WHITE, 'R')])
        self.wB = tk.PhotoImage(file=images[(WHITE, 'B')])
        self.wN = tk.PhotoImage(file=images[(WHITE, 'N')])
        self.bQ = tk.PhotoImage(file=images[(BLACK, 'Q')])
        self.bR = tk.PhotoImage(file=images[(BLACK, 'R')])
        self.bB = tk.PhotoImage(file=images[(BLACK, 'B')])
        self.bN = tk.PhotoImage(file=images[(BLACK, 'N')])

        self.canvas.create_image((0, 0), image=self.board_image, anchor='nw')

        self.grabbed = None

        self.promote_image = None
        self.promote_image_col = None
        self.promote_image_row = None
        self.chosen_promote = None
        self.promote_cords = None

        self.pieces: dict[int: TkPiece] = {}

        self.cords: dict[tuple[int, int]: int] = {}

        self.update_board()

    def get_grabbed_piece(self) -> None | Piece | Pawn:
        """Вернуть фигуру, которая взята"""
        if self.grabbed is None:
            return None

        return self.board.get_piece(self.get_grabbed_piece_row(), self.get_grabbed_piece_col())

    def get_grabbed_piece_row(self):
        """Вернуть строку, в котором стоит взятая фигура"""
        if self.grabbed is None:
            return None

        return self.pieces[self.grabbed].row

    def get_grabbed_piece_col(self):
        """Вернуть столбец, в котором стоит взятая фигура"""
        if self.grabbed is None:
            return None

        return self.pieces[self.grabbed].col

    def grab_piece(self, event: tk.Event):
        """Когда пользователь нажимает ЛКМ, определяются координаты клетки, в которой произошел клик
        Если в клетке есть фигура, она будет двигаться за курсором"""
        row, col = 7 - event.y // 75, event.x // 75
        self.grabbed: None | int = self.cords.get((row, col))
        if self.grabbed:
            piece: TkPiece = self.pieces[self.grabbed]
            if piece.get_piece().get_color() != self.board.current_player_color():
                self.grabbed = None

    def move_piece(self, event: tk.Event):
        """Если пользователь схватил фигуру мышкой, то она будет передвигаться за курсором"""
        if self.grabbed is None:
            return None

        self.canvas.coords(self.grabbed, (event.x, event.y))

    def drop_piece(self, event: tk.Event):
        """После того как пользователь отпускает ЛКМ, ход передается в self.board
        Если ход успешен, рисуется новое положение фигур
        Если ход невозможен, фигура возвращается на свое место"""
        if self.grabbed is None:
            return None

        row, col = 7 - event.y // 75, event.x // 75

        if isinstance(self.get_grabbed_piece(), Pawn):
            # Проверка, будет ли данный ход превращением пешки
            final_row = 7 if self.board.current_player_color() == WHITE else 0
            pawn_row, pawn_col = self.get_grabbed_piece_row(), self.get_grabbed_piece_col()
            if self.board.possible_move(pawn_row, pawn_col, row, col) and row == final_row:
                self.show_promote_image(row, col)
                self.master.unbind('<Button-1>')
                self.master.bind('<Button-1>', self.choice_promote)
                self.promote_cords = (pawn_row, pawn_col, row, col)
                return None

        if self.board.move_piece(self.get_grabbed_piece_row(), self.get_grabbed_piece_col(), row, col):
            self.update_board()

        else:
            old_cords = (self.pieces[self.grabbed].col * 75 + 37.5, (7 - self.pieces[self.grabbed].row) * 75 + 37.5)
            self.canvas.coords(self.grabbed, old_cords)

    def show_promote_image(self, row, col):
        """Показать картину с вариантами превращения"""

        if col > 3:
            x = 300
        else:
            x = col * 75
        y = (7 - row) * 75

        self.promote_image = self.canvas.create_rectangle((x, y, x + 300, y + 75), fill='#79553d')

        if row == 7:
            self.canvas.create_image((x, y), image=self.wQ, anchor='nw')
            self.canvas.create_image((x + 75, y), image=self.wR, anchor='nw')
            self.canvas.create_image((x + 150, y), image=self.wB, anchor='nw')
            self.canvas.create_image((x + 225, y), image=self.wN, anchor='nw')
        else:
            self.canvas.create_image((x, y), image=self.bQ, anchor='nw')
            self.canvas.create_image((x + 75, y), image=self.bR, anchor='nw')
            self.canvas.create_image((x + 150, y), image=self.bB, anchor='nw')
            self.canvas.create_image((x + 225, y), image=self.bN, anchor='nw')

        self.promote_image_col = x // 75
        self.promote_image_row = 7 - y // 75

    def hide_promote_image(self):
        """Спрятать картину с вариантами превращения"""
        self.promote_image = None
        self.update_board()

    def choice_promote(self, event: tk.Event):
        """После того как пользователь нажимает на определенную фигуру, выполняется превращение
        Если пользователь нажал вне картины, то ход отменяется"""
        row, col = 7 - event.y // 75, event.x // 75
        if row != self.promote_image_row:
            self.hide_promote_image()
            self.master.unbind('<Button-1>')
            self.master.bind('<Button-1>', self.grab_piece)
            return None

        chars = {self.promote_image_col: 'Q',
                 self.promote_image_col + 1: 'R',
                 self.promote_image_col + 2: 'B',
                 self.promote_image_col + 3: 'N'}

        self.chosen_promote = chars.get(col)

        if self.chosen_promote is not None:
            self.board.move_and_promote_pawn(*self.promote_cords + (self.chosen_promote,))

        self.hide_promote_image()
        self.master.unbind('<Button-1>')
        self.master.bind('<Button-1>', self.grab_piece)

    def cancel_move(self, event):
        """Если пользователь нажал ПКМ, то фигура, которую он взял, возвращается на место"""
        if self.grabbed is None:
            return None
        old_cords = (self.pieces[self.grabbed].col * 75 + 37.5, (7 - self.pieces[self.grabbed].row) * 75 + 37.5)
        self.canvas.coords(self.grabbed, old_cords)
        self.grabbed = None

    def update_board(self):
        """После хода рисуется доска с новым положением фигур """
        self.canvas.create_image((0, 0), image=self.board_image, anchor='nw')
        self.pieces = {}
        self.cords = {}
        self.grabbed = None
        for row in range(8):
            for col in range(8):
                if self.board.get_piece(row, col):
                    piece = TkPiece(self.canvas, self.board.get_piece(row, col), row, col)
                    self.pieces[piece.piece_id] = piece
                    self.cords[(row, col)] = piece.piece_id

    def run(self):
        """Запуск программы"""
        self.canvas.pack()
        self.master.bind('<Button-1>', self.grab_piece)
        self.master.bind('<B1-Motion>', self.move_piece)
        self.master.bind('<ButtonRelease-1>', self.drop_piece)
        self.master.bind('<Button-3>', self.cancel_move)
        self.master.mainloop()


if __name__ == "__main__":
    board = TkBoard()
    board.run()
