import customtkinter as ctk
import threading
import tkinter.messagebox
from tkinter import filedialog
import os
import sys

# 🔥 关键：导入你刚才保存的后端模块
try:
    from nlp import NLPProcessor
except ImportError:
    tkinter.messagebox.showerror("错误", "找不到 nlp_backend.py 文件！\n请确保后端代码已保存为 nlp_backend.py 并与本文件在同一目录下。")
    sys.exit(1)

# 设置主题
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class NLPApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 窗口设置
        self.title("NLP 智能评论分析系统 (V7 Stable)")
        self.geometry("700x500")
        self.resizable(False, False)

        # 初始化处理器
        self.processor = NLPProcessor()
        self.input_file = None

        # 布局 UI
        self._init_ui()

    def _init_ui(self):
        # 1. 标题区
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.pack(pady=20, padx=20, fill="x")
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="📊 评论情感与话题挖掘系统", 
            font=("Microsoft YaHei UI", 24, "bold")
        )
        self.title_label.pack(pady=10)

        # 2. 文件选择区
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(pady=10, padx=20, fill="x")

        self.btn_select = ctk.CTkButton(
            self.file_frame, 
            text="📂 选择 JSON 数据文件", 
            command=self.select_file,
            width=200
        )
        self.btn_select.pack(side="left", padx=20, pady=20)

        self.lbl_filename = ctk.CTkLabel(
            self.file_frame, 
            text="未选择文件", 
            text_color="gray"
        )
        self.lbl_filename.pack(side="left", padx=10)

        # 3. 进度控制区
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.pack(pady=20, padx=20, fill="x")

        self.status_label = ctk.CTkLabel(
            self.progress_frame, 
            text="准备就绪", 
            font=("Microsoft YaHei UI", 14)
        )
        self.status_label.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)

        # 4. 操作按钮区
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=10, fill="x")

        self.btn_run = ctk.CTkButton(
            self.action_frame, 
            text="🚀 开始分析", 
            command=self.start_analysis,
            state="disabled",
            fg_color="#2ecc71",
            hover_color="#27ae60",
            height=50,
            font=("Microsoft YaHei UI", 16, "bold")
        )
        self.btn_run.pack(pady=10)

        # 5. 日志输出区 (简略)
        self.log_box = ctk.CTkTextbox(self, height=100)
        self.log_box.pack(pady=10, padx=20, fill="x")
        self.log(f"系统启动...检测硬件设备...")
        # 简单显示设备信息
        try:
            import nlp_backend
            self.log(f"当前计算设备: {nlp_backend.GLOBAL_DEVICE}")
        except:
            pass

    def log(self, message):
        self.log_box.insert("end", f"> {message}\n")
        self.log_box.see("end")

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="选择评论数据文件",
            filetypes=[("JSON Files", "*.json")]
        )
        if file_path:
            self.input_file = file_path
            self.lbl_filename.configure(text=os.path.basename(file_path), text_color="white")
            self.btn_run.configure(state="normal")
            self.log(f"已加载文件: {file_path}")

    def update_progress_callback(self, current_percent, message):
        """
        这个函数会被后端调用，用于更新 GUI
        """
        # 将百分比转换为 0.0 - 1.0
        val = current_percent / 100.0
        self.progress_bar.set(val)
        self.status_label.configure(text=f"{message} ({current_percent}%)")
        self.update_idletasks() # 强制刷新 UI

    def start_analysis(self):
        if not self.input_file:
            return

        # 锁定按钮防止重复点击
        self.btn_run.configure(state="disabled", text="正在处理中...")
        self.btn_select.configure(state="disabled")
        self.progress_bar.set(0)
        
        # 开启新线程运行后端，防止界面卡死
        threading.Thread(target=self.run_backend_logic, daemon=True).start()

    def run_backend_logic(self):
        output_file = "result_report.json"
        try:
            self.log("正在初始化模型，这可能需要几秒钟...")
            
            # 调用后端处理函数
            # 注意：我们将 self.update_progress_callback 传给后端
            result = self.processor.process_file(
                self.input_file, 
                output_file, 
                progress_callback=self.update_progress_callback
            )
            
            # 完成后
            self.progress_bar.set(1)
            self.status_label.configure(text="✅ 分析完成！")
            self.log(f"分析成功！结果已保存至: {output_file}")
            
            tkinter.messagebox.showinfo("成功", f"处理完成！\n共识别话题: {len(result['topics'])} 个\n结果已保存至 {output_file}")

        except Exception as e:
            self.log(f"❌ 错误: {str(e)}")
            tkinter.messagebox.showerror("运行出错", f"发生错误:\n{str(e)}\n\n请查看 nlp_error_log.txt 获取详细信息。")
        
        finally:
            # 恢复按钮状态
            self.btn_run.configure(state="normal", text="🚀 开始分析")
            self.btn_select.configure(state="normal")

if __name__ == "__main__":
    app = NLPApp()
    app.mainloop()