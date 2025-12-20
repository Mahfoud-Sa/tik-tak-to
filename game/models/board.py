"""Board model - Manages the game board state and win detection."""

from config import BOARD_SIZE, EMPTY_CELL, SYMBOL_O, SYMBOL_X


class Board:
    """Represents the Tic-Tac-Toe game board."""
    
    def __init__(self):
        """Initialize an empty board."""
        self.cells = [[EMPTY_CELL for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    
    def make_move(self, row: int, col: int, symbol: str) -> bool:
        """
        Attempt to place a symbol at the specified position.
        
        Args:
            row: Row index (0-2)
            col: Column index (0-2)
            symbol: 'x' or 'o'
            
        Returns:
            True if move was successful, False if cell was occupied
        """
        if self.cells[row][col] == EMPTY_CELL:
            self.cells[row][col] = symbol
            return True
        return False
    
    def check_winner(self) -> str | None:
        """
        Check if there's a winner.
        
        Returns:
            The winning symbol ('x' or 'o') or None if no winner
        """
        # Check rows
        for row in range(BOARD_SIZE):
            if (self.cells[row][0] != EMPTY_CELL and 
                self.cells[row][0] == self.cells[row][1] == self.cells[row][2]):
                return self.cells[row][0]
        
        # Check columns
        for col in range(BOARD_SIZE):
            if (self.cells[0][col] != EMPTY_CELL and 
                self.cells[0][col] == self.cells[1][col] == self.cells[2][col]):
                return self.cells[0][col]
        
        # Check diagonals
        if (self.cells[0][0] != EMPTY_CELL and 
            self.cells[0][0] == self.cells[1][1] == self.cells[2][2]):
            return self.cells[0][0]
        
        if (self.cells[0][2] != EMPTY_CELL and 
            self.cells[0][2] == self.cells[1][1] == self.cells[2][0]):
            return self.cells[0][2]
        
        return None
    
    def is_full(self) -> bool:
        """Check if the board is full (draw condition)."""
        for row in self.cells:
            for cell in row:
                if cell == EMPTY_CELL:
                    return False
        return True
    
    def get_empty_cells(self) -> list[tuple[int, int]]:
        """Get list of all empty cell positions."""
        empty = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.cells[row][col] == EMPTY_CELL:
                    empty.append((row, col))
        return empty
    
    def reset(self):
        """Reset the board to empty state."""
        self.cells = [[EMPTY_CELL for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    
    def get_cell(self, row: int, col: int):
        """Get the value at a specific cell."""
        return self.cells[row][col]
