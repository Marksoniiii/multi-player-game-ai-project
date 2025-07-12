#!/usr/bin/env python3
"""
国际象棋游戏启动器
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def show_menu():
    """显示游戏模式选择菜单"""
    print("🏰 国际象棋游戏")
    print("=" * 50)
    print("请选择游戏模式:")
    print("1. 🎮 图形界面模式 - 玩家vs玩家")
    print("2. 🤖 智能助手模式 - 玩家vs AI (推荐)")
    print("3. 💻 命令行模式")
    print("4. 🚪 退出")
    print("=" * 50)

def run_gui_mode():
    """运行图形界面模式 - 玩家vs玩家"""
    try:
        from chess_gui import ChessGUI
        print("✅ 成功加载图形界面模块")
        print("🎮 启动图形界面 - 玩家vs玩家...")
        
        game = ChessGUI()
        game.run()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保pygame已安装: pip install pygame")
    except Exception as e:
        print(f"❌ 图形界面启动失败: {e}")
        import traceback
        traceback.print_exc()

def run_ai_mode():
    """运行智能助手模式 - 玩家vs AI"""
    try:
        from chess_gui_ai import ChessGUIAI
        print("✅ 成功加载智能助手模块")
        print("🤖 启动智能助手模式 - 玩家vs AI...")
        print("💡 功能特色:")
        print("   • AI实时评价每一步棋")
        print("   • 提供智能移动建议")
        print("   • 游戏结束后自动复盘")
        print("   • 可调节AI难度")
        
        game = ChessGUIAI()
        game.run()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保pygame已安装: pip install pygame")
        print("请确保AI模块已正确安装")
    except Exception as e:
        print(f"❌ 智能助手启动失败: {e}")
        import traceback
        traceback.print_exc()

def run_console_mode():
    """运行命令行模式"""
    try:
        from games.chess import ChessEnv
        print("✅ 成功加载国际象棋模块")
        
        print("\n🎮 启动交互式国际象棋游戏!")
        print("输入格式: 起始位置-目标位置，例如 'e2e4' 或 'quit' 退出")
        
        env = ChessEnv()
        observation, info = env.reset()
        
        while not env.is_terminal():
            # 显示当前状态
            env.render()
            
            current_player = "白方" if env.game.current_player == 1 else "黑方"
            print(f"\n轮到 {current_player} 下棋")
            
            # 显示可用移动（前5个示例）
            valid_moves = env.get_valid_actions()
            print(f"可用移动数: {len(valid_moves)}")
            if len(valid_moves) > 0:
                print("示例移动:", end=" ")
                for i, move in enumerate(valid_moves[:5]):
                    from_pos, to_pos = move
                    cols = "abcdefgh"
                    rows = "87654321"
                    notation = (cols[from_pos[1]] + rows[from_pos[0]] + 
                               cols[to_pos[1]] + rows[to_pos[0]])
                    print(notation, end=" ")
                if len(valid_moves) > 5:
                    print("...")
                else:
                    print()
            
            # 获取用户输入
            try:
                user_input = input(f"{current_player} 请输入移动: ").strip().lower()
                
                if user_input in ['quit', 'exit', 'q']:
                    print("游戏结束!")
                    break
                
                # 解析移动
                move = env.parse_move_notation(user_input)
                if move is None:
                    print("❌ 无效的移动格式! 请使用格式如 'e2e4'")
                    continue
                
                # 检查移动是否合法
                if not env.is_move_legal(move[0], move[1]):
                    print("❌ 非法移动! 请选择有效的移动。")
                    continue
                
                # 执行移动
                observation, reward, done, truncated, info = env.step(move)
                
                print(f"✅ 执行移动: {info.get('notation', user_input)}")
                
                if info.get('check'):
                    print("🔥 将军!")
                
                if done:
                    env.render()
                    winner = env.get_winner()
                    if winner:
                        winner_name = "白方" if winner == 1 else "黑方"
                        print(f"🏆 {winner_name} 获胜!")
                    else:
                        print("🤝 平局!")
                    break
                    
            except KeyboardInterrupt:
                print("\n游戏被中断!")
                break
            except EOFError:
                print("\n游戏结束!")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                continue
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保国际象棋模块已正确安装")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    while True:
        show_menu()
        
        try:
            choice = input("请选择(1-4): ").strip()
            
            if choice == '1':
                run_gui_mode()
            elif choice == '2':
                run_ai_mode()
            elif choice == '3':
                run_console_mode()
            elif choice == '4':
                print("感谢游玩！再见！")
                break
            else:
                print("❌ 无效选择，请输入1-4之间的数字")
                continue
                
        except KeyboardInterrupt:
            print("\n感谢游玩！再见！")
            break
        except EOFError:
            print("\n感谢游玩！再见！")
            break
        except Exception as e:
            print(f"❌ 发生错误: {e}")
            continue

if __name__ == "__main__":
    main() 