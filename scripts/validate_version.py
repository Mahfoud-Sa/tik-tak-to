#!/usr/bin/env python3
"""
Version validation and synchronization utility.
Validates that embedded game versions, Windows version resources,
and release tags match semantic versioning requirements.
"""

import argparse
import os
import re
import sys

SEMVER_REGEX = re.compile(
    r"^v?(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def normalize_version(v: str) -> str:
    """Normalize version string by stripping leading 'v' and whitespace."""
    return v.strip().lstrip("vV")


def is_valid_semver(v: str) -> bool:
    """Check if string is a valid semantic version."""
    return bool(SEMVER_REGEX.match(v.strip()))


def get_config_version(config_path: str) -> str:
    """Extract __version__ from game/config.py."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError(f"Could not find __version__ in {config_path}")
    return match.group(1).strip()


def get_version_txt_version(version_txt_path: str) -> str:
    """Extract FileVersion from game/version.txt."""
    if not os.path.exists(version_txt_path):
        raise FileNotFoundError(f"version.txt not found: {version_txt_path}")
    
    with open(version_txt_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    match = re.search(r"StringStruct\(u'FileVersion',\s*u'([^']+)'\)", content)
    if not match:
        raise ValueError(f"Could not find FileVersion in {version_txt_path}")
    return match.group(1).strip()


def sync_versions(target_version: str, config_path: str, version_txt_path: str):
    """Synchronize version across config.py and version.txt."""
    norm_version = normalize_version(target_version)
    if not is_valid_semver(norm_version):
        raise ValueError(f"Invalid semantic version: {target_version}")
    
    match = SEMVER_REGEX.match(norm_version)
    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch"))
    
    # 1. Update config.py
    with open(config_path, "r", encoding="utf-8") as f:
        config_content = f.read()
    
    new_config = re.sub(
        r'__version__\s*=\s*["\'][^"\']+["\']',
        f'__version__ = "{norm_version}"',
        config_content,
        count=1
    )
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(new_config)
    print(f"Updated {config_path} to version {norm_version}")
    
    # 2. Update version.txt if it exists
    if os.path.exists(version_txt_path):
        with open(version_txt_path, "r", encoding="utf-8") as f:
            vtxt_content = f.read()
        
        # Update tuple numbers
        vtxt_content = re.sub(
            r'filevers=\([^)]+\)',
            f'filevers=({major}, {minor}, {patch}, 0)',
            vtxt_content
        )
        vtxt_content = re.sub(
            r'prodvers=\([^)]+\)',
            f'prodvers=({major}, {minor}, {patch}, 0)',
            vtxt_content
        )
        # Update string structs
        vtxt_content = re.sub(
            r"StringStruct\(u'FileVersion',\s*u'[^']+'\)",
            f"StringStruct(u'FileVersion', u'{norm_version}')",
            vtxt_content
        )
        vtxt_content = re.sub(
            r"StringStruct\(u'ProductVersion',\s*u'[^']+'\)",
            f"StringStruct(u'ProductVersion', u'{norm_version}')",
            vtxt_content
        )
        with open(version_txt_path, "w", encoding="utf-8") as f:
            f.write(vtxt_content)
        print(f"Updated {version_txt_path} to version {norm_version}")


def main():
    parser = argparse.ArgumentParser(description="Validate and sync game versions.")
    parser.add_argument("--expected-version", help="Assert version matches this target")
    parser.add_argument("--sync", help="Synchronize project files to this version")
    parser.add_argument("--config-path", default="game/config.py", help="Path to config.py")
    parser.add_argument("--version-txt-path", default="game/version.txt", help="Path to version.txt")
    
    args = parser.parse_args()
    
    config_path = os.path.abspath(args.config_path)
    version_txt_path = os.path.abspath(args.version_txt_path)
    
    if args.sync:
        sync_versions(args.sync, config_path, version_txt_path)
        print("Version synchronization completed successfully.")
        return 0
    
    cfg_ver = normalize_version(get_config_version(config_path))
    vtxt_ver = normalize_version(get_version_txt_version(version_txt_path))
    
    print(f"config.py version:   {cfg_ver}")
    print(f"version.txt version: {vtxt_ver}")
    
    if not is_valid_semver(cfg_ver):
        print(f"ERROR: config.py version '{cfg_ver}' is not valid SemVer!", file=sys.stderr)
        return 1
    
    if not is_valid_semver(vtxt_ver):
        print(f"ERROR: version.txt version '{vtxt_ver}' is not valid SemVer!", file=sys.stderr)
        return 1
    
    if cfg_ver != vtxt_ver:
        print(f"ERROR: Version mismatch between config.py ({cfg_ver}) and version.txt ({vtxt_ver})!", file=sys.stderr)
        return 1
    
    if args.expected_version:
        exp_ver = normalize_version(args.expected_version)
        if not is_valid_semver(exp_ver):
            print(f"ERROR: Expected version '{exp_ver}' is not valid SemVer!", file=sys.stderr)
            return 1
        if cfg_ver != exp_ver:
            print(f"ERROR: Codebase version ({cfg_ver}) does not match expected version ({exp_ver})!", file=sys.stderr)
            return 1
        print(f"Validation SUCCESS: All files match expected version '{exp_ver}'.")
    else:
        print("Validation SUCCESS: Codebase versions are synchronized and valid.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
