import time
import threading
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from ..base_game import BaseGame


class GameState(Enum):
    WAITING = "waiting"
    PLAYER1_TURN = "player1_turn"
    PLAYER2_TURN = "player2_turn"
    GAME_OVER = "game_over"


@dataclass
class PlayerStats:
    name: str
    score: int = 0
    time_remaining: float = 180.0  # 3分钟 = 180秒
    current_question: str = ""
    current_answer: str = ""
    is_active: bool = False
    wrong_count: int = 0  # 当前题目错误次数


@dataclass
class GameResult:
    winner: str
    player1_score: int
    player2_score: int
    game_duration: float


class IdiomGuessingGame(BaseGame):
    """成语猜多多游戏核心逻辑"""
    
    def __init__(self):
        # 初始化游戏特有的属性
        self.state = GameState.WAITING
        self.player1 = PlayerStats("玩家1")
        self.player2 = PlayerStats("玩家2")
        self.current_player_obj = None  # 避免与BaseGame的current_player冲突
        self.game_start_time = None
        self.timer_thread = None
        self.timer_running = False
        self.llm_bot = None  # LLM出题机器人
        self.game_callbacks = {}  # 用于GUI更新的回调函数
        
        # 调用父类构造函数
        super().__init__()
        
    def set_llm_bot(self, llm_bot):
        """设置LLM机器人"""
        self.llm_bot = llm_bot
        
    def set_callback(self, event_type: str, callback):
        """设置事件回调函数"""
        self.game_callbacks[event_type] = callback
    
    def start_game(self, player1_name: str = "玩家1", player2_name: str = "玩家2"):
        """开始游戏"""
        if self.llm_bot is None:
            raise ValueError("必须设置LLM机器人才能开始游戏")
            
        self.player1.name = player1_name
        self.player2.name = player2_name
        self.game_start_time = time.time()
        self.state = GameState.PLAYER1_TURN
        self.current_player_obj = self.player1
        self.current_player_obj.is_active = True
        self.current_player = 1  # 设置BaseGame的current_player
        
        # 开始计时
        self._start_timer()
        
        # 请求第一个问题
        self._request_new_question()
        
        self._trigger_callback('game_started', {
            'player1': self.player1.name,
            'player2': self.player2.name,
            'current_player': self.current_player_obj.name
        })
    
    def submit_answer(self, answer: str) -> Dict[str, Any]:
        """提交答案"""
        if self.state == GameState.GAME_OVER:
            return {'success': False, 'message': '游戏已结束'}
        
        if not self.current_player_obj.is_active:
            return {'success': False, 'message': '当前不是您的回合'}
        
        self.current_player_obj.current_answer = answer
        
        # 请求LLM判断答案
        result = self._check_answer_with_llm(answer)
        
        response = {
            'success': True,
            'correct': result['correct'],
            'message': result['message'],
            'score': self.current_player_obj.score,
            'time_remaining': self.current_player_obj.time_remaining
        }
        
        if result['correct']:
            self.current_player_obj.score += 1
            self.current_player_obj.wrong_count = 0
            # 请求新问题
            self._request_new_question()
        else:
            self.current_player_obj.wrong_count += 1
            # 如果错误次数达到2次，提供额外提示
            if self.current_player_obj.wrong_count >= 2:
                hint = self._request_hint()
                response['hint'] = hint
        
        self._trigger_callback('answer_submitted', response)
        return response
    
    def switch_player(self):
        """切换到下一个玩家"""
        if self.state == GameState.PLAYER1_TURN:
            self.player1.is_active = False
            self.player2.is_active = True
            self.current_player_obj = self.player2
            self.current_player = 2  # 设置BaseGame的current_player
            self.state = GameState.PLAYER2_TURN
            self.current_player_obj.time_remaining = 180.0  # 重置时间
        elif self.state == GameState.PLAYER2_TURN:
            self._end_game()
            return
        
        # 重新开始计时
        self._start_timer()
        self._request_new_question()
        
        self._trigger_callback('player_switched', {
            'current_player': self.current_player_obj.name,
            'player1_score': self.player1.score,
            'player2_score': self.player2.score
        })
    
    def get_game_state(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        return {
            'state': self.state.value,
            'player1': {
                'name': self.player1.name,
                'score': self.player1.score,
                'time_remaining': self.player1.time_remaining,
                'is_active': self.player1.is_active
            },
            'player2': {
                'name': self.player2.name,
                'score': self.player2.score,
                'time_remaining': self.player2.time_remaining,
                'is_active': self.player2.is_active
            },
            'current_question': self.current_player_obj.current_question if self.current_player_obj else "",
            'current_player': self.current_player_obj.name if self.current_player_obj else ""
        }
    
    def _start_timer(self):
        """开始计时"""
        # 停止当前计时器
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_running = False
            # 检查是否是当前线程，避免join自己
            if self.timer_thread != threading.current_thread():
                self.timer_thread.join()
        
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self._timer_loop)
        self.timer_thread.daemon = True
        self.timer_thread.start()
    
    def _timer_loop(self):
        """计时器循环"""
        while self.timer_running and self.current_player_obj.time_remaining > 0:
            time.sleep(0.1)
            if self.timer_running:
                self.current_player_obj.time_remaining -= 0.1
                # 每秒更新一次UI
                if int(self.current_player_obj.time_remaining * 10) % 10 == 0:
                    self._trigger_callback('time_update', {
                        'time_remaining': self.current_player_obj.time_remaining,
                        'player': self.current_player_obj.name
                    })
        
        if self.current_player_obj.time_remaining <= 0:
            self._on_time_up()
    
    def _on_time_up(self):
        """时间结束"""
        self.timer_running = False
        self.current_player_obj.time_remaining = 0
        
        # 通过回调通知GUI处理时间到事件，让GUI决定是否切换玩家
        self._trigger_callback('time_up', {
            'player': self.current_player_obj.name,
            'score': self.current_player_obj.score,
            'should_switch': True  # 提示需要切换玩家
        })
    
    def _request_new_question(self):
        """请求新问题"""
        if self.llm_bot:
            try:
                question = self.llm_bot.generate_question()
                self.current_player_obj.current_question = question
                self.current_player_obj.wrong_count = 0
                
                self._trigger_callback('new_question', {
                    'question': question,
                    'player': self.current_player_obj.name
                })
            except Exception as e:
                self._trigger_callback('error', {'message': f'获取问题失败: {str(e)}'})
    
    def _check_answer_with_llm(self, answer: str) -> Dict[str, Any]:
        """使用LLM检查答案"""
        if self.llm_bot:
            try:
                result = self.llm_bot.check_answer(
                    self.current_player_obj.current_question, 
                    answer
                )
                return result
            except Exception as e:
                return {
                    'correct': False,
                    'message': f'答案检查失败: {str(e)}'
                }
        return {'correct': False, 'message': 'LLM机器人未设置'}
    
    def _request_hint(self) -> str:
        """请求提示"""
        if self.llm_bot:
            try:
                return self.llm_bot.get_hint(self.current_player_obj.current_question)
            except Exception as e:
                return f'获取提示失败: {str(e)}'
        return '提示功能不可用'
    
    def _end_game(self):
        """结束游戏"""
        self.timer_running = False
        self.state = GameState.GAME_OVER
        
        # 确定获胜者
        if self.player1.score > self.player2.score:
            winner = self.player1.name
        elif self.player2.score > self.player1.score:
            winner = self.player2.name
        else:
            winner = "平局"
        
        result = GameResult(
            winner=winner,
            player1_score=self.player1.score,
            player2_score=self.player2.score,
            game_duration=time.time() - self.game_start_time
        )
        
        self._trigger_callback('game_ended', {
            'winner': winner,
            'player1_score': self.player1.score,
            'player2_score': self.player2.score,
            'game_duration': result.game_duration
        })
        
        return result
    
    def _trigger_callback(self, event_type: str, data: Dict[str, Any]):
        """触发回调函数"""
        if event_type in self.game_callbacks:
            try:
                self.game_callbacks[event_type](data)
            except Exception as e:
                print(f"回调函数错误 ({event_type}): {e}")
    
    def stop_game(self):
        """停止游戏"""
        self.timer_running = False
        if self.timer_thread and self.timer_thread.is_alive():
            # 检查是否是当前线程，避免join自己
            if self.timer_thread != threading.current_thread():
                self.timer_thread.join()
        self.state = GameState.GAME_OVER
        
    def reset_game(self):
        """重置游戏"""
        self.stop_game()
        self.player1 = PlayerStats("玩家1")
        self.player2 = PlayerStats("玩家2")
        self.current_player_obj = None
        self.current_player = 1  # 重置BaseGame的current_player
        self.state = GameState.WAITING
        self.game_start_time = None
    
    # 实现BaseGame的抽象方法
    def reset(self) -> Dict[str, Any]:
        """重置游戏状态"""
        self.reset_game()
        return self.get_state()
    
    def step(self, action: Any) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """执行一步动作"""
        if isinstance(action, str):
            result = self.submit_answer(action)
            observation = self.get_state()
            reward = 1.0 if result.get('correct', False) else 0.0
            done = self.is_terminal()
            info = result
            return observation, reward, done, info
        else:
            return self.get_state(), 0.0, False, {'error': 'Invalid action type'}
    
    def get_valid_actions(self, player: int = None) -> List[Any]:
        """获取有效动作列表"""
        # 对于成语猜多多游戏，有效动作是任意字符串（成语答案）
        return ["任意字符串"]  # 这里返回一个占位符，实际上任何字符串都是有效的
    
    def is_terminal(self) -> bool:
        """检查游戏是否结束"""
        return self.state == GameState.GAME_OVER
    
    def get_winner(self) -> Optional[int]:
        """获取获胜者"""
        if not self.is_terminal():
            return None
        
        if self.player1.score > self.player2.score:
            return 1
        elif self.player2.score > self.player1.score:
            return 2
        else:
            return None  # 平局
    
    def get_state(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        return self.get_game_state()
    
    def render(self) -> Any:
        """渲染游戏画面"""
        state = self.get_game_state()
        print(f"=== 成语猜多多游戏 ===")
        print(f"游戏状态: {state['state']}")
        print(f"当前玩家: {state['current_player']}")
        print(f"玩家1 ({state['player1']['name']}): {state['player1']['score']}分")
        print(f"玩家2 ({state['player2']['name']}): {state['player2']['score']}分")
        if state['current_question']:
            print(f"当前问题: {state['current_question']}")
        print("=" * 30)
        return state 