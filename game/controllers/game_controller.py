"""Game Controller - Main game logic and flow control."""

from random import randrange
from config import (
    PLAYER_O, PLAYER_X, SYMBOL_O, SYMBOL_X,
    COLOR_THEMES, NUM_THEMES
)
from models.game_state import GameState


class GameController:
    """Controls game flow and handles player actions."""
    
    def __init__(self, game_state: GameState, view=None):
        """
        Initialize the game controller.
        
        Args:
            game_state: The game state model
            view: The game view (set later to avoid circular import)
        """
        self.state = game_state
        self.view = view
        self._on_game_start_callback = None
        self._on_game_end_callback = None
    
    def set_view(self, view):
        """Set the view reference."""
        self.view = view
    
    def set_callbacks(self, on_game_start=None, on_game_end=None):
        """Set callbacks for game events."""
        self._on_game_start_callback = on_game_start
        self._on_game_end_callback = on_game_end
    
    def start_game(self):
        """Start a new game."""
        self.state.start_game()
        if self.view:
            self.view.clear_board()
            self.view.draw_grid()
            self.view.update_scores(
                self.state.player_o.wins,
                self.state.player_x.wins
            )
        if self._on_game_start_callback:
            self._on_game_start_callback()
    
    def exit_game(self):
        """Exit the current game."""
        self.state.end_game()
        if self.view:
            self.view.clear_board()
        if self._on_game_end_callback:
            self._on_game_end_callback()
    
    def handle_cell_click(self, row: int, col: int, click_x: int = None, click_y: int = None):
        """
        Handle a cell click from the player.
        
        Args:
            row: Row index (0-2)
            col: Column index (0-2)
            click_x: Actual x coordinate for drawing (optional)
            click_y: Actual y coordinate for drawing (optional)
        """
        if not self.state.is_game_active:
            return
        
        if row < 0 or col < 0:
            return
        
        current = self.state.current_player
        
        # Try to make the move
        if self.state.board.make_move(row, col, current.symbol):
            # Draw the symbol
            if self.view:
                if current.symbol == SYMBOL_O:
                    self.view.draw_o(row, col, click_x, click_y)
                else:
                    self.view.draw_x(row, col, click_x, click_y)
                self.view.update_current_player_indicator(current.symbol)
            
            self.state.increment_moves()
            
            # Check for game end
            if self._check_game_end():
                return
            
            # Switch player
            self.state.switch_player()
            
            if self.view:
                self.view.update_current_player_indicator(self.state.current_player.symbol)
    
    def _check_game_end(self) -> bool:
        """
        Check if the game has ended (win or draw).
        
        Returns:
            True if game ended, False otherwise
        """
        winner = self.state.board.check_winner()
        
        if winner:
            # Someone won
            if winner == SYMBOL_O:
                self.state.player_o.add_win()
                next_player = PLAYER_O
            else:
                self.state.player_x.add_win()
                next_player = PLAYER_X
            
            if self.view:
                self.view.update_scores(
                    self.state.player_o.wins,
                    self.state.player_x.wins
                )
            
            self._start_new_round(next_player)
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
        
        if self.view:
            self.view.schedule_board_reset()
            self.view.update_current_player_indicator(self.state.current_player.symbol)
    
    def change_theme(self):
        """Change to a random theme."""
        self.state.theme_index = randrange(NUM_THEMES)
        theme = COLOR_THEMES[self.state.theme_index]
        
        if self.view:
            self.view.apply_theme(theme[0], theme[1])
    
    def set_starting_player(self, player_index: int):
        """Set which player starts the next round."""
        if not self.state.is_game_active or self.state.moves_count == 0:
            self.state.current_player_index = player_index
            if self.view:
                self.view.update_current_player_indicator(self.state.current_player.symbol)
