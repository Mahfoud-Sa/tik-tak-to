#!/usr/bin/env python3
"""
Release build and packaging automation script.
Executes PyInstaller on Windows, builds the .exe, packages the zip bundle,
and calculates SHA256 checksums.
"""

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import zipfile


def calculate_sha256(filepath: str) -> str:
    """Calculate SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


def build_release(version: str, tag: str = "", output_dir: str = "dist"):
    """Build executable and create distribution zip package."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    game_dir = os.path.join(root_dir, "game")
    out_dir = os.path.abspath(output_dir)
    
    os.makedirs(out_dir, exist_ok=True)
    
    if not tag:
        tag = f"v{version.lstrip('vV')}"
    
    # 1. Run build_exe.py inside game/
    print(f"Building Windows executable for {tag}...")
    build_exe_script = os.path.join(game_dir, "build_exe.py")
    result = subprocess.run([sys.executable, build_exe_script], cwd=game_dir)
    if result.returncode != 0:
        raise RuntimeError("PyInstaller build failed!")
    
    exe_src = os.path.join(game_dir, "dist", "Tik Tak Tok.exe")
    if not os.path.exists(exe_src):
        exe_src_fallback = os.path.join(game_dir, "dist", "XO_Game.exe")
        if os.path.exists(exe_src_fallback):
            exe_src = exe_src_fallback
        else:
            raise FileNotFoundError(f"Expected built executable not found at: {exe_src}")
    
    # Copy standalone exe to output directory
    exe_dest = os.path.join(out_dir, "Tik Tak Tok.exe")
    shutil.copy2(exe_src, exe_dest)
    print(f"Copied {exe_src} -> {exe_dest}")
    
    # 2. Create distribution zip
    zip_name = f"Tik_Tak_Tok-{tag}-windows-x64.zip"
    zip_path = os.path.join(out_dir, zip_name)
    
    print(f"Packaging {zip_name}...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(exe_dest, arcname="Tik Tak Tok.exe")
        # Include README if available
        readme_src = os.path.join(game_dir, "README.md")
        if os.path.exists(readme_src):
            zf.write(readme_src, arcname="README.md")
    
    print(f"Distribution package created at: {zip_path}")
    
    # 3. Calculate checksums
    exe_hash = calculate_sha256(exe_dest)
    zip_hash = calculate_sha256(zip_path)
    
    checksums_file = os.path.join(out_dir, "checksums.txt")
    with open(checksums_file, "w", encoding="utf-8") as f:
        f.write(f"{exe_hash}  Tik Tak Tok.exe\n")
        f.write(f"{zip_hash}  {zip_name}\n")
    
    print(f"Checksums saved to: {checksums_file}")
    print(f"  Tik Tak Tok.exe: {exe_hash}")
    print(f"  {zip_name}: {zip_hash}")
    
    return {
        "exe_path": exe_dest,
        "zip_path": zip_path,
        "zip_name": zip_name,
        "exe_sha256": exe_hash,
        "zip_sha256": zip_hash,
        "checksums_file": checksums_file
    }


def main():
    parser = argparse.ArgumentParser(description="Build and package game release.")
    parser.add_argument("--version", default="5.0.0", help="Release version")
    parser.add_argument("--tag", default="", help="Release tag")
    parser.add_argument("--output-dir", default="dist", help="Output distribution folder")
    
    args = parser.parse_args()
    
    try:
        build_release(version=args.version, tag=args.tag, output_dir=args.output_dir)
        return 0
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
