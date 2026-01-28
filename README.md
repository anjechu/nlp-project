# NLP Comment Processor (Version 2.0)

A PyQt5-based GUI application for advanced NLP processing and cross-cultural analysis of user comments with GPU acceleration, transformer models, LLM-enhanced insights, and professional reporting capabilities.

## ⚠️ Important Note for AMD GPU Users

**AMD DirectML is disabled by default** due to compatibility issues with transformer models that cause silent crashes. The application will automatically use CPU mode, which is stable and reliable.

- ✅ **NVIDIA GPU (CUDA)**: Fully supported and recommended
- ✅ **CPU Mode**: Stable for all systems (default for AMD)
- ⚠️ **AMD GPU (DirectML)**: Disabled by default due to instability

If you have an AMD GPU and want to try GPU acceleration (not recommended):
```bash
set USE_DIRECTML=1
python gui.py
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for details.

## What's New in Version 2.0

🎉 **Major Enhancements:**
- **🌏 Cross-Cultural Analysis**: Compare sentiment and preferences across different language communities (Chinese, Japanese, English, Korean)
- **🤖 LLM-Enhanced Insights**: Integrates Qwen (via Ollama) to generate meaningful topic names and contextual insights
- **📊 Professional HTML Reports**: Generates comprehensive analysis reports with embedded charts and visualizations
- **📈 Interactive Charts**: Sentiment distribution, topic density, and cultural comparison visualizations
- **🗂️ Map-Reduce Architecture**: Process multiple game+language datasets efficiently without LLM context overflow
- **📂 Historical Report Loading**: Aggregate and analyze multiple NLP reports for unified insights

## Core Features

### NLP Processing Pipeline
- **GPU-Accelerated Sentiment Analysis**: Uses transformer models (cardiffnlp/twitter-xlm-roberta-base-sentiment)
- **Fingerprint-Based Deduplication**: Robust duplicate detection with advanced text cleaning
- **Multilingual Support**: Processes Chinese, Japanese, English, Korean, and more
- **HDBSCAN Clustering**: Intelligent topic discovery and grouping
- **PCA Dimensionality Reduction**: Efficient processing of high-dimensional embeddings
- **Cultural Distribution Tracking**: Identifies which cultures discuss each topic

### Advanced Analysis (V2)
- **LLM Topic Naming**: Transforms "Topic 1" → "Graphics & Art Style" using local Qwen model
- **Insight Generation**: 2-3 sentence contextual analysis per topic
- **Cross-Cultural Comparison**: Identifies what different cultures prefer or dislike
- **Professional Reporting**: Self-contained HTML reports with embedded charts
- **Chart Visualizations**: Sentiment distribution, topic density, score histograms with CJK support
- **Map-Reduce Processing**: Scalable analysis of 10+ game+language combinations

### User Interface
- **Tabbed Interface**: Separate tabs for NLP processing and insights generation
- **File Management**: Load and aggregate multiple historical reports
- **Progress Tracking**: Real-time progress bars and status updates
- **Auto-Open Reports**: Generated HTML reports open automatically in browser
- **Error Handling**: Clear error messages with detailed logging
- **Standalone Executable**: Can be packaged as a portable .exe file

## Installation

### Requirements

- Python 3.8 or higher
- NVIDIA CUDA-compatible GPU (optional, recommended for best performance)
- 8GB+ RAM recommended

### Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- PyQt5 - GUI framework
- PyTorch - Deep learning backend
- Transformers - Pre-trained NLP models
- Sentence-Transformers - Multilingual embeddings
- HDBSCAN - Clustering algorithm
- scikit-learn - Machine learning utilities
- pandas, numpy - Data processing
- matplotlib, seaborn - V2: Chart generation
- requests - V2: Ollama API communication (optional)

## Usage

### Quick Start

1. **Run the GUI Application**
   ```bash
   python gui.py
   ```

2. **Tab 1: NLP Processing**
   - Select input JSON file with comments
   - Choose output location for NLP results
   - Click "Process Comments" to analyze
   - Results saved in `reports/` directory

3. **Tab 2: Insights Report** (V2 Feature)
   - Load one or more historical NLP reports
   - Click "🌏 Generate Cross-Cultural Analysis Report"
   - HTML report with charts auto-opens in browser
   - Reports saved in `analysis/` directory

### Detailed Usage Guide

1. **Select Input File**: Click "Browse..." next to "Input File" and select a JSON file containing comments
   - The file must be a `.json` file
   - Format: Either a list of comment objects or an object with a "comments" key

2. **Select Output Location**: Click "Browse..." next to "Output File" and choose where to save the results
   - Results will be saved as a JSON file with topic analysis

3. **Process Comments**: Click the "Process Comments" button
   - A progress bar will show the processing status
   - GPU acceleration will be used if available
   - Results will be displayed when complete

### Input JSON Format

The input JSON file should contain comments in one of these formats:

**Format 1: List of comments**
```json
[
  {
    "text": "This product is amazing!",
    "id": 1,
    "user": "user1"
  },
  {
    "text": "Not satisfied with the quality.",
    "id": 2,
    "user": "user2"
  }
]
```

**Format 2: Object with comments key**
```json
{
  "comments": [
    {
      "text": "Great experience!",
      "id": 1
    }
  ]
}
```

Note: Each comment must have a `text`, `comment`, `content`, or `review` field containing the comment text. Additional fields like `id`, `recommendationid`, `language`, `lang`, and `user` will be preserved.

### Output Format

The output JSON file contains:
- Processing statistics (total comments, valid statements, topics identified)
- Discovered topics with sentiment analysis and representative sentences

```json
{
  "statistics": {
    "total_comments": 100,
    "valid_statements": 85,
    "topics_identified": 5,
    "sentiment_distribution": {
      "positive": 3,
      "negative": 1,
      "neutral": 1
    }
  },
  "topics": [
    {
      "topic_id": 0,
      "density": 25,
      "sentiment_score": 0.6543,
      "sentiment_label": "positive",
      "cultural_distribution": {
        "schinese": 15,
        "english": 10
      },
      "representative_sentences": [
        "The gameplay is fantastic and very engaging",
        "Graphics are beautiful and immersive",
        "Best game I've played this year"
      ],
      "sample_texts": [
        "Amazing experience overall",
        "Really enjoying the storyline",
        "..."
      ]
    }
  ]
}
```

### Advanced Features

#### V2: Cross-Cultural Analysis Report Generation

The insights tab enables you to generate professional HTML reports with LLM-enhanced insights:

**Step 1: Load Historical Reports**
```python
# In the Insights tab, click "Load Historical Reports"
# Select one or more NLP JSON reports from the reports/ directory
# The system shows how many reports are loaded
```

**Step 2: Generate Analysis**
```python
# Click "🌏 Generate Cross-Cultural Analysis Report"
# The system will:
#   1. Aggregate all topics from loaded reports
#   2. Use LLM (Qwen) to filter valuable topics
#   3. Generate meaningful topic names and insights
#   4. Create charts and visualizations
#   5. Build a comprehensive HTML report
# Report automatically opens in your browser
```

**Output**: Self-contained HTML file with:
- Executive summary with key statistics
- Sentiment distribution pie chart
- Top topics ranked by density
- Per-topic analysis with:
  - LLM-generated topic name
  - Sentiment score and label
  - Cultural distribution
  - Representative comments
  - Contextual insights
- Cross-cultural comparison insights

#### Map-Reduce Processing (For Large Datasets)

For analyzing multiple games across multiple languages, use the Map-Reduce approach:

```bash
# See MAP_REDUCE_GUIDE.md for detailed instructions

# MAP Phase: Process each game+language independently
python gui.py  # Process game1_chinese.json → reports/Report_game1_chinese.json
python gui.py  # Process game1_japanese.json → reports/Report_game1_japanese.json
python gui.py  # Process game2_chinese.json → reports/Report_game2_chinese.json
# ... (repeat for all combinations)

# REDUCE Phase: Load all reports in Insights tab
# 1. Click "Load Historical Reports"
# 2. Select ALL reports you want to aggregate
# 3. Click "Generate Cross-Cultural Analysis Report"

# RESULT: Unified report combining insights from all games and languages
```

**Why Map-Reduce?**
- Prevents LLM context overflow (e.g., Chinese positive topics getting lost)
- Each game+language gets full LLM attention during MAP phase
- REDUCE phase aggregates only the valuable topics
- Scalable to 10+ game+language combinations

#### GPU Acceleration
- Automatically detects and uses NVIDIA GPU (CUDA) or AMD GPU (DirectML)
- Falls back to CPU if no GPU is available
- Significantly faster processing with GPU

**Data Cleaning:**
- Fingerprint-based deduplication removes duplicate comments
- Removes Steam BBCode, URLs, dates, and metadata
- Splits long reviews into individual statements
- Filters out very short or invalid text

**Topic Discovery:**
- Uses HDBSCAN clustering to identify discussion topics
- Groups similar comments together
- Finds representative sentences for each topic
- Tracks language/cultural distribution per topic


## LLM Setup (Optional for V2 Features)

Version 2 uses LLM (Large Language Model) to generate meaningful topic names and insights. This is **optional** - the system works without LLM but with basic naming.

### Option 1: Ollama (Recommended)

Ollama provides easy local LLM hosting:

```bash
# 1. Install Ollama (Windows/Mac/Linux)
# Download from: https://ollama.com

# 2. Pull Qwen model (7B recommended, requires ~4GB RAM)
ollama pull qwen2.5:7b

# 3. Start Ollama server
ollama serve

# 4. Run the application - LLM will be automatically detected
python gui.py
```

### Option 2: HuggingFace (Advanced)

```python
# Install transformers if not already installed
pip install transformers

# Modify llm_report_generator.py to use HuggingFace model
# The model will be downloaded on first use (~5-15GB)
```

### Fallback Mode

If LLM is not available, the system automatically uses:
- Keyword extraction for topic naming
- Template-based insights
- Basic cultural analysis

See [OLLAMA_SETUP_GUIDE.md](OLLAMA_SETUP_GUIDE.md) and [LLM_ENHANCEMENT_GUIDE.md](LLM_ENHANCEMENT_GUIDE.md) for detailed setup.

## Building Standalone Executable

To create a standalone .exe file that doesn't require Python installation:

### Install PyInstaller

```bash
pip install pyinstaller==6.3.0
```

### Build the Executable

**Option 1: Using the spec file (recommended)**
```bash
pyinstaller nlp_processor.spec
```

**Option 2: Direct command**
```bash
pyinstaller --onefile --windowed --name NLPCommentProcessor gui.py
```

The executable will be created in the `dist/` directory.

### Testing the Executable

1. Navigate to the `dist/` directory
2. Run `NLPCommentProcessor.exe` (Windows) or `NLPCommentProcessor` (Linux/Mac)
3. Test with sample JSON files to ensure all functionality works

## Project Structure

```
nlp-project/
├── gui.py                          # Main PyQt5 GUI with tabbed interface
├── nlp.py                          # Core NLP processing pipeline
├── analysis_report_generator.py   # V2: HTML report generation with chart integration
├── llm_report_generator.py        # V2: LLM-enhanced topic naming and insights
├── chart_generator.py             # V2: Chart generation with CJK support
├── requirements.txt               # Python dependencies
├── nlp_processor.spec             # PyInstaller specification
│
├── reports/                       # Output: NLP processing results (JSON)
├── analysis/                      # Output: Analysis reports (HTML + JSON + charts)
│
├── README.md                      # Main documentation (this file)
├── METHODOLOGY.md                 # Research methodology and approach
├── TROUBLESHOOTING.md             # Common issues and solutions
├── IMPLEMENTATION.md              # Technical implementation details
├── IMPLEMENTATION_SUMMARY.md      # Feature summary
├── PACKAGING.md                   # Build and distribution guide
│
├── ANALYSIS_SYSTEM_GUIDE.md       # V2: How to use analysis features
├── LLM_ENHANCEMENT_GUIDE.md       # V2: LLM integration guide
├── MAP_REDUCE_GUIDE.md            # V2: Large-scale processing guide
├── OLLAMA_SETUP_GUIDE.md          # V2: Ollama setup instructions
├── FILE_LOCATIONS_GUIDE.md        # V2: File organization reference
│
├── test_app.py                    # Test suite for core functionality
├── test_cross_cultural_features.py # V2: Tests for analysis features
├── create_sample_data.py          # Sample data generator
├── debug.py                       # Debug utilities
└── stopWord.txt.txt               # Stop words for text cleaning
```

## NLP Processing Module

The `nlp.py` module can be used independently for batch processing or command-line usage:

### Python API

```python
from nlp import NLPProcessor

# Initialize processor (models loaded lazily on first use)
processor = NLPProcessor()

# Process a file with advanced NLP pipeline
stats = processor.process_file('input.json', 'output.json')
print(stats)
# Output: {
#   'total_comments': 100,
#   'successful': 85,
#   'errors': 15,
#   'sentiment_distribution': {'positive': 3, 'negative': 1, 'neutral': 1}
# }
```

### Command Line

```bash
# Process a JSON file directly
python nlp.py input.json output.json

# Or use default output name
python nlp.py comments.json
```

### Pipeline Stages (V2 Enhanced)

#### Core NLP Pipeline
1. **Data Cleaning**: Removes noise, duplicates, and metadata
2. **Statement Splitting**: Breaks long reviews into individual statements
3. **Fingerprint Deduplication**: Eliminates semantic duplicates
4. **Sentiment Analysis**: GPU-accelerated transformer model inference
5. **Vector Encoding**: Multilingual sentence embeddings
6. **Dimensionality Reduction**: PCA for efficient clustering
7. **Topic Clustering**: HDBSCAN for topic discovery
8. **Report Generation**: Basic JSON with statistics and topics

#### V2 Analysis Pipeline
9. **Topic Aggregation**: Combines topics from multiple reports (Map-Reduce)
10. **LLM Filtering**: Identifies valuable topics worth analyzing
11. **Topic Naming**: Generates meaningful names (e.g., "Combat System Feedback")
12. **Insight Generation**: Creates 2-3 sentence contextual summaries
13. **Cultural Analysis**: Compares preferences across language communities
14. **Visualization**: Generates charts with embedded data
15. **HTML Report**: Assembles professional, shareable report

```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for comprehensive troubleshooting guide.

### Common Issues

#### "Invalid JSON file" Error
- Ensure the file is valid JSON
- Check that comments have the required text field

#### "No comments found in file" Error
- Verify the JSON structure matches one of the supported formats
- Check that the comments array is not empty

#### LLM Not Working
- Check Ollama is running: `ollama list`
- Verify model is installed: `ollama pull qwen2.5:7b`
- Check Ollama is accessible: http://localhost:11434
- System will fallback to basic mode if LLM unavailable

#### PyQt5 Import Errors
- Reinstall PyQt5: `pip install --force-reinstall PyQt5==5.15.10`

#### Executable Not Working
- Test the application with `python gui.py` first
- Check that all dependencies are installed
- Review PyInstaller build logs for errors

## Additional Documentation

- **[METHODOLOGY.md](METHODOLOGY.md)** - Research methodology and theoretical framework
- **[ANALYSIS_SYSTEM_GUIDE.md](ANALYSIS_SYSTEM_GUIDE.md)** - V2 analysis features guide
- **[MAP_REDUCE_GUIDE.md](MAP_REDUCE_GUIDE.md)** - Large-scale processing workflow
- **[LLM_ENHANCEMENT_GUIDE.md](LLM_ENHANCEMENT_GUIDE.md)** - LLM integration details
- **[OLLAMA_SETUP_GUIDE.md](OLLAMA_SETUP_GUIDE.md)** - Ollama installation and setup
- **[FILE_LOCATIONS_GUIDE.md](FILE_LOCATIONS_GUIDE.md)** - File organization reference
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Technical implementation details
- **[PACKAGING.md](PACKAGING.md)** - Build and distribution guide

## Version History

### Version 2.0 (Current)
- 🌏 Cross-cultural analysis with LLM enhancement
- 📊 Professional HTML reports with embedded charts
- 🤖 Qwen LLM integration via Ollama or HuggingFace
- 📈 Interactive visualizations (sentiment, topics, distributions)
- 🗂️ Map-Reduce architecture for multi-game analysis
- 📂 Historical report aggregation
- 🎨 Dark theme charts with CJK support

### Version 1.0
- Basic GUI with PyQt5
- Core NLP pipeline (sentiment, clustering, embeddings)
- JSON input/output
- GPU acceleration
- Standalone executable support

## License

This project is provided as-is for educational and commercial use.