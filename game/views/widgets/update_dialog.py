"""
Update Notifier Dialog Widget
Displays a modal notification when a new version of the game is available.
Supports mandatory updates, channel tags, release notes preview, and dismissal persistence.
"""

import sys
import webbrowser
from tkinter import Toplevel, Label, Button, Frame, Text, Scrollbar, PhotoImage, ttk, messagebox as msg
from os import path
from typing import Optional, Callable

from utils.updater import UpdateManifest, UpdateService, DownloadCancellationToken
try:
    from utils.i18n import i18n
except ImportError:
    from game.utils.i18n import i18n

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
        on_dismiss: Optional[Callable[[str], None]] = None,
        update_service: Optional[UpdateService] = None,
        on_apply_update: Optional[Callable[[str], None]] = None
    ):
        self.parent = parent
        self.current_version = current_version
        self.manifest = manifest
        self.is_mandatory = is_mandatory
        self.on_dismiss = on_dismiss
        self.update_service = update_service
        self.on_apply_update = on_apply_update

        self._is_downloading = False
        self._cancel_token: Optional[DownloadCancellationToken] = None
        self._progress_bar = None
        self._progress_label = None
        self._cancel_btn = None
        self.download_btn = None
        self.later_btn = None

        self.dialog = Toplevel(parent)
        dialog_title = i18n.t("UPDATE_MANDATORY_TITLE") if is_mandatory else i18n.t("UPDATE_AVAILABLE_TITLE")
        self.dialog.title(dialog_title)
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
        try:
            self.dialog.update_idletasks()
            parent.update_idletasks()

            px = int(parent.winfo_x())
            py = int(parent.winfo_y())
            pw = int(parent.winfo_width())
            ph = int(parent.winfo_height())

            x = px + max(0, (pw - self.width) // 2)
            y = py + max(0, (ph - self.height) // 2)

            self.dialog.geometry(f"{self.width}x{self.height}+{x}+{y}")
        except Exception:
            pass

    def _create_ui(self):
        """Build dialog widgets."""
        header_bg = "#C62828" if self.is_mandatory else "#1E88E5"
        header_text = i18n.t("UPDATE_MANDATORY_HEADING") if self.is_mandatory else f"✨ {i18n.t('UPDATE_DIALOG_HEADING')}"

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
                text=i18n.t("UPDATE_MANDATORY_WARNING"),
                font=('Arial', 9, 'bold'),
                fg="#C62828",
                wraplength=420,
                justify="center"
            )
            mand_label.pack(pady=(0, 6))

        # Version comparison row
        version_frame = Frame(content_frame, pady=4)
        version_frame.pack(fill="x")

        curr_ver_text = f"{i18n.t('CURRENT_VERSION_LABEL')} v{self.current_version}"
        curr_label = Label(
            version_frame,
            text=curr_ver_text,
            font=('Arial', 10),
            fg="#666666"
        )
        curr_label.pack(side=i18n.side_end(), padx=10)

        channel_badge = f" [{self.manifest.channel.upper()}]" if self.manifest.channel != "stable" else ""
        new_ver_text = f"{i18n.t('LATEST_VERSION_LABEL')} v{self.manifest.version}{channel_badge}"
        new_label = Label(
            version_frame,
            text=new_ver_text,
            font=('Arial', 11, 'bold'),
            fg="#2E7D32" if not self.is_mandatory else "#C62828"
        )
        new_label.pack(side=i18n.side_start(), padx=10)

        # Release notes header
        notes_label = Label(
            content_frame,
            text=i18n.t("RELEASE_NOTES_HEADING"),
            font=('Arial', 9, 'bold'),
            anchor=i18n.anchor_start()
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
            notes_content = f"Release {self.manifest.tag_name}\n" + i18n.t("UPDATE_DIALOG_HEADING")
        notes_text.insert("1.0", notes_content)
        notes_text.config(state="disabled")

        # Bottom actions frame
        self.btn_frame = Frame(self.dialog, pady=10, padx=20)
        self.btn_frame.pack(fill="x")

        # Download / Update button (Primary action on side_start)
        self.download_btn = Button(
            self.btn_frame,
            text=f"⬇️ {i18n.t('DOWNLOAD_UPDATE_BUTTON_TEXT')}",
            font=BUTTON_FONT,
            bg="#2E7D32" if not self.is_mandatory else "#C62828",
            fg="white",
            activebackground="#1B5E20" if not self.is_mandatory else "#8E0000",
            activeforeground="white",
            command=self._on_download
        )
        self.download_btn.pack(side=i18n.side_start(), padx=8)

        # Later button (Dismiss action on side_end)
        if not self.is_mandatory:
            self.later_btn = Button(
                self.btn_frame,
                text=i18n.t("LATER_BUTTON_TEXT"),
                font=BUTTON_FONT,
                width=10,
                command=self._on_later
            )
            self.later_btn.pack(side=i18n.side_end(), padx=8)

    def _on_download(self):
        """Handle download action. If running in source mode, redirect to browser."""
        if not getattr(sys, 'frozen', False):
            msg.showinfo(
                i18n.t("DEV_MODE_TITLE"),
                i18n.t("DEV_MODE_MESSAGE")
            )
            target_url = self.manifest.release_page_url or self.manifest.download_url or "https://github.com/Mahfoud-Sa/tik-tak-to/releases"
            webbrowser.open(target_url)
            self.dialog.destroy()
            return

        if self.update_service:
            self._start_in_modal_download()
        else:
            target_url = self.manifest.download_url or self.manifest.release_page_url or "https://github.com/Mahfoud-Sa/tik-tak-to/releases"
            webbrowser.open(target_url)
            self.dialog.destroy()

    def _start_in_modal_download(self):
        """Transform action bar into an in-modal progress bar."""
        self._is_downloading = True
        self._cancel_token = DownloadCancellationToken()

        # Hide original buttons
        if self.download_btn and self.download_btn.winfo_exists():
            self.download_btn.pack_forget()
        if self.later_btn and self.later_btn.winfo_exists():
            self.later_btn.pack_forget()

        # Create progress UI
        self._progress_label = Label(
            self.btn_frame,
            text=i18n.t("DOWNLOADING_PROGRESS", received=0.0, total=0.0, percent=0.0),
            font=('Arial', 9),
            fg="#444444"
        )
        self._progress_label.pack(side="top", fill="x", pady=(0, 4))

        self._cancel_btn = Button(
            self.btn_frame,
            text=i18n.t("CANCEL_TEXT"),
            font=BUTTON_FONT,
            width=8,
            command=self._on_cancel_download
        )
        self._cancel_btn.pack(side=i18n.side_end())

        progress_padx = (10, 0) if i18n.is_rtl else (0, 10)
        self._progress_bar = ttk.Progressbar(
            self.btn_frame,
            orient='horizontal',
            mode='determinate',
            length=300
        )
        self._progress_bar.pack(side=i18n.side_start(), fill="x", expand=True, padx=progress_padx)

        self.update_service.download_update_async(
            manifest=self.manifest,
            on_progress=self._on_download_progress,
            on_complete=self._on_download_complete,
            cancel_token=self._cancel_token
        )

    def _on_download_progress(self, received: int, total: int, pct: float):
        """Update progress bar and label safely on main UI thread."""
        try:
            if not self._is_downloading or not self.dialog.winfo_exists():
                return

            def update():
                if not self._is_downloading or not self._progress_bar or not self._progress_label:
                    return
                rec_mb = received / (1024 * 1024)
                tot_mb = total / (1024 * 1024) if total > 0 else 0
                self._progress_bar['value'] = pct
                self._progress_label.config(
                    text=i18n.t("DOWNLOADING_PROGRESS", received=rec_mb, total=tot_mb, percent=pct)
                )

            self.dialog.after(0, update)
        except Exception:
            pass

    def _on_cancel_download(self):
        """Cancel the active download operation."""
        if self._cancel_token:
            self._cancel_token.cancel()
        self._restore_action_buttons()

    def _restore_action_buttons(self):
        """Tear down progress UI and restore download / later buttons."""
        self._is_downloading = False
        if self._progress_bar:
            self._progress_bar.destroy()
            self._progress_bar = None
        if self._progress_label:
            self._progress_label.destroy()
            self._progress_label = None
        if self._cancel_btn:
            self._cancel_btn.destroy()
            self._cancel_btn = None

        if self.download_btn and self.download_btn.winfo_exists():
            self.download_btn.pack(side="left", padx=8)
        if self.later_btn and self.later_btn.winfo_exists() and not self.is_mandatory:
            self.later_btn.pack(side="right", padx=8)

    def _on_download_complete(self, success: bool, filepath: Optional[str], error: Optional[str]):
        """Handle download finish or error."""
        try:
            if not self.dialog.winfo_exists():
                return

            def handle():
                if not self._is_downloading:
                    return

                if success and filepath:
                    self.dialog.destroy()
                    if self.on_apply_update:
                        self.on_apply_update(filepath)
                    else:
                        msg.showinfo(
                            i18n.t("DOWNLOAD_COMPLETE_TITLE"),
                            i18n.t("DOWNLOAD_COMPLETE_MESSAGE", path=filepath)
                        )
                else:
                    if self._cancel_token and self._cancel_token.is_cancelled:
                        self._restore_action_buttons()
                        return

                    target_url = self.manifest.release_page_url or self.manifest.download_url or "https://github.com/Mahfoud-Sa/tik-tak-to/releases"
                    err_msg = error or i18n.t("UPDATE_CHECK_ERROR_TITLE")
                    prompt = i18n.t("DOWNLOAD_FAILED_PROMPT", error=err_msg)
                    if msg.askyesno(i18n.t("DOWNLOAD_FAILED_TITLE"), prompt, icon="error"):
                        webbrowser.open(target_url)
                        self.dialog.destroy()
                    else:
                        self._restore_action_buttons()

            self.dialog.after(0, handle)
        except Exception:
            pass

    def _on_later(self):
        """Player clicked Later; persist dismissal so it doesn't prompt again automatically."""
        if self._is_downloading and self._cancel_token:
            self._cancel_token.cancel()
        if self.on_dismiss:
            self.on_dismiss(self.manifest.version)
        self.dialog.destroy()

    def _on_mandatory_close(self):
        """Closing a mandatory update dialog closes the dialog."""
        if self._is_downloading and self._cancel_token:
            self._cancel_token.cancel()
        self.dialog.destroy()
