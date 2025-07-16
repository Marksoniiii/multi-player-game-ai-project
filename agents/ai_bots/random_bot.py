import random
from agents.base_agent import BaseAgent
# 随机AI
'''
策略：完全随机选择合法位置
特点：简单快速，无智能可言
'''
class RandomBot(BaseAgent):
    def get_action(self, observation, env):
        valid_actions = env.get_valid_actions()
        return random.choice(valid_actions) 