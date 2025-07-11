#!/usr/bin/env python3
"""
吃豆人游戏 Pygame GUI界面
"""

import pygame
import sys
import time
from typing import Dict, Tuple, Any
from games.pacman.pacman_game import PacmanGame
from games.pacman.pacman_env import PacmanEnv

class PacmanGUI:
    """吃豆人游戏 GUI 界面"""
    
    def __init__(self, board_size: int = 21, dots_count: int = 80):
        # 初始化pygame
        pygame.init()
        
        # 游戏参数
        self.board_size = board_size
        self.dots_count = dots_count
        
        # 界面参数
        self.cell_size = 25
        self.board_width = self.board_size * self.cell_size
        self.board_height = self.board_size * self.cell_size
        self.info_panel_width = 250
        self.window_width = self.board_width + self.info_panel_width
        self.window_height = self.board_height + 50
        
        # 创建窗口
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("吃豆人大战幽灵")
        
        # 字体初始化
        self.font = self._init_font(24)
        self.title_font = self._init_font(32)
        
        # 颜色定义
        self.colors = {
            'background': (0, 0, 0),        # 黑色背景
            'wall': (0, 0, 255),            # 蓝色墙壁
            'dot': (255, 255, 0),           # 黄色豆子
            'empty': (0, 0, 0),             # 黑色空地
            'player1': (255, 255, 0),       # 经典黄色吃豆人
            'player2': (255, 50, 50),       # 红色幽灵
            'ghost_eyes': (255, 255, 255),  # 幽灵眼睛
            'text': (255, 255, 255),        # 白色文字
            'info_bg': (50, 50, 50),        # 深灰色信息面板
            'border': (100, 100, 100)       # 边框
        }
        
        # 游戏状态
        self.env = PacmanEnv(board_size, dots_count)
        self.game_running = True
        self.clock = pygame.time.Clock()
        
        # 玩家控制
        self.player1_keys = {
            pygame.K_w: 'up',
            pygame.K_s: 'down',
            pygame.K_a: 'left',
            pygame.K_d: 'right'
        }
        
        self.player2_keys = {
            pygame.K_UP: 'up',
            pygame.K_DOWN: 'down',
            pygame.K_LEFT: 'left',
            pygame.K_RIGHT: 'right'
        }
        
        # 游戏状态变量
        self.last_actions = {1: 'stay', 2: 'stay'}
        self.step_count = 0
        
        # 连续移动控制
        self.move_interval = 0.15  # 移动间隔（秒）
        self.last_move_time = 0
        
        # 玩家朝向（用于绘制吃豆人张嘴方向）
        self.player1_direction = 'right'
        self.player2_direction = 'right'
    
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
        
    def run(self):
        """运行游戏主循环"""
        print("🎮 启动吃豆人大战幽灵 GUI")
        
        # 重置游戏
        observation, info = self.env.reset()
        
        # 游戏主循环
        while self.game_running:
            # 处理事件
            actions = self.handle_events()
            
            if not self.game_running:
                break
            
            # 仅在有动作时执行一步
            if actions:
                # 获取移动前的位置
                state_before = self.env.get_state()
                pos1_before = state_before.get('player1_pos')
                pos2_before = state_before.get('player2_pos')
                
                observation, reward, done, truncated, info = self.env.step(actions)
                
                # 获取移动后的位置
                state_after = self.env.get_state()
                pos1_after = state_after.get('player1_pos')
                pos2_after = state_after.get('player2_pos')
                
                # 只有当至少有一个玩家实际移动时才增加步数
                if pos1_before != pos1_after or pos2_before != pos2_after:
                    self.step_count += 1
                
                # 检查游戏结束
                if done or truncated:
                    self.show_game_over(info)
            
            # 渲染画面
            self.render(info)
            
            # 控制帧率
            self.clock.tick(10)  # 10 FPS
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self) -> Dict[int, str]:
        """处理事件和键盘状态，支持连续移动"""
        import time
        current_time = time.time()
        
        # 1. 优先处理窗口关闭和ESC等事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_running = False
                return {}
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game_running = False
                return {}
        
        # 2. 检查是否可以移动（时间间隔控制）
        if current_time - self.last_move_time < self.move_interval:
            return {}
        
        # 3. 检查当前按键状态，支持连续移动
        keys = pygame.key.get_pressed()
        actions = {}
        
        # 玩家1 WASD控制
        if keys[pygame.K_w]:
            actions[1] = 'up'
            self.player1_direction = 'up'
        elif keys[pygame.K_s]:
            actions[1] = 'down'
            self.player1_direction = 'down'
        elif keys[pygame.K_a]:
            actions[1] = 'left'
            self.player1_direction = 'left'
        elif keys[pygame.K_d]:
            actions[1] = 'right'
            self.player1_direction = 'right'
        
        # 玩家2 方向键控制
        if keys[pygame.K_UP]:
            actions[2] = 'up'
            self.player2_direction = 'up'
        elif keys[pygame.K_DOWN]:
            actions[2] = 'down'
            self.player2_direction = 'down'
        elif keys[pygame.K_LEFT]:
            actions[2] = 'left'
            self.player2_direction = 'left'
        elif keys[pygame.K_RIGHT]:
            actions[2] = 'right'
            self.player2_direction = 'right'
        
        # 4. 如果有动作，更新时间并返回
        if actions:
            self.last_move_time = current_time
            
            # 补全未操作玩家为stay
            if 1 not in actions:
                actions[1] = 'stay'
            if 2 not in actions:
                actions[2] = 'stay'
                
            self.last_actions = actions
            return actions
        
        return {}
    
    def render(self, info: Dict[str, Any]):
        """渲染游戏画面"""
        # 清空屏幕
        self.screen.fill(self.colors['background'])
        
        # 绘制游戏板
        self.draw_board()
        
        # 绘制信息面板
        self.draw_info_panel(info)
        
        # 绘制控制说明
        self.draw_controls()
        
        # 更新显示
        pygame.display.flip()
    
    def draw_board(self):
        """绘制游戏板"""
        state = self.env.get_state()
        board = state['board']
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                x = col * self.cell_size
                y = row * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                
                cell_value = board[row, col]
                
                # 根据单元格类型绘制
                if cell_value == PacmanGame.WALL:
                    pygame.draw.rect(self.screen, self.colors['wall'], rect)
                elif cell_value == PacmanGame.DOT:
                    pygame.draw.rect(self.screen, self.colors['empty'], rect)
                    # 绘制豆子
                    dot_center = (x + self.cell_size // 2, y + self.cell_size // 2)
                    pygame.draw.circle(self.screen, self.colors['dot'], dot_center, 3)
                elif cell_value == PacmanGame.PLAYER1:
                    pygame.draw.rect(self.screen, self.colors['empty'], rect)
                    # 绘制玩家1（黄色吃豆人）
                    self._draw_pacman(x + self.cell_size // 2, y + self.cell_size // 2, 
                                    self.colors['player1'], self.player1_direction)
                elif cell_value == PacmanGame.PLAYER2:
                    pygame.draw.rect(self.screen, self.colors['empty'], rect)
                    # 绘制玩家2（红色幽灵）
                    self._draw_ghost(x + self.cell_size // 2, y + self.cell_size // 2, 
                                   self.colors['player2'])
                else:  # EMPTY
                    pygame.draw.rect(self.screen, self.colors['empty'], rect)
                
                # 绘制网格线
                pygame.draw.rect(self.screen, self.colors['border'], rect, 1)
    
    def _draw_pacman(self, center_x: int, center_y: int, color: tuple, direction: str):
        """绘制经典吃豆人图案"""
        import math
        
        radius = 10
        
        # 定义嘴巴张开的角度（以弧度为单位）
        mouth_angle = math.pi / 2.5  # 约72度的嘴巴开口，更明显
        
        # 根据方向计算嘴巴缺口的位置
        # 使用极坐标系，0度为右方，逆时针增加
        if direction == 'right':
            # 向右张嘴：缺口在右侧（0度方向）
            gap_start = -mouth_angle / 2  # 从右下开始
            gap_end = mouth_angle / 2     # 到右上结束
        elif direction == 'left':
            # 向左张嘴：缺口在左侧（180度方向）
            gap_start = math.pi - mouth_angle / 2  # 从左上开始
            gap_end = math.pi + mouth_angle / 2    # 到左下结束
        elif direction == 'up':
            # 向上张嘴：缺口在上方（270度方向）
            gap_start = 3 * math.pi / 2 - mouth_angle / 2  # 从上右开始
            gap_end = 3 * math.pi / 2 + mouth_angle / 2    # 到上左结束
        else:  # down
            # 向下张嘴：缺口在下方（90度方向）
            gap_start = math.pi / 2 - mouth_angle / 2  # 从下左开始
            gap_end = math.pi / 2 + mouth_angle / 2    # 到下右结束
        
        # 绘制吃豆人主体（带缺口的圆）
        points = []
        
        # 从圆心开始
        center = (center_x, center_y)
        points.append(center)
        
        # 生成圆弧上的点，跳过嘴巴缺口部分
        num_points = 32  # 增加点数使圆弧更平滑
        
        # 计算完整圆弧的角度范围（排除缺口）
        full_angle = 2 * math.pi - mouth_angle
        
        # 从缺口结束位置开始，绘制到缺口开始位置
        for i in range(num_points + 1):
            # 从gap_end开始，绘制完整的圆弧到gap_start
            angle = gap_end + (full_angle * i / num_points)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))
        
        # 绘制吃豆人
        pygame.draw.polygon(self.screen, color, points)
    
    def _draw_ghost(self, center_x: int, center_y: int, color: tuple):
        """绘制经典幽灵图案"""
        import math
        
        radius = 10
        
        # 绘制幽灵主体（圆形头部 + 矩形身体）
        # 1. 绘制圆形头部
        head_center = (center_x, center_y - 3)
        pygame.draw.circle(self.screen, color, head_center, radius - 2)
        
        # 2. 绘制矩形身体
        body_rect = pygame.Rect(center_x - radius + 2, center_y - 3, 
                               (radius - 2) * 2, radius + 3)
        pygame.draw.rect(self.screen, color, body_rect)
        
        # 3. 绘制波浪形底部
        wave_y = center_y + 7
        wave_points = []
        for i in range(5):
            x = center_x - radius + 2 + i * 4
            if i % 2 == 0:
                y = wave_y
            else:
                y = wave_y - 3
            wave_points.append((x, y))
        
        # 添加底部直线点
        wave_points.append((center_x + radius - 2, wave_y))
        wave_points.append((center_x + radius - 2, center_y + 3))
        wave_points.append((center_x - radius + 2, center_y + 3))
        
        pygame.draw.polygon(self.screen, color, wave_points)
        
        # 4. 绘制白色眼睛
        left_eye = (center_x - 4, center_y - 4)
        right_eye = (center_x + 4, center_y - 4)
        pygame.draw.circle(self.screen, self.colors['ghost_eyes'], left_eye, 2)
        pygame.draw.circle(self.screen, self.colors['ghost_eyes'], right_eye, 2)
        
        # 5. 绘制黑色瞳孔
        pygame.draw.circle(self.screen, (0, 0, 0), left_eye, 1)
        pygame.draw.circle(self.screen, (0, 0, 0), right_eye, 1)
    
    def draw_info_panel(self, info: Dict[str, Any]):
        """绘制信息面板"""
        panel_x = self.board_width + 10
        panel_y = 10
        
        # 绘制背景
        panel_rect = pygame.Rect(panel_x, panel_y, self.info_panel_width - 20, self.board_height - 20)
        pygame.draw.rect(self.screen, self.colors['info_bg'], panel_rect)
        pygame.draw.rect(self.screen, self.colors['border'], panel_rect, 2)
        
        # 绘制标题
        title_text = self.title_font.render("游戏信息", True, self.colors['text'])
        self.screen.blit(title_text, (panel_x + 10, panel_y + 10))
        
        # 绘制游戏信息
        y_offset = 50
        info_texts = [
            f"步数: {self.step_count}",
            f"吃豆人分数: {info.get('player1_score', 0)}",
            f"剩余豆子: {info.get('dots_remaining', 0)}",
            "",
            "当前动作:",
            f"吃豆人: {self.last_actions.get(1, 'stay')}",
            f"幽灵: {self.last_actions.get(2, 'stay')}"
        ]
        
        for text in info_texts:
            if text:  # 跳过空行
                text_surface = self.font.render(text, True, self.colors['text'])
                self.screen.blit(text_surface, (panel_x + 10, panel_y + y_offset))
            y_offset += 25
    
    def draw_controls(self):
        """绘制控制说明"""
        panel_x = self.board_width + 10
        panel_y = self.board_height - 200
        
        # 绘制背景
        control_rect = pygame.Rect(panel_x, panel_y, self.info_panel_width - 20, 180)
        pygame.draw.rect(self.screen, self.colors['info_bg'], control_rect)
        pygame.draw.rect(self.screen, self.colors['border'], control_rect, 2)
        
        # 绘制标题
        title_text = self.title_font.render("控制说明", True, self.colors['text'])
        self.screen.blit(title_text, (panel_x + 10, panel_y + 10))
        
        # 绘制控制说明
        y_offset = 40
        control_texts = [
            "吃豆人 (黄色):",
            "W - 向上",
            "S - 向下", 
            "A - 向左",
            "D - 向右",
            "",
            "幽灵 (红色):",
            "↑ - 向上",
            "↓ - 向下",
            "← - 向左",
            "→ - 向右"
        ]
        
        for text in control_texts:
            if text:  # 跳过空行
                text_surface = self.font.render(text, True, self.colors['text'])
                self.screen.blit(text_surface, (panel_x + 10, panel_y + y_offset))
            y_offset += 20
    
    def show_game_over(self, info: Dict[str, Any]):
        """显示游戏结束画面"""
        # 创建半透明覆盖层
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 游戏结束文本
        game_over_text = self.title_font.render("游戏结束！", True, self.colors['text'])
        text_rect = game_over_text.get_rect(center=(self.window_width // 2, self.window_height // 2 - 100))
        self.screen.blit(game_over_text, text_rect)
        
        # 结果文本
        winner = info.get('winner')
        if winner == 1:
            result_text = "吃豆人获胜！"
            color = self.colors['player1']
        elif winner == 2:
            result_text = "幽灵获胜！"
            color = self.colors['player2']
        else:
            result_text = "平局！"
            color = self.colors['text']
        
        result_surface = self.title_font.render(result_text, True, color)
        result_rect = result_surface.get_rect(center=(self.window_width // 2, self.window_height // 2 - 50))
        self.screen.blit(result_surface, result_rect)
        
        # 分数信息
        score_text = f"最终分数 - 吃豆人: {info.get('player1_score', 0)}, 剩余豆子: {info.get('dots_remaining', 0)}"
        score_surface = self.font.render(score_text, True, self.colors['text'])
        score_rect = score_surface.get_rect(center=(self.window_width // 2, self.window_height // 2))
        self.screen.blit(score_surface, score_rect)
        
        # 提示文本
        hint_text = "按ESC退出或关闭窗口"
        hint_surface = self.font.render(hint_text, True, self.colors['text'])
        hint_rect = hint_surface.get_rect(center=(self.window_width // 2, self.window_height // 2 + 50))
        self.screen.blit(hint_surface, hint_rect)
        
        pygame.display.flip()
        
        # 等待用户操作
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    waiting = False
                    self.game_running = False

def main():
    """主函数"""
    try:
        # 创建并运行游戏
        game = PacmanGUI(board_size=21, dots_count=80)
        game.run()
    except Exception as e:
        print(f"❌ 游戏运行错误: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main() 