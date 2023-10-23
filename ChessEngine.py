"""
This class is responsible for storing all the information about the current state of a chess game. It will also be responsible for determining the valid moves at the current state. It will also keep a move log. 
"""


class GameState:
    def __init__(self):
        # Board is an 8x8 2d list, each element of the list has 2 characters.
        # The first character represents the color of the piece, 'black' or 'white'
        # The second character represents the type of the piece, 'King', 'Queen', 'Rook', 'Bishop', 'Knight', or 'Pawn'
        # "--" represents an empty space with no piece.
        self.board = [
            # vertical axis (columns) # horizontal axis (rows)
            #  0     1     2     3     4     5     6     7
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],  # 7
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],  # 6
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # 5
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # 4
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # 3
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # 2
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],  # 1
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],  # 0
            #  a     b     c     d     e     f     g     h
        ]

        self.moveFunctions = {
            "p": self.getPawnMoves,
            "R": self.getRookMoves,
            "N": self.getKnightMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
            "K": self.getKingMoves,
        }

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False

    """
    Takes a Move as a parameter and executes it (this will not work for castling, pawn promotion, and en-passant)
    """

    def makeMove(self, move):
        # Make the move by updating the board and logging the move.
        # It also handles switching player turns and updating king locations.

        self.board[move.startRow][move.startCol] = "--"  # empty the start square
        self.board[move.endRow][
            move.endCol
        ] = move.pieceMoved  # move the piece to the end square
        self.moveLog.append(move)  # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove  # swap players
        # update the king's location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

    """
    Undo the last move made
    """

    def undoMove(self):
        # Undo the last move, restoring the board and player turns.

        if len(self.moveLog) != 0:  # make sure that there is a move to undoMove
            move = self.moveLog.pop()  # remove the last move from the move log
            self.board[move.startRow][
                move.startCol
            ] = move.pieceMoved  # put the piece back
            self.board[move.endRow][
                move.endCol
            ] = move.pieceCaptured  # put the piece back
            self.whiteToMove = not self.whiteToMove  # switch turns back
            # update the king's location if undoMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

    """
    All moves considering checks    
    It evaluates each move's impact on the current game state.
    """

    def getValidMoves(self):
        # 1. generate all possible moves (without considering checks)
        moves = self.getAllPossibleMoves()

        # 2. for each move, make the move
        for i in range(
            len(moves) - 1, -1, -1
        ):  # when removing from a list go backwards through that list
            self.makeMove(moves[i])
            # 3. generate all opponent's moves
            # 4. for each of your opponent's moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove  # switch turns
            if self.inCheck():
                moves.remove(
                    moves[i]
                )  # 5. if they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove  # switch turns back
            self.undoMove()
        if len(moves) == 0:  # either checkmate or staleMate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        return moves

    """
    Determine if the current player is in check  (attacked by the opponent).
    """

    def inCheck(self):
        if (
            self.whiteToMove
        ):  # white's turn to move, check if black can attack the square
            return self.squareUnderAttack(
                self.whiteKingLocation[0], self.whiteKingLocation[1]
            )
        else:  # black's turn to move, check if white can attack the square
            return self.squareUnderAttack(
                self.blackKingLocation[0], self.blackKingLocation[1]
            )

    """
    Determine if the enemy can attack the square row, col
    """

    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove  # switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turn back

        for move in oppMoves:
            if move.endRow == row and move.endCol == col:  # square is under attack
                return True
        return False

    """
    All moves without considering checks
    """

    def getAllPossibleMoves(self):
        # It iterates through the board and calls the appropriate move functions.

        moves = []
        for row in range(len(self.board)):  # number of rows
            for col in range(len(self.board[row])):  # number of cols in given row
                turn = self.board[row][col][0]  # gets the color of the piece
                if (
                    turn == "w"
                    and self.whiteToMove
                    or turn == "b"
                    and not self.whiteToMove
                ):
                    piece = self.board[row][col][1]  # gets the type of the piece
                    # calls the appropriate move function based on piece type
                    self.moveFunctions[piece](row, col, moves)
        return moves

    """
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    """

    def getPawnMoves(self, row, col, moves):
        if self.whiteToMove:  #  white pawn moves
            if self.board[row - 1][col] == "--":  # 1 square pawn advance
                moves.append(Move((row, col), (row - 1, col), self.board))
                if (
                    row == 6 and self.board[row - 2][col] == "--"
                ):  # 2 square pawn advanc
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if col - 1 >= 0:  # captures to the left
                if self.board[row - 1][col - 1][0] == "b":  # enemy piece to capture
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
            if col + 1 <= 7:  # captures to the right
                if self.board[row - 1][col + 1][0] == "b":  # enemy piece to captures
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))

        else:  # black pawn moves
            if self.board[row + 1][col] == "--":  # 1 square pawn advance
                moves.append(Move((row, col), (row + 1, col), self.board))
                if (
                    row == 1 and self.board[row + 2][col] == "--"
                ):  # 2 square pawn advance
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0:  # captures to the left
                if self.board[row + 1][col - 1][0] == "w":  # enemy piece to capture
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
            if col + 1 <= 7:  # captures to the right
                if self.board[row + 1][col + 1][0] == "w":  # enemy piece to capture
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))

            # TODO: add pawn promotion later

    """
        Get all the Rook moves for the rook located at row, col and add these moves to the list
    """

    def getRookMoves(self, row, col, moves):
        # Define the four possible rook movement directions: up, left, down, and right.
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemyColor = (
            "b" if self.whiteToMove else "w"
        )  # Determine the color of the enemy pieces.

        # For each direction (up, left, down, right)
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i  # Calculate the potential ending row.
                endCol = col + d[1] * i  # Calculate the potential ending column.

                # Check if the potential move is within the bounds of the chessboard (8x8).
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][
                        endCol
                    ]  # Get the piece at the potential ending position.

                    if (
                        endPiece == "--"
                    ):  # If the ending position is empty, it's a valid move.
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif (
                        endPiece[0] == enemyColor
                    ):  # If the ending position has an enemy piece, it's a valid move, but stop in this direction.
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else:  # If the ending position has a friendly piece, it's an invalid move, so stop in this direction.
                        break
                else:  # If the potential move is off the chessboard, stop in this direction.
                    break

    """
    Get all the knight moves for the knight located at row, col and add these moves to the list
    """

    def getKnightMoves(self, row, col, moves):
        # Define the possible knight moves relative to its current position.
        knightMoves = (
            (-2, -1),
            (-2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
            (2, -1),
            (2, 1),
        )
        enemyColor = (
            "w" if self.whiteToMove else "b"
        )  # Determine the color of the friendly pieces.

        for m in knightMoves:
            endRow = row + m[0]  # Calculate the potential ending row.
            endCol = col + m[1]  # Calculate the potential ending column.

            # Check if the potential move is within the bounds of the chessboard (8x8).
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][
                    endCol
                ]  # Get the piece at the potential ending position.

                if (
                    endPiece[0] != enemyColor
                ):  # If it's not an enemy piece (empty or friendly), it's a valid move.
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    """
    Get all the bishop moves for the bishop located at row, col and add these moves to the list
    """

    def getBishopMoves(self, row, col, moves):
        # Define the four possible bishop movement directions: up-left, up-right, down-left, and down-right.
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = (
            "b" if self.whiteToMove else "w"
        )  # Determine the color of the enemy pieces.

        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i  # Calculate the potential ending row.
                endCol = col + d[1] * i  # Calculate the potential ending column.

                # Check if the potential move is within the bounds of the chessboard (8x8).
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][
                        endCol
                    ]  # Get the piece at the potential ending position.

                    if (
                        endPiece == "--"
                    ):  # If the ending position is empty, it's a valid move.
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif (
                        endPiece[0] == enemyColor
                    ):  # If the ending position has an enemy piece, it's a valid move, but stop in this direction.
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else:  # If the ending position has a friendly piece, it's an invalid move, so stop in this direction.
                        break
                else:  # If the potential move is off the chessboard, stop in this direction.
                    break

    """
    Get all the queen moves for the queen located at row, col and add these moves to the list
    """

    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    """
    Get all the king moves for the king located at row, col and add these moves to the list
    """

    def getKingMoves(self, row, col, moves):
        # Define the possible king moves, including diagonal and adjacent squares.
        kingMoves = (
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        )
        allyColor = (
            "w" if self.whiteToMove else "b"
        )  # Determine the color of the friendly pieces.

        for i in range(8):
            endRow = row + kingMoves[i][0]  # Calculate the potential ending row.
            endCol = col + kingMoves[i][1]  # Calculate the potential ending column.

            # Check if the potential move is within the bounds of the chessboard (8x8).
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][
                    endCol
                ]  # Get the piece at the potential ending position.

                if (
                    endPiece[0] != allyColor
                ):  # If it's not an ally piece (empty or enemy), it's a valid move.
                    moves.append(Move((row, col), (endRow, endCol), self.board))


class Move:
    # maps keys to values
    # key : values
    ranksToRows = {
        "1": 7,
        "2": 6,
        "3": 5,
        "4": 4,
        "5": 3,
        "6": 2,
        "7": 1,
        "8": 0,
    }  # 8 is the top row (from white's perspective)
    rowsToRanks = {value: key for key, value in ranksToRows.items()}  # reverse of above

    filesToCols = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4,
        "f": 5,
        "g": 6,
        "h": 7,
    }  # 'a' is the left column (from white's perspective)
    colsToFiles = {value: key for key, value in filesToCols.items()}  # reverse of above

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]  # this is the row number 0-7
        self.startCol = startSq[1]  # this is the column number 0-7
        self.endRow = endSq[0]  # 0-7
        self.endCol = endSq[1]  # 0-7

        # The piece moved
        self.pieceMoved = board[self.startRow][self.startCol]  # 'wp' or 'bR'
        self.pieceCaptured = board[self.endRow][self.endCol]  # '--' or 'wp'

        self.moveID = (
            self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        )

    """
    Overriding the equals method
    """

    def __eq__(self, other):
        if isinstance(other, Move):  # if other is an instance of moves
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # you can add to make this like real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(
            self.endRow, self.endCol
        )  # this is a function that converts the row and column to chess notation

    def getRankFile(self, row, col):
        # converts the row and column to chess notation
        return self.colsToFiles[col] + self.rowsToRanks[row]
