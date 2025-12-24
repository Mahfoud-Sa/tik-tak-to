"""Game Client - Joins multiplayer game sessions."""

import socket
import threading
import time
from typing import Callable, Optional

from network.protocol import (
    NetworkMessage, MessageType,
    create_connect_message, create_pong_message, create_disconnect_message
)
from network_config import DEFAULT_PORT, BUFFER_SIZE, CONNECTION_TIMEOUT


class GameClient:
    """Client for joining multiplayer Tic-Tac-Toe games."""
    
    def __init__(self):
        """Initialize the game client."""
        self.socket: Optional[socket.socket] = None
        self.is_connected = False
        self.host_address: Optional[str] = None
        
        # Callbacks
        self._on_connect: Optional[Callable] = None
        self._on_disconnect: Optional[Callable] = None
        self._on_move_received: Optional[Callable[[int, int], None]] = None
        self._on_message_received: Optional[Callable[[NetworkMessage], None]] = None
        self._on_connection_failed: Optional[Callable[[str], None]] = None
        
        # Threading
        self._receive_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
    
    def connect(self, host: str, port: int = DEFAULT_PORT) -> bool:
        """
        Connect to a game server.
        
        Args:
            host: Server IP address
            port: Server port
            
        Returns:
            True if connection successful
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(CONNECTION_TIMEOUT)
            self.socket.connect((host, port))
            self.socket.settimeout(1.0)  # Set timeout for receive
            
            self.host_address = host
            self.is_connected = True
            
            # Send connect message
            self.send_message(create_connect_message())
            
            # Start receiving messages
            self._receive_thread = threading.Thread(
                target=self._receive_messages, daemon=True
            )
            self._receive_thread.start()
            
            # Notify callback
            if self._on_connect:
                self._on_connect()
            
            return True
            
        except socket.timeout:
            if self._on_connection_failed:
                self._on_connection_failed("Connection timed out")
            return False
        except ConnectionRefusedError:
            if self._on_connection_failed:
                self._on_connection_failed("Connection refused")
            return False
        except Exception as e:
            if self._on_connection_failed:
                self._on_connection_failed(str(e))
            return False
    
    def disconnect(self):
        """Disconnect from the server."""
        if self.socket and self.is_connected:
            try:
                self.send_message(create_disconnect_message("Client leaving"))
            except Exception:
                pass
        
        self._cleanup()
    
    def refresh(self) -> bool:
        """Refresh connection - disconnect and reconnect."""
        if self.host_address:
            host = self.host_address
            self._cleanup()
            time.sleep(0.5)
            return self.connect(host)
        return False
    
    def _cleanup(self):
        """Clean up socket resources."""
        with self._lock:
            self.is_connected = False
            if self.socket:
                try:
                    self.socket.close()
                except Exception:
                    pass
                self.socket = None
    
    def _receive_messages(self):
        """Background thread to receive messages from server."""
        buffer = ""
        while self.is_connected:
            try:
                if not self.socket:
                    break
                    
                data = self.socket.recv(BUFFER_SIZE)
                if not data:
                    # Server disconnected
                    self._handle_disconnect()
                    break
                
                buffer += data.decode('utf-8')
                
                # Process complete messages
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    message = NetworkMessage.from_json(line)
                    if message:
                        self._process_message(message)
                        
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Receive error: {e}")
                self._handle_disconnect()
                break
    
    def _process_message(self, message: NetworkMessage):
        """Process an incoming message."""
        if message.msg_type == MessageType.PING:
            self.send_message(create_pong_message())
        elif message.msg_type == MessageType.MOVE:
            if self._on_move_received:
                row = message.data.get('row', -1)
                col = message.data.get('col', -1)
                self._on_move_received(row, col)
        elif message.msg_type == MessageType.DISCONNECT:
            self._handle_disconnect()
        
        # General callback
        if self._on_message_received:
            self._on_message_received(message)
    
    def _handle_disconnect(self):
        """Handle server disconnect."""
        was_connected = self.is_connected
        self._cleanup()
        
        if was_connected and self._on_disconnect:
            self._on_disconnect()
    
    def send_message(self, message: NetworkMessage) -> bool:
        """Send a message to the server."""
        if not self.socket or not self.is_connected:
            return False
        
        try:
            self.socket.sendall(message.to_bytes())
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def send_move(self, row: int, col: int) -> bool:
        """Send a move to the server."""
        from network.protocol import create_move_message
        return self.send_message(create_move_message(row, col))
    
    # Callback setters
    def on_connect(self, callback: Callable):
        """Set callback for successful connection."""
        self._on_connect = callback
    
    def on_disconnect(self, callback: Callable):
        """Set callback for disconnection."""
        self._on_disconnect = callback
    
    def on_move_received(self, callback: Callable[[int, int], None]):
        """Set callback for when a move is received."""
        self._on_move_received = callback
    
    def on_message_received(self, callback: Callable[[NetworkMessage], None]):
        """Set callback for any message received."""
        self._on_message_received = callback
    
    def on_connection_failed(self, callback: Callable[[str], None]):
        """Set callback for connection failure."""
        self._on_connection_failed = callback
