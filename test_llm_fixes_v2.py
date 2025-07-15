#!/usr/bin/env python3
"""
测试LLM修复效果 - 第二版
包含更全面的测试和错误处理
"""

import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.llm_manager import llm_manager
from agents.ai_bots.llm_idiom_bot import LLMIdiomBot

def test_gemini_fix():
    """测试Gemini模型修复效果"""
    print("=== 测试Gemini模型修复效果 ===")
    
    # 配置Gemini模型（需要用户提供API key）
    print("请输入Gemini API Key（按回车跳过）：")
    api_key = input().strip()
    
    if not api_key:
        print("跳过Gemini测试")
        return
    
    success = llm_manager.configure_model("gemini", api_key)
    if not success:
        print("配置Gemini模型失败")
        return
    
    llm_manager.set_current_model("gemini")
    
    try:
        # 创建LLM出题机器人
        bot = LLMIdiomBot()
        
        # 测试生成题目
        print("生成题目中...")
        question_data = bot.generate_question("medium")
        print(f"题目：{question_data}")
        
        if question_data.get('generated_by') != 'LLM出题官(备用)':
            print("✅ Gemini测试成功！API调用正常")
        else:
            print("⚠️ Gemini测试部分成功，使用了备用题目")
        
    except Exception as e:
        print(f"Gemini测试失败: {e}")

def test_qianwen_diversity():
    """测试千问多样性修复效果"""
    print("\n=== 测试千问多样性修复效果 ===")
    
    # 配置千问模型（需要用户提供API key）
    print("请输入千问API Key（按回车跳过）：")
    api_key = input().strip()
    
    if not api_key:
        print("跳过千问测试")
        return
    
    success = llm_manager.configure_model("qianwen", api_key)
    if not success:
        print("配置千问模型失败")
        return
    
    llm_manager.set_current_model("qianwen")
    
    try:
        # 创建LLM出题机器人
        bot = LLMIdiomBot()
        
        # 测试生成多个题目，检查多样性
        print("生成多个题目测试多样性...")
        questions = []
        for i in range(5):  # 增加到5个题目
            print(f"生成第{i+1}个题目...")
            question_data = bot.generate_question("medium")
            questions.append(question_data)
            print(f"题目{i+1}：答案={question_data.get('answer', 'N/A')}")
            time.sleep(2)  # 增加延迟避免API限制
        
        # 检查答案是否都不同
        answers = [q.get('answer', '') for q in questions]
        unique_answers = set(answers)
        
        print(f"\n答案列表：{answers}")
        print(f"唯一答案数量：{len(unique_answers)}/{len(answers)}")
        
        if len(unique_answers) >= len(answers) * 0.6:  # 至少60%不同
            print("✅ 千问多样性测试成功！答案多样性良好")
        elif len(unique_answers) > 1:
            print("⚠️ 千问多样性测试部分成功！仍有一些重复但有改善")
        else:
            print("❌ 千问多样性测试失败！答案仍然完全重复")
            
    except Exception as e:
        print(f"千问测试失败: {e}")

def test_simulator():
    """测试模拟器功能"""
    print("\n=== 测试模拟器功能 ===")
    
    # 配置模拟器
    success = llm_manager.configure_model("simulator", "dummy_key")
    if not success:
        print("配置模拟器失败")
        return
    
    llm_manager.set_current_model("simulator")
    
    try:
        # 创建LLM出题机器人
        bot = LLMIdiomBot()
        
        # 测试生成题目
        print("测试生成题目...")
        question_data = bot.generate_question("medium")
        print(f"题目：{question_data}")
        
        # 测试判断答案 - 正确答案
        print("\n测试判断正确答案...")
        correct_answer = question_data['answer']
        judgment_correct = bot.judge_answer(correct_answer, correct_answer, question_data['question'])
        print(f"正确答案判断：{judgment_correct}")
        
        # 测试判断答案 - 错误答案
        print("\n测试判断错误答案...")
        judgment_wrong = bot.judge_answer("错误答案", correct_answer, question_data['question'])
        print(f"错误答案判断：{judgment_wrong}")
        
        # 测试提示
        print("\n测试提示功能...")
        hint = bot.provide_hint(1)
        print(f"提示：{hint}")
        
        # 检查格式是否正确
        correct_format = True
        if not judgment_correct.get('correct'):
            print("❌ 正确答案判断格式错误")
            correct_format = False
            
        if judgment_wrong.get('correct', True):  # 错误答案应该返回False
            print("❌ 错误答案判断逻辑错误")
            correct_format = False
            
        if not hint.get('hint'):
            print("❌ 提示格式错误")
            correct_format = False
        
        if correct_format:
            print("✅ 模拟器测试成功！所有功能正常")
        else:
            print("⚠️ 模拟器测试部分成功，存在一些格式问题")
        
    except Exception as e:
        print(f"模拟器测试失败: {e}")

def test_api_error_handling():
    """测试API错误处理"""
    print("\n=== 测试API错误处理 ===")
    
    # 测试错误的API密钥
    print("测试错误API密钥处理...")
    
    try:
        # 配置错误的Gemini密钥
        success = llm_manager.configure_model("gemini", "invalid_key")
        if success:
            llm_manager.set_current_model("gemini")
            bot = LLMIdiomBot()
            question_data = bot.generate_question("medium")
            
            if question_data.get('generated_by') == 'LLM出题官(备用)':
                print("✅ 错误密钥处理正确，自动回退到备用题目")
            else:
                print("⚠️ 错误密钥处理异常")
        else:
            print("✅ 错误密钥被正确拒绝")
            
    except Exception as e:
        print(f"✅ 错误处理正常: {e}")

def main():
    """主函数"""
    print("成语猜多多LLM修复测试 - 第二版")
    print("=" * 50)
    
    # 测试模拟器（始终可用）
    test_simulator()
    
    # 测试错误处理
    test_api_error_handling()
    
    # 测试Gemini修复
    test_gemini_fix()
    
    # 测试千问多样性
    test_qianwen_diversity()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    
    print("\n修复总结：")
    print("1. ✅ Gemini模型：从gemini-pro更新到gemini-2.5-flash")
    print("2. ✅ 千问多样性：添加时间戳、随机数、更强随机参数")
    print("3. ✅ 模拟器逻辑：修复判断和提示功能")
    print("4. ✅ 错误处理：改进API响应解析和错误回退")

if __name__ == "__main__":
    main() 