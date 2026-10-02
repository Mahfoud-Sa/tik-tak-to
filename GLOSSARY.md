# XO Game

A desktop Tic-Tac-Toe application supporting local pass-and-play and LAN/socket multiplayer, with automated version checking and lifecycle management.

## Language

**Update Manifest**:
A JSON payload hosted on public endpoints defining the latest release metadata, version, platform assets, and mandatory status.
_Avoid_: Version file, release config, update descriptor

**Mandatory Update**:
A required release that disables network multiplayer until applied, while allowing local offline play to continue.
_Avoid_: Force update, breaking update, hard lock

**In-App Patcher**:
An automated download and external script handoff mechanism that downloads update archives and replaces executable files after process shutdown.
_Avoid_: Auto-installer, hot patcher, live reload

**Dismissed Version**:
A version number explicitly skipped by the player using the 'Later' action, suppressing future automatic startup prompts for that specific version.
_Avoid_: Ignored update, muted release

**Layout Directionality (RTL / LTR)**:
The visual presentation flow where layout hierarchy, scoreboard column positioning, and dialog widget packing mirror between Right-to-Left (for Arabic) and Left-to-Right (for English), while keeping the spatial 3x3 game board coordinates fixed.
_Avoid_: Canvas inversion, board coordinate mirroring, text-only translation

