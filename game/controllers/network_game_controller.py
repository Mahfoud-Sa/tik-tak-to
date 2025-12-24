"""Network Game Controller - Handles multiplayer game logic."""

from typing import Optional, Callable
from controllers.game_controller import GameController
from models.game_state import GameState
from network.server import GameServer
from network.client import GameClient
from network.protocol import create_move_message
from config import PLAYER_O, PLAYER_X, SYMBOL_O, SYMBOL_X


class NetworkGameController:
    """
    Controller for networked multiplayer games.
    
    Host is always Player O (plays first).
    Client is always Player X.
    """
    
    def __init__(self, game_state: GameState, view, is_host: bool):
        """
        Initialize the network game controller.
        
        Args:
            game_state: The game state model
            view: The game view
            is_host: True if this is the host, False if client
        """
        self.state = game_state
        self.view = view
        self.is_host = is_host
        
        # Local player is O for host, X for client
        self.local_player_index = PLAYER_O if is_host else PLAYER_X
        self.local_symbol = SYMBOL_O if is_host else SYMBOL_X
        
        # Network components
        self.server: Optional[GameServer] = None
        self.client: Optional[GameClient] = None
        
        # Callbacks
        self._on_game_start: Optional[Callable] = None
        self._on_game_end: Optional[Callable] = None
        self._on_opponent_disconnect: Optional[Callable] = None
        
        # Game state
        self.is_my_turn = is_host  # Host (O) always starts
        self.is_connected = False
    
    def set_callbacks(self, on_game_start=None, on_game_end=None, on_opponent_disconnect=None):
        """Set callbacks for game events."""
        self._on_game_start = on_game_start
        self._on_game_end = on_game_end
        self._on_opponent_disconnect = on_opponent_disconnect
    
    def set_server(self, server: GameServer):
        """Set the server (for host)."""
        self.server = server
        server.on_move_received(self._on_network_move_received)
        server.on_client_disconnect(self._on_disconnect)
    
    def set_client(self, client: GameClient):
        """Set the client (for joining player)."""
        self.client = client
        client.on_move_received(self._on_network_move_received)
        client.on_disconnect(self._on_disconnect)
    
    def start_game(self):
        """Start a new networked game."""
        self.state.start_game()
        self.is_my_turn = self.is_host  # Host (O) always starts first
        self.is_connected = True
        
        if self.view:
            self.view.clear_board()
            self.view.draw_grid()
            self.view.update_scores(
                self.state.player_o.wins,
                self.state.player_x.wins
            )
            self._update_turn_indicator()
        
        if self._on_game_start:
            self._on_game_start()
    
    def exit_game(self):
        """Exit the current game and cleanup network."""
        self.state.end_game()
        self.is_connected = False
        
        # Disconnect network
        if self.server:
            self.server.stop()
            self.server = None
        if self.client:
            self.client.disconnect()
            self.client = None
        
        if self.view:
            self.view.clear_board()
        
        if self._on_game_end:
            self._on_game_end()
    
    def handle_cell_click(self, row: int, col: int, click_x: int = None, click_y: int = None):
        """
        Handle a cell click from the local player.
        
        Only processes if it's the local player's turn.
        """
        if not self.state.is_game_active:
            return
        
        if not self.is_my_turn:
            return  # Not our turn!
        
        if row < 0 or col < 0:
            return
        
        # Try to make the move locally
        if self.state.board.make_move(row, col, self.local_symbol):
            # Draw the symbol
            if self.view:
                if self.local_symbol == SYMBOL_O:
                    self.view.draw_o(row, col, click_x, click_y)
                else:
                    self.view.draw_x(row, col, click_x, click_y)
            
            self.state.increment_moves()
            
            # Send move to opponent
            self._send_move(row, col)
            
            # Check for game end
            if self._check_game_end():
                return
            
            # Switch turn
            self.is_my_turn = False
            self.state.switch_player()
            self._update_turn_indicator()
    
    def _on_network_move_received(self, row: int, col: int):
        """Handle a move received from the network."""
        if self.is_my_turn:
            return  # Ignore if it's our turn (shouldn't happen)
        
        opponent_symbol = SYMBOL_X if self.is_host else SYMBOL_O
        
        # Make the move
        if self.state.board.make_move(row, col, opponent_symbol):
            # Draw opponent's symbol (need to schedule on main thread)
            if self.view:
                self.view.root.after(0, lambda: self._draw_opponent_move(row, col, opponent_symbol))
            
            self.state.increment_moves()
            
            # Check for game end
            if self._check_game_end():
                return
            
            # It's now our turn
            self.is_my_turn = True
            self.state.switch_player()
            self.view.root.after(0, self._update_turn_indicator)
    
    def _draw_opponent_move(self, row: int, col: int, symbol: str):
        """Draw opponent's move on the board."""
        if self.view:
            if symbol == SYMBOL_O:
                self.view.draw_o(row, col)
            else:
                self.view.draw_x(row, col)
    
    def _send_move(self, row: int, col: int):
        """Send a move over the network."""
        if self.server and self.is_host:
            self.server.send_move(row, col)
        elif self.client and not self.is_host:
            self.client.send_move(row, col)
    
    def _check_game_end(self) -> bool:
        """Check if the game has ended."""
        winner = self.state.board.check_winner()
        
        if winner:
            # Someone won
            if winner == SYMBOL_O:
                self.state.player_o.add_win()
                next_starter = PLAYER_O
            else:
                self.state.player_x.add_win()
                next_starter = PLAYER_X
            
            if self.view:
                self.view.update_scores(
                    self.state.player_o.wins,
                    self.state.player_x.wins
                )
            
            self._start_new_round(next_starter)
            return True
        
        if self.state.board.is_full():
            # Draw
            self._start_new_round(PLAYER_O)
            return True
        
        return False
    
    def _start_new_round(self, starting_player: int):
        """Start a new round after game ends."""
        self.state.reset_game()
        self.state.current_player_index = starting_player
        
        # Determine if it's our turn in the new round
        self.is_my_turn = (starting_player == self.local_player_index)
        
        if self.view:
            self.view.schedule_board_reset()
            self.view.root.after(1100, self._update_turn_indicator)
    
    def _update_turn_indicator(self):
        """Update the UI to show whose turn it is."""
        if self.view:
            self.view.update_current_player_indicator(self.state.current_player.symbol)
    
    def _on_disconnect(self):
        """Handle opponent disconnect."""
        self.is_connected = False
        if self._on_opponent_disconnect:
            # Schedule on main thread
            if self.view:
                self.view.root.after(0, self._on_opponent_disconnect)
    
    def change_theme(self):
        """Change to a random theme."""
        from random import randrange
        from config import COLOR_THEMES, NUM_THEMES
        
        self.state.theme_index = randrange(NUM_THEMES)
        theme = COLOR_THEMES[self.state.theme_index]
        
        if self.view:
            self.view.apply_theme(theme[0], theme[1])
