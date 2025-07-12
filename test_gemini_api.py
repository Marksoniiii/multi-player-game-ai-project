#!/usr/bin/env python3
"""
快速测试Gemini API密钥的有效性
"""

from agents.ai_bots.gemini_idiom_bot import GeminiIdiomBot


def test_api_key(api_key):
    """测试API密钥是否有效"""
    print(f"🔑 测试API密钥: {api_key[:10]}...")
    
    try:
        # 创建机器人实例
        bot = GeminiIdiomBot(api_key)
        
        # 测试问题生成
        print("📝 测试问题生成...")
        question = bot.generate_question()
        print(f"✅ 成功生成问题: {question}")
        
        # 测试答案检查
        print("📝 测试答案检查...")
        result = bot.check_answer(question, "测试答案")
        print(f"✅ 答案检查结果: {result}")
        
        # 测试提示生成
        print("📝 测试提示生成...")
        hint = bot.get_hint(question)
        print(f"✅ 生成提示: {hint}")
        
        print("🎉 API密钥测试通过！可以正常使用。")
        return True
        
    except Exception as e:
        print(f"❌ API密钥测试失败: {e}")
        return False


if __name__ == "__main__":
    # 您的API密钥
    api_key = "AIzaSyBiQxJ5Vc4BRmrXUeRyLOioZuoAJFY4syo"
    
    print("🧪 Gemini API密钥测试")
    print("=" * 50)
    
    if test_api_key(api_key):
        print("\n🚀 您可以直接启动游戏并使用这个API密钥了！")
        print("运行: python idiom_guessing_gui.py")
    else:
        print("\n❌ 请检查API密钥是否正确或网络连接是否正常") 