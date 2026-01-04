"""Multiplayer dialogs for hosting and joining games."""

from tkinter import Toplevel, Label, Button, Entry, Frame, Canvas, StringVar, PhotoImage
from tkinter import messagebox as msg
from typing import Callable, Optional
from os import path

from network_config import (
    HOST_GAME_TEXT, JOIN_GAME_TEXT, WAITING_TEXT, CONNECTED_TEXT,
    YOUR_IP_TEXT, ENTER_IP_TEXT, REFRESH_TEXT, CANCEL_TEXT, CONNECT_TEXT, BACK_TEXT,
    STATUS_CONNECTED_COLOR, STATUS_DISCONNECTED_COLOR, STATUS_WAITING_COLOR,
    PLAYER_CONNECTED_TEXT, PLAYER_DISCONNECTED_TEXT, DEFAULT_PORT
)


class MultiplayerModeDialog:
    """Dialog for choosing between Host and Join."""
    
    def __init__(self, parent, on_host: Callable, on_join: Callable):
        """
        Initialize the mode selection dialog.
        
        Args:
            parent: Parent window
            on_host: Callback when Host is selected
            on_join: Callback when Join is selected
        """
        self.dialog = Toplevel(parent)
        self.dialog.title("وضع متعدد اللاعبين")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("300x250")
        self._center_window(parent)
        
        self._on_host = on_host
        self._on_join = on_join
        
        # Set icon to match main window
        self._set_icon()
        
        self._create_ui()
    
    def _center_window(self, parent):
        """Center the dialog on parent window."""
        self.dialog.update_idletasks()
        parent.update_idletasks()
        
        px = parent.winfo_x()
        py = parent.winfo_y()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        
        w = 300
        h = 250
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")
    
    def _create_ui(self):
        """Create the dialog UI."""
        # Title
        title = Label(
            self.dialog,
            text="اختر وضع اللعب",
            font=('Arial', 14, 'bold')
        )
        title.pack(pady=20)
        
        # Button frame
        btn_frame = Frame(self.dialog)
        btn_frame.pack(pady=10)
        
        # Host button
        host_btn = Button(
            btn_frame,
            text=f"🖥️ {HOST_GAME_TEXT}",
            font=('Arial', 11),
            width=15,
            command=self._on_host_click
        )
        host_btn.pack(pady=5)
        
        # Join button
        join_btn = Button(
            btn_frame,
            text=f"🔗 {JOIN_GAME_TEXT}",
            font=('Arial', 11),
            width=15,
            command=self._on_join_click
        )
        join_btn.pack(pady=5)
        
        # Cancel button
        cancel_btn = Button(
            self.dialog,
            text=f"❌ {CANCEL_TEXT}",
            font=('Arial', 8),
            width=15,
            command=self.close
        )
        cancel_btn.pack(pady=10)
    
    def _on_host_click(self):
        """Handle Host button click."""
        self.close()
        self._on_host()
    
    def _on_join_click(self):
        """Handle Join button click."""
        self.close()
        self._on_join()
    
    def close(self):
        """Close the dialog."""
        self.dialog.destroy()
    
    def _set_icon(self):
        """Set the dialog icon to match main window."""
        try:
            icon_path = path.abspath(path.join(path.dirname(__file__), '../../assets/icons/icon.png'))
            self._icon = PhotoImage(file=icon_path)
            self.dialog.iconphoto(False, self._icon)
        except Exception:
            pass  # Icon not essential


class HostGameDialog:
    """Dialog for hosting a game and waiting for players."""
    
    def __init__(self, parent, ip_address: str, on_cancel: Callable, on_refresh: Callable):
        """
        Initialize the host game dialog.
        
        Args:
            parent: Parent window
            ip_address: Host's LAN IP address
            on_cancel: Callback when cancelled
            on_refresh: Callback when refresh clicked
        """
        self.dialog = Toplevel(parent)
        self.dialog.title("استضافة لعبة")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.dialog.geometry("350x250")
        self._center_window(parent)
        
        self._on_cancel = on_cancel
        self._on_refresh = on_refresh
        self._ip_address = ip_address
        
        # Connection status
        self._is_connected = False
        
        # Set icon to match main window
        self._set_icon()
        
        self._create_ui()
    
    def _center_window(self, parent):
        """Center the dialog on parent window."""
        self.dialog.update_idletasks()
        parent.update_idletasks()
        
        px = parent.winfo_x()
        py = parent.winfo_y()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        
        w = 350
        h = 250
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")
    
    def _create_ui(self):
        """Create the dialog UI."""
        # Title
        title = Label(
            self.dialog,
            text="جاري الاستضافة",
            font=('Arial', 14, 'bold')
        )
        title.pack(pady=15)
        
        # IP Address display
        ip_frame = Frame(self.dialog)
        ip_frame.pack(pady=5)
        
        ip_label = Label(
            ip_frame,
            text=YOUR_IP_TEXT,
            font=('Arial', 11)
        )
        ip_label.pack(side='left')
        
        ip_value = Label(
            ip_frame,
            text=self._ip_address,
            font=('Arial', 12, 'bold'),
            fg='blue'
        )
        ip_value.pack(side='left')
        
        # Port info
        port_label = Label(
            self.dialog,
            text=f"Port: {DEFAULT_PORT}",
            font=('Arial', 10),
            fg='gray'
        )
        port_label.pack()
        
        # Connection status frame
        status_frame = Frame(self.dialog)
        status_frame.pack(pady=15)
        
        # Status indicator (circle)
        self._status_canvas = Canvas(
            status_frame,
            width=20,
            height=20,
            highlightthickness=0
        )
        self._status_canvas.pack(side='left', padx=5)
        self._status_circle = self._status_canvas.create_oval(
            2, 2, 18, 18,
            fill=STATUS_WAITING_COLOR,
            outline=''
        )
        
        # Status text
        self._status_label = Label(
            status_frame,
            text=WAITING_TEXT,
            font=('Arial', 11)
        )
        self._status_label.pack(side='left')
        
        # Button frame
        btn_frame = Frame(self.dialog)
        btn_frame.pack(pady=15)
        
        # Refresh button
        self._refresh_btn = Button(
            btn_frame,
            text=f"🔄 {REFRESH_TEXT}",
            font=('Arial', 10),
            width=10,
            command=self._on_refresh_click
        )
        self._refresh_btn.pack(side='left', padx=5)
        
        # Cancel button
        cancel_btn = Button(
            btn_frame,
            text=f"❌ {CANCEL_TEXT}",
            font=('Arial', 10),
            width=10,
            command=self._on_cancel_click
        )
        cancel_btn.pack(side='left', padx=5)
    
    def set_connected(self, connected: bool):
        """Update the connection status indicator."""
        self._is_connected = connected
        if connected:
            self._status_canvas.itemconfig(
                self._status_circle,
                fill=STATUS_CONNECTED_COLOR
            )
            self._status_label.config(text=PLAYER_CONNECTED_TEXT)
        else:
            self._status_canvas.itemconfig(
                self._status_circle,
                fill=STATUS_DISCONNECTED_COLOR
            )
            self._status_label.config(text=PLAYER_DISCONNECTED_TEXT)
    
    def set_waiting(self):
        """Set status to waiting."""
        self._is_connected = False
        self._status_canvas.itemconfig(
            self._status_circle,
            fill=STATUS_WAITING_COLOR
        )
        self._status_label.config(text=WAITING_TEXT)
    
    def _on_refresh_click(self):
        """Handle refresh button click."""
        self.set_waiting()
        self._on_refresh()
    
    def _on_cancel_click(self):
        """Handle cancel button click."""
        self.close()
        self._on_cancel()
    
    def close(self):
        """Close the dialog."""
        self.dialog.destroy()
    
    def _set_icon(self):
        """Set the dialog icon to match main window."""
        try:
            icon_path = path.abspath(path.join(path.dirname(__file__), '../../assets/icons/icon.png'))
            self._icon = PhotoImage(file=icon_path)
            self.dialog.iconphoto(False, self._icon)
        except Exception:
            pass  # Icon not essential


class JoinGameDialog:
    """Dialog for joining a hosted game."""
    
    def __init__(self, parent, on_connect: Callable[[str], None], on_cancel: Callable):
        """
        Initialize the join game dialog.
        
        Args:
            parent: Parent window
            on_connect: Callback with IP address when connect clicked
            on_cancel: Callback when cancelled
        """
        self.dialog = Toplevel(parent)
        self.dialog.title("الانضمام للعبة")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.dialog.geometry("350x250")
        self._center_window(parent)
        
        self._on_connect = on_connect
        self._on_cancel = on_cancel
        
        # Connection status
        self._is_connected = False
        
        # Set icon to match main window
        self._set_icon()
        
        self._create_ui()
    
    def _center_window(self, parent):
        """Center the dialog on parent window."""
        self.dialog.update_idletasks()
        parent.update_idletasks()
        
        px = parent.winfo_x()
        py = parent.winfo_y()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        
        w = 350
        h = 250
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        
        self.dialog.geometry(f"{w}x{h}+{x}+{y}")
    
    def _create_ui(self):
        """Create the dialog UI."""
        # Title
        title = Label(
            self.dialog,
            text="الانضمام للعبة",
            font=('Arial', 14, 'bold')
        )
        title.pack(pady=15)
        
        # IP input frame
        ip_frame = Frame(self.dialog)
        ip_frame.pack(pady=10)
        
        ip_label = Label(
            ip_frame,
            text=ENTER_IP_TEXT,
            font=('Arial', 11)
        )
        ip_label.pack(side='left', padx=5)
        
        self._ip_var = StringVar()
        self._ip_entry = Entry(
            ip_frame,
            textvariable=self._ip_var,
            font=('Arial', 11),
            width=15
        )
        self._ip_entry.pack(side='left', padx=5)
        self._ip_entry.focus_set()
        
        # Port info
        port_label = Label(
            self.dialog,
            text=f"Port: {DEFAULT_PORT}",
            font=('Arial', 10),
            fg='gray'
        )
        port_label.pack()
        
        # Connection status frame
        status_frame = Frame(self.dialog)
        status_frame.pack(pady=15)
        
        # Status indicator (circle)
        self._status_canvas = Canvas(
            status_frame,
            width=20,
            height=20,
            highlightthickness=0
        )
        self._status_canvas.pack(side='left', padx=5)
        self._status_circle = self._status_canvas.create_oval(
            2, 2, 18, 18,
            fill=STATUS_DISCONNECTED_COLOR,
            outline=''
        )
        
        # Status text
        self._status_label = Label(
            status_frame,
            text="غير متصل",
            font=('Arial', 11)
        )
        self._status_label.pack(side='left')
        
        # Button frame
        btn_frame = Frame(self.dialog)
        btn_frame.pack(pady=10)
        
        # Connect button
        self._connect_btn = Button(
            btn_frame,
            text=f"🔗 {CONNECT_TEXT}",
            font=('Arial', 10),
            width=10,
            command=self._on_connect_click
        )
        self._connect_btn.pack(side='left', padx=5)
        
        # Refresh button
        self._refresh_btn = Button(
            btn_frame,
            text=f"🔄 {REFRESH_TEXT}",
            font=('Arial', 10),
            width=10,
            command=self._on_refresh_click
        )
        self._refresh_btn.pack(side='left', padx=5)
        
        # Cancel button
        cancel_btn = Button(
            btn_frame,
            text=f"❌ {CANCEL_TEXT}",
            font=('Arial', 10),
            width=10,
            command=self._on_cancel_click
        )
        cancel_btn.pack(side='left', padx=5)
        
        # Bind Enter key
        self._ip_entry.bind('<Return>', lambda e: self._on_connect_click())
    
    def set_connected(self, connected: bool):
        """Update the connection status indicator."""
        self._is_connected = connected
        if connected:
            self._status_canvas.itemconfig(
                self._status_circle,
                fill=STATUS_CONNECTED_COLOR
            )
            self._status_label.config(text=CONNECTED_TEXT)
        else:
            self._status_canvas.itemconfig(
                self._status_circle,
                fill=STATUS_DISCONNECTED_COLOR
            )
            self._status_label.config(text=PLAYER_DISCONNECTED_TEXT)
    
    def set_connecting(self):
        """Set status to connecting."""
        self._status_canvas.itemconfig(
            self._status_circle,
            fill=STATUS_WAITING_COLOR
        )
        self._status_label.config(text="جاري الاتصال...")
    
    def set_error(self, message: str):
        """Set status to error."""
        self._status_canvas.itemconfig(
            self._status_circle,
            fill=STATUS_DISCONNECTED_COLOR
        )
        self._status_label.config(text=message)
    
    def _on_connect_click(self):
        """Handle connect button click."""
        ip = self._ip_var.get().strip()
        if not ip:
            msg.showwarning("مطلوب إدخال", "الرجاء إدخال عنوان IP")
            return
        
        self.set_connecting()
        self._on_connect(ip)
    
    def _on_refresh_click(self):
        """Handle refresh button click - retry connection."""
        ip = self._ip_var.get().strip()
        if ip:
            self.set_connecting()
            self._on_connect(ip)
    
    def _on_cancel_click(self):
        """Handle cancel button click."""
        self.close()
        self._on_cancel()
    
    def close(self):
        """Close the dialog."""
        self.dialog.destroy()
    
    def _set_icon(self):
        """Set the dialog icon to match main window."""
        try:
            icon_path = path.abspath(path.join(path.dirname(__file__), '../../assets/icons/icon.png'))
            self._icon = PhotoImage(file=icon_path)
            self.dialog.iconphoto(False, self._icon)
        except Exception:
            pass  # Icon not essential
