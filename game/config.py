# Configuration constants for X/O Game

# =============================================================================
# GAME LOGIC CONSTANTS
# =============================================================================
BOARD_SIZE = 3
MAX_MOVES = 9
PLAYER_O = 0
PLAYER_X = 1
SYMBOL_O = 'o'
SYMBOL_X = 'x'
EMPTY_CELL = 0

# =============================================================================
# UI LAYOUT CONSTANTS
# =============================================================================
CANVAS_WIDTH = 600
DRAWING_CANVAS_HEIGHT = 300
GAME_CANVAS_HEIGHT = 30

# Grid line coordinates
GRID_VERTICAL_LEFT = 250
GRID_VERTICAL_RIGHT = 350
GRID_HORIZONTAL_TOP = 90
GRID_HORIZONTAL_BOTTOM = 170
GRID_START_X = 170
GRID_END_X = 450
GRID_START_Y = 30
GRID_END_Y = 240
GRID_LINE_WIDTH = 5

# Cell positioning
CELL_SIZE = 100
CELL_OFFSET_X = 200
CELL_OFFSET_Y = 30

# =============================================================================
# DRAWING CONSTANTS
# =============================================================================
SYMBOL_RADIUS = 15
X_LINE_WIDTH = 20
O_LINE_WIDTH = 10
MIN_RADIUS = 1
MAX_RADIUS = 40
RADIUS_STEP = 10
MIN_WIDTH = 15
MAX_WIDTH = 30
WIDTH_STEP = 5
MIN_POSITION = 10
MAX_POSITION = 600

# =============================================================================
# COLOR CONSTANTS
# =============================================================================
DEFAULT_BACKGROUND = 'cyan'
DEFAULT_GRID = 'gray'

# Drawing colors
DRAWING_COLORS = [
    'cyan', 'green', 'brown', 'gray', 'dark gray', 
    'orange', 'purple'
]

# X/O symbol colors
SYMBOL_COLORS = [
    'dark grey', 'red', 'black', 'yellow', 'white', 'blue'
]

# Color themes (background, grid)
COLOR_THEMES = [
    ('cyan', 'gray'),
    ('gray', 'cyan'),
    ('gray', 'orange'),
    ('orange', 'gray'),
    ('orange', 'green'),
    ('green', 'orange'),
    ('gray', 'brown'),
    ('brown', 'gray'),
    ('purple', 'gray'),
    ('gray', 'purple')
]

# =============================================================================
# TIMING CONSTANTS
# =============================================================================
COMPUTER_MOVE_DELAY = 300  # milliseconds
O_WIN_DELAY = 1000  # milliseconds
X_WIN_DELAY = 600  # milliseconds
UI_SETUP_DELAY = 40  # milliseconds

# =============================================================================
# TEXT CONSTANTS
# =============================================================================
WINDOW_TITLE = 'X/O Game'
PLAY_BUTTON_TEXT = 'Play'
EXIT_BUTTON_TEXT = 'Exit'
COMPUTER_MODE_TEXT = 'Play with computer'
CHANGE_THEME_TEXT = 'Change Theme'
ABOUT_TEXT = 'About'
EXIT_MENU_TEXT = 'Exit'
HELP_MENU_TEXT = 'Help'

# About dialog
ABOUT_TITLE = 'About X/O Game'
ABOUT_MESSAGE = 'A simple Tic-Tac-Toe game\nDeveloped by Eng. Mahfoud Mohammed Binsabbah\n2020'
FEEDBACK_TITLE = 'Feedback'
FEEDBACK_MESSAGE = 'Do you like this game?\nGive me a star on GitHub repository!'

# =============================================================================
# FONT CONSTANTS
# =============================================================================
TITLE_FONT = ('Arial', 14)
BUTTON_FONT = ('Arial', 10)

# =============================================================================
# GRID CLICK AREA CONSTANTS
# =============================================================================
# Row click areas
TOP_ROW_MIN_Y = 30
TOP_ROW_MAX_Y = 85
MIDDLE_ROW_MIN_Y = 90
MIDDLE_ROW_MAX_Y = 160
BOTTOM_ROW_MIN_Y = 150
BOTTOM_ROW_MAX_Y = 220

# Column click areas
LEFT_COL_MIN_X = 170
LEFT_COL_MAX_X = 245
MIDDLE_COL_MIN_X = 250
MIDDLE_COL_MAX_X = 345
RIGHT_COL_MIN_X = 350
RIGHT_COL_MAX_X = 445

# Theme change click areas
THEME_CHANGE_Y_THRESHOLD = 250
GRID_LINE_CLICK_RANGE = 5

# =============================================================================
# THEME CONSTANTS
# =============================================================================
NUM_THEMES = 10
DEFAULT_THEME_INDEX = 1

# =============================================================================
# FILE PATH CONSTANTS
# =============================================================================
ICON_PATH = 'assets/icons/icon.png'

# =============================================================================
# URL CONSTANTS
# =============================================================================
GITHUB_URL = 'https://github.com/Mahfoud-Sa/XO_Game.git'

# =============================================================================
# LAYOUT CONSTANTS
# =============================================================================
INITIAL_SHAPES_COUNT = 20
LABEL_PADDING_X = 20
LABEL_PADDING_Y = 3
BUTTON_PADDING_X = 9

# =============================================================================
# GAME STATE CONSTANTS
# =============================================================================
# Corner positions for computer AI
CORNER_POSITIONS = [(0, 0), (0, 2), (2, 0), (2, 2)]

# =============================================================================
# MENU CONSTANTS
# =============================================================================
MENU_TEAROFF = 0
