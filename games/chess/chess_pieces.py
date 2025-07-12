"""
国际象棋棋子定义和移动规则
"""

from typing import List, Tuple, Optional
from enum import Enum
import numpy as np

class Color(Enum):
    """棋子颜色"""
    WHITE = 1
    BLACK = 2

class PieceType(Enum):
    """棋子类型"""
    PAWN = 1    # 兵
    ROOK = 2    # 车
    KNIGHT = 3  # 马
    BISHOP = 4  # 象
    QUEEN = 5   # 后
    KING = 6    # 王

class ChessPiece:
    """国际象棋棋子基类"""
    
    def __init__(self, color: Color, piece_type: PieceType, position: Tuple[int, int]):
        self.color = color
        self.piece_type = piece_type
        self.position = position
        self.has_moved = False  # 用于王车易位和兵的双步移动
        
    def __str__(self):
        """棋子的字符串表示"""
        symbols = {
            (Color.WHITE, PieceType.PAWN): '♙',
            (Color.WHITE, PieceType.ROOK): '♖',
            (Color.WHITE, PieceType.KNIGHT): '♘',
            (Color.WHITE, PieceType.BISHOP): '♗',
            (Color.WHITE, PieceType.QUEEN): '♕',
            (Color.WHITE, PieceType.KING): '♔',
            (Color.BLACK, PieceType.PAWN): '♟',
            (Color.BLACK, PieceType.ROOK): '♜',
            (Color.BLACK, PieceType.KNIGHT): '♞',
            (Color.BLACK, PieceType.BISHOP): '♝',
            (Color.BLACK, PieceType.QUEEN): '♛',
            (Color.BLACK, PieceType.KING): '♚',
        }
        return symbols.get((self.color, self.piece_type), '?')
    
    def get_possible_moves(self, board: np.ndarray, current_pos: Tuple[int, int] = None) -> List[Tuple[int, int]]:
        """获取可能的移动位置（不考虑将军等规则）"""
        # 使用传入的当前位置，如果没有则使用self.position
        if current_pos is not None:
            old_position = self.position
            self.position = current_pos
        
        if self.piece_type == PieceType.PAWN:
            moves = self._get_pawn_moves(board)
        elif self.piece_type == PieceType.ROOK:
            moves = self._get_rook_moves(board)
        elif self.piece_type == PieceType.KNIGHT:
            moves = self._get_knight_moves(board)
        elif self.piece_type == PieceType.BISHOP:
            moves = self._get_bishop_moves(board)
        elif self.piece_type == PieceType.QUEEN:
            moves = self._get_queen_moves(board)
        elif self.piece_type == PieceType.KING:
            moves = self._get_king_moves(board)
        else:
            moves = []
        
        # 恢复原来的位置（如果临时修改了的话）
        if current_pos is not None:
            self.position = old_position
            
        return moves
    
    def _get_pawn_moves(self, board: np.ndarray) -> List[Tuple[int, int]]:
        """兵的移动规则"""
        moves = []
        row, col = self.position
        direction = -1 if self.color == Color.WHITE else 1  # 白兵向上，黑兵向下
        
        # 前进一步
        new_row = row + direction
        if 0 <= new_row < 8 and board[new_row, col] is None:
            moves.append((new_row, col))
            
            # 前进两步（首次移动）
            if not self.has_moved:
                new_row = row + 2 * direction
                if 0 <= new_row < 8 and board[new_row, col] is None:
                    moves.append((new_row, col))
        
        # 斜向吃子
        for dc in [-1, 1]:
            new_row, new_col = row + direction, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board[new_row, new_col]
                if target is not None and target.color != self.color:
                    moves.append((new_row, new_col))
        
        return moves
    
    def _get_rook_moves(self, board: np.ndarray) -> List[Tuple[int, int]]:
        """车的移动规则"""
        moves = []
        row, col = self.position
        
        # 水平和垂直方向
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * dr, col + i * dc
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target = board[new_row, new_col]
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    moves.append((new_row, new_col))
                    break  # 吃子后停止
                else:
                    break  # 遇到己方棋子停止
        
        return moves
    
    def _get_knight_moves(self, board: np.ndarray) -> List[Tuple[int, int]]:
        """马的移动规则"""
        moves = []
        row, col = self.position
        
        # 马的8个可能移动方向
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board[new_row, new_col]
                if target is None or target.color != self.color:
                    moves.append((new_row, new_col))
        
        return moves
    
    def _get_bishop_moves(self, board: np.ndarray) -> List[Tuple[int, int]]:
        """象的移动规则"""
        moves = []
        row, col = self.position
        
        # 对角线方向
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * dr, col + i * dc
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target = board[new_row, new_col]
                if target is None:
                    moves.append((new_row, new_col))
                elif target.color != self.color:
                    moves.append((new_row, new_col))
                    break
                else:
                    break
        
        return moves
    
    def _get_queen_moves(self, board: np.ndarray) -> List[Tuple[int, int]]:
        """后的移动规则（车+象）"""
        return self._get_rook_moves(board) + self._get_bishop_moves(board)
    
    def _get_king_moves(self, board: np.ndarray) -> List[Tuple[int, int]]:
        """王的移动规则"""
        moves = []
        row, col = self.position
        
        # 王的8个方向，每个方向只能走一步
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = board[new_row, new_col]
                if target is None or target.color != self.color:
                    moves.append((new_row, new_col))
        
        return moves
    
    def copy(self):
        """创建棋子的副本"""
        piece = ChessPiece(self.color, self.piece_type, self.position)
        piece.has_moved = self.has_moved
        return piece 