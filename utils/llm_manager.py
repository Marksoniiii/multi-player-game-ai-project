#!/usr/bin/env python3
"""
LLM管理器
统一管理多种大语言模型的接入
"""

import json
import time
import random
import os
import subprocess
import requests
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """LLM配置"""
    model_type: str
    api_key: str
    base_url: str = ""
    model_name: str = ""
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 30


class BaseLLMClient(ABC):
    """LLM客户端基类"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.model_type = config.model_type
        
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """检查模型是否可用"""
        pass





class GeminiClient(BaseLLMClient):
    """Google Gemini客户端"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
    def generate_text(self, prompt: str, **kwargs) -> str:
        """调用Gemini API生成文本"""
        try:
            if not self.config.api_key or self.config.api_key == "dummy_key":
                raise Exception("请配置有效的Gemini API密钥")
            
            url = f"{self.base_url}/gemini-2.0-flash:generateContent"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.config.api_key
            }
            
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "maxOutputTokens": kwargs.get("max_tokens", self.config.max_tokens),
                    "topP": kwargs.get("top_p", 0.8),
                    "topK": kwargs.get("top_k", 10)
                }
            }
            
            response = requests.post(
                url, 
                headers=headers, 
                json=data, 
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 检查是否有安全过滤或其他限制
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    
                    # 检查是否被安全过滤阻止
                    if "finishReason" in candidate and candidate["finishReason"] == "SAFETY":
                        raise Exception("内容被安全过滤阻止")
                    
                    if "content" in candidate and "parts" in candidate["content"]:
                        parts = candidate["content"]["parts"]
                        if len(parts) > 0 and "text" in parts[0]:
                            return parts[0]["text"]
                        else:
                            raise Exception(f"parts格式错误: {parts}")
                    else:
                        raise Exception(f"content格式错误: {candidate}")
                else:
                    raise Exception(f"API返回格式错误: {result}")
            else:
                error_msg = f"API调用失败: {response.status_code}"
                if response.status_code == 401:
                    error_msg += " - API密钥无效"
                elif response.status_code == 403:
                    error_msg += " - 权限不足或配额耗尽"
                elif response.status_code == 429:
                    error_msg += " - 请求过于频繁"
                else:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
                
        except Exception as e:
            raise Exception(f"Gemini API调用失败: {str(e)}")
    
    def is_available(self) -> bool:
        """检查Gemini是否可用"""
        try:
            if not self.config.api_key or self.config.api_key == "dummy_key":
                return False
            test_response = self.generate_text("测试", max_tokens=10)
            return len(test_response) > 0
        except:
            return False


class QianwenClient(BaseLLMClient):
    """阿里千问客户端 - 支持多轮对话"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.messages = []  # 存储对话历史
        
    def set_system_message(self, system_content: str):
        """设置系统消息"""
        self.messages = [{"role": "system", "content": system_content}]
        
    def add_user_message(self, content: str):
        """添加用户消息"""
        self.messages.append({"role": "user", "content": content})
        
    def add_assistant_message(self, content: str):
        """添加助手消息"""
        self.messages.append({"role": "assistant", "content": content})
        
    def clear_history(self):
        """清空对话历史（保留系统消息）"""
        system_msg = None
        for msg in self.messages:
            if msg["role"] == "system":
                system_msg = msg
                break
        self.messages = [system_msg] if system_msg else []
        
    def get_conversation_history(self):
        """获取对话历史"""
        return self.messages.copy()
        
    def generate_text(self, prompt: str, **kwargs) -> str:
        """调用千问API生成文本 - 支持多轮对话"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}"
            }

            # 如果没有对话历史，使用单轮对话模式
            if not self.messages:
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            else:
                # 多轮对话模式：将当前prompt添加到对话历史
                messages = self.messages.copy()
                messages.append({"role": "user", "content": prompt})

            data = {
                "model": self.config.model_name or "qwen-plus",
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", 0.95),
                "stream": False
            }

            # 构建完整的URL
            url = f"{self.base_url}/chat/completions"

            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=60  # 增加超时时间到60秒
            )

            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        response_content = choice["message"]["content"]
                        
                        # 如果使用多轮对话模式，自动更新对话历史
                        if self.messages:
                            self.messages.append({"role": "user", "content": prompt})
                            self.messages.append({"role": "assistant", "content": response_content})
                        
                        return response_content
                    else:
                        raise Exception(f"响应格式错误: {choice}")
                else:
                    raise Exception(f"API返回格式错误: {result}")
            else:
                error_msg = f"API调用失败: {response.status_code}"
                if response.status_code == 401:
                    error_msg += " - API密钥无效"
                elif response.status_code == 403:
                    error_msg += " - 权限不足或配额耗尽"
                elif response.status_code == 429:
                    error_msg += " - 请求过于频繁"
                else:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)

        except requests.exceptions.Timeout:
            raise Exception("请求超时，请检查API设置或增加超时时间")
        except Exception as e:
            raise Exception(f"千问API调用失败: {str(e)}")
    
    def is_available(self) -> bool:
        """检查千问是否可用"""
        try:
            if not self.config.api_key or self.config.api_key == "dummy_key":
                return False
            test_response = self.generate_text("测试", max_tokens=10)
            return len(test_response) > 0
        except:
            return False


class BedrockClient(BaseLLMClient):
    """Amazon Bedrock客户端"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.model_path = config.base_url  # 使用base_url字段存储模型路径
        self.model_id = config.model_name or "anthropic.claude-3-sonnet-20240229-v1:0"
        self.aws_region = config.api_key or "us-east-1"  # 使用api_key字段存储AWS区域
        
    def generate_text(self, prompt: str, **kwargs) -> str:
        """调用Amazon Bedrock模型生成文本"""
        try:
            # 使用安全的Bedrock客户端
            from utils.bedrock_client import SafeBedrockClient
            
            # 创建安全的Bedrock客户端
            bedrock_client = SafeBedrockClient(
                model_path=self.model_path,
                model_id=self.model_id,
                aws_region=self.aws_region
            )
            
            # 生成文本
            return bedrock_client.generate_text(prompt, **kwargs)
                
        except Exception as e:
            raise Exception(f"Bedrock模型调用失败: {str(e)}")
    
    def is_available(self) -> bool:
        """检查Bedrock模型是否可用"""
        try:
            # 尝试生成测试文本
            test_response = self.generate_text("测试", max_tokens=10)
            return len(test_response) > 0
        except:
            return False


class SimulatorClient(BaseLLMClient):
    """模拟器客户端（用于测试）"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.used_idioms = set()  # 跟踪已使用的成语
        # 预置一些成语和描述（已清理，避免暴露成语中的字）
        self.idiom_database = {
            "画蛇添足": "做了多余的事情，反而坏了事。古代有人描绘爬行动物比赛，有人给爬行动物增加了脚，结果失败了。",
            "守株待兔": "死守陈规，不知变通。比喻不主动努力，只想侥幸成功。",
            "亡羊补牢": "家畜丢失了再去修补围栏，还不算晚。比喻出了问题后想办法补救。",
            "刻舟求剑": "船只已经走了，还在船只上雕刻记号寻找掉到水里的武器。比喻观念陈旧，不知变通。",
            "买椟还珠": "购买了装珍宝的容器，却把真正的珍宝归还了。比喻只注重外表，不重视实质。",
            "杯弓蛇影": "看到容器里的武器影子，以为是爬行动物。比喻疑神疑鬼，自相惊扰。",
            "掩耳盗铃": "偷响器的人用手遮盖自己的听觉器官，以为别人听不见。比喻自欺欺人。",
            "南辕北辙": "要去南方却向北方走。比喻行动和目的相反。",
            "坐井观天": "坐在水井里看天空。比喻见识狭小，眼界有限。",
            "叶公好龙": "叶先生喜欢神兽，但真神兽来了却吓跑了。比喻口头上说爱好某样东西，实际上并不真爱好。",
            "东施效颦": "东施模仿西施皱眉，反而更丑了。比喻模仿别人不得其法，反而弄巧成拙。",
            "塞翁失马": "边塞老人失去了坐骑，但后来证明是好事。比喻一时的得失很难确定最终的好坏。",
            "狐假虎威": "狐狸借着猛兽的威势吓唬其他动物。比喻依仗别人的势力欺压人。",
            "愚公移山": "愚先生不怕困难，移动山峰不止，最终感动了上帝。比喻有恒心有毅力。",
            "精卫填海": "精卫鸟不断衔石子填塞海洋。比喻意志坚定，不怕困难。",
            "破釜沉舟": "打破锅子，凿沉船只。比喻决心很大，誓死一战。",
            "卧薪尝胆": "睡在柴草上，品尝苦胆。比喻刻苦自励，发奋图强。",
            "闻鸡起舞": "听到家禽叫就起床跳舞。比喻有志报国的人及时奋起。",
            "悬梁刺股": "头发悬挂在房梁上，用锥子刺穿大腿。比喻刻苦学习。",
            "凿壁偷光": "凿穿墙壁偷取光线。比喻家贫而读书勤奋。",
            "一帆风顺": "比喻事情进行得很顺利，就像船帆满涨，船只行驶顺利一般。形容事情发展顺利，没有阻碍。"
        }
        
    def generate_text(self, prompt: str, **kwargs) -> str:
        """模拟生成文本"""
        time.sleep(0.5)  # 模拟网络延迟
        
        # 如果是出题请求
        if "出题" in prompt or "成语" in prompt:
            return self._generate_question()
        
        # 如果是判断答案请求
        if "判断" in prompt or "答案" in prompt:
            return self._judge_answer(prompt)
        
        # 如果是提示请求
        if "提示" in prompt or "hint" in prompt.lower():
            return self._generate_hint(prompt)
        
        # 默认回复
        return "我是模拟的语言模型，正在为您服务。"
    
    def _generate_question(self) -> str:
        """生成成语题目"""
        # 获取未使用的成语
        available_idioms = [idiom for idiom in self.idiom_database.keys() if idiom not in self.used_idioms]
        
        # 如果所有成语都用过了，重置已使用列表
        if not available_idioms:
            self.used_idioms.clear()
            available_idioms = list(self.idiom_database.keys())
        
        # 选择一个未使用的成语
        idiom = random.choice(available_idioms)
        self.used_idioms.add(idiom)
        
        description = self.idiom_database[idiom]
        
        # 检查描述是否包含成语中的字，如果包含则重新生成描述
        clean_description = self._clean_description(idiom, description)
        
        # 随机选择出题方式
        question_types = [
            f"请根据以下描述猜成语：{clean_description}",
            f"这个成语的意思是：{clean_description}。请问是什么成语？",
            f"有一个成语，它的含义是{clean_description}，请猜一猜。",
            f"题目：{clean_description}这是哪个成语的意思？"
        ]
        
        # 构造完整的出题响应，包含答案信息
        question_text = random.choice(question_types)
        return f"成语：{idiom}\n描述：{question_text}"
    
    def _clean_description(self, idiom: str, description: str) -> str:
        """清理描述，避免暴露成语中的字"""
        # 将成语拆分成单个字符
        idiom_chars = list(idiom)
        
        # 检查描述中是否包含成语中的字
        for char in idiom_chars:
            if char in description:
                # 如果包含，尝试用同义词替换或重新描述
                description = self._replace_char_in_description(char, description)
        
        return description
    
    def _replace_char_in_description(self, char: str, description: str) -> str:
        """替换描述中的特定字符"""
        # 定义一些替换规则
        replacements = {
            "一": "某个",
            "帆": "船帆",
            "风": "气流",
            "顺": "顺利",
            "画": "描绘",
            "蛇": "爬行动物",
            "添": "增加",
            "足": "脚",
            "守": "等待",
            "株": "树桩",
            "待": "等待",
            "兔": "小动物",
            "亡": "丢失",
            "羊": "家畜",
            "补": "修理",
            "牢": "围栏",
            "刻": "雕刻",
            "舟": "船只",
            "求": "寻找",
            "剑": "武器",
            "买": "购买",
            "椟": "盒子",
            "还": "归还",
            "珠": "珍宝",
            "杯": "容器",
            "弓": "武器",
            "影": "影子",
            "掩": "遮盖",
            "耳": "听觉器官",
            "盗": "偷窃",
            "铃": "响器",
            "南": "南方",
            "辕": "车辕",
            "北": "北方",
            "辙": "车辙",
            "坐": "坐着",
            "井": "水井",
            "观": "观看",
            "天": "天空",
            "叶": "叶子",
            "公": "先生",
            "好": "喜欢",
            "龙": "神兽",
            "东": "东方",
            "施": "人名",
            "效": "模仿",
            "颦": "皱眉",
            "塞": "边塞",
            "翁": "老人",
            "失": "丢失",
            "马": "坐骑",
            "狐": "狐狸",
            "假": "借助",
            "虎": "猛兽",
            "威": "威势",
            "愚": "愚笨",
            "公": "先生",
            "移": "移动",
            "山": "山峰",
            "精": "精神",
            "卫": "守卫",
            "填": "填塞",
            "海": "海洋",
            "破": "打破",
            "釜": "锅子",
            "沉": "沉没",
            "舟": "船只",
            "卧": "躺着",
            "薪": "柴草",
            "尝": "品尝",
            "胆": "苦胆",
            "闻": "听到",
            "鸡": "家禽",
            "起": "起床",
            "舞": "跳舞",
            "悬": "悬挂",
            "梁": "房梁",
            "刺": "刺穿",
            "股": "大腿",
            "凿": "凿穿",
            "壁": "墙壁",
            "偷": "偷取",
            "光": "光线"
        }
        
        # 如果字符在替换规则中，使用替换词
        if char in replacements:
            return description.replace(char, replacements[char])
        
        # 如果没有替换规则，尝试用更通用的描述
        return description.replace(char, "某个字")
    
    def _judge_answer(self, prompt: str) -> str:
        """判断答案"""
        # 从提示词中提取用户答案和正确答案进行比较
        if "用户答案：" in prompt and "正确答案：" in prompt:
            try:
                lines = prompt.split('\n')
                user_answer = ""
                correct_answer = ""
                
                for line in lines:
                    if "用户答案：" in line:
                        user_answer = line.split("用户答案：")[-1].strip()
                    elif "正确答案：" in line:
                        correct_answer = line.split("正确答案：")[-1].strip()
                
                is_correct = user_answer.strip() == correct_answer.strip()
                
                if is_correct:
                    return "判断：正确\n理由：答案完全匹配\n鼓励：太棒了！回答正确！"
                else:
                    return f"判断：错误\n理由：正确答案是{correct_answer}，你的答案是{user_answer}\n鼓励：别灰心，继续加油！"
                    
            except Exception as e:
                return "判断：错误\n理由：无法解析答案\n鼓励：请重新尝试！"
        else:
            # 简单的关键词判断
            if "正确" in prompt or "对" in prompt:
                return "判断：正确\n理由：答案正确\n鼓励：恭喜你，回答正确！"
            else:
                return "判断：错误\n理由：答案不正确\n鼓励：很遗憾，回答错误。再试试吧。"
    
    def _generate_hint(self, prompt: str) -> str:
        """生成提示"""
        # 简单的提示逻辑
        hints = [
            "提示：这个成语包含四个字",
            "提示：这个成语来自古代典故",
            "提示：这个成语常用来比喻某种行为",
            "提示：这个成语的第一个字可能是动作",
            "提示：这个成语描述的是一种状态或情况"
        ]
        
        hint_text = random.choice(hints)
        
        return f"{hint_text}\n解释：这是一个通用提示，可以帮助你思考"
    
    def is_available(self) -> bool:
        """模拟器始终可用"""
        return True


class LLMManager:
    """LLM管理器"""
    
    def __init__(self):
        self.clients = {}
        self.current_client = None
        self.available_models = {
            "gemini": "Google Gemini",
            "qianwen": "千问",
            "bedrock": "Amazon Bedrock",
            "simulator": "模拟器（测试用）"
        }
        # 确保始终有一个可用的备用模型
        self.configure_model("simulator", "dummy_key")
    
    def configure_model(self, model_type: str, api_key: str, **kwargs) -> bool:
        """配置模型"""
        try:
            # 为千问设置更高的温度以增加随机性
            default_temperature = 0.9 if model_type == "qianwen" else 0.7

            config = LLMConfig(
                model_type=model_type,
                api_key=api_key,
                base_url=kwargs.get("base_url", ""),
                model_name=kwargs.get("model_name", "qwen-plus"),  # 默认使用 "qwen-plus" 模型
                max_tokens=kwargs.get("max_tokens", 2000),  # 使用较大的 max_tokens
                temperature=kwargs.get("temperature", default_temperature),
                timeout=kwargs.get("timeout", 30)
            )

            # 创建客户端
            if model_type == "gemini":
                client = GeminiClient(config)
            elif model_type == "qianwen":
                client = QianwenClient(config)
            elif model_type == "simulator":
                client = SimulatorClient(config)
            elif model_type == "bedrock":
                client = BedrockClient(config)
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")

            # 检查模型是否可用
            if model_type != "simulator" and not client.is_available():
                print(f"警告：{model_type} 模型不可用，可能是API密钥无效或网络问题")
                return False

            self.clients[model_type] = client

            # 如果是第一个配置的模型，自动设置为当前模型
            if self.current_client is None and model_type != "simulator":
                self.current_client = client

            return True

        except Exception as e:
            print(f"配置模型失败: {str(e)}")
            return False

    
    def set_current_model(self, model_type: str) -> bool:
        """设置当前使用的模型"""
        if model_type in self.clients:
            if not self.clients[model_type].is_available():
                print(f"警告：{model_type} 模型不可用，将使用备用模型")
                return False
            self.current_client = self.clients[model_type]
            return True
        return False
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        if self.current_client is None:
            if "simulator" in self.clients:
                print("警告：未配置LLM模型，使用备用模型")
                self.current_client = self.clients["simulator"]
            else:
                raise Exception("未配置任何可用的LLM模型")
        
        try:
            return self.current_client.generate_text(prompt, **kwargs)
        except Exception as e:
            print(f"当前模型 {self.current_client.model_type} 生成失败: {str(e)}")
            # 如果当前模型失败，尝试使用备用模型
            if self.current_client.model_type != "simulator" and "simulator" in self.clients:
                print("切换到备用模型")
                backup_client = self.clients["simulator"]
                return backup_client.generate_text(prompt, **kwargs)
            raise  # 如果没有备用模型，重新抛出异常
    
    def is_model_available(self, model_type: str) -> bool:
        """检查模型是否可用"""
        if model_type in self.clients:
            return self.clients[model_type].is_available()
        return False
    
    def get_available_models(self) -> Dict[str, str]:
        """获取可用模型列表"""
        return self.available_models
    
    def get_current_model(self) -> Optional[str]:
        """获取当前模型类型"""
        if self.current_client:
            return self.current_client.model_type
        return None


# 全局LLM管理器实例
llm_manager = LLMManager() 