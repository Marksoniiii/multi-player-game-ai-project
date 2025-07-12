#!/usr/bin/env python3
"""
LLM Chess Coach - 国际象棋AI教练
专门提供提示、实时评价和赛后复盘功能，不参与对战
"""

import random
import time
from typing import Dict, List, Tuple, Any, Optional
from agents.base_agent import BaseAgent
from games.chess.chess_pieces import Color, PieceType

class LLMChessCoach(BaseAgent):
    """LLM国际象棋教练 - 提供指导而非对战"""
    
    def __init__(self, name: str = "LLM教练", **kwargs):
        super().__init__(name, **kwargs)
        self.coach_mode = True  # 教练模式标记
        self.difficulty = kwargs.get('difficulty', 'medium')
        self.game_history = []  # 游戏历史记录
        self.move_evaluations = []  # 移动评价记录
        
        # 教练评价模板
        self.evaluation_templates = {
            'excellent': [
                "绝佳的移动！这步棋展现了深度的战术理解。",
                "完美的选择！这一步为您获得了显著的优势。",
                "精彩的战术眼光！这步棋解决了多个问题。"
            ],
            'good': [
                "不错的移动！这步棋符合开局/中局的基本原理。",
                "合理的选择！这一步保持了局面的平衡。",
                "正确的方向！这步棋改善了您的棋子协调性。"
            ],
            'average': [
                "还算可以的移动，但可能有更好的选择。",
                "这步棋没有明显的错误，但缺乏主动性。",
                "中规中矩的移动，建议考虑更积极的方案。"
            ],
            'poor': [
                "这步棋有些问题，请注意对方的威胁。",
                "建议重新考虑！这一步可能让您失去优势。",
                "这个移动有风险，要小心对方的反击。"
            ],
            'blunder': [
                "这是一个严重的错误！这步棋损失了重要的棋子或优势。",
                "危险的移动！这一步让对方获得了决定性的优势。",
                "请立即重新审视局面！这步棋可能导致失败。"
            ]
        }
    
    def get_action(self, observation: Dict[str, Any], env) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """教练模式下不提供对战行动，仅用于兼容接口"""
        return None
    
    def provide_hint(self, observation: Dict[str, Any], env) -> Dict[str, Any]:
        """提供移动提示"""
        try:
            # 获取当前所有合法移动
            valid_moves = env.get_valid_actions()
            if not valid_moves:
                return {"hint": "没有可用的移动", "analysis": "游戏可能已结束"}
            
            # 简化版提示逻辑（实际应该调用LLM）
            best_move = self._analyze_best_move(observation, valid_moves, env)
            hint_text = self._generate_hint_text(best_move, observation, env)
            
            return {
                "suggested_move": best_move,
                "hint": hint_text,
                "analysis": self._analyze_position(observation, env),
                "alternatives": self._get_alternative_moves(valid_moves, best_move)
            }
        except Exception as e:
            return {"hint": f"提示生成失败: {e}", "analysis": "请检查游戏状态"}
    
    def evaluate_move(self, move: Tuple[Tuple[int, int], Tuple[int, int]], 
                     before_state: Dict[str, Any], after_state: Dict[str, Any]) -> Dict[str, Any]:
        """评价玩家的移动"""
        try:
            # 计算移动评分
            score = self._calculate_move_score(move, before_state, after_state)
            
            # 生成评价文本
            evaluation_level = self._get_evaluation_level(score)
            evaluation_text = random.choice(self.evaluation_templates[evaluation_level])
            
            # 记录评价
            move_eval = {
                "move": move,
                "score": score,
                "level": evaluation_level,
                "evaluation": evaluation_text,
                "detailed_analysis": self._generate_detailed_analysis(move, before_state, after_state),
                "timestamp": time.time()
            }
            
            self.move_evaluations.append(move_eval)
            return move_eval
            
        except Exception as e:
            return {
                "move": move,
                "score": 0,
                "level": "unknown",
                "evaluation": f"评价失败: {e}",
                "detailed_analysis": "",
                "timestamp": time.time()
            }
    
    def provide_game_review(self, game_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """提供游戏复盘分析"""
        try:
            self.game_history = game_history
            
            review = {
                "overall_performance": self._analyze_overall_performance(),
                "key_moments": self._identify_key_moments(),
                "strengths": self._identify_strengths(),
                "weaknesses": self._identify_weaknesses(),
                "recommendations": self._generate_recommendations(),
                "score_trend": self._analyze_score_trend(),
                "opening_analysis": self._analyze_opening(),
                "endgame_analysis": self._analyze_endgame() if len(game_history) > 20 else None
            }
            
            return review
            
        except Exception as e:
            return {
                "overall_performance": f"复盘分析失败: {e}",
                "key_moments": [],
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
                "score_trend": [],
                "opening_analysis": "",
                "endgame_analysis": None
            }
    
    def _analyze_best_move(self, observation: Dict[str, Any], valid_moves: List, env) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """分析最佳移动（简化版）"""
        if not valid_moves:
            return None
        
        # 简化的评估逻辑（实际应该使用LLM或更复杂的算法）
        scored_moves = []
        
        for move in valid_moves:
            try:
                # 基本评分逻辑
                score = self._simple_move_evaluation(move, observation, env)
                scored_moves.append((move, score))
            except:
                scored_moves.append((move, 0))
        
        # 返回得分最高的移动
        if scored_moves:
            scored_moves.sort(key=lambda x: x[1], reverse=True)
            return scored_moves[0][0]
        
        return random.choice(valid_moves)
    
    def _simple_move_evaluation(self, move: Tuple[Tuple[int, int], Tuple[int, int]], 
                               observation: Dict[str, Any], env) -> float:
        """简化的移动评估"""
        score = 0.0
        from_pos, to_pos = move
        
        # 检查是否能吃子
        if 'board_objects' in observation:
            board = observation['board_objects']
            target_piece = board[to_pos[0]][to_pos[1]]
            if target_piece is not None:
                # 根据吃掉的棋子类型给分
                piece_values = {
                    PieceType.PAWN: 1,
                    PieceType.KNIGHT: 3,
                    PieceType.BISHOP: 3,
                    PieceType.ROOK: 5,
                    PieceType.QUEEN: 9,
                    PieceType.KING: 100
                }
                score += piece_values.get(target_piece.piece_type, 0)
        
        # 中心控制奖励
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        if to_pos in center_squares:
            score += 0.5
        
        # 随机因子
        score += random.uniform(-0.2, 0.2)
        
        return score
    
    def _generate_hint_text(self, move: Optional[Tuple[Tuple[int, int], Tuple[int, int]]], 
                           observation: Dict[str, Any], env) -> str:
        """生成提示文本"""
        if move is None:
            return "没有找到合适的移动建议"
        
        from_pos, to_pos = move
        
        # 转换坐标为棋盘记号
        cols = "abcdefgh"
        rows = "87654321"
        
        from_square = cols[from_pos[1]] + rows[from_pos[0]]
        to_square = cols[to_pos[1]] + rows[to_pos[0]]
        
        # 生成基本提示
        hint = f"建议移动: {from_square} -> {to_square}"
        
        # 添加战术分析
        if 'board_objects' in observation:
            board = observation['board_objects']
            moving_piece = board[from_pos[0]][from_pos[1]]
            target_piece = board[to_pos[0]][to_pos[1]]
            
            if target_piece is not None:
                hint += f"\n这步棋可以吃掉对方的{self._get_piece_name(target_piece.piece_type)}"
            
            if moving_piece:
                hint += f"\n移动{self._get_piece_name(moving_piece.piece_type)}到更好的位置"
        
        return hint
    
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
    
    def _analyze_position(self, observation: Dict[str, Any], env) -> str:
        """分析当前局面"""
        analysis = []
        
        # 基本局面分析
        current_player = observation.get('current_player', 1)
        player_name = "白方" if current_player == 1 else "黑方"
        analysis.append(f"当前轮到{player_name}走棋")
        
        # 将军状态
        if 'in_check' in observation:
            if observation['in_check']['white']:
                analysis.append("白王被将军！")
            if observation['in_check']['black']:
                analysis.append("黑王被将军！")
        
        # 移动数分析
        move_count = observation.get('move_count', 0)
        if move_count < 10:
            analysis.append("正在进行开局阶段，重点发展棋子和控制中心")
        elif move_count < 30:
            analysis.append("进入中局阶段，寻找战术机会")
        else:
            analysis.append("接近残局，每步棋都很关键")
        
        return "；".join(analysis)
    
    def _get_alternative_moves(self, valid_moves: List, best_move: Optional[Tuple]) -> List[Tuple]:
        """获取替代移动方案"""
        alternatives = []
        for move in valid_moves:
            if move != best_move:
                alternatives.append(move)
        return alternatives[:3]  # 最多返回3个替代方案
    
    def _calculate_move_score(self, move: Tuple[Tuple[int, int], Tuple[int, int]], 
                             before_state: Dict[str, Any], after_state: Dict[str, Any]) -> float:
        """计算移动评分"""
        # 简化的评分逻辑
        score = 0.0
        
        # 比较材料变化
        if 'captured_pieces' in before_state and 'captured_pieces' in after_state:
            before_captures = len(before_state['captured_pieces']['white']) + len(before_state['captured_pieces']['black'])
            after_captures = len(after_state['captured_pieces']['white']) + len(after_state['captured_pieces']['black'])
            
            if after_captures > before_captures:
                score += 2.0  # 吃子得分
        
        # 位置改善
        score += random.uniform(-1.0, 1.0)
        
        return score
    
    def _get_evaluation_level(self, score: float) -> str:
        """根据分数获取评价等级"""
        if score >= 2.0:
            return 'excellent'
        elif score >= 1.0:
            return 'good'
        elif score >= 0.0:
            return 'average'
        elif score >= -1.0:
            return 'poor'
        else:
            return 'blunder'
    
    def _generate_detailed_analysis(self, move: Tuple[Tuple[int, int], Tuple[int, int]], 
                                  before_state: Dict[str, Any], after_state: Dict[str, Any]) -> str:
        """生成详细分析"""
        analysis = []
        
        # 移动描述
        from_pos, to_pos = move
        cols = "abcdefgh"
        rows = "87654321"
        from_square = cols[from_pos[1]] + rows[from_pos[0]]
        to_square = cols[to_pos[1]] + rows[to_pos[0]]
        
        analysis.append(f"移动: {from_square} -> {to_square}")
        
        # 战术分析
        if 'captured_pieces' in before_state and 'captured_pieces' in after_state:
            before_captures = len(before_state['captured_pieces']['white']) + len(before_state['captured_pieces']['black'])
            after_captures = len(after_state['captured_pieces']['white']) + len(after_state['captured_pieces']['black'])
            
            if after_captures > before_captures:
                analysis.append("成功吃子")
        
        return "；".join(analysis)
    
    def _analyze_overall_performance(self) -> str:
        """分析整体表现"""
        if not self.move_evaluations:
            return "没有足够的移动记录进行分析"
        
        total_score = sum(eval['score'] for eval in self.move_evaluations)
        avg_score = total_score / len(self.move_evaluations)
        
        if avg_score >= 1.0:
            return "表现优秀！大部分移动都很有效"
        elif avg_score >= 0.0:
            return "表现良好，但还有改进空间"
        else:
            return "表现需要提高，建议多练习基本战术"
    
    def _identify_key_moments(self) -> List[str]:
        """识别关键时刻"""
        key_moments = []
        
        for i, eval in enumerate(self.move_evaluations):
            if eval['level'] == 'excellent':
                key_moments.append(f"第{i+1}手：精彩的移动！")
            elif eval['level'] == 'blunder':
                key_moments.append(f"第{i+1}手：关键错误")
        
        return key_moments
    
    def _identify_strengths(self) -> List[str]:
        """识别优势"""
        strengths = []
        
        excellent_moves = [eval for eval in self.move_evaluations if eval['level'] == 'excellent']
        if len(excellent_moves) > len(self.move_evaluations) * 0.2:
            strengths.append("战术眼光敏锐")
        
        good_moves = [eval for eval in self.move_evaluations if eval['level'] in ['excellent', 'good']]
        if len(good_moves) > len(self.move_evaluations) * 0.6:
            strengths.append("整体决策稳健")
        
        return strengths if strengths else ["继续努力，逐步提高"]
    
    def _identify_weaknesses(self) -> List[str]:
        """识别弱点"""
        weaknesses = []
        
        poor_moves = [eval for eval in self.move_evaluations if eval['level'] in ['poor', 'blunder']]
        if len(poor_moves) > len(self.move_evaluations) * 0.3:
            weaknesses.append("需要加强战术训练")
        
        blunders = [eval for eval in self.move_evaluations if eval['level'] == 'blunder']
        if len(blunders) > 2:
            weaknesses.append("避免重大失误")
        
        return weaknesses if weaknesses else ["继续保持现有水平"]
    
    def _generate_recommendations(self) -> List[str]:
        """生成建议"""
        recommendations = [
            "多练习基本战术组合",
            "学习经典开局理论",
            "提高计算能力",
            "加强残局技巧",
            "培养整体规划能力"
        ]
        
        return recommendations[:3]  # 返回3个建议
    
    def _analyze_score_trend(self) -> List[float]:
        """分析评分趋势"""
        return [eval['score'] for eval in self.move_evaluations]
    
    def _analyze_opening(self) -> str:
        """分析开局"""
        if len(self.move_evaluations) < 5:
            return "开局移动不足，无法分析"
        
        opening_scores = [eval['score'] for eval in self.move_evaluations[:10]]
        avg_opening = sum(opening_scores) / len(opening_scores)
        
        if avg_opening >= 0.5:
            return "开局发挥良好，遵循了基本原理"
        else:
            return "开局需要改进，建议学习基本开局原理"
    
    def _analyze_endgame(self) -> str:
        """分析残局"""
        if len(self.move_evaluations) < 10:
            return "残局移动不足，无法分析"
        
        endgame_scores = [eval['score'] for eval in self.move_evaluations[-10:]]
        avg_endgame = sum(endgame_scores) / len(endgame_scores)
        
        if avg_endgame >= 0.5:
            return "残局处理较好，技巧娴熟"
        else:
            return "残局需要加强，建议学习基本残局技巧"
    
    def reset_analysis(self):
        """重置分析数据"""
        self.game_history = []
        self.move_evaluations = []

# 保持向后兼容
class LLMChessAssistant(LLMChessCoach):
    """向后兼容的类名"""
    def __init__(self, name: str = "LLM教练", player_id: int = None, difficulty: str = "medium"):
        super().__init__(name, difficulty=difficulty)
        self.player_id = player_id  # 保持兼容性，但不用于对战 