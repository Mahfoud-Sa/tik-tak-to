#!/usr/bin/env python3
"""
Manifest and release history generator utility.
Generates public update manifest JSON and maintains the historical
releases.json catalog adhering to schema version 1.
"""

import argparse
import datetime
import json
import os
import re
import sys

try:
    from validate_version import normalize_version, is_valid_semver
except ImportError:
    from scripts.validate_version import normalize_version, is_valid_semver


def semver_sort_key(version_str: str):
    """Generate a comparable tuple for semantic version sorting (highest first)."""
    norm = normalize_version(version_str)
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9a-zA-Z.-]+))?", norm)
    if not match:
        return (0, 0, 0, 0, "")
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))
    prerelease = match.group(4)
    is_stable = 1 if prerelease is None else 0
    return (major, minor, patch, is_stable, prerelease or "")


def update_release_history(
    history_path: str,
    manifest: dict,
    repo: str = "Mahfoud-Sa/tik-tak-to"
) -> dict:
    """Update or prepend the manifest into the release history file."""
    now_iso = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    history = {
        "$schema": f"https://raw.githubusercontent.com/{repo}/main/schemas/version-history.schema.json",
        "schema_version": 1,
        "latest_stable": "",
        "updated_at": now_iso,
        "releases": []
    }
    
    if os.path.exists(history_path):
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict) and "releases" in loaded:
                    history = loaded
        except Exception as e:
            print(f"Warning: Could not parse existing history file ({e}), initializing new one.", file=sys.stderr)
            
    history["updated_at"] = now_iso
    
    # Build release entry
    release_entry = {
        "name": manifest.get("name", f"XO Game {manifest['tag_name']}"),
        "version": manifest["version"],
        "tag_name": manifest["tag_name"],
        "channel": manifest["channel"],
        "published_at": manifest["published_at"],
        "mandatory": manifest.get("mandatory", False),
        "release_notes": manifest.get("release_notes", ""),
        "release_page_url": manifest.get("release_page_url", ""),
        "platforms": manifest.get("platforms", {})
    }
    if manifest.get("min_supported_version"):
        release_entry["min_supported_version"] = manifest["min_supported_version"]

    # Upsert entry
    existing_index = None
    for i, item in enumerate(history.get("releases", [])):
        if item.get("tag_name") == release_entry["tag_name"] or item.get("version") == release_entry["version"]:
            existing_index = i
            break
            
    if existing_index is not None:
        history["releases"][existing_index] = release_entry
    else:
        history["releases"].insert(0, release_entry)
        
    # Sort releases: newest semver first
    history["releases"].sort(key=lambda r: semver_sort_key(r.get("version", "0.0.0")), reverse=True)
    
    # Determine latest stable version
    latest_stable = ""
    for r in history["releases"]:
        if r.get("channel") == "stable":
            latest_stable = r.get("version", "")
            break
    history["latest_stable"] = latest_stable
    
    out_dir = os.path.dirname(os.path.abspath(history_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
        
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
        f.write("\n")
        
    print(f"Release history updated at {history_path}")
    return history


def generate_manifest(
    version: str,
    channel: str,
    repo: str,
    tag: str,
    release_notes: str,
    min_supported_version: str = "",
    mandatory: bool = False,
    download_url: str = "",
    file_name: str = "Tik_Tak_Tok-windows-x64.zip",
    sha256: str = "",
    output_path: str = "version.json",
    history_path: str = ""
) -> dict:
    """Generate and write the update manifest JSON and optionally update history."""
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
        "name": f"Tik Tak Tok {tag}",
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
        f.write("\n")
    
    print(f"Update manifest written to {output_path}")
    
    if history_path:
        update_release_history(history_path, manifest, repo=repo)
        
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Generate public update manifest JSON and update history.")
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
    parser.add_argument("--history-file", default="", help="Path to releases.json history file to update")
    
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
            output_path=args.output,
            history_path=args.history_file
        )
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
