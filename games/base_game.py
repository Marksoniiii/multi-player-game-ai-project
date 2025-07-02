"""
游戏基类
定义所有游戏的基本接口
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional
import config


class BaseGame(ABC):
    """游戏基类"""
    
    def __init__(self, game_config: Dict[str, Any] = None):
        self.game_config = game_config or {}
        self.current_player = 1  # 1 或 2
        self.game_state = config.GameState.ONGOING
        self.move_count = 0
        self.start_time = time.time()
        self.last_move_time = time.time()
        self.history = []  # 游戏历史记录
        
        self.reset()
    
    @abstractmethod
    def reset(self) -> Dict[str, Any]:
        """重置游戏状态，子类需清理所有状态变量
        建议：self.move_count = 0, self.history = [], self.current_player = 1, self.game_state = ONGOING
        """
        pass
    
    @abstractmethod
    def step(self, action: Any) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """
        执行一步动作
        
        Args:
            action: 动作
            
        Returns:
            observation: 观察状态
            reward: 奖励
            done: 是否结束
            info: 额外信息
        """
        pass
    
    @abstractmethod
    def get_valid_actions(self, player: int = None) -> List[Any]:
        """获取有效动作列表，建议支持player参数，便于多智能体扩展"""
        pass
    
    @abstractmethod
    def is_terminal(self) -> bool:
        """检查游戏是否结束，需考虑平局、超时、最大步数等"""
        pass
    
    @abstractmethod
    def get_winner(self) -> Optional[int]:
        """获取获胜者 (1, 2, 或 None表示平局)"""
        pass
    
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """获取当前游戏状态，建议包含棋盘、玩家、历史等"""
        pass
    
    @abstractmethod
    def render(self) -> Any:
        """渲染游戏画面，支持命令行和GUI"""
        pass
    
    def switch_player(self):
        """切换玩家"""
        self.current_player = 3 - self.current_player  # 1 -> 2, 2 -> 1
    
    def is_timeout(self) -> bool:
        """检查是否超时"""
        if 'timeout' in self.game_config:
            return time.time() - self.last_move_time > self.game_config['timeout']
        return False
    
    def is_max_moves_reached(self) -> bool:
        """检查是否达到最大步数"""
        if 'max_moves' in self.game_config:
            return self.move_count >= self.game_config['max_moves']
        return False
    
    def update_game_state(self):
        """更新游戏状态，自动判断胜负/平局/超时"""
        if self.is_terminal():
            winner = self.get_winner()
            if winner == 1:
                self.game_state = config.GameState.PLAYER1_WIN
            elif winner == 2:
                self.game_state = config.GameState.PLAYER2_WIN
            else:
                self.game_state = config.GameState.DRAW
        elif self.is_timeout():
            self.game_state = config.GameState.TIMEOUT
        elif self.is_max_moves_reached():
            self.game_state = config.GameState.DRAW
    
    def get_game_info(self) -> Dict[str, Any]:
        """获取游戏信息，便于环境和UI展示"""
        return {
            'current_player': self.current_player,
            'game_state': self.game_state,
            'move_count': self.move_count,
            'elapsed_time': time.time() - self.start_time,
            'last_move_time': time.time() - self.last_move_time,
            'history': self.history.copy()
        }
    
    def record_move(self, player: int, action: Any, result: Dict[str, Any] = None):
        """记录移动，建议所有step后调用。自动校验player和action合法性。"""
        if player not in [1, 2]:
            raise ValueError(f"player必须为1或2，当前为{player}")
        if action is None:
            raise ValueError("action不能为空")
        move_record = {
            'player': player,
            'action': action,
            'timestamp': time.time(),
            'result': result or {}
        }
        self.history.append(move_record)
        self.move_count += 1
        self.last_move_time = time.time()
    
    def get_legal_actions(self, player: int = None) -> List[Any]:
        """获取合法动作（别名，兼容旧代码）"""
        return self.get_valid_actions(player)
    
    def clone(self) -> 'BaseGame':
        """克隆游戏状态，子类需实现深拷贝。建议用copy.deepcopy或自定义clone。"""
        raise NotImplementedError("子类必须实现clone方法，否则无法用于AI搜索/回溯")

    def get_action_space(self) -> Any:
        """获取动作空间，子类需实现。建议返回所有可能动作的列表或空间对象。"""
        raise NotImplementedError("子类必须实现get_action_space方法")

    def get_observation_space(self) -> Any:
        """获取观察空间，子类需实现。建议返回状态空间结构。"""
        raise NotImplementedError("子类必须实现get_observation_space方法")