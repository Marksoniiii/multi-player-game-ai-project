import json
import random
import re
from typing import Dict, List, Any, Optional

try:
    import google.generativeai as genai  # type: ignore
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai: Any = None  # type: ignore
    print("警告：google-generativeai 未安装，将使用离线模式")

from ..base_agent import BaseAgent


class GeminiIdiomBot(BaseAgent):
    """基于Gemini的成语猜多多游戏机器人"""
    
    def __init__(self, api_key: str = None):
        super().__init__()
        self.api_key = api_key
        self.model = None
        self.current_idiom = "画蛇添足"  # 默认成语
        self.current_question = ""  # 当前问题
        self.question_types = [
            "story", "antonym", "allusion", "literal", "riddle", "synonym", "usage"
        ]
        
        # 成语库（可以扩展）
        self.idiom_bank = [
            "画蛇添足", "杯弓蛇影", "亡羊补牢", "守株待兔", "刻舟求剑",
            "掩耳盗铃", "买椟还珠", "南辕北辙", "画饼充饥", "望梅止渴",
            "班门弄斧", "滥竽充数", "叶公好龙", "邯郸学步", "东施效颦",
            "狐假虎威", "鹬蚌相争", "螳螂捕蝉", "塞翁失马", "朝三暮四",
            "井底之蛙", "坐井观天", "夜郎自大", "盲人摸象", "管中窥豹"
        ]
        
        # 初始化模型
        self._initialize_model()
    
    def _initialize_model(self):
        """初始化Gemini模型"""
        if not GEMINI_AVAILABLE or genai is None:
            print("Google Generative AI SDK 未安装，使用离线模式")
            return
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # 配置生成参数
                generation_config = genai.types.GenerationConfig(
                    temperature=0.7,
                    top_k=40,
                    top_p=0.8,
                    max_output_tokens=1024,
                )
                # 创建模型实例
                self.model = genai.GenerativeModel(
                    model_name='gemini-1.5-flash-latest',
                    generation_config=generation_config
                )
                print("Gemini模型初始化成功")
            except Exception as e:
                print(f"Gemini模型初始化失败: {e}")
                self.model = None
        else:
            print("API密钥未设置，使用离线模式")
    
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.api_key = api_key
        self._initialize_model()
    
    def is_online_mode(self) -> bool:
        """检查是否处于在线模式"""
        return GEMINI_AVAILABLE and self.model is not None
    
    def generate_question(self) -> str:
        """生成成语问题"""
        if not self.is_online_mode():
            return self._generate_fallback_question()
        
        # 随机选择成语和问题类型
        self.current_idiom = random.choice(self.idiom_bank)
        question_type = random.choice(self.question_types)
        
        prompt = self._build_question_prompt(self.current_idiom, question_type)
        
        try:
            if self.model is not None:
                response = self.model.generate_content(prompt)
                question = self._extract_question_from_response(response.text)
                self.current_question = question
                return question
            else:
                return self._generate_fallback_question()
        except Exception as e:
            print(f"Gemini API调用失败: {e}")
            return self._generate_fallback_question()
    
    def check_answer(self, question: str, answer: str) -> Dict[str, Any]:
        """检查答案是否正确"""
        if not self.is_online_mode():
            return self._check_answer_fallback(question, answer)
        
        prompt = self._build_check_prompt(question, answer, self.current_idiom)
        
        try:
            if self.model is not None:
                response = self.model.generate_content(prompt)
                result = self._extract_check_result_from_response(response.text)
                return result
            else:
                return self._check_answer_fallback(question, answer)
        except Exception as e:
            print(f"Gemini API调用失败: {e}")
            return self._check_answer_fallback(question, answer)
    
    def get_hint(self, question: str) -> str:
        """获取提示"""
        if not self.is_online_mode():
            return self._generate_fallback_hint()
        
        prompt = self._build_hint_prompt(question, self.current_idiom)
        
        try:
            if self.model is not None:
                response = self.model.generate_content(prompt)
                hint = self._extract_hint_from_response(response.text)
                return hint
            else:
                return self._generate_fallback_hint()
        except Exception as e:
            print(f"Gemini API调用失败: {e}")
            return self._generate_fallback_hint()
    
    def generate_question_stream(self) -> Any:
        """生成流式问题（演示流式功能）"""
        if not self.is_online_mode():
            return None
        
        self.current_idiom = random.choice(self.idiom_bank)
        question_type = random.choice(self.question_types)
        prompt = self._build_question_prompt(self.current_idiom, question_type)
        
        try:
            if self.model is not None:
                response = self.model.generate_content(prompt, stream=True)
                return response
            else:
                return None
        except Exception as e:
            print(f"流式生成失败: {e}")
            return None
    
    def _build_question_prompt(self, idiom: str, question_type: str) -> str:
        """构建出题提示词"""
        type_instructions = {
            "story": "请用一个生动的小故事来描述这个成语的含义，但不要直接说出成语本身",
            "antonym": "请描述与这个成语意思相反的概念或行为",
            "allusion": "请简单提及这个成语的典故来源，但不要直接说出成语",
            "literal": "请解释这个成语中部分字的字面意思，让人能够联想到整个成语",
            "riddle": "请以谜语的形式给出提示",
            "synonym": "请用意思相近的词语或短语来描述",
            "usage": "请描述在什么情况下会用到这个成语"
        }
        
        instruction = type_instructions.get(question_type, type_instructions["story"])
        
        return f"""
你是一个成语猜多多游戏的出题机器人。请为成语"{idiom}"出一道题。

要求：
1. {instruction}
2. 题目要有趣且富有启发性
3. 难度适中，不要太简单也不要太难
4. 不要在题目中直接包含成语的任何一个字
5. 题目长度控制在50-100字之间

请直接输出题目内容，不要包含其他解释。
"""
    
    def _build_check_prompt(self, question: str, answer: str, correct_idiom: str) -> str:
        """构建答案检查提示词"""
        return f"""
你是一个成语猜多多游戏的判题机器人。

题目：{question}
标准答案：{correct_idiom}
玩家答案：{answer}

请判断玩家答案是否正确，并给出相应的反馈。

判断规则：
1. 如果答案完全正确，返回格式：正确|恭喜你，答案正确！正是'{correct_idiom}'。
2. 如果答案错误，返回格式：错误|很遗憾，答案错误。再仔细想想吧。
3. 如果答案接近正确（如同义词、近义词），返回格式：错误|答案很接近了，但不完全正确。再想想吧。

请严格按照上述格式返回，用"|"分隔判断结果和反馈信息。
"""
    
    def _build_hint_prompt(self, question: str, correct_idiom: str) -> str:
        """构建提示提示词"""
        return f"""
你是一个成语猜多多游戏的提示机器人。

题目：{question}
正确答案：{correct_idiom}

请给出一个有用的提示，帮助玩家猜出正确答案。

提示要求：
1. 不要直接说出成语
2. 可以提供成语的部分信息，如：
   - 成语的字数
   - 成语中某个字的提示
   - 成语的押韵或结构特点
   - 成语的情感色彩
3. 提示要简洁明了，30字以内

请直接输出提示内容。
"""
    
    def _extract_question_from_response(self, response: str) -> str:
        """从API响应中提取问题"""
        # 清理响应文本
        question = response.strip()
        # 移除可能的引号
        question = question.strip('"').strip("'")
        return question
    
    def _extract_check_result_from_response(self, response: str) -> Dict[str, Any]:
        """从API响应中提取检查结果"""
        try:
            # 尝试解析格式：正确|反馈信息
            if "|" in response:
                parts = response.split("|", 1)
                is_correct = parts[0].strip() == "正确"
                message = parts[1].strip()
            else:
                # 如果格式不对，尝试从内容判断
                is_correct = "正确" in response or "恭喜" in response
                message = response.strip()
            
            return {
                "correct": is_correct,
                "message": message
            }
        except Exception:
            # 如果解析失败，返回错误
            return {
                "correct": False,
                "message": "答案检查出现错误，请重试。"
            }
    
    def _extract_hint_from_response(self, response: str) -> str:
        """从API响应中提取提示"""
        return response.strip()
    
    def _generate_fallback_question(self) -> str:
        """生成备用问题（当API不可用时）"""
        fallback_questions = [
            {
                "question": "形容做事多此一举，反而坏事的成语是什么？（提示：关于蛇的故事）",
                "answer": "画蛇添足"
            },
            {
                "question": "形容因为看到类似的东西而产生不必要的恐惧的成语是什么？（提示：杯子里的影子）",
                "answer": "杯弓蛇影"
            },
            {
                "question": "形容事情出了问题才去想办法补救的成语是什么？（提示：羊跑了之后）",
                "answer": "亡羊补牢"
            },
            {
                "question": "形容不劳而获，等待机会的成语是什么？（提示：等在树桩旁）",
                "answer": "守株待兔"
            },
            {
                "question": "形容做事方法不对，无法成功的成语是什么？（提示：在船上做记号）",
                "answer": "刻舟求剑"
            },
            {
                "question": "形容自欺欺人，掩盖真相的成语是什么？（提示：捂住耳朵）",
                "answer": "掩耳盗铃"
            },
            {
                "question": "形容因小失大，舍本逐末的成语是什么？（提示：珠子和盒子）",
                "answer": "买椟还珠"
            },
            {
                "question": "形容方向完全错误，无法达到目的的成语是什么？（提示：南辕北辙）",
                "answer": "南辕北辙"
            },
            {
                "question": "形容盲目模仿别人，结果失去自我的成语是什么？（提示：学走路的故事）",
                "answer": "邯郸学步"
            },
            {
                "question": "形容装模作样，假装喜欢的成语是什么？（提示：某位先生喜欢龙）",
                "answer": "叶公好龙"
            },
            {
                "question": "形容虚假的利益诱惑的成语是什么？（提示：画出来的饼）",
                "answer": "画饼充饥"
            },
            {
                "question": "形容安于现状，眼界狭小的成语是什么？（提示：井底的动物）",
                "answer": "井底之蛙"
            },
            {
                "question": "形容事物变化无常的成语是什么？（提示：早上三个晚上四个）",
                "answer": "朝三暮四"
            },
            {
                "question": "形容在众人面前卖弄本领的成语是什么？（提示：在鲁班门前）",
                "answer": "班门弄斧"
            },
            {
                "question": "形容没有真本领却混在行家里面的成语是什么？（提示：吹竽的故事）",
                "answer": "滥竽充数"
            }
        ]
        
        selected = random.choice(fallback_questions)
        self.current_idiom = selected["answer"]
        return selected["question"]
    
    def _check_answer_fallback(self, question: str, answer: str) -> Dict[str, Any]:
        """备用答案检查"""
        if self.current_idiom and answer.strip() == self.current_idiom:
            return {
                "correct": True,
                "message": f"恭喜你，答案正确！正是'{self.current_idiom}'。"
            }
        else:
            return {
                "correct": False,
                "message": "很遗憾，答案错误。再仔细想想吧。"
            }
    
    def _generate_fallback_hint(self) -> str:
        """生成备用提示"""
        if self.current_idiom:
            return f"提示：这是一个{len(self.current_idiom)}字成语，第一个字是'{self.current_idiom[0]}'。"
        return "提示：这是一个常见的四字成语。"
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        if not self.is_online_mode():
            return {
                "status": "离线模式",
                "model": "本地问题库",
                "sdk_version": "N/A"
            }
        
        try:
            # 获取可用的模型列表
            if genai is not None:
                models = list(genai.list_models())
                return {
                    "status": "在线模式",
                    "model": "gemini-1.5-flash-latest",
                    "sdk_version": getattr(genai, '__version__', 'Unknown'),
                    "available_models": len(models)
                }
            else:
                return {
                    "status": "错误",
                    "error": "genai 未初始化"
                }
        except Exception as e:
            return {
                "status": "错误",
                "error": str(e)
            }
    
    def get_action(self, observation, env):
        """实现BaseAgent的抽象方法（游戏中不会用到）"""
        return None 