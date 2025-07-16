import time
import random
import numpy as np
from agents.base_agent import BaseAgent

class MinimaxBot(BaseAgent):
    """
    Minimax AI Bot - 平衡性能与智能
    
    核心特性:
    1. 迭代深化搜索 (Iterative Deepening)
    2. 高效的Alpha-Beta剪枝
    3. 置换表 (Transposition Table) 以缓存棋局评估
    4. 基于棋形识别的高级启发式评估函数
    5. 智能走法排序以优化剪枝效率
    """
    # 初始化方法：设置 Bot 的名称、玩家 ID、最大搜索深度 (max_depth) 和每次决策的最长时间 (timeout)。
    def __init__(self, name="MinimaxBot", player_id=1, max_depth=4, timeout=5):
        super().__init__(name, player_id)
        self.max_depth = max_depth
        self.timeout = timeout
        self._start_time = None
        self.transposition_table = {}
        
        # 棋形和对应分数
        self.patterns = {
            'FIVE': 100000, # 五连
            'OPEN_FOUR': 10000, # 活四
            'RUSH_FOUR': 5000, # 冲四
            'OPEN_THREE': 2000, #  活三
            'RUSH_THREE': 800, # 冲三
            'OPEN_TWO': 400, # 活二
            'RUSH_TWO': 100, # 冲二
            'BLOCKED_ONE': 5 # 被堵活一
        }
        
        self.zobrist_table = None # 置换表

    def _init_zobrist(self, board_size):
        """初始化Zobrist哈希表"""
        if self.zobrist_table is None:
            self.zobrist_table = np.random.randint(2**63, size=(board_size, board_size, 2), dtype=np.uint64)

    def _compute_zobrist_hash(self, board):
        """计算当前棋盘的Zobrist哈希值"""
        h = np.uint64(0)
        if self.zobrist_table is None:
             return h # 如果未初始化则返回0

        for r in range(board.shape[0]):
            for c in range(board.shape[1]):
                if board[r, c] != 0:
                    player_idx = board[r, c] - 1
                    h ^= self.zobrist_table[r, c, player_idx]
        return h

    def get_action(self, observation, env):
        """通过迭代深化搜索获取最佳动作"""
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            return None
        
        self._init_zobrist(env.game.board.shape[0])
        self._start_time = time.time()
        
        # 紧急检查：直接获胜或必须防守
        critical_move = self._find_critical_move(env.game, valid_actions)
        if critical_move:
            return critical_move

        best_action = valid_actions[0]
        
        # 迭代深化搜索
        for depth in range(1, self.max_depth + 1):
            if time.time() - self._start_time > self.timeout:
                break
                
            current_best_action, best_score = self._search_at_depth(env.game, valid_actions, depth)
            
            if current_best_action is not None:
                best_action = current_best_action
            
            # 如果找到必胜局，提前返回
            if best_score >= self.patterns['FIVE']:
                break
        
        return best_action

    def _search_at_depth(self, game, valid_actions, depth):
        """在指定深度进行搜索"""
        best_score = float('-inf')
        best_action = None
        
        # 走法排序
        sorted_actions = self._sort_moves(game, valid_actions)

        for action in sorted_actions:
            if time.time() - self._start_time > self.timeout:
                break
            
            game_copy = game.clone()
            game_copy.step(action)
            
            score = self._minimax(game_copy, depth - 1, False, float('-inf'), float('inf'))
            
            if score > best_score:
                best_score = score
                best_action = action
        
        return best_action, best_score

    def _find_critical_move(self, game, valid_actions):
        """检查是否存在一步获胜或必须防守的棋"""
        # 检查自己是否能一步获胜
        for action in valid_actions:
            game_copy = game.clone()
            game_copy.step(action)
            if game_copy.get_winner() == self.player_id:
                return action
        
        # 检查对手是否能一步获胜，从而必须防守
        opponent_id = 3 - self.player_id
        for action in valid_actions:
            game_copy = game.clone()
            game_copy.board[action[0], action[1]] = opponent_id
            if game_copy.get_winner() == opponent_id:
                game_copy.board[action[0], action[1]] = 0 # reset
                return action
        
        return None

    def _sort_moves(self, game, actions):
        """启发式走法排序"""
        move_scores = []
        for action in actions:
            score = self._evaluate_move_heuristic(game, action)
            move_scores.append((score, action))
        
        move_scores.sort(key=lambda x: x[0], reverse=True)
        return [action for score, action in move_scores]

    def _evaluate_move_heuristic(self, game, action):
        """快速评估一个走法的启发式价值"""
        score = 0
        r, c = action
        
        # 评估己方下这步棋的价值
        game.board[r, c] = self.player_id
        score += self._evaluate_position(game.board, self.player_id)
        
        # 评估对手下这步棋的价值（防守价值）
        game.board[r, c] = 3 - self.player_id
        score += self._evaluate_position(game.board, 3 - self.player_id)
        
        game.board[r, c] = 0 # 恢复棋盘
        
        # 增加中心位置的权重
        center = game.board.shape[0] // 2
        score += (center - (abs(r - center) + abs(c - center))) * 10
        
        return score

    def _minimax(self, game, depth, is_maximizing, alpha, beta):
        """带有置换表优化的Minimax算法"""
        # 时间和深度检查
        if time.time() - self._start_time > self.timeout or depth == 0 or game.is_terminal():
            return self.evaluate(game) or 0
        
        # 置换表查找
        board_hash = self._compute_zobrist_hash(game.board)
        if board_hash in self.transposition_table:
            cached = self.transposition_table[board_hash]
            if cached.get('depth', -1) >= depth:
                return cached.get('score', 0)
        
        valid_actions = game.get_valid_actions()
        if not valid_actions:
            return self.evaluate(game) or 0

        sorted_actions = self._sort_moves(game, valid_actions)

        if is_maximizing:
            max_eval = float('-inf')
            for action in sorted_actions:
                game_copy = game.clone()
                game_copy.step(action)
                eval_score = self._minimax(game_copy, depth - 1, False, alpha, beta) or 0
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            
            self.transposition_table[board_hash] = {'depth': depth, 'score': max_eval}
            return max_eval
        else:
            min_eval = float('inf')
            for action in sorted_actions:
                game_copy = game.clone()
                game_copy.step(action)
                eval_score = self._minimax(game_copy, depth - 1, True, alpha, beta) or 0
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
                    
            self.transposition_table[board_hash] = {'depth': depth, 'score': min_eval}
            return min_eval

    def evaluate(self, game):
        """高级启发式评估函数"""
        winner = game.get_winner()
        if winner is not None:
            if winner == self.player_id: return self.patterns['FIVE']
            if winner == 3 - self.player_id: return -self.patterns['FIVE']
            return 0 # 平局

        my_score = self._evaluate_position(game.board, self.player_id)
        opponent_score = self._evaluate_position(game.board, 3 - self.player_id)
        return (my_score or 0) - (opponent_score or 0)

    def _evaluate_position(self, board, player) -> int:
        """评估指定玩家在当前棋局的分数"""
        score = 0
        board_size = board.shape[0]
        
        # 遍历所有可能的五元组
        for r in range(board_size):
            for c in range(board_size):
                # 水平
                if c <= board_size - 5:
                    window = [board[r, c+i] for i in range(5)]
                    score += self._evaluate_window(window, player)
                # 垂直
                if r <= board_size - 5:
                    window = [board[r+i, c] for i in range(5)]
                    score += self._evaluate_window(window, player)
                # 主对角线
                if r <= board_size - 5 and c <= board_size - 5:
                    window = [board[r+i, c+i] for i in range(5)]
                    score += self._evaluate_window(window, player)
                # 副对角线
                if r <= board_size - 5 and c >= 4:
                    window = [board[r+i, c-i] for i in range(5)]
                    score += self._evaluate_window(window, player)
        return score

    def _evaluate_window(self, window, player):
        """评估一个五元组窗口的价值"""
        my_count = window.count(player)
        opponent_count = window.count(3 - player)
        empty_count = window.count(0)

        if my_count > 0 and opponent_count > 0:
            return 0 # 混合窗口，无价值

        if my_count == 0 and opponent_count == 0:
            return 1 # 全空，一点潜力分
            
        if my_count == 5: return self.patterns['FIVE']
        if my_count == 4 and empty_count == 1: return self.patterns['OPEN_FOUR']
        if my_count == 4 and empty_count == 0: return self.patterns['RUSH_FOUR'] # Technically, this is part of a FIVE
        if my_count == 3 and empty_count == 2: return self.patterns['OPEN_THREE']
        if my_count == 3 and empty_count == 1: return self.patterns['RUSH_THREE']
        if my_count == 2 and empty_count == 3: return self.patterns['OPEN_TWO']
        if my_count == 2 and empty_count == 2: return self.patterns['RUSH_TWO']
        if my_count == 1 and empty_count == 4: return self.patterns['BLOCKED_ONE']

        return 0