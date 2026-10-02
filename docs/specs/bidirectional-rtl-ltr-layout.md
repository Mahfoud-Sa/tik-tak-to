## Problem Statement

When players switch the game language to Arabic, the user interface remains structured in a rigid Left-to-Right (LTR) layout. In desktop applications supporting right-to-left languages, reading and spatial expectations require that primary flow elements, scoreboards, and dialog action buttons start from the right. Specifically:
1. In Arabic mode, the starting player (Player O) was displayed on the visual left and the secondary player (Player X) on the right, contradicting natural RTL visual hierarchy.
2. Dialog windows (such as Multiplayer connection dialogs and Update notification dialogs) laid out actions in LTR order, placing primary confirmation buttons on the left and dismiss buttons on the right.
3. Toggling language during runtime triggered an unhandled exception (`AttributeError: 'GameState' object has no attribute 'game_active'`), crashing language switching callbacks.
4. There were no centralized layout primitives to dynamically determine directional alignment (`start`, `end`, `grid_col`) across views, leading to ad-hoc or missing RTL adaptation.

## Solution

A comprehensive Bidirectional (RTL/LTR) Layout Presentation Architecture and runtime reflow engine:
1. **Centralized Directional Primitives in `I18n`**: Expose first-class layout direction helpers (`is_rtl`, `direction`, `side_start()`, `side_end()`, `anchor_start()`, `anchor_end()`, and `grid_col()`).
2. **Dynamic In-Place Scoreboard & Indicator Mirroring**: When the language is set to Arabic (`ar`), Player O's scoreboard and turn selector position in visual column 2 (right), and Player X in visual column 0 (left). In English (`en`), Player O is in column 0 (left) and Player X in column 2 (right). Connection indicators mirror between `ne` (RTL) and `nw` (LTR).
3. **Fixed 3x3 Game Board Grid**: The physical 3x3 play canvas coordinate system remains invariant to preserve physical intuition and prevent desynchronization in network multiplayer games.
4. **Natural Dialog Reading Flow**: Dialog action bars position primary buttons on the reading start side (`right` in RTL, `left` in LTR) and secondary buttons on the opposite side. Numeric inputs (such as IPv4 address fields) retain LTR entry (`justify='left'`) to prevent awkward cursor behavior.
5. **Runtime Observer Subscription**: The main application and game view subscribe to language change events via `i18n.subscribe()`, reflowing layouts instantly without requiring game restarts or losing active score state.
6. **State Attribute Alignment**: Fix the `game_active` attribute reference to `is_game_active` in the main application callback.

## User Stories

1. As an Arabic-speaking player, I want the game UI to flow from right to left when Arabic is selected, so that the game feels natural and native to my language.
2. As an English-speaking player, I want the game UI to flow from left to right when English is selected, so that standard LTR conventions are preserved.
3. As a player, I want Player O (the first player) to appear on the right side of the scoreboard in Arabic mode and on the left side in English mode, so that player positions follow the natural reading direction.
4. As a player, I want Player X (the second player) to appear on the left side of the scoreboard in Arabic mode and on the right side in English mode, so that scoreboard hierarchy is visually consistent.
5. As a player, I want the current player turn indicator (radio button) to align directly underneath the respective player's score column in both RTL and LTR modes, so that I always know whose turn it is.
6. As a player, I want the 3x3 game board grid coordinates to remain in standard order in both Arabic and English, so that clicking cells feels intuitive and matches standard Tic-Tac-Toe spatial layout.
7. As a multiplayer player, I want the board coordinate system to remain identical across languages, so that moves sent over the network synchronize seamlessly between players using different languages.
8. As a player, I want the connection status indicator to appear in the top-start corner of the board (`ne` in Arabic, `nw` in English), so that status alerts match the reading flow.
9. As a player, I want to toggle between Arabic and English mid-game without crashing or encountering Tkinter errors, so that language switching is completely safe and reliable.
10. As a player, I want toggling the language during an active game to update the layout and text immediately in-place, so that I do not lose current scores or game progress.
11. As a player opening the Multiplayer Host dialog in Arabic, I want action buttons to be arranged in natural reading order, so that the primary Refresh action appears on the right and Cancel appears on the left.
12. As a player opening the Multiplayer Join dialog in Arabic, I want the Connect button on the right and Cancel on the left, so that primary confirmation actions lead from the reading side.
13. As a player entering an IP address in the Join dialog in Arabic, I want the IP address input field to remain left-to-right aligned (`justify='left'`), so that typing numbers and periods is natural and uncluttered.
14. As a player viewing an Update notification dialog in Arabic, I want the Download Update button to appear on the reading start side and the Later button on the opposite side, so that primary call-to-actions follow RTL conventions.
15. As a player viewing the update release notes in Arabic, I want the section header to align to the right (`anchor='e'`), so that headings match Arabic text alignment.
16. As a player, I want my language preference and layout direction to persist across application restarts, so that I do not have to reconfigure my language every time I play.
17. As a developer, I want layout directionality helpers centralized in `I18n`, so that views do not require hardcoded language checks throughout the codebase.

## Implementation Decisions

- **Centralized Direction Helper Methods**: Added `is_rtl`, `direction`, `side_start()`, `side_end()`, `anchor_start()`, `anchor_end()`, and `grid_col(col, total_cols=3)` to the `I18n` class in the localization module.
- **Scoreboard Column Mapping**: The game view uses `i18n.grid_col(0, 3)` for Player O and `i18n.grid_col(2, 3)` for Player X during initial placement and reconfigures them during dynamic layout updates.
- **Dynamic Re-layout Method**: Implemented `update_layout_direction()` on the game view to re-grid active labels and radio buttons upon language notification.
- **State Property Alignment**: Replaced all references to `self.state.game_active` in the main application with `self.state.is_game_active`, conforming to the GameState domain model.
- **Dialog Layout Packing**: Updated dialog widget construction to pack buttons using `i18n.side_start()` and `i18n.side_end()`.
- **Technical Input Field Direction**: Maintained `justify='left'` on the IP address entry field in the Join Game dialog, while aligning its label according to `i18n.side_start()`.
- **Canvas Invariance**: Left canvas drawing methods and 3x3 line geometry untouched, adhering to the decision recorded in ADR 0002.

## Testing Decisions

- **What makes a good test**: Tests should verify observable UI layout configurations and interface contracts (e.g. column placement indices, pack side parameters, and callback invocations) rather than asserting on private internal geometry or OS window frames.
- **Modules to be tested**:
  - The `I18n` directionality interface: verifying `is_rtl`, `direction`, `side_start`, `side_end`, `anchor_start`, `anchor_end`, and `grid_col` under both `ar` and `en` settings.
  - The `GameView` layout placement: verifying that Player O and Player X grid columns mirror correctly upon initialization and update dynamically upon language toggle.
  - The `TicTacToeApp` indicator placement and language toggle callback: verifying that the connection indicator adjusts to the correct column and sticky corner without raising attribute errors.
- **Prior Art**: Existing tests in `tests/test_i18n.py` test language switching and persistence. The new `tests/test_layout_directionality.py` follows this mock-based pattern for Tkinter component testing.

## Out of Scope

- Horizontal canvas flipping or mirroring of 3x3 board cells.
- External bidirectional text shaping libraries (e.g., `arabic_reshaper` or `python-bidi`); modern Windows DirectWrite handles basic character rendering.
- Complex multi-column grid reordering beyond the 3-column layout of the game board.

## Further Notes

- Architectural context and rationale are recorded in ADR 0002 (Bidirectional RTL and LTR Layout Strategy).
- The term "Layout Directionality (RTL / LTR)" is defined in the root domain glossary.
