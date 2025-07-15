#!/usr/bin/env python3
"""
LLM成语出题机器人
专门用于成语猜多多游戏的智能出题和评判
"""

import time
import random
from typing import Dict, List, Any, Optional, Tuple
from agents.base_agent import BaseAgent
from utils.llm_manager import llm_manager


class LLMIdiomBot(BaseAgent):
    """LLM成语出题机器人 - 支持多轮对话"""
    
    def __init__(self, name: str = "LLM出题官", player_id: int = 0):
        super().__init__(name, player_id)
        self.role = "question_master"  # 角色：出题官
        self.difficulty_level = "medium"  # 难度级别
        self.question_types = [
            "story",        # 故事描述
            "meaning",      # 含义解释
            "opposite",     # 反义词提示
            "structure",    # 结构分析
            "riddle",       # 谜语形式
            "usage",        # 使用场景
            "character"     # 字面分析
        ]
        self.current_question_type = None
        self.current_idiom = None
        self.current_description = None
        self.hint_history = []
        
        # 历史记录跟踪
        self.used_idioms = set()  # 已使用的成语
        self.question_history = []  # 问题历史
        
        # 统计信息
        self.questions_generated = 0
        self.correct_judgments = 0
        self.wrong_judgments = 0
        self.hints_provided = 0
        
        # 初始化多轮对话
        self._initialize_conversation()
        
    def _initialize_conversation(self):
        """初始化多轮对话"""
        # 获取当前客户端并设置系统消息（仅千问支持多轮对话）
        try:
            current_client = llm_manager.current_client
            if (current_client and 
                current_client.__class__.__name__ == 'QianwenClient'):
                system_message = """你是一个专业的成语猜谜游戏出题官。你需要根据历史对话中已经使用过的成语，每次出一道全新的成语题，绝对不能重复使用任何成语。

你的职责：
1. 根据要求出成语题，每次都要选择不同的成语
2. 记住之前所有出过的成语，绝对不能重复
3. 判断用户答案是否正确
4. 提供合适的提示
5. 保持题目的趣味性和挑战性

出题格式要求：
成语：[四字成语]
描述：[对成语的生动描述]

请始终遵循这个格式，确保每次出题都使用不同的成语。"""
                # 使用 getattr 安全调用方法
                set_system_message = getattr(current_client, 'set_system_message', None)
                if set_system_message:
                    set_system_message(system_message)
        except Exception as e:
            print(f"初始化多轮对话失败: {e}")
    
    def reset_conversation(self):
        """重置对话历史但保留系统消息"""
        try:
            current_client = llm_manager.current_client
            if (current_client and 
                current_client.__class__.__name__ == 'QianwenClient'):
                # 使用 getattr 安全调用方法
                clear_history = getattr(current_client, 'clear_history', None)
                if clear_history:
                    clear_history()
                    self._initialize_conversation()
        except Exception as e:
            print(f"重置对话失败: {e}")
    
    def clear_all_history(self):
        """完全重置所有历史记录"""
        self.used_idioms.clear()
        self.question_history.clear()
        self.hint_history.clear()
        self.questions_generated = 0
        self.correct_judgments = 0
        self.wrong_judgments = 0
        self.hints_provided = 0
        self.reset_conversation()
        
    def get_action(self, observation: Any, env: Any) -> Any:
        """获取动作（对于出题机器人，这个方法不直接使用）"""
        return None
    
    def generate_question(self, difficulty: str = "medium") -> Dict[str, Any]:
        """生成成语题目"""
        self.difficulty_level = difficulty
        
        max_attempts = 5  # 最大尝试次数
        for attempt in range(max_attempts):
            try:
                # 选择出题方式
                question_type = random.choice(self.question_types)
                self.current_question_type = question_type
                
                # 构建提示词，包含已使用的成语列表
                prompt = self._build_question_prompt(question_type, difficulty)
                
                # 构建简化的多轮对话提示词
                difficulty_desc = {
                    "easy": "简单常见",
                    "medium": "中等难度", 
                    "hard": "较难"
                }.get(difficulty, "中等难度")
                
                simplified_prompt = f"请为我出第{self.questions_generated + 1}道成语题，要求与之前所有题目的成语都不相同，选择{difficulty_desc}的成语。"
                
                # 调用LLM生成题目，使用多轮对话
                response = llm_manager.generate_text(
                    simplified_prompt, 
                    temperature=0.95,  # 增加随机性
                    max_tokens=500,
                    top_p=0.95
                )
                
                # 解析响应
                question_data = self._parse_question_response(response)
                
                # 检查是否重复
                if question_data["answer"] in self.used_idioms:
                    print(f"检测到重复成语: {question_data['answer']}, 重新生成...")
                    continue
                
                # 记录当前题目信息
                self.current_idiom = question_data["answer"]
                self.current_description = question_data["question"]
                self.hint_history = []
                
                # 添加到历史记录
                self.used_idioms.add(question_data["answer"])
                self.question_history.append(question_data)
                
                # 更新统计
                self.questions_generated += 1
                
                return question_data
                
            except Exception as e:
                print(f"生成题目失败 (尝试 {attempt + 1}/{max_attempts}): {e}")
                if attempt == max_attempts - 1:
                    return self._get_fallback_question()
                continue
        
        return self._get_fallback_question()
    
    def judge_answer(self, user_answer: str, correct_answer: str, question: str) -> Dict[str, Any]:
        """判断答案是否正确"""
        try:
            # 构建判断提示词
            prompt = self._build_judgment_prompt(user_answer, correct_answer, question)
            
            # 调用LLM判断，适度的随机性
            response = llm_manager.generate_text(
                prompt, 
                temperature=0.7,  # 适度的随机性
                max_tokens=300
            )
            
            # 解析判断结果
            judgment_result = self._parse_judgment_response(response, user_answer, correct_answer)
            
            # 更新统计
            if judgment_result["correct"]:
                self.correct_judgments += 1
            else:
                self.wrong_judgments += 1
            
            return judgment_result
            
        except Exception as e:
            print(f"判断答案失败: {e}")
            return self._fallback_judgment(user_answer, correct_answer)
    
    def provide_hint(self, hint_level: int = 1) -> Dict[str, Any]:
        """提供提示"""
        if not self.current_idiom or not self.current_description:
            return {"error": "没有当前题目"}
        
        try:
            # 构建提示提示词
            prompt = self._build_hint_prompt(hint_level)
            
            # 调用LLM生成提示，适度的随机性
            response = llm_manager.generate_text(
                prompt, 
                temperature=0.8,  # 适度的随机性
                max_tokens=200
            )
            
            # 解析提示
            hint_data = self._parse_hint_response(response)
            
            # 记录提示历史
            self.hint_history.append({
                "level": hint_level,
                "hint": hint_data["hint"],
                "timestamp": time.time()
            })
            
            # 更新统计
            self.hints_provided += 1
            
            return hint_data
            
        except Exception as e:
            print(f"生成提示失败: {e}")
            return self._fallback_hint(hint_level)
    
    def _build_question_prompt(self, question_type: str, difficulty: str) -> str:
        """构建出题提示词"""
        difficulty_desc = {
            "easy": "简单常见",
            "medium": "中等难度",
            "hard": "较难"
        }.get(difficulty, "中等难度")
        
        type_instructions = {
            "story": "通过讲述成语的典故或故事来描述",
            "meaning": "通过解释成语的含义和用法来描述",
            "opposite": "通过提及反义词或对比概念来描述",
            "structure": "通过分析成语的结构和组成来描述",
            "riddle": "用谜语的形式来描述",
            "usage": "通过举例说明使用场景来描述",
            "character": "通过分析其中某个关键字的含义来描述"
        }.get(question_type, "通过含义解释来描述")
        
        # 添加随机性和多样性
        # 基础种子短语
        seed_phrases = [
            "请为我出一道成语题",
            "我需要一个成语猜谜",
            "给我一个成语问题",
            "出一道成语谜题",
            "请出一个成语题目",
            "帮我想一个成语问题",
            "来出个成语考题",
            "设计一个成语谜题"
        ]
        
        # 添加时间戳和随机数增强唯一性
        timestamp = int(time.time())
        random_num = random.randint(1000, 9999)
        seed_phrase = random.choice(seed_phrases)
        
        # 严格禁止重复的成语列表
        banned_idioms = [
            "画龙点睛", "画蛇添足", "守株待兔", "亡羊补牢", "刻舟求剑", 
            "买椟还珠", "杯弓蛇影", "掩耳盗铃", "南辕北辙", "坐井观天",
            "叶公好龙", "东施效颦", "塞翁失马", "狐假虎威", "愚公移山"
        ]
        
        # 推荐使用的成语分类
        recommended_categories = {
            "动物类": ["鸡犬不宁", "虎头蛇尾", "龙飞凤舞", "鹤立鸡群", "蛇蝎心肠"],
            "人物类": ["才高八斗", "德高望重", "风度翩翩", "义薄云天", "心怀叵测"],
            "自然类": ["山清水秀", "鸟语花香", "风调雨顺", "电闪雷鸣", "春暖花开"],
            "情感类": ["心花怒放", "怒发冲冠", "忧心忡忡", "欣喜若狂", "愁眉苦脸"],
            "行为类": ["勤学苦练", "废寝忘食", "夜以继日", "锲而不舍", "三心二意"]
        }
        
        category = random.choice(list(recommended_categories.keys()))
        suggested_idioms = recommended_categories[category]
        
        # 创建多样化的要求
        diversity_phrases = [
            f"（时间戳：{timestamp}，随机码：{random_num}）请从{category}中选择一个成语",
            f"现在是{timestamp}，请出一个编号{random_num}的题目，建议使用{category}",
            f"第{random_num}题，时间{timestamp}，主题：{category}",
            f"题目编号{random_num}，请从{category}中选择，避开常见成语：{', '.join(banned_idioms[:5])}",
            f"请确保这是独特的第{random_num}个题目（{timestamp}），参考{category}：{', '.join(suggested_idioms[:3])}"
        ]
        
        diversity_phrase = random.choice(diversity_phrases)
        
        # 添加已使用的成语到禁止列表
        if self.used_idioms:
            used_idioms_str = f"已使用过的成语（绝对不能重复）：{', '.join(self.used_idioms)}"
        else:
            used_idioms_str = ""
        
        prompt = f"""你是一个专业的成语猜谜游戏出题官。{seed_phrase}{diversity_phrase}

出题要求：
1. 选择一个{difficulty_desc}的四字成语，类型为{category}
2. 绝对禁止使用这些成语：{', '.join(banned_idioms)}
3. {used_idioms_str}
4. 建议从这些成语中选择：{', '.join(suggested_idioms)}
5. 采用{type_instructions}的方式
6. 描述要准确生动，既有趣又有挑战性
7. 不能直接说出成语本身
8. 描述长度控制在30-80字之间
9. 每次必须选择不同的成语，确保答案多样性

请按照以下格式严格回复：
成语：[四字成语]
描述：[对成语的{question_type}描述]

现在请出题："""
        
        return prompt
    
    def _build_judgment_prompt(self, user_answer: str, correct_answer: str, question: str) -> str:
        """构建判断提示词"""
        prompt = f"""你是一个专业的成语猜谜游戏判断官。请判断用户的答案是否正确。

题目：{question}
标准答案：{correct_answer}
用户答案：{user_answer}

判断标准：
1. 完全匹配标准答案 - 正确
2. 意思完全相同的同义成语 - 正确
3. 错别字但意思清楚且字音相近 - 正确
4. 意思接近但不完全相同 - 错误
5. 完全不同 - 错误

请按照以下格式回复：
判断：[正确/错误]
理由：[简短解释为什么正确或错误]
鼓励：[给玩家的鼓励或建议，1-2句话]

现在请判断："""
        
        return prompt
    
    def _build_hint_prompt(self, hint_level: int) -> str:
        """构建提示提示词"""
        previous_hints = "\n".join([f"提示{i+1}：{h['hint']}" for i, h in enumerate(self.hint_history)])
        
        hint_strategies = {
            1: "给出成语中一个关键字的含义或用法",
            2: "提供更具体的使用场景或例子",
            3: "给出成语的结构特点或相关词汇"
        }
        
        strategy = hint_strategies.get(hint_level, "给出更详细的解释")
        
        prompt = f"""你是一个专业的成语猜谜游戏提示官。请为玩家提供第{hint_level}个提示。

原题目：{self.current_description}
正确答案：{self.current_idiom}
提示策略：{strategy}

之前的提示：
{previous_hints if previous_hints else "无"}

要求：
1. 提示要有用但不能过于直接
2. 每个提示都要有新的信息
3. 控制在20字以内
4. 不能直接说出答案

请按照以下格式回复：
提示：[具体的提示内容]
解释：[为什么这个提示有用]

现在请提供提示："""
        
        return prompt
    
    def _parse_question_response(self, response: str) -> Dict[str, Any]:
        """解析出题响应"""
        try:
            lines = response.strip().split('\n')
            answer = ""
            question = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith("成语："):
                    answer = line.replace("成语：", "").strip()
                elif line.startswith("描述："):
                    question = line.replace("描述：", "").strip()
            
            # 清理答案中的标点符号
            answer = answer.replace("「", "").replace("」", "").replace("'", "").replace('"', "")
            
            if not answer or not question:
                # 尝试其他解析方式
                if "：" in response:
                    parts = response.split("：")
                    if len(parts) >= 2:
                        answer = parts[1].split('\n')[0].strip()
                        for line in lines:
                            if "描述" in line:
                                question = line.split("：")[-1].strip()
                                break
            
            if not answer or not question:
                raise ValueError("无法解析LLM响应")
            
            return {
                "question": question,
                "answer": answer,
                "type": self.current_question_type,
                "difficulty": self.difficulty_level,
                "generated_by": self.name
            }
            
        except Exception as e:
            print(f"解析问题失败: {e}")
            return self._get_fallback_question()
    
    def _parse_judgment_response(self, response: str, user_answer: str, correct_answer: str) -> Dict[str, Any]:
        """解析判断响应"""
        try:
            lines = response.strip().split('\n')
            judgment = ""
            reason = ""
            encouragement = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith("判断："):
                    judgment = line.replace("判断：", "").strip()
                elif line.startswith("理由："):
                    reason = line.replace("理由：", "").strip()
                elif line.startswith("鼓励："):
                    encouragement = line.replace("鼓励：", "").strip()
            
            is_correct = "正确" in judgment
            
            return {
                "correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "reason": reason,
                "encouragement": encouragement,
                "response": response
            }
            
        except Exception as e:
            print(f"解析判断失败: {e}")
            return self._fallback_judgment(user_answer, correct_answer)
    
    def _parse_hint_response(self, response: str) -> Dict[str, Any]:
        """解析提示响应"""
        try:
            lines = response.strip().split('\n')
            hint = ""
            explanation = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith("提示："):
                    hint = line.replace("提示：", "").strip()
                elif line.startswith("解释："):
                    explanation = line.replace("解释：", "").strip()
            
            if not hint:
                # 尝试直接提取
                hint = response.strip()
            
            return {
                "hint": hint,
                "explanation": explanation,
                "level": len(self.hint_history) + 1
            }
            
        except Exception as e:
            print(f"解析提示失败: {e}")
            return self._fallback_hint(len(self.hint_history) + 1)
    
    def _get_fallback_question(self) -> Dict[str, Any]:
        """获取备用题目"""
        fallback_questions = [
            {
                "question": "古代有人画蛇比赛，有人画得快，但又给蛇加上了脚，结果反而输了。这个成语比喻做多余的事反而坏事。",
                "answer": "画蛇添足",
                "type": "story",
                "difficulty": "easy"
            },
            {
                "question": "一个农夫在田里干活，看见一只兔子撞死在树桩上，于是就每天守在那里等兔子，结果田荒了也没等到。比喻不劳而获的侥幸心理。",
                "answer": "守株待兔",
                "type": "story",
                "difficulty": "easy"
            },
            {
                "question": "羊跑了之后再去修补羊圈，虽然晚了但还不算太迟。比喻出了问题后想办法补救，防止继续损失。",
                "answer": "亡羊补牢",
                "type": "meaning",
                "difficulty": "easy"
            },
            {
                "question": "船在移动，而有人在船舷上刻记号来寻找掉进水里的剑。比喻拘泥成规，不懂得根据客观情况的变化而灵活处理。",
                "answer": "刻舟求剑",
                "type": "story",
                "difficulty": "medium"
            },
            {
                "question": "比喻一个人学习很用功，连晚上都用绳子吊着头发防止瞌睡，用锥子刺大腿保持清醒。",
                "answer": "悬梁刺股",
                "type": "story",
                "difficulty": "medium"
            },
            {
                "question": "某人为了读书，在墙上凿了一个洞，借邻居家的灯光来看书。比喻勤奋好学，不怕困难。",
                "answer": "凿壁偷光",
                "type": "story",
                "difficulty": "medium"
            },
            {
                "question": "形容心情非常愉快，就像花朵盛开一样。",
                "answer": "心花怒放",
                "type": "meaning",
                "difficulty": "easy"
            },
            {
                "question": "比喻人的才能很高，就像装了八斗粮食一样。",
                "answer": "才高八斗",
                "type": "meaning",
                "difficulty": "medium"
            }
        ]
        
        # 找到未使用的备用题目
        available_questions = [q for q in fallback_questions if q["answer"] not in self.used_idioms]
        
        if not available_questions:
            # 如果所有备用题目都用完了，随机选择一个
            available_questions = fallback_questions
        
        selected = random.choice(available_questions)
        self.current_idiom = selected["answer"]
        self.current_description = selected["question"]
        self.current_question_type = selected["type"]
        
        # 添加到历史记录
        self.used_idioms.add(selected["answer"])
        
        return {
            "question": selected["question"],
            "answer": selected["answer"],
            "type": selected["type"],
            "difficulty": selected["difficulty"],
            "generated_by": f"{self.name}(备用)"
        }
    
    def _fallback_judgment(self, user_answer: str, correct_answer: str) -> Dict[str, Any]:
        """备用判断"""
        # 简单的字符串比较
        is_correct = user_answer.strip() == correct_answer.strip()
        
        return {
            "correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "reason": "基于简单字符串匹配的判断",
            "encouragement": "继续努力！" if not is_correct else "回答正确！",
            "response": f"{'正确' if is_correct else '错误'}"
        }
    
    def _fallback_hint(self, hint_level: int) -> Dict[str, Any]:
        """备用提示"""
        fallback_hints = {
            1: "这个成语包含一个动物或物品",
            2: "这个成语常用来形容某种行为或态度",
            3: "这个成语有四个字，结构工整"
        }
        
        hint = fallback_hints.get(hint_level, "这是一个常见的成语")
        
        return {
            "hint": hint,
            "explanation": "这是一个通用提示",
            "level": hint_level
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "questions_generated": self.questions_generated,
            "correct_judgments": self.correct_judgments,
            "wrong_judgments": self.wrong_judgments,
            "hints_provided": self.hints_provided,
            "judgment_accuracy": self.correct_judgments / max(1, self.correct_judgments + self.wrong_judgments),
            "current_idiom": self.current_idiom,
            "current_type": self.current_question_type,
            "difficulty_level": self.difficulty_level,
            "hint_history_count": len(self.hint_history),
            "used_idioms_count": len(self.used_idioms),
            "used_idioms": list(self.used_idioms),
            "question_history_count": len(self.question_history)
        }
    
    def reset_current_question(self):
        """重置当前题目"""
        self.current_idiom = None
        self.current_description = None
        self.current_question_type = None
        self.hint_history = []
    
    def reset_all_history(self):
        """重置所有历史记录"""
        self.used_idioms.clear()
        self.question_history.clear()
        self.reset_current_question()
    
    def set_difficulty(self, difficulty: str):
        """设置难度"""
        if difficulty in ["easy", "medium", "hard"]:
            self.difficulty_level = difficulty
        
    def get_question_types(self) -> List[str]:
        """获取支持的出题类型"""
        return self.question_types.copy()
    
    def reset(self):
        """重置统计"""
        super().reset()
        self.questions_generated = 0
        self.correct_judgments = 0
        self.wrong_judgments = 0
        self.hints_provided = 0
        self.reset_all_history() 