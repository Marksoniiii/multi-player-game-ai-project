"""
吃豆人游戏的人类智能体
处理双人吃豆人游戏的键盘输入
"""

import time
from typing import Dict, List, Tuple, Any, Optional
from ..base_agent import BaseAgent


class PacmanHumanAgent(BaseAgent):
    """吃豆人游戏的人类智能体"""
    
    def __init__(self, name: str = "Human", player_id: int = 1):
        super().__init__(name, player_id)
        self.last_action = 'stay'
        
        # 按键映射
        self.key_mapping = {
            'w': 'up',
            'a': 'left',
            's': 'down',
            'd': 'right',
            ' ': 'stay',
            'q': 'quit'
        }
        
        # 玩家1和玩家2的不同按键
        if player_id == 1:
            self.control_info = "玩家1控制: W(上) A(左) S(下) D(右) 空格(停留)"
        else:
            self.control_info = "玩家2控制: ↑(上) ←(左) ↓(下) →(右) Enter(停留)"
            self.key_mapping.update({
                'up': 'up',
                'left': 'left',
                'down': 'down',
                'right': 'right',
                'enter': 'stay'
            })
    
    def get_action(self, observation: Any, env: Any) -> str:
        """
        获取人类玩家的动作
        
        Args:
            observation: 当前观察
            env: 环境对象
            
        Returns:
            人类玩家选择的动作
        """
        start_time = time.time()
        
        # 显示当前游戏状态
        self._display_game_state(observation, env)
        
        # 获取有效动作
        valid_actions = env.get_valid_actions()
        
        # 获取人类输入
        action = self._get_human_input(valid_actions, env)
        
        # 更新统计
        move_time = time.time() - start_time
        self.total_moves += 1
        self.total_time += move_time
        
        return action
    
    def _display_game_state(self, observation: Any, env: Any):
        """显示游戏状态"""
        print(f"\n=== {self.name} (玩家{self.player_id}) 的回合 ===")
        
        # 获取游戏状态
        if hasattr(env, 'get_game_info'):
            game_info = env.get_game_info()
            print(f"玩家1分数: {game_info.get('player1_score', 0)}")
            print(f"玩家2分数: {game_info.get('player2_score', 0)}")
            print(f"剩余豆子: {game_info.get('dots_remaining', 0)}")
            print(f"移动次数: {game_info.get('move_count', 0)}")
        
        # 显示棋盘
        if hasattr(env, 'render'):
            env.render(mode='human')
        
        # 显示控制说明
        print(self.control_info)
    
    def _get_human_input(self, valid_actions: List[str], env: Any) -> str:
        """获取人类输入"""
        while True:
            try:
                # 显示当前可用动作
                print(f"可用动作: {valid_actions}")
                
                # 获取用户输入
                user_input = input(f"玩家{self.player_id}请输入动作: ").strip().lower()
                
                # 检查退出
                if user_input == 'q' or user_input == 'quit':
                    raise KeyboardInterrupt
                
                # 映射按键到动作
                action = self._map_key_to_action(user_input)
                
                # 验证动作
                if action in valid_actions:
                    self.last_action = action
                    return action
                else:
                    print(f"无效动作: {action}")
                    print("请重新输入")
                    
            except KeyboardInterrupt:
                print("\n游戏被用户中断")
                return 'quit'
            except Exception as e:
                print(f"输入错误: {e}")
                print("请重新输入")
    
    def _map_key_to_action(self, key: str) -> str:
        """将按键映射到动作"""
        # 直接的动作输入
        if key in ['up', 'down', 'left', 'right', 'stay']:
            return key
        
        # 按键映射
        if key in self.key_mapping:
            return self.key_mapping[key]
        
        # 数字键映射（快捷输入）
        action_map = {
            '1': 'up',
            '2': 'down',
            '3': 'left',
            '4': 'right',
            '5': 'stay'
        }
        
        if key in action_map:
            return action_map[key]
        
        # 如果都不匹配，返回停留
        return 'stay'
    
    def reset(self):
        """重置人类智能体"""
        super().reset()
        self.last_action = 'stay'
    
    def get_info(self) -> Dict[str, Any]:
        """获取人类智能体信息"""
        info = super().get_info()
        info.update({
            'type': 'PacmanHuman',
            'description': f'吃豆人游戏的人类玩家{self.player_id}',
            'control_scheme': self.control_info,
            'last_action': self.last_action
        })
        return info


class DualPacmanHumanController:
    """双人吃豆人游戏控制器"""
    
    def __init__(self):
        self.player1_agent = PacmanHumanAgent("Human Player 1", 1)
        self.player2_agent = PacmanHumanAgent("Human Player 2", 2)
        
        # 同步输入模式
        self.sync_input = True
    
    def get_actions(self, observation: Any, env: Any) -> Dict[int, str]:
        """获取双人动作"""
        actions = {}
        
        if self.sync_input:
            # 同步输入模式：一次性获取两个玩家的动作
            actions = self._get_sync_input(observation, env)
        else:
            # 异步输入模式：依次获取每个玩家的动作
            actions[1] = self.player1_agent.get_action(observation, env)
            actions[2] = self.player2_agent.get_action(observation, env)
        
        return actions
    
    def _get_sync_input(self, observation: Any, env: Any) -> Dict[int, str]:
        """同步输入模式"""
        print("\n=== 双人吃豆人游戏 ===")
        
        # 显示游戏状态
        if hasattr(env, 'get_game_info'):
            game_info = env.get_game_info()
            print(f"玩家1分数: {game_info.get('player1_score', 0)}")
            print(f"玩家2分数: {game_info.get('player2_score', 0)}")
            print(f"剩余豆子: {game_info.get('dots_remaining', 0)}")
            print(f"移动次数: {game_info.get('move_count', 0)}")
        
        # 显示棋盘
        if hasattr(env, 'render'):
            env.render(mode='human')
        
        # 显示控制说明
        print("控制说明:")
        print("玩家1: W(上) A(左) S(下) D(右)")
        print("玩家2: I(上) J(左) K(下) L(右)")
        print("输入格式: 玩家1动作,玩家2动作 (例如: w,i)")
        
        actions = {}
        
        while True:
            try:
                # 获取用户输入
                user_input = input("请输入两个玩家的动作: ").strip().lower()
                
                # 检查退出
                if user_input == 'q' or user_input == 'quit':
                    raise KeyboardInterrupt
                
                # 解析输入
                if ',' in user_input:
                    # 双人输入
                    p1_input, p2_input = user_input.split(',', 1)
                    actions[1] = self._parse_action(p1_input.strip(), 1)
                    actions[2] = self._parse_action(p2_input.strip(), 2)
                else:
                    # 单人输入（假设是玩家1）
                    actions[1] = self._parse_action(user_input, 1)
                    actions[2] = 'stay'
                
                return actions
                
            except KeyboardInterrupt:
                print("\n游戏被用户中断")
                return {1: 'quit', 2: 'quit'}
            except Exception as e:
                print(f"输入错误: {e}")
                print("请重新输入")
    
    def _parse_action(self, input_str: str, player_id: int) -> str:
        """解析单个玩家的动作"""
        # 玩家1的按键映射
        if player_id == 1:
            key_map = {
                'w': 'up',
                'a': 'left',
                's': 'down',
                'd': 'right',
                ' ': 'stay'
            }
        else:  # 玩家2
            key_map = {
                'i': 'up',
                'j': 'left',
                'k': 'down',
                'l': 'right',
                ' ': 'stay'
            }
        
        # 直接的动作输入
        if input_str in ['up', 'down', 'left', 'right', 'stay']:
            return input_str
        
        # 按键映射
        if input_str in key_map:
            return key_map[input_str]
        
        # 默认停留
        return 'stay'
    
    def reset(self):
        """重置控制器"""
        self.player1_agent.reset()
        self.player2_agent.reset() 