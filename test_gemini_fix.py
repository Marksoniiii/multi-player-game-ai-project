#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Gemini API调用修复
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.llm_manager import llm_manager

def test_gemini_connection():
    """测试Gemini连接"""
    print("=== Gemini API 连接测试 ===")
    
    # 测试1: 检查配置
    print("\n1. 检查模型配置...")
    available_models = llm_manager.get_available_models()
    print(f"可用模型: {available_models}")
    
    # 测试2: 尝试配置Gemini（需要有效的API密钥）
    print("\n2. 测试Gemini配置...")
    print("注意: 需要有效的Gemini API密钥才能成功")
    
    # 这里需要用户提供真实的API密钥
    api_key = input("请输入Gemini API密钥 (或按回车跳过): ").strip()
    
    if api_key:
        success = llm_manager.configure_model("gemini", api_key)
        print(f"配置结果: {'成功' if success else '失败'}")
        
        if success:
            # 测试3: 检查可用性
            print("\n3. 检查Gemini可用性...")
            is_available = llm_manager.is_model_available("gemini")
            print(f"Gemini可用: {is_available}")
            
            if is_available:
                # 测试4: 尝试生成文本
                print("\n4. 测试文本生成...")
                try:
                    response = llm_manager.generate_text("请用一句话解释什么是人工智能", max_tokens=50)
                    print(f"生成结果: {response}")
                except Exception as e:
                    print(f"生成失败: {str(e)}")
        else:
            print("配置失败，无法进行后续测试")
    else:
        print("跳过Gemini测试")
    
    # 测试5: 检查模拟器模式
    print("\n5. 检查模拟器模式...")
    if "simulator" in llm_manager.clients:
        print("模拟器模式可用")
        try:
            response = llm_manager.clients["simulator"].generate_text("生成一个成语题目")
            print(f"模拟器响应: {response[:100]}...")
        except Exception as e:
            print(f"模拟器测试失败: {str(e)}")
    else:
        print("模拟器模式不可用")

def test_error_handling():
    """测试错误处理"""
    print("\n=== 错误处理测试 ===")
    
    # 测试无效API密钥
    print("\n1. 测试无效API密钥...")
    try:
        success = llm_manager.configure_model("gemini", "invalid_key")
        print(f"配置结果: {'成功' if success else '失败'}")
        is_available = llm_manager.is_model_available("gemini")
        print(f"无效密钥可用性: {is_available}")
    except Exception as e:
        print(f"预期错误: {str(e)}")
    
    # 测试空API密钥
    print("\n2. 测试空API密钥...")
    try:
        success = llm_manager.configure_model("gemini", "")
        print(f"配置结果: {'成功' if success else '失败'}")
        is_available = llm_manager.is_model_available("gemini")
        print(f"空密钥可用性: {is_available}")
    except Exception as e:
        print(f"预期错误: {str(e)}")

if __name__ == "__main__":
    print("Gemini API 修复测试")
    print("=" * 50)
    
    test_gemini_connection()
    test_error_handling()
    
    print("\n测试完成！") 