#!/usr/bin/env python3
"""
快速测试成语猜多多游戏修复效果
"""

def test_imports():
    """测试导入是否正常"""
    try:
        print("🧪 测试导入...")
        from games.idiom_guessing.idiom_guessing_env import IdiomGuessingEnv
        from agents.ai_bots.gemini_idiom_bot import GeminiIdiomBot
        print("✅ 导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_environment_creation():
    """测试环境创建"""
    try:
        print("🧪 测试环境创建...")
        from games.idiom_guessing.idiom_guessing_env import IdiomGuessingEnv
        from agents.ai_bots.gemini_idiom_bot import GeminiIdiomBot
        
        # 创建LLM机器人（无API密钥）
        llm_bot = GeminiIdiomBot()
        
        # 创建环境
        env = IdiomGuessingEnv(llm_bot)
        print("✅ 环境创建成功")
        
        # 测试重置
        state = env.reset()
        print(f"✅ 环境重置成功，返回状态: {type(state)}")
        
        # 清理
        env.close()
        return True
    except Exception as e:
        print(f"❌ 环境创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_creation():
    """测试GUI创建（不显示窗口）"""
    try:
        print("🧪 测试GUI类创建...")
        import tkinter as tk
        from idiom_guessing_gui import IdiomGuessingGUI
        
        # 创建隐藏的根窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 创建GUI实例
        gui = IdiomGuessingGUI(root)
        print("✅ GUI创建成功")
        
        # 清理
        root.destroy()
        return True
    except Exception as e:
        print(f"❌ GUI创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🎯 成语猜多多游戏修复测试")
    print("=" * 40)
    
    tests = [
        ("导入测试", test_imports),
        ("环境创建测试", test_environment_creation),
        ("GUI创建测试", test_gui_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 执行: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} 失败")
    
    print("\n" + "=" * 40)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！修复成功！")
        print("\n现在您可以重新运行游戏了：")
        print("python idiom_guessing_gui.py")
    else:
        print("❌ 部分测试失败")

if __name__ == "__main__":
    main() 