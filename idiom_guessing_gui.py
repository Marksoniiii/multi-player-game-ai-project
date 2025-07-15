#!/usr/bin/env python3
"""
成语猜多多游戏GUI界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import json
from typing import Dict, List, Any, Optional

from games.idiom_guessing import IdiomGuessingEnv
from agents.ai_bots.llm_idiom_bot import LLMIdiomBot
from utils.llm_manager import llm_manager


class IdiomGuessingGUI:
    """成语猜多多游戏GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 成语猜多多")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # 游戏组件
        self.env = IdiomGuessingEnv()
        self.llm_bot = LLMIdiomBot()
        
        # 游戏状态
        self.is_game_running = False
        self.current_player = ""
        self.game_mode = "single"
        self.players = []
        self.timer_thread = None
        self.timer_running = False
        
        # GUI组件
        self.setup_ui()
        
        # 启动时显示设置窗口
        self.show_settings()
    
    def setup_ui(self):
        """设置UI界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = tk.Label(main_frame, text="🎯 成语猜多多", 
                              font=("Arial", 24, "bold"), 
                              bg='#f0f0f0', fg='#2c3e50')
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # 状态信息框架
        status_frame = ttk.LabelFrame(main_frame, text="游戏状态", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 状态标签
        self.model_label = tk.Label(status_frame, text="模型：未配置", 
                                   font=("Arial", 10), bg='#f0f0f0')
        self.model_label.grid(row=0, column=0, sticky=tk.W)
        
        self.player_label = tk.Label(status_frame, text="玩家：-", 
                                    font=("Arial", 10), bg='#f0f0f0')
        self.player_label.grid(row=0, column=1, sticky=tk.W)
        
        self.mode_label = tk.Label(status_frame, text="模式：单人", 
                                  font=("Arial", 10), bg='#f0f0f0')
        self.mode_label.grid(row=0, column=2, sticky=tk.W)
        
        # 计时和得分框架
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 计时器
        timer_frame = ttk.LabelFrame(info_frame, text="倒计时", padding="5")
        timer_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)
        
        self.timer_label = tk.Label(timer_frame, text="03:00", 
                                   font=("Arial", 20, "bold"), 
                                   fg='#e74c3c', bg='#f0f0f0')
        self.timer_label.grid(row=0, column=0)
        
        # 得分
        score_frame = ttk.LabelFrame(info_frame, text="得分", padding="5")
        score_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        self.score_label = tk.Label(score_frame, text="0", 
                                   font=("Arial", 20, "bold"), 
                                   fg='#27ae60', bg='#f0f0f0')
        self.score_label.grid(row=0, column=0)
        
        # 错误计数
        error_frame = ttk.LabelFrame(info_frame, text="错误", padding="5")
        error_frame.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=5)
        
        self.error_label = tk.Label(error_frame, text="0", 
                                   font=("Arial", 20, "bold"), 
                                   fg='#e74c3c', bg='#f0f0f0')
        self.error_label.grid(row=0, column=0)
        
        # 题目显示区域
        question_frame = ttk.LabelFrame(main_frame, text="题目", padding="10")
        question_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.question_text = tk.Text(question_frame, height=4, width=60, 
                                    font=("Arial", 12), wrap=tk.WORD,
                                    bg='#ffffff', fg='#2c3e50')
        self.question_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 滚动条
        question_scrollbar = ttk.Scrollbar(question_frame, orient=tk.VERTICAL, 
                                         command=self.question_text.yview)
        question_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.question_text.configure(yscrollcommand=question_scrollbar.set)
        
        # 答案输入区域
        answer_frame = ttk.LabelFrame(main_frame, text="答案输入", padding="10")
        answer_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.answer_entry = tk.Entry(answer_frame, font=("Arial", 14), width=30)
        self.answer_entry.grid(row=0, column=0, padx=5)
        self.answer_entry.bind('<Return>', self.submit_answer)
        
        self.submit_button = tk.Button(answer_frame, text="提交答案", 
                                     command=self.submit_answer,
                                     font=("Arial", 12), bg='#3498db', fg='white')
        self.submit_button.grid(row=0, column=1, padx=5)
        
        self.hint_button = tk.Button(answer_frame, text="要提示", 
                                   command=self.get_hint,
                                   font=("Arial", 12), bg='#f39c12', fg='white')
        self.hint_button.grid(row=0, column=2, padx=5)
        
        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        self.start_button = tk.Button(control_frame, text="开始游戏", 
                                    command=self.start_game,
                                    font=("Arial", 12), bg='#27ae60', fg='white')
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = tk.Button(control_frame, text="暂停", 
                                    command=self.pause_game,
                                    font=("Arial", 12), bg='#f39c12', fg='white')
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.next_player_button = tk.Button(control_frame, text="下一玩家", 
                                          command=self.next_player,
                                          font=("Arial", 12), bg='#9b59b6', fg='white')
        self.next_player_button.grid(row=0, column=2, padx=5)
        
        self.settings_button = tk.Button(control_frame, text="设置", 
                                       command=self.show_settings,
                                       font=("Arial", 12), bg='#95a5a6', fg='white')
        self.settings_button.grid(row=0, column=3, padx=5)
        
        # 消息显示区域
        message_frame = ttk.LabelFrame(main_frame, text="消息", padding="5")
        message_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.message_text = tk.Text(message_frame, height=4, width=60, 
                                   font=("Arial", 10), wrap=tk.WORD,
                                   bg='#ecf0f1', fg='#2c3e50')
        self.message_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        question_frame.columnconfigure(0, weight=1)
        question_frame.rowconfigure(0, weight=1)
        
        # 初始状态
        self.update_ui_state()
    
    def show_settings(self):
        """显示设置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("游戏设置")
        settings_window.geometry("400x500")
        settings_window.configure(bg='#f0f0f0')
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 模型选择
        model_frame = ttk.LabelFrame(settings_window, text="语言模型选择", padding="10")
        model_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        self.model_var = tk.StringVar(value="simulator")
        models = llm_manager.get_available_models()
        
        for i, (model_id, model_name) in enumerate(models.items()):
            rb = tk.Radiobutton(model_frame, text=model_name, 
                               variable=self.model_var, value=model_id,
                               font=("Arial", 10), bg='#f0f0f0')
            rb.grid(row=i, column=0, sticky=tk.W, pady=2)
        
        # API设置
        api_frame = ttk.LabelFrame(settings_window, text="API设置", padding="10")
        api_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        tk.Label(api_frame, text="API Key:", font=("Arial", 10), bg='#f0f0f0').grid(row=0, column=0, sticky=tk.W)
        self.api_key_entry = tk.Entry(api_frame, show="*", width=30)
        self.api_key_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(api_frame, text="Base URL (可选):", font=("Arial", 10), bg='#f0f0f0').grid(row=1, column=0, sticky=tk.W)
        self.base_url_entry = tk.Entry(api_frame, width=30)
        self.base_url_entry.grid(row=1, column=1, padx=5)
        
        # 游戏模式
        mode_frame = ttk.LabelFrame(settings_window, text="游戏模式", padding="10")
        mode_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        self.mode_var = tk.StringVar(value="single")
        
        single_rb = tk.Radiobutton(mode_frame, text="单人模式", 
                                  variable=self.mode_var, value="single",
                                  font=("Arial", 10), bg='#f0f0f0')
        single_rb.grid(row=0, column=0, sticky=tk.W)
        
        pvp_rb = tk.Radiobutton(mode_frame, text="双人对战", 
                               variable=self.mode_var, value="pvp",
                               font=("Arial", 10), bg='#f0f0f0')
        pvp_rb.grid(row=1, column=0, sticky=tk.W)
        
        # 玩家设置
        player_frame = ttk.LabelFrame(settings_window, text="玩家设置", padding="10")
        player_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        tk.Label(player_frame, text="玩家1:", font=("Arial", 10), bg='#f0f0f0').grid(row=0, column=0, sticky=tk.W)
        self.player1_entry = tk.Entry(player_frame, width=20)
        self.player1_entry.insert(0, "玩家1")
        self.player1_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(player_frame, text="玩家2:", font=("Arial", 10), bg='#f0f0f0').grid(row=1, column=0, sticky=tk.W)
        self.player2_entry = tk.Entry(player_frame, width=20)
        self.player2_entry.insert(0, "玩家2")
        self.player2_entry.grid(row=1, column=1, padx=5)
        
        # 时间设置
        time_frame = ttk.LabelFrame(settings_window, text="时间设置", padding="10")
        time_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        tk.Label(time_frame, text="时间限制(秒):", font=("Arial", 10), bg='#f0f0f0').grid(row=0, column=0, sticky=tk.W)
        self.time_var = tk.StringVar(value="180")
        time_spinbox = tk.Spinbox(time_frame, from_=60, to=600, increment=30, 
                                 textvariable=self.time_var, width=10)
        time_spinbox.grid(row=0, column=1, padx=5)
        
        # 按钮
        button_frame = ttk.Frame(settings_window)
        button_frame.grid(row=5, column=0, pady=10)
        
        apply_button = tk.Button(button_frame, text="应用设置", 
                               command=lambda: self.apply_settings(settings_window),
                               font=("Arial", 12), bg='#27ae60', fg='white')
        apply_button.grid(row=0, column=0, padx=5)
        
        cancel_button = tk.Button(button_frame, text="取消", 
                                command=settings_window.destroy,
                                font=("Arial", 12), bg='#e74c3c', fg='white')
        cancel_button.grid(row=0, column=1, padx=5)
        
        # 配置网格权重
        settings_window.columnconfigure(0, weight=1)
    
    def apply_settings(self, settings_window):
        """应用设置"""
        try:
            # 配置模型
            model_type = self.model_var.get()
            api_key = self.api_key_entry.get()
            base_url = self.base_url_entry.get()
            
            if model_type != "simulator" and not api_key:
                messagebox.showerror("错误", "请输入API Key")
                return
            
            # 配置LLM
            success = llm_manager.configure_model(
                model_type=model_type,
                api_key=api_key,
                base_url=base_url
            )
            
            if not success:
                messagebox.showerror("错误", "模型配置失败")
                return
            
            llm_manager.set_current_model(model_type)
            
            # 设置游戏参数
            self.game_mode = self.mode_var.get()
            time_limit = int(self.time_var.get())
            
            # 设置玩家
            if self.game_mode == "single":
                self.players = [self.player1_entry.get() or "玩家1"]
            else:
                self.players = [
                    self.player1_entry.get() or "玩家1",
                    self.player2_entry.get() or "玩家2"
                ]
            
            # 重新初始化环境
            self.env = IdiomGuessingEnv(time_limit=time_limit)
            
            # 更新界面
            self.update_ui_state()
            
            # 显示消息
            model_name = llm_manager.get_available_models()[model_type]
            self.add_message(f"设置已应用：{model_name}，{'双人对战' if self.game_mode == 'pvp' else '单人模式'}")
            
            settings_window.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"应用设置失败: {str(e)}")
    
    def start_game(self):
        """开始游戏"""
        try:
            if not llm_manager.get_current_model():
                messagebox.showerror("错误", "请先配置语言模型")
                return
            
            # 启动游戏
            self.env.start_game(mode=self.game_mode, players=self.players)
            self.is_game_running = True
            
            # 生成第一个问题
            self.generate_new_question()
            
            # 启动计时器
            self.start_timer()
            
            # 更新界面
            self.update_ui_state()
            
            self.add_message("游戏开始！")
            
        except Exception as e:
            messagebox.showerror("错误", f"启动游戏失败: {str(e)}")
    
    def pause_game(self):
        """暂停/恢复游戏"""
        if self.is_game_running:
            self.timer_running = False
            self.is_game_running = False
            self.pause_button.config(text="恢复")
            self.add_message("游戏已暂停")
        else:
            self.timer_running = True
            self.is_game_running = True
            self.pause_button.config(text="暂停")
            self.add_message("游戏已恢复")
    
    def submit_answer(self, event=None):
        """提交答案"""
        if not self.is_game_running:
            return
        
        answer = self.answer_entry.get().strip()
        if not answer:
            return
        
        try:
            # 提交答案
            result = self.env.step(f"answer:{answer}")
            observation, reward, done, truncated, info = result
            
            action_result = info.get("action_result", {})
            
            # 清空输入框
            self.answer_entry.delete(0, tk.END)
            
            # 处理结果
            if action_result.get("correct", False):
                self.add_message(f"✅ 正确！{action_result.get('message', '')}")
                # 自动生成下一题
                if "next_question" in action_result:
                    self.display_question(action_result["next_question"])
            else:
                self.add_message(f"❌ {action_result.get('message', '答案错误')}")
            
            # 更新界面
            self.update_ui_state()
            
            # 检查游戏结束
            if done or truncated:
                self.end_game()
                
        except Exception as e:
            messagebox.showerror("错误", f"提交答案失败: {str(e)}")
    
    def get_hint(self):
        """获取提示"""
        if not self.is_game_running:
            return
        
        try:
            result = self.env.step("hint")
            observation, reward, done, truncated, info = result
            
            action_result = info.get("action_result", {})
            
            if "error" in action_result:
                self.add_message(f"❌ {action_result['error']}")
            else:
                hint = action_result.get("hint", "")
                remaining = action_result.get("remaining_hints", 0)
                self.add_message(f"💡 提示：{hint} (剩余提示次数: {remaining})")
                
        except Exception as e:
            messagebox.showerror("错误", f"获取提示失败: {str(e)}")
    
    def next_player(self):
        """切换到下一个玩家"""
        if not self.is_game_running or self.game_mode != "pvp":
            return
        
        try:
            result = self.env.step("next_player")
            observation, reward, done, truncated, info = result
            
            action_result = info.get("action_result", {})
            
            if "error" in action_result:
                self.add_message(f"❌ {action_result['error']}")
            else:
                message = action_result.get("message", "")
                self.add_message(f"🔄 {message}")
                
                # 生成新问题
                self.generate_new_question()
                
            # 更新界面
            self.update_ui_state()
            
            # 检查游戏结束
            if done or truncated:
                self.end_game()
                
        except Exception as e:
            messagebox.showerror("错误", f"切换玩家失败: {str(e)}")
    
    def generate_new_question(self):
        """生成新问题"""
        try:
            result = self.env.step("generate_question")
            observation, reward, done, truncated, info = result
            
            action_result = info.get("action_result", {})
            
            if "error" in action_result:
                self.add_message(f"❌ {action_result['error']}")
            else:
                self.display_question(action_result)
                
        except Exception as e:
            messagebox.showerror("错误", f"生成问题失败: {str(e)}")
    
    def display_question(self, question_data):
        """显示问题"""
        question = question_data.get("question", "")
        question_type = question_data.get("type", "")
        difficulty = question_data.get("difficulty", "")
        
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(tk.END, f"【{difficulty}】{question}")
        
        self.add_message(f"🎯 新题目已生成（类型：{question_type}）")
    
    def start_timer(self):
        """启动计时器"""
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self.timer_loop)
        self.timer_thread.daemon = True
        self.timer_thread.start()
    
    def timer_loop(self):
        """计时器循环"""
        while self.timer_running:
            try:
                observation = self.env._get_observation()
                remaining_time = observation.get("remaining_time", 0)
                
                if remaining_time <= 0:
                    self.timer_running = False
                    self.root.after(0, self.end_game)
                    break
                
                # 更新计时器显示
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                time_str = f"{minutes:02d}:{seconds:02d}"
                
                self.root.after(0, lambda: self.timer_label.config(text=time_str))
                
                # 时间不足警告
                if remaining_time <= 30:
                    self.root.after(0, lambda: self.timer_label.config(fg='#e74c3c'))
                elif remaining_time <= 60:
                    self.root.after(0, lambda: self.timer_label.config(fg='#f39c12'))
                
                time.sleep(1)
                
            except Exception as e:
                print(f"计时器错误: {e}")
                break
    
    def end_game(self):
        """结束游戏"""
        self.is_game_running = False
        self.timer_running = False
        
        try:
            # 获取最终统计
            stats = self.env.get_game_statistics()
            
            # 显示结果
            self.show_game_result(stats)
            
            # 更新界面
            self.update_ui_state()
            
            self.add_message("🏁 游戏结束！")
            
        except Exception as e:
            messagebox.showerror("错误", f"结束游戏失败: {str(e)}")
    
    def show_game_result(self, stats):
        """显示游戏结果"""
        result_window = tk.Toplevel(self.root)
        result_window.title("游戏结果")
        result_window.geometry("400x300")
        result_window.configure(bg='#f0f0f0')
        result_window.transient(self.root)
        result_window.grab_set()
        
        # 标题
        title_label = tk.Label(result_window, text="🏆 游戏结果", 
                              font=("Arial", 18, "bold"), 
                              bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=10)
        
        # 结果显示
        result_frame = ttk.Frame(result_window)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for i, (player, player_stats) in enumerate(stats.items()):
            player_frame = ttk.LabelFrame(result_frame, text=player, padding="10")
            player_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(player_frame, text=f"答对题数：{player_stats['correct_count']}", 
                    font=("Arial", 12), bg='#f0f0f0').pack(anchor=tk.W)
            tk.Label(player_frame, text=f"答错题数：{player_stats['wrong_count']}", 
                    font=("Arial", 12), bg='#f0f0f0').pack(anchor=tk.W)
            tk.Label(player_frame, text=f"准确率：{player_stats['accuracy']:.1%}", 
                    font=("Arial", 12), bg='#f0f0f0').pack(anchor=tk.W)
            tk.Label(player_frame, text=f"用时：{player_stats['time_used']:.1f}秒", 
                    font=("Arial", 12), bg='#f0f0f0').pack(anchor=tk.W)
        
        # 获胜者
        if self.game_mode == "pvp" and len(stats) > 1:
            scores = {player: s['correct_count'] for player, s in stats.items()}
            max_score = max(scores.values())
            winners = [player for player, score in scores.items() if score == max_score]
            
            if len(winners) == 1:
                winner_text = f"🏆 获胜者：{winners[0]}"
            else:
                winner_text = f"🤝 平局：{', '.join(winners)}"
            
            winner_label = tk.Label(result_window, text=winner_text, 
                                   font=("Arial", 14, "bold"), 
                                   bg='#f0f0f0', fg='#27ae60')
            winner_label.pack(pady=10)
        
        # 关闭按钮
        close_button = tk.Button(result_window, text="关闭", 
                               command=result_window.destroy,
                               font=("Arial", 12), bg='#3498db', fg='white')
        close_button.pack(pady=10)
    
    def update_ui_state(self):
        """更新界面状态"""
        try:
            # 获取游戏信息
            observation = self.env._get_observation()
            
            # 更新状态标签
            current_model = llm_manager.get_current_model()
            if current_model:
                model_name = llm_manager.get_available_models().get(current_model, current_model)
                self.model_label.config(text=f"模型：{model_name}")
            
            current_player = observation.get("current_player", "")
            self.player_label.config(text=f"玩家：{current_player}")
            
            mode_text = "双人对战" if self.game_mode == "pvp" else "单人模式"
            self.mode_label.config(text=f"模式：{mode_text}")
            
            # 更新得分
            self.score_label.config(text=str(observation.get("correct_count", 0)))
            self.error_label.config(text=str(observation.get("wrong_count", 0)))
            
            # 更新按钮状态
            if self.is_game_running:
                self.start_button.config(state=tk.DISABLED)
                self.pause_button.config(state=tk.NORMAL)
                self.submit_button.config(state=tk.NORMAL)
                self.hint_button.config(state=tk.NORMAL)
                self.answer_entry.config(state=tk.NORMAL)
                
                if self.game_mode == "pvp":
                    self.next_player_button.config(state=tk.NORMAL)
                else:
                    self.next_player_button.config(state=tk.DISABLED)
            else:
                self.start_button.config(state=tk.NORMAL)
                self.pause_button.config(state=tk.DISABLED, text="暂停")
                self.submit_button.config(state=tk.DISABLED)
                self.hint_button.config(state=tk.DISABLED)
                self.answer_entry.config(state=tk.DISABLED)
                self.next_player_button.config(state=tk.DISABLED)
                
        except Exception as e:
            print(f"更新界面失败: {e}")
    
    def add_message(self, message):
        """添加消息"""
        self.message_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} {message}\n")
        self.message_text.see(tk.END)
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    app = IdiomGuessingGUI()
    app.run() 