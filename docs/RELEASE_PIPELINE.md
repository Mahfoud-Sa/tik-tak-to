# XO Game - Release and In-Game Update Pipeline

## 1. Architecture & Platform Overview

* **Game Engine**: Python 3 (Tkinter GUI).
* **Architecture**: Model-View-Controller (MVC) with Socket-based Multiplayer.
* **Target Release Platform**: Windows x64 Desktop Application (`XO_Game.exe` packaged with PyInstaller).
* **Version Sources**:
  * [game/config.py](file:///c:/Users/mahfoud/Documents/GitHub/XO_Game/game/config.py): `__version__ = "5.0.0"`
  * [game/version.txt](file:///c:/Users/mahfoud/Documents/GitHub/XO_Game/game/version.txt): Windows PE executable resource metadata (`FileVersion`, `ProductVersion`).
* **Hosting Setup**:
  * **Binaries & Assets**: Hosted publicly via [GitHub Releases](https://github.com/Mahfoud-Sa/tik-tak-to/releases).
  * **Static Update Manifest**: Hosted via [GitHub Pages](https://mahfoud-sa.github.io/tik-tak-to/updates/version.json) and as a direct release asset fallback (`https://github.com/Mahfoud-Sa/tik-tak-to/releases/latest/download/version.json`).

---

## 2. GitHub Actions Release Workflow (`.github/workflows/release.yml`)

The automated workflow manages the entire build, packaging, release creation, and metadata publication pipeline.

### Workflow Triggers
1. **Pushing a SemVer Tag**:
   ```bash
   git tag v5.1.0
   git push origin v5.1.0
   ```
2. **Manual Execution (`workflow_dispatch`)**:
   Navigate to **Actions** -> **Release & Update Pipeline** -> **Run workflow**:
   * `version`: e.g. `5.1.0` or `v5.1.0`
   * `prerelease`: Check if publishing as a beta or release candidate (`false` for stable)
   * `custom_notes`: Optional player-facing release highlights
   * `min_supported_version`: Optional minimum version (for mandatory updates)
   * `mandatory`: Optional boolean to mark the update as mandatory

### Pipeline Steps
1. **Validation & Version Agreement**:
   Executes `python scripts/validate_version.py --expected-version <VER>` to guarantee that the tag, `game/config.py`, and `game/version.txt` strictly agree before building.
2. **Test Suite**:
   Runs `python -m compileall game` and `python -m unittest discover tests`. Builds will fail immediately if any test fails.
3. **PyInstaller Compilation & Packaging**:
   Executes `python scripts/build_release.py` on `windows-latest`:
   * Produces standalone `XO_Game.exe`.
   * Bundles into `XO_Game-vX.Y.Z-windows-x64.zip`.
   * Computes cryptographic `SHA-256` checksums into `checksums.txt`.
4. **Changelog & Manifest Generation**:
   Generates player-facing release notes from git commits since previous release and creates `version.json` compliant with [schemas/version-manifest.schema.json](file:///c:/Users/mahfoud/Documents/GitHub/XO_Game/schemas/version-manifest.schema.json).
   Simultaneously updates the cumulative release history in `docs/updates/releases.json` compliant with [schemas/version-history.schema.json](file:///c:/Users/mahfoud/Documents/GitHub/XO_Game/schemas/version-history.schema.json).
5. **GitHub Release Publishing**:
   Uploads `XO_Game.exe`, `XO_Game-vX.Y.Z-windows-x64.zip`, `checksums.txt`, and `version.json` using GitHub CLI (`gh release create --clobber`).
6. **Public Metadata & Website History Sync**:
   * For **stable** releases: updates `docs/updates/version.json` (latest stable manifest consumed by desktop updater and website hero) AND `docs/updates/releases.json` (version history feed).
   * For **prereleases**: updates only `docs/updates/releases.json` with `channel: "prerelease"`, ensuring prereleases never displace the latest stable manifest in `version.json`.
   * Automatically commits both files back to the repository branch so GitHub Pages immediately serves the updated version history and download links.

---

## 3. Public Update Manifest & Release History Specification

### 3.1 Single Release Manifest (`docs/updates/version.json`)
* **Schema**: [schemas/version-manifest.schema.json](file:///c:/Users/mahfoud/Documents/GitHub/XO_Game/schemas/version-manifest.schema.json)
* Stores metadata for the single latest stable release. Ingested by the in-game auto-updater.

### 3.2 Historical Releases Catalog (`docs/updates/releases.json`)
* **Schema**: [schemas/version-history.schema.json](file:///c:/Users/mahfoud/Documents/GitHub/XO_Game/schemas/version-history.schema.json)
* Stores the cumulative release catalog sorted newest first. Shared by the website landing page and the dedicated `/versions` history page.
* Sample structure:
```json
{
  "$schema": "https://raw.githubusercontent.com/Mahfoud-Sa/tik-tak-to/main/schemas/version-history.schema.json",
  "schema_version": 1,
  "latest_stable": "3.0.1",
  "updated_at": "2026-10-02T08:06:41Z",
  "releases": [
    {
      "name": "XO Game v3.0.1",
      "version": "3.0.1",
      "tag_name": "v3.0.1",
      "channel": "stable",
      "published_at": "2026-10-02T08:06:41Z",
      "mandatory": false,
      "release_notes": "...",
      "release_page_url": "https://github.com/Mahfoud-Sa/tik-tak-to/releases/tag/v3.0.1",
      "platforms": {
        "windows": {
          "file_name": "XO_Game-v3.0.1-windows-x64.zip",
          "download_url": "https://github.com/Mahfoud-Sa/tik-tak-to/releases/download/v3.0.1/XO_Game-v3.0.1-windows-x64.zip",
          "sha256": "f62675d20c6b2873924be98c20d0749d1ac5aac655ebb7a0a15291234efec81a"
        }
      }
    }
  ]
}
```

### Manifest Ingestion & Failover Strategy
The in-game update engine and website query sources in priority order:
1. **GitHub Pages Endpoint**: `https://mahfoud-sa.github.io/tik-tak-to/updates/releases.json` and `version.json` (fast static CDN).
2. **GitHub Raw Repository**: `https://raw.githubusercontent.com/Mahfoud-Sa/tik-tak-to/main/docs/updates/releases.json`.
3. **Latest Release Asset**: `https://github.com/Mahfoud-Sa/tik-tak-to/releases/latest/download/version.json`.
4. **GitHub Releases API Fallback**: `https://api.github.com/repos/Mahfoud-Sa/tik-tak-to/releases/latest`.

---

## 4. In-Game Update Checking & UI

### In-Game Update Engine ([game/utils/updater.py](file:///c:/Users/mahfoud/Documents/GitHub/XO_Game/game/utils/updater.py))
* **SemVer 2.0.0 Compliance**: Compares numeric identifiers numerically (e.g. `11 > 2`), handles prereleases (`alpha`, `beta`, `rc`), and ignores build metadata.
* **Non-Blocking Background Threads**: Checks run asynchronously in a daemon thread and never interrupt gameplay or Tkinter GUI response.
* **Lifecycle & Foreground Detection**: Hooked to `<FocusIn>`. When the player returns to the game, an update check runs if the 15-minute cooldown (`cooldown_seconds = 900`) has elapsed.
* **Channel Filtering**: Stable players do not receive prereleases (`-beta`, `-rc`) unless opted in.
* **Dismissal Persistence**: When a player clicks **Later**, the dismissed version is saved in `~/.xo_game_updater.json`. Future automatic checks will not re-prompt for that version.
* **Manual Check**: Selecting **"التحقق من وجود تحديثات..."** in the Help menu bypasses cooldown and dismissal, providing direct feedback.
* **Mandatory Updates**: If `mandatory: true` or `current_version < min_supported_version`, the dialog marks the update as critical, hides the "Later" button, and requires downloading the update to proceed.

---

## 5. Security & GitHub Configuration

### Permissions
The workflow uses minimal scoped permissions in `.github/workflows/release.yml`:
```yaml
permissions:
  contents: write
  pages: write
  id-token: write
```

### GitHub Repository Settings
1. Go to **Settings** -> **Actions** -> **General** -> **Workflow permissions**.
2. Select **Read and write permissions** (allows GitHub Actions bot to create releases and push tags).
3. If using GitHub Pages for the web portal:
   * Go to **Settings** -> **Pages**.
   * Source: **Deploy from a branch** -> branch `main`, folder `/docs`.

---

## 6. How to Perform a Release

### Option A: Via Command Line (Recommended)
1. Ensure `game/config.py` and `game/version.txt` are updated:
   ```bash
   python scripts/validate_version.py --sync 5.1.0
   ```
2. Commit and push changes:
   ```bash
   git commit -am "chore(release): bump version to 5.1.0"
   git push origin main
   ```
3. Tag and push the release tag:
   ```bash
   git tag v5.1.0
   git push origin v5.1.0
   ```
4. GitHub Actions will automatically validate, test, build, create the GitHub Release, and publish the update manifest.

### Option B: Via GitHub Actions UI (`workflow_dispatch`)
1. In your GitHub repository, open the **Actions** tab.
2. Select **Release & Update Pipeline**.
3. Click **Run workflow**:
   * Set version to `5.1.0`.
   * Click **Run workflow**.

---

## 7. Rollback Procedure
If a published release has a critical bug:
1. **Suppress Updates Immediately**:
   Edit `docs/updates/version.json` on branch `main` to point back to the previous stable version (e.g. `5.0.0`), commit and push. Clients will stop seeing the broken update within minutes.
2. **Mark Broken Release as Pre-release or Delete**:
   On GitHub Releases, edit the faulty release and mark it as pre-release or delete it.

---

## 8. How to Test the Complete End-to-End Flow

1. **Verify Local Installed Version**:
   Run the game with `__version__ = "5.0.0"`:
   ```bash
   python game/main.py
   ```
2. **Simulate a Published Update**:
   Update `docs/updates/version.json` temporarily to version `"5.1.0"`.
3. **Verify Startup Notification**:
   Launch `python game/main.py`. Within 2 seconds, the update notification dialog pops up with:
   * Installed version `v5.0.0`
   * Available version `v5.1.0`
   * Release notes preview
   * "تحميل التحديث" and "لاحقاً" buttons
4. **Verify Dismissal Persistence**:
   Click **"لاحقاً"** (Later). Close and re-launch `python game/main.py`. The dialog will not appear.
5. **Verify Manual Check**:
   Click **مساعدة** -> **التحقق من وجود تحديثات...**. The dialog reappears despite the earlier dismissal.
6. **Verify Foreground Lifecycle Hook**:
   Click away from the window and return after the cooldown period to observe background check execution.
