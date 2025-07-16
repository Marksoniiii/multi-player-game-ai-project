# Amazon Bedrock Voice Conversation 配置指南

## 概述

本指南专门针对Amazon Bedrock Voice Conversation项目在成语猜多游戏中的集成配置。该项目提供了与AWS Bedrock服务的语音对话功能，可以用于生成成语题目和判断答案。

## 项目结构

Amazon Bedrock Voice Conversation项目包含以下关键文件：

- **`app.py`**: 主应用程序，处理语音对话
- **`api_request_schema.py`**: 定义Bedrock模型的API请求模式
- **`fine_tunning_data.py`**: 包含系统提示词和对话历史
- **`requirements.txt`**: Python依赖库
- **`README.md`**: 项目说明文档

## 配置步骤

### 1. 环境准备

#### 安装Python依赖
```bash
cd D:\amazon-bedrock-voice-conversation
pip install -r requirements.txt
```

#### 安装boto3（如果未安装）
```bash
pip install boto3
```

### 2. AWS凭证配置

#### 方法1：环境变量（推荐）
```bash
# Windows PowerShell
$env:AWS_ACCESS_KEY_ID="your-access-key-id"
$env:AWS_SECRET_ACCESS_KEY="your-secret-access-key"
$env:AWS_DEFAULT_REGION="us-east-1"
$env:MODEL_ID="amazon.titan-text-express-v1"

# Windows CMD
set AWS_ACCESS_KEY_ID=your-access-key-id
set AWS_SECRET_ACCESS_KEY=your-secret-access-key
set AWS_DEFAULT_REGION=us-east-1
set MODEL_ID=amazon.titan-text-express-v1
```

#### 方法2：AWS配置文件
```bash
# 创建或编辑 ~/.aws/credentials
[default]
aws_access_key_id = your-access-key-id
aws_secret_access_key = your-secret-access-key

# 创建或编辑 ~/.aws/config
[default]
region = us-east-1
```

### 3. 在成语猜多游戏中配置

1. 启动成语猜多游戏
2. 点击"设置"按钮
3. 在"语言模型选择"中选择"本地模型"
4. 填写配置：
   - **模型路径**: `D:\amazon-bedrock-voice-conversation`
   - **API端点**: 留空
5. 点击"应用设置"

### 4. 测试配置

运行测试脚本验证配置：
```bash
python local_model_example.py
```

## 支持的Bedrock模型

### 文本生成模型
- `amazon.titan-text-express-v1` (默认)
- `amazon.titan-text-lite-v1`
- `anthropic.claude-3-sonnet-20240229-v1:0`
- `anthropic.claude-3-haiku-20240307-v1:0`
- `meta.llama2-13b-chat-v1`
- `meta.llama2-70b-chat-v1`

### 配置模型
在 `api_request_schema.py` 中可以查看和修改每个模型的默认参数：

```python
def get_model_request_schema(model_id):
    if model_id == "amazon.titan-text-express-v1":
        return {
            "modelId": "amazon.titan-text-express-v1",
            "contentType": "application/json",
            "accept": "application/json",
            "body": json.dumps({
                "inputText": "Hello, how are you?",
                "textGenerationConfig": {
                    "maxTokenCount": 512,
                    "temperature": 0.7,
                    "topP": 0.9,
                    "stopSequences": []
                }
            })
        }
```

## 自定义配置

### 1. 修改系统提示词

编辑 `fine_tunning_data.py` 文件中的 `get_system_prompt()` 函数：

```python
def get_system_prompt():
    return """你是一个专业的成语猜多游戏助手。你的任务是：
1. 生成有趣的成语题目
2. 判断玩家的答案是否正确
3. 提供有用的提示

请确保：
- 题目描述清晰易懂
- 答案准确无误
- 提示有帮助但不直接给出答案
"""
```

### 2. 调整模型参数

在 `api_request_schema.py` 中修改模型参数：

```python
"textGenerationConfig": {
    "maxTokenCount": 1000,  # 增加最大token数
    "temperature": 0.8,      # 增加创造性
    "topP": 0.95,           # 增加多样性
    "stopSequences": ["用户:", "助手:"]  # 添加停止序列
}
```

### 3. 添加对话历史

在 `fine_tunning_data.py` 中实现对话历史管理：

```python
def get_conversation_history():
    return [
        {"role": "user", "content": "请出一道成语题目"},
        {"role": "assistant", "content": "成语：画蛇添足\n描述：做了多余的事情，反而坏了事。"}
    ]
```

## 故障排除

### 1. AWS凭证错误
```
错误：botocore.exceptions.NoCredentialsError
解决：检查AWS凭证配置是否正确
```

### 2. 模型访问权限错误
```
错误：botocore.exceptions.ClientError: An error occurred (AccessDeniedException)
解决：确保AWS账户已启用Bedrock模型访问权限
```

### 3. 区域错误
```
错误：botocore.exceptions.ClientError: An error occurred (ValidationException)
解决：检查AWS_DEFAULT_REGION设置，确保模型在该区域可用
```

### 4. 模型ID错误
```
错误：botocore.exceptions.ClientError: An error occurred (ResourceNotFoundException)
解决：检查MODEL_ID是否正确，确保模型在AWS账户中已启用
```

## 性能优化

### 1. 减少延迟
- 使用AWS Lambda函数缓存模型响应
- 启用Bedrock的流式响应
- 使用更近的AWS区域

### 2. 成本优化
- 选择合适的模型大小
- 调整maxTokenCount参数
- 使用缓存减少重复请求

### 3. 错误处理
- 实现重试机制
- 添加降级到备用模型的逻辑
- 记录详细的错误日志

## 高级功能

### 1. 多模型支持
```python
# 在环境变量中设置不同的模型
export MODEL_ID="anthropic.claude-3-sonnet-20240229-v1:0"
```

### 2. 流式响应
```python
# 启用流式响应以提供更好的用户体验
response = bedrock.invoke_model_with_response_stream(
    modelId=model_id,
    contentType=content_type,
    accept=accept,
    body=body
)
```

### 3. 批量处理
```python
# 批量处理多个请求以提高效率
def batch_generate_text(prompts, max_tokens=1000):
    responses = []
    for prompt in prompts:
        response = generate_text(prompt, max_tokens)
        responses.append(response)
    return responses
```

## 监控和日志

### 1. 启用CloudWatch日志
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_text(prompt, max_tokens=2000, temperature=0.7):
    logger.info(f"生成文本请求: {prompt[:100]}...")
    # ... 生成逻辑
    logger.info(f"生成完成，长度: {len(response)}")
    return response
```

### 2. 性能监控
```python
import time

def generate_text_with_monitoring(prompt, **kwargs):
    start_time = time.time()
    response = generate_text(prompt, **kwargs)
    end_time = time.time()
    
    logger.info(f"请求耗时: {end_time - start_time:.2f}秒")
    return response
```

## 安全考虑

### 1. 凭证安全
- 不要在代码中硬编码AWS凭证
- 使用IAM角色而不是访问密钥
- 定期轮换访问密钥

### 2. 输入验证
```python
def validate_prompt(prompt):
    if len(prompt) > 10000:
        raise ValueError("提示词过长")
    if not prompt.strip():
        raise ValueError("提示词不能为空")
    return prompt
```

### 3. 输出过滤
```python
def filter_response(response):
    # 过滤不适当的内容
    inappropriate_words = ["不当词汇"]
    for word in inappropriate_words:
        if word in response:
            return "抱歉，无法生成相关内容。"
    return response
```

## 联系支持

如果遇到问题：
1. 检查AWS Bedrock服务状态
2. 查看CloudWatch日志
3. 参考AWS Bedrock文档
4. 联系AWS支持团队 