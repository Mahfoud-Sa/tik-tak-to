"""
Tests for UI RTL/LTR Layout Directionality.
Verifies:
- Scoreboard and turn selector column placement mirrors in RTL (column 2 for O, 0 for X)
  and restores in LTR (column 0 for O, 2 for X).
- Dynamic re-layout reconfigures existing widgets in-place.
- Connection status indicator placement mirrors appropriately.
- No AttributeError occurs on is_game_active.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add game directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'game')))

try:
    from views.game_view import GameView
    from utils.i18n import i18n
    from main import TicTacToeApp
except ImportError:
    from game.views.game_view import GameView
    from game.utils.i18n import i18n
    from game.main import TicTacToeApp


class TestLayoutDirectionality(unittest.TestCase):
    """Unit and mock UI tests for RTL/LTR layout behavior."""

    @patch('views.game_view.IntVar')
    @patch('views.game_view.Canvas')
    @patch('views.game_view.Label')
    @patch('views.game_view.Radiobutton')
    def test_game_view_setup_in_rtl(self, mock_radio, mock_label, mock_canvas, mock_int_var):
        mock_label.side_effect = lambda *args, **kwargs: MagicMock()
        mock_radio.side_effect = lambda *args, **kwargs: MagicMock()

        i18n.set_language("ar")
        root = MagicMock()
        view = GameView(root)
        view.setup_game_ui()

        # In RTL: Player O should be at column 2, Player X at column 0
        o_grid_kwargs = view.o_wins_label.grid.call_args[1]
        self.assertEqual(o_grid_kwargs["column"], 2)

        x_grid_kwargs = view.x_wins_label.grid.call_args[1]
        self.assertEqual(x_grid_kwargs["column"], 0)

        po_grid_kwargs = view.player_o_radio.grid.call_args[1]
        self.assertEqual(po_grid_kwargs["column"], 2)

        px_grid_kwargs = view.player_x_radio.grid.call_args[1]
        self.assertEqual(px_grid_kwargs["column"], 0)

    @patch('views.game_view.IntVar')
    @patch('views.game_view.Canvas')
    @patch('views.game_view.Label')
    @patch('views.game_view.Radiobutton')
    def test_game_view_setup_in_ltr(self, mock_radio, mock_label, mock_canvas, mock_int_var):
        mock_label.side_effect = lambda *args, **kwargs: MagicMock()
        mock_radio.side_effect = lambda *args, **kwargs: MagicMock()

        i18n.set_language("en")
        root = MagicMock()
        view = GameView(root)
        view.setup_game_ui()

        # In LTR: Player O should be at column 0, Player X at column 2
        o_grid_kwargs = view.o_wins_label.grid.call_args[1]
        self.assertEqual(o_grid_kwargs["column"], 0)

        x_grid_kwargs = view.x_wins_label.grid.call_args[1]
        self.assertEqual(x_grid_kwargs["column"], 2)

        po_grid_kwargs = view.player_o_radio.grid.call_args[1]
        self.assertEqual(po_grid_kwargs["column"], 0)

        px_grid_kwargs = view.player_x_radio.grid.call_args[1]
        self.assertEqual(px_grid_kwargs["column"], 2)

    @patch('views.game_view.IntVar')
    @patch('views.game_view.Canvas')
    @patch('views.game_view.Label')
    @patch('views.game_view.Radiobutton')
    def test_game_view_dynamic_re_layout(self, mock_radio, mock_label, mock_canvas, mock_int_var):
        mock_label.side_effect = lambda *args, **kwargs: MagicMock()
        mock_radio.side_effect = lambda *args, **kwargs: MagicMock()

        i18n.set_language("en")
        root = MagicMock()
        view = GameView(root)
        view.setup_game_ui()

        # Switch to RTL and update layout
        i18n.set_language("ar")
        view.update_layout_direction()

        view.o_wins_label.grid_configure.assert_called_with(column=2)
        view.x_wins_label.grid_configure.assert_called_with(column=0)
        view.player_o_radio.grid_configure.assert_called_with(column=2)
        view.player_x_radio.grid_configure.assert_called_with(column=0)

        # Switch back to LTR and update layout
        i18n.set_language("en")
        view.update_layout_direction()

        view.o_wins_label.grid_configure.assert_called_with(column=0)
        view.x_wins_label.grid_configure.assert_called_with(column=2)
        view.player_o_radio.grid_configure.assert_called_with(column=0)
        view.player_x_radio.grid_configure.assert_called_with(column=2)

    @patch('main.create_help_menu')
    @patch('main.Canvas')
    @patch('main.GameView')
    @patch('main.GameController')
    @patch('main.GameState')
    @patch('main.Tk')
    def test_main_app_connection_indicator_direction(
        self, mock_tk, mock_state, mock_ctrl, mock_view, mock_canvas, mock_help
    ):
        mock_state.return_value.is_game_active = False
        i18n.set_language("ar")
        app = TicTacToeApp()

        # Create indicator in RTL
        app._create_connection_indicator()
        mock_canvas.return_value.grid.assert_called_with(column=2, row=2, sticky='ne', padx=5, pady=5)

        # Toggle language to EN
        i18n.set_language("en")
        app._update_ui_language()
        mock_canvas.return_value.grid_configure.assert_called_with(column=0, sticky='nw')

        # Toggle back to AR
        i18n.set_language("ar")
        app._update_ui_language()
        mock_canvas.return_value.grid_configure.assert_called_with(column=2, sticky='ne')


if __name__ == '__main__':
    unittest.main()
