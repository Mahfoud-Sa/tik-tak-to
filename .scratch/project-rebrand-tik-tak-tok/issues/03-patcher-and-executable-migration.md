# 03: In-App Patcher & Executable Dual-Process Migration

**What to build:**
The standalone Windows binary targets `Tik Tak Tok.exe`. The automated in-place patcher terminates both `XO Game.exe` and `Tik Tak Tok.exe`, extracts the new binary from the update zip archive, cleans up any old `XO Game.exe` from the target installation folder, and relaunches `Tik Tak Tok.exe`.

**Blocked by:**
01: Desktop Brand Localization & Live Language Switching

**Status:**
completed

- [x] In-place batch patcher script terminates both `XO Game.exe` and `Tik Tak Tok.exe`.
- [x] Generated batch script removes legacy `XO Game.exe` / `XO_Game.exe` from the target directory if upgrading.
- [x] Binary staging logic recognizes update archives containing `Tik Tak Tok.exe`, `tik_tak_tok.exe`, or `XO_Game.exe`.
- [x] PyInstaller configuration / build script packages standalone executable as `Tik Tak Tok.exe`.
- [x] Automated tests for batch patcher and staging pass.
