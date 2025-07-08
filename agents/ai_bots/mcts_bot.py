"""
MCTS Bot - 最后修复版
"""
import time
import random
import math
from typing import Dict, Any, Optional, List, Tuple

from agents.base_agent import BaseAgent
from agents.ai_bots.minimax_bot import MinimaxBot # 导入评估器
import config

# MCTSNode 类的定义保持不变
class MCTSNode:
    """MCTS节点 - 结构更标准"""
    def __init__(self, game_state, parent=None, action=None):
        self.state = game_state
        self.parent = parent
        self.action = action
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_actions = self.state.get_valid_actions()

    def select_child(self, exploration_constant):
        """使用UCT (UCB1 applied to trees) 公式选择子节点"""
        best_score = -1
        best_child = None
        for child in self.children:
            if child.visits == 0:
                return child
            
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

# --- MCTSBot 主类 ---
class MCTSBot(BaseAgent):
    """
    终极版MCTS Bot
    1.  **强大的紧急威胁评估**：在搜索前检查连五、活四、双三等关键棋形。
    2.  **时间预算搜索**：在固定时间内尽可能多地模拟，保证响应速度。
    3.  **启发式模拟**：使用Minimax评估函数指导模拟，提升模拟质量。
    4.  **健壮的反向传播**：确保节点价值被正确更新。
    """
    # ==================== BUG修复点 ====================
    # 在参数列表中增加了 **kwargs，以接收并忽略所有多余的参数（如旧的 simulation_count）
    def __init__(self, name: str = "MCTSBot", player_id: int = 1, **kwargs):
        super().__init__(name, player_id)
        ai_config = config.AI_CONFIGS.get('mcts', {})
        self.timeout = ai_config.get('timeout', 5.0) 
        self.exploration_constant = ai_config.get('exploration_constant', 1.414)
        self.evaluator = MinimaxBot(player_id=self.player_id)

    def get_action(self, observation: Any, env: Any) -> Any:
        start_time = time.time()
        root_state = env.game.clone()
        
        # 1. 紧急威胁评估 (强化直觉)
        urgent_move = self._find_urgent_move(root_state)
        if urgent_move:
            print(f"MCTS AI ({self.name}) 发现紧急棋步: {urgent_move}")
            return urgent_move

        # 2. MCTS搜索 (时间预算内深度思考)
        root_node = MCTSNode(root_state)
        
        simulation_count = 0
        while time.time() - start_time < self.timeout:
            node = root_node
            
            # --- 选择 (Selection) ---
            while not node.untried_actions and node.children:
                node = node.select_child(self.exploration_constant)
            
            # --- 扩展 (Expansion) ---
            if node.untried_actions:
                node = node.expand()
            
            # --- 模拟 (Simulation) ---
            winner = self._heuristic_simulate(node.state)
            
            # --- 反向传播 (Backpropagation) ---
            self._backpropagate(node, winner)
            
            simulation_count += 1

        elapsed_time = time.time() - start_time
        print(f">>> MCTS Bot ({self.name}) 在 {elapsed_time:.2f}s 内完成了 {simulation_count} 次模拟。")
        
        # 3. 最终决策
        if not root_node.children:
            return random.choice(env.get_valid_actions())

        best_child = max(root_node.children, key=lambda c: c.visits)
        return best_child.action

    def _find_urgent_move(self, state) -> Optional[Tuple[int, int]]:
        """按优先级顺序查找最紧急的落子点（连五、活四、双三等）"""
        valid_actions = state.get_valid_actions()
        my_id = self.player_id
        opponent_id = 3 - my_id

        priority_list = [
            {'player': my_id, 'score_ge': 10000, 'desc': "我方连五"},
            {'player': opponent_id, 'score_ge': 10000, 'desc': "对方连五"},
            {'player': my_id, 'score_ge': 4000, 'desc': "我方活四"},
            {'player': opponent_id, 'score_ge': 4000, 'desc': "对方活四"},
            {'player': my_id, 'score_ge': 800, 'desc': "我方双三"},
            {'player': opponent_id, 'score_ge': 800, 'desc': "对方双三"},
        ]

        for priority in priority_list:
            player = priority['player']
            threshold = priority['score_ge']
            
            initial_score = self.evaluator.calculate_player_score(state.board, player)
            
            for action in valid_actions:
                temp_board = state.board.copy()
                temp_board[action[0], action[1]] = player
                
                new_score = self.evaluator.calculate_player_score(temp_board, player)
                
                if (new_score - initial_score) >= threshold:
                    print(f"    紧急评估发现: {priority['desc']} @ {action}")
                    return action
        return None

    def _heuristic_simulate(self, state) -> Optional[int]:
        """使用Minimax评估函数进行高质量模拟"""
        temp_state = state.clone()
        for _ in range(10): 
            if temp_state.is_terminal():
                break

            valid_actions = temp_state.get_valid_actions()
            if not valid_actions:
                break
            
            best_action = None
            best_score = -float('inf')
            
            self.evaluator.player_id = temp_state.current_player
            
            for action in valid_actions:
                next_state_eval = temp_state.clone()
                next_state_eval.step(action)
                score = self.evaluator.evaluate(next_state_eval)
                if score > best_score:
                    best_score = score
                    best_action = action
            
            if best_action:
                temp_state.step(best_action)
            else: 
                break
            
        return temp_state.get_winner()

    def _backpropagate(self, node, winner):
        """完全正确的反向传播逻辑"""
        current_node = node
        while current_node is not None:
            current_node.visits += 1
            parent_player_id = 3 - current_node.state.current_player
            if winner == parent_player_id:
                current_node.wins += 1.0
            elif winner is None:
                current_node.wins += 0.5
            
            current_node = current_node.parent