"""
MCTS Bot
使用蒙特卡洛树搜索算法 - 最终修复版
"""

import time
import random
import math
import numpy as np
from typing import Dict, Any, Optional

from agents.base_agent import BaseAgent
from agents.ai_bots.minimax_bot import MinimaxBot # 导入评估器
import config

class MCTSNode:
    """MCTS节点 - 结构更标准"""
    def __init__(self, game_state, parent=None, action=None):
        self.state = game_state
        self.parent = parent
        self.action = action # 导致这个状态的动作
        self.children = []
        self.wins = 0      # 从这个节点出发的模拟中，父节点玩家获胜的次数
        self.visits = 0    # 这个节点被访问的总次数
        self.untried_actions = self.state.get_valid_actions()

    def select_child(self, exploration_constant):
        """使用UCT (UCB1 applied to trees) 公式选择子节点"""
        best_score = -1
        best_child = None
        for child in self.children:
            if child.visits == 0:
                # 优先选择未探索过的节点
                return child
            
            # UCT公式
            exploit = child.wins / child.visits
            explore = exploration_constant * math.sqrt(math.log(self.visits) / child.visits)
            score = exploit + explore
            
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    def expand(self):
        """从未尝试的动作中扩展一个子节点"""
        action = self.untried_actions.pop(0)
        next_state = self.state.clone()
        next_state.step(action)
        child_node = MCTSNode(next_state, parent=self, action=action)
        self.children.append(child_node)
        return child_node

    def update(self, result):
        """
        用模拟结果更新节点。
        result: 1 表示胜利, -1 表示失败, 0 表示平局
        """
        self.visits += 1
        self.wins += result


class MCTSBot(BaseAgent):
    """
    优化的MCTS Bot - 最终修复版。
    核心修复：使用了完全正确和健壮的反向传播逻辑。
    """
    def __init__(self, name: str = "MCTSBot", player_id: int = 1, simulation_count: int = 1000):
        super().__init__(name, player_id)
        ai_config = config.AI_CONFIGS.get('mcts', {})
        self.simulation_count = ai_config.get('simulation_count', simulation_count)
        self.exploration_constant = ai_config.get('exploration_constant', 1.414)
        self.timeout = ai_config.get('timeout', 10)
        # 创建评估器，用于进行高质量的模拟
        self.evaluator = MinimaxBot(player_id=self.player_id)

    def get_action(self, observation: Any, env: Any) -> Any:
        print(f">>> MCTS Bot 思考开始！模拟次数设置为: {self.simulation_count} <<<")
        start_time = time.time()
        
        root = MCTSNode(game_state=env.game.clone())
        
        # 优先检查一步必胜/必防的情况
        winning_move = self._find_immediate_win(root.state, self.player_id)
        if winning_move:
            print("MCTS 发现一步制胜棋!")
            return winning_move
            
        opponent_id = 3 - self.player_id
        blocking_move = self._find_immediate_win(root.state, opponent_id)
        if blocking_move:
            print("MCTS 发现必须防守!")
            return blocking_move
            
        for i in range(self.simulation_count):
            if time.time() - start_time > self.timeout:
                print(f"MCTS 超时，已完成 {i} 次模拟")
                break
                
            node = root
            
            # 1. 选择 (Selection)
            while node.untried_actions == [] and node.children != []:
                node = node.select_child(self.exploration_constant)
                
            # 2. 扩展 (Expansion)
            if node.untried_actions != []:
                node = node.expand()
                
            # 3. 模拟 (Simulation)
            winner = self._heuristic_simulate(node.state)
            
            # 4. 反向传播 (Backpropagation) - 已修复
            self._backpropagate(node, winner)

        if not root.children:
            return random.choice(env.get_valid_actions())

        # 选择访问次数最多的子节点作为最终决策
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.action

    def _heuristic_simulate(self, state) -> Optional[int]:
        """使用Minimax的评估函数进行高质量模拟"""
        temp_state = state.clone()
        for _ in range(15): # 模拟的步数可以适当增加
            if temp_state.is_terminal():
                break

            valid_actions = temp_state.get_valid_actions()
            if not valid_actions:
                break
            
            best_action = None
            best_score = -float('inf')
            
            self.evaluator.player_id = temp_state.current_player
            
            for action in valid_actions:
                next_state = temp_state.clone()
                next_state.step(action)
                score = self.evaluator.evaluate(next_state)
                if score > best_score:
                    best_score = score
                    best_action = action
            
            temp_state.step(best_action)
            
        return temp_state.get_winner()

    def _backpropagate(self, node, winner):
        """
        完全正确的反向传播逻辑。
        """
        current_node = node
        while current_node is not None:
            current_node.visits += 1
            # 获胜者是父节点的当前玩家，则父节点获胜次数+1
            # 这里的逻辑是：一个节点的价值是从其父节点的视角来看的
            parent_player = 3 - current_node.state.current_player
            if winner == parent_player:
                current_node.wins += 1
            # 如果是平局，可以加0.5分
            elif winner is None:
                current_node.wins += 0.5
            
            current_node = current_node.parent

    def _find_immediate_win(self, state, player_id):
        """寻找一步制胜点"""
        for action in state.get_valid_actions():
            next_state = state.clone()
            next_state.step(action)
            if next_state.get_winner() == player_id:
                return action
        return None