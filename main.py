import tkinter as tk

from Board import Board
from Pieces import Piece
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

    def move_on_canvas(self, canvas: tk.Canvas, event: tk.Event):
        pass

    def create_image_on_canvas(self):
        x, y = self.col * 75 + 37.5, (7 - self.row) * 75 + 37.5

        return self.canvas.create_image((x, y), image=self.image)


class TkBoard:
    def __init__(self):
        self.board = Board()

        self.master = tk.Tk()
        self.master.geometry('600x600')
        self.master.resizable(False, False)
        self.master.title('Chess')

        self.canvas = tk.Canvas(self.master, height=600, width=600)

        self.board_image = tk.PhotoImage(file='Board.png')
        self.canvas.create_image((0, 0), image=self.board_image, anchor='nw')

        self.grabbed = None

        self.pieces = {}

        self.cords = {}

        self.update_board()

    def grab_piece(self, event: tk.Event):
        row, col = 7 - event.y // 75, event.x // 75
        self.grabbed: None | TkPiece = self.cords.get((row, col))

    def move_piece(self, event: tk.Event):
        if self.grabbed is None:
            return None

        self.canvas.coords(self.grabbed, (event.x, event.y))


    def drop_piece(self, event: tk.Event):
        if self.grabbed is None:
            return None

        row, col = 7 - event.y // 75, event.x // 75

        if self.board.move_piece(self.pieces[self.grabbed].row, self.pieces[self.grabbed].col, row, col):
            self.update_board()
            self.grabbed = None

        else:
            self.canvas.coords(self.grabbed, (self.pieces[self.grabbed].col * 75 + 37.5, (7 - self.pieces[self.grabbed].row) * 75 + 37.5))

    def update_board(self):
        self.pieces = {}
        self.cords = {}
        for row in range(8):
            for col in range(8):
                if self.board.get_piece(row, col):
                    piece = TkPiece(self.canvas, self.board.get_piece(row, col), row, col)
                    self.pieces[piece.piece_id] = piece
                    self.cords[(row, col)] = piece.piece_id

    def run(self):
        self.canvas.pack()
        self.master.bind('<Button-1>', self.grab_piece)
        self.master.bind('<B1-Motion>', self.move_piece)
        self.master.bind('<ButtonRelease-1>', self.drop_piece)
        self.master.mainloop()


board = TkBoard()

board.run()
