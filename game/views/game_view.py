"""Game View - Handles all visual rendering of the game."""

from tkinter import Canvas, Label, Radiobutton, Checkbutton, IntVar
from random import randrange

from config import (
    CANVAS_WIDTH, DRAWING_CANVAS_HEIGHT, GAME_CANVAS_HEIGHT,
    GRID_VERTICAL_LEFT, GRID_VERTICAL_RIGHT,
    GRID_HORIZONTAL_TOP, GRID_HORIZONTAL_BOTTOM,
    GRID_START_X, GRID_END_X, GRID_START_Y, GRID_END_Y,
    GRID_LINE_WIDTH, GRID_LINE_CLICK_RANGE,
    CELL_SIZE, CELL_OFFSET_X, CELL_OFFSET_Y,
    SYMBOL_RADIUS, X_LINE_WIDTH, O_LINE_WIDTH,
    COLOR_THEMES, DEFAULT_BACKGROUND, DEFAULT_GRID,
    SYMBOL_COLORS, DRAWING_COLORS,
    TOP_ROW_MIN_Y, TOP_ROW_MAX_Y,
    MIDDLE_ROW_MIN_Y, MIDDLE_ROW_MAX_Y,
    BOTTOM_ROW_MIN_Y, BOTTOM_ROW_MAX_Y,
    LEFT_COL_MIN_X, LEFT_COL_MAX_X,
    MIDDLE_COL_MIN_X, MIDDLE_COL_MAX_X,
    RIGHT_COL_MIN_X, RIGHT_COL_MAX_X,
    THEME_CHANGE_Y_THRESHOLD,
    LABEL_PADDING_X, LABEL_PADDING_Y,
    COMPUTER_MODE_TEXT, O_WIN_DELAY,
    MIN_RADIUS, MAX_RADIUS, RADIUS_STEP,
    MIN_WIDTH, MAX_WIDTH, WIDTH_STEP,
    MIN_POSITION, MAX_POSITION, INITIAL_SHAPES_COUNT,
    PLAYER_O, PLAYER_X, SYMBOL_O
)


class GameView:
    """Handles all visual rendering for the Tic-Tac-Toe game."""
    
    def __init__(self, root, controller=None):
        """
        Initialize the game view.
        
        Args:
            root: Tkinter root window
            controller: Game controller (can be set later)
        """
        self.root = root
        self.controller = controller
        self.theme_index = 1
        
        # Create canvases
        self.drawing_canvas = Canvas(
            root,
            height=DRAWING_CANVAS_HEIGHT,
            width=CANVAS_WIDTH,
            background=DEFAULT_BACKGROUND
        )
        self.game_canvas = Canvas(
            root,
            height=GAME_CANVAS_HEIGHT,
            width=CANVAS_WIDTH,
            background=DEFAULT_GRID
        )
        
        # UI elements (created when game starts)
        self.o_wins_label = None
        self.x_wins_label = None
        self.player_o_radio = None
        self.player_x_radio = None
        self.computer_mode_check = None
        self.starting_player_var = IntVar()
        self.computer_mode_var = IntVar()
        
        # Place canvases
        self.drawing_canvas.grid(column=0, row=4, columnspan=3)
        self.game_canvas.grid(column=0, row=5, columnspan=3)
        
        # Draw initial decorations
        self._draw_random_shapes(INITIAL_SHAPES_COUNT)
        
        # Bind drawing canvas events
        self.drawing_canvas.bind("<Button>", self._on_drawing_click)
        self.drawing_canvas.bind("<Button-3>", self._clear_drawing)
    
    def set_controller(self, controller):
        """Set the controller reference."""
        self.controller = controller
    
    def setup_game_ui(self):
        """Set up game UI elements (called when game starts)."""
        # Score labels
        self.o_wins_label = Label(
            self.root,
            text="O\n0",
            background=DEFAULT_BACKGROUND
        )
        self.x_wins_label = Label(
            self.root,
            text="X\n0",
            background=DEFAULT_BACKGROUND
        )
        
        # Player radio buttons
        self.player_o_radio = Radiobutton(
            self.root,
            text='',
            variable=self.starting_player_var,
            value=PLAYER_O,
            command=self._on_starting_player_change
        )
        self.player_x_radio = Radiobutton(
            self.root,
            text='',
            variable=self.starting_player_var,
            value=PLAYER_X,
            command=self._on_starting_player_change
        )
        
        # Computer mode checkbox
        self.computer_mode_check = Checkbutton(
            self.root,
            text=COMPUTER_MODE_TEXT,
            variable=self.computer_mode_var,
            command=self._on_computer_mode_toggle
        )
        
        # Place UI elements
        self.o_wins_label.grid(column=0, row=1, ipadx=LABEL_PADDING_X, ipady=LABEL_PADDING_Y)
        self.x_wins_label.grid(column=2, row=1, ipadx=LABEL_PADDING_X, ipady=LABEL_PADDING_Y)
        self.player_o_radio.grid(column=0, row=2)
        self.player_x_radio.grid(column=2, row=2)
        self.computer_mode_check.grid(column=0, columnspan=3, row=7, sticky='w')
        
        # Default selection
        self.player_o_radio.select()
        
        # Bind game canvas click
        self.game_canvas.bind("<Button-1>", self._on_board_click)
    
    def cleanup_game_ui(self):
        """Remove game UI elements (called when exiting game)."""
        if self.o_wins_label:
            self.o_wins_label.destroy()
            self.o_wins_label = None
        if self.x_wins_label:
            self.x_wins_label.destroy()
            self.x_wins_label = None
        if self.player_o_radio:
            self.player_o_radio.destroy()
            self.player_o_radio = None
        if self.player_x_radio:
            self.player_x_radio.destroy()
            self.player_x_radio = None
        if self.computer_mode_check:
            self.computer_mode_check.destroy()
            self.computer_mode_check = None
        
        # Unbind click
        self.game_canvas.unbind("<Button-1>")
    
    def swap_canvas_sizes(self, game_active: bool):
        """Swap canvas sizes based on game state."""
        if game_active:
            self.drawing_canvas.configure(height=GAME_CANVAS_HEIGHT, width=CANVAS_WIDTH)
            self.game_canvas.configure(height=DRAWING_CANVAS_HEIGHT, width=CANVAS_WIDTH)
            self.drawing_canvas.delete("all")
        else:
            self.drawing_canvas.configure(height=DRAWING_CANVAS_HEIGHT, width=CANVAS_WIDTH)
            self.game_canvas.configure(height=GAME_CANVAS_HEIGHT, width=CANVAS_WIDTH)
            self._draw_random_shapes(INITIAL_SHAPES_COUNT)
    
    def draw_grid(self, color=None):
        """Draw the game grid lines."""
        if color is None:
            color = COLOR_THEMES[self.theme_index][1]
        
        # Vertical lines
        self.game_canvas.create_line(
            GRID_VERTICAL_LEFT, GRID_START_Y,
            GRID_VERTICAL_LEFT, GRID_END_Y,
            width=GRID_LINE_WIDTH, fill=color
        )
        self.game_canvas.create_line(
            GRID_VERTICAL_RIGHT, GRID_START_Y,
            GRID_VERTICAL_RIGHT, GRID_END_Y,
            width=GRID_LINE_WIDTH, fill=color
        )
        
        # Horizontal lines
        self.game_canvas.create_line(
            GRID_START_X, GRID_HORIZONTAL_TOP,
            GRID_END_X, GRID_HORIZONTAL_TOP,
            width=GRID_LINE_WIDTH, fill=color
        )
        self.game_canvas.create_line(
            GRID_START_X, GRID_HORIZONTAL_BOTTOM,
            GRID_END_X, GRID_HORIZONTAL_BOTTOM,
            width=GRID_LINE_WIDTH, fill=color
        )
    
    def draw_x(self, row: int, col: int, click_x: int = None, click_y: int = None):
        """Draw X symbol at the specified position."""
        color = self._get_random_symbol_color()
        
        if click_x is not None and click_y is not None:
            x, y = click_x, click_y
        else:
            x = (col * CELL_SIZE) + CELL_OFFSET_X
            y = CELL_OFFSET_Y + (row * CELL_SIZE)
        
        self.game_canvas.create_line(
            x + SYMBOL_RADIUS, y - SYMBOL_RADIUS,
            x - SYMBOL_RADIUS, y + SYMBOL_RADIUS,
            width=X_LINE_WIDTH, fill=color
        )
        self.game_canvas.create_line(
            x - SYMBOL_RADIUS, y - SYMBOL_RADIUS,
            x + SYMBOL_RADIUS, y + SYMBOL_RADIUS,
            width=X_LINE_WIDTH, fill=color
        )
    
    def draw_o(self, row: int, col: int, click_x: int = None, click_y: int = None):
        """Draw O symbol at the specified position."""
        color = self._get_random_symbol_color()
        
        if click_x is not None and click_y is not None:
            x, y = click_x, click_y
        else:
            x = (col * CELL_SIZE) + CELL_OFFSET_X
            y = CELL_OFFSET_Y + (row * CELL_SIZE)
        
        self.game_canvas.create_oval(
            x - SYMBOL_RADIUS, y - SYMBOL_RADIUS,
            x + SYMBOL_RADIUS, y + SYMBOL_RADIUS,
            width=O_LINE_WIDTH, outline=color
        )
    
    def clear_board(self):
        """Clear the game canvas."""
        self.game_canvas.delete("all")
    
    def schedule_board_reset(self):
        """Schedule board reset with delay."""
        self.root.after(O_WIN_DELAY, self._delayed_board_reset)
    
    def _delayed_board_reset(self):
        """Reset board after delay."""
        self.clear_board()
        self.draw_grid()
    
    def update_scores(self, o_wins: int, x_wins: int):
        """Update the score display."""
        if self.o_wins_label:
            self.o_wins_label.configure(text=f"O\n{o_wins}")
        if self.x_wins_label:
            self.x_wins_label.configure(text=f"X\n{x_wins}")
    
    def update_current_player_indicator(self, symbol: str):
        """Update the radio button to show current player."""
        if symbol == SYMBOL_O and self.player_o_radio:
            self.player_o_radio.select()
        elif self.player_x_radio:
            self.player_x_radio.select()
    
    def apply_theme(self, bg_color: str, grid_color: str):
        """Apply a color theme."""
        self.drawing_canvas.configure(background=grid_color)
        self.game_canvas.configure(background=bg_color)
        self.clear_board()
        self.draw_grid(grid_color)
        
        if self.o_wins_label:
            self.o_wins_label.configure(background=bg_color)
        if self.x_wins_label:
            self.x_wins_label.configure(background=bg_color)
    
    def get_cell_from_click(self, x: int, y: int) -> tuple[int, int]:
        """
        Convert click coordinates to grid cell.
        
        Returns:
            (row, col) tuple, or (-1, -1) if not a valid cell
        """
        row, col = -1, -1
        
        # Check if click is on grid lines (for theme change)
        if self._is_grid_line_click(x, y):
            if self.controller:
                self.controller.change_theme()
            return (-1, -1)
        
        # Determine row
        if TOP_ROW_MIN_Y < y < TOP_ROW_MAX_Y:
            row = 0
        elif MIDDLE_ROW_MIN_Y < y < MIDDLE_ROW_MAX_Y:
            row = 1
        elif BOTTOM_ROW_MIN_Y < y < BOTTOM_ROW_MAX_Y:
            row = 2
        
        # Determine column
        if LEFT_COL_MIN_X < x < LEFT_COL_MAX_X:
            col = 0
        elif MIDDLE_COL_MIN_X < x < MIDDLE_COL_MAX_X:
            col = 1
        elif RIGHT_COL_MIN_X < x < RIGHT_COL_MAX_X:
            col = 2
        
        return (row, col)
    
    def _is_grid_line_click(self, x: int, y: int) -> bool:
        """Check if click is on a grid line."""
        if y > THEME_CHANGE_Y_THRESHOLD:
            return True
        if GRID_VERTICAL_LEFT - GRID_LINE_CLICK_RANGE < x < GRID_VERTICAL_LEFT + GRID_LINE_CLICK_RANGE:
            return True
        if GRID_VERTICAL_RIGHT - GRID_LINE_CLICK_RANGE < x < GRID_VERTICAL_RIGHT + GRID_LINE_CLICK_RANGE:
            return True
        if GRID_HORIZONTAL_TOP - GRID_LINE_CLICK_RANGE < y < GRID_HORIZONTAL_TOP + GRID_LINE_CLICK_RANGE:
            return True
        if GRID_HORIZONTAL_BOTTOM - GRID_LINE_CLICK_RANGE < y < GRID_HORIZONTAL_BOTTOM + GRID_LINE_CLICK_RANGE:
            return True
        return False
    
    def _on_board_click(self, event):
        """Handle board click event."""
        row, col = self.get_cell_from_click(event.x, event.y)
        if row >= 0 and col >= 0 and self.controller:
            self.controller.handle_cell_click(row, col, event.x, event.y)
    
    def _on_starting_player_change(self):
        """Handle starting player radio button change."""
        if self.controller:
            self.controller.set_starting_player(self.starting_player_var.get())
    
    def _on_computer_mode_toggle(self):
        """Handle computer mode checkbox toggle."""
        if self.controller:
            self.controller.toggle_computer_mode()
    
    def _get_random_symbol_color(self) -> str:
        """Get a random color for symbols."""
        return SYMBOL_COLORS[randrange(len(SYMBOL_COLORS))]
    
    def _get_random_drawing_color(self) -> str:
        """Get a random color for drawing."""
        return DRAWING_COLORS[randrange(len(DRAWING_COLORS))]
    
    def _draw_random_shapes(self, count: int):
        """Draw random decorative shapes on drawing canvas."""
        for _ in range(count):
            x = randrange(MIN_POSITION, MAX_POSITION)
            y = randrange(MIN_POSITION, MAX_POSITION)
            r = randrange(MIN_RADIUS, MAX_RADIUS, RADIUS_STEP)
            
            self.drawing_canvas.create_oval(
                x - r, y - r, x + r, y + r,
                width=randrange(MIN_WIDTH, MAX_WIDTH, WIDTH_STEP),
                outline=self._get_random_drawing_color()
            )
            
            x = randrange(MIN_POSITION, MAX_POSITION)
            y = randrange(MIN_POSITION, MAX_POSITION)
            r = randrange(MAX_RADIUS)
            
            self.drawing_canvas.create_line(
                x + r, y - r, x - r, y + r,
                width=randrange(MIN_WIDTH, MAX_WIDTH, WIDTH_STEP),
                fill=self._get_random_drawing_color()
            )
            self.drawing_canvas.create_line(
                x - r, y - r, x + r, y + r,
                width=randrange(MIN_WIDTH, MAX_WIDTH, WIDTH_STEP),
                fill=self._get_random_drawing_color()
            )
    
    def _on_drawing_click(self, event):
        """Handle drawing canvas click."""
        color = self._get_random_drawing_color()
        r = randrange(MIN_RADIUS, MAX_RADIUS, RADIUS_STEP)
        
        if event.y > THEME_CHANGE_Y_THRESHOLD:
            self.drawing_canvas.configure(background=color)
        else:
            self.drawing_canvas.create_oval(
                event.x - r, event.y - r,
                event.x + r, event.y + r,
                width=randrange(MIN_WIDTH, MAX_WIDTH, WIDTH_STEP),
                outline=color
            )
    
    def _clear_drawing(self, event):
        """Clear the drawing canvas."""
        self.drawing_canvas.delete("all")
