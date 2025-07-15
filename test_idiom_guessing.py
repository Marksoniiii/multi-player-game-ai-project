#!/usr/bin/env python3
"""
成语猜多多游戏测试脚本
"""

import sys
import os
import time
import unittest

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from games.idiom_guessing import IdiomGuessingGame, IdiomGuessingEnv
from agents.ai_bots.llm_idiom_bot import LLMIdiomBot
from utils.llm_manager import llm_manager


class TestIdiomGuessingGame(unittest.TestCase):
    """测试成语猜多多游戏"""
    
    def setUp(self):
        """设置测试环境"""
        # 配置模拟器
        llm_manager.configure_model("simulator", "test_key")
        llm_manager.set_current_model("simulator")
        
        self.game = IdiomGuessingGame(time_limit=10)  # 测试用短时间
        self.env = IdiomGuessingEnv(time_limit=10)
        self.bot = LLMIdiomBot()
    
    def test_game_initialization(self):
        """测试游戏初始化"""
        self.assertFalse(self.game.is_running)
        self.assertEqual(self.game.game_mode, "single")
        self.assertEqual(self.game.time_limit, 10)
        self.assertEqual(self.game.current_question_id, 0)
    
    def test_set_game_mode(self):
        """测试设置游戏模式"""
        # 单人模式
        self.game.set_game_mode("single", ["Player1"])
        self.assertEqual(self.game.game_mode, "single")
        self.assertEqual(len(self.game.players), 1)
        
        # 双人模式
        self.game.set_game_mode("pvp", ["Player1", "Player2"])
        self.assertEqual(self.game.game_mode, "pvp")
        self.assertEqual(len(self.game.players), 2)
    
    def test_llm_bot_question_generation(self):
        """测试LLM机器人出题"""
        question_data = self.bot.generate_question("easy")
        
        self.assertIn("question", question_data)
        self.assertIn("answer", question_data)
        self.assertIn("type", question_data)
        self.assertIn("difficulty", question_data)
        
        # 验证答案和问题不为空
        self.assertTrue(len(question_data["question"]) > 0)
        self.assertTrue(len(question_data["answer"]) > 0)
        
        print(f"生成的题目: {question_data['question']}")
        print(f"正确答案: {question_data['answer']}")
    
    def test_llm_bot_answer_judgment(self):
        """测试LLM机器人答案判断"""
        # 先生成一个题目
        question_data = self.bot.generate_question("easy")
        question = question_data["question"]
        correct_answer = question_data["answer"]
        
        # 测试正确答案
        result = self.bot.judge_answer(correct_answer, correct_answer, question)
        self.assertTrue(result["correct"])
        
        # 测试错误答案
        result = self.bot.judge_answer("错误答案", correct_answer, question)
        self.assertFalse(result["correct"])
    
    def test_llm_bot_hint_generation(self):
        """测试LLM机器人提示生成"""
        # 先生成一个题目
        question_data = self.bot.generate_question("easy")
        
        # 生成提示
        hint_data = self.bot.provide_hint(1)
        
        self.assertIn("hint", hint_data)
        self.assertIn("level", hint_data)
        self.assertTrue(len(hint_data["hint"]) > 0)
        
        print(f"生成的提示: {hint_data['hint']}")
    
    def test_game_start_and_question_generation(self):
        """测试游戏开始和问题生成"""
        self.game.set_game_mode("single", ["TestPlayer"])
        self.game.start_game()
        
        self.assertTrue(self.game.is_running)
        
        # 生成问题
        question_data = self.game.generate_question()
        
        self.assertIn("question", question_data)
        self.assertIn("answer", question_data)
        self.assertTrue(len(self.game.current_question) > 0)
        self.assertTrue(len(self.game.current_answer) > 0)
        
        print(f"当前问题: {self.game.current_question}")
        print(f"当前答案: {self.game.current_answer}")
    
    def test_answer_submission(self):
        """测试答案提交"""
        self.game.set_game_mode("single", ["TestPlayer"])
        self.game.start_game()
        
        # 生成问题
        question_data = self.game.generate_question()
        correct_answer = question_data["answer"]
        
        # 提交正确答案
        result = self.game.submit_answer(correct_answer)
        
        self.assertIn("correct", result)
        self.assertTrue(result["correct"])
        
        # 检查统计更新
        stats = self.game.get_current_stats()
        self.assertIsNotNone(stats)
        self.assertEqual(stats.correct_count, 1)
        
        print(f"答案提交结果: {result}")
    
    def test_hint_system(self):
        """测试提示系统"""
        self.game.set_game_mode("single", ["TestPlayer"])
        self.game.start_game()
        
        # 生成问题
        self.game.generate_question()
        
        # 获取提示
        hint_result = self.game.get_hint()
        
        self.assertIn("hint", hint_result)
        self.assertEqual(self.game.hint_count, 1)
        
        print(f"提示结果: {hint_result}")
    
    def test_env_integration(self):
        """测试环境集成"""
        # 启动游戏
        observation = self.env.start_game("single", ["TestPlayer"])
        
        self.assertIn("is_running", observation)
        self.assertTrue(observation["is_running"])
        
        # 生成问题
        result = self.env.step("generate_question")
        observation, reward, done, truncated, info = result
        
        self.assertIn("action_result", info)
        self.assertIn("question", info["action_result"])
        
        # 提交答案
        correct_answer = info["action_result"]["answer"]
        result = self.env.step(f"answer:{correct_answer}")
        observation, reward, done, truncated, info = result
        
        self.assertGreater(reward, 0)  # 正确答案应该有正奖励
        
        print(f"环境测试完成")
    
    def test_game_statistics(self):
        """测试游戏统计"""
        self.game.set_game_mode("single", ["TestPlayer"])
        self.game.start_game()
        
        # 生成并回答几个问题
        for i in range(3):
            question_data = self.game.generate_question()
            if i < 2:  # 前两个答对
                result = self.game.submit_answer(question_data["answer"])
            else:  # 最后一个答错
                result = self.game.submit_answer("错误答案")
        
        # 检查统计
        stats = self.game.get_game_statistics()
        self.assertIn("TestPlayer", stats)
        
        player_stats = stats["TestPlayer"]
        self.assertEqual(player_stats["correct_count"], 2)
        self.assertEqual(player_stats["wrong_count"], 1)
        self.assertEqual(player_stats["total_attempts"], 3)
        
        print(f"游戏统计: {stats}")
    
    def test_llm_manager(self):
        """测试LLM管理器"""
        # 测试模型配置
        success = llm_manager.configure_model("simulator", "test_key")
        self.assertTrue(success)
        
        # 测试模型设置
        success = llm_manager.set_current_model("simulator")
        self.assertTrue(success)
        
        # 测试文本生成
        response = llm_manager.generate_text("测试提示")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
        
        print(f"LLM管理器测试完成")


def run_interactive_test():
    """运行交互式测试"""
    print("=" * 60)
    print("🎯 成语猜多多 - 交互式测试")
    print("=" * 60)
    
    # 配置模拟器
    llm_manager.configure_model("simulator", "test_key")
    llm_manager.set_current_model("simulator")
    
    # 创建游戏实例
    env = IdiomGuessingEnv(time_limit=60)
    
    print("\n1. 启动游戏...")
    observation = env.start_game("single", ["测试玩家"])
    print(f"游戏状态: {observation['is_running']}")
    
    print("\n2. 生成第一个问题...")
    result = env.step("generate_question")
    observation, reward, done, truncated, info = result
    
    if "action_result" in info:
        question_data = info["action_result"]
        print(f"题目: {question_data['question']}")
        print(f"答案: {question_data['answer']}")
        print(f"类型: {question_data['type']}")
        print(f"难度: {question_data['difficulty']}")
        
        print("\n3. 测试错误答案...")
        result = env.step("answer:错误答案")
        observation, reward, done, truncated, info = result
        print(f"错误答案结果: {info['action_result']['message']}")
        
        print("\n4. 获取提示...")
        result = env.step("hint")
        observation, reward, done, truncated, info = result
        if "hint" in info["action_result"]:
            print(f"提示: {info['action_result']['hint']}")
        
        print("\n5. 提交正确答案...")
        correct_answer = question_data['answer']
        result = env.step(f"answer:{correct_answer}")
        observation, reward, done, truncated, info = result
        print(f"正确答案结果: {info['action_result']['message']}")
        
        print("\n6. 查看游戏统计...")
        stats = env.get_game_statistics()
        print(f"统计信息: {stats}")
    
    print("\n✅ 交互式测试完成!")


if __name__ == "__main__":
    print("成语猜多多游戏测试")
    print("=" * 50)
    
    # 选择测试类型
    test_type = input("选择测试类型 (1: 单元测试, 2: 交互测试): ").strip()
    
    if test_type == "1":
        # 运行单元测试
        unittest.main(verbosity=2)
    elif test_type == "2":
        # 运行交互式测试
        run_interactive_test()
    else:
        print("无效选择，运行单元测试...")
        unittest.main(verbosity=2) 