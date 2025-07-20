# 文件路径: snake_gui.py
import pygame
import sys
import time
from typing import Dict, Any
from games.snake import SnakeEnv
from agents import RandomBot
from agents.ai_bots.snake_ai import SnakeAI, BasicSnakeAI

COLORS = {
    'WHITE': (255, 255, 255), 'BLACK': (0, 0, 0), 'RED': (255, 0, 0),
    'BLUE': (0, 0, 255), 'GREEN': (0, 255, 0), 'GRAY': (128, 128, 128),
    'DARK_GRAY': (64, 64, 64), 'YELLOW': (255, 255, 0), 'ORANGE': (255, 165, 0),
    'CYAN': (0, 200, 200), 'PINK': (255, 150, 150)
}

class SnakeGUI:
    """贪吃蛇图形界面 """
    
    def __init__(self):
        pygame.init()
        self.board_size = 20
        self.cell_size = 25
        self.margin = 50
        self.ui_width = 200
        
        self.window_width = self.board_size * self.cell_size + self.margin * 2 + self.ui_width
        self.window_height = self.board_size * self.cell_size + self.margin * 2
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Snake AI Battle")
        self.clock = pygame.time.Clock()
        
        # 初始化支持中文的字体
        self.font_large = self._init_font(36)
        self.font_medium = self._init_font(24)
        self.font_small = self._init_font(20)
        
        self.env = SnakeEnv(board_size=self.board_size)
        self.selected_ai_name = "Basic AI"
        self.ai_agent = BasicSnakeAI(name=self.selected_ai_name, player_id=2)
        
        self.human_direction = (0, 1)
        self.game_over = False
        self.winner = None
        self.paused = False
        
        self.buttons = self._create_buttons()
        self.last_update_time = time.time()
        self.update_interval = 0.15  # 游戏速度，可以调
        
        self.reset_game()
    
    def _create_buttons(self) -> Dict[str, Dict[str, Any]]:
        btn_w, btn_h = 160, 40
        start_x = self.board_size * self.cell_size + self.margin * 2 + (self.ui_width - btn_w) // 2
        
        return {
            'basic_ai': {'rect': pygame.Rect(start_x, 50, btn_w, btn_h), 'text': 'Basic AI', 'agent': BasicSnakeAI},
            'smart_ai': {'rect': pygame.Rect(start_x, 100, btn_w, btn_h), 'text': 'Smart AI', 'agent': SnakeAI},
            'random_ai': {'rect': pygame.Rect(start_x, 150, btn_w, btn_h), 'text': 'Random AI', 'agent': RandomBot},
            'new_game': {'rect': pygame.Rect(start_x, 220, btn_w, btn_h), 'text': 'New Game', 'color': COLORS['GREEN']},
            'pause': {'rect': pygame.Rect(start_x, 270, btn_w, btn_h), 'text': 'Pause', 'color': COLORS['ORANGE']},
            'quit': {'rect': pygame.Rect(start_x, 320, btn_w, btn_h), 'text': 'Quit', 'color': COLORS['RED']}
        }

    def _init_font(self, size: int):
        """初始化支持中文的字体"""
        # 尝试多种中文字体
        chinese_fonts = [
            'simhei',      # 黑体
            'simsun',      # 宋体
            'yahei',       # 雅黑
            'microsoftyahei',  # 微软雅黑
            'dengxian',    # 等线
            'kaiti',       # 楷体
            'fangsong',    # 仿宋
            'arial unicode ms',  # Arial Unicode MS
            'noto sans cjk sc',  # Noto Sans CJK SC
        ]
        
        # 首先尝试系统字体
        for font_name in chinese_fonts:
            try:
                font = pygame.font.SysFont(font_name, size)
                # 测试是否能渲染中文
                test_surface = font.render("测试", True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    return font
            except:
                continue
        
        # 如果所有中文字体都失败，尝试默认字体
        try:
            return pygame.font.SysFont('arial', size)
        except:
            # 最后的备用选项
            return pygame.font.Font(None, size)

    def reset_game(self):
        self.env.reset()
        self.human_direction = (0, 1)
        self.game_over = False
        self.winner = None
        self.paused = False
        self.buttons['pause']['text'] = 'Pause'
        self.last_update_time = time.time()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update_game()
            self.draw()
            self.clock.tick(30)
        pygame.quit()
        sys.exit()

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                self.paused = not self.paused
                self.buttons['pause']['text'] = 'Resume' if self.paused else 'Pause'
            if not self.paused and not self.game_over:
                if event.type == pygame.KEYDOWN:
                    self._handle_snake_input(event.key)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_button_click(event.pos)
        return True

    def _handle_button_click(self, mouse_pos):
        for name, info in self.buttons.items():
            if info['rect'].collidepoint(mouse_pos):
                if name.endswith('_ai'):
                    self.selected_ai_name = info['text']
                    self.ai_agent = info['agent'](name=self.selected_ai_name, player_id=2)
                    self.reset_game()
                elif name == 'new_game': self.reset_game()
                elif name == 'pause':
                    self.paused = not self.paused
                    self.buttons['pause']['text'] = 'Resume' if self.paused else 'Pause'
                elif name == 'quit': pygame.quit(); sys.exit()

    def _handle_snake_input(self, key):
        key_map = {
            pygame.K_UP: (-1, 0), pygame.K_w: (-1, 0),
            pygame.K_DOWN: (1, 0), pygame.K_s: (1, 0),
            pygame.K_LEFT: (0, -1), pygame.K_a: (0, -1),
            pygame.K_RIGHT: (0, 1), pygame.K_d: (0, 1)
        }
        if key in key_map:
            new_dir = key_map[key]
            # 禁止180度掉头
            if new_dir[0] != -self.env.game.direction1[0] or new_dir[1] != -self.env.game.direction1[1]:
                self.human_direction = new_dir

    def update_game(self):
        if self.game_over or self.paused:
            return

        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval:
            self.last_update_time = current_time
            state = self.env.game.get_state()
            # 统一传递两个参数，兼容所有AI
            try:
                ai_action = self.ai_agent.get_action(state, self.env)
            except TypeError:
                # 兼容只接受一个参数的AI
                ai_action = self.ai_agent.get_action(state)
            actions = {1: self.human_direction, 2: ai_action}
            # 【已修复】正确接收来自 env.step 的5个返回值，修复崩溃问题
            _, _, terminated, truncated, _ = self.env.step(actions)
            if terminated or truncated:
                self.game_over = True
                self.winner = self.env.get_winner()

    def draw(self):
        self.screen.fill(COLORS['DARK_GRAY'])
        self._draw_board()
        self._draw_ui()
        pygame.display.flip()

    def _draw_board(self):
        board_rect = pygame.Rect(self.margin, self.margin, self.board_size * self.cell_size, self.board_size * self.cell_size)
        pygame.draw.rect(self.screen, COLORS['BLACK'], board_rect)
        
        state = self.env.game.get_state()
        board = state['board']
        for r in range(self.board_size):
            for c in range(self.board_size):
                rect = pygame.Rect(self.margin + c * self.cell_size, self.margin + r * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (30, 30, 30), rect, 1)
                
                colors = {1: COLORS['BLUE'], 2: COLORS['CYAN'], 3: COLORS['RED'], 4: COLORS['PINK'], 5: COLORS['GREEN']}
                if board[r, c] != 0:
                    pygame.draw.rect(self.screen, colors[board[r, c]], rect.inflate(-4, -4), border_radius=3)

    def _draw_ui(self):
        ui_x = self.board_size * self.cell_size + self.margin * 2
        
        for name, info in self.buttons.items():
            color = info.get('color', COLORS['GRAY'])
            if name.endswith('_ai') and info['text'] == self.selected_ai_name:
                color = COLORS['YELLOW']
            pygame.draw.rect(self.screen, color, info['rect'], border_radius=8)
            text_surf = self.font_medium.render(info['text'], True, COLORS['BLACK'])
            self.screen.blit(text_surf, text_surf.get_rect(center=info['rect'].center))

        state = self.env.game.get_state()
        status_y = 380
        status_texts = [
            f"You (Blue): {len(state['snake1'])} ({'Alive' if state['alive1'] else 'Dead'})",
            f"AI (Red): {len(state['snake2'])} ({'Alive' if state['alive2'] else 'Dead'})",
            f"Moves: {state['move_count']}"
        ]
        for i, text in enumerate(status_texts):
            self.screen.blit(self.font_small.render(text, True, COLORS['WHITE']), (ui_x + 10, status_y + i * 25))

        msg, color = "", COLORS['WHITE']
        if self.game_over:
            winner_map = {1: ("You Win!", COLORS['GREEN']), 2: ("AI Wins!", COLORS['RED']), -1: ("It's a Draw!", COLORS['YELLOW'])}
            msg, color = winner_map.get(self.winner, ("Game Over", COLORS['WHITE']))
        elif self.paused:
            msg, color = "Paused", COLORS['ORANGE']
        
        if msg:
            board_center_x = self.margin + self.board_size * self.cell_size / 2
            text_surf = self.font_large.render(msg, True, color)
            self.screen.blit(text_surf, text_surf.get_rect(center=(board_center_x, self.margin / 2)))


if __name__ == '__main__':
    gui = SnakeGUI()
    gui.run()