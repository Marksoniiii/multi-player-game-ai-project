#!/usr/bin/env python3
"""
吃豆人游戏主程序
支持双人对战模式
"""

import sys
import time
from games.pacman.pacman_game import PacmanGame
from games.pacman.pacman_env import PacmanEnv
from agents.human.pacman_human_agent import DualPacmanHumanController

def main():
    print("🟡 欢迎来到双人吃豆人游戏！")
    print("=" * 50)
    
    # 创建游戏环境
    try:
        board_size = 21
        dots_count = 80
        
        print(f"初始化游戏...")
        print(f"迷宫大小: {board_size}x{board_size}")
        print(f"豆子数量: {dots_count}")
        
        env = PacmanEnv(board_size=board_size, dots_count=dots_count)
        
        # 创建双人控制器
        controller = DualPacmanHumanController()
        
        print("游戏初始化完成！")
        print()
        
        # 游戏主循环
        play_game(env, controller)
        
    except Exception as e:
        print(f"❌ 游戏初始化失败: {e}")
        sys.exit(1)

def play_game(env, controller):
    """游戏主循环"""
    print("🎮 游戏开始！")
    print("=" * 50)
    
    # 重置环境
    observation, info = env.reset()
    
    # 显示初始状态
    print("\n初始游戏状态:")
    env.render(mode='human')
    print(f"玩家1位置: {info.get('player1_pos')}")
    print(f"玩家2位置: {info.get('player2_pos')}")
    print(f"剩余豆子: {info.get('dots_remaining')}")
    
    game_running = True
    step_count = 0
    
    while game_running:
        try:
            # 获取玩家动作
            actions = controller.get_actions(observation, env)
            
            # 检查退出
            if 'quit' in actions.values():
                print("\n游戏被用户退出")
                break
            
            # 执行动作
            observation, reward, done, truncated, info = env.step(actions)
            step_count += 1
            
            # 显示游戏状态
            print(f"\n--- 第 {step_count} 步 ---")
            print(f"执行动作: {actions}")
            print(f"玩家1分数: {info.get('player1_score', 0)}")
            print(f"玩家2分数: {info.get('player2_score', 0)}")
            print(f"剩余豆子: {info.get('dots_remaining', 0)}")
            print(f"奖励: {reward}")
            
            # 检查碰撞
            if info.get('collision'):
                print("⚠️  玩家碰撞！")
            
            # 检查游戏结束
            if done or truncated:
                game_running = False
                print("\n🎯 游戏结束！")
                
                # 显示最终结果
                show_final_results(info)
                break
            
            # 添加一些延迟以便观察
            time.sleep(0.5)
            
        except KeyboardInterrupt:
            print("\n\n游戏被用户中断")
            break
        except Exception as e:
            print(f"❌ 游戏执行错误: {e}")
            break
    
    print("\n👋 感谢游戏！")

def show_final_results(info):
    """显示游戏最终结果"""
    print("=" * 50)
    print("🏆 游戏结果")
    print("=" * 50)
    
    player1_score = info.get('player1_score', 0)
    player2_score = info.get('player2_score', 0)
    winner = info.get('winner')
    
    print(f"玩家1最终分数: {player1_score}")
    print(f"玩家2最终分数: {player2_score}")
    print(f"剩余豆子: {info.get('dots_remaining', 0)}")
    
    if winner == 1:
        print("🎉 玩家1获胜！")
    elif winner == 2:
        print("🎉 玩家2获胜！")
    else:
        print("🤝 平局！")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 