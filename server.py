# server.py
import socket
import threading
import pickle
import pygame
import os
import sys
import random
import pygame.gfxdraw
from game_logic import *


game = Game()


HOST = '0.0.0.0'
PORT = 65432
clients = []
game_state = {}  # Simplified placeholder
client_dict = {}





def handle_client(conn, addr):
    print(f"Client connected: {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            action = pickle.loads(data)
            response = ""
            print(action)
            if action == "get_id":
                response = client_dict[addr]

            if action == "waiting":
                print("waiting")
                return

            if action == "game_state":
                response = game

            # Drawing cards here
            if action == "draw":
                print("Draw pile is",game.draw_pile.cards)
                response = game.draw_pile.draw_card()
                print("You drew",response)

            print(f"Received action: {action}")
            # TODO: Update game_state based on action
            broadcast_game_state(response)
    finally:
        conn.close()
        clients.remove(conn)

def broadcast_game_state(message):
    #data = pickle.dumps(game_state)
    data = pickle.dumps(message)
    for client in clients:
        try:
            print("sending data")
            client.sendall(data)
        except:
            pass

def start_server():
    clock = pygame.time.Clock()
    running = True

    new_game = Game()
    selected_index = None
    selected_card_name = None
    selected_token_card = None
    card_played_this_turn = False
    game_state["game"] = new_game
    players = [2,1,0]

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.05)
        s.bind((HOST, PORT))
        s.listen()
        print("Server listening...")
        while running:
            try:
                conn, addr = s.accept()
                clients.append(conn)
                client_dict[addr] = players.pop()

                threading.Thread(target=handle_client, args=(conn,addr), daemon=True).start()
            except socket.timeout:
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

                #draw_window(game, selected_index, selected_card_name, selected_token_card)



def main():

        clock = pygame.time.Clock()
        running = True
        game = Game()
        selected_index = None
        selected_card_name = None
        selected_token_card = None
        card_played_this_turn = False

        start_server([clock,running,game,selected_index,selected_card_name,selected_token_card,card_played_this_turn])


if __name__ == '__main__':
    start_server()
    #main()