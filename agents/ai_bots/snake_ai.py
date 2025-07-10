"""
Snake AI - 简洁实用版本
"""
import random
import heapq
from typing import List, Tuple, Dict, Optional, Set
from agents.base_agent import BaseAgent

class SnakeAI(BaseAgent):
    """
    简洁实用的贪吃蛇AI
    
    核心策略：
    1. A*寻路找食物
    2. 基本安全性检查
    3. 简单的生存策略
    """
    
    def __init__(self, name: str = "SnakeAI", player_id: int = 1):
        super().__init__(name, player_id)
        self.directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # 右、下、左、上
        self.direction_names = ['right', 'down', 'left', 'up']

    def get_action(self, observation, env):
        """获取下一步动作"""
        # 获取游戏状态并适配旧接口
        raw_game_state = env.game.get_state()
        game_state = {
            'snakes': {
                1: raw_game_state.get('snake1', []),
                2: raw_game_state.get('snake2', [])
            },
            'food': raw_game_state.get('foods', []),
            'board_size': (env.game.width, env.game.height)
        }
        
        my_snake = game_state['snakes'].get(self.player_id)
        
        if not my_snake or len(my_snake) == 0:
            return random.choice(self.direction_names)
        
        my_head = my_snake[0]
        food_positions = game_state['food']
        
        # 1. 寻找最近的食物
        target_food = self._find_nearest_food(my_head, food_positions)
        
        # 2. 计算可能的动作
        possible_actions = []
        
        for i, direction in enumerate(self.directions):
            new_pos = (my_head[0] + direction[0], my_head[1] + direction[1])
            
            # 检查是否安全
            if self._is_safe_move(new_pos, my_snake, game_state):
                possible_actions.append((i, new_pos))
        
        if not possible_actions:
            # 如果没有安全动作，随机选择一个
            return random.choice(self.direction_names)
        
        # 3. 选择最佳动作
        if target_food:
            best_action = self._choose_best_action_to_food(possible_actions, target_food)
        else:
            # 如果没有食物，选择最安全的动作
            best_action = self._choose_safest_action(possible_actions, my_snake, game_state)
        
        return self.direction_names[best_action]

    def _find_nearest_food(self, head: Tuple[int, int], food_positions: List[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """找到最近的食物"""
        if not food_positions:
            return None
        
        min_distance = float('inf')
        nearest_food = None
        
        for food in food_positions:
            distance = abs(head[0] - food[0]) + abs(head[1] - food[1])  # 曼哈顿距离
            if distance < min_distance:
                min_distance = distance
                nearest_food = food
        
        return nearest_food

    def _is_safe_move(self, new_pos: Tuple[int, int], my_snake: List[Tuple[int, int]], game_state: Dict) -> bool:
        """检查移动是否安全"""
        width, height = game_state['board_size']
        
        # 检查边界
        if new_pos[0] < 0 or new_pos[0] >= width or new_pos[1] < 0 or new_pos[1] >= height:
            return False
        
        # 检查是否撞到自己的身体（排除尾巴，因为尾巴会移动）
        if new_pos in my_snake[:-1]:
            return False
        
        # 检查是否撞到其他蛇
        for snake_id, snake in game_state['snakes'].items():
            if snake_id != self.player_id and snake:
                if new_pos in snake:
                    return False
        
        return True

    def _choose_best_action_to_food(self, possible_actions: List[Tuple[int, Tuple[int, int]]], 
                                   target_food: Tuple[int, int]) -> int:
        """选择朝向食物的最佳动作"""
        best_action = possible_actions[0][0]
        min_distance = float('inf')
        
        for action_idx, new_pos in possible_actions:
            distance = abs(new_pos[0] - target_food[0]) + abs(new_pos[1] - target_food[1])
            if distance < min_distance:
                min_distance = distance
                best_action = action_idx
        
        return best_action

    def _choose_safest_action(self, possible_actions: List[Tuple[int, Tuple[int, int]]], 
                             my_snake: List[Tuple[int, int]], game_state: Dict) -> int:
        """选择最安全的动作"""
        best_action = possible_actions[0][0]
        max_safe_distance = -1
        
        for action_idx, new_pos in possible_actions:
            # 计算这个位置的安全性（周围有多少空间）
            safe_distance = self._calculate_safe_distance(new_pos, my_snake, game_state)
            
            if safe_distance > max_safe_distance:
                max_safe_distance = safe_distance
                best_action = action_idx
        
        return best_action

    def _calculate_safe_distance(self, pos: Tuple[int, int], my_snake: List[Tuple[int, int]], 
                                game_state: Dict) -> int:
        """计算位置的安全距离（BFS搜索可达空间）"""
        width, height = game_state['board_size']
        visited = set()
        queue = [pos]
        visited.add(pos)
        
        # 收集所有障碍物
        obstacles = set()
        obstacles.update(my_snake)
        for snake_id, snake in game_state['snakes'].items():
            if snake_id != self.player_id and snake:
                obstacles.update(snake)
        
        count = 0
        while queue and count < 20:  # 限制搜索深度
            current = queue.pop(0)
            count += 1
            
            for dx, dy in self.directions:
                next_pos = (current[0] + dx, current[1] + dy)
                
                # 检查边界
                if (next_pos[0] < 0 or next_pos[0] >= width or 
                    next_pos[1] < 0 or next_pos[1] >= height):
                    continue
                
                # 检查是否已访问或是障碍物
                if next_pos in visited or next_pos in obstacles:
                    continue
                
                visited.add(next_pos)
                queue.append(next_pos)
        
        return count

    def _a_star_to_food(self, start: Tuple[int, int], goal: Tuple[int, int], 
                       game_state: Dict) -> Optional[List[Tuple[int, int]]]:
        """A*算法寻找到食物的路径"""
        if start == goal:
            return [start]
        
        width, height = game_state['board_size']
        
        # 收集障碍物
        obstacles = set()
        for snake_id, snake in game_state['snakes'].items():
            if snake:
                obstacles.update(snake[:-1])  # 不包括尾巴
        
        # A*搜索
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, goal)}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == goal:
                # 重构路径
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            
            for dx, dy in self.directions:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # 检查边界
                if (neighbor[0] < 0 or neighbor[0] >= width or 
                    neighbor[1] < 0 or neighbor[1] >= height):
                    continue
                
                # 检查障碍物
                if neighbor in obstacles:
                    continue
                
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self._heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return None  # 没有找到路径

    def _heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """A*算法的启发式函数（曼哈顿距离）"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])