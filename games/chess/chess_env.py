"""
国际象棋环境
实现gym风格接口
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from games.base_env import BaseEnv
from .chess_game import ChessGame

class ChessEnv(BaseEnv):
    """国际象棋环境"""
    
    def __init__(self, **kwargs):
        game = ChessGame(**kwargs)
        super().__init__(game)
    
    def _setup_spaces(self):
        """设置观察空间和动作空间"""
        # 观察空间：8x8棋盘，每个位置可以是0-12的值
        self.observation_space = None
        # 动作空间：从任意位置到任意位置的移动
        self.action_space = None
    
    def _get_observation(self) -> np.ndarray:
        """获取观察"""
        state = self.game.get_state()
        return state['board']
    
    def _get_action_mask(self) -> np.ndarray:
        """获取动作掩码"""
        # 创建一个64x64的掩码矩阵，表示从每个位置到每个位置的移动是否有效
        mask = np.zeros((64, 64), dtype=bool)
        valid_moves = self.game.get_valid_actions()
        
        for from_pos, to_pos in valid_moves:
            from_idx = from_pos[0] * 8 + from_pos[1]
            to_idx = to_pos[0] * 8 + to_pos[1]
            mask[from_idx, to_idx] = True
        
        return mask
    
    def get_valid_actions(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """获取有效动作"""
        return self.game.get_valid_actions()
    
    def is_terminal(self) -> bool:
        """检查游戏是否结束"""
        return self.game.is_terminal()
    
    def get_winner(self) -> Optional[int]:
        """获取获胜者"""
        return self.game.get_winner()
    
    def render(self, mode: str = 'human'):
        """渲染环境"""
        if mode == 'human':
            print(self.game.render())
            return self.game.render()
        elif mode == 'rgb_array':
            return self._render_rgb_array()
        else:
            return self.game.render()
    
    def _render_rgb_array(self) -> np.ndarray:
        """渲染为RGB数组（用于图形界面）"""
        # 创建一个简单的RGB图像表示
        board = self.game.board
        img = np.ones((8 * 60, 8 * 60, 3), dtype=np.uint8) * 255
        
        # 棋盘格子颜色
        for row in range(8):
            for col in range(8):
                x, y = col * 60, row * 60
                
                # 棋盘格子颜色（黑白相间）
                if (row + col) % 2 == 0:
                    img[y:y+60, x:x+60] = [240, 217, 181]  # 浅色格子
                else:
                    img[y:y+60, x:x+60] = [181, 136, 99]   # 深色格子
                
                # 绘制棋子（简化版）
                piece = board[row, col]
                if piece:
                    center_x, center_y = x + 30, y + 30
                    if piece.color.value == 1:  # 白方
                        img[center_y-20:center_y+20, center_x-20:center_x+20] = [255, 255, 255]
                    else:  # 黑方
                        img[center_y-20:center_y+20, center_x-20:center_x+20] = [0, 0, 0]
        
        return img
    
    def get_board_state(self) -> np.ndarray:
        """获取棋盘状态"""
        state = self.game.get_state()
        return state['board']
    
    def get_game_state(self) -> Dict[str, Any]:
        """获取完整游戏状态"""
        return self.game.get_state()
    
    def get_fen(self) -> str:
        """获取FEN字符串"""
        return self.game.get_fen()
    
    def get_natural_language_state(self) -> str:
        """获取自然语言描述的游戏状态（为LLM AI准备）"""
        return self.game.get_natural_language_state()
    
    def parse_move_notation(self, notation: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """解析移动记谱法"""
        if len(notation) < 4:
            return None
        
        try:
            # 标准格式：e2e4
            cols = "abcdefgh"
            rows = "87654321"
            
            from_col = cols.index(notation[0])
            from_row = rows.index(notation[1])
            to_col = cols.index(notation[2])
            to_row = rows.index(notation[3])
            
            return ((from_row, from_col), (to_row, to_col))
        except (ValueError, IndexError):
            return None
    
    def is_move_legal(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """检查移动是否合法"""
        valid_moves = self.get_valid_actions()
        return (from_pos, to_pos) in valid_moves
    
    def get_piece_at(self, pos: Tuple[int, int]):
        """获取指定位置的棋子"""
        row, col = pos
        if 0 <= row < 8 and 0 <= col < 8:
            return self.game.board[row, col]
        return None
    
    def get_attacked_squares(self, color_value: int) -> List[Tuple[int, int]]:
        """获取被指定颜色攻击的所有格子"""
        from .chess_pieces import Color
        color = Color.WHITE if color_value == 1 else Color.BLACK
        attacked_squares = []
        
        for row in range(8):
            for col in range(8):
                if self.game._is_square_attacked((row, col), color):
                    attacked_squares.append((row, col))
        
        return attacked_squares
    
    def clone(self) -> 'ChessEnv':
        """克隆环境"""
        cloned_game = self.game.clone()
        cloned_env = ChessEnv()
        cloned_env.game = cloned_game
        return cloned_env 