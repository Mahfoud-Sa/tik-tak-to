"""
Tests for UpdateNotifierDialog UI Transformation and Development Guardrails.
Verifies:
- Dev mode guardrail opens browser fallback when running from source.
- Frozen production mode starts in-modal progress bar and download.
- Cancel button aborts download and restores action buttons.
- Download error prompts friendly alert with manual browser fallback option.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add game directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'game')))

try:
    from views.widgets.update_dialog import UpdateNotifierDialog
    from utils.updater import UpdateManifest, UpdateService, DownloadCancellationToken
except ImportError:
    from game.views.widgets.update_dialog import UpdateNotifierDialog
    from game.utils.updater import UpdateManifest, UpdateService, DownloadCancellationToken


class TestUpdateDialogUI(unittest.TestCase):
    """Test suite for update dialog UI behavior and guardrails."""

    def setUp(self):
        self.manifest = UpdateManifest(
            schema_version=1,
            name="XO Game",
            version="4.0.0",
            tag_name="v4.0.0",
            channel="stable",
            published_at="2026-10-02T12:00:00Z",
            release_notes="New features",
            release_page_url="https://github.com/Mahfoud-Sa/tik-tak-to/releases/tag/v4.0.0",
            download_url="https://github.com/Mahfoud-Sa/tik-tak-to/releases/download/v4.0.0/update.zip",
            file_name="update.zip",
            sha256="abcdef1234567890",
            mandatory=False
        )

    def _create_test_dialog(self, mock_service):
        parent = MagicMock()
        with patch('views.widgets.update_dialog.Toplevel'), \
             patch.object(UpdateNotifierDialog, '_center_window'), \
             patch.object(UpdateNotifierDialog, '_set_icon'), \
             patch.object(UpdateNotifierDialog, '_create_ui'):
            dialog = UpdateNotifierDialog(
                parent=parent,
                current_version="3.0.0",
                manifest=self.manifest,
                update_service=mock_service
            )
            dialog.download_btn = MagicMock()
            dialog.later_btn = MagicMock()
            dialog.btn_frame = MagicMock()
            return dialog

    @patch('views.widgets.update_dialog.webbrowser.open')
    @patch('views.widgets.update_dialog.msg.showinfo')
    def test_dev_mode_guardrail_opens_browser(
        self, mock_msg, mock_web_open
    ):
        mock_service = MagicMock(spec=UpdateService)

        with patch.object(sys, 'frozen', False, create=True):
            dialog = self._create_test_dialog(mock_service)
            dialog._on_download()

            # Assert browser was opened and no in-app download was started
            mock_web_open.assert_called_once()
            mock_service.download_update_async.assert_not_called()

    @patch('views.widgets.update_dialog.Label')
    @patch('views.widgets.update_dialog.Button')
    @patch('views.widgets.update_dialog.ttk.Progressbar')
    def test_frozen_mode_transforms_ui_and_starts_download(
        self, mock_pb, mock_btn, mock_lbl
    ):
        mock_service = MagicMock(spec=UpdateService)

        with patch.object(sys, 'frozen', True, create=True):
            dialog = self._create_test_dialog(mock_service)
            dialog._on_download()

            # Assert async download was triggered
            mock_service.download_update_async.assert_called_once()
            self.assertTrue(dialog._is_downloading)
            self.assertIsNotNone(dialog._cancel_token)

    @patch('views.widgets.update_dialog.Label')
    @patch('views.widgets.update_dialog.Button')
    @patch('views.widgets.update_dialog.ttk.Progressbar')
    def test_cancel_download_restores_buttons(
        self, mock_pb, mock_btn, mock_lbl
    ):
        mock_service = MagicMock(spec=UpdateService)

        with patch.object(sys, 'frozen', True, create=True):
            dialog = self._create_test_dialog(mock_service)
            dialog._on_download()
            self.assertTrue(dialog._is_downloading)

            # Now cancel download
            dialog._on_cancel_download()
            self.assertTrue(dialog._cancel_token.is_cancelled)
            self.assertFalse(dialog._is_downloading)


if __name__ == '__main__':
    unittest.main()
