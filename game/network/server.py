"""Game Server - Hosts multiplayer game sessions."""

import socket
import threading
import time
from typing import Callable, Optional

from network.protocol import (
    NetworkMessage, MessageType,
    create_connect_message, create_pong_message, create_disconnect_message
)
from network_config import DEFAULT_PORT, BUFFER_SIZE, CONNECTION_TIMEOUT


class GameServer:
    """Server for hosting multiplayer Tic-Tac-Toe games."""
    
    def __init__(self):
        """Initialize the game server."""
        self.socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.client_address: Optional[tuple] = None
        self.is_running = False
        self.is_connected = False
        
        # Callbacks
        self._on_client_connect: Optional[Callable] = None
        self._on_client_disconnect: Optional[Callable] = None
        self._on_move_received: Optional[Callable[[int, int], None]] = None
        self._on_message_received: Optional[Callable[[NetworkMessage], None]] = None
        
        # Threading
        self._accept_thread: Optional[threading.Thread] = None
        self._receive_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
    
    def get_local_ip(self) -> str:
        """Get the local IP address for LAN connections."""
        try:
            # Create a dummy connection to find local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def start(self, port: int = DEFAULT_PORT) -> bool:
        """
        Start the server and listen for connections.
        
        Args:
            port: Port to listen on
            
        Returns:
            True if server started successfully
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('', port))
            self.socket.listen(1)
            self.socket.settimeout(1.0)  # Allow periodic checking
            self.is_running = True
            
            # Start accepting connections in background
            self._accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            self._accept_thread.start()
            
            return True
        except Exception as e:
            print(f"Server start error: {e}")
            return False
    
    def stop(self):
        """Stop the server and disconnect all clients."""
        self.is_running = False
        self.is_connected = False
        
        # Send disconnect to client
        if self.client_socket:
            try:
                self.send_message(create_disconnect_message("Server closing"))
                self.client_socket.close()
            except Exception:
                pass
            self.client_socket = None
        
        # Close server socket
        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass
            self.socket = None
    
    def refresh(self):
        """Refresh - close current client and wait for new connection."""
        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception:
                pass
            self.client_socket = None
        
        self.is_connected = False
        if self._on_client_disconnect:
            self._on_client_disconnect()
    
    def _accept_connections(self):
        """Background thread to accept incoming connections."""
        while self.is_running:
            try:
                client, address = self.socket.accept()
                with self._lock:
                    self.client_socket = client
                    self.client_address = address
                    self.is_connected = True
                
                # Start receiving messages from client
                self._receive_thread = threading.Thread(
                    target=self._receive_messages, daemon=True
                )
                self._receive_thread.start()
                
                # Notify callback
                if self._on_client_connect:
                    self._on_client_connect()
                    
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    print(f"Accept error: {e}")
                break
    
    def _receive_messages(self):
        """Background thread to receive messages from client."""
        buffer = ""
        while self.is_running and self.is_connected:
            try:
                if not self.client_socket:
                    break
                    
                data = self.client_socket.recv(BUFFER_SIZE)
                if not data:
                    # Client disconnected
                    self._handle_disconnect()
                    break
                
                buffer += data.decode('utf-8')
                
                # Process complete messages (newline separated)
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
        """Handle client disconnect."""
        with self._lock:
            self.is_connected = False
            if self.client_socket:
                try:
                    self.client_socket.close()
                except Exception:
                    pass
                self.client_socket = None
        
        if self._on_client_disconnect:
            self._on_client_disconnect()
    
    def send_message(self, message: NetworkMessage) -> bool:
        """Send a message to the connected client."""
        if not self.client_socket or not self.is_connected:
            return False
        
        try:
            self.client_socket.sendall(message.to_bytes())
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def send_move(self, row: int, col: int) -> bool:
        """Send a move to the client."""
        from network.protocol import create_move_message
        return self.send_message(create_move_message(row, col))
    
    # Callback setters
    def on_client_connect(self, callback: Callable):
        """Set callback for when a client connects."""
        self._on_client_connect = callback
    
    def on_client_disconnect(self, callback: Callable):
        """Set callback for when a client disconnects."""
        self._on_client_disconnect = callback
    
    def on_move_received(self, callback: Callable[[int, int], None]):
        """Set callback for when a move is received."""
        self._on_move_received = callback
    
    def on_message_received(self, callback: Callable[[NetworkMessage], None]):
        """Set callback for any message received."""
        self._on_message_received = callback
