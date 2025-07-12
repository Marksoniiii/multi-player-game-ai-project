"""
吃豆人游戏专用AI实现
"""

import random
from typing import Dict, List, Tuple, Any
from agents.base_agent import BaseAgent
from games.pacman.pacman_game import PacmanGame

class PacmanAI(BaseAgent):
    """吃豆人AI - 专注于收集豆子并避开幽灵"""
    
    def __init__(self, player_id: int = 1):
        super().__init__()
        self.player_id = player_id
        self.name = f"吃豆人AI_{player_id}"
    
    def get_action(self, observation: Dict[str, Any], env) -> str:
        """获取吃豆人的动作"""
        state = observation
        board = state.get('board')
        player_pos = state.get('player1_pos') if self.player_id == 1 else state.get('player2_pos')
        ghost_pos = state.get('player2_pos') if self.player_id == 1 else state.get('player1_pos')
        
        if not player_pos:
            return 'stay'
        
        # 获取所有可能的动作
        valid_actions = ['up', 'down', 'left', 'right', 'stay']
        safe_actions = []
        
        # 计算每个动作的安全性和收益
        action_scores = {}
        
        for action in valid_actions:
            new_pos = self._get_new_position(player_pos, action)
            
            # 检查是否可以移动到新位置
            if not self._is_valid_position(new_pos, board):
                continue
                
            score = 0
            
            # 避开幽灵
            if ghost_pos:
                ghost_distance = self._manhattan_distance(new_pos, ghost_pos)
                if ghost_distance <= 1:
                    score -= 100  # 太危险
                elif ghost_distance <= 2:
                    score -= 50   # 有风险
                else:
                    score += ghost_distance  # 越远越好
            
            # 追逐豆子
            nearest_dot = self._find_nearest_dot(new_pos, board)
            if nearest_dot:
                dot_distance = self._manhattan_distance(new_pos, nearest_dot)
                score += 100 - dot_distance  # 越接近豆子越好
            
            # 检查这个位置是否有豆子
            if board[new_pos[0], new_pos[1]] == PacmanGame.DOT:
                score += 200  # 直接吃到豆子
            
            action_scores[action] = score
            if score > -50:  # 不是太危险的动作
                safe_actions.append(action)
        
        # 选择最佳动作
        if action_scores:
            best_action = max(action_scores, key=action_scores.get)
            return best_action
        
        return 'stay'
    
    def _get_new_position(self, pos: Tuple[int, int], action: str) -> Tuple[int, int]:
        """根据动作计算新位置"""
        row, col = pos
        if action == 'up':
            return (row - 1, col)
        elif action == 'down':
            return (row + 1, col)
        elif action == 'left':
            return (row, col - 1)
        elif action == 'right':
            return (row, col + 1)
        else:
            return pos
    
    def _is_valid_position(self, pos: Tuple[int, int], board) -> bool:
        """检查位置是否有效"""
        row, col = pos
        if row < 0 or row >= board.shape[0] or col < 0 or col >= board.shape[1]:
            return False
        return board[row, col] != PacmanGame.WALL
    
    def _manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """计算曼哈顿距离"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _find_nearest_dot(self, pos: Tuple[int, int], board) -> Tuple[int, int]:
        """找到最近的豆子"""
        min_distance = float('inf')
        nearest_dot = None
        
        for row in range(board.shape[0]):
            for col in range(board.shape[1]):
                if board[row, col] == PacmanGame.DOT:
                    distance = self._manhattan_distance(pos, (row, col))
                    if distance < min_distance:
                        min_distance = distance
                        nearest_dot = (row, col)
        
        return nearest_dot


class GhostAI(BaseAgent):
    """幽灵AI - 专注于追逐吃豆人"""
    
    def __init__(self, player_id: int = 2):
        super().__init__()
        self.player_id = player_id
        self.name = f"幽灵AI_{player_id}"
        self.last_pacman_pos = None
        self.patrol_target = None
    
    def get_action(self, observation: Dict[str, Any], env) -> str:
        """获取幽灵的动作"""
        state = observation
        board = state.get('board')
        ghost_pos = state.get('player2_pos') if self.player_id == 2 else state.get('player1_pos')
        pacman_pos = state.get('player1_pos') if self.player_id == 2 else state.get('player2_pos')
        
        if not ghost_pos:
            return 'stay'
        
        # 获取所有可能的动作
        valid_actions = ['up', 'down', 'left', 'right', 'stay']
        action_scores = {}
        
        for action in valid_actions:
            new_pos = self._get_new_position(ghost_pos, action)
            
            # 检查是否可以移动到新位置
            if not self._is_valid_position(new_pos, board):
                continue
            
            score = 0
            
            # 追逐吃豆人
            if pacman_pos:
                distance_to_pacman = self._manhattan_distance(new_pos, pacman_pos)
                score += 100 - distance_to_pacman  # 越接近吃豆人越好
                
                # 如果能直接抓到吃豆人
                if distance_to_pacman == 0:
                    score += 1000
                elif distance_to_pacman == 1:
                    score += 500
                
                self.last_pacman_pos = pacman_pos
            
            # 如果找不到吃豆人，去最后已知位置
            elif self.last_pacman_pos:
                distance_to_last = self._manhattan_distance(new_pos, self.last_pacman_pos)
                score += 50 - distance_to_last
            
            # 避免停留在同一位置
            if action != 'stay':
                score += 10
            
            action_scores[action] = score
        
        # 选择最佳动作
        if action_scores:
            best_action = max(action_scores, key=action_scores.get)
            return best_action
        
        return 'stay'
    
    def _get_new_position(self, pos: Tuple[int, int], action: str) -> Tuple[int, int]:
        """根据动作计算新位置"""
        row, col = pos
        if action == 'up':
            return (row - 1, col)
        elif action == 'down':
            return (row + 1, col)
        elif action == 'left':
            return (row, col - 1)
        elif action == 'right':
            return (row, col + 1)
        else:
            return pos
    
    def _is_valid_position(self, pos: Tuple[int, int], board) -> bool:
        """检查位置是否有效"""
        row, col = pos
        if row < 0 or row >= board.shape[0] or col < 0 or col >= board.shape[1]:
            return False
        return board[row, col] != PacmanGame.WALL
    
    def _manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """计算曼哈顿距离"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) 