# Ollama Configuration Guide for Qwen LLM Integration

This guide explains how to configure and use Ollama with Qwen for the NLP project's LLM-enhanced report generation.

## What is Ollama?

Ollama is a lightweight tool that makes it easy to run large language models locally on your machine. It's the easiest way to use Qwen without dealing with complex model loading and GPU configuration.

## Installation

### Windows

1. Download Ollama from: https://ollama.ai/download
2. Run the installer (OllamaSetup.exe)
3. Ollama will start automatically as a background service

### macOS

```bash
curl https://ollama.ai/install.sh | sh
```

### Linux

```bash
curl https://ollama.ai/install.sh | sh
```

## Setup Qwen Model

After installing Ollama, you need to download the Qwen model:

### 1. Open Terminal/Command Prompt

### 2. Pull the Qwen Model

```bash
# For 7B model (recommended, ~4GB)
ollama pull qwen:7b

# Or for larger model (better quality, ~14GB)
ollama pull qwen:14b

# Or for smaller model (faster, ~1.5GB)
ollama pull qwen:1.8b
```

Wait for the download to complete. This will download the model to your local machine.

### 3. Verify Installation

Test that the model works:

```bash
ollama run qwen:7b "Hello, how are you?"
```

You should see a response from the model.

### 4. Keep Ollama Running

Ollama runs as a background service on port 11434. Make sure it's running:

**Windows**: Ollama should be running in the system tray
**macOS/Linux**: Check with `ollama serve` or `ps aux | grep ollama`

## Configuration in NLP Project

The GUI automatically tries to connect to Ollama when initializing. You don't need to change any code.

### Default Settings

- **Ollama URL**: `http://localhost:11434`
- **Model**: `qwen:7b`
- **Mode**: Auto-detects Ollama, falls back to HuggingFace if unavailable

### Custom Configuration (Optional)

If you want to use a different model or configuration, modify `gui.py`:

```python
# In gui.py, around line 60:
self.llm_generator = LLMReportGenerator(
    use_ollama=True,
    ollama_model="qwen:14b"  # Change to your preferred model
)
```

Or create the generator directly in your code:

```python
from llm_report_generator import LLMReportGenerator

# Use Ollama with Qwen
generator = LLMReportGenerator(use_ollama=True, ollama_model="qwen:7b")

# Or use HuggingFace (requires model download)
generator = LLMReportGenerator(use_ollama=False, model_path="Qwen/Qwen-7B-Chat")
```

## Usage in GUI

1. **Start Ollama** (if not already running):
   ```bash
   ollama serve
   ```

2. **Launch the NLP GUI**:
   ```bash
   python gui.py
   ```

3. **Load or Generate Reports**:
   - Use the "Data Processing" tab to analyze game feedback
   - Or load existing reports

4. **Enhance with LLM**:
   - Go to "Insights Report" tab
   - Click "✨ Enhance with LLM" button
   - The system will use Ollama to:
     - Generate meaningful topic names
     - Create insight summaries
     - Perform cross-cultural analysis

5. **View Results**:
   - Enhanced reports will show:
     - Named topics (e.g., "Graphics & Art Style" instead of "Topic 1")
     - LLM-generated insights
     - Cross-cultural preferences
     - Statistical visualizations

## Checking Connection Status

The GUI will show LLM status in the Insights Report tab:

- ✅ **"LLM Ready"** (green): Ollama is connected and working
- ⚠️ **"LLM Not Available"** (gray): Ollama is not running or model not found

Check the console/logs for detailed messages:
```
✅ Connected to Ollama with model: qwen:7b
```

Or if there's an issue:
```
⚠️ Ollama not available: [error message]
📝 Make sure Ollama is running: ollama serve
📝 And model is pulled: ollama pull qwen:7b
```

## Troubleshooting

### Issue: "Ollama not available"

**Solution**:
1. Check if Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```
   
2. If not, start it:
   ```bash
   ollama serve
   ```

3. Verify model is downloaded:
   ```bash
   ollama list
   ```
   
   If qwen is not listed, pull it:
   ```bash
   ollama pull qwen:7b
   ```

### Issue: Slow Performance

**Solutions**:
- Use smaller model: `ollama pull qwen:1.8b`
- Close other applications to free up RAM
- For GPU acceleration, ensure your GPU drivers are up to date

### Issue: Connection Timeout

**Solution**:
- Increase timeout in `llm_report_generator.py`:
  ```python
  timeout=60  # Increase from 30 to 60 seconds
  ```

### Issue: Model Not Found

**Solution**:
```bash
# List available models
ollama list

# Pull the correct model
ollama pull qwen:7b
```

## Cross-Cultural Analysis

With Ollama configured, the system can perform cross-cultural analysis:

### What It Analyzes

- **Chinese Players** (简体中文/繁體中文): Preferences and feedback
- **Japanese Players** (日本語): Unique perspectives
- **English Players** (English): Western market insights
- **Korean Players** (한국어): Additional insights

### Example Output

```
🌍 Cultural: Chinese: 179 | English: 120 | Japanese: 45
🗺️  Cross-Cultural: Chinese players emphasize story immersion, 
    while English speakers focus more on gameplay mechanics...
```

## Performance Tips

1. **First Run**: Initial model loading takes time. Subsequent runs are faster.
2. **Batch Processing**: Process multiple reports at once for efficiency.
3. **Model Selection**:
   - `qwen:1.8b`: Fast, good for quick testing
   - `qwen:7b`: Balanced (recommended)
   - `qwen:14b`: Best quality, slower

## Advanced: Using HuggingFace Instead

If you prefer HuggingFace transformers instead of Ollama:

```python
from llm_report_generator import LLMReportGenerator

# Download Qwen model from HuggingFace first
generator = LLMReportGenerator(
    use_ollama=False,
    model_path="Qwen/Qwen-7B-Chat"  # Or local path
)
```

Note: HuggingFace approach requires:
- More VRAM (8GB+ GPU)
- Manual model download
- Longer initial load time
- But offers more control and customization

## Support

For issues specific to:
- **Ollama**: https://github.com/jmorganca/ollama
- **Qwen Model**: https://github.com/QwenLM/Qwen
- **This Project**: Check the repository issues

## Summary

1. Install Ollama from https://ollama.ai
2. Run `ollama pull qwen:7b`
3. Start Ollama with `ollama serve`
4. Launch GUI - it will auto-connect
5. Use "Enhance with LLM" for intelligent reports

That's it! The system will now generate enhanced reports with cross-cultural insights automatically.
