import pygame
import sys
import os
import random
import pygame.gfxdraw

# Initialize pygame
pygame.init()

# Set up display
ORIGINAL_WIDTH = 1200
WIDTH = int(ORIGINAL_WIDTH * 1.5)  # expand by 50% for info panel
MAX_HEIGHT = 950
GRID_ROWS, GRID_COLS = 10, 10
CARD_ASPECT_RATIO = 3.5 / 2.5
CELL_WIDTH = ORIGINAL_WIDTH // GRID_COLS
CELL_HEIGHT = int(CELL_WIDTH * CARD_ASPECT_RATIO)
HEIGHT = CELL_HEIGHT * GRID_ROWS
if HEIGHT > MAX_HEIGHT:
    CELL_HEIGHT = MAX_HEIGHT // GRID_ROWS
    CELL_WIDTH = int(CELL_HEIGHT / CARD_ASPECT_RATIO)
    ORIGINAL_WIDTH = CELL_WIDTH * GRID_COLS
    WIDTH = int(ORIGINAL_WIDTH * 1.5)
    HEIGHT = CELL_HEIGHT * GRID_ROWS

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sequence Game Prototype")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_FELT = (0, 100, 0)
BEIGE = (245, 245, 220)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
FONT = pygame.font.SysFont(None, 36)
BUFFER = int(0.05 * CELL_WIDTH)

class Token:
    def __init__(self, color, grid_pos):
        self.color = color
        self.grid_pos = grid_pos

    def draw(self, surface):
        row, col = self.grid_pos
        center_x = col * CELL_WIDTH + CELL_WIDTH // 2
        center_y = row * CELL_HEIGHT + CELL_HEIGHT // 2
        radius = min(CELL_WIDTH, CELL_HEIGHT) // 4
        pygame.gfxdraw.aacircle(surface, center_x, center_y, radius, self.color)
        pygame.gfxdraw.filled_circle(surface, center_x, center_y, radius, self.color)

class CardDeck:
    def __init__(self, cards=None):
        self.cards = cards if cards else []

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop() if self.cards else None

    def add_card(self, card_name):
        self.cards.append(card_name)

    def is_empty(self):
        return len(self.cards) == 0

class Card:
    def __init__(self, name, image_path, grid_pos, cell_width, cell_height):
        self.name = name
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

    def set_card(self, row, col, card):
        self.grid[row][col] = card

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

class Player:
    def __init__(self, player_id, token_color):
        self.player_id = player_id
        self.token_color = token_color
        self.hand = CardDeck()
        self.has_drawn = False
        self.player_sequences = set()
        self.global_sequences = set()

    def add_card_to_hand(self, card_name):
        self.hand.add_card(card_name)

    def remove_card_from_hand(self, card_name):
        if card_name in self.hand.cards:
            self.hand.cards.remove(card_name)

    def has_card(self, card_name):
        return card_name in self.hand.cards

    def add_sequence(self, sequence):
        if sequence not in self.global_sequences:
            self.global_sequences.add(sequence)
            if sequence.player_id == self.player_id:
                self.player_sequences.add(sequence)

class Game:
    def __init__(self):
        self.players = [
            Player(1, RED),
            Player(2, GREEN),
            Player(3, BLUE)
        ]
        self.current_turn_index = 0
        suits = ['S', 'D', 'C', 'H']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        full_deck = [v + s for s in suits for v in values] * 2
        self.draw_pile = CardDeck(full_deck)
        # TODO REMOVE THIS
        #self.draw_pile.shuffle()
        self.discard_pile = CardDeck()

        for player in self.players:
            for _ in range(7):
                card = self.draw_pile.draw_card()
                if card:
                    player.add_card_to_hand(card)

    @property
    def current_player(self):
        return self.players[self.current_turn_index]

    def next_turn(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.players)

    def place_token(self, card):
        if not card.placed_token:
            player = self.current_player
            card.placed_token = Token(player.token_color, card.grid_pos)
            self.next_turn()

class Sequence:
    def __init__(self, cards, player_id, color):
        self.cards = cards
        self.player_id = player_id
        self.color = color

    def __eq__(self, other):
        return isinstance(other, Sequence) and set(c.grid_pos for c in self.cards) == set(c.grid_pos for c in other.cards)

    def __hash__(self):
        return hash(frozenset(c.grid_pos for c in self.cards))

# Game board setup
img_dir = "img"
all_cards = sorted([f for f in os.listdir(img_dir) if f.endswith(".png")])

corner_positions = [(0, 0), (0, 9), (9, 9), (9, 0)]
suits = ['S', 'D', 'C', 'H']
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Q', 'K', 'A']
suit_order = []
for suit in suits:
    ordered = reversed(values) if suit in ['C', 'H'] else values
    suit_order.extend([v + suit for v in ordered])

def draw_highlight_overlay(surface, rect, color=(255, 255, 0), alpha=80):
    overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    overlay.fill((*color, alpha))
    surface.blit(overlay, rect.topleft)

def spiral_positions(rows, cols):
    seen = [[False]*cols for _ in range(rows)]
    result = []
    directions = [(0,1), (1,0), (0,-1), (-1,0)]
    row = col = di = 0
    for _ in range(rows * cols):
        if not seen[row][col]:
            result.append((row, col))
            seen[row][col] = True
        nr, nc = row + directions[di][0], col + directions[di][1]
        if 0 <= nr < rows and 0 <= nc < cols and not seen[nr][nc]:
            row, col = nr, nc
        else:
            di = (di + 1) % 4
            row, col = row + directions[di][0], col + directions[di][1]
    return result

def place_token_on_card(card, player, selected_card_name, game):
    card.placed_token = Token(player.token_color, card.grid_pos)
    player.remove_card_from_hand(selected_card_name)
    game.discard_pile.add_card(selected_card_name)


def remove_token_from_card(card, player, selected_card_name, game):
    card.placed_token = None
    player.remove_card_from_hand(selected_card_name)
    game.discard_pile.add_card(selected_card_name)


def iter_all_cards(grid):
    for row in grid.grid:
        for card in row:
            if card:
                yield card

def check_for_sequences(grid, length=5):
    directions = [(1, 0), (0, 1), (1, 1), (1, -1),(-1, 1), (-1, -1)]  # horizontal, vertical, diagonal, anti-diagonal
    sequences = []

    for row in range(len(grid.grid)):
        for col in range(len(grid.grid[0])):
            start_card = grid.grid[row][col]
            if not start_card or not start_card.placed_token:
                continue
            color = start_card.placed_token.color
            player_id = getattr(start_card.placed_token, 'player_id', None)
            for dr, dc in directions:
                matched = [start_card]
                for i in range(1, length):
                    r, c = row + dr * i, col + dc * i
                    if 0 <= r < len(grid.grid) and 0 <= c < len(grid.grid[0]):
                        next_card = grid.grid[r][c]
                        if next_card and ((next_card.placed_token and next_card.placed_token.color == color) or next_card.name == "board_corner"):
                            matched.append(next_card)
                        else:
                            break
                    else:
                        break
                if len(matched) == length:
                    sequences.append(Sequence(matched, player_id, color))
    return sequences


def draw_player_turn_info(WINDOW, player, rect):
    pygame.draw.rect(WINDOW, (230, 200, 140), rect, border_radius=10)
    pygame.draw.rect(WINDOW, BLACK, rect, 2, border_radius=10)
    text = BIG_FONT.render(f"Player {player.player_id}'s Turn", True, player.token_color)
    text_rect = text.get_rect(center=rect.center)
    WINDOW.blit(text, text_rect)

spiral = spiral_positions(GRID_ROWS, GRID_COLS)
playable_positions = [pos for pos in spiral if pos not in corner_positions]
full_card_list = []
while len(full_card_list) < len(playable_positions):
    full_card_list.extend(suit_order)
full_card_list = full_card_list[:len(playable_positions)]

grid = CardGrid(GRID_ROWS, GRID_COLS, (0, 0), CELL_WIDTH, CELL_HEIGHT)

for idx, pos in enumerate(corner_positions):
    path = os.path.join(img_dir, "board_corner.png")
    card = Card("board_corner", path, pos, CELL_WIDTH, CELL_HEIGHT)
    grid.set_card(pos[0], pos[1], card)

for name, pos in zip(full_card_list, playable_positions):
    filename = name + ".png"
    path = os.path.join(img_dir, filename)
    if filename in all_cards:
        card = Card(name, path, pos, CELL_WIDTH, CELL_HEIGHT)
        grid.set_card(pos[0], pos[1], card)

# Create a 3x3 hand grid using main card size
HAND_ROWS, HAND_COLS = 3, 3
HAND_CELL_WIDTH = CELL_WIDTH
HAND_CELL_HEIGHT = CELL_HEIGHT
HAND_TOP_LEFT = (ORIGINAL_WIDTH + 20, 150)
hand_grid = CardGrid(HAND_ROWS, HAND_COLS, HAND_TOP_LEFT, HAND_CELL_WIDTH, HAND_CELL_HEIGHT)

# Define BIG_FONT for larger buttons
BIG_FONT = pygame.font.SysFont(None, 36)

# Define draw pile, and end turn button rectangles
DRAW_PILE_RECT = pygame.Rect(ORIGINAL_WIDTH + 20, 550, CELL_WIDTH * 2, CELL_HEIGHT)
END_TURN_RECT = pygame.Rect(ORIGINAL_WIDTH + 20, 700, CELL_WIDTH * 2, 60)

selected_hand_card_index = None
selected_card_name = None
selected_token_card = None

ONE_EYED_JACKS = {"JH", "JS"}  # Jack of Hearts and Jack of Spades
TWO_EYED_JACKS = {"JD", "JC"}  # Jack of Diamonds and Jack of Clubs



def main():
    clock = pygame.time.Clock()
    running = True
    game = Game()
    selected_index = None
    selected_card_name = None
    selected_token_card = None
    card_played_this_turn = False
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                current_player = game.current_player
                if DRAW_PILE_RECT.collidepoint(event.pos):
                    if not current_player.has_drawn and selected_card_name is None and card_played_this_turn:
                        card = game.draw_pile.draw_card()
                        if card:
                            current_player.add_card_to_hand(card)
                            current_player.has_drawn = True
                elif END_TURN_RECT.collidepoint(event.pos) and card_played_this_turn:
                    current_player.has_drawn = False
                    selected_index = None
                    selected_card_name = None
                    selected_token_card = None
                    card_played_this_turn = False

                    # Check for sequences before changing turn
                    sequences = check_for_sequences(grid)
                    # For now we just print them
                    if sequences:
                        for seq in sequences:
                            print(
                                f"Sequence found for Player {seq.player_id} with color {seq.color} on {[(c.grid_pos) for c in seq.cards]}")
                            for player in game.players:
                                player.add_sequence(seq)

                        # Clear all highlights
                        for card in iter_all_cards(grid):
                            card.highlight = None



                    game.next_turn()
                else:
                    clicked_hand = False
                    for idx in range(min(HAND_ROWS * HAND_COLS, len(current_player.hand.cards))):
                        row, col = divmod(idx, HAND_COLS)
                        card = hand_grid.grid[row][col]
                        if card and card.rect.collidepoint(event.pos):
                            if selected_index != idx:
                                selected_index = idx
                                selected_card_name = current_player.hand.cards[idx]
                                selected_token_card = None
                            else:
                                selected_index = None
                                selected_card_name = None
                                selected_token_card = None
                            clicked_hand = True
                            break
                    if not clicked_hand and selected_card_name:
                        clicked_card = next((card for card in iter_all_cards(grid) if card.rect.collidepoint(event.pos)),
                                            None)
                        if clicked_card:
                            match selected_card_name:
                                case name if name in ONE_EYED_JACKS:
                                    if clicked_card.placed_token:
                                        if selected_token_card == clicked_card:
                                            remove_token_from_card(clicked_card, current_player, selected_card_name, game)
                                            selected_card_name = None
                                            selected_index = None
                                            selected_token_card = None
                                            card_played_this_turn = True
                                        else:
                                            selected_token_card = clicked_card

                                case name if name in TWO_EYED_JACKS and not card_played_this_turn:
                                    if not clicked_card.placed_token and clicked_card.name != "board_corner":
                                        place_token_on_card(clicked_card, current_player, selected_card_name, game)
                                        selected_card_name = None
                                        selected_index = None
                                        selected_token_card = None
                                        card_played_this_turn = True

                                case _ if not card_played_this_turn:
                                    if clicked_card.name == selected_card_name and not clicked_card.placed_token:
                                        place_token_on_card(clicked_card, current_player, selected_card_name, game)
                                        selected_index = None
                                        selected_card_name = None
                                        selected_token_card = None
                                        card_played_this_turn = True
        draw_window(game, selected_index, selected_card_name, selected_token_card)

    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()
