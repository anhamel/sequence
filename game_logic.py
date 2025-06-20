import pygame
import random
import os

# Initialize pygame
pygame.init()





class Token:
    def __init__(self, color, grid_pos):
        self.color = color
        self.grid_pos = grid_pos


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

class CardGrid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
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
    def __init__(self,):
        #Colors included in this class because they are important to game logic
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.GRID_ROWS, self.GRID_COLS = 10, 10
        self.players = [
            Player(1, self.RED),
            Player(2, self.GREEN),
            Player(3, self.BLUE)
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

        # Create a 3x3 hand grid using main card size
        self.HAND_ROWS, self.HAND_COLS = 3, 3
        self.hand_grid = CardGrid(self.HAND_ROWS, self.HAND_COLS)
        self.grid = (self.GRID_ROWS, self.GRID_COLS, (0, 0))

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



corner_positions = [(0, 0), (0, 9), (9, 9), (9, 0)]
suits = ['S', 'D', 'C', 'H']
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Q', 'K', 'A']
suit_order = []
for suit in suits:
    ordered = reversed(values) if suit in ['C', 'H'] else values
    suit_order.extend([v + suit for v in ordered])



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




spiral = spiral_positions(GRID_ROWS, GRID_COLS)
playable_positions = [pos for pos in spiral if pos not in corner_positions]
full_card_list = []
while len(full_card_list) < len(playable_positions):
    full_card_list.extend(suit_order)
full_card_list = full_card_list[:len(playable_positions)]











selected_hand_card_index = None
selected_card_name = None
selected_token_card = None

ONE_EYED_JACKS = {"JH", "JS"}  # Jack of Hearts and Jack of Spades
TWO_EYED_JACKS = {"JD", "JC"}  # Jack of Diamonds and Jack of Clubs