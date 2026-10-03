"""
Tests for Internationalization (i18n) and Arabic/English Language Switching.
Verifies:
- Default language is Arabic.
- Translation lookup in Arabic and English.
- Dynamic language switching (toggle_language and set_language).
- Listener subscription and notification upon language change.
- Persistence of user language preference.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add game directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'game')))

try:
    from game.utils.i18n import I18n, i18n
except ImportError:
    from utils.i18n import I18n, i18n


class TestI18n(unittest.TestCase):
    """Test suite for localization service."""

    def setUp(self):
        self.temp_settings = tempfile.NamedTemporaryFile(delete=False)
        self.temp_settings.close()
        self.i18n_instance = I18n(settings_file=self.temp_settings.name, default_lang="ar")

    def tearDown(self):
        if os.path.exists(self.temp_settings.name):
            os.remove(self.temp_settings.name)

    def test_default_language_is_arabic(self):
        self.assertEqual(self.i18n_instance.get_language(), "ar")
        self.assertEqual(self.i18n_instance.t("PLAY_BUTTON_TEXT"), "ابدأ اللعب")
        self.assertEqual(self.i18n_instance.t("WINDOW_TITLE"), "لعبة XO")
        self.assertEqual(self.i18n_instance.t("ABOUT_TITLE"), "حول لعبة XO")

    def test_switch_to_english(self):
        self.i18n_instance.set_language("en")
        self.assertEqual(self.i18n_instance.get_language(), "en")
        self.assertEqual(self.i18n_instance.t("PLAY_BUTTON_TEXT"), "Play Game")
        self.assertEqual(self.i18n_instance.t("WINDOW_TITLE"), "Tik Tak Tok")
        self.assertEqual(self.i18n_instance.t("ABOUT_TITLE"), "About Tik Tak Tok")
        self.assertEqual(self.i18n_instance.t("MULTIPLAYER_BUTTON_TEXT"), "Multiplayer")

    def test_toggle_language(self):
        # Starts in ar
        self.assertEqual(self.i18n_instance.get_language(), "ar")
        new_lang = self.i18n_instance.toggle_language()
        self.assertEqual(new_lang, "en")
        self.assertEqual(self.i18n_instance.get_language(), "en")
        self.assertEqual(self.i18n_instance.t("PLAY_BUTTON_TEXT"), "Play Game")

        # Toggle back to ar
        new_lang = self.i18n_instance.toggle_language()
        self.assertEqual(new_lang, "ar")
        self.assertEqual(self.i18n_instance.get_language(), "ar")
        self.assertEqual(self.i18n_instance.t("PLAY_BUTTON_TEXT"), "ابدأ اللعب")

    def test_string_formatting_interpolation(self):
        ar_msg = self.i18n_instance.t("UP_TO_DATE_MESSAGE", version="5.0.0")
        self.assertIn("v5.0.0", ar_msg)
        self.assertIn("أنت تستخدم بالفعل", ar_msg)

        self.i18n_instance.set_language("en")
        en_msg = self.i18n_instance.t("UP_TO_DATE_MESSAGE", version="5.0.0")
        self.assertIn("v5.0.0", en_msg)
        self.assertIn("already using the latest version", en_msg)

    def test_subscribers_notified_on_language_change(self):
        notifications = []

        def listener():
            notifications.append(self.i18n_instance.get_language())

        self.i18n_instance.subscribe(listener)
        self.i18n_instance.set_language("en")
        self.i18n_instance.set_language("ar")

        self.assertEqual(notifications, ["en", "ar"])

    def test_language_persistence(self):
        self.i18n_instance.set_language("en")

        # Create new instance with same settings file
        new_instance = I18n(settings_file=self.temp_settings.name)
        self.assertEqual(new_instance.get_language(), "en")

    def test_legacy_settings_migration(self):
        legacy_temp = tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8")
        legacy_temp.write('{"language": "en"}')
        legacy_temp.close()

        new_settings_path = os.path.join(tempfile.gettempdir(), f"test_migrated_{os.getpid()}.json")
        if os.path.exists(new_settings_path):
            os.remove(new_settings_path)

        try:
            # Create instance pointing to new path with legacy path injected
            migrated_i18n = I18n(settings_file=new_settings_path)
            migrated_i18n._legacy_settings_file = legacy_temp.name
            migrated_i18n._load_preference()

            self.assertEqual(migrated_i18n.get_language(), "en")
            self.assertTrue(os.path.exists(new_settings_path))
        finally:
            if os.path.exists(legacy_temp.name):
                os.remove(legacy_temp.name)
            if os.path.exists(new_settings_path):
                os.remove(new_settings_path)

    def test_directionality_helpers_ar(self):
        self.i18n_instance.set_language("ar")
        self.assertTrue(self.i18n_instance.is_rtl)
        self.assertEqual(self.i18n_instance.direction, "rtl")
        self.assertEqual(self.i18n_instance.side_start(), "right")
        self.assertEqual(self.i18n_instance.side_end(), "left")
        self.assertEqual(self.i18n_instance.anchor_start(), "e")
        self.assertEqual(self.i18n_instance.anchor_end(), "w")
        # Grid column mirroring for 3-column layout
        self.assertEqual(self.i18n_instance.grid_col(0, 3), 2)
        self.assertEqual(self.i18n_instance.grid_col(1, 3), 1)
        self.assertEqual(self.i18n_instance.grid_col(2, 3), 0)

    def test_directionality_helpers_en(self):
        self.i18n_instance.set_language("en")
        self.assertFalse(self.i18n_instance.is_rtl)
        self.assertEqual(self.i18n_instance.direction, "ltr")
        self.assertEqual(self.i18n_instance.side_start(), "left")
        self.assertEqual(self.i18n_instance.side_end(), "right")
        self.assertEqual(self.i18n_instance.anchor_start(), "w")
        self.assertEqual(self.i18n_instance.anchor_end(), "e")
        # Grid column mirroring for 3-column layout
        self.assertEqual(self.i18n_instance.grid_col(0, 3), 0)
        self.assertEqual(self.i18n_instance.grid_col(1, 3), 1)
        self.assertEqual(self.i18n_instance.grid_col(2, 3), 2)


class TestAppLanguageSwitch(unittest.TestCase):
    """Test suite for TicTacToeApp dynamic language dropdown integration."""

    @patch('main.create_help_menu')
    @patch('main.GameView')
    @patch('main.GameController')
    @patch('main.GameState')
    @patch('main.Tk')
    def test_app_language_dropdown_updates_ui(
        self, mock_tk, mock_state, mock_ctrl, mock_view, mock_help
    ):
        import main
        from main import TicTacToeApp
        app_i18n = main.i18n
        mock_state.return_value.is_game_active = False
        mock_state.return_value.game_active = False
        app = TicTacToeApp()

        # lang_button should no longer exist
        self.assertFalse(hasattr(app, 'lang_button'))

        # lang_dropdown should exist
        self.assertTrue(hasattr(app, 'lang_dropdown'))

        # When locale updates, dropdown label is synchronized
        app_i18n.set_language("en")
        with patch.object(app.play_button, 'config') as mock_play_cfg, \
             patch.object(app.lang_dropdown, 'set') as mock_set:
            app._update_ui_language()
            mock_play_cfg.assert_called_with(text="Play Game")
            mock_set.assert_called_with("English")

        app_i18n.set_language("ar")
        with patch.object(app.play_button, 'config') as mock_play_cfg, \
             patch.object(app.lang_dropdown, 'set') as mock_set:
            app._update_ui_language()
            mock_play_cfg.assert_called_with(text="ابدأ اللعب")
            mock_set.assert_called_with("العربية")

        # When selecting English from dropdown, language switches to 'en'
        with patch.object(app.lang_dropdown, 'get', return_value="English"):
            app._on_language_selected()
            self.assertEqual(app_i18n.get_language(), "en")

        # When selecting Arabic from dropdown, language switches to 'ar'
        with patch.object(app.lang_dropdown, 'get', return_value="العربية"):
            app._on_language_selected()
            self.assertEqual(app_i18n.get_language(), "ar")

    @patch('main.create_help_menu')
    @patch('main.GameView')
    @patch('main.GameController')
    @patch('main.GameState')
    @patch('main.Tk')
    def test_app_language_dropdown_lifecycle(
        self, mock_tk, mock_state, mock_ctrl, mock_view, mock_help
    ):
        import main
        from main import TicTacToeApp
        mock_state.return_value.is_game_active = False
        mock_state.return_value.game_active = False
        app = TicTacToeApp()

        with patch.object(app.lang_dropdown, 'pack_forget') as mock_forget:
            app._start_game()
            mock_forget.assert_called()

        with patch.object(app.lang_dropdown, 'pack') as mock_pack:
            app._cleanup_game_ui()
            mock_pack.assert_called_with(side='top', pady=5)




if __name__ == '__main__':
    unittest.main()

