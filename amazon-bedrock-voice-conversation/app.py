#导入必要的py模块
import json #JSON 处理模块
import os #系统相关模块
import time
import sys #系统相关模块
import boto3 #AWS 服务相关模块 是 Python 的 AWS SDK，用于与各种 AWS 服务进行交互
import threading

from api_request_schema import api_request_list, get_model_ids  #从api_request_schema模块导入api_request_list和get_model_ids

from fine_tunning_data import ft_data #用于大模型微调

# 获取环境变量MODEL_ID和AWS_REGION
model_id = os.getenv('MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0') #修改
aws_region = os.getenv('AWS_REGION', 'us-east-1')  

if model_id not in get_model_ids():
    print(f'Error: Models ID {model_id} in not a valid model ID. Set MODEL_ID env var to one of {get_model_ids()}.')
    sys.exit(0)

api_request = api_request_list[model_id] #根据model_id，从api_request_list中获取对应的 API 请求信息
config = {
    'log_level': 'none',  # One of: info, debug, none
    'region': aws_region, #AWS 区域，使用之前获取的aws_region
    'bedrock': {
        'api_request': api_request
    } #Amazon Bedrock 的配置信息，其中api_request为之前获取的对应模型的 API 请求信息
}

bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name=config['region'])

def printer(text, level):
    if config['log_level'] == 'info' and level == 'info':
        print(text)
    elif config['log_level'] == 'debug' and level in ['info', 'debug']:
        print(text)

#对此进行关于大模型的微调
class BedrockModelsWrapper:

    @staticmethod
    #define_body 根据配置模型的ID和不同模型构造适合该模型的API请求体
    def define_body(text):   #此处的text为用户输入的问题
        model_id = config['bedrock']['api_request']['modelId']  #从配置中获取模型ID
        model_provider = model_id.split('.')[0] #获取提供商
        body = config['bedrock']['api_request']['body'] #从配置中初始化基础请求体模板
        
        if model_provider == 'amazon':
            body['inputText'] = text
        elif model_provider == 'meta':
            if 'llama3' in model_id:
                body['prompt'] = f"""
                    <|begin_of_text|>  
                    <|start_header_id|>user<|end_header_id|>
                    {text},   
                    <|eot_id|>
                    <|start_header_id|>assistant<|end_header_id|>
                    """
            else: 
                body['prompt'] = f"<s>[INST] {text}, please output in Chinese. [/INST]"
        
        elif model_provider == 'anthropic':
            if 'claude-3' in model_id:
                # 读取所需要的微调数据
                # Claude3的message字段
                mesg = ft_data['anthropic']['claude-3']['messages']
                # Claude3的system字段
                system_mesg = ft_data['anthropic']['claude-3']['system']

                # 为了防止数据集中最后一个不是assistant
                if mesg[-1]['role'] == 'assistant':
                    mesg.append({
                        "role": "user",
                        "content": text  # text是define_body方法中的参数
                    })
                else:
                    mesg[-1]['content'] += text

                body['messages'] = mesg
                if system_mesg:  # 如果有system的字段，则在body的system字段中加入它
                    body['system'] = system_mesg
            else:
                body['prompt'] = f'\n\nHuman: {text}\n\nAssistant:'
        elif model_provider == 'cohere':
            body['prompt'] = text
        elif model_provider == 'mistral':
            body['prompt'] = f"<s>[INST] {text}, please output in Chinese. [/INST]"
        else:
            raise Exception('Unknown model provider.')

        return body

    @staticmethod
    def get_stream_chunk(event):
        return event.get('chunk')

    @staticmethod
    def get_stream_text(chunk):
        model_id = config['bedrock']['api_request']['modelId']
        model_provider = model_id.split('.')[0]

        chunk_obj = ''
        text = ''
        if model_provider == 'amazon':
            chunk_obj = json.loads(chunk.get('bytes').decode())
            text = chunk_obj['outputText']
        elif model_provider == 'meta':
            chunk_obj = json.loads(chunk.get('bytes').decode())
            text = chunk_obj['generation']
        elif model_provider == 'anthropic':
            if "claude-3" in model_id:
                chunk_obj = json.loads(chunk.get('bytes').decode())

                if chunk_obj['type'] == 'content_block_delta':
                    if chunk_obj['delta']['type'] == 'text_delta':
                        text = chunk_obj['delta']['text']
            else:
                #Claude2.x
                chunk_obj = json.loads(chunk.get('bytes').decode())
                text = chunk_obj['completion']
        elif model_provider == 'cohere':
            chunk_obj = json.loads(chunk.get('bytes').decode())
            text = ' '.join([c["text"] for c in chunk_obj['generations']])
        elif model_provider == 'mistral':
            chunk_obj = json.loads(chunk.get('bytes').decode())
            text = chunk_obj['outputs'][0]['text']
        else:
            raise NotImplementedError('Unknown model provider.')

        printer(f'[DEBUG] {chunk_obj}', 'debug')
        return text  #此处的text从用户提的问题转化成模型对这个问题的回答

# 简化的文本输出生成器，移除音频相关功能
def to_text_generator(bedrock_stream):
    code_block = False
    code_announced = False
    current_point = []  # 用于存储当前要点的文本

    if bedrock_stream:
        for event in bedrock_stream:
            chunk = BedrockModelsWrapper.get_stream_chunk(event)
            if chunk:
                text = BedrockModelsWrapper.get_stream_text(chunk)

                # 检测完整代码块标记
                if '```' in text:
                    if not code_block:  # 代码块开始
                        code_block = True
                        if current_point:
                            # 输出当前要点
                            point_text = ''.join(current_point)
                            if point_text.strip():
                                print(point_text, flush=True, end='')
                            current_point = []
                        if not code_announced:
                            print('（以下为示例代码）', end='', flush=True)
                            code_announced = True
                    else:  # 代码块结束
                        code_block = False
                        code_announced = False
                        print('\n（代码部分结束，继续讲解）', end='', flush=True)
                    continue  # 跳过标记本身

                if code_block:
                    # 在控制台显示代码
                    print(text, end='', flush=True)
                    continue

                # 按照句号对文本进行划分
                if '.' in text:
                    sentences = text.split('.')
                    for i, sentence in enumerate(sentences):
                        if i < len(sentences) - 1:
                            current_point.append(sentence + '. ')
                            point_text = ''.join(current_point)
                            if point_text.strip():
                                print(point_text, flush=True, end='')
                            current_point = []
                        else:
                            current_point.append(sentence)
                else:
                    current_point.append(text)

        if current_point:
            point_text = ''.join(current_point)
            if point_text.strip():
                print(point_text, flush=True, end='')
            current_point = []

        print('\n')

class BedrockWrapper:

    def __init__(self):
        self.speaking = False #初始化模型没有回复
    
    #检测模型是否正在回复
    def is_speaking(self):
        return self.speaking

    def invoke_bedrock(self, text):
        printer('[DEBUG] Bedrock generation started', 'debug')
        self.speaking = True

        body = BedrockModelsWrapper.define_body(text)
        printer(f"[DEBUG] Request body: {body}", 'debug')

        try:
            body_json = json.dumps(body)
            response = bedrock_runtime.invoke_model_with_response_stream(
                body=body_json,
                modelId=config['bedrock']['api_request']['modelId'],
                accept=config['bedrock']['api_request']['accept'],
                contentType=config['bedrock']['api_request']['contentType']
            )

            printer('[DEBUG] Capturing Bedrocks response/bedrock_stream', 'debug')
            bedrock_stream = response.get('body')
            printer(f"[DEBUG] Bedrock_stream: {bedrock_stream}", 'debug')
 
            # 直接使用文本生成器，不涉及音频
            to_text_generator(bedrock_stream)
            printer('[DEBUG] Created bedrock stream to text generator', 'debug')

        except Exception as e:
            print(e)
            time.sleep(2)
            self.speaking = False

        time.sleep(1)
        self.speaking = False
        printer('\n[DEBUG] Bedrock generation completed', 'debug')

class TextInputWrapper:
    def __init__(self, bedrock_wrapper):
        self.bedrock_wrapper = bedrock_wrapper
        self.input_thread = threading.Thread(target=self.text_input_loop, daemon=True)
        
    def text_input_loop(self):
        while True:
            try:
                text = input("\n[文字输入] 请输入问题（按回车发送，输入 q 退出）: ")
                if text.lower() == 'q':
                    os._exit(0)
                if text.strip():
                    # 调用Bedrock处理文字输入
                    self.bedrock_wrapper.invoke_bedrock(text)
            except Exception as e:
                print(f"文字输入异常: {e}")

    def start(self):
        self.input_thread.start()

# 启动文字输入
def enable_text_input():
    bedrock_wrapper = BedrockWrapper()
    text_wrapper = TextInputWrapper(bedrock_wrapper)
    text_wrapper.start()

info_text = f'''
*************************************************************
[INFO] Supported FM models: {get_model_ids()}.
[INFO] Change FM model by setting <MODEL_ID> environment variable. Example: export MODEL_ID=meta.llama2-70b-chat-v1

[INFO] AWS Region: {config['region']}
[INFO] Amazon Bedrock model: {config['bedrock']['api_request']['modelId']}
[INFO] Log level: {config['log_level']}

[INFO] 文本聊天模式已启动！
[INFO] 请输入您的问题，模型将以文本形式回复。
*************************************************************
'''
print(info_text)

enable_text_input()  # 启动文字输入

# 保持主线程运行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n程序已退出")
