#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立的Bedrock客户端
避免启动交互模式
"""

import json
import boto3
import os
from typing import Dict, Any, Optional

class SafeBedrockClient:
    """安全的Bedrock客户端，避免启动交互模式"""
    
    def __init__(self, model_path: str, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0", 
                 aws_region: str = "us-east-1"):
        self.model_path = model_path
        self.model_id = model_id
        self.aws_region = aws_region
        self.bedrock_runtime = None
        
    def _init_client(self):
        """初始化Bedrock客户端"""
        if self.bedrock_runtime is None:
            self.bedrock_runtime = boto3.client(
                service_name='bedrock-runtime', 
                region_name=self.aws_region
            )
    
    def _define_body(self, text: str) -> Dict[str, Any]:
        """构造请求体，避免导入app.py"""
        model_provider = self.model_id.split('.')[0]
        
        if model_provider == 'anthropic':
            if 'claude-3' in self.model_id:
                # 使用成语猜谜专用的系统提示
                system_message = '''
你是一个成语猜谜游戏大师。你的任务是：

【出题模式】
- 当用户要求出题时，生成成语谜题
- 输出格式：成语：xxxx；描述：xxxx
- 重要：必须同时提供成语和描述！
- 只出四字成语，不要出其他类型的词语
- 避免使用"守株待兔""画龙点睛"等高频成语
- 保证成语多样性，避免重复
- 题目描述要生动有趣，便于猜测

【判断答案模式】
- 当用户提供答案时，判断是否正确
- 严格按照以下格式回复：
  判断：[正确/错误]
  理由：[详细说明判断依据]
  鼓励：[给玩家的鼓励或建议]
- 重要：只判断用户提供的答案，不要自己生成新的成语！
- 如果用户答案与正确答案不完全一致，必须回复"错误"
- 不要添加任何额外的成语或答案
- 不要泄露正确答案

【提示模式】
- 当用户要求提示时，给出与谜底相关的隐晦线索
- 不要直接给出答案
- 提示要简洁有用
- 不要泄露完整答案

关键规则：
1. 在判断答案时，只判断用户提供的答案，不要生成新的成语
2. 严格按照指定格式回复
3. 不要添加任何额外的内容
4. 出题时必须同时提供成语和描述
5. 只出四字成语
'''
                
                return {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "system": system_message,
                    "messages": [
                        {
                            "role": "user",
                            "content": text
                        }
                    ]
                }
            else:
                return {
                    "prompt": f'\n\nHuman: {text}\n\nAssistant:',
                    "max_tokens": 1000
                }
        else:
            raise Exception(f'不支持的模型提供商: {model_provider}')
    
    def _get_stream_text(self, chunk: Dict[str, Any]) -> str:
        """从响应块中提取文本"""
        model_provider = self.model_id.split('.')[0]
        
        if model_provider == 'anthropic':
            if 'claude-3' in self.model_id:
                chunk_obj = json.loads(chunk.get('bytes').decode())
                if chunk_obj['type'] == 'content_block_delta':
                    if chunk_obj['delta']['type'] == 'text_delta':
                        return chunk_obj['delta']['text']
            else:
                chunk_obj = json.loads(chunk.get('bytes').decode())
                return chunk_obj['completion']
        
        return ""
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        try:
            self._init_client()
            
            # 构造请求体
            body = self._define_body(prompt)
            body_json = json.dumps(body)
            
            # 发送请求
            response = self.bedrock_runtime.invoke_model_with_response_stream(
                body=body_json,
                modelId=self.model_id,
                accept='application/json',
                contentType='application/json'
            )
            
            # 处理响应流
            bedrock_stream = response.get('body')
            if bedrock_stream:
                full_response = ""
                for event in bedrock_stream:
                    chunk = event.get('chunk')
                    if chunk:
                        text = self._get_stream_text(chunk)
                        if text:
                            full_response += text
                
                return full_response.strip()
            else:
                raise Exception("未收到有效响应")
                
        except Exception as e:
            raise Exception(f"Bedrock模型调用失败: {str(e)}")
    
    def is_available(self) -> bool:
        """检查模型是否可用"""
        try:
            test_response = self.generate_text("测试", max_tokens=10)
            return len(test_response) > 0
        except:
            return False 