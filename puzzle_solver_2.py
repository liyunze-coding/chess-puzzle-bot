import cv2
import numpy as np
from PIL import ImageGrab
import time
import pyautogui as ptg
import chess
import chess.engine
import asyncio
from glob import glob

'''
Made by Ryan Lee In Zer

This script is specifically designed for https://lichess.org, on Windows 10

PLEASE DO NOT USE THIS SCRIPT FOR RATED GAMES

This script is made for the purpose purely for coding practice and learning image processing,
I do not condone using this script for malicious purposes such as cheating and/or gaining more rating.
I am not responsible for any consequences led by the usage of this script.
I encourage the usage of this bot to play against another bot.
'''

# bounding area of the chess board (top left x, top left y, bottom right x, bottom right y)
board_bbox = (554, 200, 1275, 921)
playing_color_bbox = (1348, 721, 1398, 771)

# 442,924 flip board button

#555,910, 850, 946

# get the board position based on input

piece_map = {
    'black_bishop': 'b',
    'black_king': 'k',
    'black_knight': 'n',
    'black_pawn': 'p',
    'black_queen': 'q',
    'black_rook': 'r',
    'white_bishop': 'B',
    'white_king': 'K',
    'white_knight': 'N',
    'white_pawn': 'P',
    'white_queen': 'Q',
    'white_rook': 'R'
}

chess_piece_templates = []
for filename in glob('piece_templates/*.png'):
    piece_name = filename[16:-6]
    chess_piece_templates.append(
        [piece_name, cv2.imread(filename, 0)])


def capture_image():
    img = ImageGrab.grab(bbox=board_bbox)
    img.save('board.png')
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    return img


def playing_color():
    image = ImageGrab.grab(bbox=playing_color_bbox)
    image = np.array(image)
    white_pixels = np.count_nonzero((image >= [235, 235, 235]).all(axis=2))

    if white_pixels > 500:
        return 'white'
    elif white_pixels == 0:
        return None
    else:
        return 'black'


def check_grid_cells(image):
    length = round((board_bbox[2] - board_bbox[0]) / 8)

    string = ''
    for y in range(8):
        blank_count = 0
        for x in range(8):
            confirm_chess_piece = ''
            cropped = image[y*length:y*length+length, x*length:x*length+length]

            for chess_piece, template in chess_piece_templates:
                res = cv2.matchTemplate(
                    cropped, template, cv2.TM_CCOEFF_NORMED)
                threshold = 0.95
                loc = np.where(res >= threshold)
                if len(list(zip(*loc[::-1]))) >= 1:
                    confirm_chess_piece = chess_piece
            if confirm_chess_piece == '':
                blank_count += 1
            else:
                if blank_count >= 1:
                    string += str(blank_count)
                    blank_count = 0
                string += piece_map[confirm_chess_piece]
        if blank_count >= 1:
            string += str(blank_count)
            blank_count = 0
        if y != 7:
            string += '/'
    return string

# move mouse to the left side of the screen to start


def waiting_to_start():
    while 1:
        if ptg.position()[0] <= 20:
            break
    print('alright let\'s go')

# main function (mainly logic for generating best move)


def play_move(player_color, before, after, is_pawn):
    length = round((board_bbox[2] - board_bbox[0]) / 8)
    before_column = before[0]
    before_row = before[1]

    after_column = after[0]
    after_row = after[1]

    rows = ['8', '7', '6', '5', '4', '3', '2', '1']
    columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    if player_color == "black":
        rows = rows[::-1]
        columns = columns[::-1]

    before_x_index = columns.index(before_column)
    before_y_index = rows.index(before_row)

    after_x_index = columns.index(after_column)
    after_y_index = rows.index(after_row)

    before_x = board_bbox[0] + length//2 + length * before_x_index
    before_y = board_bbox[1] + length//2 + length * before_y_index

    after_x = board_bbox[0] + length//2 + length * after_x_index
    after_y = board_bbox[1] + length//2 + length * after_y_index

    ptg.moveTo(before_x, before_y)
    time.sleep(0.2)
    ptg.dragTo(after_x, after_y, 0.1, button='left')
    if ((after_row == '8' and before_row == '7') or (after_row == '1' and before_row == '2')) and abs(before_x_index - after_x_index) <= 1:
        if is_pawn:
            ptg.click()


async def main():
    transport, engine = await chess.engine.popen_uci("stockfish_14_x64_avx2.exe")
    original_color = None

    waiting_to_start()

    play_as = playing_color()

    # return
    if play_as is None and original_color is None:
        color = input("can't find colour\n(1) white\n(2) black\n")
        waiting_to_start()
        play_as = 'white' if color == '1' else 'black'
    print(play_as)
    original_color = play_as
    # print(playing_color())

    board_image = capture_image()

    ascii_board = check_grid_cells(board_image)

    if play_as == 'white':
        ascii_board += ' w KQkq'
    else:
        ascii_board += ' b KQkq'

    board = chess.Board(ascii_board)
    if play_as == 'black':
        board.apply_transform(chess.flip_vertical)
        board.apply_transform(chess.flip_horizontal)
    print(board)
    while not board.is_game_over():
        result = await engine.play(board, chess.engine.Limit(depth=20))
        ai_move = str(result.move)

        before_pos = ai_move[:2]
        after_pos = ai_move[2:]

        before_piece = board.piece_at(chess.parse_square(before_pos))

        is_pawn = str(before_piece).lower() == 'p'

        play_move(play_as, before_pos, after_pos, is_pawn)
        print(board)

        board.push(result.move)
        time.sleep(1.5)

        play_as = playing_color()
        print(play_as, original_color)

        if play_as is None:
            play_as = original_color
        # elif play_as != original_color:
            #ptg.click(442, 924)

        original_color = play_as

        board_image = capture_image()

        ascii_board = check_grid_cells(board_image)
        if play_as == 'white':
            ascii_board += ' w KQkq'
        else:
            ascii_board += ' b KQkq'
        board = chess.Board(ascii_board)
        if play_as == 'black':
            board.apply_transform(chess.flip_vertical)
            board.apply_transform(chess.flip_horizontal)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(chess.engine.EventLoopPolicy())
    # try:
    asyncio.run(main())
    # except:
    #     ptg.click(1640, 560)
    #     ptg.click(1640, 560)
    #     ptg.click(1560, 600)

    #     ptg.moveTo(0, 200)

    #     subprocess.call(['python', 'lichess_main.py'])
