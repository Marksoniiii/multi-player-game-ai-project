import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import gym
from gym import spaces

from ..base_env import BaseEnv
from .idiom_guessing_game import IdiomGuessingGame, GameState


class IdiomGuessingEnv(BaseEnv):
    """成语猜多多游戏环境"""
    
    def __init__(self, llm_bot=None):
        self.game = IdiomGuessingGame()
        self.llm_bot = llm_bot
        if llm_bot:
            self.game.set_llm_bot(llm_bot)
        
        # 调用父类构造函数
        super().__init__(self.game)
        
        self.reset()
    
    def _setup_spaces(self) -> None:
        """设置观察空间和动作空间"""
        # 动作空间：字符串（成语答案）
        self.action_space = spaces.Discrete(1)  # 这里简化为离散空间
        
        # 观察空间：游戏状态字典
        self.observation_space = spaces.Dict({
            'game_state': spaces.Discrete(4),  # 游戏状态
            'current_player': spaces.Discrete(2),  # 当前玩家
            'scores': spaces.Box(low=0, high=100, shape=(2,), dtype=np.int32),  # 分数
            'time_remaining': spaces.Box(low=0, high=180, shape=(2,), dtype=np.float32),  # 剩余时间
            'question': spaces.Text(max_length=200),  # 当前问题
        })
    
    def _get_action_mask(self) -> np.ndarray:
        """获取动作掩码"""
        # 对于成语猜多多游戏，所有动作都是有效的（文本输入）
        return np.array([1])
    
    def reset(self) -> Dict[str, Any]:
        """重置环境"""
        if hasattr(self.game, 'reset_game'):
            self.game.reset_game()
        else:
            self.game.reset()
        return self.get_detailed_observation()
    
    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """执行动作"""
        # action 是玩家提交的答案
        result = self.game.submit_answer(action)
        
        observation = self.get_detailed_observation()
        reward = 1.0 if result.get('correct', False) else 0.0
        done = self.game.state == GameState.GAME_OVER
        info = result
        
        return observation, reward, done, info
    
    def render(self, mode='human'):
        """渲染游戏状态"""
        state = self.game.get_game_state()
        
        if mode == 'human':
            print(f"=== 成语猜多多游戏 ===")
            print(f"游戏状态: {state['state']}")
            print(f"当前玩家: {state['current_player']}")
            print(f"玩家1 ({state['player1']['name']}): {state['player1']['score']}分 | 剩余时间: {state['player1']['time_remaining']:.1f}秒")
            print(f"玩家2 ({state['player2']['name']}): {state['player2']['score']}分 | 剩余时间: {state['player2']['time_remaining']:.1f}秒")
            if state['current_question']:
                print(f"当前问题: {state['current_question']}")
            print("=" * 30)
        
        return state
    
    def close(self):
        """关闭环境"""
        self.game.stop_game()
    
    def seed(self, seed=None):
        """设置随机种子"""
        np.random.seed(seed)
        return [seed]
    
    def _get_observation(self) -> np.ndarray:
        """获取观察"""
        state = self.game.get_game_state()
        
        # 将游戏状态转换为数值
        state_mapping = {
            'waiting': 0,
            'player1_turn': 1,
            'player2_turn': 2,
            'game_over': 3
        }
        
        # 返回简化的观察（用于兼容父类）
        return np.array([
            state_mapping.get(state['state'], 0),
            0 if state['player1']['is_active'] else 1,
            state['player1']['score'],
            state['player2']['score'],
            state['player1']['time_remaining'],
            state['player2']['time_remaining']
        ])
    
    def get_detailed_observation(self) -> Dict[str, Any]:
        """获取详细观察（用于GUI显示）"""
        state = self.game.get_game_state()
        
        # 将游戏状态转换为数值
        state_mapping = {
            'waiting': 0,
            'player1_turn': 1,
            'player2_turn': 2,
            'game_over': 3
        }
        
        return {
            'game_state': state_mapping.get(state['state'], 0),
            'current_player': 0 if state['player1']['is_active'] else 1,
            'scores': np.array([state['player1']['score'], state['player2']['score']], dtype=np.int32),
            'time_remaining': np.array([state['player1']['time_remaining'], state['player2']['time_remaining']], dtype=np.float32),
            'question': state['current_question'],
            'player1_name': state['player1']['name'],
            'player2_name': state['player2']['name'],
            'raw_state': state  # 保留原始状态用于GUI显示
        }
    
    def start_game(self, player1_name: str = "玩家1", player2_name: str = "玩家2"):
        """开始游戏"""
        self.game.start_game(player1_name, player2_name)
        return self._get_observation()
    
    def get_valid_actions(self) -> List[str]:
        """获取有效动作（这里返回空列表，因为动作是文本输入）"""
        return []
    
    def submit_answer(self, answer: str) -> Dict[str, Any]:
        """提交答案的便捷方法"""
        return self.game.submit_answer(answer)
    
    def set_callback(self, event_type: str, callback):
        """设置事件回调"""
        self.game.set_callback(event_type, callback)
    
    def get_game_state(self) -> Dict[str, Any]:
        """获取游戏状态"""
        return self.game.get_game_state()
    
    def switch_player(self):
        """切换玩家"""
        self.game.switch_player()
    
    def set_llm_bot(self, llm_bot):
        """设置LLM机器人"""
        self.llm_bot = llm_bot
        self.game.set_llm_bot(llm_bot) 