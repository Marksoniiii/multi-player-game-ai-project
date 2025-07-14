#!/usr/bin/env python3
"""
游戏启动脚本
让用户选择不同的游戏模式
"""

import sys
import os
import subprocess

def main():
    print("=" * 50)
    print("🎮 多游戏AI对战平台")
    print("=" * 50)
    print()
    print("请选择游戏模式:")
    print("1. 多游戏GUI - 五子棋和贪吃蛇 (推荐)")
    print("2. 贪吃蛇专用GUI - 更好的贪吃蛇体验")
    print("3. 乒乓球 Pong - 玩家 vs AI 或 双人")
    print("4. 吃豆人游戏 - 双人对战 (新增)")
    print("5. 国际象棋 - 玩家vs玩家对战 (最新)")
    print("6. 成语猜多多 - 双人对战猜成语 (NEW!)")
    print("7. 五子棋命令行版本")
    print("8. 贪吃蛇命令行版本")
    print("9. 运行测试")
    print("10. 退出")
    print()
    
    while True:
        try:
            choice = input("请输入选择 (1-10): ").strip()
            
            if choice == '1':
                print("\n🎯 启动多游戏图形界面...")
                print("支持:")
                print("- 五子棋: 鼠标点击落子")
                print("- 贪吃蛇: 方向键/WASD控制")
                print("- 多种AI难度选择")
                print("- 暂停/继续功能")
                print()
                
                # 检查GUI文件是否存在
                if os.path.exists("gui_game.py"):
                    subprocess.run([sys.executable, "gui_game.py"])
                elif os.path.exists("multi_game_gui.py"):
                    subprocess.run([sys.executable, "multi_game_gui.py"])
                else:
                    print("❌ GUI文件未找到，请检查项目文件")
                break
                
            elif choice == '2':
                print("\n🐍 启动贪吃蛇专用图形界面...")
                print("特性:")
                print("- 专为贪吃蛇优化的界面")
                print("- 更流畅的游戏体验")
                print("- 多种贪吃蛇AI算法")
                print("- 实时状态显示")
                print()
                
                if os.path.exists("snake_gui.py"):
                    subprocess.run([sys.executable, "snake_gui.py"])
                else:
                    print("❌ 贪吃蛇GUI文件未找到")
                break
                
            elif choice == '3':
                print("\n🏓 启动乒乓球 Pong ...")
                print("特性:")
                print("- 玩家 vs 玩家 / 玩家 vs AI")
                print("- 贪婪 AI 或手动控制")
                print("- 漂亮的像素 UI 与倒计时")
                print("控制说明:")
                print("- 玩家1: W(上) / S(下)")
                print("- 玩家2: ↑(上) / ↓(下) 或 AI 自动")
                print()
                # Pong GUI 路径
                pong_path = os.path.join("games", "pong", "pong_gui.py")
                if os.path.exists(pong_path):
                    subprocess.run([sys.executable, pong_path])
                else:
                    print("❌ Pong GUI 文件未找到")
                break
                
            elif choice == '4':
                print("\n🟡 启动吃豆人大战幽灵...")
                print("特性:")
                print("- 多种游戏模式选择")
                print("- 玩家 vs 玩家 对战")
                print("- 玩家 vs AI 智能对战")
                print("- 角色选择 (吃豆人/幽灵)")
                print("- 智能AI系统")
                print("- 美观的图形界面")
                print("控制说明:")
                print("- 吃豆人: W(上) A(左) S(下) D(右)")
                print("- 幽灵: 方向键控制")
                print("- 鼠标点击选择游戏模式")
                print()
                
                if os.path.exists("pacman_gui.py"):
                    subprocess.run([sys.executable, "pacman_gui.py"])
                else:
                    print("❌ 吃豆人游戏文件未找到")
                break
                
            elif choice == '5':
                print("\n♔ 启动国际象棋游戏...")
                print("特性:")
                print("- 完整的国际象棋规则实现")
                print("- 支持所有特殊规则 (王车易位、吃过路兵、兵的升变)")
                print("- 玩家vs玩家对战")
                print("- 标准记谱法支持")
                print("- 自然语言游戏状态描述")
                print("- 为LLM AI集成预留接口")
                print("控制说明:")
                print("- 输入移动格式: e2e4 (从e2到e4)")
                print("- 输入 'quit' 退出游戏")
                print()
                
                if os.path.exists("chess_launcher.py"):
                    subprocess.run([sys.executable, "chess_launcher.py"])
                else:
                    print("❌ 国际象棋游戏文件未找到")
                break
                
            elif choice == '6':
                print("\n🎯 启动成语猜多多...")
                print("特性:")
                print("- 双人对战猜成语游戏")
                print("- 基于Gemini LLM智能出题")
                print("- 3分钟限时挑战")
                print("- 多种题目类型 (故事、典故、谜语等)")
                print("- 智能答案判断和提示系统")
                print("- 实时计分和计时")
                print("游戏说明:")
                print("- 每位玩家有独立的3分钟答题时间")
                print("- 答对得1分，答错不扣分")
                print("- 连续答错2次可获得额外提示")
                print("- 计时结束后比较得分决定胜负")
                print("注意: 需要设置有效的Gemini API密钥才能开始游戏")
                print()
                
                if os.path.exists("idiom_guessing_gui.py"):
                    subprocess.run([sys.executable, "idiom_guessing_gui.py"])
                else:
                    print("❌ 成语猜多多游戏文件未找到")
                break
                
            elif choice == '7':
                print("\n♟️  启动五子棋命令行版本...")
                subprocess.run([sys.executable, "main.py", "--game", "gomoku", "--player1", "human", "--player2", "random"])
                break
                
            elif choice == '8':
                print("\n🐍 启动贪吃蛇命令行版本...")
                subprocess.run([sys.executable, "main.py", "--game", "snake", "--player1", "human", "--player2", "snake_ai"])
                break
                
            elif choice == '9':
                print("\n🧪 运行项目测试...")
                subprocess.run([sys.executable, "test_project.py"])
                break
                
            elif choice == '10':
                print("\n👋 再见！")
                sys.exit(0)
                
            else:
                print("❌ 无效选择，请输入 1-10")
                
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            sys.exit(0)
        except EOFError:
            print("\n\n👋 再见！")
            sys.exit(0)

if __name__ == "__main__":
    main() 