"""
贪吃蛇游戏专用GUI
简化版本，专注于贪吃蛇游戏
"""

import pygame
import sys
import time
import os
from typing import Optional, Tuple, Dict, Any
from games.snake import SnakeGame, SnakeEnv
from agents import RandomBot, SnakeAI, SmartSnakeAI, HumanAgent

# 颜色定义
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (255, 0, 0),
    'BLUE': (0, 0, 255),
    'GREEN': (0, 255, 0),
    'GRAY': (128, 128, 128),
    'LIGHT_GRAY': (211, 211, 211),
    'DARK_GRAY': (64, 64, 64),
    'YELLOW': (255, 255, 0),
    'ORANGE': (255, 165, 0),
    'CYAN': (0, 255, 255)
}

class SnakeGUI:
    """贪吃蛇图形界面"""
    
    def __init__(self):
        # 初始化pygame
        pygame.init()
        
        self.board_size = 20
        self.cell_size = 25
        self.margin = 50
        
        self.window_width = self.board_size * self.cell_size + self.margin * 2 + 300
        self.window_height = self.board_size * self.cell_size + self.margin * 2
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Snake AI Battle")
        self.clock = pygame.time.Clock()
        
        # 字体 - 使用默认字体避免中文问题
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # 游戏状态
        self.env = SnakeEnv(board_size=self.board_size)
        self.human_agent = HumanAgent(name="Human Player", player_id=1)
        self.ai_agent = SnakeAI(name="Snake AI", player_id=2)
        self.current_agent = self.human_agent
        self.game_over = False
        self.winner = None
        self.thinking = False
        self.selected_ai = "SnakeAI"
        self.paused = False
        
        # UI元素
        self.buttons = self._create_buttons()
        
        # 游戏计时
        self.last_update = time.time()
        self.update_interval = 0.3  # 300ms更新一次
        
        self.reset_game()
    
    def _create_buttons(self) -> Dict[str, Dict[str, Any]]:
        """创建UI按钮"""
        button_width = 120
        button_height = 30
        start_x = self.board_size * self.cell_size + self.margin + 20
        
        buttons = {
            # AI选择
            'snake_ai': {
                'rect': pygame.Rect(start_x, 50, button_width, button_height),
                'text': 'Basic AI',
                'color': COLORS['YELLOW']
            },
            'smart_ai': {
                'rect': pygame.Rect(start_x, 90, button_width, button_height),
                'text': 'Smart AI',
                'color': COLORS['LIGHT_GRAY']
            },
            'random_ai': {
                'rect': pygame.Rect(start_x, 130, button_width, button_height),
                'text': 'Random AI',
                'color': COLORS['LIGHT_GRAY']
            },
            
            # 控制按钮
            'new_game': {
                'rect': pygame.Rect(start_x, 190, button_width, button_height),
                'text': 'New Game',
                'color': COLORS['GREEN']
            },
            'pause': {
                'rect': pygame.Rect(start_x, 230, button_width, button_height),
                'text': 'Pause',
                'color': COLORS['ORANGE']
            },
            'quit': {
                'rect': pygame.Rect(start_x, 270, button_width, button_height),
                'text': 'Quit',
                'color': COLORS['RED']
            }
        }
        
        return buttons
    
    def _create_ai_agent(self):
        """创建AI智能体"""
        if self.selected_ai == "SnakeAI":
            self.ai_agent = SnakeAI(name="Snake AI", player_id=2)
        elif self.selected_ai == "SmartSnakeAI":
            self.ai_agent = SmartSnakeAI(name="Smart AI", player_id=2)
        elif self.selected_ai == "RandomBot":
            self.ai_agent = RandomBot(name="Random AI", player_id=2)
    
    def reset_game(self):
        """重置游戏"""
        self.env.reset()
        self.game_over = False
        self.winner = None
        self.thinking = False
        self.current_agent = self.human_agent
        self.last_update = time.time()
        self.paused = False
        self.buttons['pause']['text'] = 'Pause'
    
    def handle_events(self) -> bool:
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                # 处理贪吃蛇的键盘输入
                if (isinstance(self.current_agent, HumanAgent) and 
                    not self.game_over and not self.thinking and not self.paused):
                    self._handle_snake_input(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    mouse_pos = pygame.mouse.get_pos()
                    self._handle_button_click(mouse_pos)
        
        return True
    
    def _handle_button_click(self, mouse_pos: Tuple[int, int]):
        """处理按钮点击"""
        for button_name, button_info in self.buttons.items():
            if button_info['rect'].collidepoint(mouse_pos):
                if button_name == 'new_game':
                    self.reset_game()
                elif button_name == 'quit':
                    pygame.quit()
                    sys.exit()
                elif button_name == 'pause':
                    self.paused = not self.paused
                    self.buttons['pause']['text'] = 'Resume' if self.paused else 'Pause'
                elif button_name.endswith('_ai'):
                    # 更新选中的AI
                    for btn_name in ['snake_ai', 'smart_ai', 'random_ai']:
                        self.buttons[btn_name]['color'] = COLORS['LIGHT_GRAY']
                    
                    if button_name == 'snake_ai':
                        self.selected_ai = "SnakeAI"
                    elif button_name == 'smart_ai':
                        self.selected_ai = "SmartSnakeAI"
                    elif button_name == 'random_ai':
                        self.selected_ai = "RandomBot"
                    
                    self.buttons[button_name]['color'] = COLORS['YELLOW']
                    self._create_ai_agent()
                    self.reset_game()
    
    def _handle_snake_input(self, key):
        """处理贪吃蛇键盘输入"""
        key_to_action = {
            pygame.K_UP: (-1, 0),    # 上
            pygame.K_w: (-1, 0),
            pygame.K_DOWN: (1, 0),   # 下
            pygame.K_s: (1, 0),
            pygame.K_LEFT: (0, -1),  # 左
            pygame.K_a: (0, -1),
            pygame.K_RIGHT: (0, 1),  # 右
            pygame.K_d: (0, 1)
        }
        if key in key_to_action:
            action = key_to_action[key]
            # 玩家输入时直接更新方向，不切换current_agent
            self._make_move(action, switch_player=False)

    def _make_move(self, action, switch_player=True):
        """执行移动"""
        if self.game_over or self.paused:
            return
        try:
            observation, reward, terminated, truncated, info = self.env.step(action)
            if terminated or truncated:
                self.game_over = True
                self.winner = self.env.get_winner()
            else:
                if switch_player:
                    self._switch_player()
        except Exception as e:
            print(f"Move execution failed: {e}")

    def _switch_player(self):
        """切换玩家"""
        if isinstance(self.current_agent, HumanAgent):
            self.current_agent = self.ai_agent
            self.thinking = True
        else:
            self.current_agent = self.human_agent
    
    def update_game(self):
        """更新游戏状态"""
        if self.game_over or self.paused:
            return
        
        current_time = time.time()
        
        # 检查是否需要更新
        if current_time - self.last_update < self.update_interval:
            return
        
        self.last_update = current_time
        
        # AI回合
        if (not isinstance(self.current_agent, HumanAgent) and self.thinking):
            try:
                observation = self.env._get_observation()
                action = self.current_agent.get_action(observation, self.env)
                
                if not action:
                    # 如果AI未返回动作，保持原方向
                    if self.env.game.current_player == 2:
                        action = self.env.game.direction2
                    else:
                        action = (0, 1)
                
                self._make_move(action)
                self.thinking = False
                
            except Exception as e:
                print(f"AI thinking failed: {e}")
                self.thinking = False
        
        # 玩家回合：自动推进蛇（如果没有输入则保持原方向）
        elif isinstance(self.current_agent, HumanAgent) and not self.thinking:
            current_direction = self.env.game.direction1
            self._make_move(current_direction, switch_player=False)
    
    def draw(self):
        """绘制游戏界面"""
        # 清空屏幕
        self.screen.fill(COLORS['WHITE'])
        
        # 绘制游戏区域
        self._draw_snake_game()
        
        # 绘制UI
        self._draw_ui()
        
        # 绘制游戏状态
        self._draw_game_status()
        
        # 更新显示
        pygame.display.flip()
    
    def _draw_snake_game(self):
        """绘制贪吃蛇游戏"""
        # 绘制游戏区域背景
        game_rect = pygame.Rect(
            self.margin, 
            self.margin,
            self.board_size * self.cell_size,
            self.board_size * self.cell_size
        )
        pygame.draw.rect(self.screen, COLORS['LIGHT_GRAY'], game_rect)
        pygame.draw.rect(self.screen, COLORS['BLACK'], game_rect, 2)
        
        # 绘制网格
        for i in range(self.board_size + 1):
            # 垂直线
            x = self.margin + i * self.cell_size
            pygame.draw.line(self.screen, COLORS['GRAY'], 
                           (x, self.margin), 
                           (x, self.margin + self.board_size * self.cell_size), 1)
            # 水平线
            y = self.margin + i * self.cell_size
            pygame.draw.line(self.screen, COLORS['GRAY'], 
                           (self.margin, y), 
                           (self.margin + self.board_size * self.cell_size, y), 1)
        
        # 绘制游戏元素
        state = self.env.game.get_state()
        board = state['board']
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                if board[row, col] != 0:
                    x = self.margin + col * self.cell_size + 2
                    y = self.margin + row * self.cell_size + 2
                    rect = pygame.Rect(x, y, self.cell_size - 4, self.cell_size - 4)
                    
                    if board[row, col] == 1:  # 蛇1头部
                        pygame.draw.rect(self.screen, COLORS['BLUE'], rect)
                        # 绘制眼睛
                        eye_size = 3
                        pygame.draw.circle(self.screen, COLORS['WHITE'], 
                                         (x + 6, y + 6), eye_size)
                        pygame.draw.circle(self.screen, COLORS['WHITE'], 
                                         (x + self.cell_size - 10, y + 6), eye_size)
                    elif board[row, col] == 2:  # 蛇1身体
                        pygame.draw.rect(self.screen, COLORS['CYAN'], rect)
                    elif board[row, col] == 3:  # 蛇2头部
                        pygame.draw.rect(self.screen, COLORS['RED'], rect)
                        # 绘制眼睛
                        eye_size = 3
                        pygame.draw.circle(self.screen, COLORS['WHITE'], 
                                         (x + 6, y + 6), eye_size)
                        pygame.draw.circle(self.screen, COLORS['WHITE'], 
                                         (x + self.cell_size - 10, y + 6), eye_size)
                    elif board[row, col] == 4:  # 蛇2身体
                        pygame.draw.rect(self.screen, COLORS['ORANGE'], rect)
                    elif board[row, col] == 5:  # 食物
                        pygame.draw.ellipse(self.screen, COLORS['GREEN'], rect)
    
    def _draw_ui(self):
        """绘制UI界面"""
        # 绘制按钮
        for button_name, button_info in self.buttons.items():
            pygame.draw.rect(self.screen, button_info['color'], button_info['rect'])
            pygame.draw.rect(self.screen, COLORS['BLACK'], button_info['rect'], 2)
            
            text_surface = self.font_medium.render(button_info['text'], True, COLORS['BLACK'])
            text_rect = text_surface.get_rect(center=button_info['rect'].center)
            self.screen.blit(text_surface, text_rect)
        
        # 绘制标题
        start_x = self.board_size * self.cell_size + self.margin + 20
        
        ai_title_text = self.font_medium.render("AI Selection:", True, COLORS['BLACK'])
        self.screen.blit(ai_title_text, (start_x, 25))
        
        # 绘制操作说明
        instructions = [
            "Controls:",
            "• Arrow keys/WASD to move",
            "• Eat green food to grow",
            "• Avoid walls and snakes",
            "• Blue snake is you",
            "• Red snake is AI"
        ]
        
        start_y = 320
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, COLORS['DARK_GRAY'])
            self.screen.blit(text, (start_x, start_y + i * 20))
    
    def _draw_game_status(self):
        """绘制游戏状态"""
        start_x = self.board_size * self.cell_size + self.margin + 20
        status_y = 450
        
        if self.paused:
            status_text = "Game Paused"
            color = COLORS['ORANGE']
        elif self.game_over:
            if self.winner == 1:
                status_text = "You Win!"
                color = COLORS['GREEN']
            elif self.winner == 2:
                status_text = "AI Wins!"
                color = COLORS['RED']
            else:
                status_text = "Draw!"
                color = COLORS['ORANGE']
        else:
            if isinstance(self.current_agent, HumanAgent):
                status_text = "Your Turn"
                color = COLORS['BLUE']
            else:
                if self.thinking:
                    status_text = "AI Thinking..."
                    color = COLORS['ORANGE']
                else:
                    status_text = "AI Turn"
                    color = COLORS['RED']
        
        text_surface = self.font_large.render(status_text, True, color)
        self.screen.blit(text_surface, (start_x, status_y))
        
        # 游戏信息
        info_y = status_y + 40
        state = self.env.game.get_state()
        len1 = len(state['snake1']) if state['alive1'] else 0
        len2 = len(state['snake2']) if state['alive2'] else 0
        alive1 = "Alive" if state['alive1'] else "Dead"
        alive2 = "Alive" if state['alive2'] else "Dead"
        
        player_info = f"You: {len1} ({alive1})"
        ai_info = f"AI: {len2} ({alive2})"
        
        info_surface = self.font_small.render(player_info, True, COLORS['BLUE'])
        self.screen.blit(info_surface, (start_x, info_y))
        
        info_surface2 = self.font_small.render(ai_info, True, COLORS['RED'])
        self.screen.blit(info_surface2, (start_x, info_y + 20))
    
    def run(self):
        """运行游戏主循环"""
        running = True
        
        while running:
            # 处理事件
            running = self.handle_events()
            
            # 更新游戏
            self.update_game()
            
            # 绘制界面
            self.draw()
            
            # 控制帧率
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    print("Starting Snake AI Battle...")
    print("Controls:")
    print("- Arrow keys or WASD to control your snake")
    print("- Eat green food to grow")
    print("- Avoid walls and snake bodies")
    print("- Blue snake is you, red snake is AI")
    print("- Choose different AI opponents")
    
    try:
        game = SnakeGUI()
        game.run()
    except Exception as e:
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()