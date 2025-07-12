"""
Stockfish国际象棋AI
基于世界顶级Stockfish引擎的专业级国际象棋AI
"""

import time
import subprocess
import tempfile
import os
from typing import Dict, List, Tuple, Any, Optional, Union
from agents.base_agent import BaseAgent
from games.chess.chess_pieces import ChessPiece, Color, PieceType
from games.chess.chess_game import ChessMove

try:
    import chess
    import chess.engine
    import chess.pgn
    HAS_PYTHON_CHESS = True
except ImportError:
    HAS_PYTHON_CHESS = False

try:
    from stockfish import Stockfish
    HAS_STOCKFISH = True
except ImportError:
    HAS_STOCKFISH = False


class StockfishChessAI(BaseAgent):
    """
    基于Stockfish的专业国际象棋AI
    
    核心特性：
    1. 世界顶级引擎：Stockfish的强大棋力
    2. 多难度等级：从新手到专家
    3. 实时评估：每步棋的详细分析
    4. 开局库：标准开局变化
    5. 残局精确：完美的残局技巧
    """
    
    def __init__(self, 
                 name: str = "Stockfish", 
                 player_id: int = 2, 
                 difficulty: int = 8,
                 stockfish_path: str = "stockfish",
                 time_limit: float = 1.0):
        super().__init__(name, player_id)
        
        self.difficulty = difficulty  # 0-20，0最弱，20最强
        self.stockfish_path = stockfish_path
        self.time_limit = time_limit
        self.stockfish = None
        self.board = None
        self.move_evaluations = []
        self.game_analysis = {}
        
        # 难度对应设置
        self.difficulty_settings = {
            0: {"depth": 1, "time": 0.1, "skill": 0},    # 新手
            1: {"depth": 2, "time": 0.2, "skill": 2},    # 入门
            2: {"depth": 3, "time": 0.3, "skill": 4},    # 初级
            3: {"depth": 4, "time": 0.5, "skill": 6},    # 中级
            4: {"depth": 5, "time": 0.7, "skill": 8},    # 中上
            5: {"depth": 6, "time": 1.0, "skill": 10},   # 高级
            6: {"depth": 7, "time": 1.5, "skill": 12},   # 专家
            7: {"depth": 8, "time": 2.0, "skill": 14},   # 大师
            8: {"depth": 10, "time": 3.0, "skill": 16},  # 国际大师
            9: {"depth": 12, "time": 5.0, "skill": 18},  # 特级大师
            10: {"depth": 15, "time": 10.0, "skill": 20} # 最强
        }
        
        # 初始化引擎
        self._init_engine()
        
    def _init_engine(self) -> bool:
        """初始化Stockfish引擎"""
        if not HAS_STOCKFISH:
            print("⚠️  stockfish库未安装，使用基础AI模式")
            return False
        
        if not HAS_PYTHON_CHESS:
            print("⚠️  python-chess库未安装，使用基础AI模式")
            return False
        
        try:
            # 尝试初始化Stockfish
            self.stockfish = Stockfish(path=self.stockfish_path)
            
            # 设置引擎参数
            settings = self.difficulty_settings.get(self.difficulty, self.difficulty_settings[8])
            self.stockfish.set_depth(settings["depth"])
            
            # 设置技能等级（0-20）
            self.stockfish.set_elo_rating(1000 + settings["skill"] * 100)
            
            # 初始化棋盘
            self.board = chess.Board()
            self.stockfish.set_position([])
            
            print(f"✅ Stockfish引擎初始化成功 (难度: {self.difficulty})")
            return True
            
        except Exception as e:
            print(f"❌ Stockfish初始化失败: {e}")
            print("使用基础AI模式")
            return False
    
    def get_action(self, observation: Any, env: Any) -> Any:
        """获取AI的下一步行动"""
        start_time = time.time()
        
        # 获取所有可能的移动
        valid_moves = env.get_valid_actions()
        if not valid_moves:
            return None
        
        # 如果Stockfish不可用，使用基础AI
        if not self.stockfish:
            return self._get_basic_move(valid_moves, env)
        
        try:
            # 同步棋盘状态
            self._sync_board_state(env)
            
            # 获取Stockfish的最佳移动
            best_move = self.stockfish.get_best_move()
            
            if best_move:
                # 转换为项目格式
                move = self._convert_stockfish_move(best_move, env)
                if move in valid_moves:
                    # 评价这步棋
                    evaluation = self._evaluate_move(move, env, best_move)
                    evaluation['thinking_time'] = time.time() - start_time
                    self.move_evaluations.append(evaluation)
                    
                    # 更新统计
                    self.total_moves += 1
                    self.total_time += time.time() - start_time
                    
                    return move
            
        except Exception as e:
            print(f"Stockfish错误: {e}")
        
        # 回退到基础AI
        return self._get_basic_move(valid_moves, env)
    
    def _sync_board_state(self, env: Any):
        """同步棋盘状态到Stockfish"""
        try:
            # 获取游戏历史记录
            moves = []
            for move_record in env.game.history:
                if 'action' in move_record and move_record['action']:
                    uci_move = self._convert_to_uci(move_record['action'])
                    if uci_move:
                        moves.append(uci_move)
            
            # 设置位置
            self.stockfish.set_position(moves)
            
        except Exception as e:
            print(f"同步棋盘状态错误: {e}")
    
    def _convert_to_uci(self, move: Tuple[Tuple[int, int], Tuple[int, int]]) -> Optional[str]:
        """转换移动为UCI格式"""
        try:
            from_pos, to_pos = move
            
            # 转换坐标为chess格式
            from_square = chess.square(from_pos[1], 7 - from_pos[0])
            to_square = chess.square(to_pos[1], 7 - to_pos[0])
            
            return chess.square_name(from_square) + chess.square_name(to_square)
            
        except Exception as e:
            print(f"UCI转换错误: {e}")
            return None
    
    def _convert_stockfish_move(self, stockfish_move: str, env: Any) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """转换Stockfish移动为项目格式"""
        try:
            # 解析UCI格式移动
            from_square = chess.parse_square(stockfish_move[:2])
            to_square = chess.parse_square(stockfish_move[2:4])
            
            # 转换为项目坐标
            from_pos = (7 - chess.square_rank(from_square), chess.square_file(from_square))
            to_pos = (7 - chess.square_rank(to_square), chess.square_file(to_square))
            
            return (from_pos, to_pos)
            
        except Exception as e:
            print(f"移动转换错误: {e}")
            return None
    
    def _get_basic_move(self, valid_moves: List[Tuple[Tuple[int, int], Tuple[int, int]]], env: Any) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """基础AI移动（当Stockfish不可用时）"""
        best_move = None
        best_score = float('-inf')
        
        for move in valid_moves:
            score = self._evaluate_basic_move(move, env)
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move or valid_moves[0]
    
    def _evaluate_basic_move(self, move: Tuple[Tuple[int, int], Tuple[int, int]], env: Any) -> float:
        """基础移动评估"""
        from_pos, to_pos = move
        board = env.game.board
        
        moving_piece = board[from_pos[0], from_pos[1]]
        target_piece = board[to_pos[0], to_pos[1]]
        
        score = 0
        
        # 棋子价值
        piece_values = {
            PieceType.PAWN: 1,
            PieceType.KNIGHT: 3,
            PieceType.BISHOP: 3,
            PieceType.ROOK: 5,
            PieceType.QUEEN: 9,
            PieceType.KING: 0
        }
        
        # 吃子奖励
        if target_piece:
            score += piece_values.get(target_piece.piece_type, 0) * 10
        
        # 中心控制
        center_bonus = [[0, 0, 0, 0, 0, 0, 0, 0],
                       [0, 1, 1, 1, 1, 1, 1, 0],
                       [0, 1, 2, 2, 2, 2, 1, 0],
                       [0, 1, 2, 3, 3, 2, 1, 0],
                       [0, 1, 2, 3, 3, 2, 1, 0],
                       [0, 1, 2, 2, 2, 2, 1, 0],
                       [0, 1, 1, 1, 1, 1, 1, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0]]
        
        score += center_bonus[to_pos[0]][to_pos[1]]
        
        return score
    
    def _evaluate_move(self, move: Tuple[Tuple[int, int], Tuple[int, int]], env: Any, stockfish_move: str) -> Dict[str, Any]:
        """详细评价移动"""
        evaluation = {
            'move': move,
            'stockfish_move': stockfish_move,
            'score': 0,
            'evaluation': 0,
            'analysis': '',
            'best_line': []
        }
        
        if self.stockfish:
            try:
                # 获取局面评估
                eval_result = self.stockfish.get_evaluation()
                if eval_result:
                    evaluation['evaluation'] = eval_result.get('value', 0)
                    evaluation['score'] = self._convert_evaluation_to_score(eval_result)
                
                # 获取最佳变化
                top_moves = self.stockfish.get_top_moves(3)
                if top_moves:
                    evaluation['best_line'] = [move.get('Move', '') for move in top_moves]
                
                # 分析文本
                evaluation['analysis'] = self._generate_analysis(move, env, eval_result)
                
            except Exception as e:
                evaluation['analysis'] = f"分析错误: {e}"
        
        return evaluation
    
    def _convert_evaluation_to_score(self, eval_result: Dict[str, Any]) -> float:
        """转换引擎评估为分数"""
        if eval_result.get('type') == 'mate':
            # 将军得分
            mate_in = eval_result.get('value', 0)
            return 1000 if mate_in > 0 else -1000
        else:
            # centipawn评估转换为分数
            cp = eval_result.get('value', 0)
            return max(0, min(10, 5 + cp / 100))  # 转换为0-10分
    
    def _generate_analysis(self, move: Tuple[Tuple[int, int], Tuple[int, int]], env: Any, eval_result: Dict[str, Any]) -> str:
        """生成移动分析"""
        analysis_parts = []
        
        from_pos, to_pos = move
        board = env.game.board
        
        # 基本移动描述
        moving_piece = board[from_pos[0], from_pos[1]]
        if moving_piece:
            piece_name = self._get_piece_name(moving_piece.piece_type)
            analysis_parts.append(f"{piece_name}移动到{self._pos_to_notation(to_pos)}")
        
        # 评估描述
        if eval_result:
            if eval_result.get('type') == 'mate':
                mate_in = eval_result.get('value', 0)
                if mate_in > 0:
                    analysis_parts.append(f"将军！{mate_in}步内获胜")
                else:
                    analysis_parts.append(f"被将军！{abs(mate_in)}步内失败")
            else:
                cp = eval_result.get('value', 0)
                if cp > 100:
                    analysis_parts.append("优势明显")
                elif cp > 50:
                    analysis_parts.append("略有优势")
                elif cp > -50:
                    analysis_parts.append("势均力敌")
                elif cp > -100:
                    analysis_parts.append("略有劣势")
                else:
                    analysis_parts.append("劣势明显")
        
        return "，".join(analysis_parts)
    
    def _get_piece_name(self, piece_type: PieceType) -> str:
        """获取棋子中文名称"""
        names = {
            PieceType.PAWN: "兵",
            PieceType.KNIGHT: "马",
            PieceType.BISHOP: "象",
            PieceType.ROOK: "车",
            PieceType.QUEEN: "后",
            PieceType.KING: "王"
        }
        return names.get(piece_type, "棋子")
    
    def _pos_to_notation(self, pos: Tuple[int, int]) -> str:
        """位置转换为标记"""
        return f"{chr(ord('a') + pos[1])}{8 - pos[0]}"
    
    def get_real_time_suggestion(self, env: Any) -> str:
        """获取实时建议"""
        if not self.stockfish:
            return "Stockfish不可用"
        
        try:
            self._sync_board_state(env)
            
            # 获取最佳移动
            best_move = self.stockfish.get_best_move()
            if best_move:
                move_analysis = f"建议移动: {best_move}"
                
                # 获取评估
                eval_result = self.stockfish.get_evaluation()
                if eval_result:
                    if eval_result.get('type') == 'mate':
                        mate_in = eval_result.get('value', 0)
                        move_analysis += f"（将军{mate_in}步内获胜）"
                    else:
                        cp = eval_result.get('value', 0)
                        move_analysis += f"（评估: {cp/100:.1f}）"
                
                return move_analysis
        
        except Exception as e:
            return f"分析错误: {e}"
        
        return "无法获取建议"
    
    def get_game_review(self, game_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """获取游戏复盘"""
        review = {
            'total_moves': len(self.move_evaluations),
            'average_score': 0,
            'best_moves': [],
            'worst_moves': [],
            'accuracy': 0,
            'engine_level': f"难度 {self.difficulty}/10",
            'suggestions': []
        }
        
        if self.move_evaluations:
            scores = [eval.get('score', 0) for eval in self.move_evaluations]
            review['average_score'] = sum(scores) / len(scores)
            
            # 找出最佳和最差移动
            sorted_moves = sorted(self.move_evaluations, key=lambda x: x.get('score', 0))
            review['worst_moves'] = sorted_moves[:3]
            review['best_moves'] = sorted_moves[-3:]
            
            # 计算准确率
            good_moves = sum(1 for score in scores if score >= 6)
            review['accuracy'] = (good_moves / len(scores)) * 100
            
            # 建议
            if review['accuracy'] < 50:
                review['suggestions'].append("建议多练习基本战术")
            elif review['accuracy'] < 75:
                review['suggestions'].append("注意计算深度")
            else:
                review['suggestions'].append("表现不错，继续保持")
        
        return review
    
    def set_difficulty(self, difficulty: int):
        """设置难度等级"""
        self.difficulty = max(0, min(10, difficulty))
        if self.stockfish:
            settings = self.difficulty_settings.get(self.difficulty, self.difficulty_settings[8])
            self.stockfish.set_depth(settings["depth"])
            self.stockfish.set_elo_rating(1000 + settings["skill"] * 100)
    
    def get_engine_info(self) -> Dict[str, Any]:
        """获取引擎信息"""
        return {
            'name': 'Stockfish',
            'available': self.stockfish is not None,
            'difficulty': self.difficulty,
            'settings': self.difficulty_settings.get(self.difficulty, {}),
            'python_chess': HAS_PYTHON_CHESS,
            'stockfish_lib': HAS_STOCKFISH
        }
    
    def get_last_move_evaluation(self) -> Optional[Dict[str, Any]]:
        """获取最后一步棋的评价"""
        if self.move_evaluations:
            return self.move_evaluations[-1]
        return None
    
    def reset_analysis(self):
        """重置分析数据"""
        self.move_evaluations = []
        self.game_analysis = {}
        if self.stockfish:
            try:
                self.stockfish.set_position([])
                self.board = chess.Board()
            except Exception as e:
                print(f"重置引擎状态错误: {e}") 