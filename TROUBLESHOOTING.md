# Troubleshooting Guide

## GUI 闪退问题 (GUI Crash Issues)

### 症状 (Symptoms)
GUI 在显示以下消息后突然关闭：
```
🚀 成功激活 AMD GPU 加速
❤️ 正在初始化情感分析模型...
  📥 下载/加载 tokenizer...
```

### 常见原因 (Common Causes)

#### 1. 首次运行 - 模型下载超时
**问题**: 首次运行需要从 HuggingFace 下载 ~500MB 的模型文件，可能因网络问题导致超时或下载失败。

**解决方案**:
- 确保网络连接稳定
- 如果在中国大陆，可能需要配置代理或镜像
- 设置环境变量使用镜像站：
  ```bash
  set HF_ENDPOINT=https://hf-mirror.com
  python gui.py
  ```

#### 2. GPU 兼容性问题
**问题**: AMD DirectML 可能与某些 PyTorch 版本或模型不兼容。

**解决方案 - 使用 CPU 模式**:
创建 `gui_cpu.py` 文件并使用以下代码：
```python
import os
os.environ['FORCE_CPU'] = '1'  # Force CPU mode
exec(open('gui.py').read())
```

或者修改 `nlp.py` 第 41 行:
```python
# 原来的代码
GPU_DEVICE = get_device()

# 改为强制 CPU
GPU_DEVICE = torch.device("cpu")
print("🐢 强制使用 CPU 模式")
```

#### 3. GPU 内存不足
**问题**: GPU 显存不足以加载模型。

**解决方案**:
- 关闭其他使用 GPU 的程序
- 使用 CPU 模式（见上方）

#### 4. 防火墙/代理问题
**问题**: 防火墙或代理阻止访问 huggingface.co。

**解决方案**:
- 临时禁用防火墙测试
- 配置代理：
  ```bash
  set HTTP_PROXY=http://your-proxy:port
  set HTTPS_PROXY=http://your-proxy:port
  python gui.py
  ```

### 调试步骤 (Debug Steps)

#### 1. 查看完整错误信息
在命令行运行而不是双击运行：
```bash
cd D:\桌面\test\nlp-project-copilot-integrate-gui-with-nlp-code
python gui.py
```

查看是否有错误信息输出。

#### 2. 测试模型下载
单独测试模型下载：
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

print("开始下载 tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-xlm-roberta-base-sentiment")
print("✓ Tokenizer 下载成功")

print("开始下载模型...")
model = AutoModelForSequenceClassification.from_pretrained(
    "cardiffnlp/twitter-xlm-roberta-base-sentiment", 
    use_safetensors=True
)
print("✓ 模型下载成功")
```

#### 3. 检查依赖版本
```bash
python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import transformers; print('Transformers:', transformers.__version__)"
python -c "import PyQt5; print('PyQt5: OK')"
```

#### 4. 查看缓存目录
模型默认缓存在：
- Windows: `C:\Users\YourName\.cache\huggingface\hub\`
- Linux: `~/.cache/huggingface/hub/`

检查是否有部分下载的文件。如果有，可以删除后重新下载。

### 快速解决方案 (Quick Solutions)

#### 方案 A: 使用 CPU 模式（最稳定）
修改 `nlp.py` 文件，在第 41 行附近：
```python
# GPU_DEVICE = get_device()  # 注释掉原来的
GPU_DEVICE = torch.device("cpu")  # 强制 CPU
print("🐢 使用 CPU 模式（更稳定但较慢）")
```

#### 方案 B: 预先下载模型
手动下载模型到缓存目录，避免运行时下载：
```bash
python -c "from transformers import AutoTokenizer, AutoModelForSequenceClassification; AutoTokenizer.from_pretrained('cardiffnlp/twitter-xlm-roberta-base-sentiment'); AutoModelForSequenceClassification.from_pretrained('cardiffnlp/twitter-xlm-roberta-base-sentiment', use_safetensors=True); print('下载完成')"
```

#### 方案 C: 增加超时时间
如果网络较慢，增加 HTTP 超时：
```bash
set HF_HUB_DOWNLOAD_TIMEOUT=600
python gui.py
```

### 性能对比 (Performance Comparison)

| 模式 | 速度 | 稳定性 | 内存占用 |
|------|------|--------|---------|
| AMD GPU (DirectML) | 快 | 中等 | 高 |
| NVIDIA GPU (CUDA) | 最快 | 高 | 高 |
| CPU | 较慢 | 最高 | 中等 |

**建议**: 如果首次运行或遇到问题，先使用 CPU 模式确保功能正常，之后再尝试 GPU 加速。

### 联系支持 (Contact Support)

如果以上方案都无法解决，请提供以下信息：
1. 完整的错误信息（从命令行运行获取）
2. Python 版本：`python --version`
3. 依赖版本：`pip list | findstr "torch transformers"`
4. 操作系统版本
5. GPU 型号（如果使用 GPU）
