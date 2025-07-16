#api_request_list就是一个大字典，然后里面有很多小字典
api_request_list = {
    'amazon.titan-text-express-v1': {
        "modelId": "amazon.titan-text-express-v1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "inputText": "",
            "textGenerationConfig": {
                "maxTokenCount": 4096,
                "stopSequences": [],
                "temperature": 0,
                "topP": 1
            }
        }
    },
    'amazon.titan-text-lite-v1': {
        "modelId": "amazon.titan-text-lite-v1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "inputText": "",
            "textGenerationConfig": {
                "maxTokenCount": 4096,
                "stopSequences": [],
                "temperature": 0,
                "topP": 1
            }
        }
    },
    'anthropic.claude-3-sonnet-20240229-v1:0': {
        "modelId": "anthropic.claude-3-sonnet-20240229-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "messages": "",
            "max_tokens": 4000, # 对max_token进行上调
            "temperature": 0.3, # 此处将温度调整0.3,使得模型生成结果更稳定、确定性更强，更聚焦于训练数据中的常见模式
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": [
                "\n\nHuman:"
            ],
            "anthropic_version": "bedrock-2023-05-31"
        }
    },    
    'anthropic.claude-v2:1': {
        "modelId": "anthropic.claude-v2:1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_tokens_to_sample": 300,
            "temperature": 0.5,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": [
                "\n\nHuman:"
            ],
            "anthropic_version": "bedrock-2023-05-31"
        }
    },
    'anthropic.claude-v2': {
        "modelId": "anthropic.claude-v2",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_tokens_to_sample": 300,
            "temperature": 0.5,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": [
                "\n\nHuman:"
            ],
            "anthropic_version": "bedrock-2023-05-31"
        }
    },
    'meta.llama3-70b-instruct-v1': {
        "modelId": "meta.llama3-70b-instruct-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_gen_len": 512,
            "temperature": 0.1,
            "top_p": 0.9
        }
    },    
    'meta.llama3-8b-instruct-v1': {
        "modelId": "meta.llama3-8b-instruct-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_gen_len": 512,
            "temperature": 0.1,
            "top_p": 0.9
        }
    },        
    'meta.llama2-13b-chat-v1': {
        "modelId": "meta.llama2-13b-chat-v1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_gen_len": 512,
            "temperature": 0.2,
            "top_p": 0.9
        }
    },
    'meta.llama2-70b-chat-v1': {
        "modelId": "meta.llama2-70b-chat-v1",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_gen_len": 512,
            "temperature": 0.2,
            "top_p": 0.9
        }
    },
    'mistral.mistral-large-2402-v1:0': {
        "modelId": "mistral.mistral-large-2402-v1:0",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_tokens": 512,
            "temperature": 0.2,
            "top_p": 0.9
        }
    },    
    'cohere.command-text-v14': {
        "modelId": "cohere.command-text-v14",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_tokens": 1024,
            "temperature": 0.8,
        }
    },
    'cohere.command-light-text-v14': {
        "modelId": "cohere.command-light-text-v14",
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "prompt": "",
            "max_tokens": 1024,
            "temperature": 0.8,
        }
    },

    # 'deepseek.r1': {
    #     "modelId": "deepseek.r1",
    #     "contentType": "application/json",
    #     "accept": "*/*",
    #     "body": {
    #         "messages": [],
    #         "max_tokens": 1000,
    #         "temperature": 0.7,
    #         "top_p": 0.9,
    #         "stop": ["<|endoftext|>"]
    #     }
    # },

}


def get_model_ids():
    return list(api_request_list.keys())
