"""
贪吃蛇专用AI智能体
"""

import random
import numpy as np
from agents.base_agent import BaseAgent
import heapq

class SnakeAI(BaseAgent):
    """贪吃蛇AI智能体"""
    
    def __init__(self, name="SnakeAI", player_id=1):
        super().__init__(name, player_id)
    
    def get_action(self, observation, env):
        """获取动作"""
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            return None
        
        # 获取当前蛇的信息
        game = env.game
        if self.player_id == 1:
            snake = game.snake1
            current_direction = game.direction1
        else:
            snake = game.snake2
            current_direction = game.direction2
        
        if not snake:
            return random.choice(valid_actions)
        
        head = snake[0]
        
        # 使用A*算法寻找到最近食物的路径
        if game.foods:
            target_food = self._find_nearest_food(head, game.foods)
            path = self._a_star_pathfinding(head, target_food, game)
            
            if path and len(path) > 1:
                next_pos = path[1]  # path[0]是当前位置
                action = self._pos_to_action(head, next_pos)
                if action in valid_actions:
                    return action
        
        # 如果A*失败，使用安全策略
        return self._get_safe_action(head, game, valid_actions)
    
    def _find_nearest_food(self, head, foods):
        """找到最近的食物"""
        min_distance = float('inf')
        nearest_food = foods[0]
        
        for food in foods:
            distance = abs(head[0] - food[0]) + abs(head[1] - food[1])
            if distance < min_distance:
                min_distance = distance
                nearest_food = food
        
        return nearest_food
    
    def _a_star_pathfinding(self, start, goal, game):
        """A*寻路算法"""
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        def get_neighbors(pos):
            x, y = pos
            neighbors = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < game.board_size and 0 <= ny < game.board_size):
                    # 检查是否撞到蛇身（但允许撞到尾部，因为尾部会移动）
                    if ((nx, ny) not in game.snake1[:-1] and 
                        (nx, ny) not in game.snake2[:-1]):
                        neighbors.append((nx, ny))
            return neighbors
        
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        
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
            
            for neighbor in get_neighbors(current):
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return None  # 没有找到路径
    
    def _pos_to_action(self, current_pos, next_pos):
        """将位置转换为动作"""
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        
        return (dx, dy)
    
    def _get_safe_action(self, head, game, valid_actions):
        """获取安全的动作"""
        safe_actions = []
        
        for action in valid_actions:
            # action已经是方向元组
            new_head = (head[0] + action[0], head[1] + action[1])
            
            # 检查是否安全
            if (0 <= new_head[0] < game.board_size and 
                0 <= new_head[1] < game.board_size and
                new_head not in game.snake1[:-1] and 
                new_head not in game.snake2[:-1]):
                safe_actions.append(action)
        
        if safe_actions:
            return random.choice(safe_actions)
        
        return random.choice(valid_actions)


class SmartSnakeAI(BaseAgent):
    """更智能的贪吃蛇AI"""
    
    def __init__(self, name="SmartSnakeAI", player_id=1):
        super().__init__(name, player_id)
    
    def get_action(self, observation, env):
        """使用A*算法寻路的贪吃蛇AI"""
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            return None
        
        game = env.game
        if self.player_id == 1:
            snake = game.snake1
            current_direction = game.direction1
        else:
            snake = game.snake2
            current_direction = game.direction2
        
        if not snake:
            return random.choice(valid_actions)
        
        head = snake[0]
        
        # 使用A*算法寻找到最近食物的路径
        if game.foods:
            target_food = self._find_nearest_food(head, game.foods)
            path = self._a_star_pathfinding(head, target_food, game)
            
            if path and len(path) > 1:
                next_pos = path[1]  # path[0]是当前位置
                action = self._pos_to_action(head, next_pos)
                if action in valid_actions:
                    return action
        
        # 如果A*失败，使用安全策略
        return self._get_safe_action(head, game, valid_actions)
    
    def _find_nearest_food(self, head, foods):
        """找到最近的食物"""
        min_distance = float('inf')
        nearest_food = foods[0]
        
        for food in foods:
            distance = abs(head[0] - food[0]) + abs(head[1] - food[1])
            if distance < min_distance:
                min_distance = distance
                nearest_food = food
        
        return nearest_food
    
    def _a_star_pathfinding(self, start, goal, game):
        """A*寻路算法"""
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        def get_neighbors(pos):
            x, y = pos
            neighbors = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < game.board_size and 0 <= ny < game.board_size):
                    # 检查是否撞到蛇身（但允许撞到尾部，因为尾部会移动）
                    if ((nx, ny) not in game.snake1[:-1] and 
                        (nx, ny) not in game.snake2[:-1]):
                        neighbors.append((nx, ny))
            return neighbors
        
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        
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
            
            for neighbor in get_neighbors(current):
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return None  # 没有找到路径
    
    def _pos_to_action(self, current_pos, next_pos):
        """将位置转换为动作"""
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        
        return (dx, dy)
    
    def _get_safe_action(self, head, game, valid_actions):
        """获取安全的动作"""
        safe_actions = []
        
        for action in valid_actions:
            # action已经是方向元组
            new_head = (head[0] + action[0], head[1] + action[1])
            
            # 检查是否安全
            if (0 <= new_head[0] < game.board_size and 
                0 <= new_head[1] < game.board_size and
                new_head not in game.snake1[:-1] and 
                new_head not in game.snake2[:-1]):
                safe_actions.append(action)
        
        if safe_actions:
            return random.choice(safe_actions)
        
        return random.choice(valid_actions)