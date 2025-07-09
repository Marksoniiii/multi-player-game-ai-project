"""
五子棋游戏逻辑
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from games.base_game import BaseGame
import config


class GomokuGame(BaseGame):
    """五子棋游戏"""
    
    def __init__(self, board_size: int = 15, win_length: int = 5, **kwargs):
        self.board_size = board_size
        self.win_length = win_length
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        super().__init__({'board_size': board_size, 'win_length': win_length})
    
    def reset(self) -> Dict[str, Any]:
        """重置游戏状态"""
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = 1
        self.game_state = config.GameState.ONGOING
        self.move_count = 0
        self.history = []
        
        return self.get_state()
    
    def step(self, action: Tuple[int, int]) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """
        执行一步动作
        
        Args:
            action: (row, col) 坐标
            
        Returns:
            observation: 观察状态
            reward: 奖励
            done: 是否结束
            info: 额外信息
        """
        row, col = action
        
        if self.board[row, col] != 0:
            return self.get_state(), -1, True, {'error': 'Invalid move'}
        
        # 记录当前玩家并落子
        player_who_moved = self.current_player
        self.board[row, col] = player_who_moved
        self.history.append((player_who_moved, (row, col)))
        self.move_count += 1
        
        # **核心修复**：在切换玩家之前，先基于当前落子的玩家检查游戏是否结束
        done = self.is_terminal()
        winner = self.get_winner()
        
        # 根据实际获胜者计算奖励
        if winner == player_who_moved:
            reward = 1.0
        elif done and winner is None: # 平局
            reward = 0.5
        else:
            reward = 0.0
            
        info = {'winner': winner}

        # 如果游戏没有结束，才切换玩家
        if not done:
            self.switch_player()
        
        return self.get_state(), reward, done, info
    
    def get_valid_actions(self, player: int = None) -> List[Tuple[int, int]]:
        """获取有效动作列表"""
        return [(i, j) for i in range(self.board_size) for j in range(self.board_size) if self.board[i, j] == 0]
    
    def is_terminal(self) -> bool:
        """检查游戏是否结束"""
        return self.get_winner() is not None or self.move_count >= self.board_size * self.board_size
    
    def get_winner(self) -> Optional[int]:
        """获取获胜者"""
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i, j] == 0:
                    continue
                player = self.board[i, j]
                for dx, dy in [(1,0),(0,1),(1,1),(1,-1)]:
                    count = 1
                    for k in range(1, self.win_length):
                        x, y = i+dx*k, j+dy*k
                        if 0<=x<self.board_size and 0<=y<self.board_size and self.board[x, y]==player:
                            count += 1
                        else:
                            break
                    if count >= self.win_length:
                        return player
        return None
    
    def get_state(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        return {
            'board': self.board.copy(),
            'current_player': self.current_player,
            'game_state': self.game_state,
            'move_count': self.move_count
        }
    
    def render(self) -> np.ndarray:
        """渲染游戏画面"""
        return self.board.copy()
    
    def clone(self) -> 'GomokuGame':
        """克隆游戏状态"""
        import copy
        new_game = GomokuGame(self.board_size, self.win_length)
        new_game.board = self.board.copy()
        new_game.current_player = self.current_player
        new_game.game_state = self.game_state
        new_game.move_count = self.move_count
        new_game.history = copy.deepcopy(self.history)
        return new_game
    
    def get_action_space(self):
        """获取动作空间"""
        return [(i, j) for i in range(self.board_size) for j in range(self.board_size)]
    
    def get_observation_space(self):
        """获取观察空间"""
        return {
            'board': (self.board_size, self.board_size),
            'current_player': 1,
            'valid_actions': []
        }
    
    def _is_valid_action(self, action: Tuple[int, int]) -> bool:
        """检查动作是否有效"""
        row, col = action
        return (0 <= row < self.board_size and 
                0 <= col < self.board_size and 
                self.board[row, col] == 0)
    
    def _check_win(self, row: int, col: int, player: int) -> bool:
        """检查是否获胜"""
        directions = [
            [(0, 1), (0, -1)],   # 水平
            [(1, 0), (-1, 0)],   # 垂直
            [(1, 1), (-1, -1)],  # 主对角线
            [(1, -1), (-1, 1)]   # 副对角线
        ]
        
        for dir_pair in directions:
            count = 1  # 当前位置算一个
            
            for dr, dc in dir_pair:
                r, c = row + dr, col + dc
                while (0 <= r < self.board_size and 
                       0 <= c < self.board_size and 
                       self.board[r, c] == player):
                    count += 1
                    r += dr
                    c += dc
            
            if count >= self.win_length:
                return True
        
        return False
    
    def _is_board_full(self) -> bool:
        """检查棋盘是否已满"""
        return np.all(self.board != 0)
    
    def get_board_string(self) -> str:
        """获取棋盘字符串表示"""
        symbols = {0: '.', 1: 'X', 2: 'O'}
        board_str = ""
        
        # 添加列标号
        board_str += "   " + " ".join([f"{i:2d}" for i in range(self.board_size)]) + "\n"
        
        for i in range(self.board_size):
            board_str += f"{i:2d} "
            for j in range(self.board_size):
                board_str += f" {symbols[self.board[i, j]]}"
            board_str += "\n"
        
        return board_str
    
    def print_board(self):
        """打印棋盘"""
        print(self.get_board_string())
    
    def get_legal_moves(self) -> List[Tuple[int, int]]:
        """获取合法移动（别名）"""
        return self.get_valid_actions()