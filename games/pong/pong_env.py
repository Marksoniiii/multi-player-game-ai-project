# games/pong/pong_env.py

from games.pong.pong_game import PongGame

class PongEnv:
    def __init__(self, window_width=800, window_height=600):
        self.game = PongGame(width=window_width, height=window_height)

    def reset(self):
        return self.game.reset()

    def step(self, actions):
        return self.game.step(actions)

    def get_valid_actions(self, player_id):
        return self.game.get_valid_actions(player_id)

    def is_terminal(self):
        return self.game.is_terminal()

    def get_winner(self):
        return self.game.get_winner()

    def update_paddle_position(self, y_pos):
        """更新玩家挡板位置"""
        if hasattr(self.game, 'p1'):
            self.game.p1.y = y_pos
