from typing import Any

class GreedyPongAI:
    """Pong 贪婪挡板 AI。

    根据球的当前位置与挡板 y 坐标的差值，简单地向上或向下移动，
    也可保持不动。此 AI 不需要环境信息，仅基于游戏对象。"""

    def __init__(self, game: Any, player_id: int = 2, speed: int = 5):
        self.game = game
        self.player_id = player_id
        self.speed = speed

    def get_action(self) -> int:
        """返回动作：-1 向上，1 向下，0 不动"""
        # 挡板对象
        paddle = self.game.p2 if self.player_id == 2 else self.game.p1
        ball = self.game.ball

        if ball.y < paddle.y - 5:
            return -1  # 向上
        elif ball.y > paddle.y + 5:
            return 1   # 向下
        else:
            return 0   # 不动 