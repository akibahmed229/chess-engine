"""
This is our main driver file. It will be responsible for handling user input and displaying the current GameState object.
"""

import pygame as p
import ChessEngine

p.init()

WIDTH = HEIGHT = 512  # 400 is another option
DIMENSION = 8  # dimensions of a chess board are 8x8
SQ_SIZE = HEIGHT // DIMENSION  # size of each square on the chess board
MAX_FPS = 30  # for animations later on
IMAGES = {}

"""
Initialize a global dictionary of images. This will be called exactly once in the main.
"""


def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        try:
            IMAGES[piece] = p.transform.scale(
                p.image.load(f"images/{piece}.bmp"), (SQ_SIZE, SQ_SIZE)
            )
        except p.error as e:
            print("Error loading image:", e)
    # Note: we can access an image by saying 'IMAGES['wp']'


"""
The main driver for our code. This will handle user input and updating the graphics.
"""


def main():
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made

    loadImages()  # only do this once, before the while loop
    running = True
    sqSelected = ()  # no square is selected, keep track of the last click of the user (tuple: (row, col))
    playerClicks = []  # keep track of player clicks (two tuples: [(6, 4), (4, 4)])
    while running:
        for (
            event
        ) in (
            p.event.get()
        ):  # event.get() returns a list of all the events that have happened since the last time it was called
            if event.type == p.QUIT:
                running = False

            # mouse handler
            elif event.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x, y) location of mouse
                col = location[0] // SQ_SIZE  # [0] is the x coordinate
                row = location[1] // SQ_SIZE  # [1] is the y coordinate

                if sqSelected == (row, col):  # the user clicked the same square twice
                    sqSelected = ()  # deselect
                    playerClicks = []  # clear player playerClicks
                else:
                    sqSelected = (row, col)
                    playerClicks.append(
                        sqSelected
                    )  # append for both 1st and 2nd clicks

                if len(playerClicks) == 2:  # after 2nd clicks
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())

                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade = True

                        sqSelected = ()  # reset user playerClicks
                        playerClicks = []  # reset user playerClicks
                    else:
                        playerClicks = [
                            sqSelected
                        ]  # if the user clicks on the same square twice, we want to reset the playerClicks list to just the last click

            # key handler
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


"""
Responsible for all the graphics within a current game state.
"""


def drawGameState(screen, gs):
    drawBoard(screen)  # draw squares on the board
    # add in piece highlighting or move suggestions (later)
    drawPieces(screen, gs.board)  # draw pieces on top of those squares


"""
Draw the squares on the board. The top left square is always light.
"""


def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]

    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(
                screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            )


"""
Draw the pieces on the board using the current GameState.board
"""


def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":  # not empty squares
                screen.blit(
                    IMAGES[piece],
                    p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE),
                )


if __name__ == "__main__":
    main()
