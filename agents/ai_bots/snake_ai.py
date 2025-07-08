"""
贪吃蛇专用AI智能体 - Bug修复版
"""

import random
import heapq
from typing import List, Tuple, Dict, Any, Optional
from agents.base_agent import BaseAgent

class SmartSnakeAI(BaseAgent):
    """
    一个高度智能的贪吃蛇AI (Bug修复版)。

    核心策略:
    1.  **哈密顿环 (Hamiltonian Cycle) 生存策略**:
        AI的默认行为是沿着一条预先计算好的、覆盖整个棋盘的安全路径移动。
        这保证了蛇永远不会自我碰撞或将自己困在死角。

    2.  **安全的A*寻路 (Safe A* Pathfinding)**:
        A*算法用于寻找从当前路径到食物的“捷径”。
        只有在确认吃掉食物后仍能安全返回蛇尾时，AI才会走上捷径。

    3.  **动态决策优先级**:
        - 生存优先: 当蛇变得很长时，专注于沿着安全路径移动。
        - 机会导向: 在安全的前提下，抓住机会吃食物。
        - 紧急避险: 如果偏离路径，优先找到返回蛇尾的路径。
    """

    def __init__(self, name: str = "SmartSnakeAI", player_id: int = 2):
        super().__init__(name, player_id)
        self.path = []
        self.cycle_path_dict = {}

    def get_action(self, observation: Dict[str, Any], env: Any) -> Tuple[int, int]:
        """根据当前游戏状态，计算并返回最佳动作。"""
        game = env.game
        board_size = game.board_size

        my_snake = game.snake1 if self.player_id == 1 else game.snake2
        opponent_snake = game.snake2 if self.player_id == 1 else game.snake1
        foods = game.foods
        
        if not my_snake:
            return random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])

        head = my_snake[0]
        
        if board_size not in self.cycle_path_dict:
            self.cycle_path_dict[board_size] = self._create_hamiltonian_cycle(board_size)
        
        self.path = self.cycle_path_dict[board_size]
        
        # 1. 寻找通往食物的安全路径
        best_food_path = self._find_best_food_path(head, my_snake, opponent_snake, foods, board_size)
        
        if best_food_path:
            move = self._get_move_from_path(head, best_food_path)
            if move: return move

        # 2. 如果没有好的食物目标，就沿着预设的安全路径（哈密顿环）移动
        default_move = self._follow_default_path(head, my_snake, opponent_snake, board_size)
        if default_move:
            return default_move
            
        # 3. 如果连安全路径都走不了，则尝试寻找自己的尾巴
        tail_path = self._a_star(head, my_snake[-1], my_snake, opponent_snake, board_size)
        if tail_path:
             move = self._get_move_from_path(head, tail_path)
             if move: return move
        
        # 4. 如果所有策略都失效，则随机选择一个不会立即死亡的动作
        safe_actions = self._get_all_safe_moves(head, my_snake, opponent_snake, board_size)
        if safe_actions:
            return random.choice(safe_actions)
            
        # 5. 【终极保障】如果无路可走，随便选一个方向（为了不让游戏崩溃）
        return (0, 1)

    def _find_best_food_path(self, head, my_snake, opponent_snake, foods, board_size):
        """寻找最佳的食物路径，综合考虑距离和安全性。"""
        shortest_path = None
        foods.sort(key=lambda f: self._manhattan_distance(head, f))

        for food in foods:
            path_to_food = self._a_star(head, food, my_snake, opponent_snake, board_size)
            if path_to_food:
                projected_snake = [food] + my_snake
                path_to_tail = self._a_star(food, projected_snake[-1], projected_snake, opponent_snake, board_size)
                if path_to_tail:
                    shortest_path = path_to_food
                    break
        return shortest_path
        
    def _follow_default_path(self, head, my_snake, opponent_snake, board_size):
        """沿着预设的哈密顿环移动。"""
        try:
            current_index = self.path.index(head)
            for i in range(1, len(self.path) + 1):
                next_index = (current_index + i) % len(self.path)
                next_pos = self.path[next_index]
                
                # Bug修复点：在这里调用 _is_safe 时，必须传入 board_size
                if self._is_safe(next_pos, my_snake, opponent_snake, board_size):
                    return self._pos_to_action(head, next_pos)
        except ValueError:
            return None
        return None

    def _get_move_from_path(self, head, path):
        """从路径中提取出下一步的移动方向。"""
        if path and len(path) > 1:
            next_pos = path[1]
            return self._pos_to_action(head, next_pos)
        return None

    def _get_all_safe_moves(self, head, my_snake, opponent_snake, board_size):
        """获取所有不会立即导致死亡的移动方向。"""
        safe_moves = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            next_pos = (head[0] + dr, head[1] + dc)
            if self._is_safe(next_pos, my_snake, opponent_snake, board_size):
                safe_moves.append((dr, dc))
        return safe_moves
        
    def _create_hamiltonian_cycle(self, board_size):
        """为给定大小的棋盘创建一个哈密顿环路径。"""
        path = []
        for i in range(board_size):
            if i % 2 == 0:
                for j in range(board_size):
                    path.append((i, j))
            else:
                for j in range(board_size - 1, -1, -1):
                    path.append((i, j))
        return path

    def _a_star(self, start, end, my_snake, opponent_snake, board_size):
        """A*寻路算法。"""
        open_set = [(0, start)]
        came_from = {}
        g_score = {(r, c): float('inf') for r in range(board_size) for c in range(board_size)}
        g_score[start] = 0
        f_score = {(r, c): float('inf') for r in range(board_size) for c in range(board_size)}
        f_score[start] = self._manhattan_distance(start, end)

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == end:
                return self._reconstruct_path(came_from, current)

            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dr, current[1] + dc)

                if self._is_safe(neighbor, my_snake, opponent_snake, board_size):
                    tentative_g_score = g_score[current] + 1
                    if tentative_g_score < g_score.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = g_score[neighbor] + self._manhattan_distance(neighbor, end)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None

    def _is_safe(self, pos, my_snake, opponent_snake, board_size):
        """检查一个位置是否安全（界内、非蛇身）。"""
        r, c = pos
        if not (0 <= r < board_size and 0 <= c < board_size):
            return False
        if pos in my_snake[:-1]:
            return False
        if pos in opponent_snake:
            return False
        return True

    def _reconstruct_path(self, came_from, current):
        """从came_from字典中重构路径。"""
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.insert(0, current)
        return total_path
    
    def _pos_to_action(self, current_pos, next_pos):
        """将两个位置的差异转换为移动方向。"""
        return (next_pos[0] - current_pos[0], next_pos[1] - current_pos[1])

    def _manhattan_distance(self, pos1, pos2):
        """计算两个点之间的曼哈顿距离。"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

class SnakeAI(SmartSnakeAI):
    def __init__(self, name: str = "SnakeAI", player_id: int = 1):
        super().__init__(name, player_id)