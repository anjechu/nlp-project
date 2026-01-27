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

# Import LLM report generator
try:
    from llm_report_generator import LLMReportGenerator
    from chart_generator import ReportChartGenerator
    from analysis_report_generator import AnalysisReportGenerator
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️ LLM Report Generator not available")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Color scheme constants for modern dark theme
THEME_DARK_BG = "#1a1a2e"
THEME_DARKER_BG = "#16213e"
THEME_BORDER = "#2d2d44"
THEME_ACCENT_VIOLET = "#6c5ce7"
THEME_ACCENT_VIOLET_HOVER = "#5f4dd1"
THEME_ACCENT_BLUE = "#4a69bd"
THEME_ACCENT_BLUE_HOVER = "#3c5a9a"
THEME_TEXT_PRIMARY = "#e0e0e0"
THEME_TEXT_SECONDARY = "#d0d0d0"
THEME_TEXT_MUTED = "#a0a0a0"
THEME_TEXT_DISABLED = "#808080"

class NLPApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NLP Intelligent Review Analysis & Prediction System (V9.0 Multi-Game)")
        self.geometry("950x750")
        self.resizable(True, True)

        self.processor = NLPProcessor()
        self.input_file = None
        
        # Store multiple loaded reports as a dictionary mapping filename to parsed JSON data
        # Used to cache analysis results for multi-game comparison in LLM tab
        self.loaded_reports = {}
        
        # Initialize LLM report generator if available
        self.llm_generator = None
        self.chart_generator = None
        self.analysis_report_generator = None
        self.use_ollama = False  # Can be configured via settings
        if LLM_AVAILABLE:
            try:
                # Initialize chart generator
                self.chart_generator = ReportChartGenerator(output_dir="charts")
                print("✅ Chart Generator initialized")
                
                # Try Ollama first (easier for local setup)
                import requests
                try:
                    response = requests.get('http://localhost:11434/api/tags', timeout=2)
                    if response.status_code == 200:
                        # Ollama is available
                        self.llm_generator = LLMReportGenerator(use_ollama=True, ollama_model="qwen:7b")
                        self.use_ollama = True
                        print("✅ LLM Report Generator initialized (Ollama)")
                    else:
                        raise Exception("Ollama not responding")
                except:
                    # Fallback to HuggingFace
                    self.llm_generator = LLMReportGenerator(use_ollama=False)
                    print("✅ LLM Report Generator initialized (HuggingFace)")
                
                # Initialize analysis report generator
                self.analysis_report_generator = AnalysisReportGenerator(
                    llm_generator=self.llm_generator,
                    chart_generator=self.chart_generator
                )
                print("✅ Analysis Report Generator initialized")
                
            except Exception as e:
                print(f"⚠️ Failed to initialize LLM: {e}")
                self.llm_generator = None
                self.chart_generator = None

        self._init_ui()

    def _init_ui(self):
        # Header with modern dark theme
        self.header_frame = ctk.CTkFrame(self, fg_color=THEME_DARK_BG, corner_radius=10, border_width=1, border_color=THEME_BORDER)
        self.header_frame.pack(pady=10, padx=20, fill="x")
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="📊 Game Feedback AI Agent", 
            font=("Segoe UI", 22, "bold"),
            text_color=THEME_TEXT_PRIMARY
        )
        self.title_label.pack(pady=12)

        # Tab view with refined styling
        self.tab_view = ctk.CTkTabview(self, fg_color=THEME_DARKER_BG, segmented_button_fg_color=THEME_DARK_BG, 
                                        segmented_button_selected_color=THEME_ACCENT_VIOLET, 
                                        segmented_button_selected_hover_color=THEME_ACCENT_VIOLET_HOVER)
        self.tab_view.pack(pady=10, padx=20, fill="both", expand=True)
        self.tab_process = self.tab_view.add("1. Data Processing")
        self.tab_report = self.tab_view.add("2. Insights Report")
        self.tab_llm = self.tab_view.add("3. LLM Prediction")

        self._setup_process_tab()
        self._setup_report_tab()
        self._setup_llm_tab()

    def _setup_process_tab(self):
        # Card-like frame with subtle borders
        file_frame = ctk.CTkFrame(self.tab_process, fg_color=THEME_DARK_BG, corner_radius=8, border_width=1, border_color=THEME_BORDER)
        file_frame.pack(pady=10, padx=10, fill="x")
        self.btn_select = ctk.CTkButton(file_frame, text="📂 Select JSON Source File", command=self.select_file,
                                         fg_color=THEME_ACCENT_BLUE, hover_color=THEME_ACCENT_BLUE_HOVER, corner_radius=6,
                                         font=("Segoe UI", 12))
        self.btn_select.pack(side="left", padx=10, pady=10)
        self.lbl_filename = ctk.CTkLabel(file_frame, text="No file selected", text_color=THEME_TEXT_DISABLED,
                                          font=("Segoe UI", 11))
        self.lbl_filename.pack(side="left", padx=10)

        self.progress_bar = ctk.CTkProgressBar(self.tab_process, progress_color=THEME_ACCENT_VIOLET, fg_color=THEME_BORDER)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)
        self.status_label = ctk.CTkLabel(self.tab_process, text="System Ready", text_color=THEME_TEXT_MUTED,
                                          font=("Segoe UI", 11))
        self.status_label.pack()

        # Generate new report button
        self.btn_run = ctk.CTkButton(
            self.tab_process, 
            text="🚀 Start NLP Engine (Generate New Report)", 
            command=self.start_analysis,
            state="disabled",
            fg_color=THEME_ACCENT_VIOLET,
            hover_color=THEME_ACCENT_VIOLET_HOVER,
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
            fg_color=THEME_ACCENT_BLUE,
            hover_color=THEME_ACCENT_BLUE_HOVER,
            corner_radius=6,
            font=("Segoe UI", 12)
        )
        self.btn_load_history.pack(pady=5)

        self.log_box = ctk.CTkTextbox(self.tab_process, height=200, fg_color=THEME_DARK_BG, 
                                       border_width=1, border_color=THEME_BORDER, corner_radius=8,
                                       font=("Consolas", 11), text_color=THEME_TEXT_SECONDARY)
        self.log_box.pack(pady=10, padx=10, fill="both", expand=True)
        self.log(f"Current Compute Device: {nlp.GLOBAL_DEVICE}")

    def _setup_report_tab(self):
        # Create frame for controls
        control_frame = ctk.CTkFrame(self.tab_report, fg_color=THEME_DARK_BG, 
                                      corner_radius=8, border_width=1, border_color=THEME_BORDER)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Add button to generate cross-cultural analysis
        self.btn_enhance_llm = ctk.CTkButton(
            control_frame,
            text="🌏 Generate Cross-Cultural Analysis Report",
            command=self.enhance_reports_with_llm,
            fg_color=THEME_ACCENT_VIOLET,
            hover_color=THEME_ACCENT_VIOLET_HOVER,
            corner_radius=6,
            font=("Segoe UI", 11, "bold"),
            state="disabled" if not LLM_AVAILABLE else "normal"
        )
        self.btn_enhance_llm.pack(side="left", padx=10, pady=8)
        
        # Status label for LLM enhancement
        self.llm_status_label = ctk.CTkLabel(
            control_frame,
            text="LLM Ready" if LLM_AVAILABLE else "LLM Not Available",
            text_color=THEME_ACCENT_VIOLET if LLM_AVAILABLE else THEME_TEXT_MUTED,
            font=("Segoe UI", 10)
        )
        self.llm_status_label.pack(side="left", padx=10)
        
        # Report display
        self.report_box = ctk.CTkTextbox(self.tab_report, font=("Consolas", 11), 
                                          fg_color=THEME_DARK_BG, border_width=1, border_color=THEME_BORDER,
                                          corner_radius=8, text_color=THEME_TEXT_SECONDARY, wrap="word")
        self.report_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.report_box.insert("0.0", "Please load data first...")

    def _setup_llm_tab(self):
        self.llm_frame = ctk.CTkFrame(self.tab_llm, fg_color="transparent")
        self.llm_frame.pack(fill="both", expand=True)

        # Left column input
        self.left_col = ctk.CTkFrame(self.llm_frame, width=350, fg_color=THEME_DARK_BG, 
                                      corner_radius=8, border_width=1, border_color=THEME_BORDER)
        self.left_col.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.left_col, text="📝 New Game Design Proposal", 
                     font=("Segoe UI", 14, "bold"), text_color=THEME_TEXT_PRIMARY).pack(pady=8)
        self.design_input = ctk.CTkTextbox(self.left_col, height=150, fg_color=THEME_DARKER_BG, 
                                            border_width=1, border_color=THEME_BORDER, corner_radius=6,
                                            font=("Segoe UI", 11), text_color=THEME_TEXT_SECONDARY)
        self.design_input.pack(fill="x", padx=8, pady=5)
        self.design_input.insert("0.0", "e.g., A hardcore souls-like game emphasizing boss battle experience...")

        ctk.CTkLabel(self.left_col, text="🎯 Target Player Audience", 
                     font=("Segoe UI", 14, "bold"), text_color=THEME_TEXT_PRIMARY).pack(pady=8)
        self.target_audience = ctk.CTkEntry(self.left_col, fg_color=THEME_DARKER_BG, 
                                             border_width=1, border_color=THEME_BORDER, corner_radius=6,
                                             font=("Segoe UI", 11), text_color=THEME_TEXT_SECONDARY)
        self.target_audience.pack(fill="x", padx=8, pady=5)
        self.target_audience.insert(0, "Hardcore action players")

        self.btn_generate_prompt = ctk.CTkButton(
            self.left_col, 
            text="✨ Generate Multi-Game Prompt", 
            command=self.generate_prompt_logic,
            fg_color=THEME_ACCENT_VIOLET, 
            hover_color=THEME_ACCENT_VIOLET_HOVER,
            height=40,
            corner_radius=8,
            font=("Segoe UI", 13, "bold")
        )
        self.btn_generate_prompt.pack(pady=20, padx=8)

        # Right column preview
        self.right_col = ctk.CTkFrame(self.llm_frame, fg_color=THEME_DARK_BG, 
                                       corner_radius=8, border_width=1, border_color=THEME_BORDER)
        self.right_col.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(self.right_col, text="🤖 Final Prompt Preview", 
                     font=("Segoe UI", 14, "bold"), text_color=THEME_TEXT_PRIMARY).pack(pady=8)
        self.prompt_preview = ctk.CTkTextbox(self.right_col, fg_color=THEME_DARKER_BG, 
                                              border_width=1, border_color=THEME_BORDER, corner_radius=6,
                                              font=("Consolas", 11), text_color=THEME_TEXT_SECONDARY)
        self.prompt_preview.pack(fill="both", expand=True, padx=8, pady=5)

    def log(self, message):
        self.log_box.insert("end", f"> {message}\n")
        self.log_box.see("end")

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            self.input_file = file_path
            self.lbl_filename.configure(text=os.path.basename(file_path), text_color=THEME_ACCENT_VIOLET)
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
            if fname in self.loaded_reports: continue  # Avoid duplicates
            
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
        text += "="*80 + "\n\n"
        
        for name, data in self.loaded_reports.items():
            total_reviews = data['statistics']['total']
            valid_reviews = data['statistics'].get('valid', total_reviews)
            topics = data.get('topics', [])
            is_enhanced = data.get('llm_enhanced', False)
            
            text += f"🎮 FILE: {name}\n"
            text += f"{'─'*80}\n"
            text += f"📊 Review Count: {total_reviews} total | {valid_reviews} analyzed\n"
            text += f"🏷️  Topics Found: {len(topics)}\n"
            text += f"{'✨ LLM Enhanced' if is_enhanced else '📝 Basic Analysis'}\n\n"
            
            # Display all valuable topics (or top 10 if too many for display)
            display_limit = min(len(topics), 10) if len(topics) > 0 else 0
            for idx, topic in enumerate(topics[:display_limit], 1):
                topic_id = topic.get('topic_id', idx)
                density = topic.get('density', 0)
                sentiment = topic.get('sentiment_label', 'neutral')
                score = topic.get('sentiment_score', 0)
                topic_name = topic.get('topic_name', f'Topic {topic_id}')
                
                # Sentiment emoji
                sentiment_emoji = {'positive': '😊', 'negative': '😞', 'neutral': '😐'}
                emoji = sentiment_emoji.get(sentiment.lower(), '😐')
                
                text += f"  {idx}. 📌 {topic_name.upper()}\n"
                text += f"     {emoji} Sentiment: {sentiment.capitalize()} ({score:+.3f})\n"
                text += f"     👥 Mentions: {density} players\n"
                
                # Show LLM summary if available
                if 'summary' in topic:
                    summary = topic['summary'][:150]
                    text += f"     💡 Insight: {summary}{'...' if len(topic['summary']) > 150 else ''}\n"
                
                # Show cross-cultural analysis if available
                if 'cultural_analysis' in topic:
                    cultural = topic['cultural_analysis']
                    dist = cultural.get('distribution', {})
                    if dist:
                        cultures_str = ' | '.join([f"{culture}: {count}" for culture, count in dist.items()])
                        text += f"     🌍 Cultural: {cultures_str}\n"
                    
                    # Show LLM cultural insight if available
                    if 'llm_insight' in cultural:
                        insight = cultural['llm_insight'][:120]
                        text += f"     🗺️  Cross-Cultural: {insight}{'...' if len(cultural['llm_insight']) > 120 else ''}\n"
                
                # Show representative sentence
                rep_sentences = topic.get('representative_sentences', [])
                if rep_sentences:
                    text += f"     💬 Example: \"{rep_sentences[0][:80]}{'...' if len(rep_sentences[0]) > 80 else ''}\"\n"
                
                text += "\n"
            
            # Show note if there are more topics
            if len(topics) > display_limit:
                text += f"  📝 ... and {len(topics) - display_limit} more topics (view full report for complete analysis)\n\n"
            
            # Show overall cultural summary if available
            if 'cultural_summary' in data:
                text += f"  🌏 CROSS-CULTURAL SUMMARY:\n"
                summary = data['cultural_summary']
                # Wrap text nicely
                words = summary.split()
                line = "     "
                for word in words:
                    if len(line) + len(word) + 1 > 80:
                        text += line + "\n"
                        line = "     " + word
                    else:
                        line += " " + word if line != "     " else word
                if line != "     ":
                    text += line + "\n"
                text += "\n"
            
            # Show charts data if available
            if 'charts' in data:
                charts = data['charts']
                if 'sentiment_distribution' in charts:
                    dist = charts['sentiment_distribution']
                    text += f"  📊 SENTIMENT OVERVIEW:\n"
                    text += f"     😊 Positive: {dist.get('positive', 0)} | "
                    text += f"😐 Neutral: {dist.get('neutral', 0)} | "
                    text += f"😞 Negative: {dist.get('negative', 0)}\n"
                
                if 'sentiment_score_stats' in charts:
                    stats = charts['sentiment_score_stats']
                    text += f"     Average Score: {stats.get('mean', 0):.3f} "
                    text += f"(σ={stats.get('std', 0):.3f})\n"
            
            # Show chart file locations if available
            if 'chart_files' in data and data['chart_files']:
                text += f"\n  📈 GENERATED CHARTS:\n"
                for chart_type, path in data['chart_files'].items():
                    chart_name = chart_type.replace('_', ' ').title()
                    text += f"     • {chart_name}: {path}\n"
            
            text += f"\n{'─'*80}\n\n"
            
        self.report_box.insert("0.0", text)
    
    def enhance_reports_with_llm(self):
        """Generate comprehensive cross-cultural analysis report"""
        if not self.analysis_report_generator:
            tkinter.messagebox.showwarning("Analysis Generator Not Available", 
                                            "Analysis report generator is not initialized. Please check your setup.")
            return
        
        if not self.loaded_reports:
            tkinter.messagebox.showwarning("No Data", 
                                            "Please load or generate NLP reports first before creating analysis.")
            return
        
        # Run analysis generation in background thread
        self.btn_enhance_llm.configure(state="disabled")
        self.llm_status_label.configure(text="Generating cross-cultural analysis...")
        threading.Thread(target=self._run_analysis_generation, daemon=True).start()
    
    def _run_analysis_generation(self):
        """Background task to generate ONE aggregated analysis report from ALL loaded reports"""
        try:
            # Collect all NLP data
            all_reports = list(self.loaded_reports.values())
            report_names = list(self.loaded_reports.keys())
            
            if not all_reports:
                self.after(0, lambda: tkinter.messagebox.showwarning(
                    "No Reports", 
                    "Please load or generate NLP reports first before creating analysis."
                ))
                return
            
            # Update status
            self.after(0, lambda: 
                self.llm_status_label.configure(
                    text=f"Aggregating {len(all_reports)} reports into unified analysis..."
                ))
            
            # Generate ONE comprehensive cross-cultural analysis from ALL reports
            # Pass report filenames for parsing game/language metadata
            html_path = self.analysis_report_generator.generate_analysis_report(
                all_reports,  # Pass all reports as a list
                output_dir="analysis",
                report_filenames=report_names  # Pass filenames for parsing
            )
            
            self.log(f"🌏 Unified cross-cultural analysis generated: {html_path}")
            self.log(f"📊 Analyzed {len(all_reports)} reports: {', '.join(report_names[:3])}{'...' if len(report_names) > 3 else ''}")
            
            # Update display (show original NLP data, not modified)
            self.after(0, self.display_report_summary)
            self.after(0, lambda: self.llm_status_label.configure(
                text=f"Analysis complete: {len(all_reports)} reports aggregated"
            ))
            
            # Show completion message
            message = f"Successfully generated unified cross-cultural analysis!\n\n"
            message += f"📊 Reports Analyzed: {len(all_reports)}\n"
            message += f"   {', '.join(name[:30] for name in report_names[:5])}\n"
            if len(report_names) > 5:
                message += f"   ... and {len(report_names) - 5} more\n"
            message += "\n"
            message += f"📁 Analysis report (HTML): {os.path.basename(html_path)}\n"
            message += "📊 Chart images: analysis/*.png\n"
            message += "📄 Analysis data (JSON): analysis/*.json\n\n"
            message += "⚠️ Note: Original NLP reports in 'reports/' folder remain untouched.\n"
            message += "         All reports have been aggregated into ONE comprehensive analysis."
            
            self.after(0, lambda: tkinter.messagebox.showinfo("Analysis Complete", message))
            
            # Open the analysis report in browser
            import webbrowser
            try:
                webbrowser.open('file://' + os.path.abspath(html_path))
                self.log(f"📖 Opened analysis report in browser")
            except Exception as e:
                self.log(f"⚠️ Could not open browser: {e}")
            
        except Exception as e:
            self.log(f"❌ Analysis Generation Error: {str(e)}")
            import traceback
            traceback.print_exc()
            self.after(0, lambda: tkinter.messagebox.showerror("Analysis Failed", 
                                          f"Failed to generate analysis: {str(e)}"))
            self.after(0, lambda: self.llm_status_label.configure(text="Analysis failed"))
        
        finally:
            self.after(0, lambda: self.btn_enhance_llm.configure(state="normal"))

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
            
            # Use all valuable topics (already filtered by LLM), not just top 5
            for t in data['topics']:
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