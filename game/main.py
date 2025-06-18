from tkinter import *
from random import randrange
import webbrowser
from tkinter import messagebox as msg
import os
from os import path

# Global game state variables
drawing_counter = 0
current_player = 0  # 0 = O, 1 = X
x_wins = 0
o_wins = 0
moves_count = 0
current_theme_index = 1
computer_selected = 0

# Color themes (background, grid)
color_themes = [
    ('cyan', 'gray'),
    ('gray', 'cyan'),
    ('gray', 'orange'),
    ('orange', 'gray'),
    ('orange', 'green'),
    ('green', 'orange'),
    ('gray', 'brown'),
    ('brown', 'gray'),
    ('purple', 'gray'),
    ('gray', 'purple')
]

# Game board (3x3 grid)
game_board = [
    [0, 0, 0],
    [0, 0, 0],
    [0, 0, 0]
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
        root.after(300, computer_play)

def computer_try_win_or_block():
    """Computer AI: Try to win or block player's win"""
    # Try to win
    if try_win('x') or try_block('o') or make_random_move():
        pass

def try_win(symbol):
    """Try to find winning move for given symbol"""
    # Horizontal checks
    for row in range(3):
        if game_board[row][0] == symbol and game_board[row][1] == symbol and game_board[row][2] == 0:
            computer_draw_x(row, 2)
            return True
        if game_board[row][1] == symbol and game_board[row][2] == symbol and game_board[row][0] == 0:
            computer_draw_x(row, 0)
            return True
        if game_board[row][0] == symbol and game_board[row][2] == symbol and game_board[row][1] == 0:
            computer_draw_x(row, 1)
            return True
    
    # Vertical checks
    for col in range(3):
        if game_board[0][col] == symbol and game_board[1][col] == symbol and game_board[2][col] == 0:
            computer_draw_x(2, col)
            return True
        if game_board[1][col] == symbol and game_board[2][col] == symbol and game_board[0][col] == 0:
            computer_draw_x(0, col)
            return True
        if game_board[0][col] == symbol and game_board[2][col] == symbol and game_board[1][col] == 0:
            computer_draw_x(1, col)
            return True
    
    # Diagonal checks
    if game_board[0][0] == symbol and game_board[1][1] == symbol and game_board[2][2] == 0:
        computer_draw_x(2, 2)
        return True
    if game_board[2][2] == symbol and game_board[1][1] == symbol and game_board[0][0] == 0:
        computer_draw_x(0, 0)
        return True
    if game_board[2][2] == symbol and game_board[0][0] == symbol and game_board[1][1] == 0:
        computer_draw_x(1, 1)
        return True
    if game_board[0][2] == symbol and game_board[1][1] == symbol and game_board[2][0] == 0:
        computer_draw_x(2, 0)
        return True
    if game_board[2][0] == symbol and game_board[1][1] == symbol and game_board[0][2] == 0:
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
    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    for row, col in corners:
        if game_board[row][col] == 0:
            computer_draw_x(row, col)
            return True
    
    # Otherwise random move
    while True:
        row, col = randrange(3), randrange(3)
        if game_board[row][col] == 0:
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
    current_theme_index = randrange(10)
    draw_grid(color_themes[current_theme_index][1])
    drawing_canvas.configure(background=color_themes[current_theme_index][1])
    game_canvas.configure(background=color_themes[current_theme_index][0])

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
    draw_grid(color_themes[current_theme_index][1])

def check_win_or_draw():
    """Check if game is won or drawn"""
    global x_wins, o_wins, current_player, moves_count, game_board
    
    moves_count += 1
    
    # Check for O win
    if check_win('o'):
        o_wins += 1
        o_wins_label.configure(text=f"O\n{o_wins}")
        game_canvas.after(1000, reset_board_canvas)
        current_player = 0
        moves_count = 0
        player_o_radio.select()
        reset_board()
        update_score_display()
        return
    
    # Check for X win
    if check_win('x'):
        x_wins += 1
        x_wins_label.configure(text=f"X\n{x_wins}")
        game_canvas.after(600, reset_board_canvas)
        current_player = 1
        moves_count = 0
        reset_board()
        player_x_radio.select()
        update_score_display()
        return
    
    # Check for draw
    if moves_count == 9:
        game_canvas.after(600, reset_board_canvas)
        current_player = 0
        moves_count = 0
        reset_board()
        update_score_display()

def check_win(symbol):
    """Check if player has won with given symbol"""
    # Horizontal wins
    for row in range(3):
        if game_board[row][0] == symbol and game_board[row][1] == symbol and game_board[row][2] == symbol:
            return True
    
    # Vertical wins
    for col in range(3):
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
    radius = randrange(1, 40, 10)
    
    if event.y > 250:  # Change background
        drawing_canvas.configure(background=color)
    else:
        if drawing_counter % 2 == 0:
            drawing_canvas.create_oval(
                event.x - radius, event.y - radius,
                event.x + radius, event.y + radius,
                width=randrange(15, 30, 5),
                outline=color
            )
        else:
            drawing_canvas.create_line(
                event.x + radius, event.y - radius,
                event.x - radius, event.y + radius,
                width=randrange(15, 30, 5),
                fill=color
            )
            drawing_canvas.create_line(
                event.x - radius, event.y - radius,
                event.x + radius, event.y + radius,
                width=randrange(15, 30, 5),
                fill=color
            )
    
    drawing_counter += 1

def exit_game():
    """Exit game and reset state"""
    global drawing_counter, current_player, x_wins, o_wins, game_board
    
    drawing_counter = 0
    current_player = 0
    x_wins = 0
    o_wins = 0
    game_board = [[0,0,0], [0,0,0], [0,0,0]]
    
    o_wins_label.configure(text="O\n0", background='cyan')
    x_wins_label.configure(text="X\n0", background='cyan')
    
    game_canvas.configure(height=30, width=600)
    drawing_canvas.configure(height=300, width=600)
    
    draw_random_shapes(20)
    play_button.configure(command=start_game, text='Play')
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
    play_button.configure(command=exit_game, text='Exit')
    game_canvas.delete("all")
    drawing_canvas.configure(height=30, width=600)
    game_canvas.configure(height=300, width=600)
    drawing_canvas.delete("all")
    root.after(40, setup_game_ui)
    draw_grid(color_themes[current_theme_index][1])
    current_player = 0

def get_random_color():
    """Get a random color for drawing"""
    colors = ['cyan', 'green', 'brown', 'gray', 'dark gray', 'orange', 'purple']
    return colors[randrange(len(colors))]

def get_random_xo_color():
    """Get random color for X/O symbols"""
    colors = ['dark grey', 'red', 'black', 'yellow', 'white', 'blue']
    return colors[randrange(len(colors))]

def draw_x(event, canvas):
    """Draw X symbol on canvas"""
    player_x_radio.select()
    color = get_random_xo_color()
    canvas.create_line(
        event.x + 15, event.y - 15,
        event.x - 15, event.y + 15,
        width=20, fill=color
    )
    canvas.create_line(
        event.x - 15, event.y - 15,
        event.x + 15, event.y + 15,
        width=20, fill=color
    )

def draw_o(event, canvas):
    """Draw O symbol on canvas"""
    player_o_radio.select()
    canvas.create_oval(
        event.x - 15, event.y - 15,
        event.x + 15, event.y + 15,
        width=10, outline=get_random_xo_color()
    )

def draw_random_shapes(count):
    """Draw random shapes on drawing canvas"""
    for _ in range(count):
        x, y, r = randrange(10, 600), randrange(10, 600), randrange(1, 40, 10)
        drawing_canvas.create_oval(
            x - r, y - r,
            x + r, y + r,
            width=randrange(15, 30, 5),
            outline=get_random_color()
        )
        
        x, y, r = randrange(10, 600), randrange(10, 600), randrange(40)
        drawing_canvas.create_line(
            x + r, y - r,
            x - r, y + r,
            width=randrange(15, 30, 5),
            fill=get_random_color()
        )
        drawing_canvas.create_line(
            x - r, y - r,
            x + r, y + r,
            width=randrange(15, 30, 5),
            fill=get_random_color()
        )

def draw_grid(color):
    """Draw the game grid"""
    game_canvas.create_line(250, 30, 250, 240, width=5, fill=color)
    game_canvas.create_line(350, 30, 350, 240, width=5, fill=color)
    game_canvas.create_line(170, 90, 450, 90, width=5, fill=color)
    game_canvas.create_line(170, 170, 450, 170, width=5, fill=color)

def computer_draw_x(row, col):
    """Draw X for computer move"""
    color = get_random_xo_color()
    x = (col * 100) + 200
    y = 30 + (row * 100)
    
    game_canvas.create_line(x + 15, y - 15, x - 15, y + 15, width=20, fill=color)
    game_canvas.create_line(x - 15, y - 15, x + 15, y + 15, width=20, fill=color)
    game_board[row][col] = 'x'

def on_board_click_player_o(event):
    """Handle board click for player O"""
    global game_board, current_player
    
    # Change theme if grid line clicked
    if (event.y > 250 or 
        248 < event.x < 253 or 
        347 < event.x < 352 or 
        167 < event.y < 173 or 
        87 < event.y < 93):
        change_theme(event)
    
    # Map click position to grid cell
    row, col = -1, -1
    
    # Top row
    if 30 < event.y < 85:
        if 170 < event.x < 245: row, col = 0, 0
        elif 250 < event.x < 345: row, col = 0, 1
        elif 350 < event.x < 445: row, col = 0, 2
    
    # Middle row
    elif 90 < event.y < 160:
        if 170 < event.x < 245: row, col = 1, 0
        elif 250 < event.x < 345: row, col = 1, 1
        elif 350 < event.x < 445: row, col = 1, 2
    
    # Bottom row
    elif 150 < event.y < 220:
        if 170 < event.x < 245: row, col = 2, 0
        elif 250 < event.x < 345: row, col = 2, 1
        elif 350 < event.x < 445: row, col = 2, 2
    
    # If valid cell and empty
    if row != -1 and game_board[row][col] == 0:
        draw_o(event, game_canvas)
        game_board[row][col] = 'o'
        current_player = 1
        check_win_or_draw()
        
        if computer_mode_var.get() == 1:  # Computer mode
            handle_click_based_on_mode()
        else:  # Two-player mode
            handle_two_players_click()

def on_board_click_player_x(event):
    """Handle board click for player X"""
    global game_board, current_player
    
    # Change theme if grid line clicked
    if (event.y > 250 or 
        248 < event.x < 253 or 
        347 < event.x < 352 or 
        167 < event.y < 173 or 
        87 < event.y < 93):
        change_theme(event)
    
    # Map click position to grid cell
    row, col = -1, -1
    
    # Top row
    if 30 < event.y < 85:
        if 170 < event.x < 245: row, col = 0, 0
        elif 250 < event.x < 345: row, col = 0, 1
        elif 350 < event.x < 445: row, col = 0, 2
    
    # Middle row
    elif 90 < event.y < 160:
        if 170 < event.x < 245: row, col = 1, 0
        elif 250 < event.x < 345: row, col = 1, 1
        elif 350 < event.x < 445: row, col = 1, 2
    
    # Bottom row
    elif 150 < event.y < 220:
        if 170 < event.x < 245: row, col = 2, 0
        elif 250 < event.x < 345: row, col = 2, 1
        elif 350 < event.x < 445: row, col = 2, 2
    
    # If valid cell and empty
    if row != -1 and game_board[row][col] == 0:
        draw_x(event, game_canvas)
        game_board[row][col] = 'x'
        current_player = 0
        check_win_or_draw()
        handle_two_players_click()

def reset_board():
    """Reset game board to initial state"""
    global game_board
    game_board = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]

def setup_game_ui():
    """Set up game UI elements"""
    global player_o_radio, player_x_radio, o_wins_label, x_wins_label, computer_mode_check
    
    # Create UI elements
    player_o_radio = Radiobutton(root, text='', variable=starting_player_var, value=0, command=update_starting_player)
    player_x_radio = Radiobutton(root, text='', variable=starting_player_var, value=1, command=update_starting_player)
    
    o_wins_label = Label(text=f"O\n{o_wins}", background='cyan')
    x_wins_label = Label(text=f"X\n{x_wins}", background='cyan')
    
    # Position UI elements
    o_wins_label.grid(column=0, row=1, ipadx=20, ipady=3)
    x_wins_label.grid(column=2, row=1, ipadx=20, ipady=3)
    player_x_radio.grid(column=2, row=2)
    player_o_radio.grid(column=0, row=2)
    
    # Computer mode checkbox
    computer_mode_check = Checkbutton(
        root, 
        text='Play with computer', 
        variable=computer_mode_var, 
        command=toggle_computer_mode
    )
    computer_mode_check.grid(column=0, columnspan=3, row=7, sticky='w')
    
    current_player = 0
    player_o_radio.select()  # Default to player O starting

def toggle_computer_mode():
    """Toggle between computer and two-player mode"""
    global current_player, o_wins, x_wins, moves_count, game_board
    
    computer_mode = computer_mode_var.get()
    current_player = 0
    moves_count = 0
    o_wins = 0
    x_wins = 0
    
    # Update UI
    o_wins_label.configure(background=color_themes[current_theme_index][0])
    x_wins_label.configure(background=color_themes[current_theme_index][0])
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
        'About X/O Game', 
        'A simple Tic-Tac-Toe game\n'
        'Developed by Eng. Mahfoud Mohammed Binsabbah\n'
        '2020'
    )
    
    feedback = msg.askyesno(
        'Feedback', 
        'Do you like this game?\n'
        'Give me a star on GitHub repository!'
    )
    
    if feedback:
        webbrowser.open('https://github.com/Mahfoud-Sa/XO_Game.git')

def change_theme_manual():
    """Manually change the game theme"""
    change_theme()

# Initialize main application
root = Tk()
root.title('X/O Game')

# Set window icon
try:
    icon_path = path.abspath(path.join(path.dirname(__file__), 'icon.png'))
    root.iconphoto(False, PhotoImage(file=icon_path))
except:
    pass  # Icon not essential

root.resizable(0, 0)

# Create menu
menu_bar = Menu(root)
root.configure(menu=menu_bar)

# Help menu
help_menu = Menu(menu_bar, tearoff=0)
help_menu.add_command(label='Change Theme', command=change_theme_manual)
help_menu.add_command(label='About', command=show_about)
help_menu.add_separator()
help_menu.add_command(label='Exit', command=root.destroy)
menu_bar.add_cascade(label='Help', menu=help_menu)

# Game variables
starting_player_var = IntVar()  # 0 = O, 1 = X
computer_mode_var = IntVar()    # 0 = Two players, 1 = vs Computer

# UI elements
title_label = Label(text='X/O Game', font=('Arial', 14), relief='groove')
play_button = Button(root, text='Play', font=('Arial', 10), command=start_game)
drawing_canvas = Canvas(height=300, width=600, background='cyan')
game_canvas = Canvas(height=30, width=600, background='gray')

# Position UI elements
title_label.grid(column=1, row=0)
play_button.grid(column=1, row=1, rowspan=1, ipadx=9)
drawing_canvas.grid(column=0, row=4, columnspan=3)
game_canvas.grid(column=0, row=5, columnspan=3)

# Initial drawing
draw_random_shapes(20)

# Bind events
drawing_canvas.bind("<Button>", on_drawing_canvas_click)
drawing_canvas.bind("<Button-3>", clear_drawing_canvas)

# Start main loop
root.mainloop()