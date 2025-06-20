import pygame
import os


IMG_PATH = "img"
# Set up display
ORIGINAL_WIDTH = 1200
WIDTH = int(ORIGINAL_WIDTH * 1.5)  # expand by 50% for info panel
MAX_HEIGHT = 950
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_FELT = (0, 100, 0)
BEIGE = (245, 245, 220)
FONT = pygame.font.SysFont(None, 36)
BIG_FONT = pygame.font.SysFont(None, 36)
class WindowManager():
    def __init__(self,game):



        self.CARD_ASPECT_RATIO = 3.5 / 2.5
        self.CELL_WIDTH = ORIGINAL_WIDTH // game.GRID_COLS
        self.CELL_HEIGHT = int(self.CELL_WIDTH * self.CARD_ASPECT_RATIO)
        self.HEIGHT = self.CELL_HEIGHT * game.GRID_ROWS
        if self.HEIGHT > MAX_HEIGHT:
            CELL_HEIGHT = MAX_HEIGHT // game.GRID_ROWS
            CELL_WIDTH = int(CELL_HEIGHT / self.CARD_ASPECT_RATIO)
            ORIGINAL_WIDTH = CELL_WIDTH * game.GRID_COLS
            WIDTH = int(ORIGINAL_WIDTH * 1.5)
            HEIGHT = CELL_HEIGHT * game.GRID_ROWS
        BUFFER = int(0.05 * CELL_WIDTH)
        self.WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sequence Game Prototype")



        # Game board setup
        img_dir = "img"
        all_cards = sorted([f for f in os.listdir(img_dir) if f.endswith(".png")])

    def draw_highlight_overlay(self,surface, rect, color=(255, 255, 0), alpha=80):
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((*color, alpha))
        surface.blit(overlay, rect.topleft)

    def draw_player_turn_info(self,WINDOW, player, rect):
        pygame.draw.rect(WINDOW, (230, 200, 140), rect, border_radius=10)
        pygame.draw.rect(WINDOW, self.BLACK, rect, 2, border_radius=10)
        text = self.BIG_FONT.render(f"Player {player.player_id}'s Turn", True, player.token_color)
        text_rect = text.get_rect(center=rect.center)
        WINDOW.blit(text, text_rect)

    def draw_token(self, token, surface):
        row, col = token.grid_pos
        center_x = col * self.CELL_WIDTH + self.CELL_WIDTH // 2
        center_y = row * self.CELL_HEIGHT + self.CELL_HEIGHT // 2
        radius = min(self.CELL_WIDTH, self.CELL_HEIGHT) // 4
        pygame.gfxdraw.aacircle(surface, center_x, center_y, radius, self.color)
        pygame.gfxdraw.filled_circle(surface, center_x, center_y, radius, self.color)

    def draw_window(self,game, selected_index, selected_card_name, selected_token_card):
        self.WINDOW.fill(GREEN_FELT)
        grid = game.grid

        grid.draw(self.WINDOW)

        # Sidebar background and turn info
        info_x = ORIGINAL_WIDTH + 20
        info_y = 40
        info_width = WIDTH - ORIGINAL_WIDTH - 40
        info_height = 80
        current_player = game.current_player

        INFO_RECT = pygame.Rect(ORIGINAL_WIDTH + 20, 40, CELL_WIDTH * 3, 60)
        draw_player_turn_info(self.WINDOW, game.current_player, INFO_RECT)

        # Clear hand grid
        for r in range(game.HAND_ROWS):
            for c in range(game.HAND_COLS):
                hand_grid.set_card(r, c, None)

        # Display current player's hand in 3x3 hand_grid
        for idx, card_name in enumerate(current_player.hand.cards[:HAND_ROWS * HAND_COLS]):
            row, col = divmod(idx, HAND_COLS)
            filename = card_name + ".png"
            path = os.path.join(IMG_PATH, filename)
            if os.path.exists(path):
                card = Card(card_name, path, (row, col), HAND_CELL_WIDTH, HAND_CELL_HEIGHT)
                hand_grid.set_card(row, col, card)

        hand_grid.draw(self.WINDOW)

        # Highlight sequences
        for sequence in current_player.global_sequences:
            for card in sequence.cards:
                draw_highlight_overlay(self.WINDOW, card.rect, sequence.color)

        # Highlight selected card in hand and matching cards on the board
        if selected_card_name:
            for row in grid.grid:
                for card in row:
                    if card and card.name == selected_card_name:
                        draw_highlight_overlay(self.WINDOW, card.rect)
            if selected_index is not None:
                row, col = divmod(selected_index, HAND_COLS)
                card = hand_grid.grid[row][col]
                if card:
                    draw_highlight_overlay(self.WINDOW, card.rect)

        # Highlight selected token for one-eyed jack action
        if selected_token_card:
            draw_highlight_overlay(self.WINDOW, selected_token_card.rect)

        # Draw draw pile rectangle
        pygame.draw.rect(self.WINDOW, (230, 200, 140), DRAW_PILE_RECT, border_radius=10)
        pygame.draw.rect(self.WINDOW, BLACK, DRAW_PILE_RECT, 2, border_radius=10)
        draw_text = BIG_FONT.render("Draw", True, BLACK)
        text_rect = draw_text.get_rect(center=DRAW_PILE_RECT.center)
        self.WINDOW.blit(draw_text, text_rect)

        # Draw end turn button
        pygame.draw.rect(self.WINDOW, (230, 200, 140), END_TURN_RECT, border_radius=10)
        pygame.draw.rect(self.WINDOW, BLACK, END_TURN_RECT, 2, border_radius=10)
        end_text = BIG_FONT.render("End Turn", True, BLACK)
        end_text_rect = end_text.get_rect(center=END_TURN_RECT.center)
        self.WINDOW.blit(end_text, end_text_rect)

        pygame.display.update()


class CardGraphic:
    def __init__(self, card_obj):


        self.original_image = pygame.image.load(image_path).convert_alpha()
        adjusted_width = cell_width - 2 * BUFFER
        adjusted_height = cell_height - 2 * BUFFER
        self.image = self.scale_image_to_cell(self.original_image, adjusted_width, adjusted_height)
        self.grid_pos = grid_pos

        if name == "board_corner":
            self.suit = False
            self.card_value = False
            self.is_face = False
        else:
            self.suit = name[-1]
            self.card_value = name[:-1]
            self.is_face = self.card_value in ['J', 'Q', 'K']

        self.rect = self.get_rect_from_grid(cell_width, cell_height)
        self.placed_token = False

    def scale_image_to_cell(self, image, max_width, max_height):
        img_width, img_height = image.get_size()
        scale_ratio = min(max_width / img_width, max_height / img_height)
        new_size = (int(img_width * scale_ratio), int(img_height * scale_ratio))
        return pygame.transform.smoothscale(image, new_size)

    def get_rect_from_grid(self, cell_width, cell_height):
        row, col = self.grid_pos
        x = col * cell_width + (cell_width - self.image.get_width()) // 2
        y = row * cell_height + (cell_height - self.image.get_height()) // 2
        return self.image.get_rect(topleft=(x, y))


class CardGrid:
    def __init__(self, rows, cols, top_left, cell_width, cell_height):
        self.rows = rows
        self.cols = cols
        self.top_left = top_left
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]

    def draw(self, surface):
        offset_x, offset_y = self.top_left
        for row in range(self.rows):
            for col in range(self.cols):
                card = self.grid[row][col]
                if card:
                    x = offset_x + col * self.cell_width + (self.cell_width - card.image.get_width()) // 2
                    y = offset_y + row * self.cell_height + (self.cell_height - card.image.get_height()) // 2
                    card.rect.topleft = (x, y)
                    surface.blit(card.image, card.rect)
                    if card.placed_token:
                        card.placed_token.draw(surface)

for idx, pos in enumerate(corner_positions):
    path = os.path.join(IMG_PATH, "board_corner.png")
    card = Card("board_corner", path, pos, CELL_WIDTH, CELL_HEIGHT)
    grid.set_card(pos[0], pos[1], card)

for name, pos in zip(full_card_list, playable_positions):
    filename = name + ".png"
    path = os.path.join(IMG_PATH, filename)
    if filename in all_cards:
        card = Card(name, path, pos, CELL_WIDTH, CELL_HEIGHT)
        grid.set_card(pos[0], pos[1], card)

# Define draw pile, and end turn button rectangles
DRAW_PILE_RECT = pygame.Rect(ORIGINAL_WIDTH + 20, 550, CELL_WIDTH * 2, CELL_HEIGHT)
END_TURN_RECT = pygame.Rect(ORIGINAL_WIDTH + 20, 700, CELL_WIDTH * 2, 60)

