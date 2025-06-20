from game_logic import *
from graphics import *
import sys

def main():
    clock = pygame.time.Clock()
    running = True
    game = Game()
    window_manager = WindowManager(game)
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