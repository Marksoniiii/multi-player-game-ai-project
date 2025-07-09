# 文件路径: games/snake/snake_env.py
from typing import Any, Dict, Tuple, Optional
import gymnasium as gym
from gymnasium import spaces
from .snake_game import SnakeGame

class SnakeEnv(gym.Env):
    """贪吃蛇游戏环境 - 最终修复版"""

    def __init__(self, board_size=20):
        super(SnakeEnv, self).__init__()
        self.game = SnakeGame(board_size=board_size)
        self.board_size = board_size
        self.action_space = spaces.Discrete(4)  # 0:Up, 1:Down, 2:Left, 3:Right
        self.observation_space = spaces.Box(low=0, high=5, shape=(self.board_size, self.board_size), dtype=int)

    def reset(self, seed=None, options=None) -> Tuple[Dict, Dict]:
        if seed is not None:
            super().reset(seed=seed)
        obs = self.game.reset()
        return obs, {}

    def step(self, actions: Dict[int, Tuple[int, int]]) -> Tuple[Dict, float, bool, bool, Dict]:
        """
        兼容旧接口：如果actions是tuple，则自动转为{1: actions}
        """
        if isinstance(actions, tuple):
            actions = {1: actions}
        obs, reward, terminated, info = self.game.step(actions)
        truncated = self.game.move_count >= self.game.game_config.get('max_moves', 1000)
        return obs, reward, terminated, truncated, info

    def render(self, mode='human'):
        # 渲染功能由 GUI 直接处理
        pass

    def close(self):
        pass

    def get_winner(self) -> Optional[int]:
        return self.game.get_winner()

    def _get_observation(self):
        """兼容旧接口，返回当前观测"""
        return self.game.get_state()

    def get_valid_actions(self, player: int = None):
        """兼容旧接口，返回可用动作"""
        return self.game.get_valid_actions(player)