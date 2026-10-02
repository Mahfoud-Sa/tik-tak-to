# 01: Desktop Brand Localization & Live Language Switching

**What to build:**
The desktop Tkinter game displays "Tik Tak Tok" in English and "لعبة XO" in Arabic across the main window title, header label, About dialog, Help menu, and update prompts. Toggling the language switch button dynamically updates all displayed titles and labels immediately.

**Blocked by:**
None (can start immediately)

**Status:**
completed

- [x] `i18n.t("WINDOW_TITLE")` returns `"Tik Tak Tok"` for `'en'` and `"لعبة XO"` for `'ar'`.
- [x] About dialog displays "About Tik Tak Tok" (English) and "حول لعبة XO" (Arabic).
- [x] Toggling between English and Arabic updates the live Tkinter window title and header label without restart.
- [x] Automated tests verify dictionary lookups, live UI update methods, and Arabic/English string accuracy.
