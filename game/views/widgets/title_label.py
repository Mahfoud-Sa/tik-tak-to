from tkinter import Label

def create_title_label(parent, text, font, relief, grid_options=None):
    """Create and place the title label with given options."""
    label = Label(parent, text=text, font=font, relief=relief)
    if grid_options is not None:
        label.grid(**grid_options)
    return label