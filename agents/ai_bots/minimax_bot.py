from agents.base_agent import BaseAgent
import time
import numpy as np

class MinimaxBot(BaseAgent):
    """
    A bot using the Minimax algorithm with Alpha-Beta Pruning.
    """
    # The __init__ function is updated to correctly handle parameters from the GUI.
    # It now properly calls the parent class's constructor.
    # **kwargs allows it to accept extra arguments (like 'name') without crashing.
    def __init__(self, name="MinimaxBot", player_id=1, max_depth=3, use_alpha_beta=True, timeout=5):
        super().__init__(name, player_id)
        self.max_depth = max_depth
        self.use_alpha_beta = use_alpha_beta
        self.timeout = timeout
        self._start_time = None

    def get_action(self, observation, env):
        """
        Uses the Minimax algorithm to find the best action.
        """
        # 兼容 observation 既可能是 dict 也可能是 ndarray
        if isinstance(observation, dict):
            board = observation.get('board', None)
        else:
            board = observation
        if board is not None:
            print(f"[MinimaxBot] get_action: board type={type(board)}, shape={getattr(board, 'shape', None)}")
            if not isinstance(board, np.ndarray):
                board = np.array(board)
            if isinstance(observation, dict):
                observation['board'] = board
            else:
                observation = board
        try:
            valid_actions = env.get_valid_actions()
            if not valid_actions:
                return None
            best_score = float('-inf')
            best_action = valid_actions[0]
            self._start_time = time.time()
            empty_count = np.sum(board == 0)
            depth = min(self.max_depth, 2 + empty_count // 30)
            for action in valid_actions:
                game_copy = env.game.clone()
                game_copy.step(action)
                if self.use_alpha_beta:
                    score = self.minimax(game_copy, depth - 1, False, float('-inf'), float('inf'))
                else:
                    score = self.minimax(game_copy, depth - 1, False)
                if score > best_score:
                    best_score = score
                    best_action = action
                if time.time() - self._start_time > self.timeout:
                    break
            return best_action
        except Exception as e:
            print(f"[MinimaxBot] get_action error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def minimax(self, game, depth, maximizing, alpha=None, beta=None):
        """
        The core recursive Minimax function.
        It now correctly uses self.env to simulate and undo moves.
        """
        # Check for terminal state (depth limit or game over)
        if depth == 0 or game.is_terminal() or (self._start_time and time.time() - self._start_time > self.timeout):
            return self.evaluate(game)
        valid_actions = game.get_valid_actions()
        if not valid_actions:
            return 0
        if maximizing:
            max_score = float('-inf')
            for action in valid_actions:
                game_copy = game.clone()
                game_copy.step(action)
                score = self.minimax(game_copy, depth - 1, False, alpha, beta)
                max_score = max(max_score, score)
                if alpha is not None:
                    alpha = max(alpha, score)
                    if beta is not None and beta <= alpha:
                        break
            return max_score
        else:
            min_score = float('inf')
            for action in valid_actions:
                game_copy = game.clone()
                game_copy.step(action)
                score = self.minimax(game_copy, depth - 1, True, alpha, beta)
                min_score = min(min_score, score)
                if beta is not None:
                    beta = min(beta, score)
                    if alpha is not None and beta <= alpha:
                        break
            return min_score

    def evaluate(self, game):
        """
        Heuristic evaluation function for the Gomoku board state.
        A better evaluation function is key to a stronger AI.
        """
        try:
            board = game.board if hasattr(game, 'board') else game.get_state()['board']
            if not isinstance(board, np.ndarray):
                board = np.array(board)
            player = self.player_id
            opponent = 3 - player
            if game.get_winner() == player:
                return 100000
            elif game.get_winner() == opponent:
                return -100000
            my_patterns = self.pattern_counts(board, player)
            opp_patterns = self.pattern_counts(board, opponent)
            score = 0
            score += my_patterns['five'] * 100000
            score += my_patterns['live_four'] * 10000
            score += my_patterns['rush_four'] * 3000
            score += my_patterns['live_three'] * 500
            score += my_patterns['sleep_three'] * 100
            score += my_patterns['live_two'] * 50
            score += my_patterns['sleep_two'] * 10
            score -= opp_patterns['five'] * 100000
            score -= opp_patterns['live_four'] * 12000
            score -= opp_patterns['rush_four'] * 4000
            score -= opp_patterns['live_three'] * 800
            score -= opp_patterns['sleep_three'] * 200
            score -= opp_patterns['live_two'] * 80
            score -= opp_patterns['sleep_two'] * 20
            return score
        except Exception as e:
            print(f"[MinimaxBot] evaluate error: {e}")
            import traceback
            traceback.print_exc()
            return 0

    def pattern_counts(self, board, player):
        size = board.shape[0]
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        patterns = {
            'five': 0, 'live_four': 0, 'rush_four': 0,
            'live_three': 0, 'sleep_three': 0,
            'live_two': 0, 'sleep_two': 0
        }
        for i in range(size):
            for j in range(size):
                for dx, dy in directions:
                    line = []
                    for k in range(-1, 6):
                        x, y = int(i + k*dx), int(j + k*dy)
                        if 0 <= x < size and 0 <= y < size:
                            line.append(int(board[x, y]))
                        else:
                            line.append(-1)
                    if len(line) < 7:
                        continue
                    for start in range(2):
                        if start+6 >= len(line):
                            continue
                        window = line[start+1:start+6]
                        left = line[start]
                        right = line[start+6]
                        if len(window) != 5:
                            continue
                        if window.count(player) == 5:
                            patterns['five'] += 1
                        elif window.count(player) == 4 and window.count(0) == 1:
                            if left == 0 or right == 0:
                                if left == 0 and right == 0:
                                    patterns['live_four'] += 1
                                else:
                                    patterns['rush_four'] += 1
                            else:
                                patterns['rush_four'] += 1
                        elif window.count(player) == 3 and window.count(0) == 2:
                            if left == 0 and right == 0:
                                patterns['live_three'] += 1
                            else:
                                patterns['sleep_three'] += 1
                        elif window.count(player) == 2 and window.count(0) == 3:
                            if left == 0 and right == 0:
                                patterns['live_two'] += 1
                            else:
                                patterns['sleep_two'] += 1
        return patterns