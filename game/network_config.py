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

# Multiplayer text (Arabic)
MULTIPLAYER_BUTTON_TEXT = 'متعدد اللاعبين'
HOST_GAME_TEXT = 'استضافة لعبة'
JOIN_GAME_TEXT = 'الانضمام للعبة'
WAITING_TEXT = 'في انتظار لاعب...'
CONNECTED_TEXT = 'متصل!'
CONNECTION_FAILED_TEXT = 'فشل الاتصال'
YOUR_TURN_TEXT = "دورك"
OPPONENT_TURN_TEXT = "دور الخصم"
ENTER_IP_TEXT = 'أدخل عنوان IP:'
REFRESH_TEXT = 'تحديث'
CANCEL_TEXT = 'إلغاء'
CONNECT_TEXT = 'اتصال'
BACK_TEXT = 'رجوع'
YOUR_IP_TEXT = 'عنوان IP الخاص بك: '
PLAYER_CONNECTED_TEXT = 'اللاعب متصل!'
PLAYER_DISCONNECTED_TEXT = 'اللاعب قطع الاتصال'

# Connection status colors
STATUS_CONNECTED_COLOR = '#00FF00'  # Green
STATUS_DISCONNECTED_COLOR = '#FF0000'  # Red
STATUS_WAITING_COLOR = '#FFAA00'  # Orange/Yellow
