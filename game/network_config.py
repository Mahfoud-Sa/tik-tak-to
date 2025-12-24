# Network configuration
DEFAULT_PORT = 5555
CONNECTION_TIMEOUT = 30  # seconds
BUFFER_SIZE = 4096
RECONNECT_CHECK_INTERVAL = 1000  # milliseconds

# Message types
MSG_CONNECT = 'CONNECT'
MSG_MOVE = 'MOVE'
MSG_GAME_STATE = 'GAME_STATE'
MSG_DISCONNECT = 'DISCONNECT'
MSG_PING = 'PING'
MSG_PONG = 'PONG'

# Multiplayer text
MULTIPLAYER_BUTTON_TEXT = 'Multiplayer'
HOST_GAME_TEXT = 'Host Game'
JOIN_GAME_TEXT = 'Join Game'
WAITING_TEXT = 'Waiting for player...'
CONNECTED_TEXT = 'Connected!'
CONNECTION_FAILED_TEXT = 'Connection failed'
YOUR_TURN_TEXT = "Your Turn"
OPPONENT_TURN_TEXT = "Opponent's Turn"
ENTER_IP_TEXT = 'Enter Host IP:'
REFRESH_TEXT = 'Refresh'
CANCEL_TEXT = 'Cancel'
CONNECT_TEXT = 'Connect'
BACK_TEXT = 'Back'
YOUR_IP_TEXT = 'Your IP: '
PLAYER_CONNECTED_TEXT = 'Player Connected!'
PLAYER_DISCONNECTED_TEXT = 'Player Disconnected'

# Connection status colors
STATUS_CONNECTED_COLOR = '#00FF00'  # Green
STATUS_DISCONNECTED_COLOR = '#FF0000'  # Red
STATUS_WAITING_COLOR = '#FFAA00'  # Orange/Yellow
