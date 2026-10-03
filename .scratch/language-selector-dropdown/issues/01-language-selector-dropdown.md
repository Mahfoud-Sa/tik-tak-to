# 01: Language Selector Dropdown & Runtime Locale Switching

**What to build:**
Replace the main menu language toggle button with a read-only `ttk.Combobox` Language Selector displaying native autonyms ("العربية" and "English"). Selecting a language triggers an immediate switch, layout directionality update, and preference persistence.

**Blocked by:** None (can start immediately)

**Status:** completed

- [x] Remove `self.lang_button` from `self.button_frame` in `game/main.py`.
- [x] Add `self.lang_dropdown = ttk.Combobox(...)` displaying native names `"العربية"` and `"English"` with read-only state.
- [x] Bind `<<ComboboxSelected>>` to change language (`i18n.set_language(...)`) and re-render UI direction (`_update_ui_language()`).
- [x] Update `tests/test_i18n.py` to verify combobox selection, active state synchronization, and preference persistence.

