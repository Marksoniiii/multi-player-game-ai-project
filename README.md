# 多人游戏AI框架

一个基于OpenAI Gym风格的多人游戏AI对战框架，支持五子棋和贪吃蛇游戏，提供图形界面和命令行两种模式。


### 1. conda 虚拟环境  (推荐)
在conda提供的命令行界面里键入命令:

```bash
conda create --name MultiPlayerGame python=3.12  # 创建虚拟环境, 推荐python版本为3.12

# 激活虚拟环境
conda activate MultiPlayerGame
# 升级pip
python -m pip install --upgrade pip
```

### 2. 项目clone
```bash
# clone 项目 (推荐使用Git, 当然你也可以直接download下来)
git clone https://github.com/ying-wen/multi-player-game-ai-project
# 进入项目目录
cd multi-player-game-ai-project
```

### 4. python 依赖安装

```bash
# 安装项目依赖
pip install -r requirements.txt
```


#### Linux
```bash
# 安装图形界面支持
# Ubuntu/Debian:
sudo apt install python3-tk #如果使用虚拟环境, tk 也可以使用 pip install tk 安装在python虚拟环境下, 这里是给系统的python解释器安装 pip 包

# 如果使用ssh连接远程服务器，启用X11转发可以在本地显示图形界面
ssh -X username@hostname
```

## 🚀 快速启动

### 验证安装
```bash
# 检查Python版本
python --version

# 检查pip版本
pip --version

# 检查依赖安装
python -c "import pygame, numpy; print('Dependencies OK')"
```

### 启动项目
```bash
# 最简单的启动方式
python start_games.py
```

然后根据菜单选择：
- **选择1**: 多游戏GUI (五子棋+贪吃蛇)
- **选择2**: 贪吃蛇专用GUI (推荐贪吃蛇玩家)
- **选择3**: 五子棋命令行版本
- **选择4**: 贪吃蛇命令行版本
- **选择5**: 运行测试
- **选择6**: 退出


## 🎮 支持的游戏

### 1. 五子棋 (Gomoku)
- **规则**: 15×15棋盘，连成5子获胜
- **操作**: 图形界面点击落子，命令行输入坐标
- **AI支持**: 随机AI、Minimax算法、MCTS算法

### 2. 贪吃蛇 (Snake)
- **规则**: 双人贪吃蛇对战，吃食物长大，避免碰撞
- **操作**: 方向键或WASD控制移动
- **AI支持**: 基础贪吃蛇AI、智能寻路AI

## 🎯 图形界面说明

### 1. 多游戏GUI (`gui_game.py`)
**特点**: 支持五子棋和贪吃蛇切换，全功能界面
- 🖱️ **五子棋**: 鼠标点击落子
- ⌨️ **贪吃蛇**: 方向键/WASD控制
- 🎮 **游戏切换**: 点击按钮切换游戏类型
- 🤖 **AI选择**: 随机AI、MinimaxAI、MCTS AI
- ⏸️ **暂停功能**: 随时暂停/继续游戏

### 2. 贪吃蛇专用GUI (`snake_gui.py`)
**特点**: 专为贪吃蛇优化，更流畅的体验
- 🐍 **专用界面**: 针对贪吃蛇优化的UI
- 🎨 **视觉效果**: 更好的蛇身和食物显示
- 🤖 **专用AI**: 基础AI、智能AI(A*算法)、随机AI
- 📊 **实时信息**: 蛇长度、存活状态实时显示

## 🎮 游戏操作指南

### 五子棋操作
- **目标**: 连成5子获胜
- **操作**: 鼠标点击棋盘交叉点落子
- **显示**: 黑子是你，白子是AI
- **标记**: 红圈标记最后一步

### 贪吃蛇操作
- **目标**: 吃食物长大，避免碰撞
- **操作**: 
  - 方向键 ↑↓←→ 控制移动
  - 或者 WASD 键控制移动
- **显示**: 
  - 蓝色蛇是你 (头部有眼睛)
  - 红色蛇是AI (头部有眼睛)
  - 绿色圆形是食物
- **获胜**: 对手撞墙/撞蛇身，或比较最终长度

## 🧠 AI算法说明

### 通用AI
- **RandomBot**: 完全随机动作，适合练习
- **HumanAgent**: 人类玩家接口

### 五子棋AI
- **MinimaxBot**: 经典博弈树搜索，中等难度
- **MCTSBot**: 蒙特卡洛树搜索，高难度

### 贪吃蛇AI
- **SnakeAI**: 基础AI，寻找最近食物
- **SmartSnakeAI**: 智能AI，使用A*寻路算法

## 💻 命令行模式

### 直接启动命令
```bash
# 五子棋人机对战
python main.py --game gomoku --player1 human --player2 minimax

# 贪吃蛇人机对战
python main.py --game snake --player1 human --player2 snake_ai

# AI对战观看
python main.py --game gomoku --player1 mcts --player2 minimax
```

### 可用智能体
- `human`: 人类玩家
- `random`: 随机AI
- `minimax`: Minimax算法AI
- `mcts`: MCTS算法AI
- `snake_ai`: 贪吃蛇基础AI
- `smart_snake_ai`: 贪吃蛇智能AI

## 📦 依赖说明

### 核心依赖
```txt
pygame>=2.1.0       # 图形界面和游戏引擎
numpy>=1.19.0       # 数值计算和数组操作
typing-extensions   # 类型提示支持
```

### 可选依赖
```bash
# 开发和测试
pytest              # 单元测试框架
black               # 代码格式化
flake8              # 代码风格检查

# 性能分析
cProfile            # Python内置性能分析器
memory_profiler     # 内存使用分析
```

## 🧪 测试验证

### 运行完整测试
```bash
python test_project.py
```

**测试结果**: 所有测试通过 (7/7)
- ✅ 模块导入测试
- ✅ 五子棋游戏逻辑测试
- ✅ 五子棋环境测试
- ✅ AI智能体测试
- ✅ 游戏对战测试
- ✅ 智能体评估测试
- ✅ 自定义智能体测试

### 单元测试
```bash
# 运行特定测试
python -m pytest tests/

# 运行覆盖率测试
python -m pytest --cov=games --cov=agents tests/
```

## 🛠️ 项目结构

```
multi-player-game-ai-project/
├── gui_game.py           # 多游戏图形界面
├── snake_gui.py          # 贪吃蛇专用GUI
├── start_games.py        # 启动脚本
├── main.py               # 命令行主程序
├── test_project.py       # 测试程序
├── config.py             # 配置文件
├── requirements.txt      # 依赖列表
├── .gitignore           # Git忽略文件
├── games/                # 游戏模块
│   ├── __init__.py
│   ├── base_game.py     # 游戏基类
│   ├── base_env.py      # 环境基类
│   ├── gomoku/          # 五子棋
│   │   ├── __init__.py
│   │   ├── gomoku_game.py
│   │   └── gomoku_env.py
│   └── snake/           # 贪吃蛇
│       ├── __init__.py
│       ├── snake_game.py
│       └── snake_env.py
├── agents/              # AI智能体
│   ├── __init__.py
│   ├── base_agent.py    # 智能体基类
│   ├── human/           # 人类智能体
│   │   ├── __init__.py
│   │   ├── human_agent.py
│   │   └── gui_human_agent.py
│   └── ai_bots/         # AI机器人
│       ├── __init__.py
│       ├── random_bot.py
│       ├── minimax_bot.py
│       ├── mcts_bot.py
│       ├── rl_bot.py
│       ├── behavior_tree_bot.py
│       └── snake_ai.py
├── utils/               # 工具模块
│   ├── __init__.py
│   └── game_utils.py
├── examples/            # 示例代码
│   ├── basic_usage.py
│   └── custom_agent.py
└── tests/               # 测试文件
    └── __init__.py
```

## 🎯 使用建议

### 新手推荐
1. **开始**: 运行 `python start_games.py`
2. **五子棋**: 选择1，然后选择随机AI练习
3. **贪吃蛇**: 选择2，体验专用界面

### 进阶玩家
1. **挑战高难度**: 选择MCTS AI对战
2. **观察AI**: 使用命令行模式观看AI对战
3. **自定义**: 修改AI参数或添加新算法

### 开发者
1. **测试**: 先运行 `python test_project.py`
2. **扩展**: 参考现有代码添加新游戏或AI
3. **调试**: 使用命令行模式便于调试

## 🐛 故障排除

### 环境问题

**Q: Python版本不兼容？**
A: 确保使用Python 3.7+，推荐3.8-3.11版本

**Q: pip安装失败？**
A: 
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 使用conda
conda install pygame numpy
```

**Q: 虚拟环境问题？**
A:
```bash
# 删除旧环境
rm -rf game_ai_env

# 重新创建
python -m venv game_ai_env
source game_ai_env/bin/activate  # Linux/macOS
# 或 game_ai_env\Scripts\activate  # Windows
pip install -r requirements.txt
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

# 或者使用VNC/远程桌面
```

**Q: 中文显示乱码？**
A: 项目已使用英文界面，避免了字体问题

### 游戏问题

**Q: 贪吃蛇移动太快/太慢？**
A: 修改配置文件中的 `update_interval` 参数

**Q: AI思考时间太长？**
A: 调整AI参数：
- Minimax: 减少 `max_depth`
- MCTS: 减少 `simulation_count`

**Q: 导入错误？**
A:
```bash
# 确保在项目根目录
cd multi-player-game-ai-project

# 检查Python路径
python -c "import sys; print(sys.path)"

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

## 🔧 高级配置

### 自定义配置
编辑 `config.py` 文件可以调整：
```python
# 游戏参数
BOARD_SIZE = 15          # 棋盘大小
WIN_LENGTH = 5           # 获胜条件
SNAKE_SPEED = 0.3        # 贪吃蛇速度

# AI参数
MINIMAX_DEPTH = 3        # Minimax搜索深度
MCTS_SIMULATIONS = 500   # MCTS模拟次数

# 界面参数
WINDOW_WIDTH = 800       # 窗口宽度
WINDOW_HEIGHT = 600      # 窗口高度
```

### 添加新游戏
1. 在 `games/` 目录下创建新游戏文件夹
2. 继承 `BaseGame` 和 `BaseEnv` 基类
3. 实现必要的方法
4. 在 `main.py` 中注册新游戏

### 添加新AI
1. 在 `agents/ai_bots/` 目录下创建新AI文件
2. 继承 `BaseAgent` 基类
3. 实现 `get_action` 方法
4. 在 `agents/__init__.py` 中导入

## 🎊 项目亮点

### 完成的功能
- ✅ **双游戏支持**: 五子棋和贪吃蛇
- ✅ **图形界面**: 两种GUI选择
- ✅ **多种AI**: 6种不同算法的AI
- ✅ **人机对战**: 流畅的实时对战
- ✅ **命令行模式**: 便于开发和调试
- ✅ **完整测试**: 所有功能经过验证
- ✅ **用户友好**: 简单的启动和操作

### 技术特色
- 🏗️ **模块化设计**: 易于扩展新游戏和AI
- 🎯 **Gym风格**: 标准化的环境接口
- 🧪 **测试驱动**: 完整的测试覆盖
- 📚 **文档完善**: 详细的使用说明

## 📋 作业要求

### 基本要求 
1. **修复项目错误** 
   - [x] 修复导入错误
   - [x] 修复语法错误
   - [x] 确保所有测试通过

2. **完善AI Bot** 
   - [x] 检查MinimaxBot的完整逻辑
   - [x] 检查完善MCTSBot的蒙特卡洛树搜索
   - [x] 检查完善贪吃蛇专用AI

3. **测试和验证** 
   - [x] 所有测试用例通过
   - [x] AI对战功能正常
   - [x] 人机对战功能正常
   - [x] 图形界面正常

### 扩展要求
1. **实现至少一个新游戏** 
   - [x] 至少支持双人对战模式
   - [x] 支持图形界面

2. **实现新AI Bot** 

### 额外功能
- [x] **图形界面**: 完整的pygame图形界面
- [x] **多游戏支持**: 在同一界面切换不同游戏
- [x] **实时对战**: 流畅的人机对战体验
- [x] **暂停功能**: 游戏过程中可暂停/继续
- [x] **启动脚本**: 用户友好的启动方式

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

### Github + git 的开发指南(建议预先学习git)
1. 在github上 Fork 项目
2. git clone到本地
3. 在本地创建特性分支 (`git checkout -b feature/AmazingFeature`)
4. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
5. 推送到分支 (`git push origin feature/AmazingFeature`)
6. 打开Pull Request

## 📄 许可证

MIT License

## 🐞 常见Bug与修复建议

- **导入错误/路径问题**：
  - 确保所有import语句为绝对导入，包结构完整，`__init__.py`文件齐全。
  - 如遇`ModuleNotFoundError`，请检查是否在项目根目录运行，或设置`PYTHONPATH`。
- **五子棋胜负判断/平局**：
  - 检查`get_winner`逻辑，确保棋盘下满时无胜者为平局。
- **贪吃蛇碰撞与边界**：
  - 检查蛇头与自身、对方、墙体的碰撞逻辑，确保双方同时死亡时为平局。
- **AI算法不完善**：
  - Minimax建议实现alpha-beta剪枝，MCTS建议实现UCB1选择与回传，SnakeAI建议实现A*寻路。
- **图形界面问题**：
  - 如pygame窗口无法显示，优先检查依赖和系统图形环境。
- **性能与内存**：
  - 长时间运行后如有卡顿，建议减少AI搜索深度或模拟次数。

## 🤖 AI算法完善建议

- **MinimaxBot**：
  - 实现alpha-beta剪枝，提升搜索效率。
  - 增加启发式评估函数（如活三、活四等）。
  - 支持动态深度和超时机制。
- **MCTSBot**：
  - 实现UCB1选择、节点扩展、模拟和回传机制。
  - 增加模拟次数参数，提升决策质量。
- **SnakeAI**：
  - 实现A*寻路算法，优先吃食物并避开危险。
  - 增加对手预测和安全性评估。

## 🧪 测试与验证建议

- **边界测试**：
  - 检查满棋盘、蛇撞墙、无可行动作等极端情况。
- **性能测试**：
  - 大量AI对战，观察内存和速度。
- **功能测试**：
  - 人机、AI对战、图形界面均需全流程测试。

## 🚀 扩展开发建议

- **新游戏开发**：
  - 参考`games/`目录结构，继承`BaseGame`和`BaseEnv`。
  - 推荐实现推箱子、乒乓球、吃豆人等。
- **新AI开发**：
  - 参考`agents/ai_bots/`，继承`BaseAgent`。
  - 可实现贪心、规则、搜索、强化学习等AI。

## 🤝 贡献与分支管理

- 建议采用`feature/bug-fixes`、`feature/ai-enhancement`等分支协作开发。
- 每次修复或新功能完成后及时提交并合并。
- 欢迎提交PR和Issue，完善项目。

