import numpy as np
import random
from agents.base_agent import BaseAgent

class MinimaxBot(BaseAgent):
    """
    A bot using the Minimax algorithm with Alpha-Beta Pruning.
    """
    # The __init__ function is updated to correctly handle parameters from the GUI.
    # It now properly calls the parent class's constructor.
    # **kwargs allows it to accept extra arguments (like 'name') without crashing.
    def __init__(self, player, board_size, search_depth=3, env=None, **kwargs):
        super().__init__(player)  # This correctly sets up the player attribute.
        self.board_size = board_size
        self.search_depth = search_depth
        self.env = env

    def get_action(self, state):
        """
        Uses the Minimax algorithm to find the best action.
        """
        # The AI gets the current state directly from its environment.
        _, best_action = self.minimax(self.search_depth, -np.inf, np.inf, True)
        return tuple(best_action) if best_action is not None else None

    def minimax(self, depth, alpha, beta, maximizing_player):
        """
        The core recursive Minimax function.
        It now correctly uses self.env to simulate and undo moves.
        """
        # Check for terminal state (depth limit or game over)
        if depth == 0 or self.env.is_game_over():
            return self.evaluate_board(self.env.game.board), None

        valid_actions = self.env.get_valid_actions()
        # If no valid moves, return current evaluation
        if len(valid_actions) == 0:
            return self.evaluate_board(self.env.game.board), None

        best_action = random.choice(valid_actions)

        if maximizing_player:
            max_eval = -np.inf
            for action in valid_actions:
                self.env.step(action)
                evaluation, _ = self.minimax(depth - 1, alpha, beta, False)
                self.env.undo()
                if evaluation > max_eval:
                    max_eval = evaluation
                    best_action = action
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break  # Alpha-Beta Pruning
            return max_eval, best_action
        else:  # Minimizing player
            min_eval = np.inf
            for action in valid_actions:
                self.env.step(action)
                evaluation, _ = self.minimax(depth - 1, alpha, beta, True)
                self.env.undo()
                if evaluation < min_eval:
                    min_eval = evaluation
                    best_action = action
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break  # Alpha-Beta Pruning
            return min_eval, best_action

    def evaluate_board(self, board):
        """
        Heuristic evaluation function for the Gomoku board state.
        A better evaluation function is key to a stronger AI.
        """
        # (The evaluation function remains the same as the previous version)
        score = 0
        player = self.player
        opponent = 3 - player

        def check_line(line):
            player_score = 0
            opponent_score = 0
            # Check for player's patterns
            for i in range(len(line) - 4):
                window = list(line[i:i+5])
                if window.count(player) == 5: return 100000 # Win
                if window.count(player) == 4 and window.count(0) == 1: player_score += 1000 # Live four
                if window.count(player) == 3 and window.count(0) == 2: player_score += 100  # Live three
                if window.count(player) == 2 and window.count(0) == 3: player_score += 10   # Live two

            # Check for opponent's patterns to block
            for i in range(len(line) - 4):
                window = list(line[i:i+5])
                if window.count(opponent) == 5: return -500000 # Loss
                if window.count(opponent) == 4 and window.count(0) == 1: opponent_score += 5000 # Block opponent's live four
                if window.count(opponent) == 3 and window.count(0) == 2: opponent_score += 500  # Block opponent's live three

            return player_score - opponent_score

        # Evaluate all rows, columns, and diagonals
        for r in range(self.board_size):
            score += check_line(board[r, :])
        for c in range(self.board_size):
            score += check_line(board[:, c])
        for d in range(-self.board_size + 5, self.board_size - 4):
            score += check_line(np.diag(board, k=d))
            score += check_line(np.diag(np.fliplr(board), k=d))

        return score