# 02: Menu Bar Streamlining & Gameplay Lifecycle Polish

**What to build:**
Hide the language dropdown during active gameplay and multiplayer screens, restoring it upon returning to the main menu. Remove redundant language toggle commands from the Help menu bar.

**Blocked by:** 01: Language Selector Dropdown & Runtime Locale Switching

**Status:** completed

- [x] Hide `self.lang_dropdown` during active gameplay (`_start_game`, multiplayer dialogs) and restore it on menu return (`reset_game`).
- [x] Remove `toggle_language_command` from `game/views/widgets/help_menu.py` and `_setup_help_menu()`.
- [x] Update `tests/test_i18n.py` and `tests/test_layout_directionality.py` to verify lifecycle visibility and clean Help menu bar.

