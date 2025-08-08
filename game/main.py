from tkinter import *
from random import randrange
import webbrowser
from tkinter import messagebox as msg
import os
from os import path
from config import *

# Global game state variables
drawing_counter = 0
current_player = PLAYER_O  # 0 = O, 1 = X
x_wins = 0
o_wins = 0
moves_count = 0
current_theme_index = DEFAULT_THEME_INDEX
computer_selected = 0

# Game board (3x3 grid)
game_board = [
    [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
    [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
    [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL]
]

def handle_two_players_click(event=1):
    """Bind click handler based on current player"""
    if current_player == 0:
        game_canvas.bind("<Button-1>", on_board_click_player_o)
    else:
        game_canvas.bind("<Button-1>", on_board_click_player_x)

def handle_click_based_on_mode(event=1):
    """Handle click based on game mode (player vs player or vs computer)"""
    global current_player
    if current_player % 2 == 0:
        player_o_radio.select()
        on_board_click_player_o(event)
    else:
        root.after(COMPUTER_MOVE_DELAY, computer_play)

def computer_try_win_or_block():
    """Computer AI: Try to win or block player's win"""
    # Try to win
    if try_win('x') or try_block('o') or make_random_move():
        pass

def try_win(symbol):
    """Try to find winning move for given symbol"""
    # Horizontal checks
    for row in range(BOARD_SIZE):
        if game_board[row][0] == symbol and game_board[row][1] == symbol and game_board[row][2] == EMPTY_CELL:
            computer_draw_x(row, 2)
            return True
        if game_board[row][1] == symbol and game_board[row][2] == symbol and game_board[row][0] == EMPTY_CELL:
            computer_draw_x(row, 0)
            return True
        if game_board[row][0] == symbol and game_board[row][2] == symbol and game_board[row][1] == EMPTY_CELL:
            computer_draw_x(row, 1)
            return True
    
    # Vertical checks
    for col in range(BOARD_SIZE):
        if game_board[0][col] == symbol and game_board[1][col] == symbol and game_board[2][col] == EMPTY_CELL:
            computer_draw_x(2, col)
            return True
        if game_board[1][col] == symbol and game_board[2][col] == symbol and game_board[0][col] == EMPTY_CELL:
            computer_draw_x(0, col)
            return True
        if game_board[0][col] == symbol and game_board[2][col] == symbol and game_board[1][col] == EMPTY_CELL:
            computer_draw_x(1, col)
            return True
    
    # Diagonal checks
    if game_board[0][0] == symbol and game_board[1][1] == symbol and game_board[2][2] == EMPTY_CELL:
        computer_draw_x(2, 2)
        return True
    if game_board[2][2] == symbol and game_board[1][1] == symbol and game_board[0][0] == EMPTY_CELL:
        computer_draw_x(0, 0)
        return True
    if game_board[2][2] == symbol and game_board[0][0] == symbol and game_board[1][1] == EMPTY_CELL:
        computer_draw_x(1, 1)
        return True
    if game_board[0][2] == symbol and game_board[1][1] == symbol and game_board[2][0] == EMPTY_CELL:
        computer_draw_x(2, 0)
        return True
    if game_board[2][0] == symbol and game_board[1][1] == symbol and game_board[0][2] == EMPTY_CELL:
        computer_draw_x(0, 2)
        return True
    
    return False

def try_block(symbol):
    """Try to block opponent's winning move"""
    return try_win(symbol)

def make_random_move():
    """Computer makes a random valid move"""
    global game_board, game_canvas
    
    # Prefer corners if available
    for row, col in CORNER_POSITIONS:
        if game_board[row][col] == EMPTY_CELL:
            computer_draw_x(row, col)
            return True
    
    # Otherwise random move
    while True:
        row, col = randrange(BOARD_SIZE), randrange(BOARD_SIZE)
        if game_board[row][col] == EMPTY_CELL:
            computer_draw_x(row, col)
            return True

def computer_play(event=1):
    """Handle computer's move"""
    global current_player, game_board
    computer_try_win_or_block()
    current_player += 1
    check_win_or_draw()
    handle_click_based_on_mode()

def change_theme(event=1):
    """Change the game theme randomly"""
    global current_theme_index
    current_theme_index = randrange(NUM_THEMES)
    draw_grid(COLOR_THEMES[current_theme_index][1])
    drawing_canvas.configure(background=COLOR_THEMES[current_theme_index][1])
    game_canvas.configure(background=COLOR_THEMES[current_theme_index][0])

def update_starting_player():
    """Update starting player based on radio button selection"""
    global current_player
    selected_player = starting_player_var.get()
    if selected_player == 0:
        current_player = 0
    elif selected_player == 1:
        current_player = 1

def reset_board_canvas():
    """Reset the game board canvas"""
    game_canvas.delete("all")
    draw_grid(COLOR_THEMES[current_theme_index][1])

def check_win_or_draw():
    """Check if game is won or drawn"""
    global x_wins, o_wins, current_player, moves_count, game_board
    
    moves_count += 1
    
    # Check for O win
    if check_win(SYMBOL_O):
        o_wins += 1
        o_wins_label.configure(text=f"O\n{o_wins}")
        game_canvas.after(O_WIN_DELAY, reset_board_canvas)
        current_player = PLAYER_O
        moves_count = 0
        player_o_radio.select()
        reset_board()
        update_score_display()
        return
    
    # Check for X win
    if check_win(SYMBOL_X):
        x_wins += 1
        x_wins_label.configure(text=f"X\n{x_wins}")
        game_canvas.after(X_WIN_DELAY, reset_board_canvas)
        current_player = PLAYER_X
        moves_count = 0
        reset_board()
        player_x_radio.select()
        update_score_display()
        return
    
    # Check for draw
    if moves_count == MAX_MOVES:
        game_canvas.after(X_WIN_DELAY, reset_board_canvas)
        current_player = PLAYER_O
        moves_count = 0
        reset_board()
        update_score_display()

def check_win(symbol):
    """Check if player has won with given symbol"""
    # Horizontal wins
    for row in range(BOARD_SIZE):
        if game_board[row][0] == symbol and game_board[row][1] == symbol and game_board[row][2] == symbol:
            return True
    
    # Vertical wins
    for col in range(BOARD_SIZE):
        if game_board[0][col] == symbol and game_board[1][col] == symbol and game_board[2][col] == symbol:
            return True
    
    # Diagonal wins
    if game_board[0][0] == symbol and game_board[1][1] == symbol and game_board[2][2] == symbol:
        return True
    if game_board[0][2] == symbol and game_board[1][1] == symbol and game_board[2][0] == symbol:
        return True
    
    return False

def clear_drawing_canvas(event):
    """Clear the drawing canvas"""
    drawing_canvas.delete("all")

def on_drawing_canvas_click(event):
    """Handle drawing canvas click events"""
    global drawing_counter, current_theme_index
    
    color = get_random_color()
    radius = randrange(MIN_RADIUS, MAX_RADIUS, RADIUS_STEP)
    
    if event.y > THEME_CHANGE_Y_THRESHOLD:  # Change background
        drawing_canvas.configure(background=color)
    else:
        if drawing_counter % 2 == 0:
            drawing_canvas.create_oval(
                event.x - radius, event.y - radius,
                event.x + radius, event.y + radius,
                width=randrange(MIN_WIDTH, MAX_WIDTH, WIDTH_STEP),
                outline=color
            )
        else:
            drawing_canvas.create_line(
                event.x + radius, event.y - radius,
                event.x - radius, event.y + radius,
                width=randrange(MIN_WIDTH, MAX_WIDTH, WIDTH_STEP),
                fill=color
            )
            drawing_canvas.create_line(
                event.x - radius, event.y - radius,
                event.x + radius, event.y + radius,
                width=randrange(MIN_WIDTH, MAX_WIDTH, WIDTH_STEP),
                fill=color
            )
    
    drawing_counter += 1

def exit_game():
    """Exit game and reset state"""
    global drawing_counter, current_player, x_wins, o_wins, game_board
    
    drawing_counter = 0
    current_player = PLAYER_O
    x_wins = 0
    o_wins = 0
    game_board = [[EMPTY_CELL,EMPTY_CELL,EMPTY_CELL], [EMPTY_CELL,EMPTY_CELL,EMPTY_CELL], [EMPTY_CELL,EMPTY_CELL,EMPTY_CELL]]
    
    o_wins_label.configure(text="O\n0", background=DEFAULT_BACKGROUND)
    x_wins_label.configure(text="X\n0", background=DEFAULT_BACKGROUND)
    
    game_canvas.configure(height=GAME_CANVAS_HEIGHT, width=CANVAS_WIDTH)
    drawing_canvas.configure(height=DRAWING_CANVAS_HEIGHT, width=CANVAS_WIDTH)
    
    draw_random_shapes(INITIAL_SHAPES_COUNT)
    play_button.configure(command=start_game, text=PLAY_BUTTON_TEXT)
    game_canvas.delete("all")
    
    # Clean up UI elements
    x_wins_label.destroy()
    o_wins_label.destroy()
    player_x_radio.destroy()
    player_o_radio.destroy()
    computer_mode_check.destroy()

def start_game():
    """Start the X/O game"""
    global moves_count, current_player
    
    game_canvas.bind("<Button-1>", handle_two_players_click)
    moves_count = 0
    play_button.configure(command=exit_game, text=EXIT_BUTTON_TEXT)
    game_canvas.delete("all")
    drawing_canvas.configure(height=GAME_CANVAS_HEIGHT, width=CANVAS_WIDTH)
    game_canvas.configure(height=DRAWING_CANVAS_HEIGHT, width=CANVAS_WIDTH)
    drawing_canvas.delete("all")
    root.after(UI_SETUP_DELAY, setup_game_ui)
    draw_grid(COLOR_THEMES[current_theme_index][1])
    current_player = PLAYER_O

def get_random_color():
    """Get a random color for drawing"""
    return DRAWING_COLORS[randrange(len(DRAWING_COLORS))]

def get_random_xo_color():
    """Get random color for X/O symbols"""
    return SYMBOL_COLORS[randrange(len(SYMBOL_COLORS))]

def draw_x(event, canvas):
    """Draw X symbol on canvas"""
    player_x_radio.select()
    color = get_random_xo_color()
    canvas.create_line(
        event.x + SYMBOL_RADIUS, event.y - SYMBOL_RADIUS,
        event.x - SYMBOL_RADIUS, event.y + SYMBOL_RADIUS,
        width=X_LINE_WIDTH, fill=color
    )
    canvas.create_line(
        event.x - SYMBOL_RADIUS, event.y - SYMBOL_RADIUS,
        event.x + SYMBOL_RADIUS, event.y + SYMBOL_RADIUS,
        width=X_LINE_WIDTH, fill=color
    )

def draw_o(event, canvas):
    """Draw O symbol on canvas"""
    player_o_radio.select()
    canvas.create_oval(
        event.x - SYMBOL_RADIUS, event.y - SYMBOL_RADIUS,
        event.x + SYMBOL_RADIUS, event.y + SYMBOL_RADIUS,
        width=O_LINE_WIDTH, outline=get_random_xo_color()
    )

def draw_random_shapes(count):
    """Draw random shapes on drawing canvas"""
    for _ in range(count):
        x, y, r = randrange(MIN_POSITION, MAX_POSITION), randrange(MIN_POSITION, MAX_POSITION), randrange(MIN_RADIUS, MAX_RADIUS, RADIUS_STEP)
        drawing_canvas.create_oval(
            x - r, y - r,
            x + r, y + r,
            width=randrange(MIN_WIDTH, MAX_WIDTH, WIDTH_STEP),
            outline=get_random_color()
        )
        
        x, y, r = randrange(MIN_POSITION, MAX_POSITION), randrange(MIN_POSITION, MAX_POSITION), randrange(MAX_RADIUS)
        drawing_canvas.create_line(
            x + r, y - r,
            x - r, y + r,
            width=randrange(MIN_WIDTH, MAX_WIDTH, WIDTH_STEP),
            fill=get_random_color()
        )
        drawing_canvas.create_line(
            x - r, y - r,
            x + r, y + r,
            width=randrange(MIN_WIDTH, MAX_WIDTH, WIDTH_STEP),
            fill=get_random_color()
        )

def draw_grid(color):
    """Draw the game grid"""
    game_canvas.create_line(GRID_VERTICAL_LEFT, GRID_START_Y, GRID_VERTICAL_LEFT, GRID_END_Y, width=GRID_LINE_WIDTH, fill=color)
    game_canvas.create_line(GRID_VERTICAL_RIGHT, GRID_START_Y, GRID_VERTICAL_RIGHT, GRID_END_Y, width=GRID_LINE_WIDTH, fill=color)
    game_canvas.create_line(GRID_START_X, GRID_HORIZONTAL_TOP, GRID_END_X, GRID_HORIZONTAL_TOP, width=GRID_LINE_WIDTH, fill=color)
    game_canvas.create_line(GRID_START_X, GRID_HORIZONTAL_BOTTOM, GRID_END_X, GRID_HORIZONTAL_BOTTOM, width=GRID_LINE_WIDTH, fill=color)

def computer_draw_x(row, col):
    """Draw X for computer move"""
    color = get_random_xo_color()
    x = (col * CELL_SIZE) + CELL_OFFSET_X
    y = CELL_OFFSET_Y + (row * CELL_SIZE)
    
    game_canvas.create_line(x + SYMBOL_RADIUS, y - SYMBOL_RADIUS, x - SYMBOL_RADIUS, y + SYMBOL_RADIUS, width=X_LINE_WIDTH, fill=color)
    game_canvas.create_line(x - SYMBOL_RADIUS, y - SYMBOL_RADIUS, x + SYMBOL_RADIUS, y + SYMBOL_RADIUS, width=X_LINE_WIDTH, fill=color)
    game_board[row][col] = SYMBOL_X

def on_board_click_player_o(event):
    """Handle board click for player O"""
    global game_board, current_player
    
    # Change theme if grid line clicked
    if (event.y > THEME_CHANGE_Y_THRESHOLD or 
        GRID_VERTICAL_LEFT - GRID_LINE_CLICK_RANGE < event.x < GRID_VERTICAL_LEFT + GRID_LINE_CLICK_RANGE or 
        GRID_VERTICAL_RIGHT - GRID_LINE_CLICK_RANGE < event.x < GRID_VERTICAL_RIGHT + GRID_LINE_CLICK_RANGE or 
        GRID_HORIZONTAL_TOP - GRID_LINE_CLICK_RANGE < event.y < GRID_HORIZONTAL_TOP + GRID_LINE_CLICK_RANGE or 
        GRID_HORIZONTAL_BOTTOM - GRID_LINE_CLICK_RANGE < event.y < GRID_HORIZONTAL_BOTTOM + GRID_LINE_CLICK_RANGE):
        change_theme(event)
    
    # Map click position to grid cell
    row, col = -1, -1
    
    # Top row
    if TOP_ROW_MIN_Y < event.y < TOP_ROW_MAX_Y:
        if LEFT_COL_MIN_X < event.x < LEFT_COL_MAX_X: row, col = 0, 0
        elif MIDDLE_COL_MIN_X < event.x < MIDDLE_COL_MAX_X: row, col = 0, 1
        elif RIGHT_COL_MIN_X < event.x < RIGHT_COL_MAX_X: row, col = 0, 2
    
    # Middle row
    elif MIDDLE_ROW_MIN_Y < event.y < MIDDLE_ROW_MAX_Y:
        if LEFT_COL_MIN_X < event.x < LEFT_COL_MAX_X: row, col = 1, 0
        elif MIDDLE_COL_MIN_X < event.x < MIDDLE_COL_MAX_X: row, col = 1, 1
        elif RIGHT_COL_MIN_X < event.x < RIGHT_COL_MAX_X: row, col = 1, 2
    
    # Bottom row
    elif BOTTOM_ROW_MIN_Y < event.y < BOTTOM_ROW_MAX_Y:
        if LEFT_COL_MIN_X < event.x < LEFT_COL_MAX_X: row, col = 2, 0
        elif MIDDLE_COL_MIN_X < event.x < MIDDLE_COL_MAX_X: row, col = 2, 1
        elif RIGHT_COL_MIN_X < event.x < RIGHT_COL_MAX_X: row, col = 2, 2
    
    # If valid cell and empty
    if row != -1 and game_board[row][col] == EMPTY_CELL:
        draw_o(event, game_canvas)
        game_board[row][col] = SYMBOL_O
        current_player = PLAYER_X
        check_win_or_draw()
        
        if computer_mode_var.get() == 1:  # Computer mode
            handle_click_based_on_mode()
        else:  # Two-player mode
            handle_two_players_click()

def on_board_click_player_x(event):
    """Handle board click for player X"""
    global game_board, current_player
    
    # Change theme if grid line clicked
    if (event.y > THEME_CHANGE_Y_THRESHOLD or 
        GRID_VERTICAL_LEFT - GRID_LINE_CLICK_RANGE < event.x < GRID_VERTICAL_LEFT + GRID_LINE_CLICK_RANGE or 
        GRID_VERTICAL_RIGHT - GRID_LINE_CLICK_RANGE < event.x < GRID_VERTICAL_RIGHT + GRID_LINE_CLICK_RANGE or 
        GRID_HORIZONTAL_TOP - GRID_LINE_CLICK_RANGE < event.y < GRID_HORIZONTAL_TOP + GRID_LINE_CLICK_RANGE or 
        GRID_HORIZONTAL_BOTTOM - GRID_LINE_CLICK_RANGE < event.y < GRID_HORIZONTAL_BOTTOM + GRID_LINE_CLICK_RANGE):
        change_theme(event)
    
    # Map click position to grid cell
    row, col = -1, -1
    
    # Top row
    if TOP_ROW_MIN_Y < event.y < TOP_ROW_MAX_Y:
        if LEFT_COL_MIN_X < event.x < LEFT_COL_MAX_X: row, col = 0, 0
        elif MIDDLE_COL_MIN_X < event.x < MIDDLE_COL_MAX_X: row, col = 0, 1
        elif RIGHT_COL_MIN_X < event.x < RIGHT_COL_MAX_X: row, col = 0, 2
    
    # Middle row
    elif MIDDLE_ROW_MIN_Y < event.y < MIDDLE_ROW_MAX_Y:
        if LEFT_COL_MIN_X < event.x < LEFT_COL_MAX_X: row, col = 1, 0
        elif MIDDLE_COL_MIN_X < event.x < MIDDLE_COL_MAX_X: row, col = 1, 1
        elif RIGHT_COL_MIN_X < event.x < RIGHT_COL_MAX_X: row, col = 1, 2
    
    # Bottom row
    elif BOTTOM_ROW_MIN_Y < event.y < BOTTOM_ROW_MAX_Y:
        if LEFT_COL_MIN_X < event.x < LEFT_COL_MAX_X: row, col = 2, 0
        elif MIDDLE_COL_MIN_X < event.x < MIDDLE_COL_MAX_X: row, col = 2, 1
        elif RIGHT_COL_MIN_X < event.x < RIGHT_COL_MAX_X: row, col = 2, 2
    
    # If valid cell and empty
    if row != -1 and game_board[row][col] == EMPTY_CELL:
        draw_x(event, game_canvas)
        game_board[row][col] = SYMBOL_X
        current_player = PLAYER_O
        check_win_or_draw()
        handle_two_players_click()

def reset_board():
    """Reset game board to initial state"""
    global game_board
    game_board = [
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL],
        [EMPTY_CELL, EMPTY_CELL, EMPTY_CELL]
    ]

def setup_game_ui():
    """Set up game UI elements"""
    global player_o_radio, player_x_radio, o_wins_label, x_wins_label, computer_mode_check
    
    # Create UI elements
    player_o_radio = Radiobutton(root, text='', variable=starting_player_var, value=PLAYER_O, command=update_starting_player)
    player_x_radio = Radiobutton(root, text='', variable=starting_player_var, value=PLAYER_X, command=update_starting_player)
    
    o_wins_label = Label(text=f"O\n{o_wins}", background=DEFAULT_BACKGROUND)
    x_wins_label = Label(text=f"X\n{x_wins}", background=DEFAULT_BACKGROUND)
    
    # Position UI elements
    o_wins_label.grid(column=0, row=1, ipadx=LABEL_PADDING_X, ipady=LABEL_PADDING_Y)
    x_wins_label.grid(column=2, row=1, ipadx=LABEL_PADDING_X, ipady=LABEL_PADDING_Y)
    player_x_radio.grid(column=2, row=2)
    player_o_radio.grid(column=0, row=2)
    
    # Computer mode checkbox
    computer_mode_check = Checkbutton(
        root, 
        text=COMPUTER_MODE_TEXT, 
        variable=computer_mode_var, 
        command=toggle_computer_mode
    )
    computer_mode_check.grid(column=0, columnspan=3, row=7, sticky='w')
    
    current_player = PLAYER_O
    player_o_radio.select()  # Default to player O starting

def toggle_computer_mode():
    """Toggle between computer and two-player mode"""
    global current_player, o_wins, x_wins, moves_count, game_board
    
    computer_mode = computer_mode_var.get()
    current_player = PLAYER_O
    moves_count = 0
    o_wins = 0
    x_wins = 0
    
    # Update UI
    o_wins_label.configure(background=COLOR_THEMES[current_theme_index][0])
    x_wins_label.configure(background=COLOR_THEMES[current_theme_index][0])
    o_wins_label.configure(text=f"O\n{o_wins}")
    x_wins_label.configure(text=f"X\n{x_wins}")
    
    reset_board_canvas()
    reset_board()
    
    # Set game mode
    if computer_mode == 1:
        game_canvas.bind("<Button-1>", handle_click_based_on_mode)
    else:
        game_canvas.bind("<Button-1>", handle_two_players_click)

def show_about():
    """Show about information"""
    msg.showinfo(
        ABOUT_TITLE, 
        ABOUT_MESSAGE
    )
    
    feedback = msg.askyesno(
        FEEDBACK_TITLE, 
        FEEDBACK_MESSAGE
    )
    
    if feedback:
        webbrowser.open(GITHUB_URL)

def update_score_display():
    """Update the score display (placeholder function)"""
    pass

def change_theme_manual():
    """Manually change the game theme"""
    change_theme()

# Initialize main application
root = Tk()
root.title(WINDOW_TITLE)

# Set window icon
try:
    icon_path = path.abspath(path.join(path.dirname(__file__), ICON_PATH))
    root.iconphoto(False, PhotoImage(file=icon_path))
except:
    pass  # Icon not essential

root.resizable(0, 0)

# Create menu
menu_bar = Menu(root)
root.configure(menu=menu_bar)

# Help menu
help_menu = Menu(menu_bar, tearoff=MENU_TEAROFF)
help_menu.add_command(label=CHANGE_THEME_TEXT, command=change_theme_manual)
help_menu.add_command(label=ABOUT_TEXT, command=show_about)
help_menu.add_separator()
help_menu.add_command(label=EXIT_MENU_TEXT, command=root.destroy)
menu_bar.add_cascade(label=HELP_MENU_TEXT, menu=help_menu)

# Game variables
starting_player_var = IntVar()  # 0 = O, 1 = X
computer_mode_var = IntVar()    # 0 = Two players, 1 = vs Computer

# UI elements
title_label = Label(text=WINDOW_TITLE, font=TITLE_FONT, relief='groove')
play_button = Button(root, text=PLAY_BUTTON_TEXT, font=BUTTON_FONT, command=start_game)
drawing_canvas = Canvas(height=DRAWING_CANVAS_HEIGHT, width=CANVAS_WIDTH, background=DEFAULT_BACKGROUND)
game_canvas = Canvas(height=GAME_CANVAS_HEIGHT, width=CANVAS_WIDTH, background=DEFAULT_GRID)

# Position UI elements
title_label.grid(column=1, row=0)
play_button.grid(column=1, row=1, rowspan=1, ipadx=BUTTON_PADDING_X)
drawing_canvas.grid(column=0, row=4, columnspan=3)
game_canvas.grid(column=0, row=5, columnspan=3)

# Initial drawing
draw_random_shapes(INITIAL_SHAPES_COUNT)

# Bind events
drawing_canvas.bind("<Button>", on_drawing_canvas_click)
drawing_canvas.bind("<Button-3>", clear_drawing_canvas)

# Start main loop
root.mainloop()