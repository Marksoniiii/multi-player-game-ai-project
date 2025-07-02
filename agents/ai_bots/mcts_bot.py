"""
MCTS Bot
使用蒙特卡洛树搜索算法 - 优化版
"""

import time
import random
import math
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from agents.base_agent import BaseAgent
# 导入我们强大的MinimaxBot，目的是为了使用它的评估函数
from agents.ai_bots.minimax_bot import MinimaxBot
import config
import copy


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
        if hasattr(self.state, 'get_valid_actions'):
            # 返回一个可修改的列表副本
            return list(self.state.get_valid_actions())
        return []
    
    def is_fully_expanded(self):
        return len(self.untried_actions) == 0
    
    def is_terminal(self):
        if hasattr(self.state, 'is_terminal'):
            return self.state.is_terminal()
        return False
    
    def get_winner(self):
        if hasattr(self.state, 'get_winner'):
            return self.state.get_winner()
        return None
    
    def clone_state(self):
        if hasattr(self.state, 'clone'):
            return self.state.clone()
        return copy.deepcopy(self.state)


class MCTSBot(BaseAgent):
    """
    优化的MCTS Bot。
    核心改进：
    1. 使用了Minimax的强大评估函数来指导模拟过程，提升模拟质量。
    2. 增加了模拟次数的默认值。
    """
    
    def __init__(self, name: str = "MCTSBot", player_id: int = 1, 
                 simulation_count: int = 500): # 设置默认模拟次数
        super().__init__(name, player_id)
        ai_config = config.AI_CONFIGS.get('mcts', {})
        self.simulation_count = ai_config.get('simulation_count', simulation_count)
        self.timeout = ai_config.get('timeout', 10)
        # 创建一个MinimaxBot实例，我们只使用它的评估函数
        self.evaluator = MinimaxBot(player_id=self.player_id)
    
    def get_action(self, observation: Any, env: Any) -> Any:
        start_time = time.time()
        # 创建一个根节点，其状态是当前游戏状态的深拷贝
        root_state = env.game.clone()
        root = MCTSNode(root_state)

        # 在给定的模拟次数或时间内进行搜索
        for i in range(self.simulation_count):
            if time.time() - start_time > self.timeout:
                print(f"MCTS timeout after {self.simulation_count} simulations")
                break
            
            node = root
            state_copy = root.clone_state()

            # 1. 选择 (Selection)
            while node.is_fully_expanded() and not node.is_terminal():
                node = self._select_child(node)
                state_copy.step(node.action)

            # 2. 扩展 (Expansion)
            if not node.is_fully_expanded() and not node.is_terminal():
                action = random.choice(node.untried_actions)
                node.untried_actions.remove(action)
                state_copy.step(action)
                child_node = MCTSNode(state_copy.clone(), parent=node, action=action)
                node.children.append(child_node)
                node = child_node

            # 3. 模拟 (Simulation) - 使用了新的、更智能的模拟策略
            reward = self._heuristic_simulate(state_copy)

            # 4. 回传 (Backpropagation)
            self._backpropagate(node, reward)

        # 选择访问次数最多的子节点作为最佳动作
        if not root.children:
            return random.choice(env.get_valid_actions())
        
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.action

    def _select_child(self, node: MCTSNode) -> MCTSNode:
        """使用UCB1公式选择最佳子节点"""
        log_total_visits = math.log(node.visits)
        best_score = -float('inf')
        best_child = None

        for child in node.children:
            if child.visits == 0:
                return child # 优先扩展未被访问过的节点
            
            # UCB1公式
            win_rate = child.value / child.visits
            exploration_term = math.sqrt(2 * log_total_visits / child.visits)
            score = win_rate + exploration_term
            
            if score > best_score:
                best_score = score
                best_child = child
                
        return best_child

    def _heuristic_simulate(self, state) -> int:
        """
        使用Minimax的评估函数进行启发式模拟。
        这比纯随机模拟要智能得多。
        """
        # 最多模拟几步，防止模拟时间过长
        for _ in range(10): 
            if state.is_terminal():
                break

            valid_actions = state.get_valid_actions()
            if not valid_actions:
                break

            best_action = None
            best_score = -float('inf')
            
            # 从所有可选落子点中，选一个对当前玩家最有利的
            # 这里的“有利”是由Minimax的评估函数判断的
            current_player = state.current_player
            self.evaluator.player_id = current_player # 确保评估器以当前玩家视角评估

            for action in valid_actions:
                temp_state = state.clone()
                temp_state.step(action)
                score = self.evaluator.evaluate(temp_state)
                
                if score > best_score:
                    best_score = score
                    best_action = action
            
            state.step(best_action)
        
        # 返回最终局面的结果
        winner = state.get_winner()
        if winner == self.player_id:
            return 1  # 赢了
        elif winner is not None:
            return -1 # 输了
        else:
            return 0  # 平局

    def _backpropagate(self, node: MCTSNode, reward: int):
        """将模拟结果反向传播更新父节点"""
        current_player_of_parent = (3 - node.state.current_player)
        
        while node is not None:
            node.visits += 1
            # 奖励需要根据节点是为哪一方玩家服务的来更新
            if node.state.current_player != current_player_of_parent:
                node.value += reward
            else:
                node.value -= reward
            
            node = node.parent
            if node:
                current_player_of_parent = (3 - node.state.current_player)

    def reset(self):
        super().reset()
    
    def get_info(self) -> Dict[str, Any]:
        info = super().get_info()
        info.update({
            'type': 'MCTS',
            'description': '使用蒙特卡洛树搜索的Bot',
            'strategy': f'MCTS with {self.simulation_count} simulations and heuristic simulation',
            'timeout': self.timeout
        })
        return info