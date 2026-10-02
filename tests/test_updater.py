"""
Comprehensive Test Suite for Auto-Update Pipeline
Validates SemVer 2.0.0 precedence, channel selection, mandatory updates,
dismissal persistence, cooldowns, and malformed manifest handling.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add game directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'game')))

from utils.updater import (
    SemVer,
    UpdateManifest,
    UpdaterSettings,
    evaluate_update,
    fetch_manifest_from_sources
)


class TestSemVerComparison(unittest.TestCase):
    """Test suite for SemVer 2.0.0 parsing and precedence rules."""

    def test_standard_versions(self):
        v1 = SemVer.parse("5.0.0")
        v2 = SemVer.parse("5.1.0")
        v3 = SemVer.parse("6.0.0")
        self.assertTrue(v1 < v2 < v3)
        self.assertEqual(v1, SemVer.parse("v5.0.0"))

    def test_lenient_versions(self):
        self.assertEqual(SemVer.parse("5.0"), SemVer(5, 0, 0))
        self.assertEqual(SemVer.parse("5"), SemVer(5, 0, 0))

    def test_prerelease_precedence_against_normal(self):
        """Normal version has higher precedence than prerelease of same triple."""
        normal = SemVer.parse("1.0.0")
        rc = SemVer.parse("1.0.0-rc.1")
        beta = SemVer.parse("1.0.0-beta.1")
        self.assertTrue(normal > rc)
        self.assertTrue(normal > beta)
        self.assertTrue(rc > beta)

    def test_semver_spec_precedence_chain(self):
        """
        Verify the exact precedence chain from SemVer 2.0.0 §11:
        1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-alpha.beta < 1.0.0-beta <
        1.0.0-beta.2 < 1.0.0-beta.11 < 1.0.0-rc.1 < 1.0.0
        """
        versions = [
            SemVer.parse("1.0.0-alpha"),
            SemVer.parse("1.0.0-alpha.1"),
            SemVer.parse("1.0.0-alpha.beta"),
            SemVer.parse("1.0.0-beta"),
            SemVer.parse("1.0.0-beta.2"),
            SemVer.parse("1.0.0-beta.11"),
            SemVer.parse("1.0.0-rc.1"),
            SemVer.parse("1.0.0")
        ]
        for i in range(len(versions) - 1):
            self.assertTrue(
                versions[i] < versions[i + 1],
                f"Expected {versions[i]} < {versions[i+1]}"
            )

    def test_build_metadata_ignored_in_precedence(self):
        """Build metadata does not figure into version precedence (SemVer §10)."""
        v1 = SemVer.parse("1.0.0+20130313144700")
        v2 = SemVer.parse("1.0.0+exp.sha.5114f85")
        self.assertEqual(v1, v2)


class TestChannelSelection(unittest.TestCase):
    """Test channel filtering (stable vs prerelease)."""

    def setUp(self):
        self.stable_manifest = UpdateManifest(
            schema_version=1,
            name="XO Game",
            version="5.1.0",
            tag_name="v5.1.0",
            channel="stable",
            published_at="2026-10-02T10:00:00Z",
            release_notes="Stable release",
            release_page_url="https://example.com/release",
            download_url="https://example.com/download.zip",
            file_name="XO_Game.zip"
        )
        self.prerelease_manifest = UpdateManifest(
            schema_version=1,
            name="XO Game",
            version="5.2.0-beta.1",
            tag_name="v5.2.0-beta.1",
            channel="prerelease",
            published_at="2026-10-02T10:00:00Z",
            release_notes="Beta release",
            release_page_url="https://example.com/release-beta",
            download_url="https://example.com/download-beta.zip",
            file_name="XO_Game.zip"
        )

    def test_stable_channel_ignores_prerelease(self):
        has_up, is_mand, reason = evaluate_update(
            manifest=self.prerelease_manifest,
            current_version_str="5.0.0",
            channel="stable"
        )
        self.assertFalse(has_up)
        self.assertIn("Prerelease version ignored", reason)

    def test_prerelease_channel_receives_prerelease(self):
        has_up, is_mand, reason = evaluate_update(
            manifest=self.prerelease_manifest,
            current_version_str="5.0.0",
            channel="prerelease"
        )
        self.assertTrue(has_up)
        self.assertFalse(is_mand)

    def test_stable_channel_accepts_stable(self):
        has_up, is_mand, reason = evaluate_update(
            manifest=self.stable_manifest,
            current_version_str="5.0.0",
            channel="stable"
        )
        self.assertTrue(has_up)
        self.assertFalse(is_mand)


class TestMandatoryUpdates(unittest.TestCase):
    """Test mandatory update rules."""

    def test_explicit_mandatory_flag(self):
        manifest = UpdateManifest(
            schema_version=1,
            name="XO Game",
            version="5.1.0",
            tag_name="v5.1.0",
            channel="stable",
            published_at="",
            release_notes="",
            release_page_url="",
            download_url="",
            file_name="",
            mandatory=True
        )
        has_up, is_mand, _ = evaluate_update(manifest, "5.0.0")
        self.assertTrue(has_up)
        self.assertTrue(is_mand)

    def test_min_supported_version_triggers_mandatory(self):
        manifest = UpdateManifest(
            schema_version=1,
            name="XO Game",
            version="5.2.0",
            tag_name="v5.2.0",
            channel="stable",
            published_at="",
            release_notes="",
            release_page_url="",
            download_url="",
            file_name="",
            min_supported_version="5.1.0"
        )
        # 5.0.0 is below min_supported_version 5.1.0 -> mandatory
        has_up, is_mand, _ = evaluate_update(manifest, "5.0.0")
        self.assertTrue(has_up)
        self.assertTrue(is_mand)

        # 5.1.5 is above min_supported_version 5.1.0 -> optional update
        has_up, is_mand, _ = evaluate_update(manifest, "5.1.5")
        self.assertTrue(has_up)
        self.assertFalse(is_mand)


class TestDismissalAndCooldown(unittest.TestCase):
    """Test dismissal persistence and cooldown mechanics."""

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.settings = UpdaterSettings(filepath=self.temp_file.name)
        self.manifest = UpdateManifest(
            schema_version=1,
            name="XO Game",
            version="5.1.0",
            tag_name="v5.1.0",
            channel="stable",
            published_at="",
            release_notes="",
            release_page_url="",
            download_url="",
            file_name=""
        )

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_dismissal_suppresses_automatic_check(self):
        # First automatic check triggers update
        has_up, _, _ = evaluate_update(
            self.manifest, "5.0.0", is_manual_check=False, settings=self.settings
        )
        self.assertTrue(has_up)

        # Player dismisses 5.1.0
        self.settings.dismiss_version("5.1.0")
        self.assertTrue(self.settings.is_dismissed("5.1.0"))

        # Subsequent automatic check is suppressed
        has_up, _, reason = evaluate_update(
            self.manifest, "5.0.0", is_manual_check=False, settings=self.settings
        )
        self.assertFalse(has_up)
        self.assertIn("dismissed", reason)

        # But manual check still alerts the user
        has_up, _, _ = evaluate_update(
            self.manifest, "5.0.0", is_manual_check=True, settings=self.settings
        )
        self.assertTrue(has_up)

    def test_cooldown_behavior(self):
        self.assertTrue(self.settings.can_auto_check(cooldown_seconds=60))
        self.settings.record_check_time()
        self.assertFalse(self.settings.can_auto_check(cooldown_seconds=60))


class TestMalformedManifestHandling(unittest.TestCase):
    """Test resiliency against malformed metadata or server errors."""

    @patch('utils.updater.fetch_json')
    def test_handles_empty_or_broken_manifest(self, mock_fetch):
        mock_fetch.return_value = {"broken": "data"}
        manifest, err = fetch_manifest_from_sources(["https://bad.url"])
        self.assertIsNone(manifest)
        self.assertIsNotNone(err)

    @patch('utils.updater.fetch_json')
    def test_handles_network_timeout(self, mock_fetch):
        mock_fetch.return_value = None
        manifest, err = fetch_manifest_from_sources(["https://timeout.url"])
        self.assertIsNone(manifest)
        self.assertIsNotNone(err)


if __name__ == '__main__':
    unittest.main()
