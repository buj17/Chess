from Board import Board
from colors import WHITE


def main():
    # Создаём шахматную доску
    board = Board()
    # Цикл ввода команд игроков
    while True:
        # Выводим положение фигур на доске
        print(board)
        # Подсказка по командам
        print('Команды:')
        print('    exit                               -- выход')
        print('    move <row> <col> <row1> <col1>     -- ход из клетки (row, col)')
        print('                                          в клетку (row1, col1)')
        print('    castling7                          -- короткая рокировка')
        print('    castling0                          -- длинная рокировка')
        print('    move_and_promote_pawn <row> <col> <row1> <col1> <char> -- превращение пешки')
        print('    "Q" - ферзь, "R" - ладья, "N" - конь, "B" - слон')
        # Выводим приглашение игроку нужного цвета
        if board.current_player_color() == WHITE:
            print('Ход белых:')
        else:
            print('Ход черных:')
        command = input()
        if command == 'exit':
            break

        if command == 'castling7':
            if board.castling7():
                print('Ход успешен')
            else:
                print('Рокировка невозможна')
            continue

        if command == 'castling0':
            if board.castling0():
                print('Ход успешен')
            else:
                print('Рокировка невозможна')
            continue

        command = command.split()

        if command[0] == 'move_and_promote_pawn':
            try:
                row, col, row1, col1 = map(int, command[1:-1])
                char = command[-1]
            except ValueError:
                print('Ошибка при вводе данных')
            else:
                if board.move_and_promote_pawn(row, col, row1, col1, char):
                    print('Ход успешен')
                else:
                    print('Неправильные координаты или фигура превращения')

        elif command[0] == 'move':

            try:
                row, col, row1, col1 = map(int, command.split()[1:])
            except ValueError:
                print('Ошибка при вводе команды')
            else:
                if board.move_piece(row, col, row1, col1):
                    print('Ход успешен')
                else:
                    print('Координаты некорректны! Попробуйте другой ход!')

        else:
            print('Несуществующая команда')

        if board.game_over():
            print(board)
            print('Игра закончена')
            break


if __name__ == '__main__':
    main()
