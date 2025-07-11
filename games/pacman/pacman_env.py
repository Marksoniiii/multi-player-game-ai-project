"""
吃豆人游戏环境
提供gym风格的接口
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from ..base_env import BaseEnv
from .pacman_game import PacmanGame

class PacmanEnv(BaseEnv):
    """吃豆人游戏环境"""
    
    def __init__(self, board_size: int = 21, dots_count: int = 100):
        # 先存储游戏参数
        self.board_size = board_size
        self.dots_count = dots_count
        
        # 创建游戏实例
        game = PacmanGame(board_size, dots_count)
        super().__init__(game)
    
    def _setup_spaces(self) -> None:
        """设置观察空间和动作空间"""
        # 动作空间：上下左右和停留
        self.action_space = ['up', 'down', 'left', 'right', 'stay']
        
        # 观察空间：2D网格，包含墙壁、豆子、玩家位置
        self.observation_space = (self.board_size, self.board_size)
    
    def _get_observation(self) -> np.ndarray:
        """获取观察"""
        state = self.game.get_state()
        return state['board']
    
    def _get_action_mask(self) -> np.ndarray:
        """获取动作掩码"""
        # 所有动作都是有效的（游戏内部会处理边界检查）
        return np.ones(len(self.action_space), dtype=bool)
    
    def reset(self) -> Tuple[np.ndarray, Dict[str, Any]]:
        """重置环境"""
        self.game.reset()
        observation = self._get_observation()
        
        # 获取游戏信息
        state = self.game.get_state()
        info = {
            'player1_score': state['player1_score'],
            'player2_score': state['player2_score'],
            'dots_remaining': state['dots_remaining'],
            'move_count': state['move_count'],
            'player1_pos': state['player1_pos'],
            'player2_pos': state['player2_pos']
        }
        
        return observation, info
    
    def step(self, actions: Dict[int, str]) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """执行动作"""
        # 验证动作
        for player, action in actions.items():
            if action not in self.action_space:
                return (
                    self._get_observation(),
                    -1000,
                    True,
                    False,
                    {'error': f'Invalid action {action} for player {player}'}
                )
        
        # 执行动作
        state, reward, done, info = self.game.step(actions)
        
        # 更新游戏状态
        self.game.update_game_state()
        
        # 获取新的观察
        observation = self._get_observation()
        
        # 检查是否超时
        truncated = self.game.is_timeout()
        
        return observation, reward, done, truncated, info
    
    def render(self, mode='human') -> Optional[np.ndarray]:
        """渲染环境"""
        return self.game.render(mode)
    
    def get_valid_actions(self, player: int = None) -> List[str]:
        """获取有效动作"""
        return self.action_space
    
    def get_state(self) -> Dict[str, Any]:
        """获取完整状态"""
        return self.game.get_state()
    
    def get_game_info(self) -> Dict[str, Any]:
        """获取游戏信息"""
        state = self.game.get_state()
        return {
            'player1_score': state['player1_score'],
            'player2_score': state['player2_score'],
            'dots_remaining': state['dots_remaining'],
            'move_count': state['move_count'],
            'winner': self.game.get_winner(),
            'game_state': self.game.game_state,
            'is_terminal': self.game.is_terminal()
        } 