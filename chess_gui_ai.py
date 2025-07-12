#!/usr/bin/env python3
"""
国际象棋 GUI 界面 - 玩家vs AI模式
Stockfish作为对战AI，LLM作为可选教练
"""

import pygame
import sys
import time
import threading
from typing import Dict, Tuple, Any, Optional, List
from games.chess.chess_game import ChessGame
from games.chess.chess_env import ChessEnv
from agents.ai_bots.llm_chess_assistant import LLMChessCoach
from agents.ai_bots.stockfish_chess_ai import StockfishChessAI

class ChessGUIAI:
    """国际象棋游戏 GUI 界面 - 玩家vs AI模式"""
    
    def __init__(self):
        # 初始化pygame
        pygame.init()
        
        # 界面参数
        self.board_size = 8
        self.cell_size = 70
        self.board_width = self.board_size * self.cell_size
        self.board_height = self.board_size * self.cell_size
        self.info_panel_width = 400  # 增加信息面板宽度
        self.margin = 30
        self.window_width = self.board_width + self.info_panel_width + self.margin * 2
        self.window_height = self.board_height + self.margin * 2
        
        # 创建窗口
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("国际象棋 - 玩家vs AI (Stockfish)")
        
        # 字体初始化
        self.text_font = self._init_chinese_font(16)
        self.title_font = self._init_chinese_font(20)
        self.small_font = self._init_chinese_font(14)
        self.large_font = self._init_unicode_font(40)
        
        # 颜色定义
        self.colors = {
            'light_square': (240, 217, 181),
            'dark_square': (181, 136, 99),
            'selected': (255, 255, 0),
            'possible_move': (144, 238, 144),
            'last_move': (255, 255, 102),
            'check': (255, 0, 0),
            'white_piece': (255, 255, 255),
            'black_piece': (0, 0, 0),
            'background': (248, 248, 248),
            'info_bg': (245, 245, 245),
            'border': (100, 100, 100),
            'text': (50, 50, 50),
            'button': (200, 200, 200),
            'button_hover': (180, 180, 180),
            'button_text': (0, 0, 0),
            'ai_thinking': (255, 200, 100),
            'evaluation_good': (144, 238, 144),
            'evaluation_bad': (255, 182, 193),
            'coach_active': (144, 238, 144),
            'coach_inactive': (200, 200, 200),
        }
        
        # 棋子Unicode符号
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
        
        # 游戏状态
        self.env = ChessEnv()
        
        # AI设置 - 只有Stockfish作为对战AI
        self.ai_agent = StockfishChessAI(name="Stockfish", player_id=2, difficulty=8)
        
        # LLM教练设置 - 可选功能
        self.coach_enabled = True  # 默认启用教练
        self.coach = LLMChessCoach(name="LLM教练") if self.coach_enabled else None
        
        self.game_running = True
        self.clock = pygame.time.Clock()
        
        # 游戏模式 - 默认玩家是白方（1），AI是黑方（2）
        self.human_player = 1
        self.ai_player = 2
        self.ai_thinking = False
        
        # 界面状态
        self.selected_square = None
        self.possible_moves = []
        self.last_move_from = None
        self.last_move_to = None
        
        # 教练功能状态
        self.current_evaluation = None
        self.coach_hint = None
        self.show_review = False
        self.game_review = None
        self.last_move_state = None  # 用于移动评价
        
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
                'text': '获取提示',
                'color': self.colors['button'] if self.coach_enabled else self.colors['coach_inactive']
            },
            'review': {
                'rect': pygame.Rect(start_x, 100, btn_width, btn_height),
                'text': '复盘分析',
                'color': self.colors['button'] if self.coach_enabled else self.colors['coach_inactive']
            },
            'difficulty': {
                'rect': pygame.Rect(start_x + 140, 100, btn_width, btn_height),
                'text': '难度: 困难',
                'color': self.colors['button']
            },
            'coach_toggle': {
                'rect': pygame.Rect(start_x, 150, btn_width, btn_height),
                'text': '教练: 开启',
                'color': self.colors['coach_active'] if self.coach_enabled else self.colors['coach_inactive']
            },
            'quit': {
                'rect': pygame.Rect(start_x + 140, 150, btn_width, btn_height),
                'text': '退出',
                'color': (255, 200, 200)
            }
        }
        
        return buttons
    
    def handle_button_click(self, button_name: str):
        """处理按钮点击"""
        if button_name == 'new_game':
            self.reset_game()
        elif button_name == 'hint':
            if self.coach_enabled:
                self.show_coach_hint()
            else:
                print("教练功能已禁用")
        elif button_name == 'review':
            if self.coach_enabled:
                self.show_game_review()
            else:
                print("教练功能已禁用")
        elif button_name == 'difficulty':
            self.change_difficulty()
        elif button_name == 'coach_toggle':
            self.toggle_coach()
        elif button_name == 'quit':
            self.game_running = False
    
    def toggle_coach(self):
        """切换教练功能"""
        self.coach_enabled = not self.coach_enabled
        
        if self.coach_enabled:
            self.coach = LLMChessCoach(name="LLM教练")
            self.buttons['coach_toggle']['text'] = '教练: 开启'
            self.buttons['coach_toggle']['color'] = self.colors['coach_active']
            self.buttons['hint']['color'] = self.colors['button']
            self.buttons['review']['color'] = self.colors['button']
            print("✅ LLM教练已启用！现在可以获取提示和复盘分析")
        else:
            self.coach = None
            self.buttons['coach_toggle']['text'] = '教练: 关闭'
            self.buttons['coach_toggle']['color'] = self.colors['coach_inactive']
            self.buttons['hint']['color'] = self.colors['coach_inactive']
            self.buttons['review']['color'] = self.colors['coach_inactive']
            # 清除教练相关显示
            self.current_evaluation = None
            self.coach_hint = None
            self.show_review = False
            print("❌ LLM教练已禁用")
    
    def show_coach_hint(self):
        """显示教练提示"""
        if not self.coach_enabled or not self.coach:
            return
        
        try:
            observation = self.env._get_observation()
            state = self.env.game.get_state()
            
            hint_result = self.coach.provide_hint(state, self.env.game)
            self.coach_hint = hint_result
            
            print(f"🎯 教练提示: {hint_result.get('hint', '无提示')}")
            print(f"📊 分析: {hint_result.get('analysis', '无分析')}")
            
        except Exception as e:
            print(f"❌ 获取教练提示失败: {e}")
    
    def evaluate_player_move(self, move: Tuple[Tuple[int, int], Tuple[int, int]]):
        """评价玩家移动"""
        if not self.coach_enabled or not self.coach:
            return
        
        try:
            if self.last_move_state is not None:
                current_state = self.env.game.get_state()
                evaluation = self.coach.evaluate_move(move, self.last_move_state, current_state)
                self.current_evaluation = evaluation
                
                print(f"🎭 移动评价: {evaluation.get('evaluation', '无评价')}")
                print(f"📈 评分: {evaluation.get('score', 0):.1f}")
                
        except Exception as e:
            print(f"❌ 移动评价失败: {e}")
    
    def make_move(self, from_row: int, from_col: int, to_row: int, to_col: int):
        """执行移动"""
        if self.env.game.is_terminal():
            return
        
        # 保存移动前状态用于教练评价
        if self.coach_enabled:
            self.last_move_state = self.env.game.get_state()
        
        # 执行移动
        try:
            move = ((from_row, from_col), (to_row, to_col))
            observation, reward, done, info = self.env.step(move)
            
            # 更新界面状态
            self.last_move_from = (from_row, from_col)
            self.last_move_to = (to_row, to_col)
            self.selected_square = None
            self.possible_moves = []
            
            # 如果是玩家移动，进行教练评价
            if self.env.game.current_player == self.ai_player:  # 玩家刚移动完，现在轮到AI
                self.evaluate_player_move(move)
            
            # 检查游戏是否结束
            if done:
                winner = self.env.game.get_winner()
                if winner == 1:
                    print("🎉 恭喜！您获胜了！")
                elif winner == 2:
                    print("😞 很遗憾，AI获胜了。")
                else:
                    print("🤝 平局！")
                
                # 如果教练启用，提供游戏总结
                if self.coach_enabled and self.coach:
                    print("🎓 教练建议进行复盘分析，点击'复盘分析'按钮查看详细分析。")
                    
        except Exception as e:
            print(f"❌ 移动失败: {e}")
    
    def change_difficulty(self):
        """改变AI难度"""
        # Stockfish使用数字难度：2(简单) -> 5(中等) -> 8(困难) -> 10(大师) -> 2(简单)
        current_difficulty = self.ai_agent.difficulty
        if current_difficulty <= 2:
            new_difficulty = 5
            difficulty_text = '难度: 中等'
        elif current_difficulty <= 5:
            new_difficulty = 8
            difficulty_text = '难度: 困难'
        elif current_difficulty <= 8:
            new_difficulty = 10
            difficulty_text = '难度: 大师'
        else:  # current_difficulty >= 10
            new_difficulty = 2
            difficulty_text = '难度: 简单'
        
        self.ai_agent.set_difficulty(new_difficulty)
        self.buttons['difficulty']['text'] = difficulty_text
        
        print(f"🎯 AI难度已调整为: {new_difficulty} ({difficulty_text})")
        
        # 重置游戏以应用新难度
        self.reset_game()
    
    def show_game_review(self):
        """显示游戏复盘分析"""
        if not self.coach_enabled or not self.coach:
            print("教练功能已禁用，无法进行复盘分析")
            return
        
        if self.env.game.is_terminal():
            try:
                # 获取游戏历史
                game_history = self.env.game.history
                if game_history:
                    review = self.coach.provide_game_review(game_history)
                    self.game_review = review
                    self.show_review = True
                    
                    print("🎓 游戏复盘分析:")
                    print(f"📊 整体表现: {review.get('overall_performance', '无数据')}")
                    print(f"🏆 优势: {', '.join(review.get('strengths', []))}")
                    print(f"⚠️ 待改进: {', '.join(review.get('weaknesses', []))}")
                    print(f"💡 建议: {', '.join(review.get('recommendations', []))}")
                else:
                    print("没有足够的游戏历史进行分析")
            except Exception as e:
                print(f"❌ 复盘分析失败: {e}")
        else:
            print("游戏未结束，无法进行完整复盘分析")
    
    def reset_game(self):
        """重置游戏"""
        self.env.reset()
        if self.coach_enabled and self.coach:
            self.coach.reset_analysis()
        self.selected_square = None
        self.possible_moves = []
        self.last_move_from = None
        self.last_move_to = None
        self.current_evaluation = None
        self.coach_hint = None
        self.show_review = False
        self.game_review = None
        self.last_move_state = None
        self.ai_thinking = False
        print("🎮 游戏重置完成")
        
        # 显示当前配置
        coach_status = "开启" if self.coach_enabled else "关闭"
        print(f"⚙️ 当前配置: Stockfish难度{self.ai_agent.difficulty}, LLM教练{coach_status}")
    
    def run(self):
        """运行游戏主循环"""
        print("🎮 启动国际象棋 AI 模式")
        
        while self.game_running:
            # 处理事件
            self.handle_events()
            
            if not self.game_running:
                break
            
            # AI回合处理
            if (self.env.game.current_player == self.ai_player and 
                not self.env.game.is_terminal() and 
                not self.ai_thinking):
                self.handle_ai_turn()
            
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
        
        # 只有轮到人类玩家时才能点击棋盘
        if self.env.game.current_player == self.human_player and not self.ai_thinking:
            # 检查是否点击了棋盘
            if (self.margin <= x <= self.margin + self.board_width and
                self.margin <= y <= self.margin + self.board_height):
                
                # 计算点击的格子
                col = (x - self.margin) // self.cell_size
                row = (y - self.margin) // self.cell_size
                
                if 0 <= row < 8 and 0 <= col < 8:
                    self.handle_square_click(row, col)
    
    def handle_square_click(self, row: int, col: int):
        """处理棋盘格子点击"""
        if self.env.game.is_terminal() or self.ai_thinking:
            return
        
        # 获取当前棋盘状态
        board = self.env.game.board
        
        # 如果没有选中的格子
        if self.selected_square is None:
            # 检查点击的格子是否有本方棋子
            piece = board[row][col]
            if piece is not None:
                current_player = self.env.game.current_player
                piece_color = piece.color.value
                
                if piece_color == current_player:
                    self.selected_square = (row, col)
                    self.possible_moves = self.get_possible_moves(row, col)
                    print(f"选中了棋子在 ({row}, {col})")
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
                  board[selected_row][selected_col] is not None and
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
    
    def handle_ai_turn(self):
        """处理AI回合"""
        if self.env.game.is_terminal():
            return
        
        self.ai_thinking = True
        
        # 在后台线程中执行AI思考
        def ai_think():
            try:
                # 获取AI的移动
                observation = self.env._get_observation()
                ai_move = self.ai_agent.get_action(observation, self.env)
                
                if ai_move:
                    # 执行AI移动
                    _, _, done, _, info = self.env.step(ai_move)
                    
                    # 更新显示
                    self.last_move_from = ai_move[0]
                    self.last_move_to = ai_move[1]
                    
                    # 获取AI的评价
                    if hasattr(self.ai_agent, 'get_last_move_evaluation'):
                        self.current_evaluation = self.ai_agent.get_last_move_evaluation()
                    else:
                        self.current_evaluation = None
                    
                    print(f"AI移动: {chr(ord('a') + ai_move[0][1])}{8 - ai_move[0][0]} -> {chr(ord('a') + ai_move[1][1])}{8 - ai_move[1][0]}")
                    
                    if self.current_evaluation:
                        analysis = self.current_evaluation.get('analysis', '无分析')
                        print(f"AI评价: {analysis}")
                
            except Exception as e:
                print(f"AI思考出错: {e}")
            finally:
                self.ai_thinking = False
        
        # 启动AI思考线程
        threading.Thread(target=ai_think, daemon=True).start()
    
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
        
        # 如果显示复盘，绘制复盘面板
        if self.show_review and self.game_review:
            self.draw_review_panel()
        
        # 更新屏幕
        pygame.display.flip()
    
    def draw_board(self):
        """绘制棋盘"""
        # 绘制棋盘背景
        for row in range(8):
            for col in range(8):
                x = self.margin + col * self.cell_size
                y = self.margin + row * self.cell_size
                
                # 确定格子颜色
                if (row + col) % 2 == 0:
                    color = self.colors['light_square']
                else:
                    color = self.colors['dark_square']
                
                # 高亮选中的格子
                if self.selected_square == (row, col):
                    color = self.colors['selected']
                # 高亮可能的移动
                elif (row, col) in self.possible_moves:
                    color = self.colors['possible_move']
                # 高亮上一步移动
                elif (self.last_move_from == (row, col) or 
                      self.last_move_to == (row, col)):
                    color = self.colors['last_move']
                
                # 绘制格子
                pygame.draw.rect(self.screen, color, 
                               (x, y, self.cell_size, self.cell_size))
                
                # 绘制边框
                pygame.draw.rect(self.screen, self.colors['border'], 
                               (x, y, self.cell_size, self.cell_size), 1)
                
                # 绘制棋子
                piece = self.env.game.board[row][col]
                if piece is not None:
                    center_x = x + self.cell_size // 2
                    center_y = y + self.cell_size // 2
                    self.draw_piece(piece, center_x, center_y)
    
    def draw_piece(self, piece, center_x: int, center_y: int):
        """绘制棋子"""
        # 确定棋子颜色和符号
        if piece.color.value == 1:  # 白方
            color = self.colors['black_piece']  # 黑色字体
            symbols = self.piece_symbols['white']
        else:  # 黑方
            color = self.colors['white_piece']  # 白色字体
            symbols = self.piece_symbols['black']
        
        # 获取棋子符号
        piece_type = piece.piece_type.name.lower()
        symbol = symbols.get(piece_type, piece_type[0].upper())
        
        # 渲染棋子
        try:
            piece_surface = self.large_font.render(symbol, True, color)
            piece_rect = piece_surface.get_rect(center=(center_x, center_y))
            self.screen.blit(piece_surface, piece_rect)
        except:
            # 备用方案：绘制简单的圆形
            pygame.draw.circle(self.screen, color, (center_x, center_y), 20)
    
    def draw_info_panel(self):
        """绘制信息面板"""
        panel_x = self.board_width + self.margin * 2
        panel_y = self.margin
        panel_width = self.info_panel_width - 20
        
        # 绘制面板背景
        pygame.draw.rect(self.screen, self.colors['info_bg'], 
                        (panel_x, panel_y, panel_width, self.board_height))
        
        y_offset = panel_y + 20
        line_height = 25
        
        # 游戏状态信息
        current_player = "白方" if self.env.game.current_player == 1 else "黑方"
        
        # 标题
        title = self.title_font.render("游戏状态", True, self.colors['text'])
        self.screen.blit(title, (panel_x + 10, y_offset))
        y_offset += 35
        
        # 当前玩家
        player_text = f"当前玩家: {current_player}"
        if self.ai_thinking:
            player_text += " (AI思考中...)"
        player_surface = self.text_font.render(player_text, True, self.colors['text'])
        self.screen.blit(player_surface, (panel_x + 10, y_offset))
        y_offset += line_height
        
        # AI信息
        ai_info = f"对手: Stockfish (难度{self.ai_agent.difficulty})"
        ai_surface = self.text_font.render(ai_info, True, self.colors['text'])
        self.screen.blit(ai_surface, (panel_x + 10, y_offset))
        y_offset += line_height
        
        # 教练状态
        coach_status = "开启" if self.coach_enabled else "关闭"
        coach_text = f"教练: {coach_status}"
        coach_color = self.colors['coach_active'] if self.coach_enabled else self.colors['text']
        coach_surface = self.text_font.render(coach_text, True, coach_color)
        self.screen.blit(coach_surface, (panel_x + 10, y_offset))
        y_offset += line_height * 2
        
        # 游戏状态
        if self.env.game.is_terminal():
            winner = self.env.game.get_winner()
            if winner:
                winner_name = "白方" if winner == 1 else "黑方"
                status_text = f"游戏结束 - {winner_name}获胜"
            else:
                status_text = "游戏结束 - 平局"
        else:
            status_text = "游戏进行中"
        
        status_surface = self.text_font.render(status_text, True, self.colors['text'])
        self.screen.blit(status_surface, (panel_x + 10, y_offset))
        y_offset += line_height * 2
        
        # 教练信息（如果启用）
        if self.coach_enabled and self.coach:
            coach_title = self.title_font.render("教练信息", True, self.colors['text'])
            self.screen.blit(coach_title, (panel_x + 10, y_offset))
            y_offset += 35
            
            # 显示最近的移动评价
            if self.current_evaluation:
                eval_text = f"上步评价: {self.current_evaluation.get('level', 'unknown')}"
                eval_color = self.colors['evaluation_good'] if self.current_evaluation.get('score', 0) > 0 else self.colors['evaluation_bad']
                eval_surface = self.text_font.render(eval_text, True, eval_color)
                self.screen.blit(eval_surface, (panel_x + 10, y_offset))
                y_offset += line_height
                
                # 显示评价详情
                evaluation_text = self.current_evaluation.get('evaluation', '')
                if len(evaluation_text) > 25:
                    evaluation_text = evaluation_text[:25] + "..."
                detail_surface = self.small_font.render(evaluation_text, True, self.colors['text'])
                self.screen.blit(detail_surface, (panel_x + 10, y_offset))
                y_offset += line_height
            
            # 显示提示信息
            if self.coach_hint:
                hint_text = self.coach_hint.get('hint', '')
                if len(hint_text) > 30:
                    hint_text = hint_text[:30] + "..."
                hint_surface = self.small_font.render(f"提示: {hint_text}", True, self.colors['text'])
                self.screen.blit(hint_surface, (panel_x + 10, y_offset))
                y_offset += line_height
        
        # 如果显示复盘分析
        if self.show_review and self.game_review:
            self.draw_review_panel()
    
    def draw_buttons(self):
        """绘制按钮"""
        for button_name, button_info in self.buttons.items():
            rect = button_info['rect']
            color = button_info['color']
            text = button_info['text']
            
            # 绘制按钮背景
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, self.colors['border'], rect, 2)
            
            # 绘制按钮文字
            text_surface = self.text_font.render(text, True, self.colors['button_text'])
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def draw_review_panel(self):
        """绘制复盘面板"""
        if not self.game_review:
            return
        
        # 创建半透明背景
        overlay = pygame.Surface((self.window_width, self.window_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 复盘面板
        panel_width = 600
        panel_height = 400
        panel_x = (self.window_width - panel_width) // 2
        panel_y = (self.window_height - panel_height) // 2
        
        # 绘制面板背景
        pygame.draw.rect(self.screen, self.colors['info_bg'], 
                        (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, self.colors['border'], 
                        (panel_x, panel_y, panel_width, panel_height), 3)
        
        # 绘制复盘内容
        y_offset = panel_y + 20
        line_height = 25
        
        # 标题
        title = self.title_font.render("复盘分析", True, self.colors['text'])
        self.screen.blit(title, (panel_x + 20, y_offset))
        y_offset += 40
        
        # 统计信息
        stats_text = f"总移动数: {self.game_review['total_moves']}"
        stats_surface = self.text_font.render(stats_text, True, self.colors['text'])
        self.screen.blit(stats_surface, (panel_x + 20, y_offset))
        y_offset += line_height
        
        avg_score_text = f"平均分数: {self.game_review['average_score']}"
        avg_surface = self.text_font.render(avg_score_text, True, self.colors['text'])
        self.screen.blit(avg_surface, (panel_x + 20, y_offset))
        y_offset += line_height * 2
        
        # 总体评价
        comment = self.game_review['overall_comment']
        comment_lines = [comment[i:i+40] for i in range(0, len(comment), 40)]
        for line in comment_lines[:3]:  # 最多显示3行
            comment_surface = self.text_font.render(line, True, self.colors['text'])
            self.screen.blit(comment_surface, (panel_x + 20, y_offset))
            y_offset += line_height
        
        # 改进建议
        y_offset += 20
        suggestion_title = self.title_font.render("改进建议:", True, self.colors['text'])
        self.screen.blit(suggestion_title, (panel_x + 20, y_offset))
        y_offset += 30
        
        for suggestion in self.game_review['improvement_suggestions'][:3]:
            suggestion_lines = [suggestion[i:i+35] for i in range(0, len(suggestion), 35)]
            for line in suggestion_lines[:2]:  # 每个建议最多2行
                suggestion_surface = self.small_font.render(f"• {line}", True, self.colors['text'])
                self.screen.blit(suggestion_surface, (panel_x + 30, y_offset))
                y_offset += 20
        
        # 关闭按钮
        close_button = pygame.Rect(panel_x + panel_width - 80, panel_y + 10, 60, 30)
        pygame.draw.rect(self.screen, self.colors['button'], close_button)
        pygame.draw.rect(self.screen, self.colors['border'], close_button, 2)
        close_text = self.text_font.render("关闭", True, self.colors['button_text'])
        close_rect = close_text.get_rect(center=close_button.center)
        self.screen.blit(close_text, close_rect)
        
        # 检查关闭按钮点击
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and close_button.collidepoint(mouse_pos):
            self.show_review = False

def main():
    """主函数"""
    try:
        game = ChessGUIAI()
        game.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 