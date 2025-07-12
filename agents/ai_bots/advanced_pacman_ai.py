"""
高级吃豆人AI - 实现路径规划、地图导航和实时追逐策略
"""

import heapq
import random
from collections import deque
from typing import Dict, List, Tuple, Any, Optional, Set
from agents.base_agent import BaseAgent
from games.pacman.pacman_game import PacmanGame

class PathFinder:
    """路径搜索算法实现"""
    
    @staticmethod
    def a_star(board, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """A*路径搜索算法"""
        def heuristic(pos1, pos2):
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        def get_neighbors(pos):
            neighbors = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = pos[0] + dr, pos[1] + dc
                if (0 <= nr < board.shape[0] and 0 <= nc < board.shape[1] and 
                    board[nr, nc] != PacmanGame.WALL):
                    neighbors.append((nr, nc))
            return neighbors
        
        open_set = [(0, start)]
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        came_from = {}
        closed_set = set()
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == goal:
                # 重建路径
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]
            
            closed_set.add(current)
            
            for neighbor in get_neighbors(current):
                if neighbor in closed_set:
                    continue
                    
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return []  # 无路径
    
    @staticmethod
    def bfs(board, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """BFS路径搜索算法"""
        def get_neighbors(pos):
            neighbors = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = pos[0] + dr, pos[1] + dc
                if (0 <= nr < board.shape[0] and 0 <= nc < board.shape[1] and 
                    board[nr, nc] != PacmanGame.WALL):
                    neighbors.append((nr, nc))
            return neighbors
        
        if start == goal:
            return []
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor in get_neighbors(current):
                if neighbor == goal:
                    return path[1:] + [neighbor]  # 不包含起始点
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return []  # 无路径
    
    @staticmethod
    def find_safe_positions(board, danger_pos: Tuple[int, int], safe_distance: int = 3) -> List[Tuple[int, int]]:
        """寻找安全位置（远离危险点）"""
        safe_positions = []
        
        for row in range(board.shape[0]):
            for col in range(board.shape[1]):
                if board[row, col] != PacmanGame.WALL:
                    distance = abs(row - danger_pos[0]) + abs(col - danger_pos[1])
                    if distance >= safe_distance:
                        safe_positions.append((row, col))
        
        return safe_positions


class AdvancedPacmanAI(BaseAgent):
    """高级吃豆人AI - 专注于收集豆子并智能避开幽灵"""
    
    def __init__(self, player_id: int = 1):
        super().__init__()
        self.player_id = player_id
        self.name = f"高级吃豆人AI_{player_id}"
        self.path_finder = PathFinder()
        self.current_target = None
        self.current_path = []
        self.escape_mode = False
        self.last_ghost_pos = None
        self.stuck_counter = 0
        self.last_position = None
        
    def get_action(self, observation: Dict[str, Any], env) -> str:
        """获取吃豆人的动作"""
        state = observation
        board = state.get('raw_board')  # 使用原始棋盘，不包含玩家位置
        player_pos = state.get('player1_pos') if self.player_id == 1 else state.get('player2_pos')
        ghost_pos = state.get('player2_pos') if self.player_id == 1 else state.get('player1_pos')
        
        if not player_pos:
            return 'stay'
        
        # 检测是否被困
        if self.last_position == player_pos:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
        self.last_position = player_pos
        
        # 分析威胁等级
        threat_level = self._analyze_threat(player_pos, ghost_pos, board)
        
        # 根据威胁等级选择策略
        if threat_level >= 3:  # 高威胁
            return self._escape_strategy(player_pos, ghost_pos, board)
        elif threat_level >= 1:  # 中等威胁
            return self._cautious_strategy(player_pos, ghost_pos, board)
        else:  # 安全
            return self._collection_strategy(player_pos, board)
    
    def _analyze_threat(self, player_pos: Tuple[int, int], ghost_pos: Tuple[int, int], board) -> int:
        """分析威胁等级"""
        if not ghost_pos:
            return 0
        
        # 计算真实距离（通过路径规划）
        path_to_ghost = self.path_finder.bfs(board, player_pos, ghost_pos)
        real_distance = len(path_to_ghost) if path_to_ghost else float('inf')
        
        if real_distance <= 1:
            return 5  # 极高威胁
        elif real_distance <= 2:
            return 4  # 高威胁
        elif real_distance <= 3:
            return 3  # 中高威胁
        elif real_distance <= 5:
            return 2  # 中等威胁
        elif real_distance <= 8:
            return 1  # 低威胁
        else:
            return 0  # 安全
    
    def _escape_strategy(self, player_pos: Tuple[int, int], ghost_pos: Tuple[int, int], board) -> str:
        """逃跑策略"""
        # 寻找安全位置
        safe_positions = self.path_finder.find_safe_positions(board, ghost_pos, safe_distance=5)
        
        if safe_positions:
            # 选择最近的安全位置
            best_safe_pos = min(safe_positions, 
                               key=lambda pos: len(self.path_finder.bfs(board, player_pos, pos)) 
                               if self.path_finder.bfs(board, player_pos, pos) else float('inf'))
            
            path = self.path_finder.a_star(board, player_pos, best_safe_pos)
            if path:
                next_pos = path[0]
                return self._pos_to_action(player_pos, next_pos)
        
        # 如果没有安全位置，选择远离幽灵的方向
        return self._move_away_from_ghost(player_pos, ghost_pos, board)
    
    def _cautious_strategy(self, player_pos: Tuple[int, int], ghost_pos: Tuple[int, int], board) -> str:
        """谨慎策略 - 在警惕幽灵的同时收集豆子"""
        # 寻找相对安全的豆子
        safe_dots = self._find_safe_dots(player_pos, ghost_pos, board)
        
        if safe_dots:
            # 选择最近的安全豆子
            target_dot = min(safe_dots, 
                           key=lambda dot: len(self.path_finder.bfs(board, player_pos, dot)) 
                           if self.path_finder.bfs(board, player_pos, dot) else float('inf'))
            
            path = self.path_finder.a_star(board, player_pos, target_dot)
            if path:
                next_pos = path[0]
                return self._pos_to_action(player_pos, next_pos)
        
        # 如果没有安全豆子，执行逃跑策略
        return self._escape_strategy(player_pos, ghost_pos, board)
    
    def _collection_strategy(self, player_pos: Tuple[int, int], board) -> str:
        """收集策略 - 高效收集豆子"""
        # 如果被困，随机移动
        if self.stuck_counter > 3:
            return self._random_move(player_pos, board)
        
        # 寻找最近的豆子
        nearest_dot = self._find_nearest_dot(player_pos, board)
        
        if nearest_dot:
            # 检查是否需要重新规划路径
            if (self.current_target != nearest_dot or 
                not self.current_path or 
                player_pos in self.current_path):
                
                self.current_target = nearest_dot
                self.current_path = self.path_finder.a_star(board, player_pos, nearest_dot)
            
            if self.current_path:
                next_pos = self.current_path[0]
                self.current_path = self.current_path[1:]
                return self._pos_to_action(player_pos, next_pos)
        
        return self._random_move(player_pos, board)
    
    def _find_safe_dots(self, player_pos: Tuple[int, int], ghost_pos: Tuple[int, int], board) -> List[Tuple[int, int]]:
        """寻找相对安全的豆子"""
        safe_dots = []
        
        for row in range(board.shape[0]):
            for col in range(board.shape[1]):
                if board[row, col] == PacmanGame.DOT:
                    dot_pos = (row, col)
                    
                    # 计算到豆子的距离
                    path_to_dot = self.path_finder.bfs(board, player_pos, dot_pos)
                    player_distance = len(path_to_dot) if path_to_dot else float('inf')
                    
                    # 计算幽灵到豆子的距离
                    ghost_path_to_dot = self.path_finder.bfs(board, ghost_pos, dot_pos)
                    ghost_distance = len(ghost_path_to_dot) if ghost_path_to_dot else float('inf')
                    
                    # 如果玩家比幽灵更容易到达这个豆子，认为是安全的
                    if player_distance < ghost_distance - 1:
                        safe_dots.append(dot_pos)
        
        return safe_dots
    
    def _find_nearest_dot(self, pos: Tuple[int, int], board) -> Optional[Tuple[int, int]]:
        """找到最近的豆子（基于真实路径距离）"""
        min_distance = float('inf')
        nearest_dot = None
        
        for row in range(board.shape[0]):
            for col in range(board.shape[1]):
                if board[row, col] == PacmanGame.DOT:
                    dot_pos = (row, col)
                    path = self.path_finder.bfs(board, pos, dot_pos)
                    distance = len(path) if path else float('inf')
                    
                    if distance < min_distance:
                        min_distance = distance
                        nearest_dot = dot_pos
        
        return nearest_dot
    
    def _move_away_from_ghost(self, player_pos: Tuple[int, int], ghost_pos: Tuple[int, int], board) -> str:
        """远离幽灵移动"""
        valid_actions = ['up', 'down', 'left', 'right']
        best_action = 'stay'
        max_distance = -1
        
        for action in valid_actions:
            new_pos = self._get_new_position(player_pos, action)
            
            if self._is_valid_position(new_pos, board):
                distance = abs(new_pos[0] - ghost_pos[0]) + abs(new_pos[1] - ghost_pos[1])
                if distance > max_distance:
                    max_distance = distance
                    best_action = action
        
        return best_action
    
    def _random_move(self, player_pos: Tuple[int, int], board) -> str:
        """随机移动（避开墙壁）"""
        valid_actions = []
        for action in ['up', 'down', 'left', 'right']:
            new_pos = self._get_new_position(player_pos, action)
            if self._is_valid_position(new_pos, board):
                valid_actions.append(action)
        
        return random.choice(valid_actions) if valid_actions else 'stay'
    
    def _pos_to_action(self, current_pos: Tuple[int, int], target_pos: Tuple[int, int]) -> str:
        """将位置转换为动作"""
        dr = target_pos[0] - current_pos[0]
        dc = target_pos[1] - current_pos[1]
        
        if dr == -1:
            return 'up'
        elif dr == 1:
            return 'down'
        elif dc == -1:
            return 'left'
        elif dc == 1:
            return 'right'
        else:
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


class AdvancedGhostAI(BaseAgent):
    """高级幽灵AI - 实现智能追逐和拦截策略"""
    
    def __init__(self, player_id: int = 2):
        super().__init__()
        self.player_id = player_id
        self.name = f"高级幽灵AI_{player_id}"
        self.path_finder = PathFinder()
        self.pacman_history = deque(maxlen=5)  # 记录吃豆人历史位置
        self.strategy = 'chase'  # 'chase', 'intercept', 'patrol'
        self.patrol_targets = []
        self.current_patrol_target = 0
        
    def get_action(self, observation: Dict[str, Any], env) -> str:
        """获取幽灵的动作"""
        state = observation
        board = state.get('raw_board')
        ghost_pos = state.get('player2_pos') if self.player_id == 2 else state.get('player1_pos')
        pacman_pos = state.get('player1_pos') if self.player_id == 2 else state.get('player2_pos')
        
        if not ghost_pos:
            return 'stay'
        
        # 记录吃豆人位置历史
        if pacman_pos:
            self.pacman_history.append(pacman_pos)
        
        # 选择策略
        if pacman_pos:
            # 计算到吃豆人的距离
            path_to_pacman = self.path_finder.bfs(board, ghost_pos, pacman_pos)
            distance = len(path_to_pacman) if path_to_pacman else float('inf')
            
            if distance <= 8:
                self.strategy = 'chase'
            elif len(self.pacman_history) >= 3:
                self.strategy = 'intercept'
            else:
                self.strategy = 'patrol'
        else:
            self.strategy = 'patrol'
        
        # 执行对应策略
        if self.strategy == 'chase':
            return self._chase_strategy(ghost_pos, pacman_pos, board)
        elif self.strategy == 'intercept':
            return self._intercept_strategy(ghost_pos, pacman_pos, board)
        else:
            return self._patrol_strategy(ghost_pos, board)
    
    def _chase_strategy(self, ghost_pos: Tuple[int, int], pacman_pos: Tuple[int, int], board) -> str:
        """直接追逐策略"""
        if not pacman_pos:
            return self._patrol_strategy(ghost_pos, board)
        
        # 使用A*算法规划最优路径
        path = self.path_finder.a_star(board, ghost_pos, pacman_pos)
        
        if path:
            next_pos = path[0]
            return self._pos_to_action(ghost_pos, next_pos)
        
        return 'stay'
    
    def _intercept_strategy(self, ghost_pos: Tuple[int, int], pacman_pos: Tuple[int, int], board) -> str:
        """拦截策略 - 预测吃豆人移动并提前拦截"""
        if not pacman_pos or len(self.pacman_history) < 2:
            return self._chase_strategy(ghost_pos, pacman_pos, board)
        
        # 预测吃豆人下一个位置
        predicted_pos = self._predict_pacman_position()
        
        if predicted_pos:
            # 尝试拦截预测位置
            path = self.path_finder.a_star(board, ghost_pos, predicted_pos)
            if path and len(path) <= 5:  # 只有在合理距离内才拦截
                next_pos = path[0]
                return self._pos_to_action(ghost_pos, next_pos)
        
        # 如果拦截不可行，回到追逐策略
        return self._chase_strategy(ghost_pos, pacman_pos, board)
    
    def _patrol_strategy(self, ghost_pos: Tuple[int, int], board) -> str:
        """巡逻策略 - 在重要位置之间巡逻"""
        if not self.patrol_targets:
            self._initialize_patrol_targets(board)
        
        if self.patrol_targets:
            target = self.patrol_targets[self.current_patrol_target]
            path = self.path_finder.bfs(board, ghost_pos, target)
            
            if path:
                next_pos = path[0]
                return self._pos_to_action(ghost_pos, next_pos)
            else:
                # 到达目标，切换到下一个巡逻点
                self.current_patrol_target = (self.current_patrol_target + 1) % len(self.patrol_targets)
        
        return self._random_move(ghost_pos, board)
    
    def _predict_pacman_position(self) -> Optional[Tuple[int, int]]:
        """预测吃豆人下一个位置"""
        if len(self.pacman_history) < 2:
            return None
        
        # 分析移动模式
        last_pos = self.pacman_history[-1]
        prev_pos = self.pacman_history[-2]
        
        # 计算移动向量
        dr = last_pos[0] - prev_pos[0]
        dc = last_pos[1] - prev_pos[1]
        
        # 预测下一个位置
        predicted_pos = (last_pos[0] + dr, last_pos[1] + dc)
        
        return predicted_pos
    
    def _initialize_patrol_targets(self, board):
        """初始化巡逻目标点"""
        # 寻找地图中的战略位置（如十字路口、角落等）
        self.patrol_targets = []
        
        height, width = board.shape
        
        # 添加四个角落附近的可达位置
        corners = [
            (2, 2), (2, width-3), (height-3, 2), (height-3, width-3)
        ]
        
        for corner in corners:
            if self._is_valid_position(corner, board):
                self.patrol_targets.append(corner)
        
        # 添加中心区域
        center = (height//2, width//2)
        if self._is_valid_position(center, board):
            self.patrol_targets.append(center)
        
        # 如果没有有效的巡逻点，使用随机位置
        if not self.patrol_targets:
            for _ in range(5):
                pos = (random.randint(1, height-2), random.randint(1, width-2))
                if self._is_valid_position(pos, board):
                    self.patrol_targets.append(pos)
    
    def _random_move(self, ghost_pos: Tuple[int, int], board) -> str:
        """随机移动"""
        valid_actions = []
        for action in ['up', 'down', 'left', 'right']:
            new_pos = self._get_new_position(ghost_pos, action)
            if self._is_valid_position(new_pos, board):
                valid_actions.append(action)
        
        return random.choice(valid_actions) if valid_actions else 'stay'
    
    def _pos_to_action(self, current_pos: Tuple[int, int], target_pos: Tuple[int, int]) -> str:
        """将位置转换为动作"""
        dr = target_pos[0] - current_pos[0]
        dc = target_pos[1] - current_pos[1]
        
        if dr == -1:
            return 'up'
        elif dr == 1:
            return 'down'
        elif dc == -1:
            return 'left'
        elif dc == 1:
            return 'right'
        else:
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