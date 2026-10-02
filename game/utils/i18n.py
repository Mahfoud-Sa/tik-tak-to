"""
Internationalization (i18n) Engine for XO Game
Provides bilingual support (Arabic and English), real-time UI translation listeners,
and persistent language selection.
"""

import json
import os
from typing import Dict, Any, Callable, List, Optional


TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Main App & Navigation
    "WINDOW_TITLE": {
        "ar": "لعبة إكس أو",
        "en": "XO Game"
    },
    "PLAY_BUTTON_TEXT": {
        "ar": "ابدأ اللعب",
        "en": "Play Game"
    },
    "EXIT_BUTTON_TEXT": {
        "ar": "خروج",
        "en": "Exit Game"
    },
    "MULTIPLAYER_BUTTON_TEXT": {
        "ar": "متعدد اللاعبين",
        "en": "Multiplayer"
    },
    "LANG_SWITCH_BUTTON_TEXT": {
        "ar": "🌐 English",
        "en": "🌐 العربية"
    },
    "CHANGE_THEME_TEXT": {
        "ar": "تغيير السمة",
        "en": "Change Theme"
    },
    "ABOUT_TEXT": {
        "ar": "حول",
        "en": "About"
    },
    "EXIT_MENU_TEXT": {
        "ar": "خروج",
        "en": "Exit"
    },
    "HELP_MENU_TEXT": {
        "ar": "مساعدة",
        "en": "Help"
    },
    "LANGUAGE_MENU_TEXT": {
        "ar": "اللغة (Language)",
        "en": "Language (اللغة)"
    },

    # About & Feedback
    "ABOUT_TITLE": {
        "ar": "حول لعبة إكس أو",
        "en": "About XO Game"
    },
    "ABOUT_MESSAGE": {
        "ar": "لعبة إكس أو بسيطة\nالإصدار: {version}\nتم تطويرها بواسطة المهندس محفوظ محمد بن سباح\n2020 - 2026",
        "en": "Simple Tic-Tac-Toe Game\nVersion: {version}\nDeveloped by Eng. Mahfoud Mohamed Bensebbah\n2020 - 2026"
    },
    "FEEDBACK_TITLE": {
        "ar": "التقييم",
        "en": "Feedback"
    },
    "FEEDBACK_MESSAGE": {
        "ar": "هل أعجبتك هذه اللعبة؟\nامنحني نجمة على مستودع GitHub!",
        "en": "Do you like this game?\nGive it a star on GitHub!"
    },

    # Update Dialogs & Notifications
    "CHECK_UPDATES_MENU_TEXT": {
        "ar": "التحقق من وجود تحديثات...",
        "en": "Check for Updates..."
    },
    "UPDATE_AVAILABLE_TITLE": {
        "ar": "تحديث جديد متوفر!",
        "en": "New Update Available!"
    },
    "UPDATE_MANDATORY_TITLE": {
        "ar": "⚠️ تحديث إجباري",
        "en": "⚠️ Mandatory Update"
    },
    "UPDATE_DIALOG_HEADING": {
        "ar": "إصدار جديد متوفر من لعبة إكس أو",
        "en": "A new version of XO Game is available"
    },
    "UPDATE_MANDATORY_HEADING": {
        "ar": "🚨 تحديث إجباري مطلوب!",
        "en": "🚨 Mandatory Update Required!"
    },
    "UPDATE_MANDATORY_WARNING": {
        "ar": "⚠️ هذا التحديث إلزامي للاستمرار في اللعب والتوافق مع خوادم اللعب الجماعي.",
        "en": "⚠️ This update is required to continue playing and maintain compatibility with multiplayer servers."
    },
    "CURRENT_VERSION_LABEL": {
        "ar": "الإصدار الحالي:",
        "en": "Current Version:"
    },
    "LATEST_VERSION_LABEL": {
        "ar": "أحدث إصدار:",
        "en": "Latest Version:"
    },
    "RELEASE_NOTES_HEADING": {
        "ar": "ما الجديد في هذا الإصدار / Release Notes:",
        "en": "What's New in this Release:"
    },
    "DOWNLOAD_UPDATE_BUTTON_TEXT": {
        "ar": "تحميل التحديث",
        "en": "Download Update"
    },
    "LATER_BUTTON_TEXT": {
        "ar": "لاحقاً",
        "en": "Later"
    },
    "CANCEL_TEXT": {
        "ar": "إلغاء",
        "en": "Cancel"
    },
    "UP_TO_DATE_TITLE": {
        "ar": "أنت على أحدث إصدار",
        "en": "Up to Date"
    },
    "UP_TO_DATE_MESSAGE": {
        "ar": "أنت تستخدم بالفعل أحدث إصدار من اللعبة (v{version}).",
        "en": "You are already using the latest version of the game (v{version})."
    },
    "UPDATE_CHECK_ERROR_TITLE": {
        "ar": "تعذر التحقق من التحديثات",
        "en": "Update Check Failed"
    },
    "UPDATE_CHECK_ERROR_MESSAGE": {
        "ar": "تعذر الاتصال بخادم التحديثات.\nيرجى التحقق من اتصالك بالإنترنت والمحاولة لاحقاً.",
        "en": "Unable to connect to update servers.\nPlease check your internet connection and try again later."
    },
    "MANDATORY_LOCKOUT_TITLE": {
        "ar": "تحديث إلزامي مطلوب",
        "en": "Mandatory Update Required"
    },
    "MANDATORY_LOCKOUT_MESSAGE": {
        "ar": "يتطلب اللعب عبر الشبكة تحديث اللعبة إلى الإصدار v{version} للتوافق مع خوادم اللعب الجماعي.\n\nهل ترغب في فتح نافذة التحديث الآن؟",
        "en": "Multiplayer mode requires updating the game to version v{version} to maintain server compatibility.\n\nWould you like to open the update window now?"
    },
    "DOWNLOADING_PROGRESS": {
        "ar": "جاري التحميل... {received:.1f} MB / {total:.1f} MB ({percent:.0f}%)",
        "en": "Downloading... {received:.1f} MB / {total:.1f} MB ({percent:.0f}%)"
    },
    "DOWNLOAD_COMPLETE_TITLE": {
        "ar": "اكتمل التحميل",
        "en": "Download Complete"
    },
    "DOWNLOAD_COMPLETE_MESSAGE": {
        "ar": "تم تحميل التحديث بنجاح إلى:\n{path}",
        "en": "Update successfully downloaded to:\n{path}"
    },
    "DOWNLOAD_FAILED_TITLE": {
        "ar": "فشل التحميل",
        "en": "Download Failed"
    },
    "DOWNLOAD_FAILED_PROMPT": {
        "ar": "فشل تحميل التحديث:\n{error}\n\nهل ترغب في فتح صفحة الإصدار في المتصفح للتحميل يدوياً؟",
        "en": "Failed to download update:\n{error}\n\nWould you like to open the release page in your browser to download manually?"
    },
    "DEV_MODE_TITLE": {
        "ar": "وضع التطوير / Development Mode",
        "en": "Development Mode"
    },
    "DEV_MODE_MESSAGE": {
        "ar": "أنت تعمل حالياً من الكود المصدري (Development Mode).\n\nسيتم فتح صفحة الإصدار في المتصفح لتحميل الحزمة يدوياً دون المساس ببيئة بايثون.",
        "en": "You are currently running from source code (Development Mode).\n\nThe release page will open in your browser to download manually without altering your Python environment."
    },

    # Multiplayer Mode Dialogs
    "MULTIPLAYER_MODE_TITLE": {
        "ar": "وضع متعدد اللاعبين",
        "en": "Multiplayer Mode"
    },
    "CHOOSE_GAME_MODE": {
        "ar": "اختر وضع اللعب",
        "en": "Choose Game Mode"
    },
    "HOST_GAME_TEXT": {
        "ar": "استضافة لعبة",
        "en": "Host Game"
    },
    "JOIN_GAME_TEXT": {
        "ar": "الانضمام للعبة",
        "en": "Join Game"
    },
    "BACK_TEXT": {
        "ar": "رجوع",
        "en": "Back"
    },
    "WAITING_TEXT": {
        "ar": "في انتظار لاعب...",
        "en": "Waiting for a player..."
    },
    "CONNECTED_TEXT": {
        "ar": "متصل!",
        "en": "Connected!"
    },
    "CONNECTION_FAILED_TEXT": {
        "ar": "فشل الاتصال",
        "en": "Connection Failed"
    },
    "ENTER_IP_TEXT": {
        "ar": "أدخل عنوان IP:",
        "en": "Enter IP Address:"
    },
    "CONNECT_TEXT": {
        "ar": "اتصال",
        "en": "Connect"
    },
    "REFRESH_TEXT": {
        "ar": "تحديث",
        "en": "Refresh"
    },
    "YOUR_IP_TEXT": {
        "ar": "عنوان IP الخاص بك: ",
        "en": "Your IP Address: "
    },
    "PLAYER_CONNECTED_TEXT": {
        "ar": "اللاعب متصل!",
        "en": "Player connected!"
    },
    "PLAYER_DISCONNECTED_TEXT": {
        "ar": "اللاعب قطع الاتصال",
        "en": "Player disconnected"
    },
    "YOUR_TURN_TEXT": {
        "ar": "دورك",
        "en": "Your Turn"
    },
    "OPPONENT_TURN_TEXT": {
        "ar": "دور الخصم",
        "en": "Opponent's Turn"
    },
    "HOST_SERVER_ERROR": {
        "ar": "فشل في بدء السيرفر. قد يكون المنفذ قيد الاستخدام.",
        "en": "Failed to start server. The port may already be in use."
    },
    "ERROR_TITLE": {
        "ar": "خطأ",
        "en": "Error"
    },
    "DISCONNECTED_TITLE": {
        "ar": "تم قطع الاتصال",
        "en": "Connection Lost"
    },
    "OPPONENT_DISCONNECTED": {
        "ar": "لقد انقطع اتصال الخصم!",
        "en": "Opponent has disconnected!"
    },
}


class I18n:
    """Internationalization manager supporting runtime switching and persistence."""

    SUPPORTED_LANGUAGES = ["ar", "en"]

    def __init__(self, settings_file: Optional[str] = None, default_lang: str = "ar"):
        if settings_file is None:
            home = os.path.expanduser("~")
            self.settings_file = os.path.join(home, ".xo_game_settings.json")
        else:
            self.settings_file = settings_file

        self._listeners: List[Callable[[], None]] = []
        self._current_lang = default_lang
        self._load_preference()

    def _load_preference(self):
        """Load preferred language from persistent settings file."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        saved = data.get("language")
                        if saved in self.SUPPORTED_LANGUAGES:
                            self._current_lang = saved
            except Exception:
                pass

    def _save_preference(self):
        """Save current language to persistent settings file."""
        data = {}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
            except Exception:
                data = {}
        data["language"] = self._current_lang
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def get_language(self) -> str:
        """Return the current active language code ('ar' or 'en')."""
        return self._current_lang

    @property
    def current_lang(self) -> str:
        return self._current_lang

    def set_language(self, lang: str):
        """Set active language and notify subscribers."""
        if lang not in self.SUPPORTED_LANGUAGES:
            return
        if self._current_lang != lang:
            self._current_lang = lang
            self._save_preference()
            self._notify_listeners()

    def toggle_language(self) -> str:
        """Toggle between Arabic and English."""
        new_lang = "en" if self._current_lang == "ar" else "ar"
        self.set_language(new_lang)
        return new_lang

    def t(self, key: str, **kwargs) -> str:
        """
        Translate a key to current language with optional keyword interpolation.
        Falls back to English, then the key itself if not found.
        """
        item = TRANSLATIONS.get(key)
        if not item:
            return key

        template = item.get(self._current_lang) or item.get("en") or key
        if kwargs:
            try:
                return template.format(**kwargs)
            except Exception:
                return template
        return template

    def subscribe(self, listener: Callable[[], None]):
        """Subscribe a callback to be called when language changes."""
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unsubscribe(self, listener: Callable[[], None]):
        """Unsubscribe a callback."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _notify_listeners(self):
        """Notify all subscribed UI components of language change."""
        for listener in list(self._listeners):
            try:
                listener()
            except Exception:
                pass


# Global singleton instance
i18n = I18n()
