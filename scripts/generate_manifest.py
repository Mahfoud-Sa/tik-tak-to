#!/usr/bin/env python3
"""
Manifest generator utility.
Generates public update manifest JSON adhering to schema version 1.
"""

import argparse
import datetime
import json
import os
import sys

from validate_version import normalize_version, is_valid_semver


def generate_manifest(
    version: str,
    channel: str,
    repo: str,
    tag: str,
    release_notes: str,
    min_supported_version: str = "",
    mandatory: bool = False,
    download_url: str = "",
    file_name: str = "XO_Game-windows-x64.zip",
    sha256: str = "",
    output_path: str = "version.json"
) -> dict:
    """Generate and write the update manifest JSON."""
    norm_version = normalize_version(version)
    if not is_valid_semver(norm_version):
        raise ValueError(f"Invalid semantic version: {version}")
    
    if not tag:
        tag = f"v{norm_version}"
    
    if not download_url:
        download_url = f"https://github.com/{repo}/releases/download/{tag}/{file_name}"
    
    release_page_url = f"https://github.com/{repo}/releases/tag/{tag}"
    
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    manifest = {
        "$schema": f"https://raw.githubusercontent.com/{repo}/main/schemas/version-manifest.schema.json",
        "schema_version": 1,
        "name": "XO Game",
        "version": norm_version,
        "tag_name": tag,
        "channel": channel,
        "published_at": now_iso,
        "mandatory": bool(mandatory),
        "release_notes": release_notes or f"Release {tag}",
        "release_page_url": release_page_url,
        "platforms": {
            "windows": {
                "file_name": file_name,
                "download_url": download_url,
                "sha256": sha256
            }
        }
    }
    
    if min_supported_version:
        norm_min = normalize_version(min_supported_version)
        if is_valid_semver(norm_min):
            manifest["min_supported_version"] = norm_min
    
    # Ensure directory exists
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"Update manifest written to {output_path}")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Generate public update manifest JSON.")
    parser.add_argument("--version", required=True, help="Release version (e.g. 5.1.0)")
    parser.add_argument("--channel", default="stable", choices=["stable", "prerelease"], help="Release channel")
    parser.add_argument("--repo", default="Mahfoud-Sa/tik-tak-to", help="GitHub repo (owner/repo)")
    parser.add_argument("--tag", help="Git tag name")
    parser.add_argument("--release-notes", default="", help="Release notes text or markdown")
    parser.add_argument("--notes-file", help="Path to file containing release notes")
    parser.add_argument("--min-supported-version", default="", help="Minimum supported version")
    parser.add_argument("--mandatory", action="store_true", help="Mark update as mandatory")
    parser.add_argument("--download-url", default="", help="Direct download URL for Windows release")
    parser.add_argument("--file-name", default="XO_Game-windows-x64.zip", help="Artifact file name")
    parser.add_argument("--sha256", default="", help="SHA256 checksum of artifact")
    parser.add_argument("--output", default="version.json", help="Output file path")
    
    args = parser.parse_args()
    
    notes = args.release_notes
    if args.notes_file and os.path.exists(args.notes_file):
        with open(args.notes_file, "r", encoding="utf-8") as f:
            notes = f.read()
    
    try:
        generate_manifest(
            version=args.version,
            channel=args.channel,
            repo=args.repo,
            tag=args.tag,
            release_notes=notes,
            min_supported_version=args.min_supported_version,
            mandatory=args.mandatory,
            download_url=args.download_url,
            file_name=args.file_name,
            sha256=args.sha256,
            output_path=args.output
        )
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
