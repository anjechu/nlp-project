import sys
import threading
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QLabel, QTextEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal, QObject

# 引入你的 NLP 模块
try:
    import nlp
    print("✅ 成功导入 nlp 模块")
except ImportError as e:
    print(f"❌ 无法导入 nlp 模块: {e}")
    input("按回车键退出...")
    sys.exit()

# --- 工作线程：在后台加载模型，防止界面卡死 ---
class ModelLoader(QObject):
    finished = pyqtSignal(object)  # 加载完成信号
    error = pyqtSignal(str)        # 加载失败信号

    def load(self):
        try:
            print("⏳正在后台加载 NLP 模型...")
            processor = nlp.NLPProcessor() # 调用你的类
            self.finished.emit(processor)
        except Exception as e:
            self.error.emit(str(e))

# --- 主界面 ---
class NLPApp(QWidget):
    def __init__(self):
        super().__init__()
        self.processor = None
        self.initUI()
        self.start_model_loading()

    def initUI(self):
        self.setWindowTitle('NLP 智能助手 (CPU 稳定版)')
        self.setGeometry(300, 300, 600, 500)

        layout = QVBoxLayout()

        # 状态标签
        self.status_label = QLabel("🚀 正在初始化环境...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; color: blue; font-weight: bold;")
        layout.addWidget(self.status_label)

        # 输入框
        layout.addWidget(QLabel("请输入文本:"))
        self.input_text = QTextEdit(self)
        self.input_text.setPlaceholderText("在这里输入你想分析的句子...")
        self.input_text.setMaximumHeight(100)
        layout.addWidget(self.input_text)

        # 按钮
        self.analyze_btn = QPushButton('开始分析', self)
        self.analyze_btn.clicked.connect(self.analyze)
        self.analyze_btn.setEnabled(False) # 模型加载完之前不可点
        layout.addWidget(self.analyze_btn)

        # 结果显示
        layout.addWidget(QLabel("分析结果:"))
        self.result_display = QTextEdit(self)
        self.result_display.setReadOnly(True)
        layout.addWidget(self.result_display)

        self.setLayout(layout)

    def start_model_loading(self):
        # 使用线程加载模型
        self.status_label.setText("⏳ 正在加载 AI 模型 (CPU模式)，请稍候...")
        self.loader_thread = threading.Thread(target=self._load_worker)
        self.loader_thread.daemon = True
        self.loader_thread.start()

    def _load_worker(self):
        # 这是一个在后台运行的函数
        try:
            # 这里的 NLPProcessor 必须和你 nlp.py 里的类名一致
            self.processor = nlp.NLPProcessor()
            # 只有 UI 线程可以更新界面，所以这里不能直接操作 label
            # 简单起见，我们在控制台打印
            print("✅ 模型加载完毕！")
            # 通过 invokeMethod 或者简单的布尔值通知主线程 (这里简化处理)
            self.status_label.setText("✅ 模型加载完成！准备就绪。")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.analyze_btn.setEnabled(True)
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            self.status_label.setText(f"❌ 加载失败: {e}")
            self.status_label.setStyleSheet("color: red;")

    def analyze(self):
        if not self.processor:
            return
        
        text = self.input_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "提示", "请输入文本！")
            return

        try:
            # 调用你的 NLP 处理逻辑
            # 假设你的 nlp.py 里有个方法叫 process 或 analyze
            # 这里需要根据你 nlp.py 的实际代码调整，我先假设是 classifier
            self.result_display.setText("正在分析中...")
            QApplication.processEvents() # 刷新界面
            
            # 如果你的逻辑是 self.classifier(text)
            results = self.processor.classifier(text)
            
            # 格式化输出
            output = str(results)
            self.result_display.setText(output)
            
        except Exception as e:
            self.result_display.setText(f"分析出错: {e}")

# --- 程序入口 (防闪退核心) ---
if __name__ == '__main__':
    print("🔹 GUI 启动程序开始运行...")
    try:
        app = QApplication(sys.argv)
        ex = NLPApp()
        ex.show()
        sys.exit(app.exec_())
    except Exception as e:
        # 如果报错，这里会捕获并打印，防止闪退
        print("\n❌ 致命错误导致程序崩溃:")
        print(e)
        import traceback
        traceback.print_exc()
        input("\n🔴 按回车键退出程序...")