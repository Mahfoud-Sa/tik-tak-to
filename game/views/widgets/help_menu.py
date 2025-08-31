# Views package
from tkinter import Menu

def create_help_menu(root, change_theme_manual, show_about, exit_command,
                    CHANGE_THEME_TEXT, ABOUT_TEXT, EXIT_MENU_TEXT, HELP_MENU_TEXT, MENU_TEAROFF):
    menu_bar = Menu(root)
    help_menu = Menu(menu_bar, tearoff=MENU_TEAROFF)
    help_menu.add_command(label=CHANGE_THEME_TEXT, command=change_theme_manual)
    help_menu.add_command(label=ABOUT_TEXT, command=show_about)
    help_menu.add_separator()
    help_menu.add_command(label=EXIT_MENU_TEXT, command=exit_command)
    menu_bar.add_cascade(label=HELP_MENU_TEXT, menu=help_menu)
    root.configure(menu=menu_bar)
    return menu_bar