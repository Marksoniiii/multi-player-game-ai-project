import time
import numpy as np
from agents.base_agent import BaseAgent
# 使用Minimax算法的AI Bot
class MinimaxBot(BaseAgent):
    """
    一个经过优化的Minimax AI Bot。
    核心改进在于其“启发式评估函数”，使其能更准确地判断局势。
    """
    def __init__(self, name="MinimaxBot", player_id=1, max_depth=3, use_alpha_beta=True, timeout=5):
        super().__init__(name, player_id)
        self.max_depth = max_depth
        self.use_alpha_beta = use_alpha_beta
        self.timeout = timeout
        self._start_time = None

    def get_action(self, observation, env):
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            return None

        self._start_time = time.time()
        
        # 优先选择能直接获胜或必须防守的位置
        # 1. 检查自己是否有必胜点
        for action in valid_actions:
            if self._is_winning_move(env.game, action, self.player_id):
                return action
        # 2. 检查对手是否有必胜点，进行防守
        opponent_id = 3 - self.player_id
        for action in valid_actions:
            if self._is_winning_move(env.game, action, opponent_id):
                return action
        
        best_score = float('-inf')
        best_action = valid_actions[0]
        
        # 动态深度调整：棋盘越空，深度越大
        empty_count = len(valid_actions)
        depth = 1
        if empty_count > 200:
            depth = 1
        elif empty_count > 150:
            depth = 2
        else:
            depth = self.max_depth

        for action in valid_actions:
            game_copy = env.game.clone()
            game_copy.step(action) # AI先走一步
            
            # 轮到对手走棋
            score = self.minimax(game_copy, depth - 1, False, float('-inf'), float('inf'))
            
            if score > best_score:
                best_score = score
                best_action = action
            
            if time.time() - self._start_time > self.timeout:
                break
                
        return best_action

    def minimax(self, game, depth, is_maximizing_player, alpha, beta):
        if depth == 0 or game.is_terminal() or (self._start_time and time.time() - self._start_time > self.timeout):
            return self.evaluate(game)

        valid_actions = game.get_valid_actions()
        if not valid_actions:
            return self.evaluate(game)

        if is_maximizing_player:
            max_eval = float('-inf')
            for action in valid_actions:
                game_copy = game.clone()
                game_copy.step(action)
                eval = self.minimax(game_copy, depth - 1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else: # Minimizing player
            min_eval = float('inf')
            for action in valid_actions:
                game_copy = game.clone()
                game_copy.step(action)
                eval = self.minimax(game_copy, depth - 1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate(self, game):
        """
        核心评估函数。
        正分代表对AI有利，负分代表对人类玩家有利。
        """
        winner = game.get_winner()
        if winner == self.player_id:
            return 100000  # AI赢
        elif winner == (3 - self.player_id):
            return -100000 # AI输
        
        my_score = self.calculate_player_score(game.board, self.player_id)
        opponent_score = self.calculate_player_score(game.board, 3 - self.player_id)
        
        # 最终分数是自己的分数减去对手的分数
        return my_score - opponent_score

    def calculate_player_score(self, board, player):
        """
        计算单个玩家在当前棋盘上的分数。
        这是通过识别不同的棋形并给予相应权重来实现的。
        """
        score = 0
        # 定义棋形和对应的分数
        score_patterns = {
            10000: [(player, player, player, player, player)], # 五连
            4000: [(0, player, player, player, player, 0)],   # 活四
            800: [(player, player, player, player, 0), (0, player, player, player, player)], # 冲四
            400: [(0, player, player, player, 0)],         # 活三
            80: [(player, player, player, 0, 0), (0, 0, player, player, player)], # 眠三
            40: [(0, player, player, 0, 0), (0, 0, player, player, 0)], # 活二
            8: [(player, player, 0, 0, 0), (0, 0, 0, player, player)]  # 眠二
        }

        board_str = ''.join(map(str, board.flatten()))
        
        # 在整个棋盘上扫描所有方向的棋形
        size = board.shape[0]
        directions = [(1,0), (0,1), (1,1), (1,-1)] # 水平, 垂直, 主对角线, 副对角线
        
        for r in range(size):
            for c in range(size):
                for dr, dc in directions:
                    line = ""
                    pos_list = []
                    for i in range(-5, 6): # 检查一个足够长的窗口
                        cur_r, cur_c = r + i * dr, c + i * dc
                        if 0 <= cur_r < size and 0 <= cur_c < size:
                            line += str(board[cur_r, cur_c])
                            pos_list.append((cur_r, cur_c))

                    for value, patterns in score_patterns.items():
                        for pattern in patterns:
                            pattern_str = ''.join(map(str, pattern))
                            if pattern_str in line:
                                score += value
                            # 检查反向棋形
                            reversed_pattern_str = pattern_str[::-1]
                            if reversed_pattern_str in line:
                                score += value
        return score
        
    def _is_winning_move(self, game, action, player):
        """检查某一步是否是制胜步"""
        game_copy = game.clone()
        game_copy.board[action[0], action[1]] = player
        return game_copy.get_winner() == player