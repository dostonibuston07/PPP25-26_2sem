import pygame
import copy

pygame.init()

WIDTH = 640
HEIGHT = 720
TILE = WIDTH // 8

WHITE = (240, 240, 240)
GRAY = (100, 100, 100)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess SUPER FINAL")

font = pygame.font.SysFont("Segoe UI Symbol", 48)
info_font = pygame.font.SysFont("Arial", 28)

SYMBOLS = {
    ("white", "Pawn"): "♙",
    ("white", "Rook"): "♖",
    ("white", "Knight"): "♘",
    ("white", "Bishop"): "♗",
    ("white", "Queen"): "♕",
    ("white", "King"): "♔",

    ("black", "Pawn"): "♟",
    ("black", "Rook"): "♜",
    ("black", "Knight"): "♞",
    ("black", "Bishop"): "♝",
    ("black", "Queen"): "♛",
    ("black", "King"): "♚",
}

class Piece:
    def __init__(self, color, row, col):
        self.color = color
        self.row = row
        self.col = col
        self.moved = False

    def move(self, r, c):
        self.row = r
        self.col = c
        self.moved = True

    def valid_moves(self, board):
        return []

class Pawn(Piece):
    def valid_moves(self, board):
        moves = []
        direction = -1 if self.color == "white" else 1

        if board.empty(self.row + direction, self.col):
            moves.append((self.row + direction, self.col))

            if not self.moved and board.empty(self.row + 2*direction, self.col):
                moves.append((self.row + 2*direction, self.col))

        for dc in [-1, 1]:
            r = self.row + direction
            c = self.col + dc
            if board.in_bounds(r, c):
                if board.get(r, c) and board.get(r, c).color != self.color:
                    moves.append((r, c))

        if board.en_passant:
            if abs(board.en_passant[1] - self.col) == 1:
                if self.row == board.en_passant[0]:
                    moves.append((self.row + direction, board.en_passant[1]))

        return moves

class Rook(Piece):
    def valid_moves(self, board):
        moves = []
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]

        for dr, dc in dirs:
            r, c = self.row, self.col
            while True:
                r += dr
                c += dc
                if not board.in_bounds(r, c):
                    break
                if board.empty(r, c):
                    moves.append((r, c))
                else:
                    if board.get(r, c).color != self.color:
                        moves.append((r, c))
                    break
        return moves

class Knight(Piece):
    def valid_moves(self, board):
        moves = []
        steps = [(2,1),(2,-1),(-2,1),(-2,-1),
                 (1,2),(1,-2),(-1,2),(-1,-2)]

        for dr, dc in steps:
            r = self.row + dr
            c = self.col + dc
            if board.in_bounds(r, c):
                if board.empty(r, c) or board.get(r, c).color != self.color:
                    moves.append((r, c))
        return moves

class Bishop(Piece):
    def valid_moves(self, board):
        moves = []
        dirs = [(1,1),(1,-1),(-1,1),(-1,-1)]

        for dr, dc in dirs:
            r, c = self.row, self.col
            while True:
                r += dr
                c += dc
                if not board.in_bounds(r, c):
                    break
                if board.empty(r, c):
                    moves.append((r, c))
                else:
                    if board.get(r, c).color != self.color:
                        moves.append((r, c))
                    break
        return moves

class Queen(Piece):
    def valid_moves(self, board):
        return Rook.valid_moves(self, board) + Bishop.valid_moves(self, board)


class King(Piece):
    def valid_moves(self, board):
        moves = []

        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr == 0 and dc == 0:
                    continue
                r = self.row + dr
                c = self.col + dc
                if board.in_bounds(r, c):
                    if board.empty(r, c) or board.get(r, c).color != self.color:
                        moves.append((r, c))
        if not self.moved:
            rook = board.get(self.row, 7)
            if rook and not rook.moved:
                if board.empty(self.row,5) and board.empty(self.row,6):
                    moves.append((self.row,6))
            rook = board.get(self.row,0)
            if rook and not rook.moved:
                if board.empty(self.row,1) and board.empty(self.row,2) and board.empty(self.row,3):
                    moves.append((self.row,2))

        return moves

class Board:
    def __init__(self):
        self.reset()

    def reset(self):
        self.grid = [[None]*8 for _ in range(8)]
        self.turn = "white"
        self.selected = None
        self.valid_moves = []
        self.history = []
        self.en_passant = None
        self.setup()

    def setup(self):
        for i in range(8):
            self.grid[1][i] = Pawn("black",1,i)
            self.grid[6][i] = Pawn("white",6,i)

        self.grid[0][0] = Rook("black",0,0)
        self.grid[0][7] = Rook("black",0,7)
        self.grid[7][0] = Rook("white",7,0)
        self.grid[7][7] = Rook("white",7,7)

        self.grid[0][1] = Knight("black",0,1)
        self.grid[0][6] = Knight("black",0,6)
        self.grid[7][1] = Knight("white",7,1)
        self.grid[7][6] = Knight("white",7,6)

        self.grid[0][2] = Bishop("black",0,2)
        self.grid[0][5] = Bishop("black",0,5)
        self.grid[7][2] = Bishop("white",7,2)
        self.grid[7][5] = Bishop("white",7,5)

        self.grid[0][3] = Queen("black",0,3)
        self.grid[7][3] = Queen("white",7,3)

        self.grid[0][4] = King("black",0,4)
        self.grid[7][4] = King("white",7,4)

    def is_check(self, color):
        king_pos = None

        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p and p.color == color and isinstance(p, King):
                    king_pos = (r, c)

        for r in range(8):
            for c in range(8):
                p = self.grid[r][c]
                if p and p.color != color:
                    if king_pos in p.valid_moves(self):
                        return True

        return False

    def legal_moves(self, piece):
        moves = []

        for r, c in piece.valid_moves(self):
            temp = copy.deepcopy(self)

            p = temp.grid[piece.row][piece.col]
            temp.grid[p.row][p.col] = None
            p.move(r, c)
            temp.grid[r][c] = p

            if not temp.is_check(piece.color):
                moves.append((r, c))

        return moves

    def move(self, piece, r, c):
        self.history.append(copy.deepcopy(self.grid))

        self.en_passant = None
        if isinstance(piece, Pawn) and abs(piece.row - r) == 2:
            self.en_passant = (r, c)

        if isinstance(piece, King):
            if c == 6:
                rook = self.grid[piece.row][7]
                self.grid[piece.row][5] = rook
                self.grid[piece.row][7] = None
                rook.move(piece.row,5)

            if c == 2:
                rook = self.grid[piece.row][0]
                self.grid[piece.row][3] = rook
                self.grid[piece.row][0] = None
                rook.move(piece.row,3)

        self.grid[piece.row][piece.col] = None
        piece.move(r, c)
        self.grid[r][c] = piece

        if isinstance(piece, Pawn):
            if piece.row == 0 or piece.row == 7:
                self.grid[r][c] = Queen(piece.color, r, c)

        self.turn = "black" if self.turn == "white" else "white"

    def undo(self):
        if self.history:
            self.grid = self.history.pop()
            self.turn = "black" if self.turn == "white" else "white"


    def draw(self):
        for r in range(8):
            for c in range(8):
                color = WHITE if (r+c)%2==0 else GRAY
                pygame.draw.rect(screen, color, (c*TILE, r*TILE, TILE, TILE))

        if self.is_check(self.turn):
            for r in range(8):
                for c in range(8):
                    p = self.grid[r][c]
                    if p and isinstance(p, King) and p.color == self.turn:
                        pygame.draw.rect(screen, RED, (c*TILE, r*TILE, TILE, TILE))

        for move in self.valid_moves:
            pygame.draw.circle(screen, GREEN,
                               (move[1]*TILE + TILE//2, move[0]*TILE + TILE//2), 10)

        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c]
                if piece:
                    symbol = SYMBOLS[(piece.color, piece.__class__.__name__)]
                    img = font.render(symbol, True, (0,0,0))
                    screen.blit(img, (c*TILE + 20, r*TILE + 10))

        text = info_font.render("Turn: " + self.turn, True, (0,0,0))
        screen.blit(text, (10, 660))

        if self.is_check(self.turn):
            text = info_font.render("CHECK!", True, RED)
            screen.blit(text, (260, 660))

        text = info_font.render("U - Undo   R - Restart", True, (0,0,0))
        screen.blit(text, (160, 690))

    def get(self, r, c):
        return self.grid[r][c]

    def empty(self, r, c):
        return self.in_bounds(r, c) and self.grid[r][c] is None

    def in_bounds(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def click(self, r, c):
        piece = self.get(r, c)

        if self.selected:
            if (r, c) in self.valid_moves:
                self.move(self.selected, r, c)
                self.selected = None
                self.valid_moves = []
                return

        if piece and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.legal_moves(piece)

board = Board()
run = True

while run:
    pygame.time.delay(40)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            board.click(y // TILE, x // TILE)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                board.undo()
            if event.key == pygame.K_r:
                board.reset()

    board.draw()
    pygame.display.update()

pygame.quit()
