#!/usr/bin/env python3
"""
Unit tests for manifest and release history generation.
"""

import json
import os
import shutil
import tempfile
import unittest

from scripts.generate_manifest import generate_manifest, update_release_history, semver_sort_key


class TestManifestGenerator(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manifest_file = os.path.join(self.test_dir, "version.json")
        self.history_file = os.path.join(self.test_dir, "releases.json")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_generate_single_manifest(self):
        manifest = generate_manifest(
            version="3.0.1",
            channel="stable",
            repo="Mahfoud-Sa/tik-tak-to",
            tag="v3.0.1",
            release_notes="Initial test release",
            output_path=self.manifest_file
        )
        self.assertTrue(os.path.exists(self.manifest_file))
        self.assertEqual(manifest["version"], "3.0.1")
        self.assertEqual(manifest["channel"], "stable")
        self.assertEqual(manifest["tag_name"], "v3.0.1")

    def test_update_release_history_ordering_and_prerelease(self):
        # 1. Add v1.0.0
        m1 = {
            "name": "XO Game v1.0.0",
            "version": "1.0.0",
            "tag_name": "v1.0.0",
            "channel": "stable",
            "published_at": "2023-01-01T00:00:00Z",
            "mandatory": False,
            "release_notes": "First release",
            "release_page_url": "https://example.com/v1.0.0",
            "platforms": {}
        }
        update_release_history(self.history_file, m1)
        
        # 2. Add v2.0.0-beta.1 (prerelease)
        m2 = {
            "name": "XO Game v2.0.0-beta.1",
            "version": "2.0.0-beta.1",
            "tag_name": "v2.0.0-beta.1",
            "channel": "prerelease",
            "published_at": "2024-01-01T00:00:00Z",
            "mandatory": False,
            "release_notes": "Beta release",
            "release_page_url": "https://example.com/v2.0.0-beta.1",
            "platforms": {}
        }
        h2 = update_release_history(self.history_file, m2)
        
        # Latest stable should STILL be 1.0.0
        self.assertEqual(h2["latest_stable"], "1.0.0")
        self.assertEqual(len(h2["releases"]), 2)
        # 2.0.0-beta.1 is semver greater than 1.0.0, so it appears first in the list
        self.assertEqual(h2["releases"][0]["version"], "2.0.0-beta.1")
        self.assertEqual(h2["releases"][1]["version"], "1.0.0")

        # 3. Add v2.0.0 (stable)
        m3 = {
            "name": "XO Game v2.0.0",
            "version": "2.0.0",
            "tag_name": "v2.0.0",
            "channel": "stable",
            "published_at": "2024-02-01T00:00:00Z",
            "mandatory": False,
            "release_notes": "Stable v2",
            "release_page_url": "https://example.com/v2.0.0",
            "platforms": {}
        }
        h3 = update_release_history(self.history_file, m3)
        self.assertEqual(h3["latest_stable"], "2.0.0")
        self.assertEqual(h3["releases"][0]["version"], "2.0.0")
        self.assertEqual(h3["releases"][1]["version"], "2.0.0-beta.1")
        self.assertEqual(h3["releases"][2]["version"], "1.0.0")


if __name__ == "__main__":
    unittest.main()
