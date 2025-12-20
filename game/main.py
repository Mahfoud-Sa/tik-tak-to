"""
Tic-Tac-Toe Game - Main Entry Point

A simple Tic-Tac-Toe game using MVC architecture.
Developed by Eng. Mahfoud Mohammed Binsabbah - 2020
Refactored to MVC pattern - 2024
"""

import webbrowser
from tkinter import Tk, PhotoImage
from tkinter import messagebox as msg
from os import path

from config import (
    WINDOW_TITLE, ICON_PATH,
    PLAY_BUTTON_TEXT, EXIT_BUTTON_TEXT,
    TITLE_FONT, BUTTON_FONT, BUTTON_PADDING_X,
    CHANGE_THEME_TEXT, ABOUT_TEXT, EXIT_MENU_TEXT, HELP_MENU_TEXT,
    MENU_TEAROFF, UI_SETUP_DELAY,
    ABOUT_TITLE, ABOUT_MESSAGE, FEEDBACK_TITLE, FEEDBACK_MESSAGE, GITHUB_URL
)

from models.game_state import GameState
from controllers.game_controller import GameController
from views.game_view import GameView
from views.widgets.title_label import create_title_label
from views.widgets.play_button import create_play_button
from views.widgets.help_menu import create_help_menu


class TicTacToeApp:
    """Main application class that wires together MVC components."""
    
    def __init__(self):
        """Initialize the application."""
        # Create root window
        self.root = Tk()
        self.root.title(WINDOW_TITLE)
        self.root.resizable(False, False)
        self._set_icon()
        
        # Initialize MVC components
        self.state = GameState()
        self.view = GameView(self.root)
        self.controller = GameController(self.state, self.view)
        
        # Wire up view and controller
        self.view.set_controller(self.controller)
        self.controller.set_callbacks(
            on_game_start=self._on_game_start,
            on_game_end=self._on_game_end
        )
        
        # Create UI
        self._create_ui()
    
    def _set_icon(self):
        """Set the window icon."""
        try:
            icon_path = path.abspath(path.join(path.dirname(__file__), ICON_PATH))
            self.root.iconphoto(False, PhotoImage(file=icon_path))
        except Exception:
            pass  # Icon not essential
    
    def _create_ui(self):
        """Create the main UI elements."""
        # Title label
        self.title_label = create_title_label(
            self.root,
            WINDOW_TITLE,
            TITLE_FONT,
            'groove',
            grid_options={"column": 1, "row": 0}
        )
        
        # Play button
        self.play_button = create_play_button(
            self.root,
            PLAY_BUTTON_TEXT,
            BUTTON_FONT,
            self._start_game,
            grid_options={"column": 1, "row": 1, "rowspan": 1, "ipadx": BUTTON_PADDING_X}
        )
        
        # Help menu
        create_help_menu(
            self.root,
            self._change_theme,
            self._show_about,
            self.root.destroy,
            CHANGE_THEME_TEXT,
            ABOUT_TEXT,
            EXIT_MENU_TEXT,
            HELP_MENU_TEXT,
            MENU_TEAROFF
        )
    
    def _start_game(self):
        """Start the game."""
        self.play_button.configure(text=EXIT_BUTTON_TEXT, command=self._exit_game)
        self.view.swap_canvas_sizes(game_active=True)
        self.view.clear_board()
        self.root.after(UI_SETUP_DELAY, self._setup_game)
    
    def _setup_game(self):
        """Set up the game after UI update."""
        self.view.setup_game_ui()
        self.controller.start_game()
    
    def _exit_game(self):
        """Exit to main menu."""
        self.controller.exit_game()
        self.view.cleanup_game_ui()
        self.view.swap_canvas_sizes(game_active=False)
        self.play_button.configure(text=PLAY_BUTTON_TEXT, command=self._start_game)
    
    def _on_game_start(self):
        """Callback when game starts."""
        pass
    
    def _on_game_end(self):
        """Callback when game ends."""
        pass
    
    def _change_theme(self):
        """Change the color theme."""
        self.controller.change_theme()
    
    def _show_about(self):
        """Show about dialog."""
        msg.showinfo(ABOUT_TITLE, ABOUT_MESSAGE)
        
        if msg.askyesno(FEEDBACK_TITLE, FEEDBACK_MESSAGE):
            webbrowser.open(GITHUB_URL)
    
    def run(self):
        """Run the application main loop."""
        self.root.mainloop()


def main():
    """Application entry point."""
    app = TicTacToeApp()
    app.run()


if __name__ == "__main__":
    main()