# 文件路径: games/snake/snake_game.py
import numpy as np
import random
from typing import Dict, List, Tuple, Any, Optional
from ..base_game import BaseGame
import config

class SnakeGame(BaseGame):
    """双人贪吃蛇游戏 - 最终修复版 (已添加render方法)"""

    def __init__(self, board_size: int = 20, initial_length: int = 3, food_count: int = 5):
        self.board_size = board_size
        self.width = board_size
        self.height = board_size
        self.board_shape = (self.width, self.height)
        self.initial_length = initial_length
        self.food_count = food_count
        game_config = {
            'board_size': board_size,
            'initial_length': initial_length,
            'food_count': food_count,
            'max_moves': config.GAME_CONFIGS['snake'].get('max_moves', 1000)
        }
        super().__init__(game_config)
        self.reset()

    def reset(self) -> Dict[str, Any]:
        """重置游戏状态，确保蛇的初始位置和方向正确"""
        center_y = self.height // 2
        
        start_x1 = self.width // 4
        self.snake1 = [(center_y, start_x1 - i) for i in range(self.initial_length)]
        self.direction1 = (0, 1)

        start_x2 = self.width * 3 // 4
        self.snake2 = [(center_y, start_x2 + i) for i in range(self.initial_length)]
        self.direction2 = (0, -1)
        
        self.foods = []
        self._generate_foods()
        
        self.alive1 = True
        self.alive2 = True
        self.move_count = 0
        
        return self.get_state()

    def step(self, actions: Dict[int, Tuple[int, int]]) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """执行一步动作，同时处理两个玩家"""
        action1 = actions.get(1, self.direction1)
        action2 = actions.get(2, self.direction2)

        if action1 and action1 != (-self.direction1[0], -self.direction1[1]):
            self.direction1 = action1
        if action2 and action2 != (-self.direction2[0], -self.direction2[1]):
            self.direction2 = action2
        
        new_head1 = (self.snake1[0][0] + self.direction1[0], self.snake1[0][1] + self.direction1[1])
        new_head2 = (self.snake2[0][0] + self.direction2[0], self.snake2[0][1] + self.direction2[1])

        p1_collided = self._is_collision(new_head1, self.snake1, self.snake2)
        p2_collided = self._is_collision(new_head2, self.snake2, self.snake1)

        if new_head1 == new_head2:
            self.alive1, self.alive2 = False, False
        else:
            if p1_collided: self.alive1 = False
            if p2_collided: self.alive2 = False

        if self.alive1:
            self.snake1.insert(0, new_head1)
            if new_head1 in self.foods:
                self.foods.remove(new_head1)
                self._generate_foods()
            else:
                self.snake1.pop()

        if self.alive2:
            self.snake2.insert(0, new_head2)
            if new_head2 in self.foods:
                self.foods.remove(new_head2)
                self._generate_foods()
            else:
                self.snake2.pop()

        self.move_count += 1
        done = self.is_terminal()
        reward = self._calculate_reward()
        info = {'winner': self.get_winner()}
        
        return self.get_state(), reward, done, info

    def _is_collision(self, head: Tuple[int, int], self_snake: List[Tuple[int, int]], other_snake: List[Tuple[int, int]]) -> bool:
        r, c = head
        return not (0 <= r < self.height and 0 <= c < self.width) or head in self_snake or head in other_snake

    def get_valid_actions(self, player: int = None) -> List[Tuple[int, int]]:
        return [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def is_terminal(self) -> bool:
        return not self.alive1 or not self.alive2 or self.move_count >= self.game_config.get('max_moves', 1000)

    def get_winner(self) -> Optional[int]:
        if not self.is_terminal(): return None
        if self.alive1 and not self.alive2: return 1
        if self.alive2 and not self.alive1: return 2
        if not self.alive1 and not self.alive2:
            if len(self.snake1) > len(self.snake2): return 1
            if len(self.snake2) > len(self.snake1): return 2
            return -1
        return None

    def get_state(self) -> Dict[str, Any]:
        board = np.zeros(self.board_shape, dtype=int)
        for x, y in self.foods: board[x, y] = 5
        for i, (x, y) in enumerate(self.snake1): board[x, y] = 1 if i == 0 and self.alive1 else 2
        for i, (x, y) in enumerate(self.snake2): board[x, y] = 3 if i == 0 and self.alive2 else 4
        return {
            'board': board,
            'snake1': self.snake1, 'snake2': self.snake2,
            'direction1': self.direction1, 'direction2': self.direction2,
            'foods': self.foods, 'alive1': self.alive1, 'alive2': self.alive2,
            'move_count': self.move_count
        }

    def _generate_foods(self):
        occupied = set(self.snake1) | set(self.snake2) | set(self.foods)
        while len(self.foods) < self.food_count:
            pos = (random.randint(0, self.height - 1), random.randint(0, self.width - 1))
            if pos not in occupied:
                self.foods.append(pos)
                occupied.add(pos)
    
    def _calculate_reward(self):
        winner = self.get_winner()
        if winner == 1: return 1.0
        if winner == 2: return -1.0
        return 0.0
        
    # ===============================================================
    # vv 【已修复】 vv 添加回被误删的 render 方法以符合基类要求
    # ===============================================================
    def render(self, mode='human') -> np.ndarray:
        """
        此方法为满足基类要求而实现。
        实际的渲染由 snake_gui.py 处理。
        """
        return self.get_state()['board']
    # ===============================================================