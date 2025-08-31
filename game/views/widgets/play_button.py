from tkinter import Button

def create_play_button(parent, text, font, command, grid_options=None):
    """Create and place the play button with given options."""
    button = Button(parent, text=text, font=font, command=command)
    if grid_options is not None:
        button.grid(**grid_options)
    return button