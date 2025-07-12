import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
from typing import Dict, Any

from games.idiom_guessing.idiom_guessing_env import IdiomGuessingEnv
from agents.ai_bots.gemini_idiom_bot import GeminiIdiomBot


class IdiomGuessingGUI:
    """成语猜多多游戏GUI"""
    
    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self.is_main_window = True
        else:
            self.root = root
            self.is_main_window = False
        
        self.root.title("成语猜多多")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # 游戏相关
        self.llm_bot = None
        self.env = None
        self.game_running = False
        self.api_key = None
        
        # GUI组件
        self.setup_ui()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = tk.Label(main_frame, text="🎯 成语猜多多", 
                              font=("Arial", 24, "bold"), 
                              bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # API密钥设置区域
        self.setup_api_frame(main_frame)
        
        # 玩家信息区域
        self.setup_player_frame(main_frame)
        
        # 游戏区域
        self.setup_game_frame(main_frame)
        
        # 控制按钮区域
        self.setup_control_frame(main_frame)
        
        # 状态栏
        self.setup_status_frame(main_frame)
    
    def setup_api_frame(self, parent):
        """设置API密钥区域"""
        api_frame = tk.LabelFrame(parent, text="🔑 API设置", 
                                 font=("Arial", 12, "bold"),
                                 bg='#f0f0f0', fg='#34495e')
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        api_inner_frame = tk.Frame(api_frame, bg='#f0f0f0')
        api_inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(api_inner_frame, text="Gemini API密钥:", 
                font=("Arial", 10), bg='#f0f0f0').pack(side=tk.LEFT)
        
        self.api_key_var = tk.StringVar()
        self.api_entry = tk.Entry(api_inner_frame, textvariable=self.api_key_var,
                                 font=("Arial", 10), width=40, show="*")
        self.api_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        self.set_api_btn = tk.Button(api_inner_frame, text="设置API", 
                                    command=self.set_api_key,
                                    font=("Arial", 10), bg='#3498db', fg='white')
        self.set_api_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # API状态指示器
        self.api_status_label = tk.Label(api_inner_frame, text="❌ 未设置", 
                                        font=("Arial", 10), bg='#f0f0f0', fg='#e74c3c')
        self.api_status_label.pack(side=tk.LEFT, padx=(10, 0))
    
    def setup_player_frame(self, parent):
        """设置玩家信息区域"""
        player_frame = tk.LabelFrame(parent, text="👥 玩家信息", 
                                   font=("Arial", 12, "bold"),
                                   bg='#f0f0f0', fg='#34495e')
        player_frame.pack(fill=tk.X, pady=(0, 10))
        
        player_inner_frame = tk.Frame(player_frame, bg='#f0f0f0')
        player_inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 玩家1
        player1_frame = tk.Frame(player_inner_frame, bg='#f0f0f0')
        player1_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(player1_frame, text="玩家1:", 
                font=("Arial", 10), bg='#f0f0f0').pack(anchor=tk.W)
        self.player1_name_var = tk.StringVar(value="玩家1")
        tk.Entry(player1_frame, textvariable=self.player1_name_var,
                font=("Arial", 10), width=15).pack(anchor=tk.W, pady=(5, 0))
        
        # 玩家2
        player2_frame = tk.Frame(player_inner_frame, bg='#f0f0f0')
        player2_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(player2_frame, text="玩家2:", 
                font=("Arial", 10), bg='#f0f0f0').pack(anchor=tk.W)
        self.player2_name_var = tk.StringVar(value="玩家2")
        tk.Entry(player2_frame, textvariable=self.player2_name_var,
                font=("Arial", 10), width=15).pack(anchor=tk.W, pady=(5, 0))
    
    def setup_game_frame(self, parent):
        """设置游戏区域"""
        game_frame = tk.LabelFrame(parent, text="🎮 游戏区域", 
                                 font=("Arial", 12, "bold"),
                                 bg='#f0f0f0', fg='#34495e')
        game_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 游戏状态显示
        status_frame = tk.Frame(game_frame, bg='#f0f0f0')
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 当前玩家和分数
        self.current_player_label = tk.Label(status_frame, text="当前玩家: 等待开始", 
                                           font=("Arial", 12, "bold"),
                                           bg='#f0f0f0', fg='#2c3e50')
        self.current_player_label.pack(anchor=tk.W)
        
        # 分数和时间显示
        score_time_frame = tk.Frame(status_frame, bg='#f0f0f0')
        score_time_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.player1_info_label = tk.Label(score_time_frame, text="玩家1: 0分 | 时间: 180秒", 
                                         font=("Arial", 10), bg='#f0f0f0', fg='#27ae60')
        self.player1_info_label.pack(side=tk.LEFT)
        
        self.player2_info_label = tk.Label(score_time_frame, text="玩家2: 0分 | 时间: 180秒", 
                                         font=("Arial", 10), bg='#f0f0f0', fg='#e67e22')
        self.player2_info_label.pack(side=tk.RIGHT)
        
        # 问题显示区域
        question_frame = tk.Frame(game_frame, bg='#f0f0f0')
        question_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        tk.Label(question_frame, text="📝 当前问题:", 
                font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#34495e').pack(anchor=tk.W)
        
        self.question_text = tk.Text(question_frame, height=4, width=80,
                                   font=("Arial", 11), bg='#ecf0f1', fg='#2c3e50',
                                   wrap=tk.WORD, state=tk.DISABLED)
        self.question_text.pack(fill=tk.X, pady=(5, 0))
        
        # 答案输入区域
        answer_frame = tk.Frame(game_frame, bg='#f0f0f0')
        answer_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        tk.Label(answer_frame, text="✍️ 您的答案:", 
                font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#34495e').pack(anchor=tk.W)
        
        answer_input_frame = tk.Frame(answer_frame, bg='#f0f0f0')
        answer_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.answer_var = tk.StringVar()
        self.answer_entry = tk.Entry(answer_input_frame, textvariable=self.answer_var,
                                   font=("Arial", 12), width=30)
        self.answer_entry.pack(side=tk.LEFT)
        self.answer_entry.bind('<Return>', self.submit_answer)
        
        self.submit_btn = tk.Button(answer_input_frame, text="提交答案", 
                                  command=self.submit_answer,
                                  font=("Arial", 11), bg='#27ae60', fg='white')
        self.submit_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # 反馈和提示区域
        feedback_frame = tk.Frame(game_frame, bg='#f0f0f0')
        feedback_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        tk.Label(feedback_frame, text="💬 反馈信息:", 
                font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#34495e').pack(anchor=tk.W)
        
        self.feedback_text = tk.Text(feedback_frame, height=3, width=80,
                                   font=("Arial", 10), bg='#fdf2e9', fg='#2c3e50',
                                   wrap=tk.WORD, state=tk.DISABLED)
        self.feedback_text.pack(fill=tk.X, pady=(5, 0))
    
    def setup_control_frame(self, parent):
        """设置控制按钮区域"""
        control_frame = tk.Frame(parent, bg='#f0f0f0')
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_btn = tk.Button(control_frame, text="🚀 开始游戏", 
                                 command=self.start_game,
                                 font=("Arial", 12, "bold"), 
                                 bg='#2ecc71', fg='white', width=12)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.reset_btn = tk.Button(control_frame, text="🔄 重置游戏", 
                                 command=self.reset_game,
                                 font=("Arial", 12, "bold"), 
                                 bg='#f39c12', fg='white', width=12)
        self.reset_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.switch_btn = tk.Button(control_frame, text="🔄 切换玩家", 
                                  command=self.switch_player,
                                  font=("Arial", 12, "bold"), 
                                  bg='#3498db', fg='white', width=12)
        self.switch_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.quit_btn = tk.Button(control_frame, text="❌ 退出", 
                                command=self.on_closing,
                                font=("Arial", 12, "bold"), 
                                bg='#e74c3c', fg='white', width=12)
        self.quit_btn.pack(side=tk.RIGHT)
    
    def setup_status_frame(self, parent):
        """设置状态栏"""
        status_frame = tk.Frame(parent, bg='#34495e', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="准备就绪", 
                                   font=("Arial", 10), bg='#34495e', fg='white')
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    def set_api_key(self):
        """设置API密钥"""
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("错误", "请输入API密钥")
            return
        
        try:
            self.api_key = api_key
            self.llm_bot = GeminiIdiomBot(api_key)
            self.api_status_label.config(text="✅ 已设置", fg='#27ae60')
            self.update_status("API密钥设置完成")
            
            # 创建或更新环境
            if self.env is None:
                self.env = IdiomGuessingEnv(self.llm_bot)
                self.setup_callbacks()
                self.update_status("游戏环境初始化完成")
            else:
                self.env.set_llm_bot(self.llm_bot)
                self.update_status("游戏环境更新完成")
            
            # 显示配额提醒
            messagebox.showinfo("API密钥设置成功", 
                              "✅ API密钥设置成功！\n\n"
                              "💡 温馨提示：\n"
                              "• Gemini免费版每天限制50次请求\n"
                              "• 如果超出配额，游戏会自动使用备用题库\n"
                              "• 备用题库包含15道精选成语题目\n"
                              "• 您现在可以开始游戏了！")
                
        except Exception as e:
            messagebox.showerror("错误", f"设置API密钥失败: {str(e)}")
            self.api_status_label.config(text="❌ 设置失败", fg='#e74c3c')
            self.update_status("API密钥设置失败")
            print(f"详细错误信息: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_callbacks(self):
        """设置游戏回调"""
        if self.env:
            self.env.set_callback('game_started', self.on_game_started)
            self.env.set_callback('new_question', self.on_new_question)
            self.env.set_callback('answer_submitted', self.on_answer_submitted)
            self.env.set_callback('time_update', self.on_time_update)
            self.env.set_callback('time_up', self.on_time_up)
            self.env.set_callback('player_switched', self.on_player_switched)
            self.env.set_callback('game_ended', self.on_game_ended)
            self.env.set_callback('error', self.on_error)
    
    def start_game(self):
        """开始游戏"""
        if not self.api_key:
            messagebox.showerror("错误", "请先设置API密钥")
            return
        
        if not self.env:
            messagebox.showerror("错误", "游戏环境未初始化")
            return
        
        player1_name = self.player1_name_var.get().strip() or "玩家1"
        player2_name = self.player2_name_var.get().strip() or "玩家2"
        
        try:
            self.env.start_game(player1_name, player2_name)
            self.game_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.reset_btn.config(state=tk.NORMAL)
            self.switch_btn.config(state=tk.NORMAL)
            self.answer_entry.config(state=tk.NORMAL)
            self.submit_btn.config(state=tk.NORMAL)
            self.update_status("游戏开始！")
        except Exception as e:
            messagebox.showerror("错误", f"开始游戏失败: {str(e)}")
    
    def reset_game(self):
        """重置游戏"""
        if self.env:
            self.env.reset()
        
        self.game_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.reset_btn.config(state=tk.DISABLED)
        self.switch_btn.config(state=tk.DISABLED)
        self.answer_entry.config(state=tk.DISABLED)
        self.submit_btn.config(state=tk.DISABLED)
        
        # 重置显示
        self.current_player_label.config(text="当前玩家: 等待开始")
        self.player1_info_label.config(text="玩家1: 0分 | 时间: 180秒")
        self.player2_info_label.config(text="玩家2: 0分 | 时间: 180秒")
        self.question_text.config(state=tk.NORMAL)
        self.question_text.delete(1.0, tk.END)
        self.question_text.config(state=tk.DISABLED)
        self.feedback_text.config(state=tk.NORMAL)
        self.feedback_text.delete(1.0, tk.END)
        self.feedback_text.config(state=tk.DISABLED)
        self.answer_var.set("")
        
        self.update_status("游戏已重置")
    
    def switch_player(self):
        """切换玩家"""
        if self.env and self.game_running:
            self.env.switch_player()
    
    def submit_answer(self, event=None):
        """提交答案"""
        if not self.game_running:
            return
        
        if not self.env:
            messagebox.showerror("错误", "游戏环境未初始化")
            return
        
        answer = self.answer_var.get().strip()
        if not answer:
            messagebox.showwarning("警告", "请输入答案")
            return
        
        try:
            result = self.env.submit_answer(answer)
            self.answer_var.set("")  # 清空输入框
        except Exception as e:
            messagebox.showerror("错误", f"提交答案失败: {str(e)}")
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
    
    def update_display(self, state):
        """更新显示"""
        # 更新当前玩家
        self.current_player_label.config(text=f"当前玩家: {state.get('current_player', '无')}")
        
        # 更新分数和时间
        player1 = state.get('player1', {})
        player2 = state.get('player2', {})
        
        p1_name = player1.get('name', '玩家1')
        p1_score = player1.get('score', 0)
        p1_time = player1.get('time_remaining', 180)
        
        p2_name = player2.get('name', '玩家2')
        p2_score = player2.get('score', 0)
        p2_time = player2.get('time_remaining', 180)
        
        self.player1_info_label.config(text=f"{p1_name}: {p1_score}分 | 时间: {p1_time:.1f}秒")
        self.player2_info_label.config(text=f"{p2_name}: {p2_score}分 | 时间: {p2_time:.1f}秒")
    
    # 游戏事件回调
    def on_game_started(self, data):
        """游戏开始回调"""
        self.root.after(0, lambda: self.update_status(f"游戏开始！当前玩家: {data['current_player']}"))
    
    def on_new_question(self, data):
        """新问题回调"""
        def update_question():
            self.question_text.config(state=tk.NORMAL)
            self.question_text.delete(1.0, tk.END)
            self.question_text.insert(1.0, data['question'])
            self.question_text.config(state=tk.DISABLED)
            self.update_status(f"新问题已生成 - {data['player']}")
        
        self.root.after(0, update_question)
    
    def on_answer_submitted(self, data):
        """答案提交回调"""
        def update_feedback():
            self.feedback_text.config(state=tk.NORMAL)
            self.feedback_text.delete(1.0, tk.END)
            
            if data['correct']:
                self.feedback_text.insert(1.0, f"✅ {data['message']}")
            else:
                self.feedback_text.insert(1.0, f"❌ {data['message']}")
                if 'hint' in data:
                    self.feedback_text.insert(tk.END, f"\n💡 提示: {data['hint']}")
            
            self.feedback_text.config(state=tk.DISABLED)
            
            # 更新显示
            if self.env:
                state = self.env.get_game_state()
                self.update_display(state)
        
        self.root.after(0, update_feedback)
    
    def on_time_update(self, data):
        """时间更新回调"""
        def update_time():
            if self.env:
                state = self.env.get_game_state()
                self.update_display(state)
        
        self.root.after(0, update_time)
    
    def on_time_up(self, data):
        """时间结束回调"""
        def show_time_up():
            self.feedback_text.config(state=tk.NORMAL)
            self.feedback_text.delete(1.0, tk.END)
            self.feedback_text.insert(1.0, f"⏰ 时间到！{data['player']}得分: {data['score']}")
            self.feedback_text.config(state=tk.DISABLED)
            self.update_status(f"{data['player']}时间到！")
            
            # 如果需要切换玩家，在主线程中处理
            if data.get('should_switch', False) and self.env:
                self.env.switch_player()
        
        self.root.after(0, show_time_up)
    
    def on_player_switched(self, data):
        """玩家切换回调"""
        def update_switch():
            self.update_status(f"切换到{data['current_player']}")
            if self.env:
                state = self.env.get_game_state()
                self.update_display(state)
        
        self.root.after(0, update_switch)
    
    def on_game_ended(self, data):
        """游戏结束回调"""
        def show_result():
            result_message = f"🎉 游戏结束！\n\n"
            result_message += f"获胜者: {data['winner']}\n"
            result_message += f"玩家1得分: {data['player1_score']}\n"
            result_message += f"玩家2得分: {data['player2_score']}\n"
            result_message += f"游戏时长: {data['game_duration']:.1f}秒"
            
            messagebox.showinfo("游戏结束", result_message)
            self.game_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.reset_btn.config(state=tk.DISABLED)
            self.switch_btn.config(state=tk.DISABLED)
            self.answer_entry.config(state=tk.DISABLED)
            self.submit_btn.config(state=tk.DISABLED)
        
        self.root.after(0, show_result)
    
    def on_error(self, data):
        """错误回调"""
        def show_error():
            messagebox.showerror("错误", data['message'])
        
        self.root.after(0, show_error)
    
    def on_closing(self):
        """窗口关闭事件"""
        if self.env:
            self.env.close()
        
        if self.is_main_window:
            self.root.quit()
        else:
            self.root.destroy()
    
    def run(self):
        """运行GUI"""
        if self.is_main_window:
            self.root.mainloop()


def main():
    """主函数"""
    gui = IdiomGuessingGUI()
    gui.run()


if __name__ == "__main__":
    main() 