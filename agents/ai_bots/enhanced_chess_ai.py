"""
增强版国际象棋AI
集成Stockfish引擎，提供专业级别的国际象棋对弈能力
"""

import time
import chess
import chess.engine
import chess.polyglot
from typing import Dict, List, Tuple, Any, Optional
from agents.base_agent import BaseAgent
from games.chess.chess_game import ChessMove


class EnhancedChessAI(BaseAgent):
    """
    增强版国际象棋AI
    
    核心特性：
    1. 集成Stockfish引擎 - 世界顶级棋力
    2. 多难度等级 - 从新手到大师
    3. 开局库支持 - 标准开局变化
    4. 深度分析 - 提供详细的局面评估
    5. 实时建议 - 为人类玩家提供专业建议
    """
    
    def __init__(self, name: str = "Enhanced AI", player_id: int = 2, 
                 stockfish_path: str = "stockfish", difficulty: str = "medium"):
        super().__init__(name, player_id)
        self.stockfish_path = stockfish_path
        self.difficulty = difficulty
        self.engine = None
        self.board = chess.Board()
        
        # 难度设置
        self.difficulty_settings = {
            "beginner": {"depth": 1, "time": 0.1, "skill_level": 0},
            "easy": {"depth": 3, "time": 0.5, "skill_level": 5},
            "medium": {"depth": 5, "time": 1.0, "skill_level": 10},
            "hard": {"depth": 8, "time": 2.0, "skill_level": 15},
            "expert": {"depth": 12, "time": 5.0, "skill_level": 20}
        }
        
        # 移动历史和分析
        self.move_history = []
        self.analysis_cache = {}
        
        # 初始化引擎
        self._initialize_engine()
    
    def _initialize_engine(self):
        """初始化Stockfish引擎"""
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
            
            # 设置引擎参数
            settings = self.difficulty_settings.get(self.difficulty, self.difficulty_settings["medium"])
            if hasattr(self.engine, 'configure'):
                self.engine.configure({"Skill Level": settings["skill_level"]})
            
            print(f"✅ Stockfish引擎初始化成功 - 难度: {self.difficulty}")
            
        except Exception as e:
            print(f"❌ Stockfish引擎初始化失败: {e}")
            print("请确保已安装Stockfish并正确配置路径")
            print("下载地址: https://stockfishchess.org/download/")
            self.engine = None
    
    def get_action(self, observation: Any, env: Any) -> Any:
        """获取AI的最佳移动"""
        if not self.engine:
            return self._fallback_move(env)
        
        start_time = time.time()
        
        try:
            # 同步棋盘状态
            self._sync_board_state(env)
            
            # 检查开局库
            opening_move = self._get_opening_move()
            if opening_move:
                move = self._convert_to_env_format(opening_move, env)
                if move:
                    return move
            
            # 使用Stockfish分析
            best_move = self._get_stockfish_move()
            if best_move:
                move = self._convert_to_env_format(best_move, env)
                if move:
                    # 分析这步棋
                    analysis = self._analyze_position(best_move)
                    self.move_history.append({
                        'move': best_move,
                        'analysis': analysis,
                        'thinking_time': time.time() - start_time
                    })
                    return move
            
        except Exception as e:
            print(f"Stockfish分析出错: {e}")
        
        # 回退方案
        return self._fallback_move(env)
    
    def _sync_board_state(self, env: Any):
        """同步棋盘状态到python-chess"""
        # 这里需要根据你的环境接口来实现
        # 将env的棋盘状态转换为python-chess的Board对象
        pass
    
    def _get_opening_move(self) -> Optional[chess.Move]:
        """从开局库获取移动"""
        try:
            # 这里可以集成开局库
            # 例如使用 chess.polyglot 读取开局书
            return None
        except:
            return None
    
    def _get_stockfish_move(self) -> Optional[chess.Move]:
        """使用Stockfish获取最佳移动"""
        settings = self.difficulty_settings.get(self.difficulty, self.difficulty_settings["medium"])
        
        try:
            # 设置思考时间限制
            limit = chess.engine.Limit(
                time=settings["time"],
                depth=settings["depth"]
            )
            
            # 获取最佳移动
            result = self.engine.play(self.board, limit)
            return result.move
        except Exception as e:
            print(f"Stockfish移动获取失败: {e}")
            return None
    
    def _analyze_position(self, move: chess.Move) -> Dict[str, Any]:
        """分析当前位置"""
        try:
            # 获取评估分数
            info = self.engine.analyse(self.board, chess.engine.Limit(time=0.1))
            score = info["score"].relative
            
            # 生成分析报告
            analysis = {
                'score': score.score() if score.score() else 0,
                'mate_in': score.mate() if score.mate() else None,
                'best_line': info.get("pv", [])[:5],  # 前5步最佳变化
                'description': self._describe_move(move)
            }
            
            return analysis
        except:
            return {'score': 0, 'description': '分析不可用'}
    
    def _describe_move(self, move: chess.Move) -> str:
        """描述移动的含义"""
        descriptions = []
        
        # 基本移动描述
        piece = self.board.piece_at(move.from_square)
        if piece:
            piece_name = self._get_piece_name(piece.piece_type)
            descriptions.append(f"{piece_name}移动")
        
        # 特殊移动
        if self.board.is_capture(move):
            descriptions.append("吃子")
        if self.board.is_check():
            descriptions.append("将军")
        if move.promotion:
            descriptions.append("升变")
        if self.board.is_castling(move):
            descriptions.append("易位")
        
        return "，".join(descriptions) if descriptions else "普通移动"
    
    def _get_piece_name(self, piece_type: int) -> str:
        """获取棋子中文名称"""
        names = {
            chess.PAWN: "兵",
            chess.ROOK: "车",
            chess.KNIGHT: "马",
            chess.BISHOP: "象",
            chess.QUEEN: "后",
            chess.KING: "王"
        }
        return names.get(piece_type, "棋子")
    
    def _convert_to_env_format(self, chess_move: chess.Move, env: Any) -> Any:
        """将chess.Move转换为环境格式"""
        # 这里需要根据你的环境接口来实现转换
        # 例如：从 chess.Move 转换为 ((from_row, from_col), (to_row, to_col))
        try:
            from_square = chess_move.from_square
            to_square = chess_move.to_square
            
            # 转换坐标系
            from_row, from_col = divmod(from_square, 8)
            to_row, to_col = divmod(to_square, 8)
            
            return ((from_row, from_col), (to_row, to_col))
        except:
            return None
    
    def _fallback_move(self, env: Any) -> Any:
        """回退移动策略"""
        valid_moves = env.get_valid_actions()
        if valid_moves:
            return valid_moves[0]  # 返回第一个有效移动
        return None
    
    def get_position_analysis(self) -> Dict[str, Any]:
        """获取当前位置的深度分析"""
        if not self.engine:
            return {"error": "引擎未初始化"}
        
        try:
            # 深度分析
            info = self.engine.analyse(self.board, chess.engine.Limit(time=2.0))
            
            return {
                'evaluation': info["score"].relative.score() if info["score"].relative.score() else 0,
                'best_line': [str(move) for move in info.get("pv", [])[:8]],
                'depth': info.get("depth", 0),
                'nodes': info.get("nodes", 0),
                'time': info.get("time", 0)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_move_suggestions(self, count: int = 3) -> List[Dict[str, Any]]:
        """获取多个候选移动"""
        if not self.engine:
            return []
        
        suggestions = []
        try:
            # 使用MultiPV获取多个候选移动
            info = self.engine.analyse(
                self.board, 
                chess.engine.Limit(time=1.0),
                multipv=count
            )
            
            for i, analysis in enumerate(info):
                if analysis.get("pv"):
                    move = analysis["pv"][0]
                    suggestions.append({
                        'rank': i + 1,
                        'move': str(move),
                        'score': analysis["score"].relative.score() if analysis["score"].relative.score() else 0,
                        'description': self._describe_move(move)
                    })
            
        except Exception as e:
            print(f"获取候选移动失败: {e}")
        
        return suggestions
    
    def set_difficulty(self, difficulty: str):
        """设置难度等级"""
        if difficulty in self.difficulty_settings:
            self.difficulty = difficulty
            if self.engine:
                settings = self.difficulty_settings[difficulty]
                try:
                    self.engine.configure({"Skill Level": settings["skill_level"]})
                    print(f"难度已设置为: {difficulty}")
                except Exception as e:
                    print(f"难度设置失败: {e}")
    
    def get_game_review(self) -> Dict[str, Any]:
        """获取对局复盘"""
        if not self.move_history:
            return {"error": "没有移动历史"}
        
        total_moves = len(self.move_history)
        avg_time = sum(move['thinking_time'] for move in self.move_history) / total_moves
        
        return {
            'total_moves': total_moves,
            'average_thinking_time': avg_time,
            'move_history': self.move_history[-10:],  # 最近10步
            'performance': "基于Stockfish引擎的专业级对弈"
        }
    
    def __del__(self):
        """清理资源"""
        if self.engine:
            try:
                self.engine.quit()
            except:
                pass 