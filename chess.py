import pygame 
import sys

pygame.init()

# Constants
WIDTH, HEIGHT = 640, 640
BOARD_SIZE = 8
SQUARE_SIZE = WIDTH // BOARD_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (247, 247, 105, 150)  
MOVE_HIGHLIGHT = (106, 168, 79, 150) 

# display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Chess")
clock = pygame.time.Clock()

# Load piece images
def load_pieces():
    pieces = {}
    for color in ['w', 'b']:
        for piece in ['p', 'r', 'n', 'b', 'q', 'k']:
            img = pygame.image.load(f"chess_pieces/{color}{piece}.png")
            img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
            pieces[f"{color}{piece}"] = img
    return pieces
# colored circles as placeholders for pieces
pieces_img = {}
for color in ['w', 'b']:
    for piece in ['p', 'r', 'n', 'b', 'q', 'k']:
        surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        font = pygame.font.SysFont('Arial', 36)
        text = font.render(piece.upper(), True, WHITE if color == 'b' else BLACK)
        text_rect = text.get_rect(center=(SQUARE_SIZE//2, SQUARE_SIZE//2))
        pygame.draw.circle(surf, BLACK if color == 'w' else WHITE, (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//2 - 5)
        pygame.draw.circle(surf, WHITE if color == 'w' else BLACK, (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//2 - 8)
        surf.blit(text, text_rect)
        pieces_img[f"{color}{piece}"] = surf

# board initialization
def init_board():
    board = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    
    # Set up pawns
    for col in range(BOARD_SIZE):
        board[1][col] = 'bp'
        board[6][col] = 'wp'
    
    # Set up other pieces
    back_row = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
    for col in range(BOARD_SIZE):
        board[0][col] = 'b' + back_row[col]
        board[7][col] = 'w' + back_row[col]
    
    return board

# Draw the board
def draw_board():
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Draw the pieces on the board
def draw_pieces(board):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            if piece:
                screen.blit(pieces_img[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Highlight selected piece and possible moves
def draw_highlights(selected, valid_moves):
    if selected:
        row, col = selected
        highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight.fill(HIGHLIGHT)
        screen.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))
        
        for move_row, move_col in valid_moves:
            highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            highlight.fill(MOVE_HIGHLIGHT)
            screen.blit(highlight, (move_col * SQUARE_SIZE, move_row * SQUARE_SIZE))

# Check if the king is still alive
def is_king_alive(board, color):
    king = color + 'k'
    for row in board:
        if king in row:
            return True
    return False

def draw_winner_message(message):
    font = pygame.font.SysFont('Arial', 64, bold=True)
    text = font.render(message, True, (255, 0, 0))
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, rect)
    pygame.display.flip()
    pygame.time.wait(10000)  # Wait 10 seconds before closing

# Get valid moves for a piece
def get_valid_moves(board, row, col, turn):
    piece = board[row][col]
    if not piece or piece[0] != turn:
        return []
    
    piece_type = piece[1]
    moves = []
    
    # Pawn moves
    if piece_type == 'p':
        direction = -1 if turn == 'w' else 1
        
        # Move forward one square
        if 0 <= row + direction < BOARD_SIZE and not board[row + direction][col]:
            moves.append((row + direction, col))
            
            # Move forward two squares from starting position
            if (turn == 'w' and row == 6) or (turn == 'b' and row == 1):
                if not board[row + 2*direction][col]:
                    moves.append((row + 2*direction, col))
        
        # Capture diagonally
        for c_offset in [-1, 1]:
            if 0 <= col + c_offset < BOARD_SIZE and 0 <= row + direction < BOARD_SIZE:
                if board[row + direction][col + c_offset] and board[row + direction][col + c_offset][0] != turn:
                    moves.append((row + direction, col + c_offset))
    
    # Rook moves 
    elif piece_type == 'r':
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            for i in range(1, BOARD_SIZE):
                r, c = row + i*dr, col + i*dc
                if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                    break
                if not board[r][c]:
                    moves.append((r, c))
                else:
                    if board[r][c][0] != turn:
                        moves.append((r, c))
                    break
    
    # Knight moves
    elif piece_type == 'n':
        for dr, dc in [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]:
            r, c = row + dr, col + dc
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                if not board[r][c] or board[r][c][0] != turn:
                    moves.append((r, c))
    
    # Bishop moves
    elif piece_type == 'b':
        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            for i in range(1, BOARD_SIZE):
                r, c = row + i*dr, col + i*dc
                if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                    break
                if not board[r][c]:
                    moves.append((r, c))
                else:
                    if board[r][c][0] != turn:
                        moves.append((r, c))
                    break
    
    # Queen moves
    elif piece_type == 'q':
        # Rook-like moves
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            for i in range(1, BOARD_SIZE):
                r, c = row + i*dr, col + i*dc
                if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                    break
                if not board[r][c]:
                    moves.append((r, c))
                else:
                    if board[r][c][0] != turn:
                        moves.append((r, c))
                    break
        
        # Bishop-like moves
        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            for i in range(1, BOARD_SIZE):
                r, c = row + i*dr, col + i*dc
                if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                    break
                if not board[r][c]:
                    moves.append((r, c))
                else:
                    if board[r][c][0] != turn:
                        moves.append((r, c))
                    break
    
    # King moves 
    elif piece_type == 'k':
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    if not board[r][c] or board[r][c][0] != turn:
                        moves.append((r, c))
    
    return moves

# Main game loop
def main():
    board = init_board()
    selected = None
    valid_moves = []
    turn = 'w'  # White goes first
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    col = event.pos[0] // SQUARE_SIZE
                    row = event.pos[1] // SQUARE_SIZE
                    
                    if selected:
                        if (row, col) in valid_moves:
                            # Move the piece
                            board[row][col] = board[selected[0]][selected[1]]
                            board[selected[0]][selected[1]] = ''

                            # pawn promotion 
                            moved_piece = board[row][col]
                            if moved_piece[1] == 'p' and (row == 0 or row == 7):
                                board[row][col] = moved_piece[0] + 'q'

                            # Check for win condition
                            if not is_king_alive(board, 'b'):
                                draw_winner_message("White Wins!")
                                running = False 
                            elif not is_king_alive(board, 'w'):
                                draw_winner_message("Black Wins!")
                                running = False
                                break
                            
                            # Switch turns
                            turn = 'b' if turn == 'w' else 'w'
                            
                            # Reset selection
                            selected = None
                            valid_moves = []
                        else:
                            # Select a new piece 
                            if board[row][col] and board[row][col][0] == turn:
                                selected = (row, col)
                                valid_moves = get_valid_moves(board, row, col, turn)
                            else:
                                selected = None
                                valid_moves = []
                    else:
                        # Select a piece if it's the correct turn
                        if board[row][col] and board[row][col][0] == turn:
                            selected = (row, col)
                            valid_moves = get_valid_moves(board, row, col, turn)
        
        # Draw everything
        draw_board()
        draw_highlights(selected, valid_moves)
        draw_pieces(board)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()