"""
Snake AI
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

class BasicSnakeAI(BaseAgent):
    """基础贪吃蛇AI - 只考虑直接路径到食物，不考虑安全性"""
    
    def __init__(self, name="BasicSnakeAI", player_id=2):
        super().__init__(name, player_id)
    
    def get_action(self, observation, env):
        """获取动作 - 简单的直接寻路算法"""
        game_state = self._parse_game_state(env)
        
        my_head = game_state['my_head']
        my_snake = game_state['my_snake']
        food_positions = game_state['food_positions']
        board_size = game_state['board_size']
        
        # 如果没有食物，随机移动
        if not food_positions:
            return self._get_random_safe_action(my_head, my_snake, board_size)
        
        # 找到最近的食物
        nearest_food = self._find_nearest_food(my_head, food_positions)
        
        # 尝试直接移动到食物
        action = self._move_towards_food(my_head, nearest_food, my_snake, board_size)
        
        # 如果无法直接移动，随机选择安全动作
        if action is None:
            action = self._get_random_safe_action(my_head, my_snake, board_size)
        
        return action
    
    def _parse_game_state(self, env):
        """解析游戏状态"""
        state = env.game.get_state()
        board = state['board']
        board_size = board.shape[0]
        
        # 找到我的蛇
        my_snake = []
        my_head = None
        for r in range(board_size):
            for c in range(board_size):
                if board[r, c] == self.player_id:  # 我的头部
                    my_head = (r, c)
                elif board[r, c] == self.player_id + 1:  # 我的身体
                    my_snake.append((r, c))
        
        # 找到食物
        food_positions = []
        for r in range(board_size):
            for c in range(board_size):
                if board[r, c] == 5:  # 食物
                    food_positions.append((r, c))
        
        return {
            'my_head': my_head,
            'my_snake': my_snake,
            'food_positions': food_positions,
            'board_size': board_size
        }
    
    def _find_nearest_food(self, head, food_positions):
        """找到最近的食物"""
        if not food_positions:
            return None
        
        nearest_food = min(food_positions, key=lambda food: abs(food[0] - head[0]) + abs(food[1] - head[1]))
        return nearest_food
    
    def _move_towards_food(self, head, food, snake, board_size):
        """直接移动到食物"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 上、下、左、右
        
        # 计算到食物的方向
        dr = food[0] - head[0]
        dc = food[1] - head[1]
        
        # 优先选择主要方向
        if abs(dr) > abs(dc):
            # 垂直方向优先
            if dr > 0:  # 向下
                preferred_dirs = [(1, 0), (0, 1), (0, -1), (-1, 0)]
            else:  # 向上
                preferred_dirs = [(-1, 0), (0, 1), (0, -1), (1, 0)]
        else:
            # 水平方向优先
            if dc > 0:  # 向右
                preferred_dirs = [(0, 1), (1, 0), (-1, 0), (0, -1)]
            else:  # 向左
                preferred_dirs = [(0, -1), (1, 0), (-1, 0), (0, 1)]
        
        # 尝试每个方向
        for direction in preferred_dirs:
            new_head = (head[0] + direction[0], head[1] + direction[1])
            
            # 检查是否安全
            if self._is_safe_move(new_head, snake, board_size):
                return direction
        
        return None
    
    def _is_safe_move(self, new_head, snake, board_size):
        """检查移动是否安全"""
        r, c = new_head
        
        # 检查边界
        if r < 0 or r >= board_size or c < 0 or c >= board_size:
            return False
        
        # 检查是否撞到自己
        if new_head in snake:
            return False
        
        return True
    
    def _get_random_safe_action(self, head, snake, board_size):
        """获取随机安全动作"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        safe_directions = []
        
        for direction in directions:
            new_head = (head[0] + direction[0], head[1] + direction[1])
            if self._is_safe_move(new_head, snake, board_size):
                safe_directions.append(direction)
        
        if safe_directions:
            return random.choice(safe_directions)
        else:
            # 没有安全方向，选择第一个方向（游戏会结束）
            return directions[0]