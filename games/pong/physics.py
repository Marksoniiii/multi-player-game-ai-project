# games/pong/physics.py

class Ball:
    def __init__(self, x, y, vx, vy, radius=5):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.radius = radius

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

class Paddle:
    def __init__(self, x, y, width=10, height=60, speed=200):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.speed = speed

    def move(self, direction, dt, field_height):
        self.y += direction * self.speed * dt
        max_y = field_height - self.height / 2
        min_y = self.height / 2
        self.y = max(min_y, min(max_y, self.y))
