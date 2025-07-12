#!/usr/bin/env python3
"""
国际象棋 GUI 界面
支持玩家vs玩家对战，可点击移动棋子
"""

import pygame
import sys
import time
from typing import Dict, Tuple, Any, Optional, List
from games.chess.chess_game import ChessGame
from games.chess.chess_env import ChessEnv

class ChessGUI:
    """国际象棋游戏 GUI 界面"""
    
    def __init__(self):
        # 初始化pygame
        pygame.init()
        
        # 界面参数
        self.board_size = 8
        self.cell_size = 70
        self.board_width = self.board_size * self.cell_size
        self.board_height = self.board_size * self.cell_size
        self.info_panel_width = 350
        self.margin = 30
        self.window_width = self.board_width + self.info_panel_width + self.margin * 2
        self.window_height = self.board_height + self.margin * 2
        
        # 创建窗口
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("国际象棋 - 玩家vs玩家")
        
        # 字体初始化 - 分别为棋子和文字优化
        self.text_font = self._init_chinese_font(16)    # 中文文字专用
        self.title_font = self._init_chinese_font(20)   # 中文标题专用
        self.small_font = self._init_chinese_font(14)   # 小号中文文字
        self.large_font = self._init_unicode_font(40)   # Unicode棋子专用
        self.font = self.text_font  # 兼容性
        
        # 颜色定义
        self.colors = {
            'light_square': (240, 217, 181),    # 浅色方格
            'dark_square': (181, 136, 99),      # 深色方格
            'selected': (255, 255, 0),          # 选中高亮
            'possible_move': (144, 238, 144),   # 可能的移动
            'last_move': (255, 255, 102),       # 上一步移动
            'check': (255, 0, 0),               # 将军警告
            'white_piece': (255, 255, 255),     # 白子
            'black_piece': (0, 0, 0),           # 黑子
            'background': (248, 248, 248),      # 背景
            'info_bg': (245, 245, 245),         # 信息面板背景
            'border': (100, 100, 100),          # 边框
            'text': (50, 50, 50),               # 文字
            'button': (200, 200, 200),          # 按钮
            'button_hover': (180, 180, 180),    # 按钮悬停
            'button_text': (0, 0, 0),           # 按钮文字
        }
        
        # 棋子Unicode符号和备用字符
        self.piece_symbols = {
            'white': {
                'king': '♔', 'queen': '♕', 'rook': '♖', 
                'bishop': '♗', 'knight': '♘', 'pawn': '♙'
            },
            'black': {
                'king': '♚', 'queen': '♛', 'rook': '♜', 
                'bishop': '♝', 'knight': '♞', 'pawn': '♟'
            }
        }
        
        # 备用ASCII字符（如果Unicode不支持）
        self.piece_symbols_ascii = {
            'white': {
                'king': 'K', 'queen': 'Q', 'rook': 'R', 
                'bishop': 'B', 'knight': 'N', 'pawn': 'P'
            },
            'black': {
                'king': 'k', 'queen': 'q', 'rook': 'r', 
                'bishop': 'b', 'knight': 'n', 'pawn': 'p'
            }
        }
        
        # 游戏状态
        self.env = ChessEnv()
        self.game_running = True
        self.clock = pygame.time.Clock()
        
        # 界面状态
        self.selected_square = None
        self.possible_moves = []
        self.last_move_from = None
        self.last_move_to = None
        
        # 按钮
        self.buttons = self._create_buttons()
        
        # 重置游戏
        self.reset_game()
        
        # 测试字体渲染
        self._test_font_rendering()
        
    def _test_font_rendering(self):
        """测试字体渲染效果"""
        print("\n🔍 测试字体渲染:")
        
        # 测试Unicode棋子符号
        print("  棋子符号:")
        test_symbols = ['♔', '♚', '♙', '♟', '♕', '♛']
        for symbol in test_symbols:
            try:
                surface = self.large_font.render(symbol, True, (255, 255, 255))
                width = surface.get_width()
                height = surface.get_height()
                print(f"    {symbol}: 宽度={width}, 高度={height}, {'✅通过' if width > 15 else '❌失败'}")
            except Exception as e:
                print(f"    {symbol}: 渲染失败 - {e}")
        
        # 测试中文文字
        print("  中文文字:")
        test_texts = ["国际象棋", "当前玩家", "游戏进行中"]
        for text in test_texts:
            try:
                surface = self.text_font.render(text, True, (255, 255, 255))
                width = surface.get_width()
                expected_width = len(text) * 12  # 估算宽度
                print(f"    {text}: 宽度={width}, {'✅通过' if width > expected_width else '❌失败'}")
            except Exception as e:
                print(f"    {text}: 渲染失败 - {e}")
        print()
    
    def _init_chinese_font(self, size: int):
        """初始化专用于中文文字显示的字体"""
        chinese_fonts = [
            'microsoftyahei',    # 微软雅黑 - 首选中文字体
            'yahei',             # 雅黑
            'simhei',            # 黑体
            'simsun',            # 宋体
            'dengxian',          # 等线
            'kaiti',             # 楷体
            'fangsong',          # 仿宋
            'arial unicode ms',   # Arial Unicode MS
            'tahoma',            # Tahoma
            'arial',             # Arial
        ]
        
        # 测试中文字符
        test_text = "当前玩家白方黑方游戏进行中"
        
        for font_name in chinese_fonts:
            try:
                font = pygame.font.SysFont(font_name, size)
                # 测试中文渲染
                test_surface = font.render(test_text, True, (255, 255, 255))
                if test_surface.get_width() > size * len(test_text) * 0.3:  # 合理的宽度
                    print(f"✅ 中文字体: {font_name}")
                    return font
            except:
                continue
        
        # 备用方案
        try:
            print("⚠️  使用默认中文字体")
            return pygame.font.SysFont('arial', size)
        except:
            return pygame.font.Font(None, size)
    
    def _init_unicode_font(self, size: int):
        """初始化专用于Unicode棋子符号的字体"""
        return self._init_font(size)
    
    def _init_font(self, size: int):
        """初始化支持Unicode和中文的字体"""
        # 专门支持Unicode符号的字体
        unicode_fonts = [
            'segoeuisymbol',     # Windows Segoe UI Symbol
            'segoeuiemoji',      # Windows Segoe UI Emoji 
            'dejavusans',        # DejaVu Sans
            'liberation sans',    # Liberation Sans
            'arial unicode ms',   # Arial Unicode MS
            'lucida sans unicode', # Lucida Sans Unicode
            'simhei',            # 中文黑体
            'simsun',            # 中文宋体
            'yahei',             # 中文雅黑
            'microsoftyahei',    # 微软雅黑
            'arial',             # Arial
            'times new roman',   # Times New Roman
            'courier new',       # Courier New
        ]
        
        # 测试Unicode棋子符号
        test_symbols = ['♔', '♚', '♙', '♟']
        
        for font_name in unicode_fonts:
            try:
                font = pygame.font.SysFont(font_name, size)
                # 测试Unicode符号渲染
                for symbol in test_symbols:
                    test_surface = font.render(symbol, True, (255, 255, 255))
                    if test_surface.get_width() > 8:  # 确保符号有合理的宽度
                        print(f"✅ 找到支持Unicode的字体: {font_name}")
                        return font
            except:
                continue
        
        # 如果都失败，使用默认字体
        try:
            print("⚠️  使用默认字体")
            return pygame.font.Font(None, size)
        except:
            return pygame.font.SysFont('arial', size)
    
    def _create_buttons(self) -> Dict[str, Dict[str, Any]]:
        """创建界面按钮"""
        btn_width = 120
        btn_height = 35
        start_x = self.board_width + self.margin * 2 + 20
        
        buttons = {
            'new_game': {
                'rect': pygame.Rect(start_x, 50, btn_width, btn_height),
                'text': '新游戏',
                'color': self.colors['button']
            },
            'hint': {
                'rect': pygame.Rect(start_x + 140, 50, btn_width, btn_height),
                'text': '提示',
                'color': self.colors['button']
            },
            'quit': {
                'rect': pygame.Rect(start_x + 70, 100, btn_width, btn_height),
                'text': '退出',
                'color': (255, 200, 200)
            }
        }
        
        return buttons
    
    def reset_game(self):
        """重置游戏"""
        self.env.reset()
        self.selected_square = None
        self.possible_moves = []
        self.last_move_from = None
        self.last_move_to = None
        print("游戏重置完成")
    
    def run(self):
        """运行游戏主循环"""
        print("🎮 启动国际象棋 GUI")
        
        while self.game_running:
            # 处理事件
            self.handle_events()
            
            if not self.game_running:
                break
            
            # 渲染画面
            self.render()
            
            # 控制帧率
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_running = False
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_running = False
                    return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    self.handle_mouse_click(event.pos)
    
    def handle_mouse_click(self, pos: Tuple[int, int]):
        """处理鼠标点击"""
        x, y = pos
        
        # 检查是否点击了按钮
        for button_name, button_info in self.buttons.items():
            if button_info['rect'].collidepoint(pos):
                self.handle_button_click(button_name)
                return
        
        # 检查是否点击了棋盘
        if (self.margin <= x <= self.margin + self.board_width and
            self.margin <= y <= self.margin + self.board_height):
            
            # 计算点击的格子
            col = (x - self.margin) // self.cell_size
            row = (y - self.margin) // self.cell_size
            
            if 0 <= row < 8 and 0 <= col < 8:
                self.handle_square_click(row, col)
    
    def handle_button_click(self, button_name: str):
        """处理按钮点击"""
        if button_name == 'new_game':
            self.reset_game()
        elif button_name == 'hint':
            self.show_hint()
        elif button_name == 'quit':
            self.game_running = False
    
    def handle_square_click(self, row: int, col: int):
        """处理棋盘格子点击"""
        if self.env.game.is_terminal():
            return
        
        # 获取当前棋盘状态
        board = self.env.game.board
        
        # 如果没有选中的格子
        if self.selected_square is None:
            # 检查点击的格子是否有本方棋子
            piece = board[row][col]
            if piece is not None:
                current_player = self.env.game.current_player
                # 修复：正确处理颜色比较
                piece_color = piece.color.value  # 获取颜色的数值
                expected_color = current_player   # 当前玩家（1=白方，2=黑方）
                
                if piece_color == expected_color:
                    self.selected_square = (row, col)
                    self.possible_moves = self.get_possible_moves(row, col)
                    color_name = '白方' if piece_color == 1 else '黑方'
                    print(f"选中了 {color_name} {piece.piece_type.name} 在 ({row}, {col})")
        else:
            # 已经选中了一个格子
            selected_row, selected_col = self.selected_square
            
            # 如果点击了同一个格子，取消选择
            if (row, col) == self.selected_square:
                self.selected_square = None
                self.possible_moves = []
                print("取消选择")
            # 如果点击了可能的移动位置
            elif (row, col) in self.possible_moves:
                self.make_move(selected_row, selected_col, row, col)
            # 如果点击了其他己方棋子
            elif (board[row][col] is not None and 
                  board[row][col].color.value == board[selected_row][selected_col].color.value):
                self.selected_square = (row, col)
                self.possible_moves = self.get_possible_moves(row, col)
                print(f"重新选择棋子在 ({row}, {col})")
            else:
                # 点击了无效位置
                self.selected_square = None
                self.possible_moves = []
                print("无效移动，取消选择")
    
    def get_possible_moves(self, row: int, col: int) -> List[Tuple[int, int]]:
        """获取指定位置棋子的可能移动"""
        possible_moves = []
        
        # 获取该位置棋子的所有合法移动
        for from_pos, to_pos in self.env.game.get_valid_actions():
            if from_pos[0] == row and from_pos[1] == col:
                possible_moves.append(to_pos)
        
        return possible_moves
    
    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int):
        """执行移动"""
        try:
            # 构建移动对象 - 使用位置元组格式
            move = ((from_row, from_col), (to_row, to_col))
            
            # 执行移动
            observation, reward, done, truncated, info = self.env.step(move)
            
            if 'error' not in info:
                self.last_move_from = (from_row, from_col)
                self.last_move_to = (to_row, to_col)
                self.selected_square = None
                self.possible_moves = []
                
                # 检查游戏状态
                if self.env.game.is_terminal():
                    winner = self.env.game.get_winner()
                    if winner:
                        winner_name = '白方' if winner == 1 else '黑方'
                        print(f"将死！{winner_name} 获胜!")
                    else:
                        print("僵局！")
                elif hasattr(self.env.game, 'is_check') and self.env.game.is_check():
                    current_player_name = '白方' if self.env.game.current_player == 1 else '黑方'
                    print(f"{current_player_name} 被将军!")
                
                print(f"移动成功: {chr(ord('a') + from_col)}{8 - from_row} -> {chr(ord('a') + to_col)}{8 - to_row}")
            else:
                print("移动失败")
                self.selected_square = None
                self.possible_moves = []
        except Exception as e:
            print(f"移动出错: {e}")
            self.selected_square = None
            self.possible_moves = []
    
    def undo_move(self):
        """撤销移动"""
        if self.env.game.move_history:
            # 暂时不支持撤销功能
            print("暂时不支持撤销功能")
        else:
            print("没有可以撤销的移动")
    
    def show_hint(self):
        """显示提示"""
        legal_moves = self.env.game.get_valid_actions()
        if legal_moves:
            import random
            from_pos, to_pos = random.choice(legal_moves)
            print(f"提示: {chr(ord('a') + from_pos[1])}{8 - from_pos[0]} -> {chr(ord('a') + to_pos[1])}{8 - to_pos[0]}")
        else:
            print("没有可用的移动")
    
    def render(self):
        """渲染整个界面"""
        # 填充背景
        self.screen.fill(self.colors['background'])
        
        # 绘制棋盘
        self.draw_board()
        
        # 绘制信息面板
        self.draw_info_panel()
        
        # 绘制按钮
        self.draw_buttons()
        
        # 更新显示
        pygame.display.flip()
    
    def draw_board(self):
        """绘制棋盘"""
        # 绘制边框
        border_rect = pygame.Rect(self.margin - 2, self.margin - 2, 
                                 self.board_width + 4, self.board_height + 4)
        pygame.draw.rect(self.screen, self.colors['border'], border_rect, 2)
        
        # 绘制格子
        for row in range(8):
            for col in range(8):
                x = self.margin + col * self.cell_size
                y = self.margin + row * self.cell_size
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                
                # 确定格子颜色
                if (row + col) % 2 == 0:
                    color = self.colors['light_square']
                else:
                    color = self.colors['dark_square']
                
                # 特殊高亮
                if self.selected_square == (row, col):
                    color = self.colors['selected']
                elif (row, col) in self.possible_moves:
                    color = self.colors['possible_move']
                elif (self.last_move_from == (row, col) or 
                      self.last_move_to == (row, col)):
                    color = self.colors['last_move']
                
                pygame.draw.rect(self.screen, color, rect)
                
                # 绘制棋子
                piece = self.env.game.board[row][col]
                if piece is not None:
                    self.draw_piece(piece, x + self.cell_size // 2, y + self.cell_size // 2)
        
        # 绘制坐标标签
        self.draw_coordinates()
    
    def draw_piece(self, piece, center_x: int, center_y: int):
        """绘制棋子 - 多重备用方案"""
        piece_color = piece.color.value  # 1=白方, 2=黑方
        piece_type = piece.piece_type.name.lower()
        
        # 方案1: 尝试Unicode符号
        if self._try_draw_unicode_piece(piece, center_x, center_y):
            return
            
        # 方案2: 尝试改进的图形绘制
        self._draw_graphic_piece(piece, center_x, center_y)
    
    def _try_draw_unicode_piece(self, piece, center_x: int, center_y: int) -> bool:
        """尝试绘制Unicode棋子，成功返回True"""
        piece_color = piece.color.value
        piece_type = piece.piece_type.name.lower()
        
        try:
            # 获取棋子符号
            if piece_color == 1:  # 白方
                symbol = self.piece_symbols['white'][piece_type]
                text_color = (255, 255, 255)
                shadow_color = (80, 80, 80)
            else:  # 黑方
                symbol = self.piece_symbols['black'][piece_type] 
                text_color = (0, 0, 0)
                shadow_color = (200, 200, 200)
            
            # 测试渲染
            text_surface = self.large_font.render(symbol, True, text_color)
            
            # 检查渲染质量
            if text_surface.get_width() > 15:  # 提高检测标准
                # 绘制阴影
                shadow_surface = self.large_font.render(symbol, True, shadow_color)
                shadow_rect = shadow_surface.get_rect(center=(center_x + 2, center_y + 2))
                self.screen.blit(shadow_surface, shadow_rect)
                
                # 绘制主体
                text_rect = text_surface.get_rect(center=(center_x, center_y))
                self.screen.blit(text_surface, text_rect)
                return True
                
        except Exception as e:
            print(f"Unicode渲染失败: {e}")
            
        return False
    
    def _draw_graphic_piece(self, piece, center_x: int, center_y: int):
        """使用图形绘制棋子（备用方案）"""
        piece_color = piece.color.value
        piece_type = piece.piece_type.name
        
        # 棋子基础设置
        size = 22
        
        if piece_color == 1:  # 白方
            fill_color = (255, 255, 255)
            border_color = (0, 0, 0)
            text_color = (0, 0, 0)
        else:  # 黑方
            fill_color = (40, 40, 40)
            border_color = (255, 255, 255)
            text_color = (255, 255, 255)
        
        # 根据棋子类型绘制
        if piece_type == 'PAWN':
            # 兵：圆形
            pygame.draw.circle(self.screen, fill_color, (center_x, center_y), size//2)
            pygame.draw.circle(self.screen, border_color, (center_x, center_y), size//2, 3)
            
        elif piece_type == 'ROOK':
            # 车：正方形
            rect = pygame.Rect(center_x - size//2, center_y - size//2, size, size)
            pygame.draw.rect(self.screen, fill_color, rect)
            pygame.draw.rect(self.screen, border_color, rect, 3)
            
        elif piece_type == 'KNIGHT':
            # 马：特殊L形状
            points = [
                (center_x - size//3, center_y - size//2),
                (center_x + size//3, center_y - size//2),
                (center_x + size//2, center_y - size//4),
                (center_x + size//2, center_y + size//2),
                (center_x - size//2, center_y + size//2),
                (center_x - size//2, center_y)
            ]
            pygame.draw.polygon(self.screen, fill_color, points)
            pygame.draw.polygon(self.screen, border_color, points, 3)
            
        elif piece_type == 'BISHOP':
            # 象：菱形
            points = [
                (center_x, center_y - size//2),
                (center_x + size//2, center_y),
                (center_x, center_y + size//2),
                (center_x - size//2, center_y)
            ]
            pygame.draw.polygon(self.screen, fill_color, points)
            pygame.draw.polygon(self.screen, border_color, points, 3)
            
        elif piece_type == 'QUEEN':
            # 后：圆形+皇冠
            pygame.draw.circle(self.screen, fill_color, (center_x, center_y), size//2)
            pygame.draw.circle(self.screen, border_color, (center_x, center_y), size//2, 3)
            # 皇冠装饰
            crown_points = [
                (center_x - size//3, center_y - size//3),
                (center_x - size//6, center_y - size//2),
                (center_x, center_y - size//3),
                (center_x + size//6, center_y - size//2),
                (center_x + size//3, center_y - size//3)
            ]
            pygame.draw.lines(self.screen, border_color, False, crown_points, 3)
            
        elif piece_type == 'KING':
            # 王：圆形+十字
            pygame.draw.circle(self.screen, fill_color, (center_x, center_y), size//2)
            pygame.draw.circle(self.screen, border_color, (center_x, center_y), size//2, 3)
            # 十字装饰
            cross_size = size//3
            pygame.draw.line(self.screen, border_color,
                           (center_x - cross_size, center_y),
                           (center_x + cross_size, center_y), 4)
            pygame.draw.line(self.screen, border_color,
                           (center_x, center_y - cross_size),
                           (center_x, center_y + cross_size), 4)
        
        # 添加字母标识
        ascii_symbol = self.piece_symbols_ascii[
            'white' if piece_color == 1 else 'black'
        ][piece_type.lower()]
        
        text_surface = self.text_font.render(ascii_symbol, True, text_color)
        text_rect = text_surface.get_rect(center=(center_x, center_y + size//2 + 10))
        self.screen.blit(text_surface, text_rect)
    
    def draw_coordinates(self):
        """绘制坐标标签"""
        # 绘制列标签 (a-h)
        for col in range(8):
            x = self.margin + col * self.cell_size + self.cell_size // 2
            y = self.margin + self.board_height + 5
            label = chr(ord('a') + col)
            text_surface = self.small_font.render(label, True, self.colors['text'])
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)
        
        # 绘制行标签 (1-8)
        for row in range(8):
            x = self.margin - 15
            y = self.margin + row * self.cell_size + self.cell_size // 2
            label = str(8 - row)
            text_surface = self.small_font.render(label, True, self.colors['text'])
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)
    
    def draw_info_panel(self):
        """绘制信息面板"""
        panel_x = self.board_width + self.margin * 2
        panel_y = self.margin
        panel_width = self.info_panel_width - 20
        panel_height = self.board_height
        
        # 绘制面板背景
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, self.colors['info_bg'], panel_rect)
        pygame.draw.rect(self.screen, self.colors['border'], panel_rect, 2)
        
        # 绘制标题
        title_y = panel_y + 20
        title_text = "国际象棋"
        title_surface = self.title_font.render(title_text, True, self.colors['text'])
        title_rect = title_surface.get_rect(center=(panel_x + panel_width // 2, title_y))
        self.screen.blit(title_surface, title_rect)
        
        # 绘制当前玩家
        current_player_y = title_y + 40
        current_player_text = f"当前玩家: {'白方' if self.env.game.current_player == 1 else '黑方'}"
        current_player_surface = self.text_font.render(current_player_text, True, self.colors['text'])
        self.screen.blit(current_player_surface, (panel_x + 10, current_player_y))
        
        # 绘制游戏状态
        status_y = current_player_y + 30
        if self.env.game.is_terminal():
            winner = self.env.game.get_winner()
            if winner:
                status_text = f"将死！{'白方' if winner == 1 else '黑方'} 获胜!"
            else:
                status_text = "僵局！"
        elif hasattr(self.env.game, 'is_check') and self.env.game.is_check():
            status_text = f"{'白方' if self.env.game.current_player == 1 else '黑方'} 被将军!"
        else:
            status_text = "游戏进行中"
        
        status_surface = self.text_font.render(status_text, True, self.colors['text'])
        self.screen.blit(status_surface, (panel_x + 10, status_y))
        
        # 绘制步数
        moves_y = status_y + 30
        moves_text = f"步数: {len(self.env.game.move_history)}"
        moves_surface = self.text_font.render(moves_text, True, self.colors['text'])
        self.screen.blit(moves_surface, (panel_x + 10, moves_y))
        
        # 绘制吃掉的棋子
        captured_y = moves_y + 40
        captured_text = "被吃棋子:"
        captured_surface = self.text_font.render(captured_text, True, self.colors['text'])
        self.screen.blit(captured_surface, (panel_x + 10, captured_y))
        
        # 白方被吃的棋子
        white_captured_y = captured_y + 25
        white_captured_pieces = []
        black_captured_pieces = []
        
        # 获取被吃的棋子（简化显示）
        for color, pieces in self.env.game.captured_pieces.items():
            for piece in pieces:
                piece_type_name = piece.piece_type.name.lower()
                
                # 统一使用ASCII字符，更可靠
                if color.value == 1:  # 白方
                    symbol = self.piece_symbols_ascii['white'][piece_type_name]
                    white_captured_pieces.append(symbol)
                else:  # 黑方
                    symbol = self.piece_symbols_ascii['black'][piece_type_name]
                    black_captured_pieces.append(symbol)
        
        white_captured_text = "白方: " + "".join(white_captured_pieces)
        white_captured_surface = self.text_font.render(white_captured_text, True, self.colors['text'])
        self.screen.blit(white_captured_surface, (panel_x + 10, white_captured_y))
        
        # 黑方被吃的棋子
        black_captured_y = white_captured_y + 25
        black_captured_text = "黑方: " + "".join(black_captured_pieces)
        black_captured_surface = self.text_font.render(black_captured_text, True, self.colors['text'])
        self.screen.blit(black_captured_surface, (panel_x + 10, black_captured_y))
        
        # 绘制移动历史
        history_y = black_captured_y + 40
        history_text = "移动历史:"
        history_surface = self.text_font.render(history_text, True, self.colors['text'])
        self.screen.blit(history_surface, (panel_x + 10, history_y))
        
        # 显示最近的几步移动
        recent_moves = self.env.game.move_history[-8:]  # 最近8步
        for i, move in enumerate(recent_moves):
            move_y = history_y + 25 + i * 20
            move_text = f"{len(self.env.game.move_history) - len(recent_moves) + i + 1}. {str(move)}"
            move_surface = self.small_font.render(move_text, True, self.colors['text'])
            self.screen.blit(move_surface, (panel_x + 10, move_y))
        
        # 绘制控制说明
        controls_y = self.board_height - 100
        controls_text = [
            "控制说明:",
            "• 点击棋子选择",
            "• 点击目标位置移动",
            "• ESC键退出"
        ]
        
        for i, text in enumerate(controls_text):
            y = controls_y + i * 18
            text_surface = self.small_font.render(text, True, self.colors['text'])
            self.screen.blit(text_surface, (panel_x + 10, y))
    
    def draw_buttons(self):
        """绘制按钮"""
        mouse_pos = pygame.mouse.get_pos()
        
        for button_name, button_info in self.buttons.items():
            rect = button_info['rect']
            color = button_info['color']
            text = button_info['text']
            
            # 鼠标悬停效果
            if rect.collidepoint(mouse_pos):
                color = self.colors['button_hover']
            
            # 绘制按钮
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, self.colors['border'], rect, 2)
            
            # 绘制按钮文字
            text_surface = self.text_font.render(text, True, self.colors['button_text'])
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)

def main():
    """主函数"""
    try:
        game = ChessGUI()
        game.run()
    except KeyboardInterrupt:
        print("\n游戏被用户中断")
    except Exception as e:
        print(f"游戏运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 