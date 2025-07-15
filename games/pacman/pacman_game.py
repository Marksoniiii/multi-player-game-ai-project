"""
双人吃豆人游戏实现
"""

import numpy as np
import random
from typing import Dict, List, Tuple, Any, Optional
from ..base_game import BaseGame
import config

class PacmanGame(BaseGame):
    """双人吃豆人游戏"""
    
    # 地图元素常量
    EMPTY = 0
    WALL = 1
    DOT = 2
    PLAYER1 = 3
    PLAYER2 = 4
    
    def __init__(self, board_size: int = 21, dots_count: int = 100):
        self.board_size = board_size
        self.width = board_size
        self.height = board_size
        self.dots_count = dots_count
        
        # 游戏配置
        game_config = {
            'board_size': board_size,
            'dots_count': dots_count,
            'max_moves': config.GAME_CONFIGS.get('pacman', {}).get('max_moves', 2000)
        }
        
        # 初始化游戏状态
        self.board = None
        self.player1_pos = None
        self.player2_pos = None
        self.player1_score = 0
        self.player2_score = 0
        self.dots_remaining = 0
        
        super().__init__(game_config)
        self.reset()
    
    def reset(self) -> Dict[str, Any]:
        """重置游戏状态"""
        self.move_count = 0
        self.current_player = 1
        self.player1_score = 0
        self.player2_score = 0
        
        # 创建迷宫地图
        self._create_maze()
        
        # 放置豆子
        self._place_dots()
        
        # 设置玩家初始位置
        self._place_players()
        
        return self.get_state()
    
    def _create_maze(self):
        """创建迷宫地图"""
        # 创建基础迷宫结构
        self.board = np.zeros((self.height, self.width), dtype=int)
        
        # 创建边界墙
        self.board[0, :] = self.WALL
        self.board[-1, :] = self.WALL
        self.board[:, 0] = self.WALL
        self.board[:, -1] = self.WALL
        
        # 创建内部迷宫结构
        for i in range(2, self.height - 2, 2):
            for j in range(2, self.width - 2, 2):
                self.board[i, j] = self.WALL
                
                # 随机创建通道
                if random.random() < 0.7:  # 70%的概率创建通道
                    direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                    ni, nj = i + direction[0], j + direction[1]
                    if 0 < ni < self.height - 1 and 0 < nj < self.width - 1:
                        self.board[ni, nj] = self.WALL
    
    def _place_dots(self):
        """在空地上放置豆子"""
        empty_positions = []
        for i in range(self.height):
            for j in range(self.width):
                if self.board[i, j] == self.EMPTY:
                    empty_positions.append((i, j))
        
        # 随机选择位置放置豆子
        if len(empty_positions) > 0:
            dots_to_place = min(self.dots_count, len(empty_positions))
            dot_positions = random.sample(empty_positions, dots_to_place)
            
            for pos in dot_positions:
                self.board[pos[0], pos[1]] = self.DOT
            
            self.dots_remaining = dots_to_place
    
    def _place_players(self):
        """放置两个玩家在合适的位置，确保其周围有可移动空间"""
        def is_valid(pos):
            r, c = pos
            if self.board[r, c] != self.EMPTY:
                return False
            # 至少有一个相邻空格可移动
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.height and 0 <= nc < self.width and self.board[nr, nc] == self.EMPTY:
                    return True
            return False

        # 生成所有满足条件的位置
        candidates = [(i, j) for i in range(1, self.height - 1) for j in range(1, self.width - 1) if is_valid((i, j))]
        if len(candidates) < 2:
            # 如果候选不足，强制清理固定位置周围的墙壁
            default_positions = [(1, 1), (self.height - 2, self.width - 2)]
            for r, c in default_positions:
                self._clear_surroundings(r, c)
            self.player1_pos, self.player2_pos = default_positions
        else:
            # 随机选择两个距离较远的点
            pos1 = random.choice(candidates)
            pos2 = max(candidates, key=lambda p: abs(p[0] - pos1[0]) + abs(p[1] - pos1[1]))
            self.player1_pos, self.player2_pos = pos1, pos2

        # 确保玩家起始位置没有豆子或墙壁
        self.board[self.player1_pos[0], self.player1_pos[1]] = self.EMPTY
        self.board[self.player2_pos[0], self.player2_pos[1]] = self.EMPTY

    def _clear_surroundings(self, r: int, c: int):
        """清理指定位置及其四邻域的墙壁和豆子"""
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    self.board[nr, nc] = self.EMPTY
    
    def step(self, actions: Dict[int, str]) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """执行一步动作"""
        # 处理两个玩家的动作
        action1 = actions.get(1, 'stay')
        action2 = actions.get(2, 'stay')
        
        # 移动玩家
        old_pos1 = self.player1_pos
        old_pos2 = self.player2_pos
        
        self.player1_pos = self._move_player(self.player1_pos, action1)
        self.player2_pos = self._move_player(self.player2_pos, action2)
        
        # 检查是否收集豆子
        self._check_dot_collection()
        
        # 检查碰撞
        collision = self._check_collision()
        
        # 计算奖励
        reward = self._calculate_reward(old_pos1, old_pos2, collision)
        
        # 更新移动计数
        self.move_count += 1
        
        # 检查游戏是否结束
        done = self.is_terminal()
        
        # 游戏信息
        info = {
            'player1_score': self.player1_score,
            'player2_score': self.player2_score,
            'dots_remaining': self.dots_remaining,
            'collision': collision,
            'winner': self.get_winner()
        }
        
        return self.get_state(), reward, done, info
    
    def _move_player(self, pos: Tuple[int, int], action: str) -> Tuple[int, int]:
        """移动玩家"""
        if not pos:
            return pos
            
        row, col = pos
        
        # 根据动作移动
        if action == 'up':
            new_row = row - 1
            new_col = col
        elif action == 'down':
            new_row = row + 1
            new_col = col
        elif action == 'left':
            new_row = row
            new_col = col - 1
        elif action == 'right':
            new_row = row
            new_col = col + 1
        else:  # stay
            return pos
        
        # 检查边界和墙壁
        if (0 <= new_row < self.height and 0 <= new_col < self.width and 
            self.board[new_row, new_col] != self.WALL):
            return (new_row, new_col)
        else:
            return pos  # 无法移动，保持原位
    
    def _check_dot_collection(self):
        """检查豆子收集 - 只有吃豆人（玩家1）可以收集豆子"""
        if self.player1_pos and self.board[self.player1_pos[0], self.player1_pos[1]] == self.DOT:
            self.board[self.player1_pos[0], self.player1_pos[1]] = self.EMPTY
            self.player1_score += 10
            self.dots_remaining -= 1
        
        # 幽灵（玩家2）不能收集豆子，只能追逐
    
    def _check_collision(self) -> bool:
        """检查玩家碰撞"""
        if self.player1_pos and self.player2_pos:
            return self.player1_pos == self.player2_pos
        return False
    
    def _calculate_reward(self, old_pos1: Tuple[int, int], old_pos2: Tuple[int, int], collision: bool) -> float:
        """计算奖励 - 吃豆人 vs 幽灵"""
        reward = 0.0
        
        # 吃豆人收集豆子的奖励
        if self.player1_pos != old_pos1:
            reward += 1.0  # 吃豆人移动奖励
        
        # 幽灵追逐奖励（距离奖励）
        if self.player1_pos and self.player2_pos:
            # 计算曼哈顿距离
            distance = abs(self.player1_pos[0] - self.player2_pos[0]) + abs(self.player1_pos[1] - self.player2_pos[1])
            if self.player2_pos != old_pos2:
                # 幽灵靠近吃豆人有奖励
                old_distance = abs(old_pos1[0] - old_pos2[0]) + abs(old_pos1[1] - old_pos2[1])
                if distance < old_distance:
                    reward -= 2.0  # 对吃豆人来说是惩罚
        
        # 碰撞 - 幽灵抓到吃豆人
        if collision:
            reward -= 100.0  # 吃豆人被抓到，大惩罚
        
        # 游戏结束奖励
        if self.is_terminal():
            winner = self.get_winner()
            if winner == 1:
                reward += 100.0  # 吃豆人获胜
            elif winner == 2:
                reward -= 100.0  # 幽灵获胜
        
        return reward
    
    def get_valid_actions(self, player: int = None) -> List[str]:
        """获取有效动作列表"""
        return ['up', 'down', 'left', 'right', 'stay']
    
    def is_terminal(self) -> bool:
        """检查游戏是否结束"""
        # 吃豆人吃掉60%及以上豆子
        total_dots = self.dots_count
        collected = total_dots - self.dots_remaining
        if collected / total_dots >= 0.6:
            return True
        # 达到最大移动次数
        if self.move_count >= self.game_config.get('max_moves', 2000):
            return True
        # 玩家碰撞
        if self._check_collision():
            return True
        return False

    def get_winner(self) -> Optional[int]:
        """获取获胜者 - 吃豆人 vs 幽灵规则"""
        if not self.is_terminal():
            return None
        # 如果发生碰撞，幽灵获胜
        if self._check_collision():
            return 2  # 幽灵抓到吃豆人
        # 如果吃豆人吃掉60%及以上豆子，吃豆人获胜
        total_dots = self.dots_count
        collected = total_dots - self.dots_remaining
        if collected / total_dots >= 0.6:
            return 1  # 吃豆人胜利
        # 如果时间到了，根据收集的豆子比例判断
        if self.move_count >= self.game_config.get('max_moves', 2000):
            collected_ratio = collected / total_dots
            if collected_ratio >= 0.6:
                return 1  # 吃豆人胜利
            else:
                return 2  # 幽灵胜利
        return None  # 其他情况平局
    
    def get_state(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        # 创建包含玩家位置的棋盘
        display_board = self.board.copy()
        
        if self.player1_pos:
            display_board[self.player1_pos[0], self.player1_pos[1]] = self.PLAYER1
        if self.player2_pos:
            display_board[self.player2_pos[0], self.player2_pos[1]] = self.PLAYER2
        
        return {
            'board': display_board,
            'raw_board': self.board,
            'player1_pos': self.player1_pos,
            'player2_pos': self.player2_pos,
            'player1_score': self.player1_score,
            'player2_score': self.player2_score,
            'dots_remaining': self.dots_remaining,
            'move_count': self.move_count,
            'current_player': self.current_player
        }
    
    def render(self, mode='human') -> Any:
        """渲染游戏画面"""
        if mode == 'human':
            # 简单的文本输出
            print(f"Player 1 Score: {self.player1_score}, Player 2 Score: {self.player2_score}")
            print(f"Dots Remaining: {self.dots_remaining}")
            print(f"Moves: {self.move_count}")
            
            # 显示棋盘
            display_board = self.get_state()['board']
            symbols = {
                self.EMPTY: ' ',
                self.WALL: '#',
                self.DOT: '.',
                self.PLAYER1: '1',
                self.PLAYER2: '2'
            }
            
            for row in display_board:
                line = ''.join(symbols.get(cell, '?') for cell in row)
                print(line)
            print()
            
        return self.get_state()['board']
    
    def clone(self) -> 'PacmanGame':
        """克隆游戏状态"""
        new_game = PacmanGame(self.board_size, self.dots_count)
        new_game.board = self.board.copy()
        new_game.player1_pos = self.player1_pos
        new_game.player2_pos = self.player2_pos
        new_game.player1_score = self.player1_score
        new_game.player2_score = self.player2_score
        new_game.dots_remaining = self.dots_remaining
        new_game.move_count = self.move_count
        new_game.current_player = self.current_player
        return new_game
    
    def get_action_space(self) -> List[str]:
        """获取动作空间"""
        return ['up', 'down', 'left', 'right', 'stay']
    
    def get_observation_space(self) -> Tuple[int, int]:
        """获取观察空间"""
        return (self.height, self.width) 