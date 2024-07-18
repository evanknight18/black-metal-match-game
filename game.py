import pygame
import random

def main():
    # Initialize Pygame
    pygame.init()
    screen_width, screen_height = 600, 700
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Black Metal Match-3 Game')

    # Load images
    tile_images = [
        pygame.image.load(f'assets/images/tile{i}.png').convert_alpha()
        for i in range(1, 6)
    ]

    # Load sounds
    match_sound = pygame.mixer.Sound('assets/sounds/match.wav')
    match4_sound = pygame.mixer.Sound('assets/sounds/match4.wav')
    pygame.mixer.music.load('assets/sounds/background.mp3')
    pygame.mixer.music.play(-1)

    # Game variables
    font = pygame.font.Font(None, 36)
    score = 0
    moves = 30
    target_score = 1000
    round_number = 1
    game_over = False

    # Create game board
    def create_board(rows, cols):
        board = []
        for row in range(rows):
            board.append([random.choice(tile_images) for _ in range(cols)])
        return board

    board = create_board(8, 8)

    def draw_board(screen, board, tile_size, fall_positions=None):
        for row in range(len(board)):
            for col in range(len(board[row])):
                if board[row][col] is None:
                    continue
                x = col * tile_size
                y = row * tile_size + 100
                if fall_positions and (col, row) in fall_positions:
                    y += fall_positions[(col, row)]
                screen.blit(board[row][col], (x, y))

    def draw_ui(screen, score, moves, target_score, round_number):
        pygame.draw.rect(screen, (50, 50, 50), (0, 0, screen_width, 100))
        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        moves_text = font.render(f'Moves: {moves}', True, (255, 255, 255))
        target_text = font.render(f'Target Score: {target_score}', True, (255, 255, 255))
        round_text = font.render(f'Round: {round_number}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        screen.blit(moves_text, (10, 40))
        screen.blit(target_text, (10, 70))
        screen.blit(round_text, (screen_width - 150, 10))

    def animate_swap(screen, board, tile_size, pos1, pos2):
        clock = pygame.time.Clock()
        fps = 60
        animation_duration = 500
        steps = int(animation_duration / (1000 / fps))
        
        x1, y1 = pos1[0] * tile_size, pos1[1] * tile_size + 100
        x2, y2 = pos2[0] * tile_size, pos2[1] * tile_size + 100
        dx, dy = (x2 - x1) / steps, (y2 - y1) / steps
        
        for i in range(steps):
            screen.fill((0, 0, 0))
            draw_board(screen, board, tile_size)
            draw_ui(screen, score, moves, target_score, round_number)
            screen.blit(board[pos1[1]][pos1[0]], (x1 + dx * i, y1 + dy * i))
            screen.blit(board[pos2[1]][pos2[0]], (x2 - dx * i, y2 - dy * i))
            pygame.display.flip()
            clock.tick(fps)
        
        board[pos1[1]][pos1[0]], board[pos2[1]][pos2[0]] = board[pos2[1]][pos2[0]], board[pos1[1]][pos1[0]]

    def animate_fall(screen, board, tile_size, fall_positions):
        clock = pygame.time.Clock()
        fps = 60
        animation_duration = 500
        steps = int(animation_duration / (1000 / fps))
        
        initial_positions = {pos: fall_positions[pos] for pos in fall_positions}
        
        for i in range(steps):
            screen.fill((0, 0, 0))
            current_positions = {pos: initial_positions[pos] * (i / steps) for pos in initial_positions}
            draw_board(screen, board, tile_size, current_positions)
            draw_ui(screen, score, moves, target_score, round_number)
            pygame.display.flip()
            clock.tick(fps)

    tile_size = 75

    def swap_tiles(board, pos1, pos2):
        board[pos1[1]][pos1[0]], board[pos2[1]][pos2[0]] = board[pos2[1]][pos2[0]], board[pos1[1]][pos1[0]]

    def check_matches(board):
        matched = []
        for row in range(len(board)):
            for col in range(len(board[row]) - 2):
                if board[row][col] == board[row][col + 1] == board[row][col + 2]:
                    match_length = 3
                    while col + match_length < len(board[row]) and board[row][col] == board[row][col + match_length]:
                        match_length += 1
                    matched.extend([(col + i, row) for i in range(match_length)])
                    col += match_length - 1
        for col in range(len(board[0])):
            for row in range(len(board) - 2):
                if board[row][col] == board[row + 1][col] == board[row + 2][col]:
                    match_length = 3
                    while row + match_length < len(board) and board[row][col] == board[row + match_length][col]:
                        match_length += 1
                    matched.extend([(col, row + i) for i in range(match_length)])
                    row += match_length - 1
        return matched

    def play_match_sound(matches):
        if len(matches) >= 4:
            match4_sound.play()
        else:
            match_sound.play()

    def remove_matches(board, matches):
        for col, row in matches:
            board[row][col] = None

    def drop_tiles(board):
        fall_positions = {}
        for col in range(len(board[0])):
            empty_tiles = [row for row in range(len(board)) if board[row][col] is None]
            if empty_tiles:
                for row in reversed(range(len(board))):
                    if board[row][col] is not None and row < max(empty_tiles):
                        new_row = max(empty_tiles)
                        fall_positions[(col, new_row)] = (new_row - row) * tile_size
                        board[new_row][col] = board[row][col]
                        board[row][col] = None
                        empty_tiles.remove(new_row)
                        empty_tiles.insert(0, row)
        return fall_positions

    def fill_empty_tiles(board, tile_images):
        new_falls = {}
        for col in range(len(board[0])):
            for row in range(len(board)):
                if board[row][col] is None:
                    board[row][col] = random.choice(tile_images)
                    new_falls[(col, row)] = -tile_size * (row + 1)
        return new_falls

    def is_adjacent(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1

    def handle_matches(screen, board, tile_size, score):
        matches = check_matches(board)
        if matches:
            score += len(matches) * 10
            play_match_sound(matches)
            remove_matches(board, matches)
            fall_positions = drop_tiles(board)
            animate_fall(screen, board, tile_size, fall_positions)
            new_falls = fill_empty_tiles(board, tile_images)
            animate_fall(screen, board, tile_size, new_falls)
        return score

    def reset_game():
        nonlocal score, moves, target_score, board, game_over, round_number
        score = 0
        moves = 30
        target_score += 500
        round_number += 1
        board = create_board(8, 8)
        game_over = False

    # Main game loop
    running = True
    selected_tile = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and moves > 0 and not game_over:
                x, y = event.pos
                col, row = x // tile_size, (y - 100) // tile_size  # Adjust for scoreboard offset
                if 0 <= col < 8 and 0 <= row < 8:  # Ensure click is within board bounds
                    if selected_tile:
                        if is_adjacent(selected_tile, (col, row)):
                            animate_swap(screen, board, tile_size, selected_tile, (col, row))
                            matches = check_matches(board)
                            score = handle_matches(screen, board, tile_size, score)
                            if not matches:
                                animate_swap(screen, board, tile_size, selected_tile, (col, row))  # Swap back if no match
                            while check_matches(board):  # Handle combos
                                score = handle_matches(screen, board, tile_size, score)
                            selected_tile = None
                            moves -= 1  # Decrement moves
                        else:
                            selected_tile = (col, row)
                    else:
                        selected_tile = (col, row)
            elif event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_RETURN:
                    reset_game()

        # Drawing code
        screen.fill((0, 0, 0))  # Clear screen with black
        draw_board(screen, board, tile_size)
        draw_ui(screen, score, moves, target_score, round_number)

        # Check for game over
        if moves == 0 and score < target_score:
            game_over_text = font.render('Game Over! You Lose!', True, (255, 0, 0))
            screen.blit(game_over_text, (screen_width // 2 - 150, screen_height // 2 - 50))
            game_over = True
        elif score >= target_score:
            game_over_text = font.render('You Win! Press Enter for Next Round!', True, (0, 255, 0))
            screen.blit(game_over_text, (screen_width // 2 - 250, screen_height // 2 - 50))
            game_over = True

        # Update display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
