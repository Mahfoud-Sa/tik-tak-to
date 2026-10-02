# 0002. Bidirectional RTL and LTR Layout Strategy

## Context
The XO Game provides bilingual support in Arabic (`ar`) and English (`en`). Desktop applications supporting right-to-left (RTL) languages require a natural reading flow for UI widgets, player scoreboard indicators, and dialog actions, while avoiding disorientation or desynchronization in board game logic.

## Decision
1. **Directional UI Flow**:
   - The application dynamically mirrors UI widgets between RTL (`ar`) and LTR (`en`).
   - In RTL (`ar`), the starting player (Player O) scoreboard and turn selector are placed in the right column (`col 2`), and Player X in the left column (`col 0`). In LTR (`en`), Player O is in `col 0` and Player X in `col 2`.
   - Dialog primary action buttons are placed on the reading start side (`right` in RTL, `left` in LTR), and dismissal/secondary buttons on the opposite side.
   - Text labels anchor to the start side (`e` in RTL, `w` in LTR).
2. **Fixed 3x3 Board Grid Coordinates**:
   - The spatial coordinates of the 3x3 game board canvas remain identical across all languages. Board cell (row, col) coordinates are not inverted to preserve physical intuition and avoid protocol mismatch in LAN multiplayer games.
3. **Preserve LTR for Technical Form Fields**:
   - Technical inputs (such as IPv4 addresses in the Join Game dialog) remain formatted and aligned left-to-right (`justify='left'`) to prevent awkward caret navigation.
4. **Centralized Direction Helpers in `I18n`**:
   - `I18n` provides standard layout helpers (`is_rtl`, `side_start()`, `side_end()`, `anchor_start()`, `anchor_end()`, `grid_col()`) so that views do not contain hardcoded language checks.

## Consequences
- Clean, consistent visual hierarchy for both Arabic and English players.
- Smooth runtime language switching without restarting the game or losing ongoing scores.
- Preserves multiplayer compatibility and identical board move event processing.
