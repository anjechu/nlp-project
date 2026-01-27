import customtkinter as ctk
import threading
import tkinter.messagebox
from tkinter import filedialog
import os
import sys
import json
import time
from datetime import datetime

# 🔥 导入后端
try:
    from nlp import NLPProcessor
    import nlp 
except ImportError:
    tkinter.messagebox.showerror("错误", "找不到 nlp.py 文件！")
    sys.exit(1)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class NLPApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NLP 智能评论分析与预测系统 (V9.0 Multi-Game)")
        self.geometry("950x750")
        self.resizable(True, True)

        self.processor = NLPProcessor()
        self.input_file = None
        
        # 🔴 关键修改：用于存储多个加载的报告 {filename: json_data}
        self.loaded_reports = {} 

        self._init_ui()

    def _init_ui(self):
        # 头部
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.pack(pady=10, padx=20, fill="x")
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="📊 Game Feedback AI Agent", 
            font=("Microsoft YaHei UI", 20, "bold")
        )
        self.title_label.pack(pady=5)

        # 选项卡
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(pady=10, padx=20, fill="both", expand=True)
        self.tab_process = self.tab_view.add("1. 数据清洗与分析")
        self.tab_report = self.tab_view.add("2. 核心洞察报告")
        self.tab_llm = self.tab_view.add("3. LLM 预测代理")

        self._setup_process_tab()
        self._setup_report_tab()
        self._setup_llm_tab()

    def _setup_process_tab(self):
        file_frame = ctk.CTkFrame(self.tab_process)
        file_frame.pack(pady=10, padx=10, fill="x")
        self.btn_select = ctk.CTkButton(file_frame, text="📂 选择 JSON 源文件", command=self.select_file)
        self.btn_select.pack(side="left", padx=10, pady=10)
        self.lbl_filename = ctk.CTkLabel(file_frame, text="未选择文件", text_color="gray")
        self.lbl_filename.pack(side="left", padx=10)

        self.progress_bar = ctk.CTkProgressBar(self.tab_process)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)
        self.status_label = ctk.CTkLabel(self.tab_process, text="系统就绪")
        self.status_label.pack()

        # 生成新报告
        self.btn_run = ctk.CTkButton(
            self.tab_process, 
            text="🚀 启动 NLP 引擎 (生成新报告)", 
            command=self.start_analysis,
            state="disabled",
            fg_color="#2ecc71",
            hover_color="#27ae60",
            height=40,
            font=("Microsoft YaHei UI", 14, "bold")
        )
        self.btn_run.pack(pady=10)

        # 🔴 加载历史报告 (支持多选)
        self.btn_load_history = ctk.CTkButton(
            self.tab_process,
            text="📂 批量加载历史报告 (用于 LLM 分析)",
            command=self.load_history_report,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.btn_load_history.pack(pady=5)

        self.log_box = ctk.CTkTextbox(self.tab_process, height=200)
        self.log_box.pack(pady=10, padx=10, fill="both", expand=True)
        self.log(f"当前计算设备: {nlp.GLOBAL_DEVICE}")

    def _setup_report_tab(self):
        self.report_box = ctk.CTkTextbox(self.tab_report, font=("Consolas", 12))
        self.report_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.report_box.insert("0.0", "请先加载数据...")

    def _setup_llm_tab(self):
        self.llm_frame = ctk.CTkFrame(self.tab_llm, fg_color="transparent")
        self.llm_frame.pack(fill="both", expand=True)

        # 左侧输入
        self.left_col = ctk.CTkFrame(self.llm_frame, width=350)
        self.left_col.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.left_col, text="📝 新游戏设计提案", font=("bold", 14)).pack(pady=5)
        self.design_input = ctk.CTkTextbox(self.left_col, height=150)
        self.design_input.pack(fill="x", padx=5, pady=5)
        self.design_input.insert("0.0", "例如：一款硬核的类魂游戏，强调 Boss 战体验...")

        ctk.CTkLabel(self.left_col, text="🎯 目标玩家群体", font=("bold", 14)).pack(pady=5)
        self.target_audience = ctk.CTkEntry(self.left_col)
        self.target_audience.pack(fill="x", padx=5, pady=5)
        self.target_audience.insert(0, "硬核动作玩家")

        self.btn_generate_prompt = ctk.CTkButton(
            self.left_col, 
            text="✨ 生成多游戏对比 Prompt", 
            command=self.generate_prompt_logic,
            fg_color="#9b59b6", 
            hover_color="#8e44ad",
            height=40
        )
        self.btn_generate_prompt.pack(pady=20)

        # 右侧预览
        self.right_col = ctk.CTkFrame(self.llm_frame)
        self.right_col.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(self.right_col, text="🤖 最终 Prompt 预览", font=("bold", 14)).pack(pady=5)
        self.prompt_preview = ctk.CTkTextbox(self.right_col)
        self.prompt_preview.pack(fill="both", expand=True, padx=5, pady=5)

    def log(self, message):
        self.log_box.insert("end", f"> {message}\n")
        self.log_box.see("end")

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            self.input_file = file_path
            self.lbl_filename.configure(text=os.path.basename(file_path))
            self.btn_run.configure(state="normal")
            self.log(f"已选择源文件: {file_path}")

    def update_progress_callback(self, current_percent, message):
        self.progress_bar.set(current_percent / 100.0)
        self.status_label.configure(text=f"{message} ({current_percent}%)")
        self.update_idletasks()

    def start_analysis(self):
        self.btn_run.configure(state="disabled")
        self.progress_bar.set(0)
        threading.Thread(target=self.run_backend_logic, daemon=True).start()

    def run_backend_logic(self):
        # 1. 自动生成带时间戳的文件名，防止覆盖
        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = "reports"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, f"Report_{base_name}_{timestamp}.json")

        try:
            self.log(f"🚀 启动分析: {base_name}")
            result = self.processor.process_file(
                self.input_file, 
                output_file, 
                progress_callback=self.update_progress_callback
            )
            
            # 2. 自动加载到内存字典中
            report_name = os.path.basename(output_file)
            self.loaded_reports[report_name] = result
            
            self.progress_bar.set(1)
            self.status_label.configure(text="✅ 分析完成")
            self.log(f"报告已保存至: {output_file}")
            
            self.display_report_summary()
            tkinter.messagebox.showinfo("完成", f"分析完成！\n已自动加载报告: {report_name}")

        except Exception as e:
            self.log(f"❌ 错误: {str(e)}")
            tkinter.messagebox.showerror("错误", str(e))
        finally:
            self.btn_run.configure(state="normal")

    def load_history_report(self):
        # 🔴 支持多选文件
        initial_dir = "reports" if os.path.exists("reports") else "."
        file_paths = filedialog.askopenfilenames(
            title="选择历史报告 (可多选)",
            filetypes=[("JSON Reports", "*.json")],
            initialdir=initial_dir
        )
        
        if not file_paths: return

        count = 0
        for path in file_paths:
            fname = os.path.basename(path)
            if fname in self.loaded_reports: continue # 避免重复
            
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if "topics" not in data: continue
                
                self.loaded_reports[fname] = data
                count += 1
            except Exception:
                continue
        
        if count > 0:
            self.display_report_summary()
            self.log(f"📚 成功加载 {count} 份历史报告")
            self.status_label.configure(text=f"已缓存 {len(self.loaded_reports)} 个项目")
            tkinter.messagebox.showinfo("成功", f"加载了 {count} 个文件！\n请前往 Tab 3 生成 Prompt。")

    def display_report_summary(self):
        """显示当前已加载的所有报告简报"""
        self.report_box.delete("0.0", "end")
        
        if not self.loaded_reports:
            self.report_box.insert("0.0", "暂无数据。请运行分析或加载历史报告。")
            return

        text = f"📚 当前分析池 (共 {len(self.loaded_reports)} 个游戏数据):\n"
        text += "="*60 + "\n\n"
        
        for name, data in self.loaded_reports.items():
            total_reviews = data['statistics']['total']
            # 取最热的那个话题展示一下
            top_topic = data['topics'][0] if data['topics'] else None
            top_sent = top_topic['representative_sentences'][0][:50] + "..." if top_topic else "无数据"
            
            text += f"🎮 文件: {name}\n"
            text += f"   - 评论量: {total_reviews}\n"
            text += f"   - 最热话题 ({top_topic['sentiment_label']}): {top_sent}\n"
            text += "-"*40 + "\n"
            
        self.report_box.insert("0.0", text)

    def generate_prompt_logic(self):
        """
        核心：将 loaded_reports 中的精华数据（代表句 + 原始样本）组装给 LLM
        """
        if not self.loaded_reports:
            tkinter.messagebox.showwarning("警告", "请先加载至少一个 JSON 报告！")
            return

        design_idea = self.design_input.get("0.0", "end").strip()
        audience = self.target_audience.get()

        # 1. 组装 Context
        context_str = "=== COMPETITOR ANALYSIS DATA ===\n"
        
        for filename, data in self.loaded_reports.items():
            # 简化文件名作为游戏ID
            game_id = filename.replace("Report_", "").replace(".json", "")
            
            context_str += f"\n🎮 GAME: {game_id}\n"
            context_str += "="*30 + "\n"
            
            # 只取前 5 个最重要的话题
            for t in data['topics'][:5]:
                topic_id = t['topic_id']
                label = t['sentiment_label'].upper()
                
                # --- [A] 深度观点 (Representative) ---
                # 取前 1 条最长、最有深度的评论
                deep_insight = t['representative_sentences'][0] if t['representative_sentences'] else "N/A"
                
                # --- [B] 广度样本 (Samples) ---
                # 从 sample_texts 中取前 3 条，但要过滤掉已经出现在 deep_insight 里的，避免重复
                raw_samples = []
                for s in t['sample_texts']:
                    # 如果样本太短(小于5字)或者跟代表句太像，就跳过
                    if len(s) > 5 and s not in deep_insight:
                        raw_samples.append(s)
                    if len(raw_samples) >= 3: # 限制取 3 条样本
                        break
                
                samples_str = " | ".join(raw_samples)

                # 组装这段话题的文本
                context_str += f"📍 [Topic {topic_id}] {label}\n"
                context_str += f"   ➤ Deep Insight: \"{deep_insight}\"\n"
                context_str += f"   ➤ Player Voices: \"{samples_str}\"\n\n"
            
            context_str += "-"*30 + "\n"

        # 2. 组装最终 Prompt
        final_prompt = f"""
You are an expert Game Design Consultant.

I am planning a new game project:
[MY DESIGN]
Description: {design_idea}
Target Audience: {audience}

[MARKET DATA]
I have analyzed player feedback from similar games. 
- "Deep Insight": High-quality, detailed feedback extracted by algorithms.
- "Player Voices": Raw, random comments representing the general crowd sentiment.

{context_str}

[YOUR TASK]
Based on the market data above and my design concept:
1. **Risk Analysis**: What are the most common specific complaints (e.g., UI, mechanics, bugs) across these games?
2. **Feature Suggestion**: Based on the positive "Player Voices", what small details make players happy?
3. **Innovation**: How can I differentiate my game while avoiding the reported pitfalls?
"""
        
        # 3. 显示
        self.prompt_preview.delete("0.0", "end")
        self.prompt_preview.insert("0.0", final_prompt)
        # self.log("Prompt 已生成，准备发送给 LLM API...")

if __name__ == "__main__":
    app = NLPApp()
    app.mainloop()