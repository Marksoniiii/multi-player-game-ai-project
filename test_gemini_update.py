#!/usr/bin/env python3
"""
测试更新后的Gemini Bot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.ai_bots.gemini_idiom_bot import GeminiIdiomBot

def test_gemini_bot():
    """测试Gemini Bot的功能"""
    print("🧪 测试Gemini Bot更新...")
    
    # 创建bot实例
    bot = GeminiIdiomBot()
    
    # 测试模型信息
    print("\n📊 模型信息:")
    model_info = bot.get_model_info()
    for key, value in model_info.items():
        print(f"  {key}: {value}")
    
    # 测试离线模式
    print("\n🔄 测试离线模式...")
    question = bot.generate_question()
    print(f"问题: {question}")
    
    # 测试答案检查
    print("\n🔍 测试答案检查...")
    result = bot.check_answer(question, "画蛇添足")
    print(f"答案检查结果: {result}")
    
    # 测试提示功能
    print("\n💡 测试提示功能...")
    hint = bot.get_hint(question)
    print(f"提示: {hint}")
    
    # 测试在线模式（如果有API密钥）
    print("\n🌐 测试在线模式...")
    api_key = input("请输入Gemini API密钥 (直接回车跳过): ").strip()
    
    if api_key:
        bot.set_api_key(api_key)
        print("API密钥已设置")
        
        # 获取更新后的模型信息
        print("\n📊 在线模式模型信息:")
        model_info = bot.get_model_info()
        for key, value in model_info.items():
            print(f"  {key}: {value}")
        
        # 测试在线问题生成
        print("\n🤖 在线问题生成...")
        online_question = bot.generate_question()
        print(f"在线问题: {online_question}")
        
        # 测试流式生成（如果支持）
        print("\n🌊 测试流式生成...")
        try:
            stream_response = bot.generate_question_stream()
            if stream_response:
                print("流式响应:")
                for chunk in stream_response:
                    print(chunk.text, end="", flush=True)
                print()
            else:
                print("流式生成未启用")
        except Exception as e:
            print(f"流式生成测试失败: {e}")
    else:
        print("跳过在线模式测试")
    
    print("\n✅ 测试完成!")

if __name__ == "__main__":
    test_gemini_bot() 