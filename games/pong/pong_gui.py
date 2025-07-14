import pygame
import sys
import time

# 修正模块导入路径，以便脚本能直接运行
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from games.pong.pong_game import PongGame
from agents.ai_bots.greedy_pong_ai import GreedyPongAI

# 基本设置
WIDTH, HEIGHT = 800, 600
# 更新颜色方案，使其更具现代感和对比度
DARK_BLUE = (20, 20, 40)
LIGHT_BLUE = (173, 216, 230) # 用于球、拍子和文字
ACCENT_COLOR = (255, 200, 0) # 用于强调得分和时间

FPS = 60

class PongGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pong Game - Enhanced") # 更新窗口标题
        self.clock = pygame.time.Clock()
        
        # 尝试使用不同的字体或更大的字号
        self.font_large = pygame.font.SysFont("Arial", 48, bold=True) # 标题字体
        self.font_medium = pygame.font.SysFont("Arial", 36) # 菜单选项字体
        self.font_small = pygame.font.SysFont("Arial", 30) # 得分和时间字体

        self.menu_active = True
        self.ai_mode = False
        self.running = True
        self.game = PongGame(WIDTH, HEIGHT)
        self.ai = None
        self.actions = {1: 0, 2: 0}

    def show_menu(self):
        self.screen.fill(DARK_BLUE) # 菜单背景色

        # 标题和选项使用不同的字体和颜色
        title = self.font_large.render("PONG - Game Menu", True, LIGHT_BLUE)
        mode1 = self.font_medium.render("1 - Two Players (W/S & ↑/↓)", True, LIGHT_BLUE)
        mode2 = self.font_medium.render("2 - Player vs AI (W/S controls left)", True, LIGHT_BLUE)
        restart = self.font_medium.render("R - Restart", True, LIGHT_BLUE)
        quit_game = self.font_medium.render("Q - Quit", True, LIGHT_BLUE)

        # 调整菜单项的垂直间距，使其更美观
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100)) # 标题更高
        self.screen.blit(mode1, (WIDTH // 2 - mode1.get_width() // 2, 200))
        self.screen.blit(mode2, (WIDTH // 2 - mode2.get_width() // 2, 260))
        self.screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, 320))
        self.screen.blit(quit_game, (WIDTH // 2 - quit_game.get_width() // 2, 380))
        
        pygame.display.flip()

    def reset_game(self):
        self.game = PongGame(WIDTH, HEIGHT)  # 完全重启游戏，重置计时和分数
        if self.ai_mode:
            self.ai = GreedyPongAI(self.game, player_id=2)
        else:
            self.ai = None
        self.actions = {1: 0, 2: 0}

    def handle_events(self):
        self.actions = {1: 0, 2: 0}
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if self.menu_active:
                    if event.key == pygame.K_1:
                        self.ai_mode = False
                        self.menu_active = False
                        self.reset_game()
                    elif event.key == pygame.K_2:
                        self.ai_mode = True
                        self.menu_active = False
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        self.running = False
                else:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    # 在游戏进行中按下Q键也可以退出
                    elif event.key == pygame.K_q:
                        self.running = False


        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.actions[1] = -1
        elif keys[pygame.K_s]:
            self.actions[1] = 1

        if not self.ai_mode:
            if keys[pygame.K_UP]:
                self.actions[2] = -1
            elif keys[pygame.K_DOWN]:
                self.actions[2] = 1

    def draw(self):
        self.screen.fill(DARK_BLUE) # 游戏背景色

        # 中线 - 虚线效果，更美观
        for i in range(0, HEIGHT, 20): # 每隔20像素绘制一个短线
            pygame.draw.line(self.screen, LIGHT_BLUE, (WIDTH // 2, i), (WIDTH // 2, i + 10), 2)

        # 球拍 - 使用 LIGHT_BLUE
        for paddle in [self.game.p1, self.game.p2]:
            pygame.draw.rect(self.screen, LIGHT_BLUE, pygame.Rect(
                paddle.x - paddle.width // 2,
                paddle.y - paddle.height // 2,
                paddle.width,
                paddle.height
            ))

        # 球 - 使用 LIGHT_BLUE
        ball = self.game.ball
        pygame.draw.circle(self.screen, LIGHT_BLUE, (int(ball.x), int(ball.y)), ball.radius)

        # 得分 - 使用 ACCENT_COLOR，字体更大
        score_text = self.font_medium.render(f"{self.game.score[1]} : {self.game.score[2]}", True, ACCENT_COLOR)
        # 调整得分位置，使其更居中且不与时间重叠
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

        # 倒计时 - 使用 ACCENT_COLOR，字体更大
        time_left = max(0, int(self.game.game_duration - (time.time() - self.game.start_time)))
        time_text = self.font_small.render(f"Time: {time_left}s", True, ACCENT_COLOR)
        # 调整时间位置
        self.screen.blit(time_text, (WIDTH - time_text.get_width() - 30, 20)) # 距离右侧更远

        pygame.display.flip()

    def show_winner(self):
        winner = self.game.get_winner()
        if winner == 0:
            msg = "Draw!"
        else:
            msg = f"Player {winner} Wins!"

        result = self.font_large.render(msg, True, ACCENT_COLOR) # 胜者信息使用大字体和强调色
        self.screen.fill(DARK_BLUE) # 胜者界面背景色
        self.screen.blit(result, (
            WIDTH // 2 - result.get_width() // 2,
            HEIGHT // 2 - result.get_height() // 2
        ))
        pygame.display.flip()
        pygame.time.wait(3000)

    def run(self):
        while self.running:
            if self.menu_active:
                self.show_menu()
                self.handle_events()
            else:
                self.handle_events()

                # AI 控制
                if self.ai_mode and self.ai:
                    self.actions[2] = self.ai.get_action()

                self.game.step(self.actions)
                self.draw()

                if self.game.is_terminal():
                    self.show_winner()
                    self.reset_game() # 重置游戏状态，以便下次从菜单开始新局
                    self.menu_active = True

            self.clock.tick(FPS)

if __name__ == "__main__":
    gui = PongGUI()
    gui.run()
