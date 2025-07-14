# agents/ai_bots/greedy_bot.py

from agents.base_agent import BaseAgent

class GreedyPongAI(BaseAgent):
    def __init__(self, name="GreedyPongAI", player_id=1):
        super().__init__(name, player_id)

    def get_action(self, observation, env):
        ball_x, ball_y, vx, vy = observation['ball']
        own_y = observation['paddles'][self.player_id]

        # 预测球是否向自己这一侧
        if (self.player_id == 1 and vx < 0) or (self.player_id == 2 and vx > 0):
            # 时间 = horizontal distance / |vx|
            target_x = env.game.p1.x if self.player_id == 1 else env.game.p2.x
            dt = abs((ball_x - target_x) / vx)
            predicted_y = ball_y + vy * dt
            # 碰壁反弹效果
            predicted_y %= (2 * env.game.FIELD_HEIGHT)
            if predicted_y > env.game.FIELD_HEIGHT:
                predicted_y = 2*env.game.FIELD_HEIGHT - predicted_y

            # 简单贪心：移动方向
            if predicted_y > own_y + 5:
                return 1
            elif predicted_y < own_y - 5:
                return -1
        return 0

