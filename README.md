# 多人游戏AI对战框架

一个基于OpenAI Gym风格的多人游戏AI对战框架，支持五子棋、贪吃蛇、乒乓球、吃豆人和成语猜多多等多种游戏，提供图形界面和命令行两种模式，集成多种AI算法。

## 🎮 项目特色

- **多游戏支持**: 五子棋、贪吃蛇、乒乓球、吃豆人、成语猜多多
- **丰富AI算法**: Minimax、MCTS、强化学习、行为树、LLM等
- **双界面模式**: 图形界面(GUI)和命令行界面
- **模块化设计**: 易于扩展新游戏和AI算法
- **完整测试**: 全面的功能测试和性能验证

## 📋 目录

- [快速开始](#-快速开始)
- [支持的游戏](#-支持的游戏)
- [AI算法](#-ai算法)
- [项目结构](#-项目结构)
- [使用指南](#-使用指南)
- [开发指南](#-开发指南)
- [故障排除](#-故障排除)

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 推荐使用conda或venv创建虚拟环境

### 安装步骤

#### 1. 创建虚拟环境 (推荐)
```bash
# 使用conda
conda create --name MultiPlayerGame python=3.12
conda activate MultiPlayerGame

# 或使用venv
python -m venv MultiPlayerGame
source MultiPlayerGame/bin/activate  # Linux/macOS
# MultiPlayerGame\Scripts\activate  # Windows
```

#### 2. 克隆项目
```bash
git clone https://github.com/ying-wen/multi-player-game-ai-project
cd multi-player-game-ai-project
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 验证安装
```bash
python -c "import pygame, numpy; print('✅ 依赖安装成功')"
```

### 启动游戏

```bash
python start_games.py
```

选择游戏模式：
- **1**: 多游戏GUI (五子棋+贪吃蛇)
- **2**: 贪吃蛇专用GUI
- **3**: 乒乓球 Pong
- **4**: 吃豆人游戏
- **5**: 成语猜多多
- **6**: 退出

## 🎮 支持的游戏

### 1. 五子棋 (Gomoku)
- **规则**: 15×15棋盘，连成5子获胜
- **操作**: 鼠标点击落子
- **AI支持**: 随机AI、Minimax算法、MCTS算法
- **特色**: 支持Alpha-Beta剪枝、置换表优化

### 2. 贪吃蛇 (Snake)
- **规则**: 双人贪吃蛇对战，吃食物长大，避免碰撞
- **操作**: 方向键或WASD控制移动
- **AI支持**: 基础AI、智能寻路AI(A*算法)
- **特色**: 实时碰撞检测、安全空间计算

### 3. 乒乓球 (Pong)
- **规则**: 经典乒乓球游戏，双人对战或人机对战
- **操作**: W/S键(玩家1)、方向键(玩家2)
- **AI支持**: 贪婪AI算法
- **特色**: 像素风格UI、物理引擎

### 4. 吃豆人 (Pacman)
- **规则**: 吃豆人与幽灵对战，收集豆子或躲避
- **操作**: WASD控制吃豆人，方向键控制幽灵
- **AI支持**: 基础AI、高级AI(路径规划)
- **特色**: 迷宫系统、道具系统

### 5. 成语猜多多 (Idiom Guessing)
- **规则**: 基于LLM的智能成语猜谜游戏
- **操作**: 键盘输入答案
- **AI支持**: LLM智能出题系统
- **特色**: 支持多种大语言模型、智能提示

## 🧠 AI算法

### 通用AI
- **RandomBot**: 完全随机动作，适合基准测试
- **HumanAgent**: 人类玩家接口

### 五子棋AI
- **MinimaxBot**: 经典博弈树搜索算法
  - Alpha-Beta剪枝优化
  - 迭代深化搜索
  - 置换表缓存
  - 启发式评估函数
- **MCTSBot**: 蒙特卡洛树搜索算法
  - PUCT选择策略
  - 启发式模拟
  - 动态时间控制

### 贪吃蛇AI
- **SnakeAI**: 智能寻路算法
  - A*路径规划
  - 安全空间计算
  - 碰撞避免
- **BasicSnakeAI**: 基础贪心算法

### 其他游戏AI
- **GreedyPongAI**: 乒乓球贪婪AI
- **PacmanAI**: 吃豆人路径规划AI
- **LLMIdiomBot**: 基于大语言模型的智能出题

### 高级AI
- **BehaviorTreeBot**: 行为树AI
- **RLBot**: 强化学习AI (Q-learning)
- **AdvancedPacmanAI**: 高级吃豆人AI

## 📁 项目结构

```
multi-player-game-ai-project/
├── start_games.py              # 游戏启动脚本
├── gui_game.py                 # 多游戏图形界面
├── snake_gui.py                # 贪吃蛇专用GUI
├── pacman_gui.py               # 吃豆人GUI
├── idiom_guessing_gui.py       # 成语猜多多GUI
├── config.py                   # 配置文件
├── requirements.txt            # 依赖列表
│
├── games/                      # 游戏模块
│   ├── base_game.py           # 游戏基类
│   ├── base_env.py            # 环境基类
│   ├── gomoku/                # 五子棋
│   ├── snake/                 # 贪吃蛇
│   ├── pong/                  # 乒乓球
│   ├── pacman/                # 吃豆人
│   └── idiom_guessing/        # 成语猜多多
│
├── agents/                     # AI智能体
│   ├── base_agent.py          # 智能体基类
│   ├── human/                 # 人类智能体
│   └── ai_bots/               # AI机器人
│       ├── random_bot.py      # 随机AI
│       ├── minimax_bot.py     # Minimax算法
│       ├── mcts_bot.py        # MCTS算法
│       ├── snake_ai.py        # 贪吃蛇AI
│       ├── pacman_ai.py       # 吃豆人AI
│       ├── llm_idiom_bot.py   # LLM智能体
│       └── ...                # 其他AI
│
├── utils/                      # 工具模块
│   ├── bedrock_client.py      # AWS Bedrock客户端
│   ├── llm_manager.py         # LLM管理器
│   └── game_utils.py          # 游戏工具
│
├── examples/                   # 示例代码
│   ├── basic_usage.py         # 基础使用示例
│   ├── custom_agent.py        # 自定义智能体示例
│   └── advanced_ai_examples.py # 高级AI示例
│
└── amazon-bedrock-voice-conversation/  # AWS Bedrock集成
    ├── app.py                 # 语音对话应用
    ├── api_request_schema.py  # API请求模式
    └── fine_tunning_data.py   # 微调数据
```

## 🎯 使用指南

### 图形界面操作

#### 多游戏GUI
- **游戏切换**: 点击"Switch Game"按钮
- **AI选择**: 下拉菜单选择不同AI
- **暂停/继续**: 点击"Pause/Resume"按钮
- **重新开始**: 点击"New Game"按钮

#### 贪吃蛇专用GUI
- **控制**: 方向键或WASD
- **AI对战**: 选择不同AI难度
- **实时信息**: 显示蛇长度和存活状态

#### 吃豆人GUI
- **模式选择**: 人机对战或双人对战
- **角色选择**: 吃豆人或幽灵
- **控制**: WASD(吃豆人)、方向键(幽灵)

#### 成语猜多多GUI
- **模式选择**: 单人挑战或双人对战
- **LLM配置**: 设置API密钥和模型
- **答题**: 键盘输入成语答案

### 命令行模式

```bash
# 五子棋人机对战
python -c "
from games.gomoku.gomoku_env import GomokuEnv
from agents.ai_bots.minimax_bot import MinimaxBot
env = GomokuEnv()
agent = MinimaxBot()
# 开始游戏...
"

# 贪吃蛇AI对战
python -c "
from games.snake.snake_env import SnakeEnv
from agents.ai_bots.snake_ai import SnakeAI
env = SnakeEnv()
agent1 = SnakeAI(player_id=1)
agent2 = SnakeAI(player_id=2)
# 开始对战...
"
```

## 🔧 开发指南

### 添加新游戏

1. 在`games/`目录下创建新游戏文件夹
2. 继承`BaseGame`和`BaseEnv`基类
3. 实现必要的方法：
   ```python
   class NewGame(BaseGame):
       def reset(self) -> Dict[str, Any]:
           # 重置游戏状态
           pass
       
       def step(self, action) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
           # 执行动作
           pass
       
       def get_valid_actions(self) -> List[Any]:
           # 获取有效动作
           pass
       
       def is_terminal(self) -> bool:
           # 检查游戏是否结束
           pass
   ```

### 添加新AI

1. 在`agents/ai_bots/`目录下创建新AI文件
2. 继承`BaseAgent`基类
3. 实现`get_action`方法：
   ```python
   class NewAI(BaseAgent):
       def get_action(self, observation, env):
           # 实现AI决策逻辑
           return action
   ```

### 配置参数

编辑`config.py`文件调整参数：

```python
# 游戏参数
GAME_CONFIGS = {
    'new_game': {
        'board_size': 10,
        'timeout': 30,
        'max_moves': 100,
    }
}

# AI参数
AI_CONFIGS = {
    'new_ai': {
        'max_depth': 4,
        'timeout': 5,
    }
}
```

## 🐛 故障排除

### 环境问题

**Q: Python版本不兼容？**
A: 确保使用Python 3.8+，推荐3.10-3.12版本

**Q: pip安装失败？**
A: 
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

**Q: pygame安装失败？**
A:
```bash
# Windows
pip install pygame --pre

# Linux
sudo apt-get install python3-pygame

# macOS
brew install pygame
```

### 图形界面问题

**Q: pygame窗口无法显示？**
A: 
- **Windows**: 检查是否安装了Visual C++ Redistributable
- **macOS**: 安装XQuartz (`brew install --cask xquartz`)
- **Linux**: 安装图形界面支持 (`sudo apt install python3-tk`)

**Q: SSH远程连接无法显示图形？**
A:
```bash
# 启用X11转发
ssh -X username@hostname

# 或使用VNC/远程桌面
```

### 游戏问题

**Q: AI思考时间太长？**
A: 调整AI参数：
```python
# 在config.py中修改
AI_CONFIGS = {
    'minimax': {'max_depth': 3},  # 减少搜索深度
    'mcts': {'timeout': 3},       # 减少时间限制
}
```

**Q: 导入错误？**
A:
```bash
# 确保在项目根目录
cd multi-player-game-ai-project

# 设置PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### 性能优化

**Q: 游戏运行卡顿？**
A:
- 关闭不必要的后台程序
- 降低AI搜索深度
- 使用更快的硬件

**Q: 内存使用过高？**
A:
- 减少MCTS模拟次数
- 定期清理游戏历史记录
- 使用更轻量的AI算法

## 🎊 项目亮点

### 完成的功能
- ✅ **多游戏支持**: 5种不同游戏类型
- ✅ **丰富AI算法**: 10+种不同算法的AI
- ✅ **双界面模式**: GUI和命令行
- ✅ **实时对战**: 流畅的人机对战体验
- ✅ **模块化设计**: 易于扩展和维护
- ✅ **完整测试**: 全面的功能验证
- ✅ **用户友好**: 简单的启动和操作

### 技术特色
- 🏗️ **模块化架构**: 清晰的代码结构
- 🎯 **Gym风格接口**: 标准化的环境接口
- 🧪 **测试驱动**: 完整的测试覆盖
- 📚 **文档完善**: 详细的使用说明
- 🤖 **AI多样性**: 从基础到高级的多种算法
- 🎮 **游戏丰富**: 从传统到现代的多种游戏

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

### 开发流程
1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

### 代码规范
- 使用Python 3.8+语法
- 遵循PEP 8代码风格
- 添加适当的类型提示
- 编写单元测试

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

**注意**: 这是一个教学项目，包含一些故意设置的bug和不完善的功能，需要学生修复和改进。请参考项目中的TODO文档了解具体任务。

