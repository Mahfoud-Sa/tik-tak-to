# 3. Project Rebranding to Tik Tak Tok (لعبة XO)

Date: 2026-10-02

## Status
Accepted

## Context
The project was originally developed under the name "XO Game" (in Arabic: "لعبة إكس أو"). To improve brand distinction, playfulness, and phonetic appeal across both Arabic and English gaming audiences, the project is undergoing a comprehensive brand update.

## Decision
We decided to:
1. Adopt **"Tik Tak Tok"** as the canonical English brand name and **"لعبة XO"** as the canonical Arabic brand name across all user-facing desktop UI and web surfaces.
2. Rename the compiled standalone Windows executable from `XO Game.exe` to `Tik Tak Tok.exe`.
3. Update the in-place batch patcher (`batch_patcher.bat`) to support seamless migration: it checks and terminates both `XO Game.exe` and `Tik Tak Tok.exe`, replaces executable files, cleans up legacy `XO Game.exe` binaries in the install directory, and launches `Tik Tak Tok.exe`.
4. Migrate the persistent user settings file to `~/.tik_tak_tok_settings.json`, with a transparent fallback to read existing user preferences from `~/.xo_game_settings.json`.
5. Retain the GitHub repository URL at `https://github.com/Mahfoud-Sa/tik-tak-to` to preserve existing clone URLs, deployment remotes, and continuous integration workflows without friction.

## Consequences
- Clean, consistent identity across the desktop game, web app, version catalogs, and release notifications.
- Existing players on older versions can update via the in-app updater without encountering broken executable paths or orphan binaries.
