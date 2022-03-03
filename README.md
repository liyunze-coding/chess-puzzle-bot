# chess puzzle solving bot

## chess playing bot 2.0 : https://github.com/liyunze-coding/chess-playing-bot-v2

(follow the instructions here)

---

## How it works

This program uses `OpenCV` 's template matching feature. It looks at individual chess pieces from right to left each row, starting from the top left.

When it views an unknown chess piece, it takes confidence value of each template and take the template with the highest confidence value, telling us what chess piece it is.

After identifying all the chess pieces on the board, it gets processed into a chess board (with `python-chess` library)

It then uses `Stockfish` engine (.exe) as a chess engine to generate the best move

After the best move is generated, the program uses math to figure out what coordinates on the desktop the mouse should drag and drop. Using the coordinates, `pyautogui` then executes the mouse input.

---

install requirements via

`pip install -r requirements.txt`

in terminal / command prompt.
