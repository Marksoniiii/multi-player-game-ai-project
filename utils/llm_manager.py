#!/usr/bin/env python3
"""
LLM管理器
统一管理多种大语言模型的接入
"""

import json
import time
import random
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import requests
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
            
            url = f"{self.base_url}/gemini-2.5-flash:generateContent"
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
    """阿里千问客户端"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
    def generate_text(self, prompt: str, **kwargs) -> str:
        """调用千问API生成文本"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}"
            }
            
            # 增加随机性参数
            data = {
                "model": self.config.model_name or "qwen-max",
                "input": {
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                "parameters": {
                    "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                    "temperature": kwargs.get("temperature", 0.9),  # 增加随机性
                    "top_p": kwargs.get("top_p", 0.95),  # 增加多样性
                    "top_k": kwargs.get("top_k", 30),   # 降低top_k增加随机性
                    "repetition_penalty": kwargs.get("repetition_penalty", 1.5),  # 进一步增加重复惩罚
                    "enable_search": False,
                    "incremental_output": False,
                    "do_sample": True,  # 确保采样模式
                    "seed": kwargs.get("seed", random.randint(1, 1000000))  # 随机种子
                }
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if "output" in result and "text" in result["output"]:
                    return result["output"]["text"]
                else:
                    raise Exception("API返回格式错误")
            else:
                raise Exception(f"API调用失败: {response.status_code}, {response.text}")
                
        except Exception as e:
            raise Exception(f"千问API调用失败: {str(e)}")
    
    def is_available(self) -> bool:
        """检查千问是否可用"""
        try:
            test_response = self.generate_text("测试", max_tokens=10)
            return len(test_response) > 0
        except:
            return False


class SimulatorClient(BaseLLMClient):
    """模拟器客户端（用于测试）"""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        # 预置一些成语和描述
        self.idiom_database = {
            "画蛇添足": "做了多余的事情，反而坏了事。古代有人画蛇比赛，有人给蛇画了脚，结果失败了。",
            "守株待兔": "死守陈规，不知变通。比喻不主动努力，只想侥幸成功。",
            "亡羊补牢": "羊丢了再去修补羊圈，还不算晚。比喻出了问题后想办法补救。",
            "刻舟求剑": "船已经走了，还在船上刻记号找掉到水里的剑。比喻观念陈旧，不知变通。",
            "买椟还珠": "买了装珠宝的盒子，却把真正的珠宝退还了。比喻只注重外表，不重视实质。",
            "杯弓蛇影": "看到酒杯里的弓影，以为是蛇。比喻疑神疑鬼，自相惊扰。",
            "掩耳盗铃": "偷铃铛的人用手捂住自己的耳朵，以为别人听不见。比喻自欺欺人。",
            "南辕北辙": "要去南方却向北走。比喻行动和目的相反。",
            "坐井观天": "坐在井里看天空。比喻见识狭小，眼界有限。",
            "叶公好龙": "叶公喜欢龙，但真龙来了却吓跑了。比喻口头上说爱好某样东西，实际上并不真爱好。",
            "东施效颦": "东施模仿西施皱眉，反而更丑了。比喻模仿别人不得其法，反而弄巧成拙。",
            "塞翁失马": "边塞老人失去了马，但后来证明是好事。比喻一时的得失很难确定最终的好坏。",
            "狐假虎威": "狐狸借着老虎的威势吓唬其他动物。比喻依仗别人的势力欺压人。",
            "愚公移山": "愚公不怕困难，挖山不止，最终感动了上帝。比喻有恒心有毅力。",
            "精卫填海": "精卫鸟不断衔石子填海。比喻意志坚定，不怕困难。",
            "破釜沉舟": "砸烂锅子，凿沉船只。比喻决心很大，誓死一战。",
            "卧薪尝胆": "睡在柴草上，品尝苦胆。比喻刻苦自励，发奋图强。",
            "闻鸡起舞": "听到鸡叫就起床练武。比喻有志报国的人及时奋起。",
            "悬梁刺股": "头发悬在梁上，用锥子刺大腿。比喻刻苦学习。",
            "凿壁偷光": "凿穿墙壁引光线。比喻家贫而读书勤奋。"
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
        idiom = random.choice(list(self.idiom_database.keys()))
        description = self.idiom_database[idiom]
        
        # 随机选择出题方式
        question_types = [
            f"请根据以下描述猜成语：{description}",
            f"这个成语的意思是：{description}。请问是什么成语？",
            f"有一个成语，它的含义是{description}，请猜一猜。",
            f"题目：{description}这是哪个成语的意思？"
        ]
        
        # 构造完整的出题响应，包含答案信息
        question_text = random.choice(question_types)
        return f"成语：{idiom}\n描述：{question_text}"
    
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
            "qianwen": "阿里千问2.5Max",
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
                model_name=kwargs.get("model_name", ""),
                max_tokens=kwargs.get("max_tokens", 2000),
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