"""Player model - Represents a game player."""

from config import SYMBOL_O, SYMBOL_X


class Player:
    """Represents a player in the game."""
    
    def __init__(self, symbol: str, is_computer: bool = False):
        """
        Initialize a player.
        
        Args:
            symbol: Player's symbol ('x' or 'o')
            is_computer: True if this is a computer player
        """
        self.symbol = symbol
        self.is_computer = is_computer
        self.wins = 0
    
    def add_win(self):
        """Increment the player's win count."""
        self.wins += 1
    
    def reset_wins(self):
        """Reset win count to zero."""
        self.wins = 0
    
    @property
    def display_name(self) -> str:
        """Get display name for the player."""
        return self.symbol.upper()
