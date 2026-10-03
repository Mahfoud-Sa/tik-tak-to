## Problem Statement

Players currently change the display language in the main desktop window via a push button that alternates between Arabic and English (`LANG_SWITCH_BUTTON_TEXT`). A toggle button has several usability issues:
1. It does not explicitly indicate all available languages in the system, forcing users to click it to discover what other options exist.
2. It conflicts with accessibility and internationalization best practices, where language selection should be an explicit choice between native language autonyms ("العربية" and "English").
3. A duplicate "Change Language" toggle item in the top desktop Help menu creates redundant, fragmented controls across two different interaction paradigms.
4. Players need a modern, clean dropdown selector in the primary menu that immediately switches and persists the active language and mirrors the layout accordingly, while automatically tucking away during active gameplay to avoid cluttering the board.

## Solution

Replace the main menu language toggle button with a native, read-only dropdown control (`ttk.Combobox`) and streamline the application navigation:
1. **In-Window Language Selector**: Replace `self.lang_button` in `self.button_frame` with `self.lang_dropdown` displaying native language names (`"العربية"` and `"English"`).
2. **Immediate Selection Event**: Selecting a language from the dropdown immediately switches the application locale (`i18n.set_language(...)`), flips the RTL/LTR UI layout direction, and saves the choice to `~/.tik_tak_tok_settings.json`.
3. **Lifecycle Management**: The dropdown automatically hides (`pack_forget`) when entering local or multiplayer gameplay, and restores (`pack`) upon match completion or returning to the main menu.
4. **Menu Bar Streamlining**: Remove the duplicate language toggle action from the Help menu (`create_help_menu`), making the in-window dropdown the singular source of truth for language switching.

## User Stories

1. As a player launching the game, I want to see a language dropdown in the main menu clearly displaying the current language in its native script, so that I immediately understand what language is active.
2. As an English-speaking player opening the game when it defaults to Arabic, I want to see "English" listed in the dropdown, so that I can switch the language without needing to read Arabic.
3. As an Arabic-speaking player opening the game when it is set to English, I want to see "العربية" listed in the dropdown, so that I can easily identify my native language.
4. As a player selecting a language from the dropdown, I want the UI text and layout directionality (RTL/LTR) to update immediately without requiring me to click a separate "Apply" or "Save" button.
5. As a player selecting a language, I want my choice saved to my user settings file, so that the game opens in my preferred language the next time I play.
6. As a player starting a game, I want the language dropdown to disappear while the match is underway, so that the board interface remains clean and uncluttered.
7. As a player finishing or resetting a match and returning to the menu, I want the language dropdown to reappear in its expected place, so that I can adjust settings between games.
8. As a player opening multiplayer dialogs, I want the language dropdown to be hidden, so that it does not overlap or distract from multiplayer setup.
9. As a player navigating the Help menu bar, I want a concise menu without redundant language toggles, so that the Help menu remains focused on theme customization, update checks, and game information.
10. As a player using keyboard or mouse navigation on the dropdown, I want the combobox to be read-only, so that I cannot inadvertently enter invalid language strings.

## Implementation Decisions

- **Domain Glossary Alignment**: Adopts the canonical term **Language Selector (محدد اللغة)** recorded in `GLOSSARY.md`, superseding the deprecated "language toggle button".
- **Widget Selection & Styling**: The language selector is implemented as a read-only `ttk.Combobox` placed directly in the main menu button frame beneath the Multiplayer button, using centered alignment and standard menu padding.
- **Autonym Presentation**: Options are strictly native language names: `"العربية"` and `"English"`, mapped internally to language codes `"ar"` and `"en"`.
- **Immediate Runtime Reaction**: The dropdown binds to `<<ComboboxSelected>>` to execute `i18n.set_language(...)` and re-render the layout via `_update_ui_language()`.
- **Menu Bar Cleanup**: `create_help_menu` in `views/widgets/help_menu.py` removes `toggle_language_command` and `LANGUAGE_MENU_TEXT` parameters to eliminate redundant actions.
- **Menu Lifecycle Cohesion**: The dropdown joins the existing menu button pack/unpack flow during `_start_game`, `reset_game`, and multiplayer dialog transitions.

## Testing Decisions

- **What makes a good test**: Tests must verify externally observable behavior and state contracts:
  1. Selecting an option from `lang_dropdown` updates `i18n.get_language()` and triggers UI language refresh.
  2. The combobox displays the correct active native language name when the locale changes.
  3. The combobox is packed during menu state and unpacked during active gameplay.
  4. The Help menu no longer provisions a language toggle action.
- **Modules to be tested**:
  - `tests/test_i18n.py`: Update `TestAppLanguageSwitch` to test combobox selection event handling and active value synchronization.
  - `tests/test_layout_directionality.py`: Verify that switching languages through the application updates the UI layout mirroring.
- **Prior Art**: Follows the existing test structure in `tests/test_i18n.py` (`TestAppLanguageSwitch`) using `unittest.TestCase` and Tkinter mock harnesses.

## Out of Scope

- Adding new languages beyond Arabic (`ar`) and English (`en`).
- Allowing runtime language switching while a live network multiplayer socket match is in progress.
- Changing font family or font size configuration inside the dropdown listbox popup.

## Further Notes

- Maintains complete backwards compatibility with user settings in `~/.tik_tak_tok_settings.json` and legacy `~/.xo_game_settings.json`.
- Respects ADR 0002 bidirectional layout strategy for RTL/LTR mirroring.
