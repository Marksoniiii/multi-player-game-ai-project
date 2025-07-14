import random
import time
from games.pong.physics import Ball, Paddle

FIELD_WIDTH = 800
FIELD_HEIGHT = 600
PADDLE_OFFSET = 30

class PongGame:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.ball = Ball(x=width // 2, y=height // 2, vx=200, vy=200)
        self.p1 = Paddle(x=PADDLE_OFFSET, y=height // 2)
        self.p2 = Paddle(x=width - PADDLE_OFFSET, y=height // 2)
        self.score = {1: 0, 2: 0}
        self.terminal = False
        self.max_score = 10

        # 新增游戏时长及拍子缩短机制
        self.start_time = time.time()        # 游戏开始时间（只初始化一次）
        self.game_duration = 60              # 总游戏时长秒数
        self.last_shrink_time = self.start_time
        self.paddle_shrink_interval = 10    # 每10秒拍子缩短一次
        self.min_paddle_height = 30         

    def reset(self):
        self.ball = Ball(FIELD_WIDTH / 2, FIELD_HEIGHT / 2,
                         vx=random.choice([-200, 200]),
                         vy=random.uniform(-100, 100))
        self.p1 = Paddle(PADDLE_OFFSET, FIELD_HEIGHT / 2)
        self.p2 = Paddle(FIELD_WIDTH - PADDLE_OFFSET, FIELD_HEIGHT / 2)
        self.score = {1: 0, 2: 0}
        self.terminal = False
        # 注意：不要重置 start_time，保持游戏总时长一致
        self.last_shrink_time = time.time()

    def step(self, action):
        dt = 0.016
        self.p1.move(action.get(1, 0), dt, FIELD_HEIGHT)
        self.p2.move(action.get(2, 0), dt, FIELD_HEIGHT)
        self.ball.update(dt)
        self.handle_collisions()

        now = time.time()
        # 拍子每隔10秒缩短
        if now - self.last_shrink_time >= self.paddle_shrink_interval:
            self.last_shrink_time = now
            for paddle in [self.p1, self.p2]:
                if paddle.height > self.min_paddle_height:
                    paddle.height -= 5

        # 超过游戏总时长则终止游戏
        if now - self.start_time >= self.game_duration:
            self.terminal = True

        return self.get_observation()

    def handle_collisions(self):
        # 撞击上下边界反弹
        if self.ball.y - self.ball.radius <= 0 or self.ball.y + self.ball.radius >= FIELD_HEIGHT:
            self.ball.vy *= -1

        # 撞击球拍反弹，且速度加快10%
        for paddle, player in [(self.p1, 1), (self.p2, 2)]:
            if abs(self.ball.x - paddle.x) < paddle.width and \
               paddle.y - paddle.height / 2 < self.ball.y < paddle.y + paddle.height / 2:
                self.ball.vx *= -1.1
                offset = (self.ball.y - paddle.y) / (paddle.height / 2)
                self.ball.vy += offset * 100

        # 判断得分，不重置游戏开始时间
        if self.ball.x < 0:
            self.score[2] += 1
            self.reset_ball_and_paddles()
        elif self.ball.x > FIELD_WIDTH:
            self.score[1] += 1
            self.reset_ball_and_paddles()

    def reset_ball_and_paddles(self):
        # 重置球和拍子位置，不重置计时和得分
        self.ball = Ball(FIELD_WIDTH / 2, FIELD_HEIGHT / 2,
                         vx=random.choice([-200, 200]),
                         vy=random.uniform(-100, 100))
        self.p1 = Paddle(PADDLE_OFFSET, FIELD_HEIGHT / 2, height=self.p1.height)
        self.p2 = Paddle(FIELD_WIDTH - PADDLE_OFFSET, FIELD_HEIGHT / 2, height=self.p2.height)

    def get_observation(self):
        return {
            'ball': (self.ball.x, self.ball.y, self.ball.vx, self.ball.vy),
            'paddles': {1: self.p1.y, 2: self.p2.y},
            'score': self.score.copy()
        }

    def get_valid_actions(self, player_id):
        return [-1, 0, 1]

    def is_terminal(self):
        return self.terminal

    def get_winner(self):
        if self.score[1] > self.score[2]:
            return 1
        elif self.score[2] > self.score[1]:
            return 2
        else:
            return 0  # 平局
