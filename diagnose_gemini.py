#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini API 详细诊断脚本
"""

import sys
import os
import requests
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.llm_manager import llm_manager

def test_network_connectivity():
    """测试网络连接"""
    print("=== 网络连接测试 ===")
    
    # 测试基本网络连接
    try:
        response = requests.get("https://www.google.com", timeout=10)
        print(f"✅ 基本网络连接: 正常 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ 基本网络连接: 失败 - {str(e)}")
        return False
    
    # 测试Google API端点
    try:
        response = requests.get("https://generativelanguage.googleapis.com", timeout=10)
        print(f"✅ Google API端点: 可访问 (状态码: {response.status_code})")
    except Exception as e:
        print(f"❌ Google API端点: 不可访问 - {str(e)}")
        return False
    
    return True

def test_api_key_format(api_key):
    """测试API密钥格式"""
    print(f"\n=== API密钥格式测试 ===")
    
    if not api_key:
        print("❌ API密钥为空")
        return False
    
    if len(api_key) < 20:
        print("❌ API密钥长度不足")
        return False
    
    if not api_key.startswith("AIza"):
        print("❌ API密钥格式不正确 (应该以'AIza'开头)")
        return False
    
    print("✅ API密钥格式正确")
    return True

def test_direct_api_call(api_key):
    """直接测试API调用"""
    print(f"\n=== 直接API调用测试 ===")
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": api_key
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Hello"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API调用成功")
            return True
        else:
            print(f"❌ API调用失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API调用异常: {str(e)}")
        return False

def test_llm_manager_integration(api_key):
    """测试LLM管理器集成"""
    print(f"\n=== LLM管理器集成测试 ===")
    
    # 配置模型
    success = llm_manager.configure_model("gemini", api_key)
    print(f"配置结果: {'✅ 成功' if success else '❌ 失败'}")
    
    if success:
        # 检查可用性
        is_available = llm_manager.is_model_available("gemini")
        print(f"可用性检查: {'✅ 可用' if is_available else '❌ 不可用'}")
        
        if is_available:
            # 测试文本生成
            try:
                response = llm_manager.generate_text("测试", max_tokens=10)
                print(f"✅ 文本生成成功: {response}")
                return True
            except Exception as e:
                print(f"❌ 文本生成失败: {str(e)}")
                return False
        else:
            print("❌ 模型不可用")
            return False
    else:
        print("❌ 模型配置失败")
        return False

def main():
    """主诊断函数"""
    print("Gemini API 详细诊断")
    print("=" * 50)
    
    # 1. 网络连接测试
    if not test_network_connectivity():
        print("\n❌ 网络连接问题，请检查网络设置")
        return
    
    # 2. 获取API密钥
    api_key = input("\n请输入Gemini API密钥: ").strip()
    
    if not api_key:
        print("❌ 未提供API密钥")
        return
    
    # 3. API密钥格式测试
    if not test_api_key_format(api_key):
        print("\n❌ API密钥格式问题")
        return
    
    # 4. 直接API调用测试
    if not test_direct_api_call(api_key):
        print("\n❌ 直接API调用失败")
        return
    
    # 5. LLM管理器集成测试
    if not test_llm_manager_integration(api_key):
        print("\n❌ LLM管理器集成失败")
        return
    
    print("\n✅ 所有测试通过！Gemini API工作正常")

if __name__ == "__main__":
    main() 