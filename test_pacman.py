#!/usr/bin/env python3
"""
吃豆人游戏功能测试
"""

def test_pacman_game():
    """测试吃豆人游戏基本功能"""
    print("🧪 开始测试吃豆人游戏...")
    
    try:
        # 测试导入
        from games.pacman import PacmanGame, PacmanEnv
        print("✅ 模块导入成功")
        
        # 测试游戏创建
        game = PacmanGame(board_size=11, dots_count=20)
        print("✅ 游戏创建成功")
        
        # 测试游戏状态
        print(f"玩家1位置: {game.player1_pos}")
        print(f"玩家2位置: {game.player2_pos}")
        print(f"豆子数量: {game.dots_remaining}")
        print(f"游戏板大小: {game.board.shape}")
        
        # 测试环境
        env = PacmanEnv(board_size=11, dots_count=20)
        print("✅ 环境创建成功")
        
        # 测试重置
        observation, info = env.reset()
        print("✅ 环境重置成功")
        print(f"观察空间形状: {observation.shape}")
        print(f"玩家1分数: {info.get('player1_score', 0)}")
        print(f"玩家2分数: {info.get('player2_score', 0)}")
        
        # 测试一步动作
        actions = {1: 'right', 2: 'left'}
        observation, reward, done, truncated, info = env.step(actions)
        print("✅ 动作执行成功")
        print(f"奖励: {reward}")
        print(f"游戏结束: {done}")
        
        # 测试游戏渲染
        print("✅ 游戏渲染测试:")
        env.render(mode='human')
        
        print("\n🎉 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pacman_game() 