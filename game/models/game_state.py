"""GameState model - Manages overall game state."""

from config import PLAYER_O, PLAYER_X, SYMBOL_O, SYMBOL_X, DEFAULT_THEME_INDEX
from models.board import Board
from models.player import Player


class GameState:
    """Manages the overall state of the game."""
    
    def __init__(self):
        """Initialize game state."""
        self.board = Board()
        self.players = [
            Player(SYMBOL_O),  # Player O (index 0)
            Player(SYMBOL_X),  # Player X (index 1)
        ]
        self.current_player_index = PLAYER_O
        self.moves_count = 0
        self.theme_index = DEFAULT_THEME_INDEX
        self.is_game_active = False
    
    @property
    def current_player(self) -> Player:
        """Get the current player."""
        return self.players[self.current_player_index]
    
    @property
    def other_player(self) -> Player:
        """Get the non-current player."""
        other_index = 1 - self.current_player_index
        return self.players[other_index]
    
    @property
    def player_o(self) -> Player:
        """Get player O."""
        return self.players[PLAYER_O]
    
    @property
    def player_x(self) -> Player:
        """Get player X."""
        return self.players[PLAYER_X]
    
    def switch_player(self):
        """Switch to the other player."""
        self.current_player_index = 1 - self.current_player_index
    
    def increment_moves(self):
        """Increment the move counter."""
        self.moves_count += 1
    
    def reset_game(self):
        """Reset the game for a new round (keeps scores)."""
        self.board.reset()
        self.moves_count = 0
    
    def reset_all(self):
        """Full reset including scores."""
        self.reset_game()
        self.current_player_index = PLAYER_O
        for player in self.players:
            player.reset_wins()
    
    def start_game(self):
        """Start a new game."""
        self.is_game_active = True
        self.reset_game()
        self.current_player_index = PLAYER_O
    
    def end_game(self):
        """End the current game."""
        self.is_game_active = False
        self.reset_all()
