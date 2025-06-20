import pygame
from game_logic import *

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sequence Game Prototype")
def draw_window(game, player_id, selected_index, selected_card_name, selected_token_card):
    WINDOW.fill(GREEN_FELT)
    grid.draw(WINDOW)

    # Sidebar background and turn info
    info_x = ORIGINAL_WIDTH + 20
    info_y = 40
    info_width = WIDTH - ORIGINAL_WIDTH - 40
    info_height = 80
    #pygame.draw.rect(WINDOW, BEIGE, (info_x - 10, info_y - 10, info_width, info_height))
    current_player = game.current_player
    #turn_text = FONT.render(f"Player {current_player.player_id}'s Turn", True, current_player.token_color)
    #WINDOW.blit(turn_text, (info_x, info_y))

    INFO_RECT = pygame.Rect(ORIGINAL_WIDTH + 20, 40, CELL_WIDTH * 3, 60)
    ID_RECT = pygame.Rect(ORIGINAL_WIDTH + 20, 800, CELL_WIDTH * 3, 60)
    draw_player_turn_info(WINDOW, game.current_player, INFO_RECT)
    draw_player_ID(WINDOW, player_id, ID_RECT)


    # Clear hand grid
    for r in range(HAND_ROWS):
        for c in range(HAND_COLS):
            hand_grid.set_card(r, c, None)

    # Display current player's hand in 3x3 hand_grid
    for idx, card_name in enumerate(current_player.hand.cards[:HAND_ROWS * HAND_COLS]):
        row, col = divmod(idx, HAND_COLS)
        filename = card_name + ".png"
        path = os.path.join(img_dir, filename)
        if os.path.exists(path):
            card = Card(card_name, path, (row, col), HAND_CELL_WIDTH, HAND_CELL_HEIGHT)
            hand_grid.set_card(row, col, card)

    hand_grid.draw(WINDOW)

    # Highlight sequences
    for sequence in current_player.global_sequences:
        for card in sequence.cards:
            draw_highlight_overlay(WINDOW, card.rect, sequence.color)

    # Highlight selected card in hand and matching cards on the board
    if selected_card_name:
        for row in grid.grid:
            for card in row:
                if card and card.name == selected_card_name:
                    draw_highlight_overlay(WINDOW, card.rect)
        if selected_index is not None:
            row, col = divmod(selected_index, HAND_COLS)
            card = hand_grid.grid[row][col]
            if card:
                draw_highlight_overlay(WINDOW, card.rect)

    # Highlight selected token for one-eyed jack action
    if selected_token_card:
        draw_highlight_overlay(WINDOW, selected_token_card.rect)

    # Draw draw pile rectangle
    pygame.draw.rect(WINDOW, (230, 200, 140), DRAW_PILE_RECT, border_radius=10)
    pygame.draw.rect(WINDOW, BLACK, DRAW_PILE_RECT, 2, border_radius=10)
    draw_text = BIG_FONT.render("Draw", True, BLACK)
    text_rect = draw_text.get_rect(center=DRAW_PILE_RECT.center)
    WINDOW.blit(draw_text, text_rect)

    # Draw end turn button
    pygame.draw.rect(WINDOW, (230, 200, 140), END_TURN_RECT, border_radius=10)
    pygame.draw.rect(WINDOW, BLACK, END_TURN_RECT, 2, border_radius=10)
    end_text = BIG_FONT.render("End Turn", True, BLACK)
    end_text_rect = end_text.get_rect(center=END_TURN_RECT.center)
    WINDOW.blit(end_text, end_text_rect)

    pygame.display.update()