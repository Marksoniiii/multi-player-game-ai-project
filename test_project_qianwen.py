import requests

# 请替换为你的真实API Key
API_KEY = "sk-3e2b8271143748c0be0a355f41d3a85a"
url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 初始化多轮对话的messages数组
messages = [
    {
        "role": "system",
        "content": "你是一个专业的成语猜谜游戏出题官。每次都要根据历史已用成语，出一道全新题，不能重复。"
    }
]

used_idioms = set()
for i in range(3):
    # 构造用户输入，动态带上已用成语
    user_prompt = f"""请为我出一道成语题，要求：
1. 不能用这些成语：画龙点睛, 画蛇添足, 守株待兔, 亡羊补牢, 刻舟求剑, {', '.join(used_idioms)}
2. 已用成语（绝对不能重复）：{', '.join(used_idioms) if used_idioms else '无'}
3. 不能直接说出成语本身，描述要有趣有挑战性，30-80字
请严格按格式回复：成语：[四字成语]\n描述：[描述内容]"""

    messages.append({"role": "user", "content": user_prompt})

    data = {
        "model": "qwen-plus",
        "messages": messages,
        "max_tokens": 2000,
        "temperature": 0.9,
        "top_p": 0.95,
        "stream": False
    }

    response = requests.post(url, headers=headers, json=data, timeout=30)
    result = response.json()
    if "choices" in result and len(result["choices"]) > 0:
        assistant_output = result["choices"][0]["message"]["content"]
        print(f"第{i+1}轮AI出题：\n{assistant_output}\n")
        # 简单提取成语（假设格式为“成语：xxxx”）
        idiom_line = [line for line in assistant_output.splitlines() if line.startswith("成语：")]
        if idiom_line:
            idiom = idiom_line[0].replace("成语：", "").strip()
            used_idioms.add(idiom)
        messages.append({"role": "assistant", "content": assistant_output})
    else:
        print("API返回异常：", result)
        break