"""Network protocol for game communication."""

import json
import time
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Any, Optional


class MessageType(Enum):
    """Types of network messages."""
    CONNECT = 'CONNECT'
    MOVE = 'MOVE'
    GAME_STATE = 'GAME_STATE'
    GAME_OVER = 'GAME_OVER'
    DISCONNECT = 'DISCONNECT'
    PING = 'PING'
    PONG = 'PONG'
    ERROR = 'ERROR'


@dataclass
class NetworkMessage:
    """Represents a network message for game communication."""
    msg_type: MessageType
    data: dict
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_json(self) -> str:
        """Serialize message to JSON string."""
        return json.dumps({
            'type': self.msg_type.value,
            'data': self.data,
            'timestamp': self.timestamp
        })
    
    def to_bytes(self) -> bytes:
        """Serialize message to bytes for network transmission."""
        return (self.to_json() + '\n').encode('utf-8')
    
    @classmethod
    def from_json(cls, json_str: str) -> Optional['NetworkMessage']:
        """Deserialize message from JSON string."""
        try:
            obj = json.loads(json_str)
            return cls(
                msg_type=MessageType(obj['type']),
                data=obj.get('data', {}),
                timestamp=obj.get('timestamp', time.time())
            )
        except (json.JSONDecodeError, KeyError, ValueError):
            return None
    
    @classmethod
    def from_bytes(cls, data: bytes) -> Optional['NetworkMessage']:
        """Deserialize message from bytes."""
        try:
            return cls.from_json(data.decode('utf-8').strip())
        except UnicodeDecodeError:
            return None


# Convenience factory methods
def create_connect_message(player_name: str = "Player") -> NetworkMessage:
    """Create a connection message."""
    return NetworkMessage(MessageType.CONNECT, {'player_name': player_name})


def create_move_message(row: int, col: int) -> NetworkMessage:
    """Create a move message."""
    return NetworkMessage(MessageType.MOVE, {'row': row, 'col': col})


def create_game_state_message(board: list, current_player: int, scores: dict) -> NetworkMessage:
    """Create a game state sync message."""
    return NetworkMessage(MessageType.GAME_STATE, {
        'board': board,
        'current_player': current_player,
        'scores': scores
    })


def create_disconnect_message(reason: str = "") -> NetworkMessage:
    """Create a disconnect message."""
    return NetworkMessage(MessageType.DISCONNECT, {'reason': reason})


def create_ping_message() -> NetworkMessage:
    """Create a ping message for connection checking."""
    return NetworkMessage(MessageType.PING, {})


def create_pong_message() -> NetworkMessage:
    """Create a pong response message."""
    return NetworkMessage(MessageType.PONG, {})
