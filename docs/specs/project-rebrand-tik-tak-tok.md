## Problem Statement

The application and repository historically operated under the name "XO Game" (in Arabic: "لعبة إكس أو"). While descriptive, this title was generic, lacked distinctive brand identity across gaming and open-source platforms, and created phonetic divergence between international and Arabic-speaking players. Furthermore, maintaining inconsistent naming across user interfaces, standalone executable binaries (`XO Game.exe`), settings files (`~/.xo_game_settings.json`), web documentation, and release manifests causes brand confusion and user disorientation. Updating the brand name requires a coordinated, backwards-compatible transition so existing players updating via the in-app patcher can seamlessly migrate without file conflicts, broken shortcuts, or lost language preferences.

## Solution

A comprehensive, ecosystem-wide rebrand to **"Tik Tak Tok"** in English and **"لعبة XO"** in Arabic:
1. **Desktop Interface & Localization**: The main application window, header labels, About dialogues, Help menus, and update notices display "Tik Tak Tok" when running in English and "لعبة XO" when running in Arabic.
2. **Settings Migration with Legacy Fallback**: User preferences migrate to `~/.tik_tak_tok_settings.json`. When launching, the engine checks for existing settings in `~/.xo_game_settings.json`, transparently inherits user configurations, and writes subsequent changes to the new filename.
3. **Executable Rebranding & Patcher Migration**: The standalone Windows binary is renamed to `Tik Tak Tok.exe`. The automated in-place patcher terminates both `XO Game.exe` and `Tik Tak Tok.exe` during an upgrade, extracts the new binary, deletes the legacy binary from the installation folder, and relaunches `Tik Tak Tok.exe`.
4. **Release Manifest Alignment**: Current and future update manifests reflect `"name": "Tik Tak Tok"`, while preserving historical release titles in `releases.json` for audit fidelity.
5. **Web Presentation & Documentation**: The web landing page, version catalog, emblems, meta tags, and interactive player arena adopt "Tik Tak Tok" and "لعبة XO", while keeping the upstream GitHub repository URL (`https://github.com/Mahfoud-Sa/tik-tak-to`) stable.

## User Stories

1. As a desktop player launching the game in English, I want to see "Tik Tak Tok" in the window title and main header, so that I recognize the official brand of the game.
2. As a desktop player launching the game in Arabic, I want to see "لعبة XO" in the window title and main header, so that the name is familiar and culturally natural.
3. As a desktop player opening the About dialogue in English, I want the title to read "About Tik Tak Tok" and describe the application as "Simple Tik Tak Tok Game", so that the branding is consistent.
4. As a desktop player opening the About dialogue in Arabic, I want the title to read "حول لعبة XO" and describe the application as "لعبة XO بسيطة", so that the text matches standard Arabic typography.
5. As a player with pre-existing settings stored in `~/.xo_game_settings.json`, I want the game to automatically read my saved language preference upon startup, so that my choices are preserved without resetting to default.
6. As a player modifying my settings, I want new preferences saved to `~/.tik_tak_tok_settings.json`, so that settings files reflect the new project name.
7. As a player downloading an update through the in-app patcher, I want the patcher to replace the old `XO Game.exe` executable with `Tik Tak Tok.exe`, so that my game files are clean and up to date.
8. As a player updating from an older version, I want the patcher to safely terminate any running `XO Game.exe` or `Tik Tak Tok.exe` processes before copying files, so that Windows file-locking errors do not cause the update to fail.
9. As a player updating from an older version, I want the patcher to delete the legacy `XO Game.exe` file from my installation folder, so that I am not left with two confusing executables side by side.
10. As a player checking for updates, I want the update dialog heading to announce "A new version of Tik Tak Tok is available" (in Arabic: "إصدار جديد متوفر من لعبة XO"), so that update alerts match the app identity.
11. As a player inspecting the Windows executable properties, I want the Product Name, Internal Name, and File Description to read "Tik Tak Tok", so that the Windows Task Manager and Details tab display the proper product name.
12. As a web visitor viewing the landing page in English, I want the site title, navigation brand, hero header, and copyright to display "Tik Tak Tok", so that the web presence matches the desktop game.
13. As a web visitor viewing the landing page in Arabic, I want the site title, navigation brand, hero header, and copyright to display "لعبة XO", so that the Arabic web experience is natural and cohesive.
14. As a visitor browsing the version history catalog, I want recent updates to be titled under "Tik Tak Tok" while historical records retain their original version names, so that changelog history remains honest and traceable.
15. As a developer cloning the project or checking release feeds, I want the repository URL to remain at `Mahfoud-Sa/tik-tak-to`, so that existing git remotes, deployment workflows, and GitHub Pages URLs do not break.

## Implementation Decisions

- **Domain Glossary Canonical Terms**: The project domain model canonicalizes "Tik Tak Tok (لعبة XO)" as the singular brand name and explicitly designates "XO Game", "Tic Tac Toe", and "لعبة إكس أو" as terms to avoid.
- **Dynamic i18n Lookup Strategy**: All brand-sensitive UI strings (`WINDOW_TITLE`, `ABOUT_TITLE`, `ABOUT_MESSAGE`, `UPDATE_DIALOG_HEADING`) resolve through the dynamic localization dictionary, supporting runtime Arabic/English switching.
- **Bi-Directional Fallback Settings Loader**: The `I18n` class initializes with `~/.tik_tak_tok_settings.json` as its primary target and `~/.xo_game_settings.json` as a secondary fallback. If the primary file is absent but the fallback file is present, the fallback data is loaded and immediately copied to the primary path.
- **Multi-Process Patcher Compatibility**: The batch script generation routine is enhanced to issue taskkill commands against both `XO Game.exe` and `Tik Tak Tok.exe`, extract either binary name from the update package, delete any stale alternate binary, and launch the newly installed `Tik Tak Tok.exe`.
- **Zip Staging Matcher**: The updater's binary staging function matches any archive member whose base filename is either `tik tak tok.exe`, `tik_tak_tok.exe`, `xo game.exe`, or `xo_game.exe`, ensuring forward and backward update zip compatibility.
- **Release Manifest Schema Stability**: The `version.json` payload defaults the `"name"` property to `"Tik Tak Tok"` and default asset zip filename to `"Tik_Tak_Tok-windows-x64.zip"` without breaking the schema contract.

## Testing Decisions

- **What makes a good test**: Tests must verify externally observable behavior and contracts (e.g. string values in language dictionaries, fallback persistence migration, generated batch script commands, archive extraction) rather than internal Tkinter geometry or implementation details.
- **Modules to be tested**:
  - `tests/test_i18n.py`: Verify that "Tik Tak Tok" is returned for English and "لعبة XO" for Arabic across all navigation and about keys; verify that initializing `I18n` with a legacy settings file migrates user settings to the new path.
  - `tests/test_batch_patcher.py`: Verify that update zip extraction recognizes `Tik Tak Tok.exe`, and that the generated batch script includes wait loops, dual-process termination, legacy executable cleanup, and the new launch command.
  - `tests/test_manifest.py` & `tests/test_updater.py`: Verify that default manifest creation and fallback parsing yield `"Tik Tak Tok"` as the application name.
- **Prior Art**: Follows existing unit tests in `tests/test_i18n.py`, `tests/test_batch_patcher.py`, and `tests/test_manifest.py`.

## Out of Scope

- Renaming the remote GitHub repository URL (`Mahfoud-Sa/tik-tak-to`) on GitHub.com.
- Retroactively altering historical Git commit messages or tags prior to the rebranding commit.
- Changing core game board mechanics or the 3x3 grid logic.

## Further Notes

- Architectural context and trade-offs are documented in ADR 0003 (`docs/adr/0003-rebrand-tik-tak-tok.md`).
- Canonical brand terminology is recorded in the root `GLOSSARY.md`.
