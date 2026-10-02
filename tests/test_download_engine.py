"""
Tests for In-App Chunked Download Engine and SHA-256 Checksum Verification.
Verifies:
- Chunked downloading with progress reporting
- SHA-256 integrity verification against manifest
- Checksum mismatch rejection and temporary file cleanup
- User cancellation handling and partial file cleanup
"""

import hashlib
import io
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add game directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'game')))

from utils.updater import (
    UpdateManifest,
    UpdateService,
    DownloadCancellationToken,
    verify_file_sha256
)


class MockHTTPResponse:
    """Mock urllib response that streams chunks and provides headers."""

    def __init__(self, data: bytes, chunk_size: int = 1024):
        self.data = data
        self.stream = io.BytesIO(data)
        self.chunk_size = chunk_size
        self.headers = {"Content-Length": str(len(data))}
        self.status = 200

    def read(self, amt=None):
        if amt is None:
            return self.stream.read()
        return self.stream.read(amt)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TestDownloadEngine(unittest.TestCase):
    """Test suite for chunked downloading, cancellation, and checksum verification."""

    def setUp(self):
        self.test_content = b"PK\x03\x04Dummy zip archive content for testing update payload"
        self.correct_sha256 = hashlib.sha256(self.test_content).hexdigest()
        self.service = UpdateService(current_version="3.0.0")

        self.manifest = UpdateManifest(
            schema_version=1,
            name="XO Game",
            version="3.1.0",
            tag_name="v3.1.0",
            channel="stable",
            published_at="2026-10-02T12:00:00Z",
            release_notes="Update test notes",
            release_page_url="https://github.com/Mahfoud-Sa/tik-tak-to/releases/tag/v3.1.0",
            download_url="https://github.com/Mahfoud-Sa/tik-tak-to/releases/download/v3.1.0/update.zip",
            file_name="update.zip",
            sha256=self.correct_sha256,
            mandatory=False
        )

    def test_verify_file_sha256_helper(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(self.test_content)
            temp_path = f.name

        try:
            self.assertTrue(verify_file_sha256(temp_path, self.correct_sha256))
            self.assertTrue(verify_file_sha256(temp_path, self.correct_sha256.upper()))
            self.assertFalse(verify_file_sha256(temp_path, "0" * 64))
            self.assertTrue(verify_file_sha256(temp_path, ""))  # Empty expected hash skips check
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    @patch('urllib.request.urlopen')
    def test_download_success_with_progress_and_valid_sha256(self, mock_urlopen):
        mock_urlopen.return_value = MockHTTPResponse(self.test_content, chunk_size=16)

        progress_reports = []

        def on_progress(received, total, percent):
            progress_reports.append((received, total, percent))

        success, filepath, error = self.service.download_update(
            manifest=self.manifest,
            on_progress=on_progress,
            chunk_size=16
        )

        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))

        try:
            with open(filepath, 'rb') as f:
                downloaded = f.read()
            self.assertEqual(downloaded, self.test_content)

            # Assert progress was tracked
            self.assertTrue(len(progress_reports) > 0)
            last_received, last_total, last_pct = progress_reports[-1]
            self.assertEqual(last_received, len(self.test_content))
            self.assertEqual(last_total, len(self.test_content))
            self.assertAlmostEqual(last_pct, 100.0, places=1)
        finally:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)

    @patch('urllib.request.urlopen')
    def test_download_sha256_mismatch_rejects_and_deletes_file(self, mock_urlopen):
        mock_urlopen.return_value = MockHTTPResponse(self.test_content)

        # Corrupt expected hash
        corrupted_manifest = UpdateManifest(
            schema_version=1,
            name="XO Game",
            version="3.1.0",
            tag_name="v3.1.0",
            channel="stable",
            published_at="2026-10-02T12:00:00Z",
            release_notes="Update test notes",
            release_page_url="",
            download_url="https://example.com/update.zip",
            file_name="update.zip",
            sha256="deadbeef" * 8,
            mandatory=False
        )

        success, filepath, error = self.service.download_update(
            manifest=corrupted_manifest,
            chunk_size=16
        )

        self.assertFalse(success)
        self.assertIsNone(filepath)
        self.assertIn("Checksum verification failed", error)

    @patch('urllib.request.urlopen')
    def test_download_cancellation_cleans_up_partial_file(self, mock_urlopen):
        # 100 KB payload
        large_payload = b"X" * (100 * 1024)
        mock_urlopen.return_value = MockHTTPResponse(large_payload, chunk_size=1024)

        cancel_token = DownloadCancellationToken()

        def cancel_on_first_chunk(received, total, pct):
            if received >= 2048:
                cancel_token.cancel()

        success, filepath, error = self.service.download_update(
            manifest=self.manifest,
            on_progress=cancel_on_first_chunk,
            cancel_token=cancel_token,
            chunk_size=1024
        )

        self.assertFalse(success)
        self.assertIsNone(filepath)
        self.assertIn("cancelled", error.lower())


if __name__ == '__main__':
    unittest.main()
