"""
Tests for External Batch Patcher and In-Place Executable Replacement.
Verifies:
- Extraction and staging of replacement binary from verified zip.
- Windows batch updater script generation with proper escaping, wait loops, and restart commands.
- Dev mode guardrails avoiding process replacement in source environments.
- Error handling on malformed zip archives.
"""

import io
import os
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch, MagicMock

# Add game directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'game')))

from utils.updater import (
    generate_updater_batch_script,
    stage_executable_from_zip,
    apply_in_place_update
)


class TestBatchPatcher(unittest.TestCase):
    """Test suite for batch updater script generation and binary staging."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dummy_exe_content = b"MZ\x90\x00Dummy executable bytes"

        # Create a sample update zip archive
        self.zip_path = os.path.join(self.temp_dir.name, "update.zip")
        with zipfile.ZipFile(self.zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("XO_Game.exe", self.dummy_exe_content)
            zf.writestr("README.md", "# Release notes")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_stage_executable_from_zip_success(self):
        staged_exe = stage_executable_from_zip(self.zip_path)
        self.assertTrue(os.path.exists(staged_exe))
        try:
            with open(staged_exe, "rb") as f:
                content = f.read()
            self.assertEqual(content, self.dummy_exe_content)
        finally:
            if os.path.exists(staged_exe):
                os.remove(staged_exe)

    def test_stage_executable_from_zip_missing_exe_raises(self):
        empty_zip = os.path.join(self.temp_dir.name, "empty.zip")
        with zipfile.ZipFile(empty_zip, "w") as zf:
            zf.writestr("notes.txt", "no exe here")

        with self.assertRaises(FileNotFoundError):
            stage_executable_from_zip(empty_zip)

    def test_generate_updater_batch_script_syntax_and_quoting(self):
        pid = 12345
        staged_exe = r"C:\Temp\staged\XO_Game.exe"
        target_exe = r"C:\Program Files\XO Game\XO_Game.exe"

        script = generate_updater_batch_script(
            pid=pid,
            staged_exe=staged_exe,
            target_exe=target_exe
        )

        # Assert key operations are present with quotes
        self.assertIn("tasklist", script)
        self.assertIn(str(pid), script)
        self.assertIn(f'copy /y "{staged_exe}" "{target_exe}"', script)
        self.assertIn(f'start "" "{target_exe}"', script)
        self.assertIn("del", script)

    @patch('utils.updater.webbrowser.open')
    def test_apply_in_place_update_dev_mode_guardrail(self, mock_web_open):
        with patch.object(sys, 'frozen', False, create=True):
            # Running from source should NOT execute batch script
            with patch('subprocess.Popen') as mock_popen:
                result = apply_in_place_update(self.zip_path)
                self.assertFalse(result)
                mock_popen.assert_not_called()
                mock_web_open.assert_called_once()


if __name__ == '__main__':
    unittest.main()
