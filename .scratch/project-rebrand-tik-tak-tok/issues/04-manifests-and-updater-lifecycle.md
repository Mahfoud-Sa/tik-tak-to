# 04: Release Manifests & Update Lifecycle Integration

**What to build:**
Update manifests default to `"name": "Tik Tak Tok"` and `"file_name": "Tik_Tak_Tok-windows-x64.zip"`. When update checks succeed or prompt the user, headings announce "Tik Tak Tok" / "لعبة XO". Historical entries in `releases.json` remain preserved.

**Blocked by:**
03: In-App Patcher & Executable Dual-Process Migration

**Status:**
completed

- [x] `version.json` has `"name": "Tik Tak Tok"` and `"file_name": "Tik_Tak_Tok-windows-x64.zip"`.
- [x] `UpdateManifest` ingestion defaults fallback name to `"Tik Tak Tok"`.
- [x] Historical release items in `releases.json` retain historical titles for audit fidelity.
- [x] Automated tests verify manifest deserialization and update notification UI strings.
