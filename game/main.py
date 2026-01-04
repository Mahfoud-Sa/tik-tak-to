"""
Tic-Tac-Toe Game - Main Entry Point

A simple Tic-Tac-Toe game using MVC architecture.
Developed by Eng. Mahfoud Mohammed Binsabbah - 2020
Refactored to MVC pattern - 2024
Multiplayer support added - 2024
"""

import webbrowser
from tkinter import Tk, PhotoImage, Button, Frame, Canvas
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
from network_config import (
    MULTIPLAYER_BUTTON_TEXT,
    STATUS_CONNECTED_COLOR, STATUS_DISCONNECTED_COLOR
)

from models.game_state import GameState
from controllers.game_controller import GameController
from controllers.network_game_controller import NetworkGameController
from views.game_view import GameView
from views.widgets.title_label import create_title_label
from views.widgets.play_button import create_play_button
from views.widgets.help_menu import create_help_menu
from views.widgets.multiplayer_dialogs import (
    MultiplayerModeDialog, HostGameDialog, JoinGameDialog
)
from network.server import GameServer
from network.client import GameClient


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
        
        # Network components (for multiplayer)
        self.network_controller = None
        self.server = None
        self.client = None
        self.is_multiplayer_mode = False
        
        # Dialogs
        self.host_dialog = None
        self.join_dialog = None
        
        # Wire up view and controller
        self.view.set_controller(self.controller)
        self.controller.set_callbacks(
            on_game_start=self._on_game_start,
            on_game_end=self._on_game_end
        )
        
        # Create UI
        self._create_ui()
        
        # Connection status indicator (hidden initially)
        self._status_canvas = None
        self._status_circle = None
    
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
        
        # Button frame for Play and Multiplayer
        self.button_frame = Frame(self.root)
        self.button_frame.grid(column=1, row=1)
        
        # Play button (local 2-player)
        self.play_button = Button(
            self.button_frame,
            text=PLAY_BUTTON_TEXT,
            font=BUTTON_FONT,
            command=self._start_game
        )
        self.play_button.pack(side='top', pady=5, ipadx=BUTTON_PADDING_X)
        
        # Multiplayer button
        self.multiplayer_button = Button(
            self.button_frame,
            text=MULTIPLAYER_BUTTON_TEXT,
            font=BUTTON_FONT,
            command=self._show_multiplayer_dialog
        )
        self.multiplayer_button.pack(side='top', pady=5, ipadx=BUTTON_PADDING_X)
        
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
    
    def _create_connection_indicator(self):
        """Create the connection status indicator on the game board."""
        if self._status_canvas is None:
            self._status_canvas = Canvas(
                self.root,
                width=20,
                height=20,
                highlightthickness=0,
                bg=self.view.game_canvas.cget('bg')
            )
            self._status_circle = self._status_canvas.create_oval(
                2, 2, 18, 18,
                fill=STATUS_CONNECTED_COLOR,
                outline=''
            )
            self._status_canvas.grid(column=0, row=2, sticky='nw', padx=5, pady=5)
    
    def _update_connection_indicator(self, connected: bool):
        """Update the connection status indicator."""
        if self._status_canvas:
            color = STATUS_CONNECTED_COLOR if connected else STATUS_DISCONNECTED_COLOR
            self._status_canvas.itemconfig(self._status_circle, fill=color)
    
    def _destroy_connection_indicator(self):
        """Remove the connection status indicator."""
        if self._status_canvas:
            self._status_canvas.destroy()
            self._status_canvas = None
            self._status_circle = None
    
    # =========================================================================
    # LOCAL GAME METHODS
    # =========================================================================
    
    def _start_game(self):
        """Start a local 2-player game."""
        self.is_multiplayer_mode = False
        self.play_button.configure(text=EXIT_BUTTON_TEXT, command=self._exit_game)
        self.multiplayer_button.pack_forget()  # Hide multiplayer button during game
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
        self._cleanup_game_ui()
    
    def _cleanup_game_ui(self):
        """Clean up game UI and return to main menu."""
        self.view.cleanup_game_ui()
        self.view.swap_canvas_sizes(game_active=False)
        self.play_button.configure(text=PLAY_BUTTON_TEXT, command=self._start_game)
        self.multiplayer_button.pack(side='left', padx=5, ipadx=BUTTON_PADDING_X)
        self._destroy_connection_indicator()
    
    # =========================================================================
    # MULTIPLAYER METHODS
    # =========================================================================
    
    def _show_multiplayer_dialog(self):
        """Show the multiplayer mode selection dialog."""
        MultiplayerModeDialog(
            self.root,
            on_host=self._start_hosting,
            on_join=self._show_join_dialog
        )
    
    def _start_hosting(self):
        """Start hosting a multiplayer game."""
        # Create and start server
        self.server = GameServer()
        ip_address = self.server.get_local_ip()
        
        if not self.server.start():
            msg.showerror("\u062e\u0637\u0623", "\u0641\u0634\u0644 \u0641\u064a \u0628\u062f\u0621 \u0627\u0644\u0633\u064a\u0631\u0641\u0631. \u0642\u062f \u064a\u0643\u0648\u0646 \u0627\u0644\u0645\u0646\u0641\u0630 \u0642\u064a\u062f \u0627\u0644\u0627\u0633\u062a\u062e\u062f\u0627\u0645.")
            return
        
        # Set up callbacks
        self.server.on_client_connect(self._on_client_connected)
        self.server.on_client_disconnect(self._on_client_disconnected_hosting)
        
        # Show host dialog
        self.host_dialog = HostGameDialog(
            self.root,
            ip_address,
            on_cancel=self._cancel_hosting,
            on_refresh=self._refresh_hosting
        )
    
    def _on_client_connected(self):
        """Called when a client connects to our server."""
        if self.host_dialog:
            self.root.after(0, lambda: self._handle_client_connected())
    
    def _handle_client_connected(self):
        """Handle client connection on main thread."""
        if self.host_dialog:
            self.host_dialog.set_connected(True)
            # Wait a moment then start the game
            self.root.after(1000, self._start_multiplayer_game_as_host)
    
    def _start_multiplayer_game_as_host(self):
        """Start the multiplayer game as host."""
        if self.host_dialog:
            self.host_dialog.close()
            self.host_dialog = None
        
        self.is_multiplayer_mode = True
        
        # Create network controller
        self.network_controller = NetworkGameController(
            self.state, self.view, is_host=True
        )
        self.network_controller.set_server(self.server)
        self.network_controller.set_callbacks(
            on_opponent_disconnect=self._on_opponent_disconnected
        )
        
        # Wire up view to use network controller
        self.view.set_controller(self.network_controller)
        
        # Set up UI
        self.play_button.configure(text=EXIT_BUTTON_TEXT, command=self._exit_multiplayer_game)
        self.multiplayer_button.pack_forget()
        self.view.swap_canvas_sizes(game_active=True)
        self.view.clear_board()
        
        # Create connection indicator
        self.root.after(UI_SETUP_DELAY, self._setup_multiplayer_game)
    
    def _setup_multiplayer_game(self):
        """Set up multiplayer game UI."""
        self.view.setup_game_ui()
        self.network_controller.start_game()
        self._create_connection_indicator()
        self._update_connection_indicator(True)
    
    def _cancel_hosting(self):
        """Cancel hosting and return to main menu."""
        if self.server:
            self.server.stop()
            self.server = None
        self.host_dialog = None
    
    def _refresh_hosting(self):
        """Refresh - disconnect current client and wait for new one."""
        if self.server:
            self.server.refresh()
    
    def _on_client_disconnected_hosting(self):
        """Called when client disconnects while hosting (before game starts)."""
        if self.host_dialog:
            self.root.after(0, lambda: self.host_dialog.set_waiting())
    
    def _show_join_dialog(self):
        """Show the join game dialog."""
        self.join_dialog = JoinGameDialog(
            self.root,
            on_connect=self._try_connect,
            on_cancel=self._cancel_joining
        )
    
    def _try_connect(self, ip_address: str):
        """Try to connect to a host."""
        self.client = GameClient()
        
        # Set up callbacks
        self.client.on_connection_failed(self._on_connection_failed)
        self.client.on_connect(self._on_connected_to_host)
        self.client.on_disconnect(self._on_disconnected_from_host)
        
        # Try to connect (in background)
        import threading
        def connect_thread():
            success = self.client.connect(ip_address)
            if not success and self.join_dialog:
                self.root.after(0, lambda: self.join_dialog.set_error("Connection failed"))
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def _on_connection_failed(self, message: str):
        """Called when connection fails."""
        if self.join_dialog:
            self.root.after(0, lambda: self.join_dialog.set_error(message))
    
    def _on_connected_to_host(self):
        """Called when successfully connected to host."""
        if self.join_dialog:
            self.root.after(0, self._handle_connected_to_host)
    
    def _handle_connected_to_host(self):
        """Handle successful connection on main thread."""
        if self.join_dialog:
            self.join_dialog.set_connected(True)
            # Wait a moment then start the game
            self.root.after(1000, self._start_multiplayer_game_as_client)
    
    def _start_multiplayer_game_as_client(self):
        """Start the multiplayer game as client."""
        if self.join_dialog:
            self.join_dialog.close()
            self.join_dialog = None
        
        self.is_multiplayer_mode = True
        
        # Create network controller
        self.network_controller = NetworkGameController(
            self.state, self.view, is_host=False
        )
        self.network_controller.set_client(self.client)
        self.network_controller.set_callbacks(
            on_opponent_disconnect=self._on_opponent_disconnected
        )
        
        # Wire up view to use network controller
        self.view.set_controller(self.network_controller)
        
        # Set up UI
        self.play_button.configure(text=EXIT_BUTTON_TEXT, command=self._exit_multiplayer_game)
        self.multiplayer_button.pack_forget()
        self.view.swap_canvas_sizes(game_active=True)
        self.view.clear_board()
        
        self.root.after(UI_SETUP_DELAY, self._setup_multiplayer_game)
    
    def _cancel_joining(self):
        """Cancel joining and return to main menu."""
        if self.client:
            self.client.disconnect()
            self.client = None
        self.join_dialog = None
    
    def _on_disconnected_from_host(self):
        """Called when disconnected from host."""
        if self.join_dialog:
            self.root.after(0, lambda: self.join_dialog.set_connected(False))
    
    def _on_opponent_disconnected(self):
        """Called when opponent disconnects during game."""
        self._update_connection_indicator(False)
        msg.showwarning("\u062a\u0645 \u0642\u0637\u0639 \u0627\u0644\u0627\u062a\u0635\u0627\u0644", "\u0644\u0642\u062f \u0627\u0646\u0642\u0637\u0639 \u0627\u062a\u0635\u0627\u0644 \u0627\u0644\u062e\u0635\u0645!")
        self._exit_multiplayer_game()
    
    def _exit_multiplayer_game(self):
        """Exit multiplayer game and return to main menu."""
        if self.network_controller:
            self.network_controller.exit_game()
            self.network_controller = None
        
        if self.server:
            self.server.stop()
            self.server = None
        
        if self.client:
            self.client.disconnect()
            self.client = None
        
        # Restore local controller
        self.view.set_controller(self.controller)
        
        self._cleanup_game_ui()
    
    # =========================================================================
    # COMMON METHODS
    # =========================================================================
    
    def _on_game_start(self):
        """Callback when game starts."""
        pass
    
    def _on_game_end(self):
        """Callback when game ends."""
        pass
    
    def _change_theme(self):
        """Change the color theme."""
        if self.is_multiplayer_mode and self.network_controller:
            self.network_controller.change_theme()
        else:
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