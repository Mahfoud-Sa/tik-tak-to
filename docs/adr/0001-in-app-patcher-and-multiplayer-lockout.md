# 0001. In-App Patcher and Multiplayer Lockout for Updates

## Context
When a new version is released, players need a seamless way to upgrade without corrupting running game files or requiring complex external packaging tools. Furthermore, when updates contain breaking multiplayer protocol changes or security fixes, version discrepancies between clients could break network games.

## Decision
1. **Mandatory Update Gating**: When a mandatory update is pending and dismissed or closed by the player, offline pass-and-play continues to function normally, but online multiplayer mode is locked out until the application is updated.
2. **In-App Patcher via External Batch Runner**: The desktop application downloads the release archive directly within the game UI with a progress indicator, cryptographically validates the SHA-256 checksum against the manifest, and executes an external batch updater script that waits for `XO_Game.exe` to terminate before extracting and replacing the binary and relaunching the game.

## Consequences
- Preserves offline game availability even if update servers are unreachable or the player is offline.
- Avoids Windows file locking errors when replacing the running executable.
- Requires reliable cleanup of temporary updater scripts and download archives upon completion or failure.
