import customtkinter as ctk
import threading
import tkinter.messagebox
from tkinter import filedialog
import os
import sys
import json
import time
from datetime import datetime

# Import backend
try:
    from nlp import NLPProcessor
    import nlp 
except ImportError:
    tkinter.messagebox.showerror("Error", "Cannot find nlp.py file!")
    sys.exit(1)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class NLPApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NLP Intelligent Review Analysis & Prediction System (V9.0 Multi-Game)")
        self.geometry("950x750")
        self.resizable(True, True)

        self.processor = NLPProcessor()
        self.input_file = None
        
        # Store multiple loaded reports {filename: json_data}
        self.loaded_reports = {} 

        self._init_ui()

    def _init_ui(self):
        # Header with modern dark theme
        self.header_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10, border_width=1, border_color="#2d2d44")
        self.header_frame.pack(pady=10, padx=20, fill="x")
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="📊 Game Feedback AI Agent", 
            font=("Segoe UI", 22, "bold"),
            text_color="#e0e0e0"
        )
        self.title_label.pack(pady=12)

        # Tab view with refined styling
        self.tab_view = ctk.CTkTabview(self, fg_color="#16213e", segmented_button_fg_color="#1a1a2e", 
                                        segmented_button_selected_color="#6c5ce7", 
                                        segmented_button_selected_hover_color="#5f4dd1")
        self.tab_view.pack(pady=10, padx=20, fill="both", expand=True)
        self.tab_process = self.tab_view.add("1. Data Processing")
        self.tab_report = self.tab_view.add("2. Insights Report")
        self.tab_llm = self.tab_view.add("3. LLM Prediction")

        self._setup_process_tab()
        self._setup_report_tab()
        self._setup_llm_tab()

    def _setup_process_tab(self):
        # Card-like frame with subtle borders
        file_frame = ctk.CTkFrame(self.tab_process, fg_color="#1a1a2e", corner_radius=8, border_width=1, border_color="#2d2d44")
        file_frame.pack(pady=10, padx=10, fill="x")
        self.btn_select = ctk.CTkButton(file_frame, text="📂 Select JSON Source File", command=self.select_file,
                                         fg_color="#4a69bd", hover_color="#3c5a9a", corner_radius=6,
                                         font=("Segoe UI", 12))
        self.btn_select.pack(side="left", padx=10, pady=10)
        self.lbl_filename = ctk.CTkLabel(file_frame, text="No file selected", text_color="#808080",
                                          font=("Segoe UI", 11))
        self.lbl_filename.pack(side="left", padx=10)

        self.progress_bar = ctk.CTkProgressBar(self.tab_process, progress_color="#6c5ce7", fg_color="#2d2d44")
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)
        self.status_label = ctk.CTkLabel(self.tab_process, text="System Ready", text_color="#a0a0a0",
                                          font=("Segoe UI", 11))
        self.status_label.pack()

        # Generate new report button
        self.btn_run = ctk.CTkButton(
            self.tab_process, 
            text="🚀 Start NLP Engine (Generate New Report)", 
            command=self.start_analysis,
            state="disabled",
            fg_color="#6c5ce7",
            hover_color="#5f4dd1",
            height=40,
            corner_radius=8,
            font=("Segoe UI", 14, "bold")
        )
        self.btn_run.pack(pady=10)

        # Load history report (support multi-select)
        self.btn_load_history = ctk.CTkButton(
            self.tab_process,
            text="📂 Load Historical Reports (For LLM Analysis)",
            command=self.load_history_report,
            fg_color="#4a69bd",
            hover_color="#3c5a9a",
            corner_radius=6,
            font=("Segoe UI", 12)
        )
        self.btn_load_history.pack(pady=5)

        self.log_box = ctk.CTkTextbox(self.tab_process, height=200, fg_color="#1a1a2e", 
                                       border_width=1, border_color="#2d2d44", corner_radius=8,
                                       font=("Consolas", 11), text_color="#d0d0d0")
        self.log_box.pack(pady=10, padx=10, fill="both", expand=True)
        self.log(f"Current Compute Device: {nlp.GLOBAL_DEVICE}")

    def _setup_report_tab(self):
        self.report_box = ctk.CTkTextbox(self.tab_report, font=("Consolas", 12), 
                                          fg_color="#1a1a2e", border_width=1, border_color="#2d2d44",
                                          corner_radius=8, text_color="#d0d0d0")
        self.report_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.report_box.insert("0.0", "Please load data first...")

    def _setup_llm_tab(self):
        self.llm_frame = ctk.CTkFrame(self.tab_llm, fg_color="transparent")
        self.llm_frame.pack(fill="both", expand=True)

        # Left column input
        self.left_col = ctk.CTkFrame(self.llm_frame, width=350, fg_color="#1a1a2e", 
                                      corner_radius=8, border_width=1, border_color="#2d2d44")
        self.left_col.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.left_col, text="📝 New Game Design Proposal", 
                     font=("Segoe UI", 14, "bold"), text_color="#e0e0e0").pack(pady=8)
        self.design_input = ctk.CTkTextbox(self.left_col, height=150, fg_color="#16213e", 
                                            border_width=1, border_color="#2d2d44", corner_radius=6,
                                            font=("Segoe UI", 11), text_color="#d0d0d0")
        self.design_input.pack(fill="x", padx=8, pady=5)
        self.design_input.insert("0.0", "e.g., A hardcore souls-like game emphasizing boss battle experience...")

        ctk.CTkLabel(self.left_col, text="🎯 Target Player Audience", 
                     font=("Segoe UI", 14, "bold"), text_color="#e0e0e0").pack(pady=8)
        self.target_audience = ctk.CTkEntry(self.left_col, fg_color="#16213e", 
                                             border_width=1, border_color="#2d2d44", corner_radius=6,
                                             font=("Segoe UI", 11), text_color="#d0d0d0")
        self.target_audience.pack(fill="x", padx=8, pady=5)
        self.target_audience.insert(0, "Hardcore action players")

        self.btn_generate_prompt = ctk.CTkButton(
            self.left_col, 
            text="✨ Generate Multi-Game Prompt", 
            command=self.generate_prompt_logic,
            fg_color="#6c5ce7", 
            hover_color="#5f4dd1",
            height=40,
            corner_radius=8,
            font=("Segoe UI", 13, "bold")
        )
        self.btn_generate_prompt.pack(pady=20, padx=8)

        # Right column preview
        self.right_col = ctk.CTkFrame(self.llm_frame, fg_color="#1a1a2e", 
                                       corner_radius=8, border_width=1, border_color="#2d2d44")
        self.right_col.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(self.right_col, text="🤖 Final Prompt Preview", 
                     font=("Segoe UI", 14, "bold"), text_color="#e0e0e0").pack(pady=8)
        self.prompt_preview = ctk.CTkTextbox(self.right_col, fg_color="#16213e", 
                                              border_width=1, border_color="#2d2d44", corner_radius=6,
                                              font=("Consolas", 11), text_color="#d0d0d0")
        self.prompt_preview.pack(fill="both", expand=True, padx=8, pady=5)

    def log(self, message):
        self.log_box.insert("end", f"> {message}\n")
        self.log_box.see("end")

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            self.input_file = file_path
            self.lbl_filename.configure(text=os.path.basename(file_path), text_color="#6c5ce7")
            self.btn_run.configure(state="normal")
            self.log(f"Selected source file: {file_path}")

    def update_progress_callback(self, current_percent, message):
        self.progress_bar.set(current_percent / 100.0)
        self.status_label.configure(text=f"{message} ({current_percent}%)")
        self.update_idletasks()

    def start_analysis(self):
        self.btn_run.configure(state="disabled")
        self.progress_bar.set(0)
        threading.Thread(target=self.run_backend_logic, daemon=True).start()

    def run_backend_logic(self):
        # Auto-generate timestamped filename to prevent overwriting
        base_name = os.path.splitext(os.path.basename(self.input_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = "reports"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, f"Report_{base_name}_{timestamp}.json")

        try:
            self.log(f"🚀 Starting analysis: {base_name}")
            result = self.processor.process_file(
                self.input_file, 
                output_file, 
                progress_callback=self.update_progress_callback
            )
            
            # Auto-load to memory dictionary
            report_name = os.path.basename(output_file)
            self.loaded_reports[report_name] = result
            
            self.progress_bar.set(1)
            self.status_label.configure(text="✅ Analysis Complete")
            self.log(f"Report saved to: {output_file}")
            
            self.display_report_summary()
            tkinter.messagebox.showinfo("Complete", f"Analysis complete!\nReport loaded: {report_name}")

        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            tkinter.messagebox.showerror("Error", str(e))
        finally:
            self.btn_run.configure(state="normal")

    def load_history_report(self):
        # Support multi-file selection
        initial_dir = "reports" if os.path.exists("reports") else "."
        file_paths = filedialog.askopenfilenames(
            title="Select Historical Reports (Multiple Selection Allowed)",
            filetypes=[("JSON Reports", "*.json")],
            initialdir=initial_dir
        )
        
        if not file_paths: return

        count = 0
        for path in file_paths:
            fname = os.path.basename(path)
            if fname in self.loaded_reports: continue # Avoid duplicates
            
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
            self.log(f"📚 Successfully loaded {count} historical reports")
            self.status_label.configure(text=f"Cached {len(self.loaded_reports)} projects")
            tkinter.messagebox.showinfo("Success", f"Loaded {count} files!\nGo to Tab 3 to generate prompts.")

    def display_report_summary(self):
        """Display summary of all currently loaded reports"""
        self.report_box.delete("0.0", "end")
        
        if not self.loaded_reports:
            self.report_box.insert("0.0", "No data available. Please run analysis or load historical reports.")
            return

        text = f"📚 Current Analysis Pool ({len(self.loaded_reports)} game datasets):\n"
        text += "="*60 + "\n\n"
        
        for name, data in self.loaded_reports.items():
            total_reviews = data['statistics']['total']
            # Display the hottest topic
            top_topic = data['topics'][0] if data['topics'] else None
            top_sent = top_topic['representative_sentences'][0][:50] + "..." if top_topic else "No data"
            
            text += f"🎮 File: {name}\n"
            text += f"   - Review Count: {total_reviews}\n"
            text += f"   - Top Topic ({top_topic['sentiment_label']}): {top_sent}\n"
            text += "-"*40 + "\n"
            
        self.report_box.insert("0.0", text)

    def generate_prompt_logic(self):
        """
        Core: Assemble refined data (representative sentences + raw samples) from loaded_reports for LLM
        """
        if not self.loaded_reports:
            tkinter.messagebox.showwarning("Warning", "Please load at least one JSON report first!")
            return

        design_idea = self.design_input.get("0.0", "end").strip()
        audience = self.target_audience.get()

        # Assemble Context
        context_str = "=== COMPETITOR ANALYSIS DATA ===\n"
        
        for filename, data in self.loaded_reports.items():
            # Simplify filename as game ID
            game_id = filename.replace("Report_", "").replace(".json", "")
            
            context_str += f"\n🎮 GAME: {game_id}\n"
            context_str += "="*30 + "\n"
            
            # Only take top 5 most important topics
            for t in data['topics'][:5]:
                topic_id = t['topic_id']
                label = t['sentiment_label'].upper()
                
                # [A] Deep Insight (Representative)
                # Take the first longest, most detailed comment
                deep_insight = t['representative_sentences'][0] if t['representative_sentences'] else "N/A"
                
                # [B] Breadth Samples
                # Take first 3 from sample_texts, filter out those already in deep_insight to avoid duplicates
                raw_samples = []
                for s in t['sample_texts']:
                    # Skip if sample is too short (<5 chars) or too similar to representative sentence
                    if len(s) > 5 and s not in deep_insight:
                        raw_samples.append(s)
                    if len(raw_samples) >= 3: # Limit to 3 samples
                        break
                
                samples_str = " | ".join(raw_samples)

                # Assemble topic text
                context_str += f"📍 [Topic {topic_id}] {label}\n"
                context_str += f"   ➤ Deep Insight: \"{deep_insight}\"\n"
                context_str += f"   ➤ Player Voices: \"{samples_str}\"\n\n"
            
            context_str += "-"*30 + "\n"

        # Assemble final Prompt
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
        
        # Display
        self.prompt_preview.delete("0.0", "end")
        self.prompt_preview.insert("0.0", final_prompt)

if __name__ == "__main__":
    app = NLPApp()
    app.mainloop()