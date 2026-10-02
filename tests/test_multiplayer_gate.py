"""
Tests for Mandatory Update Multiplayer Gating and Lifecycle Checking.
Verifies that:
- Mandatory updates lock out online multiplayer while keeping local 2-player mode playable.
- Upgrade intercept prompt is displayed when accessing multiplayer while mandatory update is pending.
- Window focus (<FocusIn>) does not trigger background update checks.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add game directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'game')))

from utils.updater import UpdateManifest


class TestMultiplayerGate(unittest.TestCase):
    """Test suite for multiplayer gate and update lifecycle."""

    def setUp(self):
        self.mandatory_manifest = UpdateManifest(
            schema_version=1,
            name="XO Game",
            version="6.0.0",
            tag_name="v6.0.0",
            channel="stable",
            published_at="2026-10-02T12:00:00Z",
            release_notes="Mandatory network protocol update",
            release_page_url="https://github.com/Mahfoud-Sa/tik-tak-to/releases/tag/v6.0.0",
            download_url="https://github.com/Mahfoud-Sa/tik-tak-to/releases/download/v6.0.0/update.zip",
            file_name="update.zip",
            mandatory=True
        )

    @patch('main.MultiplayerModeDialog')
    @patch('main.create_help_menu')
    @patch('main.GameView')
    @patch('main.GameController')
    @patch('main.GameState')
    @patch('main.Tk')
    def test_multiplayer_intercepted_when_mandatory_update_pending(
        self, mock_tk, mock_state, mock_ctrl, mock_view, mock_help, mock_mp_dialog
    ):
        from main import TicTacToeApp

        # Create app instance with mocked Tkinter root
        app = TicTacToeApp()
        app.pending_mandatory_manifest = self.mandatory_manifest

        with patch.object(app, '_show_mandatory_update_lockout_prompt') as mock_prompt:
            app._show_multiplayer_dialog()
            # Assert lockout prompt was shown and MultiplayerModeDialog was NOT opened
            mock_prompt.assert_called_once_with(self.mandatory_manifest)
            mock_mp_dialog.assert_not_called()

    @patch('main.MultiplayerModeDialog')
    @patch('main.create_help_menu')
    @patch('main.GameView')
    @patch('main.GameController')
    @patch('main.GameState')
    @patch('main.Tk')
    def test_multiplayer_allowed_when_no_mandatory_update(
        self, mock_tk, mock_state, mock_ctrl, mock_view, mock_help, mock_mp_dialog
    ):
        from main import TicTacToeApp

        app = TicTacToeApp()
        app.pending_mandatory_manifest = None

        with patch.object(app, '_show_mandatory_update_lockout_prompt') as mock_prompt:
            app._show_multiplayer_dialog()
            mock_prompt.assert_not_called()
            mock_mp_dialog.assert_called_once()

    @patch('main.create_help_menu')
    @patch('main.GameView')
    @patch('main.GameController')
    @patch('main.GameState')
    @patch('main.Tk')
    def test_local_game_allowed_even_if_mandatory_update_pending(
        self, mock_tk, mock_state, mock_ctrl, mock_view, mock_help
    ):
        from main import TicTacToeApp

        app = TicTacToeApp()
        app.pending_mandatory_manifest = self.mandatory_manifest

        # Local start game should proceed without error
        with patch.object(app.controller, 'start_game') as mock_start:
            app._start_game()
            app._setup_game()
            mock_start.assert_called_once()

    @patch('main.create_help_menu')
    @patch('main.GameView')
    @patch('main.GameController')
    @patch('main.GameState')
    @patch('main.Tk')
    def test_no_focus_in_binding_for_update_checks(
        self, mock_tk_cls, mock_state, mock_ctrl, mock_view, mock_help
    ):
        from main import TicTacToeApp

        mock_root = MagicMock()
        mock_tk_cls.return_value = mock_root

        app = TicTacToeApp()

        # Check all calls to root.bind
        bound_events = [call.args[0] for call in mock_root.bind.call_args_list if call.args]
        self.assertNotIn("<FocusIn>", bound_events)


if __name__ == '__main__':
    unittest.main()
