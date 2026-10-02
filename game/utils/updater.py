"""
Auto-Update Engine for Tik Tak Tok (لعبة XO)
Implements SemVer 2.0.0 parsing & comparison, public update manifest ingestion,
persistent dismissal tracking, channel filtering, and async lifecycle checks.
"""

import json
import os
import re
import sys
import time
import hashlib
import tempfile
import zipfile
import subprocess
import webbrowser
import urllib.request
import urllib.error
import threading
from typing import Optional, Tuple, Callable, List, Union, Dict, Any
from dataclasses import dataclass, field


# =============================================================================
# SEMVER 2.0.0 IMPLEMENTATION
# =============================================================================

SEMVER_REGEX = re.compile(
    r"^v?(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def _compare_identifiers(a: Union[int, str], b: Union[int, str]) -> int:
    """
    Compare two prerelease identifiers according to SemVer 2.0.0 §11.
    - Numbers are compared numerically.
    - Strings are compared lexicographically in ASCII sort order.
    - Numbers have lower precedence than alphanumeric identifiers.
    Returns: -1 if a < b, 1 if a > b, 0 if a == b
    """
    a_is_int = isinstance(a, int)
    b_is_int = isinstance(b, int)
    
    if a_is_int and b_is_int:
        if a < b:
            return -1
        elif a > b:
            return 1
        return 0
    elif a_is_int and not b_is_int:
        # Numeric identifiers have lower precedence
        return -1
    elif not a_is_int and b_is_int:
        return 1
    else:
        # Both are strings
        if str(a) < str(b):
            return -1
        elif str(a) > str(b):
            return 1
        return 0


@dataclass(frozen=True)
class SemVer:
    """Semantic Versioning 2.0.0 compliant version class."""
    major: int
    minor: int
    patch: int
    prerelease: Tuple[Union[int, str], ...] = ()
    buildmetadata: Tuple[str, ...] = ()

    @classmethod
    def parse(cls, version_str: str) -> "SemVer":
        """Parse a SemVer 2.0.0 version string."""
        if not version_str or not isinstance(version_str, str):
            raise ValueError(f"Invalid version string: {version_str}")
        
        clean = version_str.strip()
        match = SEMVER_REGEX.match(clean)
        if not match:
            # Fallback for lenient numbers like "5.0"
            parts = re.findall(r'\d+', clean)
            if not parts:
                raise ValueError(f"Cannot parse version: {version_str}")
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            return cls(major, minor, patch)
        
        major = int(match.group("major"))
        minor = int(match.group("minor"))
        patch = int(match.group("patch"))
        
        raw_pre = match.group("prerelease")
        prerelease_parts = []
        if raw_pre:
            for item in raw_pre.split('.'):
                if item.isdigit():
                    prerelease_parts.append(int(item))
                else:
                    prerelease_parts.append(item)
        
        raw_build = match.group("buildmetadata")
        build_parts = tuple(raw_build.split('.')) if raw_build else ()
        
        return cls(major, minor, patch, tuple(prerelease_parts), build_parts)

    @property
    def is_prerelease(self) -> bool:
        """Return True if this is a pre-release version."""
        return len(self.prerelease) > 0

    def __str__(self) -> str:
        s = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            s += "-" + ".".join(str(p) for p in self.prerelease)
        if self.buildmetadata:
            s += "+" + ".".join(self.buildmetadata)
        return s

    def _compare(self, other: "SemVer") -> int:
        """Compare self with other according to SemVer 2.0.0 precedence."""
        if not isinstance(other, SemVer):
            raise TypeError(f"Cannot compare SemVer with {type(other)}")
        
        # 1. Compare major, minor, patch numerically
        for a, b in [(self.major, other.major), (self.minor, other.minor), (self.patch, other.patch)]:
            if a < b:
                return -1
            elif a > b:
                return 1
        
        # 2. When major, minor, patch are equal, normal version > prerelease version
        if not self.is_prerelease and other.is_prerelease:
            return 1
        if self.is_prerelease and not other.is_prerelease:
            return -1
        if not self.is_prerelease and not other.is_prerelease:
            return 0
        
        # 3. Both are prereleases: compare identifier by identifier
        for i in range(min(len(self.prerelease), len(other.prerelease))):
            cmp = _compare_identifiers(self.prerelease[i], other.prerelease[i])
            if cmp != 0:
                return cmp
        
        # Larger set of prerelease fields has higher precedence
        if len(self.prerelease) < len(other.prerelease):
            return -1
        elif len(self.prerelease) > len(other.prerelease):
            return 1
        
        return 0

    def __lt__(self, other: "SemVer") -> bool:
        return self._compare(other) < 0

    def __le__(self, other: "SemVer") -> bool:
        return self._compare(other) <= 0

    def __gt__(self, other: "SemVer") -> bool:
        return self._compare(other) > 0

    def __ge__(self, other: "SemVer") -> bool:
        return self._compare(other) >= 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return False
        return self._compare(other) == 0


# =============================================================================
# MANIFEST MODEL & SETTINGS
# =============================================================================

@dataclass
class UpdateManifest:
    """Public update manifest data."""
    schema_version: int
    name: str
    version: str
    tag_name: str
    channel: str
    published_at: str
    release_notes: str
    release_page_url: str
    download_url: str
    file_name: str
    sha256: str = ""
    min_supported_version: Optional[str] = None
    mandatory: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "UpdateManifest":
        """Construct manifest from JSON dict."""
        platforms = data.get("platforms", {})
        win_info = platforms.get("windows", {})
        
        return cls(
            schema_version=data.get("schema_version", 1),
            name=data.get("name", "Tik Tak Tok"),
            version=data.get("version", "").lstrip("vV"),
            tag_name=data.get("tag_name") or f"v{data.get('version', '')}",
            channel=data.get("channel", "stable"),
            published_at=data.get("published_at", ""),
            release_notes=data.get("release_notes", ""),
            release_page_url=data.get("release_page_url", ""),
            download_url=win_info.get("download_url", data.get("release_page_url", "")),
            file_name=win_info.get("file_name", "Tik_Tak_Tok-windows-x64.zip"),
            sha256=win_info.get("sha256", ""),
            min_supported_version=data.get("min_supported_version"),
            mandatory=bool(data.get("mandatory", False))
        )


class UpdaterSettings:
    """Manages persistent update settings such as dismissed versions and cooldowns."""
    
    def __init__(self, filepath: Optional[str] = None):
        if filepath is None:
            home = os.path.expanduser("~")
            self.filepath = os.path.join(home, ".xo_game_updater.json")
        else:
            self.filepath = filepath
        self._data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def get_dismissed_version(self) -> Optional[str]:
        return self._data.get("dismissed_version")

    def dismiss_version(self, version: str):
        """Mark a version as dismissed by the user."""
        self._data["dismissed_version"] = version.lstrip("vV")
        self._data["dismissed_at"] = time.time()
        self._save()

    def clear_dismissal(self):
        """Clear dismissed version flag."""
        if "dismissed_version" in self._data:
            del self._data["dismissed_version"]
            self._save()

    def is_dismissed(self, version: str) -> bool:
        """Check if this version was dismissed by the player."""
        dismissed = self.get_dismissed_version()
        if not dismissed:
            return False
        return dismissed == version.lstrip("vV")

    def get_preferred_channel(self) -> str:
        return self._data.get("preferred_channel", "stable")

    def set_preferred_channel(self, channel: str):
        self._data["preferred_channel"] = channel
        self._save()

    def get_last_check_time(self) -> float:
        return float(self._data.get("last_check_time", 0.0))

    def record_check_time(self):
        self._data["last_check_time"] = time.time()
        self._save()

    def can_auto_check(self, cooldown_seconds: int = 900) -> bool:
        """Return True if enough time has passed since last check."""
        now = time.time()
        return (now - self.get_last_check_time()) >= cooldown_seconds


class DownloadCancellationToken:
    """Thread-safe cancellation token for async download operations."""

    def __init__(self):
        self._is_cancelled = False
        self._lock = threading.Lock()

    def cancel(self):
        with self._lock:
            self._is_cancelled = True

    @property
    def is_cancelled(self) -> bool:
        with self._lock:
            return self._is_cancelled


def verify_file_sha256(filepath: str, expected_sha256: str) -> bool:
    """
    Verify file against expected sha256 hex string (case-insensitive).
    If expected_sha256 is empty or None, verification is skipped and returns True.
    """
    if not expected_sha256:
        return True
    if not os.path.exists(filepath):
        return False
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest().lower() == expected_sha256.strip().lower()


# Backward compatibility alias
UpdateInfo = UpdateManifest


# =============================================================================
# MANIFEST FETCHING & EVALUATION
# =============================================================================

def fetch_json(url: str, timeout: int = 5) -> Optional[dict]:
    """Fetch JSON from a URL with standard user-agent."""
    headers = {
        "User-Agent": "XO-Game-UpdateChecker/5.0",
        "Accept": "application/json"
    }
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            if resp.status == 200:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
    except Exception:
        return None
    return None


def fetch_manifest_from_sources(
    sources: List[str],
    timeout: int = 5
) -> Tuple[Optional[UpdateManifest], Optional[str]]:
    """
    Query candidate URLs in order until a valid manifest is parsed.
    Returns (manifest, error_message)
    """
    for url in sources:
        data = fetch_json(url, timeout=timeout)
        if data and isinstance(data, dict):
            # Check if this is GitHub Releases API format or our manifest format
            if "tag_name" in data and "version" not in data:
                # GitHub API fallback format
                tag = data.get("tag_name", "")
                manifest = UpdateManifest(
                    schema_version=1,
                    name=data.get("name") or "XO Game",
                    version=tag.lstrip("vV"),
                    tag_name=tag,
                    channel="prerelease" if data.get("prerelease") else "stable",
                    published_at=data.get("published_at", ""),
                    release_notes=data.get("body", ""),
                    release_page_url=data.get("html_url", ""),
                    download_url=data.get("html_url", ""),
                    file_name="XO_Game-windows-x64.zip",
                    mandatory=False
                )
                return manifest, None
            elif "version" in data:
                # Custom Manifest schema
                try:
                    manifest = UpdateManifest.from_dict(data)
                    return manifest, None
                except Exception:
                    continue

    return None, "Unable to reach update servers or parse release metadata."


def evaluate_update(
    manifest: UpdateManifest,
    current_version_str: str,
    channel: str = "stable",
    is_manual_check: bool = False,
    settings: Optional[UpdaterSettings] = None
) -> Tuple[bool, bool, Optional[str]]:
    """
    Evaluate if an update should be presented to the player.
    
    Returns:
        (is_update_available, is_mandatory, reason)
    """
    try:
        curr_ver = SemVer.parse(current_version_str)
        remote_ver = SemVer.parse(manifest.version)
    except Exception as e:
        return False, False, f"Version parsing error: {e}"

    # 1. Compare versions
    if remote_ver <= curr_ver:
        return False, False, "Game is already up to date."

    # 2. Check channel compatibility
    # If user is on stable channel and remote is prerelease, skip unless user opted in
    if channel == "stable" and manifest.channel != "stable":
        return False, False, "Prerelease version ignored on stable channel."

    # 3. Determine if update is mandatory
    is_mandatory = manifest.mandatory
    if manifest.min_supported_version:
        try:
            min_ver = SemVer.parse(manifest.min_supported_version)
            if curr_ver < min_ver:
                is_mandatory = True
        except Exception:
            pass

    # 4. Check dismissal for non-mandatory updates during automatic checks
    if not is_manual_check and not is_mandatory:
        if settings and settings.is_dismissed(manifest.version):
            return False, False, "Update was previously dismissed."

    return True, is_mandatory, None


# =============================================================================
# UPDATE SERVICE
# =============================================================================

class UpdateService:
    """
    Manages in-game update checking, cooldowns, and async notifications.
    """

    def __init__(
        self,
        current_version: str,
        repo: str = "Mahfoud-Sa/tik-tak-to",
        cooldown_seconds: int = 900,
        settings: Optional[UpdaterSettings] = None
    ):
        self.current_version = current_version
        self.repo = repo
        self.cooldown_seconds = cooldown_seconds
        self.settings = settings or UpdaterSettings()
        self._is_checking = False
        self._lock = threading.Lock()

        # Primary, secondary, and fallback update manifest URLs
        self.manifest_urls = [
            f"https://mahfoud-sa.github.io/tik-tak-to/updates/version.json",
            f"https://raw.githubusercontent.com/{self.repo}/main/docs/updates/version.json",
            f"https://github.com/{self.repo}/releases/latest/download/version.json",
            f"https://api.github.com/repos/{self.repo}/releases/latest"
        ]

    def check_for_updates(
        self,
        is_manual: bool = False,
        channel: Optional[str] = None
    ) -> Tuple[bool, bool, Optional[UpdateManifest], Optional[str]]:
        """
        Synchronously check for updates.
        Returns: (has_update, is_mandatory, manifest, error_msg)
        """
        active_channel = channel or self.settings.get_preferred_channel()
        manifest, err = fetch_manifest_from_sources(self.manifest_urls, timeout=5)
        if not manifest:
            return False, False, None, err

        self.settings.record_check_time()

        has_update, is_mandatory, reason = evaluate_update(
            manifest=manifest,
            current_version_str=self.current_version,
            channel=active_channel,
            is_manual_check=is_manual,
            settings=self.settings
        )

        return has_update, is_mandatory, manifest, reason

    def check_async(
        self,
        is_manual: bool,
        on_result: Callable[[bool, bool, Optional[UpdateManifest], Optional[str]], None]
    ):
        """
        Execute check in a background thread to prevent blocking gameplay.
        """
        with self._lock:
            if self._is_checking:
                # Avoid duplicate requests
                return
            self._is_checking = True

        def worker():
            try:
                has_up, is_mand, manifest, err = self.check_for_updates(is_manual=is_manual)
                on_result(has_up, is_mand, manifest, err)
            except Exception as e:
                on_result(False, False, None, str(e))
            finally:
                with self._lock:
                    self._is_checking = False

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def check_on_foreground(
        self,
        on_result: Callable[[bool, bool, Optional[UpdateManifest], Optional[str]], None]
    ):
        """
        Triggered when game window returns to foreground.
        Respects cooldown to prevent excessive requests.
        """
        if not self.settings.can_auto_check(self.cooldown_seconds):
            return
        self.check_async(is_manual=False, on_result=on_result)

    def dismiss_update(self, version: str):
        """Persist dismissal of an optional update."""
        self.settings.dismiss_version(version)

    def download_update(
        self,
        manifest: UpdateManifest,
        destination_path: Optional[str] = None,
        on_progress: Optional[Callable[[int, int, float], None]] = None,
        cancel_token: Optional[DownloadCancellationToken] = None,
        chunk_size: int = 65536,
        timeout: int = 15
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Download release archive in chunks, tracking progress and verifying SHA-256.
        Returns: (success, file_path, error_message)
        """
        download_url = manifest.download_url or manifest.release_page_url
        if not download_url:
            return False, None, "No download URL available in manifest."

        if destination_path is None:
            temp_dir = tempfile.gettempdir()
            filename = manifest.file_name or f"XO_Game-{manifest.tag_name}.zip"
            destination_path = os.path.join(temp_dir, filename)

        headers = {
            "User-Agent": "XO-Game-UpdateChecker/5.0",
            "Accept": "*/*"
        }
        req = urllib.request.Request(download_url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                total_bytes = 0
                content_length = resp.headers.get("Content-Length")
                if content_length and content_length.isdigit():
                    total_bytes = int(content_length)

                bytes_received = 0
                with open(destination_path, "wb") as out_file:
                    while True:
                        if cancel_token and cancel_token.is_cancelled:
                            out_file.close()
                            if os.path.exists(destination_path):
                                try:
                                    os.remove(destination_path)
                                except Exception:
                                    pass
                            return False, None, "Download cancelled by user."

                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break

                        out_file.write(chunk)
                        bytes_received += len(chunk)

                        pct = (bytes_received / total_bytes * 100.0) if total_bytes > 0 else 0.0
                        if on_progress:
                            on_progress(bytes_received, total_bytes, pct)

            # Verify integrity
            if manifest.sha256:
                if not verify_file_sha256(destination_path, manifest.sha256):
                    if os.path.exists(destination_path):
                        try:
                            os.remove(destination_path)
                        except Exception:
                            pass
                    return False, None, "Checksum verification failed: file does not match expected SHA-256."

            return True, destination_path, None

        except urllib.error.URLError as e:
            if destination_path and os.path.exists(destination_path):
                try:
                    os.remove(destination_path)
                except Exception:
                    pass
            return False, None, f"Network error during download: {e.reason if hasattr(e, 'reason') else e}"
        except Exception as e:
            if destination_path and os.path.exists(destination_path):
                try:
                    os.remove(destination_path)
                except Exception:
                    pass
            return False, None, f"Download error: {str(e)}"

    def download_update_async(
        self,
        manifest: UpdateManifest,
        on_progress: Optional[Callable[[int, int, float], None]] = None,
        on_complete: Optional[Callable[[bool, Optional[str], Optional[str]], None]] = None,
        cancel_token: Optional[DownloadCancellationToken] = None
    ) -> threading.Thread:
        """Execute download in a background daemon thread."""
        def worker():
            success, filepath, error = self.download_update(
                manifest=manifest,
                on_progress=on_progress,
                cancel_token=cancel_token
            )
            if on_complete:
                on_complete(success, filepath, error)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread


# =============================================================================
# IN-PLACE PATCHER & EXEC REPLACEMENT
# =============================================================================

def stage_executable_from_zip(zip_path: str, destination_dir: Optional[str] = None) -> str:
    """
    Extract XO_Game.exe from zip into a staging directory.
    Returns absolute path to staged executable.
    """
    if not os.path.exists(zip_path):
        raise FileNotFoundError(f"Update archive not found: {zip_path}")

    if destination_dir is None:
        stage_dir = tempfile.mkdtemp(prefix="xo_update_stage_")
    else:
        stage_dir = destination_dir
        os.makedirs(stage_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        exe_member = None
        for name in zf.namelist():
            base = os.path.basename(name).lower()
            if base in ("tik tak tok.exe", "tik_tak_tok.exe", "xo_game.exe", "xo game.exe"):
                exe_member = name
                break

        if not exe_member:
            raise FileNotFoundError("Executable was not found inside the update package.")

        extracted_path = zf.extract(exe_member, stage_dir)
        return os.path.abspath(extracted_path)


def generate_updater_batch_script(pid: int, staged_exe: str, target_exe: str) -> str:
    """
    Generate a Windows batch updater script that waits for process PID to exit,
    terminates lingering game processes, replaces the target executable with the
    staged binary, cleans up legacy executables, relaunches the game, and self-destructs.
    """
    staged_dir = os.path.dirname(staged_exe)
    target_dir = os.path.dirname(target_exe)
    legacy_exe = os.path.join(target_dir, "XO Game.exe")
    legacy_exe_alt = os.path.join(target_dir, "XO_Game.exe")

    batch_content = f"""@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: Wait for application process {pid} to terminate
:wait_loop
tasklist /fi "PID eq {pid}" 2>nul | find "{pid}" >nul
if !ERRORLEVEL! equ 0 (
    timeout /t 1 /nobreak >nul
    goto wait_loop
)

:: Terminate any lingering legacy or current game processes
taskkill /f /im "XO Game.exe" >nul 2>&1
taskkill /f /im "XO_Game.exe" >nul 2>&1
taskkill /f /im "Tik Tak Tok.exe" >nul 2>&1

:: Brief pause to ensure OS releases file locks
timeout /t 1 /nobreak >nul

:: Replace the target executable with the staged version
copy /y "{staged_exe}" "{target_exe}" >nul
if !ERRORLEVEL! neq 0 (
    move /y "{staged_exe}" "{target_exe}" >nul
)

:: Clean up legacy executable if upgrading from older version
if exist "{legacy_exe}" if /i "{legacy_exe}" neq "{target_exe}" del /f /q "{legacy_exe}" >nul 2>&1
if exist "{legacy_exe_alt}" if /i "{legacy_exe_alt}" neq "{target_exe}" del /f /q "{legacy_exe_alt}" >nul 2>&1

:: Clean up staging directory
rmdir /s /q "{staged_dir}" 2>nul

:: Relaunch the updated application
start "" "{target_exe}"

:: Self-destruct batch script
del "%~f0" & exit
"""
    return batch_content


def apply_in_place_update(zip_path: str, root_window=None) -> bool:
    """
    Safely apply an update using the external batch patcher.
    In dev mode (not sys.frozen), opens browser download page as a fallback.
    """
    if not getattr(sys, 'frozen', False):
        webbrowser.open("https://github.com/Mahfoud-Sa/tik-tak-to/releases")
        return False

    try:
        target_exe = os.path.abspath(sys.executable)
        staged_exe = stage_executable_from_zip(zip_path)
        pid = os.getpid()

        script_content = generate_updater_batch_script(
            pid=pid,
            staged_exe=staged_exe,
            target_exe=target_exe
        )

        temp_dir = tempfile.gettempdir()
        batch_path = os.path.join(temp_dir, f"xo_updater_{pid}.bat")
        with open(batch_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        creation_flags = 0
        if sys.platform == "win32":
            creation_flags = subprocess.CREATE_NEW_CONSOLE

        subprocess.Popen(
            ["cmd.exe", "/c", batch_path],
            creationflags=creation_flags,
            close_fds=True
        )

        if root_window:
            try:
                root_window.destroy()
            except Exception:
                pass

        sys.exit(0)
        return True

    except Exception:
        return False


# Legacy bridge
AsyncUpdateChecker = UpdateService
