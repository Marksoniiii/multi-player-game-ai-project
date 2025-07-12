"""
国际象棋游戏核心逻辑
"""

import numpy as np
import copy
from typing import Dict, List, Tuple, Any, Optional, Union
from games.base_game import BaseGame
from .chess_pieces import ChessPiece, Color, PieceType
import config

class ChessMove:
    """国际象棋移动表示"""
    
    def __init__(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                 piece: ChessPiece, captured_piece: Optional[ChessPiece] = None,
                 promotion_piece: Optional[PieceType] = None, 
                 is_castling: bool = False, is_en_passant: bool = False):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.piece = piece
        self.captured_piece = captured_piece
        self.promotion_piece = promotion_piece
        self.is_castling = is_castling
        self.is_en_passant = is_en_passant
    
    def __str__(self):
        """国际象棋标准记谱法"""
        cols = "abcdefgh"
        rows = "87654321"
        
        from_square = cols[self.from_pos[1]] + rows[self.from_pos[0]]
        to_square = cols[self.to_pos[1]] + rows[self.to_pos[0]]
        
        notation = from_square + to_square
        
        if self.promotion_piece:
            promotion_symbols = {
                PieceType.QUEEN: 'q',
                PieceType.ROOK: 'r',
                PieceType.BISHOP: 'b',
                PieceType.KNIGHT: 'n'
            }
            notation += promotion_symbols.get(self.promotion_piece, 'q')
        
        return notation
    
    def to_dict(self):
        """转换为字典格式，便于序列化"""
        return {
            'from': self.from_pos,
            'to': self.to_pos,
            'piece_type': self.piece.piece_type.value,
            'piece_color': self.piece.color.value,
            'captured': self.captured_piece.piece_type.value if self.captured_piece else None,
            'promotion': self.promotion_piece.value if self.promotion_piece else None,
            'castling': self.is_castling,
            'en_passant': self.is_en_passant,
            'notation': str(self)
        }

class ChessGame(BaseGame):
    """国际象棋游戏"""
    
    def __init__(self, **kwargs):
        # 初始化棋盘
        self.board = np.full((8, 8), None, dtype=object)
        self.captured_pieces = {Color.WHITE: [], Color.BLACK: []}
        self.move_history = []
        self.en_passant_target = None  # 吃过路兵的目标位置
        self.castling_rights = {
            Color.WHITE: {'kingside': True, 'queenside': True},
            Color.BLACK: {'kingside': True, 'queenside': True}
        }
        self.halfmove_clock = 0  # 50步规则计数器
        self.fullmove_number = 1
        
        # 游戏配置
        game_config = {
            'max_moves': kwargs.get('max_moves', 200),  # 最大回合数
            'timeout': kwargs.get('timeout', 1800),     # 30分钟时限
        }
        
        super().__init__(game_config)
        
    def reset(self) -> Dict[str, Any]:
        """重置游戏到初始状态"""
        self.board = np.full((8, 8), None, dtype=object)
        self.captured_pieces = {Color.WHITE: [], Color.BLACK: []}
        self.move_history = []
        self.en_passant_target = None
        self.castling_rights = {
            Color.WHITE: {'kingside': True, 'queenside': True},
            Color.BLACK: {'kingside': True, 'queenside': True}
        }
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.current_player = 1  # 白方先行
        self.game_state = config.GameState.ONGOING
        self.move_count = 0
        self.history = []
        
        # 初始化棋盘
        self._setup_initial_position()
        
        return self.get_state()
    
    def _setup_initial_position(self):
        """设置初始棋盘位置"""
        # 设置白方棋子（底部，行7和6）
        # 白兵
        for col in range(8):
            self.board[6, col] = ChessPiece(Color.WHITE, PieceType.PAWN, (6, col))
        
        # 白方主力棋子
        piece_order = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
                      PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]
        for col, piece_type in enumerate(piece_order):
            self.board[7, col] = ChessPiece(Color.WHITE, piece_type, (7, col))
        
        # 设置黑方棋子（顶部，行1和0）
        # 黑兵
        for col in range(8):
            self.board[1, col] = ChessPiece(Color.BLACK, PieceType.PAWN, (1, col))
        
        # 黑方主力棋子
        for col, piece_type in enumerate(piece_order):
            self.board[0, col] = ChessPiece(Color.BLACK, piece_type, (0, col))
    
    def step(self, action: Union[Tuple[Tuple[int, int], Tuple[int, int]], ChessMove]) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """执行一步棋"""
        # 处理不同的action格式
        if isinstance(action, tuple) and len(action) == 2:
            from_pos, to_pos = action
            move = self._create_move(from_pos, to_pos)
        elif isinstance(action, ChessMove):
            move = action
        else:
            return self.get_state(), -1, True, {'error': 'Invalid action format'}
        
        if move is None:
            return self.get_state(), -1, True, {'error': 'Invalid move'}
        
        # 验证移动是否合法
        if not self._is_legal_move(move):
            return self.get_state(), -1, True, {'error': 'Illegal move'}
        
        # 执行移动
        player_who_moved = self.current_player
        self._execute_move(move)
        
        # 检查游戏是否结束
        done = self.is_terminal()
        winner = self.get_winner()
        
        # 计算奖励
        if winner == player_who_moved:
            reward = 1.0
        elif done and winner is None:
            reward = 0.0  # 平局
        else:
            reward = 0.0
        
        info = {
            'move': move.to_dict(),
            'winner': winner,
            'check': self._is_in_check(Color.WHITE if self.current_player == 1 else Color.BLACK),
            'notation': str(move)
        }
        
        # 记录移动
        self.record_move(player_who_moved, move.to_dict(), info)
        
        # 如果游戏没有结束，切换玩家
        if not done:
            self.switch_player()
        
        return self.get_state(), reward, done, info
    
    def _create_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> Optional[ChessMove]:
        """从位置创建移动对象"""
        piece = self.board[from_pos[0], from_pos[1]]
        if piece is None:
            return None
        
        captured_piece = self.board[to_pos[0], to_pos[1]]
        
        # 检查是否是兵的升变
        promotion_piece = None
        if (piece.piece_type == PieceType.PAWN and 
            ((piece.color == Color.WHITE and to_pos[0] == 0) or 
             (piece.color == Color.BLACK and to_pos[0] == 7))):
            promotion_piece = PieceType.QUEEN  # 默认升变为后
        
        # 检查是否是王车易位
        is_castling = (piece.piece_type == PieceType.KING and 
                      abs(to_pos[1] - from_pos[1]) == 2)
        
        # 检查是否是吃过路兵
        is_en_passant = (piece.piece_type == PieceType.PAWN and 
                        to_pos == self.en_passant_target and
                        captured_piece is None)
        
        return ChessMove(from_pos, to_pos, piece, captured_piece, 
                        promotion_piece, is_castling, is_en_passant)
    
    def _execute_move(self, move: ChessMove):
        """执行移动"""
        # 移动棋子
        self.board[move.from_pos[0], move.from_pos[1]] = None
        self.board[move.to_pos[0], move.to_pos[1]] = move.piece
        move.piece.position = move.to_pos
        move.piece.has_moved = True
        
        # 处理吃子
        if move.captured_piece:
            self.captured_pieces[move.captured_piece.color].append(move.captured_piece)
        
        # 处理特殊移动
        if move.is_castling:
            self._execute_castling(move)
        elif move.is_en_passant:
            self._execute_en_passant(move)
        elif move.promotion_piece:
            self._execute_promotion(move)
        
        # 更新吃过路兵目标
        self._update_en_passant_target(move)
        
        # 更新王车易位权限
        self._update_castling_rights(move)
        
        # 更新50步规则计数器
        if move.piece.piece_type == PieceType.PAWN or move.captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        
        # 记录移动
        self.move_history.append(move)
        
        # 更新回合数
        if move.piece.color == Color.BLACK:
            self.fullmove_number += 1
    
    def _execute_castling(self, move: ChessMove):
        """执行王车易位"""
        king_row = move.from_pos[0]
        
        if move.to_pos[1] == 6:  # 王翼易位
            rook_from = (king_row, 7)
            rook_to = (king_row, 5)
        else:  # 后翼易位
            rook_from = (king_row, 0)
            rook_to = (king_row, 3)
        
        # 移动车
        rook = self.board[rook_from[0], rook_from[1]]
        self.board[rook_from[0], rook_from[1]] = None
        self.board[rook_to[0], rook_to[1]] = rook
        rook.position = rook_to
        rook.has_moved = True
    
    def _execute_en_passant(self, move: ChessMove):
        """执行吃过路兵"""
        # 移除被吃的兵
        captured_pawn_pos = (move.from_pos[0], move.to_pos[1])
        captured_pawn = self.board[captured_pawn_pos[0], captured_pawn_pos[1]]
        self.board[captured_pawn_pos[0], captured_pawn_pos[1]] = None
        self.captured_pieces[captured_pawn.color].append(captured_pawn)
    
    def _execute_promotion(self, move: ChessMove):
        """执行兵的升变"""
        self.board[move.to_pos[0], move.to_pos[1]] = ChessPiece(
            move.piece.color, move.promotion_piece, move.to_pos
        )
    
    def _update_en_passant_target(self, move: ChessMove):
        """更新吃过路兵目标"""
        if (move.piece.piece_type == PieceType.PAWN and 
            abs(move.to_pos[0] - move.from_pos[0]) == 2):
            # 兵前进两步，设置吃过路兵目标
            target_row = (move.from_pos[0] + move.to_pos[0]) // 2
            self.en_passant_target = (target_row, move.to_pos[1])
        else:
            self.en_passant_target = None
    
    def _update_castling_rights(self, move: ChessMove):
        """更新王车易位权限"""
        # 如果王移动，失去所有易位权限
        if move.piece.piece_type == PieceType.KING:
            color = move.piece.color
            self.castling_rights[color]['kingside'] = False
            self.castling_rights[color]['queenside'] = False
        
        # 如果车移动，失去对应的易位权限
        elif move.piece.piece_type == PieceType.ROOK:
            color = move.piece.color
            if move.from_pos == (0 if color == Color.BLACK else 7, 0):
                self.castling_rights[color]['queenside'] = False
            elif move.from_pos == (0 if color == Color.BLACK else 7, 7):
                self.castling_rights[color]['kingside'] = False
    
    def get_valid_actions(self, player: int = None) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """获取当前玩家的所有合法移动"""
        if player is None:
            player = self.current_player
        
        color = Color.WHITE if player == 1 else Color.BLACK
        moves = []
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row, col]
                if piece and piece.color == color:
                    # 传递当前实际位置给get_possible_moves
                    piece_moves = piece.get_possible_moves(self.board, (row, col))
                    for to_pos in piece_moves:
                        move = self._create_move((row, col), to_pos)
                        if move and self._is_legal_move(move):
                            moves.append(((row, col), to_pos))
        
        # 添加王车易位
        castling_moves = self._get_castling_moves(color)
        moves.extend(castling_moves)
        
        return moves
    
    def _get_castling_moves(self, color: Color) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """获取王车易位的合法移动"""
        moves = []
        
        if self._is_in_check(color):
            return moves  # 被将军时不能易位
        
        king_row = 0 if color == Color.BLACK else 7
        king_pos = (king_row, 4)
        
        # 检查王翼易位
        if (self.castling_rights[color]['kingside'] and
            self.board[king_row, 5] is None and
            self.board[king_row, 6] is None and
            not self._is_square_attacked((king_row, 5), color) and
            not self._is_square_attacked((king_row, 6), color)):
            moves.append((king_pos, (king_row, 6)))
        
        # 检查后翼易位
        if (self.castling_rights[color]['queenside'] and
            self.board[king_row, 1] is None and
            self.board[king_row, 2] is None and
            self.board[king_row, 3] is None and
            not self._is_square_attacked((king_row, 2), color) and
            not self._is_square_attacked((king_row, 3), color)):
            moves.append((king_pos, (king_row, 2)))
        
        return moves
    
    def _is_legal_move(self, move: ChessMove) -> bool:
        """检查移动是否合法（不能让自己的王处于被将军状态）"""
        # 临时执行移动
        original_board = copy.deepcopy(self.board)
        original_en_passant = self.en_passant_target
        
        # 执行移动
        self.board[move.from_pos[0], move.from_pos[1]] = None
        self.board[move.to_pos[0], move.to_pos[1]] = move.piece
        
        if move.is_en_passant:
            captured_pawn_pos = (move.from_pos[0], move.to_pos[1])
            self.board[captured_pawn_pos[0], captured_pawn_pos[1]] = None
        
        # 检查是否将军自己的王
        is_legal = not self._is_in_check(move.piece.color)
        
        # 恢复棋盘
        self.board = original_board
        self.en_passant_target = original_en_passant
        
        return is_legal
    
    def _is_in_check(self, color: Color) -> bool:
        """检查指定颜色的王是否被将军"""
        # 找到王的位置
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.board[row, col]
                if (piece and piece.piece_type == PieceType.KING and 
                    piece.color == color):
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        if king_pos is None:
            # 【重要修复】如果国王不存在，说明被吃掉了，这是严重错误
            # 在正常游戏中不应该发生，但如果发生了，我们认为这是极端的"被将军"状态
            return True
        
        return self._is_square_attacked(king_pos, color)

    def _king_exists(self, color: Color) -> bool:
        """检查指定颜色的国王是否还在棋盘上"""
        for row in range(8):
            for col in range(8):
                piece = self.board[row, col]
                if (piece and piece.piece_type == PieceType.KING and 
                    piece.color == color):
                    return True
        return False

    def _is_square_attacked(self, pos: Tuple[int, int], defending_color: Color) -> bool:
        """检查位置是否被对方攻击"""
        attacking_color = Color.BLACK if defending_color == Color.WHITE else Color.WHITE
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row, col]
                if piece and piece.color == attacking_color:
                    # 传递当前实际位置给get_possible_moves
                    possible_moves = piece.get_possible_moves(self.board, (row, col))
                    if pos in possible_moves:
                        return True
        
        return False
    
    def is_terminal(self) -> bool:
        """检查游戏是否结束"""
        color = Color.WHITE if self.current_player == 1 else Color.BLACK
        
        # 【重要修复】检查国王是否还在棋盘上
        if not self._king_exists(Color.WHITE) or not self._king_exists(Color.BLACK):
            return True  # 国王被吃掉，游戏立即结束
        
        # 检查是否有合法移动
        if not self.get_valid_actions():
            return True  # 将死或僵局
        
        # 50步规则
        if self.halfmove_clock >= 100:  # 50回合 = 100半回合
            return True
        
        # 三次重复（简化版）
        if self._is_threefold_repetition():
            return True
        
        # 最大移动数限制
        if self.move_count >= self.game_config.get('max_moves', 200):
            return True
        
        return False
    
    def _is_threefold_repetition(self) -> bool:
        """检查三次重复（简化版）"""
        if len(self.move_history) < 8:
            return False
        
        # 简化的重复检测：检查最近的位置是否重复3次
        current_state = self._get_position_hash()
        repetition_count = 1
        
        # 检查历史中的重复
        for i in range(len(self.move_history) - 4, -1, -4):  # 每4步检查一次
            if i < 0:
                break
            # 这里应该比较完整的游戏状态，为简化暂时跳过
            # repetition_count += 1
        
        return repetition_count >= 3
    
    def _get_position_hash(self) -> str:
        """获取当前位置的哈希值（用于重复检测）"""
        # 简化版，实际应该包括更多信息
        board_str = ""
        for row in range(8):
            for col in range(8):
                piece = self.board[row, col]
                if piece:
                    board_str += f"{piece.color.value}{piece.piece_type.value}"
                else:
                    board_str += "0"
        return board_str
    
    def get_winner(self) -> Optional[int]:
        """获取获胜者"""
        if not self.is_terminal():
            return None
        
        # 【重要修复】检查是否有国王被吃掉
        white_king_exists = self._king_exists(Color.WHITE)
        black_king_exists = self._king_exists(Color.BLACK)
        
        if not white_king_exists and not black_king_exists:
            return None  # 双方国王都被吃掉（不应该发生，但处理边界情况）
        elif not white_king_exists:
            return 2  # 白王被吃掉，黑方胜
        elif not black_king_exists:
            return 1  # 黑王被吃掉，白方胜
        
        # 正常的将死/僵局判定
        color = Color.WHITE if self.current_player == 1 else Color.BLACK
        
        # 检查是否被将军
        if self._is_in_check(color):
            # 将死
            return 2 if self.current_player == 1 else 1
        else:
            # 僵局或其他平局情况
            return None
    
    def get_state(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        # 创建简化的棋盘表示
        board_array = np.zeros((8, 8), dtype=int)
        for row in range(8):
            for col in range(8):
                piece = self.board[row, col]
                if piece:
                    # 编码：白方1-6，黑方7-12
                    base = 0 if piece.color == Color.WHITE else 6
                    board_array[row, col] = base + piece.piece_type.value
        
        return {
            'board': board_array,
            'board_objects': self.board,  # 完整的棋子对象（用于AI分析）
            'current_player': self.current_player,
            'game_state': self.game_state,
            'move_count': self.move_count,
            'move_history': [move.to_dict() for move in self.move_history],
            'captured_pieces': {
                'white': [p.piece_type.value for p in self.captured_pieces[Color.WHITE]],
                'black': [p.piece_type.value for p in self.captured_pieces[Color.BLACK]]
            },
            'castling_rights': self.castling_rights,
            'en_passant_target': self.en_passant_target,
            'halfmove_clock': self.halfmove_clock,
            'fullmove_number': self.fullmove_number,
            'in_check': {
                'white': self._is_in_check(Color.WHITE),
                'black': self._is_in_check(Color.BLACK)
            }
        }
    
    def render(self) -> str:
        """渲染棋盘的字符串表示"""
        board_str = "\n   a b c d e f g h\n"
        
        for row in range(8):
            board_str += f"{8-row}  "
            for col in range(8):
                piece = self.board[row, col]
                if piece:
                    board_str += str(piece) + " "
                else:
                    board_str += "· "
            board_str += f" {8-row}\n"
        
        board_str += "   a b c d e f g h\n"
        
        # 添加游戏信息
        current_color = "白方" if self.current_player == 1 else "黑方"
        board_str += f"\n当前玩家: {current_color}\n"
        board_str += f"回合数: {self.fullmove_number}\n"
        
        # 显示将军状态
        if self._is_in_check(Color.WHITE):
            board_str += "白王被将军!\n"
        if self._is_in_check(Color.BLACK):
            board_str += "黑王被将军!\n"
        
        return board_str
    
    def clone(self) -> 'ChessGame':
        """克隆游戏状态"""
        new_game = ChessGame()
        new_game.board = copy.deepcopy(self.board)
        new_game.current_player = self.current_player
        new_game.game_state = self.game_state
        new_game.move_count = self.move_count
        new_game.history = copy.deepcopy(self.history)
        new_game.captured_pieces = copy.deepcopy(self.captured_pieces)
        new_game.move_history = copy.deepcopy(self.move_history)
        new_game.en_passant_target = self.en_passant_target
        new_game.castling_rights = copy.deepcopy(self.castling_rights)
        new_game.halfmove_clock = self.halfmove_clock
        new_game.fullmove_number = self.fullmove_number
        return new_game
    
    def get_action_space(self) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """获取动作空间"""
        # 所有可能的移动（从任意位置到任意位置）
        actions = []
        for from_row in range(8):
            for from_col in range(8):
                for to_row in range(8):
                    for to_col in range(8):
                        if (from_row, from_col) != (to_row, to_col):
                            actions.append(((from_row, from_col), (to_row, to_col)))
        return actions
    
    def get_observation_space(self) -> Dict[str, Any]:
        """获取观察空间"""
        return {
            'board': (8, 8),
            'current_player': 1,
            'move_history': [],
            'game_info': {}
        }
    
    def get_fen(self) -> str:
        """获取FEN（Forsyth-Edwards Notation）字符串"""
        # 棋盘部分
        fen_pieces = {
            (Color.WHITE, PieceType.KING): 'K',
            (Color.WHITE, PieceType.QUEEN): 'Q',
            (Color.WHITE, PieceType.ROOK): 'R',
            (Color.WHITE, PieceType.BISHOP): 'B',
            (Color.WHITE, PieceType.KNIGHT): 'N',
            (Color.WHITE, PieceType.PAWN): 'P',
            (Color.BLACK, PieceType.KING): 'k',
            (Color.BLACK, PieceType.QUEEN): 'q',
            (Color.BLACK, PieceType.ROOK): 'r',
            (Color.BLACK, PieceType.BISHOP): 'b',
            (Color.BLACK, PieceType.KNIGHT): 'n',
            (Color.BLACK, PieceType.PAWN): 'p',
        }
        
        fen_board = ""
        for row in range(8):
            empty_count = 0
            for col in range(8):
                piece = self.board[row, col]
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_board += str(empty_count)
                        empty_count = 0
                    fen_board += fen_pieces[(piece.color, piece.piece_type)]
            
            if empty_count > 0:
                fen_board += str(empty_count)
            
            if row < 7:
                fen_board += "/"
        
        # 当前玩家
        active_color = "w" if self.current_player == 1 else "b"
        
        # 王车易位权限
        castling = ""
        if self.castling_rights[Color.WHITE]['kingside']:
            castling += "K"
        if self.castling_rights[Color.WHITE]['queenside']:
            castling += "Q"
        if self.castling_rights[Color.BLACK]['kingside']:
            castling += "k"
        if self.castling_rights[Color.BLACK]['queenside']:
            castling += "q"
        if not castling:
            castling = "-"
        
        # 吃过路兵目标
        en_passant = "-"
        if self.en_passant_target:
            cols = "abcdefgh"
            rows = "87654321"
            en_passant = cols[self.en_passant_target[1]] + rows[self.en_passant_target[0]]
        
        return f"{fen_board} {active_color} {castling} {en_passant} {self.halfmove_clock} {self.fullmove_number}"
    
    def get_natural_language_state(self) -> str:
        """获取适合LLM理解的自然语言游戏状态描述"""
        state = self.get_state()
        
        description = f"""
当前国际象棋局面：

回合信息：
- 当前轮到：{'白方' if self.current_player == 1 else '黑方'}
- 总回合数：{self.fullmove_number}
- 50步计数：{self.halfmove_clock}/100

棋盘状态：
{self.render()}

特殊状态：
- 白王被将军：{'是' if state['in_check']['white'] else '否'}
- 黑王被将军：{'是' if state['in_check']['black'] else '否'}
- 可王车易位：白方王翼{'可' if self.castling_rights[Color.WHITE]['kingside'] else '不可'}，白方后翼{'可' if self.castling_rights[Color.WHITE]['queenside'] else '不可'}
- 可王车易位：黑方王翼{'可' if self.castling_rights[Color.BLACK]['kingside'] else '不可'}，黑方后翼{'可' if self.castling_rights[Color.BLACK]['queenside'] else '不可'}
- 吃过路兵目标：{self.en_passant_target if self.en_passant_target else '无'}

被吃棋子：
- 白方损失：{', '.join([str(PieceType(p)) for p in state['captured_pieces']['white']]) if state['captured_pieces']['white'] else '无'}
- 黑方损失：{', '.join([str(PieceType(p)) for p in state['captured_pieces']['black']]) if state['captured_pieces']['black'] else '无'}

最近3步棋：
{self._get_recent_moves_description()}
"""
        return description
    
    def _get_recent_moves_description(self) -> str:
        """获取最近几步棋的描述"""
        if not self.move_history:
            return "暂无移动记录"
        
        recent_moves = self.move_history[-6:]  # 最近6步
        description = ""
        
        for i, move in enumerate(recent_moves):
            move_number = self.fullmove_number - (len(recent_moves) - i - 1) // 2
            color = "白方" if move.piece.color == Color.WHITE else "黑方"
            piece_name = self._get_piece_chinese_name(move.piece.piece_type)
            
            description += f"{move_number}. {color} {piece_name} {move}\n"
        
        return description
    
    def _get_piece_chinese_name(self, piece_type: PieceType) -> str:
        """获取棋子的中文名称"""
        names = {
            PieceType.PAWN: "兵",
            PieceType.ROOK: "车",
            PieceType.KNIGHT: "马",
            PieceType.BISHOP: "象",
            PieceType.QUEEN: "后",
            PieceType.KING: "王"
        }
        return names.get(piece_type, "未知") 