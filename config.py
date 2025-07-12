# -*- coding:utf-8 -*-
###
# Created Date: Sunday, June 22nd 2025, 4:15:02 pm
# Author: Ying Wen
# -----
# Last Modified: 
# Modified By: 
# -----
# Copyright (c) 2025 MARL @ SJTU
###
"""
双人游戏AI框架配置文件
"""

# 游戏配置
GAME_CONFIGS = {
    'gomoku': {
        'board_size': 15,
        'win_length': 5,
        'timeout': 30,  # 秒
        'max_moves': 225,  # 15x15
    },
    'snake': {
        'board_size': 20,
        'initial_length': 3,
        'food_count': 5,
        'timeout': 60,
        'max_moves': 1000,
    },
    'mahjong': {
        'players': 4,
        'tiles_per_hand': 13,
        'timeout': 120,
        'max_rounds': 100,
    },
    'chess': {
        'board_size': 8,
        'timeout': 1800,  # 30分钟
        'max_moves': 200,  # 最大回合数
        'time_control': '30+0',  # 时间控制格式
    }
}

# AI配置
AI_CONFIGS = {
    'minimax': {
        'max_depth': 4,
        'use_alpha_beta': True,
        'evaluation_timeout': 5,
    },
    'mcts': {
        'simulation_count': 1000,
        'exploration_constant': 1.414,
        'timeout': 10,
    },
    'rl': {
        'learning_rate': 0.1,
        'discount_factor': 0.9,
        'epsilon': 0.1,
        'training_episodes': 10000,
    },
    'behavior_tree': {
        'max_depth': 10,
        'timeout': 5,
    }
}

# 界面配置
UI_CONFIG = {
    'window_width': 800,
    'window_height': 600,
    'cell_size': 30,
    'fps': 60,
    'colors': {
        'background': (255, 255, 255),
        'grid': (200, 200, 200),
        'player1': (255, 0, 0),
        'player2': (0, 0, 255),
        'text': (0, 0, 0),
    }
}

# 测试配置
TEST_CONFIG = {
    'default_games': 100,
    'timeout_per_game': 300,  # 秒
    'save_results': True,
    'results_dir': 'results/',
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'game.log',
}

# 游戏状态
class GameState:
    ONGOING = 'ongoing'
    PLAYER1_WIN = 'player1_win'
    PLAYER2_WIN = 'player2_win'
    DRAW = 'draw'
    TIMEOUT = 'timeout'

# 玩家类型
class PlayerType:
    HUMAN = 'human'
    RANDOM = 'random'
    MINIMAX = 'minimax'
    MCTS = 'mcts'
    RL = 'rl'
    BEHAVIOR_TREE = 'behavior_tree'

# 动作类型
class ActionType:
    PLACE = 'place'      # 放置棋子/移动
    PASS = 'pass'        # 跳过回合
    RESIGN = 'resign'    # 认输
    DRAW = 'draw'        # 请求和棋 