#!/usr/bin/env python3
"""
成语猜多多游戏环境
"""

import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple

from games.base_env import BaseEnv
from games.idiom_guessing.idiom_guessing_game import IdiomGuessingGame


class IdiomGuessingEnv(BaseEnv):
    """成语猜多多游戏环境"""
    
    def __init__(self, time_limit: float = 180):
        self.game = IdiomGuessingGame(time_limit=time_limit)
        super().__init__(self.game)
        
    def _setup_spaces(self) -> None:
        """设置观察空间和动作空间"""
        # 观察空间：文本描述，这里用字典表示
        self.observation_space = "text"
        
        # 动作空间：文本回答，这里用字符串表示
        self.action_space = "text"
    
    def _get_observation(self) -> Dict[str, Any]:
        """获取观察"""
        game_info = self.game.get_game_info()
        return {
            "type": "observation",
            "game_info": game_info,
            "current_question": game_info.get("current_question", ""),
            "current_player": game_info.get("current_player", ""),
            "remaining_time": game_info.get("remaining_time", 0),
            "correct_count": game_info.get("correct_count", 0),
            "wrong_count": game_info.get("wrong_count", 0),
            "hint_count": game_info.get("hint_count", 0),
            "max_hints": game_info.get("max_hints", 2),
            "is_running": game_info.get("is_running", False),
            "is_time_up": game_info.get("is_time_up", False)
        }
    
    def _get_action_mask(self) -> np.ndarray:
        """获取动作掩码"""
        # 文本游戏不需要动作掩码
        return np.array([1])
    
    def reset(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """重置环境"""
        self.game.reset()
        observation = self._get_observation()
        info = self.game.get_game_info()
        return observation, info
    
    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, bool, Dict[str, Any]]:
        """执行动作"""
        if not isinstance(action, str):
            return self._get_observation(), -1, True, False, {'error': 'Action must be a string'}
        
        # 处理不同类型的动作
        if action.startswith("answer:"):
            # 提交答案
            answer = action[7:].strip()
            result = self.game.submit_answer(answer)
            reward = 1 if result.get("correct", False) else -0.1
            done = result.get("game_over", False)
            
        elif action.startswith("hint"):
            # 请求提示
            result = self.game.get_hint()
            reward = -0.05  # 使用提示的小惩罚
            done = False
            
        elif action.startswith("next_player"):
            # 切换到下一个玩家
            result = self.game.next_player()
            reward = 0
            done = result.get("game_over", False)
            
        elif action.startswith("generate_question"):
            # 生成新问题
            result = self.game.generate_question()
            reward = 0
            done = False
            
        else:
            # 默认当作答案处理
            result = self.game.submit_answer(action)
            reward = 1 if result.get("correct", False) else -0.1
            done = result.get("game_over", False)
        
        # 获取新观察
        observation = self._get_observation()
        
        # 检查是否超时
        truncated = observation.get("is_time_up", False)
        if truncated:
            done = True
        
        # 合并结果信息
        info = {
            "action_result": result,
            "game_info": self.game.get_game_info()
        }
        
        return observation, reward, done, truncated, info
    
    def start_game(self, mode: str = "single", players: List[str] = None):
        """开始游戏"""
        if players is None:
            players = ["Player1"]
        
        self.game.set_game_mode(mode, players)
        self.game.start_game()
        
        # 生成第一个问题
        self.game.generate_question()
        
        return self._get_observation()
    
    def get_current_question(self) -> str:
        """获取当前问题"""
        return self.game.current_question
    
    def get_current_player(self) -> Optional[str]:
        """获取当前玩家"""
        return self.game.get_current_player()
    
    def get_game_statistics(self) -> Dict[str, Any]:
        """获取游戏统计"""
        return self.game.get_game_statistics()
    
    def is_game_over(self) -> bool:
        """检查游戏是否结束"""
        return not self.game.is_running
    
    def get_winner(self) -> Optional[str]:
        """获取获胜者"""
        return self.game.winner
    
    def render(self, mode: str = "human") -> None:
        """渲染游戏状态"""
        if mode == "human":
            self._render_human()
        elif mode == "ansi":
            return self._render_ansi()
    
    def _render_human(self) -> None:
        """人类可读的渲染"""
        game_info = self.game.get_game_info()
        current_player = game_info.get("current_player", "")
        
        print("\n" + "="*50)
        print("🎯 成语猜多多")
        print("="*50)
        
        if current_player:
            print(f"当前玩家: {current_player}")
        
        print(f"游戏模式: {'双人对战' if self.game.game_mode == 'pvp' else '单人模式'}")
        print(f"时间限制: {self.game.time_limit}秒")
        
        if game_info.get("is_running", False):
            print(f"剩余时间: {game_info.get('remaining_time', 0):.1f}秒")
            print(f"已答对: {game_info.get('correct_count', 0)}题")
            print(f"已答错: {game_info.get('wrong_count', 0)}题")
            print(f"已用提示: {game_info.get('hint_count', 0)}/{game_info.get('max_hints', 2)}")
            
            if game_info.get("current_question"):
                print(f"\n题目: {game_info['current_question']}")
                print("\n请输入你的答案:")
            else:
                print("\n等待生成题目...")
        else:
            print("游戏未开始")
        
        print("="*50)
    
    def _render_ansi(self) -> str:
        """ANSI格式渲染"""
        game_info = self.game.get_game_info()
        
        output = []
        output.append("成语猜多多游戏状态")
        output.append(f"当前玩家: {game_info.get('current_player', '')}")
        output.append(f"剩余时间: {game_info.get('remaining_time', 0):.1f}秒")
        output.append(f"得分: {game_info.get('correct_count', 0)}")
        output.append(f"题目: {game_info.get('current_question', '')}")
        
        return "\n".join(output)
    
    def get_valid_actions(self) -> List[str]:
        """获取有效动作"""
        if not self.game.is_running:
            return ["generate_question"]
        
        actions = ["answer:"]  # 答案前缀
        
        if self.game.hint_count < self.game.max_hints:
            actions.append("hint")
        
        if self.game.game_mode == "pvp":
            actions.append("next_player")
        
        return actions
    
    def close(self) -> None:
        """关闭环境"""
        pass 