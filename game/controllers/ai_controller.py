"""AI Controller - Computer opponent logic."""

from random import choice
from config import BOARD_SIZE, EMPTY_CELL, SYMBOL_X, SYMBOL_O, CORNER_POSITIONS
from models.board import Board


class AIController:
    """Handles computer opponent move selection."""
    
    def __init__(self):
        """Initialize AI controller."""
        pass
    
    def find_best_move(self, board: Board) -> tuple[int, int] | None:
        """
        Find the best move for the computer (X).
        
        Priority:
        1. Win if possible
        2. Block opponent's win
        3. Take a corner
        4. Take any available cell
        
        Args:
            board: Current game board
            
        Returns:
            (row, col) tuple for best move, or None if no moves available
        """
        # Try to win
        win_move = self._find_winning_move(board, SYMBOL_X)
        if win_move:
            return win_move
        
        # Block opponent's win
        block_move = self._find_winning_move(board, SYMBOL_O)
        if block_move:
            return block_move
        
        # Take center if available
        if board.get_cell(1, 1) == EMPTY_CELL:
            return (1, 1)
        
        # Take a corner
        corner_move = self._find_corner_move(board)
        if corner_move:
            return corner_move
        
        # Take any available cell
        empty_cells = board.get_empty_cells()
        if empty_cells:
            return choice(empty_cells)
        
        return None
    
    def _find_winning_move(self, board: Board, symbol: str) -> tuple[int, int] | None:
        """
        Find a move that would win for the given symbol.
        
        Args:
            board: Current game board
            symbol: Symbol to check for ('x' or 'o')
            
        Returns:
            (row, col) if winning move found, None otherwise
        """
        # Check rows
        for row in range(BOARD_SIZE):
            cells = [board.get_cell(row, col) for col in range(BOARD_SIZE)]
            move = self._check_line_for_win(cells, symbol)
            if move is not None:
                return (row, move)
        
        # Check columns
        for col in range(BOARD_SIZE):
            cells = [board.get_cell(row, col) for row in range(BOARD_SIZE)]
            move = self._check_line_for_win(cells, symbol)
            if move is not None:
                return (move, col)
        
        # Check main diagonal
        cells = [board.get_cell(i, i) for i in range(BOARD_SIZE)]
        move = self._check_line_for_win(cells, symbol)
        if move is not None:
            return (move, move)
        
        # Check anti-diagonal
        cells = [board.get_cell(i, BOARD_SIZE - 1 - i) for i in range(BOARD_SIZE)]
        move = self._check_line_for_win(cells, symbol)
        if move is not None:
            return (move, BOARD_SIZE - 1 - move)
        
        return None
    
    def _check_line_for_win(self, cells: list, symbol: str) -> int | None:
        """
        Check if a line (row, col, or diagonal) has a winning opportunity.
        
        Args:
            cells: List of 3 cell values
            symbol: Symbol to check for
            
        Returns:
            Index of empty cell if 2 symbols + 1 empty, None otherwise
        """
        symbol_count = cells.count(symbol)
        empty_count = cells.count(EMPTY_CELL)
        
        if symbol_count == 2 and empty_count == 1:
            return cells.index(EMPTY_CELL)
        
        return None
    
    def _find_corner_move(self, board: Board) -> tuple[int, int] | None:
        """Find an available corner position."""
        available_corners = [
            pos for pos in CORNER_POSITIONS 
            if board.get_cell(pos[0], pos[1]) == EMPTY_CELL
        ]
        if available_corners:
            return choice(available_corners)
        return None
