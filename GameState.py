from enum import Enum, auto

class GameState(Enum):
    MAIN_MENU = auto()
    MAIN_GAME = auto()
    MAIN_GAME_PAUSED = auto()
    LEADERBOARD = auto()
    GAME_OVER = auto()
    GAME_OVER_DATABASE_UPLOAD = auto()