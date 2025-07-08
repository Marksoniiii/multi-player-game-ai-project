"""
MCTS Bot
使用蒙特卡洛树搜索算法 - 完善最终版
"""

import time
import random
import math
from typing import Dict, Any, Optional

from agents.base_agent import BaseAgent
from agents.ai_bots.minimax_bot import MinimaxBot # 导入评估器，用于高质量模拟
import config

class MCTSNode:
    """
    蒙特卡洛树搜索的节点。
    每个节点代表一个游戏状态。
    """
    def __init__(self, game_state, parent=None, action=None):
        """
        初始化一个MCTS节点。
        
        Args:
            game_state: 当前节点代表的游戏状态 (一个BaseGame的克隆实例)。
            parent: 父节点 (MCTSNode)。
            action: 到达此状态所执行的动作。
        """
        self.state = game_state
        self.parent = parent
        self.action = action
        self.children = []
        self.wins = 0  # 从此节点出发，父节点玩家获胜的次数
        self.visits = 0 # 此节点被访问的总次数
        self.untried_actions = self.state.get_valid_actions() # 获取所有未尝试的合法动作

    def select_child(self, exploration_constant: float) -> 'MCTSNode':
        """
        使用UCT (UCB1 for Trees) 公式选择最佳子节点。
        这个公式平衡了对已知好节点的利用（exploit）和对未知节点的探索（explore）。
        
        Args:
            exploration_constant: 探索常数，用于调整探索的权重。
            
        Returns:
            得分最高的子节点。
        """
        best_score = -1
        best_child = None
        for child in self.children:
            if child.visits == 0:
                # 优先选择从未被访问过的节点
                return child
            
            # UCT公式
            exploit = child.wins / child.visits  # 利用项：胜率
            explore = exploration_constant * math.sqrt(math.log(self.visits) / child.visits) # 探索项
            score = exploit + explore
            
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    def expand(self) -> 'MCTSNode':
        """
        从未尝试的动作中扩展一个新的子节点。
        
        Returns:
            新创建的子节点。
        """
        action = self.untried_actions.pop(0) # 选择一个未尝试的动作
        next_state = self.state.clone() # 克隆当前状态以模拟下一步
        next_state.step(action)
        child_node = MCTSNode(next_state, parent=self, action=action)
        self.children.append(child_node)
        return child_node

    def update(self, result: float):
        """
        用模拟结果更新当前节点。
        
        Args:
            result: 模拟游戏的结果（1为胜利, 0.5为平局, 0为失败）。
        """
        self.visits += 1
        self.wins += result


class MCTSBot(BaseAgent):
    """
    一个经过优化的蒙特卡洛树搜索（MCTS）智能体。
    
    核心改进：
    1.  **启发式模拟**: 使用Minimax的评估函数代替纯随机模拟，极大提升了模拟质量和AI棋力。
    2.  **健壮的反向传播**: 修复了反向传播逻辑，确保节点价值被正确更新。
    3.  **即时胜负判断**: 优先检查一步之内就能获胜或必须防守的棋步。
    """
    def __init__(self, name: str = "MCTSBot", player_id: int = 1, simulation_count: int = 1000):
        super().__init__(name, player_id)
        ai_config = config.AI_CONFIGS.get('mcts', {})
        self.simulation_count = ai_config.get('simulation_count', simulation_count)
        self.exploration_constant = ai_config.get('exploration_constant', 1.414)
        self.timeout = ai_config.get('timeout', 10)
        # 创建一个评估器，用于在模拟阶段提供启发式指导
        self.evaluator = MinimaxBot(player_id=self.player_id)

    # vvvvvvvvvvv  替换下面的 get_action 方法 vvvvvvvvvvvvvvvvv
    def get_action(self, observation: Any, env: Any) -> Any:
        print(f">>> MCTS Bot 思考开始！模拟次数设置为: {self.simulation_count} <<<")
        start_time = time.time()

        root = MCTSNode(game_state=env.game.clone())

        # --- 增强的威胁评估逻辑 ---
        # 1. 检查自己是否有“活四”或更高分的制胜点
        my_critical_move = self._find_critical_move(root.state, self.player_id)
        if my_critical_move:
            print("MCTS 发现制胜点!")
            return my_critical_move

        # 2. 检查对手是否有“活四”等关键威胁点，必须立即防守
        opponent_id = 3 - self.player_id
        opponent_critical_move = self._find_critical_move(root.state, opponent_id)
        if opponent_critical_move:
            print("MCTS 发现必须防守的关键点!")
            return opponent_critical_move
        # --- 威胁评估结束 ---

        for i in range(self.simulation_count):
            if time.time() - start_time > self.timeout:
                print(f"MCTS 超时，已完成 {i} 次模拟")
                break
                
            node = root
            
            # 1. 选择 (Selection)
            while not node.untried_actions and node.children:
                node = node.select_child(self.exploration_constant)
                
            # 2. 扩展 (Expansion)
            if node.untried_actions:
                node = node.expand()
                
            # 3. 模拟 (Simulation)
            winner = self._heuristic_simulate(node.state)
            
            # 4. 反向传播 (Backpropagation)
            self._backpropagate(node, winner)

        if not root.children:
            valid_actions = env.get_valid_actions()
            return random.choice(valid_actions) if valid_actions else None

        # 选择访问次数最多的子节点作为最终决策
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.action
    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


    def _heuristic_simulate(self, state) -> Optional[int]:
        """
        使用Minimax评估函数进行启发式模拟，代替纯随机走子。
        这会模拟未来几步，并返回一个更有可能的游戏结局。
        """
        temp_state = state.clone()
        for _ in range(15): # 模拟的深度可以调整
            if temp_state.is_terminal():
                break

            valid_actions = temp_state.get_valid_actions()
            if not valid_actions:
                break
            
            best_action = None
            best_score = -float('inf')
            
            # 设置评估器的玩家ID为当前模拟状态的玩家
            self.evaluator.player_id = temp_state.current_player
            
            # 遍历所有合法动作，选择评估分数最高的一个
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
        从叶节点开始，向上反向传播模拟结果，更新路径上所有节点的统计信息。
        """
        current_node = node
        while current_node is not None:
            current_node.visits += 1
            # 节点的价值是从其父节点的视角来评估的。
            # 因此，需要判断获胜方是否是当前节点的“上一步”玩家（即父节点的玩家）。
            parent_player_id = 3 - current_node.state.current_player
            if winner == parent_player_id:
                current_node.wins += 1.0 # 胜利得1分
            elif winner is None: # 平局得0.5分
                current_node.wins += 0.5
            
            current_node = current_node.parent

    def _find_immediate_win(self, state, player_id: int) -> Optional[Any]:
        """寻找并返回一步就能获胜的动作。"""
        for action in state.get_valid_actions():
            next_state = state.clone()
            next_state.step(action)
            if next_state.get_winner() == player_id:
                return action
        return None
    
    # vvvvvvvvvvv  在 MCTSBot 类中新增下面的辅助方法 vvvvvvvvvvvvvvvvv
    def _find_critical_move(self, state, player_id):
        """
        寻找关键落子点（如活四、冲四等高分棋形）。
        这比原版只检查是否五子连珠的 get_winner() 方法要强大得多。
        """
        valid_actions = state.get_valid_actions()
        
        # 获取当前局势下该玩家的分数
        initial_score = self.evaluator.calculate_player_score(state.board, player_id)
        
        # 定义一个分数阈值，活四的分数是4000
        CRITICAL_SCORE_INCREASE = 3500 

        for action in valid_actions:
            # 检查落子是否在棋盘内且为空
            if state.board[action[0]][action[1]] != 0:
                continue

            temp_board = state.board.copy()
            temp_board[action[0], action[1]] = player_id # 模拟落子
            
            # 计算落子后的分数
            new_score = self.evaluator.calculate_player_score(temp_board, player_id)
            
            # 如果分数增量巨大（意味着形成了强大的棋形，如活四）
            if (new_score - initial_score) >= CRITICAL_SCORE_INCREASE:
                return action
            
        return None
    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^