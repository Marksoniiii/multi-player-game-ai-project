#!/usr/bin/env python3
"""
快速启动高级AI吃豆人游戏
"""

import sys
import pygame
from pacman_gui import GameLauncher

def main():
    """主函数"""
    print("=" * 60)
    print("🧠 高级AI吃豆人游戏")
    print("=" * 60)
    print()
    print("🎯 特色功能:")
    print("✅ A*路径规划算法")
    print("✅ BFS地图导航")
    print("✅ 威胁等级智能分析")
    print("✅ 实时追逐策略")
    print("✅ 预测拦截系统")
    print("✅ 动态策略切换")
    print()
    print("🎮 控制说明:")
    print("- 吃豆人: WASD键控制")
    print("- 幽灵: 方向键控制")
    print("- 退出: ESC键")
    print()
    print("🤖 AI难度:")
    print("- 基础AI: 简单规则策略")
    print("- 高级AI: 智能路径规划 + 实时追逐")
    print()
    print("正在启动游戏界面...")
    print("=" * 60)
    
    try:
        # 启动游戏
        launcher = GameLauncher()
        launcher.run()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 