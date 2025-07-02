"""
MCTS Bot
使用蒙特卡洛树搜索算法
"""

import time
import random
import math
from typing import Dict, List, Tuple, Any, Optional
from agents.base_agent import BaseAgent
import config
import copy
from agents.ai_bots.minimax_bot import MinimaxBot

class MCTSBot(BaseAgent):
    def __init__(self, name: str = "MCTSBot", player_id: int = 1, simulation_count: int = 300):
        super().__init__(name, player_id)
        ai_config = config.AI_CONFIGS.get('mcts', {})
        self.simulation_count = ai_config.get('simulation_count', simulation_count)
        self.timeout = ai_config.get('timeout', 10)
        self.evaluator = MinimaxBot(name="Eval", player_id=self.player_id)

class MCTSNode:
    """MCTS节点"""
    
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.untried_actions = self._get_untried_actions()
    
    def _get_untried_actions(self):
        """获取未尝试的动作"""
        if hasattr(self.state, 'get_valid_actions'):
            return self.state.get_valid_actions()
        return []
    
    def is_fully_expanded(self):
        """检查是否完全展开"""
        return len(self.untried_actions) == 0
    
    def is_terminal(self):
        """检查是否为终止节点"""
        if hasattr(self.state, 'is_terminal'):
            return self.state.is_terminal()
        return False
    
    def get_winner(self):
        """获取获胜者"""
        if hasattr(self.state, 'get_winner'):
            return self.state.get_winner()
        return None
    
    def clone_state(self):
        """克隆状态"""
        if hasattr(self.state, 'clone'):
            return self.state.clone()
        return self.state


class MCTSBot(BaseAgent):
    """MCTS Bot"""
    
    def __init__(self, name: str = "MCTSBot", player_id: int = 1, 
                 simulation_count: int = 300):
        super().__init__(name, player_id)
        ai_config = config.AI_CONFIGS.get('mcts', {})
        self.simulation_count = ai_config.get('simulation_count', simulation_count)
        self.timeout = ai_config.get('timeout', 10)
        self.evaluator = MinimaxBot(name="Eval", player_id=self.player_id)
    
    def get_action(self, observation: Any, env: Any) -> Any:
        """
        使用MCTS选择动作
        
        Args:
            observation: 当前观察
            env: 环境对象
            
        Returns:
            选择的动作
        """
        start_time = time.time()
        root = MCTSNode(env.game.clone())
        for _ in range(self.simulation_count):
            node = root
            state = node.clone_state()
            # 选择
            while node.is_fully_expanded() and not node.is_terminal():
                node = self._select_child(node)
                state = node.clone_state()
            # 扩展
            if not node.is_terminal() and node.untried_actions:
                action = node.untried_actions.pop()
                state.step(action)
                child = MCTSNode(state.clone(), parent=node, action=action)
                node.children.append(child)
                node = child
            # 模拟
            reward = self._simulate(state)
            # 回传
            self._backpropagate(node, reward)
            if time.time() - start_time > self.timeout:
                break
        # 选择访问次数最多的动作
        best_child = max(root.children, key=lambda c: c.visits, default=None)
        return best_child.action if best_child else random.choice(env.get_valid_actions())

    def _select_child(self, node):
        # UCB1公式
        log_N = math.log(node.visits + 1)
        C = math.sqrt(2)
        def ucb(child):
            if child.visits == 0:
                return float('inf')
            return child.value / child.visits + C * math.sqrt(log_N / child.visits)
        return max(node.children, key=ucb)

    def _simulate(self, state):
        # 启发式模拟到终局：优先选择评估分数最高的点
        player = state.current_player

        while not state.is_terminal():
            valid_actions = state.get_valid_actions()
            if not valid_actions:
                break

            best_action = None
            best_score = -float('inf')

            # 从所有可选布子点中，选一个对自己最有利的
            for action in valid_actions:
                temp_state = state.clone()
                temp_state.step(action)
                # 使用Minimax的评估函数来打分
                score = self.evaluator.evaluate(temp_state)
                # 因为minimax的评估函数是基于自己减去对手，所以需要根据当前模拟的玩家调整
                if player != self.player_id:
                    score = -score

                if score > best_score:
                    best_score = score
                    best_action = action

            if best_action:
                state.step(best_action)
            else:
                # 如果没有可选动作，则随机走
                state.step(random.choice(valid_actions))

        winner = state.get_winner()
        if winner == self.player_id:
            return 1
        elif winner is not None:
            return -1
        else:
            return 0
    def _simple_heuristic(self, state, player, opponent):
        # 简单启发式：连四>连三>连二，惩罚对方连四
        board = state.board if hasattr(state, 'board') else state.get_state()['board']
        def count_line(b, p, n):
            count = 0
            size = b.shape[0]
            for i in range(size):
                for j in range(size):
                    if b[i, j] != p:
                        continue
                    # 横向
                    if j + n <= size and all(b[i, j+k] == p for k in range(n)):
                        count += 1
                    # 纵向
                    if i + n <= size and all(b[i+k, j] == p for k in range(n)):
                        count += 1
                    # 主对角线
                    if i + n <= size and j + n <= size and all(b[i+k, j+k] == p for k in range(n)):
                        count += 1
                    # 副对角线
                    if i + n <= size and j - n + 1 >= 0 and all(b[i+k, j-k] == p for k in range(n)):
                        count += 1
            return count
        score = 0
        score += count_line(board, player, 4) * 100
        score += count_line(board, player, 3) * 10
        score += count_line(board, player, 2) * 2
        score -= count_line(board, opponent, 4) * 120
        return score

    def _backpropagate(self, node, reward):
        while node is not None:
            node.visits += 1
            node.value += reward
            node = node.parent

    def reset(self):
        """重置MCTS Bot"""
        super().reset()
    
    def get_info(self) -> Dict[str, Any]:
        """获取MCTS Bot信息"""
        info = super().get_info()
        info.update({
            'type': 'MCTS',
            'description': '使用蒙特卡洛树搜索的Bot',
            'strategy': f'MCTS with {self.simulation_count} simulations',
            'timeout': self.timeout
        })
        return info