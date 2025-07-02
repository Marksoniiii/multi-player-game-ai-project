"""
贪吃蛇游戏逻辑（简化版）
"""

import numpy as np
import random
from typing import Dict, List, Tuple, Any, Optional
from ..base_game import BaseGame
import config


class SnakeGame(BaseGame):
    """双人贪吃蛇游戏"""
    
    def __init__(self, board_size: int = 20, initial_length: int = 3, food_count: int = 5):
        self.board_size = board_size  # 必须在super之前赋值
        self.width = board_size
        self.height = board_size
        self.board_shape = (self.width, self.height)
        self.initial_length = initial_length
        self.food_count = food_count
        game_config = {
            'board_size': board_size,
            'initial_length': initial_length,
            'food_count': food_count,
            'timeout': config.GAME_CONFIGS['snake']['timeout'],
            'max_moves': config.GAME_CONFIGS['snake']['max_moves']
        }
        super().__init__(game_config)
        
        # 蛇的位置和方向
        self.snake1 = []  # 玩家1的蛇
        self.snake2 = []  # 玩家2的蛇
        self.direction1 = (0, 1)  # 玩家1的方向
        self.direction2 = (0, -1)  # 玩家2的方向
        
        # 食物位置
        self.foods = []
        
        # 游戏状态
        self.alive1 = True
        self.alive2 = True
        
        self.reset()
    
    def reset(self) -> Dict[str, Any]:
        """重置游戏状态"""
        # 初始化蛇的位置
        center = self.board_size // 2
        self.snake1 = [(center, center - 2)]
        self.snake2 = [(center, center + 2)]
        
        # 初始化方向
        self.direction1 = (0, 1)  # 向右
        self.direction2 = (0, -1)  # 向左
        
        # 初始化食物
        self.foods = []
        self._generate_foods()
        
        # 重置游戏状态
        self.alive1 = True
        self.alive2 = True
        self.current_player = 1
        self.game_state = config.GameState.ONGOING
        self.move_count = 0
        self.history = []
        
        return self.get_state()
    
    def step(self, action: Tuple[int, int]) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """
        执行一步动作
        
        Args:
            action: (dx, dy) 方向向量
            
        Returns:
            observation: 观察状态
            reward: 奖励
            done: 是否结束
            info: 额外信息
        """
        # 更新方向
        if self.current_player == 1:
            self.direction1 = action
        else:
            self.direction2 = action
        
        # 移动蛇
        if self.current_player == 1 and self.alive1:
            self._move_snake(1)
        elif self.current_player == 2 and self.alive2:
            self._move_snake(2)
        
        # 检查游戏结束条件
        done = self._check_game_over()
        
        # 计算奖励
        reward = self._calculate_reward()
        
        # 获取观察状态
        observation = self.get_state()
        
        # 额外信息
        info = {
            'snake1_length': len(self.snake1),
            'snake2_length': len(self.snake2),
            'food_count': len(self.foods),
            'alive1': self.alive1,
            'alive2': self.alive2
        }
        
        return observation, reward, done, info
    
    def get_valid_actions(self, player: int = None) -> List[Tuple[int, int]]:
        """获取有效动作列表"""
        # 四个方向：上、下、左、右
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        if player is None:
            player = self.current_player
        
        # 过滤掉反向移动
        current_direction = self.direction1 if player == 1 else self.direction2
        valid_directions = []
        
        for direction in directions:
            if direction != (-current_direction[0], -current_direction[1]):
                valid_directions.append(direction)
        
        return valid_directions
    
    def is_terminal(self) -> bool:
        """检查游戏是否结束"""
        return not (self.alive1 or self.alive2)
    
    def get_winner(self) -> Optional[int]:
        """获取获胜者"""
        if not self.is_terminal():
            return None
        
        if self.alive1 and not self.alive2:
            return 1
        elif self.alive2 and not self.alive1:
            return 2
        else:
            return None  # 平局
    
    def get_state(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        board = np.zeros(self.board_shape, dtype=int)  # 使用self.board_shape
        
        # 绘制蛇1
        for i, (x, y) in enumerate(self.snake1):
            if 0 <= x < self.board_size and 0 <= y < self.board_size:
                board[x, y] = 1 if i == 0 else 2  # 头部为1，身体为2
        
        # 绘制蛇2
        for i, (x, y) in enumerate(self.snake2):
            if 0 <= x < self.board_size and 0 <= y < self.board_size:
                board[x, y] = 3 if i == 0 else 4  # 头部为3，身体为4
        
        # 绘制食物
        for x, y in self.foods:
            if 0 <= x < self.board_size and 0 <= y < self.board_size:
                board[x, y] = 5
        
        return {
            'board': board,
            'snake1': self.snake1.copy(),
            'snake2': self.snake2.copy(),
            'foods': self.foods.copy(),
            'direction1': self.direction1,
            'direction2': self.direction2,
            'alive1': self.alive1,
            'alive2': self.alive2,
            'current_player': self.current_player,
            'valid_actions': self.get_valid_actions(),
            'game_state': self.game_state,
            'move_count': self.move_count
        }
    
    def render(self) -> np.ndarray:
        """渲染游戏画面"""
        state = self.get_state()
        return state['board']
    
    def clone(self) -> 'SnakeGame':
        """克隆游戏状态"""
        cloned_game = SnakeGame(self.board_size, self.initial_length, self.food_count)
        cloned_game.snake1 = self.snake1.copy()
        cloned_game.snake2 = self.snake2.copy()
        cloned_game.direction1 = self.direction1
        cloned_game.direction2 = self.direction2
        cloned_game.foods = self.foods.copy()
        cloned_game.alive1 = self.alive1
        cloned_game.alive2 = self.alive2
        cloned_game.current_player = self.current_player
        cloned_game.game_state = self.game_state
        cloned_game.move_count = self.move_count
        cloned_game.history = self.history.copy()
        return cloned_game
    
    def get_action_space(self):
        """获取动作空间"""
        return [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    def get_observation_space(self):
        """获取观察空间"""
        return {
            'board': self.board_shape,
            'snake1': [],
            'snake2': [],
            'foods': []
        }
    
    def _move_snake(self, player: int):
        """移动蛇"""
        if player == 1:
            snake = self.snake1
            direction = self.direction1
            alive = self.alive1
        else:
            snake = self.snake2
            direction = self.direction2
            alive = self.alive2
        
        if not alive:
            return
        
        # 计算新头部位置
        head = snake[0]
        new_head = (head[0] + direction[0], head[1] + direction[1])
        
        # 检查边界碰撞
        if (new_head[0] < 0 or new_head[0] >= self.board_size or
            new_head[1] < 0 or new_head[1] >= self.board_size):
            if player == 1:
                self.alive1 = False
            else:
                self.alive2 = False
            return
        
        # 检查自身碰撞
        if new_head in snake:
            if player == 1:
                self.alive1 = False
            else:
                self.alive2 = False
            return
        
        # 检查与对方蛇的碰撞
        other_snake = self.snake2 if player == 1 else self.snake1
        if new_head in other_snake:
            if player == 1:
                self.alive1 = False
            else:
                self.alive2 = False
            return
        
        # 移动蛇
        snake.insert(0, new_head)
        
        # 检查是否吃到食物
        if new_head in self.foods:
            self.foods.remove(new_head)
            self._generate_foods()
        else:
            snake.pop()
    
    def _generate_foods(self):
        """生成食物"""
        while len(self.foods) < self.food_count:
            x = random.randint(0, self.board_size - 1)
            y = random.randint(0, self.board_size - 1)
            pos = (x, y)
            
            # 确保食物不在蛇身上
            if pos not in self.snake1 and pos not in self.snake2 and pos not in self.foods:
                self.foods.append(pos)
    
    def _check_game_over(self) -> bool:
        """检查游戏是否结束"""
        return not (self.alive1 or self.alive2)
    
    def _calculate_reward(self) -> float:
        """计算奖励"""
        if self.current_player == 1:
            if not self.alive1:
                return -1.0
            elif not self.alive2:
                return 1.0
        else:
            if not self.alive2:
                return -1.0
            elif not self.alive1:
                return 1.0
        
        return 0.0