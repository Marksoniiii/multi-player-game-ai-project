#!/usr/bin/env python3
"""
成语猜多多游戏类
"""

import time
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from games.base_game import BaseGame
from utils.llm_manager import llm_manager


@dataclass
class GameStats:
    """游戏统计"""
    correct_count: int = 0
    wrong_count: int = 0
    total_attempts: int = 0
    start_time: float = 0
    end_time: float = 0
    time_limit: float = 180  # 3分钟
    
    @property
    def elapsed_time(self) -> float:
        """已用时间"""
        if self.end_time > 0:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    @property
    def remaining_time(self) -> float:
        """剩余时间"""
        return max(0, self.time_limit - self.elapsed_time)
    
    @property
    def is_time_up(self) -> bool:
        """是否超时"""
        return self.remaining_time <= 0


class IdiomGuessingGame(BaseGame):
    """成语猜多多游戏"""
    
    def __init__(self, time_limit: float = 180):
        # 创建游戏配置
        game_config = {
            'timeout': time_limit,
            'max_moves': 1000  # 最大问题数
        }
        
        # 初始化游戏特有属性
        self.time_limit = time_limit
        self.game_mode = "single"  # single or pvp
        self.players = []
        self.current_player_index = 0
        self.current_question = ""
        self.current_answer = ""
        self.current_question_id = 0
        self.hint_count = 0
        self.max_hints = 2
        
        # 玩家统计
        self.player_stats = {}
        
        # 游戏状态
        self.is_running = False
        self.winner = None
        self.game_result = None
        
        # 题目历史
        self.question_history = []
        
        # 调用基类构造函数
        super().__init__(game_config)
        
    def set_game_mode(self, mode: str, players: List[str]):
        """设置游戏模式"""
        self.game_mode = mode
        self.players = players
        self.current_player_index = 0
        
        # 初始化玩家统计
        self.player_stats = {}
        for player in players:
            self.player_stats[player] = GameStats(
                start_time=time.time(),
                time_limit=self.time_limit
            )
    
    def start_game(self):
        """开始游戏"""
        self.is_running = True
        self.winner = None
        self.game_result = None
        self.question_history = []
        
        # 重置当前玩家统计
        current_player = self.get_current_player()
        if current_player:
            self.player_stats[current_player].start_time = time.time()
            self.player_stats[current_player].end_time = 0
    
    def get_current_player(self) -> Optional[str]:
        """获取当前玩家"""
        if self.players and 0 <= self.current_player_index < len(self.players):
            return self.players[self.current_player_index]
        return None
    
    def get_current_stats(self) -> Optional[GameStats]:
        """获取当前玩家统计"""
        current_player = self.get_current_player()
        if current_player:
            return self.player_stats[current_player]
        return None
    
    def generate_question(self) -> Dict[str, Any]:
        """生成新问题"""
        try:
            # 构建出题提示词
            prompt = self._build_question_prompt()
            
            # 调用LLM生成问题
            response = llm_manager.generate_text(prompt)
            
            # 解析响应
            question_data = self._parse_question_response(response)
            
            self.current_question = question_data["question"]
            self.current_answer = question_data["answer"]
            self.current_question_id += 1
            self.hint_count = 0
            
            # 记录问题历史
            self.question_history.append({
                "id": self.current_question_id,
                "question": self.current_question,
                "answer": self.current_answer,
                "player": self.get_current_player(),
                "timestamp": time.time(),
                "source": question_data.get("source", "unknown")  # 记录来源
            })
            
            return question_data
            
        except Exception as e:
            print(f"生成问题失败: {e}")
            # 降级到默认问题
            return self._get_fallback_question()
    
    def submit_answer(self, answer: str) -> Dict[str, Any]:
        """提交答案"""
        if not self.is_running:
            return {"error": "游戏未开始"}
        
        current_stats = self.get_current_stats()
        if not current_stats:
            return {"error": "无效的玩家"}
        
        # 检查是否超时
        if current_stats.is_time_up:
            return self._handle_timeout()
        
        # 更新尝试次数
        current_stats.total_attempts += 1
        
        # 判断答案
        result = self._judge_answer(answer)
        
        # 更新统计
        if result["correct"]:
            current_stats.correct_count += 1
        else:
            current_stats.wrong_count += 1
        
        # 检查游戏结束条件
        if current_stats.is_time_up:
            result.update(self._handle_timeout())
        
        return result
    
    def get_hint(self) -> Dict[str, Any]:
        """获取提示"""
        if self.hint_count >= self.max_hints:
            return {"error": "提示次数已用完"}
        
        try:
            # 构建提示提示词
            prompt = self._build_hint_prompt()
            
            # 调用LLM生成提示
            hint_text = llm_manager.generate_text(prompt)
            
            self.hint_count += 1
            
            return {
                "hint": hint_text,
                "remaining_hints": self.max_hints - self.hint_count,
                "hint_method": "ai_generated"  # 标记提示方法
            }
            
        except Exception as e:
            print(f"生成提示失败: {e}")
            return {"error": "提示生成失败"}
    
    def next_player(self) -> Dict[str, Any]:
        """切换到下一个玩家"""
        if self.game_mode == "single":
            return {"error": "单人模式无法切换玩家"}
        
        # 结束当前玩家的游戏
        current_stats = self.get_current_stats()
        if current_stats:
            current_stats.end_time = time.time()
        
        # 切换到下一个玩家
        self.current_player_index += 1
        
        if self.current_player_index >= len(self.players):
            # 所有玩家都完成了，结束游戏
            return self._end_game()
        else:
            # 开始下一个玩家的游戏
            self.start_game()
            return {
                "current_player": self.get_current_player(),
                "message": f"轮到{self.get_current_player()}了！"
            }
    
    def _build_question_prompt(self) -> str:
        """构建出题提示词"""
        prompt = f"""你是一个成语猜谜游戏的出题者。请为玩家出一道成语题。

要求：
1. 选择一个常见的四字成语
2. 用多样化的方式描述这个成语的含义，但绝对不要直接说出成语本身
3. 描述方式可以是：典故、情景、反义词、字面解释、谜语等
4. 描述要准确但不要太简单或太难
5. 重要：描述中不能包含成语中的任何字或词，避免暴露答案
6. 请按照以下格式回复：

成语：[四字成语]
描述：[对成语的描述]

现在请出题："""
        
        return prompt
    
    def _parse_question_response(self, response: str) -> Dict[str, Any]:
        """解析问题响应"""
        try:
            lines = response.strip().split('\n')
            answer = ""
            question = ""
            
            # 解析AI返回的成语和描述
            for line in lines:
                line = line.strip()
                if line.startswith("成语："):
                    answer = line.replace("成语：", "").strip()
                elif line.startswith("描述："):
                    question = line.replace("描述：", "").strip()
            
            # 清理答案中的标点符号或引号
            answer = answer.replace("「", "").replace("」", "").replace("'", "").replace('"', "")
            
            # 如果AI没有返回成语和描述，使用备用题库
            if not answer or not question:
                print("AI未返回完整格式，使用备用题库")
                return self._get_fallback_question()
            
            # 清理描述中的多余内容
            question = question.strip()
            # 移除描述开头的模板化内容
            if question.startswith("请根据以下描述猜成语："):
                question = question.replace("请根据以下描述猜成语：", "").strip()
            elif question.startswith("题目："):
                question = question.replace("题目：", "").strip()
            elif question.startswith("这个成语的意思是："):
                question = question.replace("这个成语的意思是：", "").strip()
            elif question.startswith("有一个成语，它的含义是"):
                question = question.replace("有一个成语，它的含义是", "").strip()
                if question.endswith("，请猜一猜。"):
                    question = question.replace("，请猜一猜。", "").strip()
                elif question.endswith("。请问是什么成语？"):
                    question = question.replace("。请问是什么成语？", "").strip()
            
            # 验证答案是否为四字成语
            if len(answer) != 4:
                print(f"AI返回的答案不是四字成语: {answer}，使用备用题库")
                return self._get_fallback_question()
            
            print(f"AI生成题目成功 - 成语: {answer}, 描述: {question}")
            
            return {
                "question": question,
                "answer": answer,
                "question_id": self.current_question_id + 1,
                "source": "ai"  # 标记为AI生成
            }
            
        except Exception as e:
            print(f"解析问题失败: {e}")
            return self._get_fallback_question()
    
    def _get_fallback_question(self) -> Dict[str, Any]:
        """获取备用问题"""
        fallback_questions = [
            {"question": "这个成语比喻做了多余的事情，反而坏了事。来自古代一个画蛇比赛的故事。", "answer": "画蛇添足"},
            {"question": "这个成语比喻死守陈规，不知变通。讲的是一个人守着树等兔子的故事。", "answer": "守株待兔"},
            {"question": "这个成语比喻出了问题后想办法补救。讲的是羊丢了再修羊圈的故事。", "answer": "亡羊补牢"},
            {"question": "这个成语比喻观念陈旧，不知变通。讲的是在船上找掉到水里的剑的故事。", "answer": "刻舟求剑"},
            {"question": "这个成语比喻刻苦学习。讲的是用绳子吊着头发防止瞌睡，用锥子刺大腿保持清醒。", "answer": "悬梁刺股"},
            {"question": "这个成语比喻勤奋好学。讲的是在墙上凿洞借邻居家的灯光看书。", "answer": "凿壁偷光"},
            {"question": "这个成语比喻心情非常愉快，就像花朵盛开一样。", "answer": "心花怒放"},
            {"question": "这个成语比喻人的才能很高，就像装了八斗粮食一样。", "answer": "才高八斗"},
            {"question": "这个成语比喻做事非常认真，连吃饭睡觉都忘记了。", "answer": "废寝忘食"},
            {"question": "这个成语比喻做事很有毅力，就像用刀刻东西一样坚持不懈。", "answer": "锲而不舍"},
        ]
        
        selected = random.choice(fallback_questions)
        return {
            "question": selected["question"],
            "answer": selected["answer"],
            "question_id": self.current_question_id + 1,
            "source": "fallback"  # 标记为备用题库
        }
    
    def _judge_answer(self, answer: str) -> Dict[str, Any]:
        """判断答案"""
        try:
            # 直接比较答案，不使用AI判断
            is_correct = self._simple_compare(answer)
            
            result = {
                "correct": is_correct,
                "user_answer": answer,
                "correct_answer": self.current_answer,
                "judge_method": "direct_compare"  # 标记判断方法
            }
            
            if is_correct:
                result["message"] = f"恭喜你，回答正确！"
            else:
                result["message"] = f"很遗憾，回答错误。正确答案是：{self.current_answer}"
                if self.hint_count < self.max_hints:
                    result["hint_available"] = True
            
            # 无论对错都生成新题目，避免作弊
            next_question = self.generate_question()
            result["next_question"] = next_question
            
            return result
            
        except Exception as e:
            print(f"判断答案失败: {e}")
            # 降级到简单比较
            return self._simple_judge(answer)
    

    
    def _simple_judge(self, answer: str) -> Dict[str, Any]:
        """简单判断"""
        is_correct = self._simple_compare(answer)
        
        result = {
            "correct": is_correct,
            "user_answer": answer,
            "correct_answer": self.current_answer
        }
        
        if is_correct:
            result["message"] = f"恭喜你，回答正确！"
        else:
            result["message"] = f"很遗憾，回答错误。正确答案是：{self.current_answer}"
            if self.hint_count < self.max_hints:
                result["hint_available"] = True
        
        # 无论对错都生成新题目，避免作弊
        next_question = self.generate_question()
        result["next_question"] = next_question
        
        return result
    
    def _simple_compare(self, answer: str) -> bool:
        """简单比较答案"""
        # 去除空格和标点
        clean_answer = answer.replace(" ", "").replace("，", "").replace("。", "").replace("！", "").replace("？", "")
        clean_correct = self.current_answer.replace(" ", "").replace("，", "").replace("。", "").replace("！", "").replace("？", "")
        
        # 完全匹配
        if clean_answer == clean_correct:
            return True
        
        # 支持一些常见的变体
        # 例如：画蛇添足 vs 画蛇添足
        # 例如：守株待兔 vs 守株待兔
        # 这里可以添加更多的同义词或变体处理
        
        return False
    
    def _build_hint_prompt(self) -> str:
        """构建提示提示词"""
        prompt = f"""你是一个成语猜谜游戏的提示者。

题目：{self.current_question}
正确答案：{self.current_answer}
这是第{self.hint_count + 1}次提示（最多{self.max_hints}次）

请给出一个有用的提示，帮助玩家猜出答案，但不要直接说出答案。
提示可以是：
1. 关键字的含义
2. 成语的结构特点
3. 相关的同义词或反义词
4. 更具体的使用场景

请用简短的一句话给出提示："""
        
        return prompt
    
    def _handle_timeout(self) -> Dict[str, Any]:
        """处理超时"""
        current_stats = self.get_current_stats()
        if current_stats:
            current_stats.end_time = time.time()
        
        if self.game_mode == "single":
            self.is_running = False
            return {
                "game_over": True,
                "reason": "timeout",
                "message": "时间到！游戏结束。",
                "final_score": current_stats.correct_count if current_stats else 0
            }
        else:
            return self.next_player()
    
    def _end_game(self) -> Dict[str, Any]:
        """结束游戏"""
        self.is_running = False
        
        # 计算最终结果
        scores = {}
        for player, stats in self.player_stats.items():
            scores[player] = stats.correct_count
        
        # 找到获胜者
        if scores:
            max_score = max(scores.values())
            winners = [player for player, score in scores.items() if score == max_score]
            
            if len(winners) == 1:
                self.winner = winners[0]
                result_message = f"恭喜{self.winner}获胜！"
            else:
                result_message = f"平局！{', '.join(winners)}并列第一。"
        else:
            result_message = "游戏结束。"
        
        return {
            "game_over": True,
            "reason": "completed",
            "message": result_message,
            "scores": scores,
            "winner": self.winner,
            "statistics": self.get_game_statistics()
        }
    
    def get_game_statistics(self) -> Dict[str, Any]:
        """获取游戏统计信息"""
        stats = {}
        for player, player_stats in self.player_stats.items():
            stats[player] = {
                "correct_count": player_stats.correct_count,
                "wrong_count": player_stats.wrong_count,
                "total_attempts": player_stats.total_attempts,
                "accuracy": player_stats.correct_count / max(1, player_stats.total_attempts),
                "time_used": player_stats.elapsed_time,
                "avg_time_per_question": player_stats.elapsed_time / max(1, player_stats.correct_count)
            }
        
        return stats
    
    def get_game_info(self) -> Dict[str, Any]:
        """获取游戏信息"""
        current_stats = self.get_current_stats()
        current_player = self.get_current_player()
        
        info = {
            "game_mode": self.game_mode,
            "current_player": current_player,
            "is_running": self.is_running,
            "current_question": self.current_question,
            "current_question_id": self.current_question_id,
            "hint_count": self.hint_count,
            "max_hints": self.max_hints,
            "time_limit": self.time_limit,
            "question_history_count": len(self.question_history)
        }
        
        if current_stats:
            info.update({
                "correct_count": current_stats.correct_count,
                "wrong_count": current_stats.wrong_count,
                "total_attempts": current_stats.total_attempts,
                "elapsed_time": current_stats.elapsed_time,
                "remaining_time": current_stats.remaining_time,
                "is_time_up": current_stats.is_time_up
            })
        
        return info
    
    def reset(self):
        """重置游戏"""
        self.current_player_index = 0
        self.current_question = ""
        self.current_answer = ""
        self.current_question_id = 0
        self.hint_count = 0
        self.is_running = False
        self.winner = None
        self.game_result = None
        self.question_history = []
        self.player_stats = {}
        
        # 重新初始化玩家统计
        for player in self.players:
            self.player_stats[player] = GameStats(time_limit=self.time_limit)
        
        # 调用父类reset
        self.move_count = 0
        self.history = []
        self.current_player = 1
        self.game_state = "ongoing"
        self.start_time = time.time()
        self.last_move_time = time.time()
        
        return self.get_game_info()
    
    def step(self, action: Any) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """执行一步动作"""
        if isinstance(action, str):
            if action.startswith("answer:"):
                answer = action[7:].strip()
                result = self.submit_answer(answer)
                reward = 1.0 if result.get("correct", False) else -0.1
                done = result.get("game_over", False)
                observation = self.get_state()
                info = {"action_result": result}
                return observation, reward, done, info
            elif action == "hint":
                result = self.get_hint()
                reward = -0.05
                done = False
                observation = self.get_state()
                info = {"action_result": result}
                return observation, reward, done, info
            elif action == "next_player":
                result = self.next_player()
                reward = 0.0
                done = result.get("game_over", False)
                observation = self.get_state()
                info = {"action_result": result}
                return observation, reward, done, info
            elif action == "generate_question":
                result = self.generate_question()
                reward = 0.0
                done = False
                observation = self.get_state()
                info = {"action_result": result}
                return observation, reward, done, info
        
        # 默认处理
        return self.get_state(), 0.0, False, {"error": "Invalid action"}
    
    def get_valid_actions(self, player: int = None) -> List[Any]:
        """获取有效动作列表"""
        if not self.is_running:
            return ["generate_question"]
        
        actions = ["answer:", "hint"]
        if self.game_mode == "pvp":
            actions.append("next_player")
        
        return actions
    
    def is_terminal(self) -> bool:
        """检查游戏是否结束"""
        return not self.is_running
    
    def get_winner(self) -> Optional[int]:
        """获取获胜者"""
        if self.game_mode == "single":
            return 1 if self.is_running else None
        
        if self.winner and len(self.players) >= 2:
            try:
                winner_index = self.players.index(self.winner)
                return winner_index + 1
            except ValueError:
                return None
        
        return None
    
    def get_state(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        return self.get_game_info()
    
    def render(self) -> str:
        """渲染游戏画面"""
        game_info = self.get_game_info()
        output = []
        output.append("=" * 50)
        output.append("🎯 成语猜多多")
        output.append("=" * 50)
        
        if game_info.get("current_player"):
            output.append(f"当前玩家: {game_info['current_player']}")
        
        output.append(f"游戏模式: {'双人对战' if self.game_mode == 'pvp' else '单人模式'}")
        
        if game_info.get("is_running", False):
            output.append(f"剩余时间: {game_info.get('remaining_time', 0):.1f}秒")
            output.append(f"已答对: {game_info.get('correct_count', 0)}题")
            output.append(f"已答错: {game_info.get('wrong_count', 0)}题")
            
            if game_info.get("current_question"):
                output.append("")
                output.append(f"题目: {game_info['current_question']}")
            else:
                output.append("等待生成题目...")
        else:
            output.append("游戏未开始")
        
        output.append("=" * 50)
        return "\n".join(output) 