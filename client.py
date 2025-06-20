# client.py
import socket
import threading
import pickle
import pygame
import sys
import os
import random
import pygame.gfxdraw
import time
from game_logic import *
from window import *



HOST = '127.0.0.1'  # Server IP
PORT = 65432

def listen_for_updates(sock,message=None):
    sock.sendall(pickle.dumps(message))
    print(message)
    while True:
        print("Listening")
        try:
            data = sock.recv(4096)

            if data:
                game_state = pickle.loads(data)
                game = game_state
                print("Received game state:", game_state)  # TODO: Render update
                return(game_state)

        except:
            break

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((HOST, PORT))
        threading.Thread(target=listen_for_updates, args=(s,), daemon=True).start()
        #game_data = listen_for_updates(s)
        game = Game()
        clock = pygame.time.Clock()
        running = True

        player_id = listen_for_updates(s,"get_id")
        current_player_id = 0

        print("player ID is",player_id)

        # start_client()
        selected_index = None
        selected_card_name = None
        selected_token_card = None
        card_played_this_turn = False
        while running:

            clock.tick(60)
            current_player_id = game.current_player.player_id

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if current_player_id == player_id:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        current_player = game.current_player
                        if DRAW_PILE_RECT.collidepoint(event.pos):
                            if not current_player.has_drawn and selected_card_name is None and card_played_this_turn:
                                message = "draw"
                                card = listen_for_updates(s,message)
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
                            #message = "test_message"
                            #game_state = listen_for_updates(s,message)
                            #game = game_state["game"]
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
                                clicked_card = next(
                                    (card for card in iter_all_cards(grid) if card.rect.collidepoint(event.pos)),
                                    None)
                                if clicked_card:
                                    match selected_card_name:
                                        case name if name in ONE_EYED_JACKS:
                                            if clicked_card.placed_token:
                                                if selected_token_card == clicked_card:
                                                    remove_token_from_card(clicked_card, current_player,
                                                                           selected_card_name, game)
                                                    selected_card_name = None
                                                    selected_index = None
                                                    selected_token_card = None
                                                    card_played_this_turn = True
                                                else:
                                                    selected_token_card = clicked_card

                                        case name if name in TWO_EYED_JACKS and not card_played_this_turn:
                                            if not clicked_card.placed_token and clicked_card.name != "board_corner":
                                                place_token_on_card(clicked_card, current_player, selected_card_name,
                                                                    game)
                                                selected_card_name = None
                                                selected_index = None
                                                selected_token_card = None
                                                card_played_this_turn = True

                                        case _ if not card_played_this_turn:
                                            if clicked_card.name == selected_card_name and not clicked_card.placed_token:
                                                place_token_on_card(clicked_card, current_player, selected_card_name,
                                                                    game)
                                                selected_index = None
                                                selected_card_name = None
                                                selected_token_card = None
                                                card_played_this_turn = True
                else:
                    while player_id != current_player_id:
                        game = listen_for_updates(s,'game_state')
                        time.sleep(1)
                        print(player_id, current_player_id)
                        #s.listen()
                        #waiting = True
                        #while waiting:
                        #    try:

            draw_window(game, player_id, selected_index, selected_card_name, selected_token_card)


if __name__ == "__main__":
    main()
