"""
游戏模块
统一导出所有基础环境和游戏基类，便于主程序import。
"""

from .base_game import BaseGame
from .base_env import BaseEnv
from .pacman import PacmanGame, PacmanEnv
from .chess import ChessGame, ChessEnv
from .idiom_guessing import IdiomGuessingGame, IdiomGuessingEnv

__all__ = ['BaseGame', 'BaseEnv', 'PacmanGame', 'PacmanEnv', 'ChessGame', 'ChessEnv', 'IdiomGuessingGame', 'IdiomGuessingEnv']