"""
Update Notifier Dialog Widget
Displays a modal notification when a new version of the game is available.
Supports mandatory updates, channel tags, release notes preview, and dismissal persistence.
"""

import webbrowser
from tkinter import Toplevel, Label, Button, Frame, Text, Scrollbar, PhotoImage
from os import path
from typing import Optional, Callable

from utils.updater import UpdateManifest
from config import (
    ICON_PATH, BUTTON_FONT, TITLE_FONT,
    UPDATE_AVAILABLE_TITLE, UPDATE_DIALOG_HEADING,
    CURRENT_VERSION_LABEL, LATEST_VERSION_LABEL,
    DOWNLOAD_UPDATE_BUTTON_TEXT, LATER_BUTTON_TEXT
)


class UpdateNotifierDialog:
    """Dialog notifying the player that an update is available."""

    def __init__(
        self,
        parent,
        current_version: str,
        manifest: UpdateManifest,
        is_mandatory: bool = False,
        on_dismiss: Optional[Callable[[str], None]] = None
    ):
        self.parent = parent
        self.current_version = current_version
        self.manifest = manifest
        self.is_mandatory = is_mandatory
        self.on_dismiss = on_dismiss

        self.dialog = Toplevel(parent)
        self.dialog.title("⚠️ تحديث إجباري" if is_mandatory else UPDATE_AVAILABLE_TITLE)
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Handle window close (X button)
        if self.is_mandatory:
            self.dialog.protocol("WM_DELETE_WINDOW", self._on_mandatory_close)
        else:
            self.dialog.protocol("WM_DELETE_WINDOW", self._on_later)

        # Center the dialog
        self.width = 460
        self.height = 380 if is_mandatory else 360
        self._center_window(parent)
        self._set_icon()
        self._create_ui()

    def _set_icon(self):
        """Set window icon to match main window."""
        try:
            icon_file = path.abspath(path.join(path.dirname(__file__), "..", "..", ICON_PATH))
            if path.exists(icon_file):
                self.dialog.iconphoto(False, PhotoImage(file=icon_file))
        except Exception:
            pass

    def _center_window(self, parent):
        """Center the dialog over parent window."""
        self.dialog.update_idletasks()
        parent.update_idletasks()

        px = parent.winfo_x()
        py = parent.winfo_y()
        pw = parent.winfo_width()
        ph = parent.winfo_height()

        x = px + max(0, (pw - self.width) // 2)
        y = py + max(0, (ph - self.height) // 2)

        self.dialog.geometry(f"{self.width}x{self.height}+{x}+{y}")

    def _create_ui(self):
        """Build dialog widgets."""
        header_bg = "#C62828" if self.is_mandatory else "#1E88E5"
        header_text = "🚨 تحديث إجباري مطلوب!" if self.is_mandatory else f"✨ {UPDATE_DIALOG_HEADING}"

        # Header banner
        header_frame = Frame(self.dialog, bg=header_bg, pady=10)
        header_frame.pack(fill="x")

        title_label = Label(
            header_frame,
            text=header_text,
            font=('Arial', 13, 'bold'),
            fg="white",
            bg=header_bg
        )
        title_label.pack()

        content_frame = Frame(self.dialog, padx=20, pady=10)
        content_frame.pack(fill="both", expand=True)

        # Mandatory warning message if applicable
        if self.is_mandatory:
            mand_label = Label(
                content_frame,
                text="⚠️ هذا التحديث إلزامي للاستمرار في اللعب والتوافق مع خوادم اللعب الجماعي.",
                font=('Arial', 9, 'bold'),
                fg="#C62828",
                wraplength=420,
                justify="center"
            )
            mand_label.pack(pady=(0, 6))

        # Version comparison row
        version_frame = Frame(content_frame, pady=4)
        version_frame.pack(fill="x")

        curr_ver_text = f"{CURRENT_VERSION_LABEL} v{self.current_version}"
        curr_label = Label(
            version_frame,
            text=curr_ver_text,
            font=('Arial', 10),
            fg="#666666"
        )
        curr_label.pack(side="right", padx=10)

        channel_badge = f" [{self.manifest.channel.upper()}]" if self.manifest.channel != "stable" else ""
        new_ver_text = f"{LATEST_VERSION_LABEL} v{self.manifest.version}{channel_badge}"
        new_label = Label(
            version_frame,
            text=new_ver_text,
            font=('Arial', 11, 'bold'),
            fg="#2E7D32" if not self.is_mandatory else "#C62828"
        )
        new_label.pack(side="left", padx=10)

        # Release notes header
        notes_label = Label(
            content_frame,
            text="ما الجديد في هذا الإصدار / Release Notes:",
            font=('Arial', 9, 'bold'),
            anchor="w"
        )
        notes_label.pack(fill="x", pady=(6, 2))

        # Notes scrollable text box
        notes_frame = Frame(content_frame)
        notes_frame.pack(fill="both", expand=True, pady=4)

        scrollbar = Scrollbar(notes_frame)
        scrollbar.pack(side="right", fill="y")

        notes_text = Text(
            notes_frame,
            wrap="word",
            height=6,
            font=('Consolas', 9),
            yscrollcommand=scrollbar.set,
            relief="groove",
            borderwidth=1
        )
        notes_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=notes_text.yview)

        notes_content = self.manifest.release_notes.strip()
        if not notes_content:
            notes_content = f"Release {self.manifest.tag_name}\nتحسينات وإصلاحات جديدة للميزات والاتصال الشبكي."
        notes_text.insert("1.0", notes_content)
        notes_text.config(state="disabled")

        # Bottom actions frame
        btn_frame = Frame(self.dialog, pady=10, padx=20)
        btn_frame.pack(fill="x")

        # Later button (omitted or disabled if mandatory)
        if not self.is_mandatory:
            later_btn = Button(
                btn_frame,
                text=LATER_BUTTON_TEXT,
                font=BUTTON_FONT,
                width=10,
                command=self._on_later
            )
            later_btn.pack(side="right", padx=8)

        # Download / Update button
        download_btn = Button(
            btn_frame,
            text=f"⬇️ {DOWNLOAD_UPDATE_BUTTON_TEXT}",
            font=BUTTON_FONT,
            bg="#2E7D32" if not self.is_mandatory else "#C62828",
            fg="white",
            activebackground="#1B5E20" if not self.is_mandatory else "#8E0000",
            activeforeground="white",
            command=self._on_download
        )
        download_btn.pack(side="left", padx=8)

    def _on_download(self):
        """Open download or release page link."""
        target_url = self.manifest.download_url or self.manifest.release_page_url
        if not target_url:
            target_url = "https://github.com/Mahfoud-Sa/tik-tak-to/releases"
        webbrowser.open(target_url)
        self.dialog.destroy()

    def _on_later(self):
        """Player clicked Later; persist dismissal so it doesn't prompt again automatically."""
        if self.on_dismiss:
            self.on_dismiss(self.manifest.version)
        self.dialog.destroy()

    def _on_mandatory_close(self):
        """Closing a mandatory update dialog closes the dialog."""
        self.dialog.destroy()
