"""
MCTS Bot - 简洁有效版本
"""
import time
import random
import math
import numpy as np
from typing import Any, Dict, List
from agents.base_agent import BaseAgent
import config

class MCTSNode:
    """MCTS节点，为启发式搜索优化"""
    # 构建 MCTS 搜索树的基本单元。每个 MCTSNode 对象代表游戏树中的一个特定局面（状态）。
    # 每个节点包含以下属性：
    # - state: 当前局面
    # - parent: 父节点
    # - action: 从父节点到当前节点的动作
    # - children: 当前节点的所有子节点
    # - wins: 当前节点获胜次数
    # - visits: 当前节点被访问次数
    # - prior: 先验概率/价值
    def __init__(self, game_state, parent=None, action=None, prior=0.0):
        self.state = game_state
        self.parent = parent
        self.action = action
        self.children = []
        self.wins = 0
        self.visits = 0
        self.prior = prior  # 走法的先验概率/价值
        self.untried_actions = list(self.state.get_valid_actions())
        self._is_terminal = self.state.is_terminal()

    def select_child(self, exploration_constant=1.414):
        """使用PUCT (Polynomial Upper Confidence Trees) 公式选择子节点"""
        # PUCT = Q(s,a) + U(s,a)
        #Q(s,a): child.wins / child.visits，代表该行动的平均胜率（利用）。
        #U(s,a): 探索项，鼓励探索不常访问或先验概率高的节点。
        best_value = -float('inf')
        best_child = None
        for child in self.children:
            q_value = child.wins / child.visits if child.visits > 0 else 0
            u_value = exploration_constant * child.prior * math.sqrt(self.visits) / (1 + child.visits)
            puct_value = q_value + u_value
            
            if puct_value > best_value:
                best_value = puct_value
                best_child = child
        return best_child

    def expand(self, action, prior):
        """根据一个动作和其先验概率来扩展节点"""
        next_state = self.state.clone()
        next_state.step(action)
        child = MCTSNode(next_state, parent=self, action=action, prior=prior)
        self.children.append(child)
        self.untried_actions.remove(action)
        return child

    def update(self, result):
        self.visits += 1
        self.wins += result

class MCTSBot(BaseAgent):
    """
    MCTS Bot
    核心特性:
    1. AlphaGo式PUCT选择策略
    2. 由棋形评估驱动的启发式模拟和扩展
    3. 强大的棋形识别能力
    """
    
    def __init__(self, name: str = "MCTSBot", player_id: int = 1, **kwargs):
        super().__init__(name, player_id)
        ai_config = config.AI_CONFIGS.get('mcts', {})
        self.timeout = ai_config.get('timeout', 3.0)
        self.max_simulations = ai_config.get('max_simulations', 1000)
        self.exploration_constant = ai_config.get('exploration_constant', 1.5)
        
        # 棋形和分数 - 从MinimaxBot借鉴
        self.patterns = {
            'FIVE': 100000, 'OPEN_FOUR': 10000, 'RUSH_FOUR': 5000,
            'OPEN_THREE': 2000, 'RUSH_THREE': 800, 'OPEN_TWO': 400,
            'RUSH_TWO': 100, 'BLOCKED_ONE': 5
        }

    def get_action(self, observation: Any, env: Any) -> Any:
        start_time = time.time()
        root_state = env.game.clone()
        
        # 紧急检查
        critical_move = self._check_urgent_moves(root_state)
        if critical_move:
            return critical_move

        action_priors = self._get_action_priors(root_state, root_state.get_valid_actions())
        root_node = MCTSNode(root_state, prior=1.0)
        
        sim_count = 0
        while time.time() - start_time < self.timeout and sim_count < self.max_simulations:
            node = self._select(root_node)
            
            if not node._is_terminal:
                node = self._expand(node)
            
            result = self._simulate(node)
            self._backpropagate(node, result)
            sim_count += 1
        
        return self._get_best_action(root_node)

    def _select(self, node):
        current_node = node
        while not current_node._is_terminal:
            if not current_node.children:
                return current_node
            
            selected_child = current_node.select_child(self.exploration_constant)
            if selected_child is None:
                return current_node # Return current node if no child can be selected
            current_node = selected_child

        return current_node

    def _expand(self, node):
        if not node.untried_actions:
            return node
        
        action_priors = self._get_action_priors(node.state, node.untried_actions)
        prior, action = action_priors[0] # 选择评估最高的动作进行扩展
        
        return node.expand(action, prior)

    def _simulate(self, node):
        current_state = node.state.clone()
        
        for _ in range(30): # 限制模拟深度
            if current_state.is_terminal():
                break
            
            valid_actions = current_state.get_valid_actions()
            if not valid_actions:
                break
            
            action_priors = self._get_action_priors(current_state, valid_actions, for_simulation=True)
            action = self._select_action_by_priors(action_priors)
            current_state.step(action)
        
        winner = current_state.get_winner()
        if winner == self.player_id: return 1.0
        if winner is None: return 0.5 # 平局
        return 0.0 # 输

    def _backpropagate(self, node, result):
        current = node
        while current is not None:
            current.update(result)
            result = 1.0 - result # 对手视角
            current = current.parent

    def _get_best_action(self, root_node):
        if not root_node.children:
            valid_actions = root_node.state.get_valid_actions()
            return random.choice(valid_actions) if valid_actions else None
            
        best_child = max(root_node.children, key=lambda c: c.visits)
        return best_child.action

    def _get_action_priors(self, state, actions, for_simulation=False):
        """获取所有动作的先验价值"""
        priors = []
        for action in actions:
            # 评估己方下这步棋的价值
            my_score = self._evaluate_move(state, action, self.player_id)
            # 评估对手下这步棋的价值 (防守价值)
            opponent_score = self._evaluate_move(state, action, 3 - self.player_id)
            priors.append((my_score + opponent_score, action))
        
        priors.sort(key=lambda x: x[0], reverse=True)
        
        # 归一化为概率
        total_score = sum(p[0] for p in priors) + 1e-9 # 避免除以0
        normalized_priors = [(score / total_score, action) for score, action in priors]
        
        return normalized_priors

    def _select_action_by_priors(self, priors):
        """根据先验概率随机选择动作"""
        actions = [p[1] for p in priors]
        probabilities = [p[0] for p in priors]
        return random.choices(actions, weights=probabilities, k=1)[0]
    
    def _evaluate_move(self, state, action, player_id):
        """使用棋形评估来评估一个动作，并添加位置权重"""
        board_copy = state.board.copy()
        board_copy[action] = player_id
        
        # 基础棋形评估
        base_score = self._evaluate_position(board_copy, player_id)
        
        # 添加位置权重 - 中心位置更有价值
        r, c = action
        board_size = board_copy.shape[0]
        center = board_size // 2
        # 计算到中心的距离
        distance_to_center = abs(r - center) + abs(c - center)
        
        # 位置权重：中心位置加分，边缘位置减分
        # 对于15x15盘，中心是(7,7)，最大距离是14
        max_distance = board_size - 1
        position_weight = (max_distance - distance_to_center) * 50  # 中心位置额外加分
        
        # 特殊处理：如果是空棋盘的第一手，大幅提升中心位置的价值
        if self._is_empty_board(state.board):
            if distance_to_center == 0:  # 中心位置
                position_weight += 1000  # 中心位置价值
            elif distance_to_center <= 2:  # 中心附近
                position_weight += 500
            else:  # 边缘位置
                position_weight -= 200   
        return base_score + position_weight
    
    def _is_empty_board(self, board):
        """查棋盘是否为空"""
        return np.all(board == 0)

    def _evaluate_position(self, board, player):
        """评估棋盘上某个玩家的分数"""
        score = 0
        board_size = board.shape[0]
        
        for r in range(board_size):
            for c in range(board_size):
                if c <= board_size - 5: score += self._evaluate_window(board[r, c:c+5], player)
                if r <= board_size - 5: score += self._evaluate_window(board[r:r+5, c], player)
                if r <= board_size - 5 and c <= board_size - 5: score += self._evaluate_window([board[r+i, c+i] for i in range(5)], player)
                if r <= board_size - 5 and c >= 4: score += self._evaluate_window([board[r+i, c-i] for i in range(5)], player)
        return score

    def _evaluate_window(self, window, player):
        """评估一个窗口(五元组)的价值"""
        window = list(window)
        my_count = window.count(player)
        opponent_count = window.count(3 - player)
        empty_count = window.count(0)

        if my_count > 0 and opponent_count > 0: return 0
        if my_count == 0 and opponent_count == 0: return 1

        if my_count == 5: return self.patterns['FIVE']
        if my_count == 4 and empty_count == 1: return self.patterns['OPEN_FOUR']
        if my_count == 3 and empty_count == 2: return self.patterns['OPEN_THREE']
        if my_count == 3 and empty_count == 1: return self.patterns['RUSH_THREE']
        if my_count == 2 and empty_count == 3: return self.patterns['OPEN_TWO']
        
        # 简化冲四的判断
        if my_count == 4 and opponent_count == 0: return self.patterns['RUSH_FOUR']

        return 0
    
    def _check_urgent_moves(self, state):
        """检查并返回必胜或必须防守的棋"""
        valid_actions = state.get_valid_actions()
        opponent_id = 3 - self.player_id

        # 检查自己是否有必胜棋
        for action in valid_actions:
            state_copy = state.clone()
            state_copy.step(action)
            if state_copy.get_winner() == self.player_id:
                return action
        
        # 检查对手是否有必胜棋 (需要防守)
        for action in valid_actions:
            state_copy = state.clone()
            state_copy.board[action] = opponent_id
            if state_copy.get_winner() == opponent_id:
                return action
        
        return None