# 02: User Settings Migration with Legacy Fallback

**What to build:**
The game saves player preferences in `~/.tik_tak_tok_settings.json`. If a player has existing settings from an older installation in `~/.xo_game_settings.json`, the game seamlessly inherits those settings on startup and writes subsequent updates to the new file.

**Blocked by:**
01: Desktop Brand Localization & Live Language Switching

**Status:**
completed

- [x] Primary settings file is `~/.tik_tak_tok_settings.json`.
- [x] If the primary settings file does not exist, the engine checks for `~/.xo_game_settings.json`.
- [x] If the legacy file exists, saved language is loaded and migrated to the new file path.
- [x] Automated unit tests verify fallback reading, preference migration, and persistence.
