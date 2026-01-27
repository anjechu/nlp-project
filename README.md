# NLP Comment Processor

A PyQt5-based GUI application for advanced NLP processing and analysis of user comments with GPU acceleration, transformer models, and topic clustering.

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

## Features

- **User-Friendly GUI**: Simple and intuitive interface built with PyQt5
- **Advanced NLP Pipeline**: 
  - GPU-accelerated sentiment analysis using transformer models (cardiffnlp/twitter-xlm-roberta-base-sentiment)
  - Fingerprint-based deduplication for robust data cleaning
  - Sentence embeddings with multilingual support
  - HDBSCAN clustering for topic discovery
  - PCA dimensionality reduction for efficient processing
- **JSON File Processing**: Upload JSON files containing user comments
- **Topic Modeling**: Automatically identifies discussion topics and their sentiment
- **Progress Tracking**: Real-time progress bar during processing
- **Error Handling**: Clear error messages for invalid inputs or processing issues
- **Standalone Executable**: Can be packaged as a standalone .exe file

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

## Usage

### Running the GUI Application

```bash
python gui.py
```

### Using the Application

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

**GPU Acceleration:**
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
├── gui.py                      # PyQt5 GUI application
├── nlp.py                      # NLP processing module
├── requirements.txt            # Python dependencies
├── nlp_processor.spec         # PyInstaller specification file
├── .gitignore                 # Git ignore file
└── README.md                  # This file
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

### Pipeline Stages

1. **Data Cleaning**: Removes noise, duplicates, and metadata
2. **Statement Splitting**: Breaks long reviews into individual statements
3. **Fingerprint Deduplication**: Eliminates semantic duplicates
4. **Sentiment Analysis**: GPU-accelerated transformer model inference
5. **Vector Encoding**: Multilingual sentence embeddings
6. **Dimensionality Reduction**: PCA for efficient clustering
7. **Topic Clustering**: HDBSCAN for topic discovery
8. **Report Generation**: Summary with statistics and representative sentences

```

## Troubleshooting

### "Invalid JSON file" Error
- Ensure the file is valid JSON
- Check that comments have the required text field

### "No comments found in file" Error
- Verify the JSON structure matches one of the supported formats
- Check that the comments array is not empty

### PyQt5 Import Errors
- Reinstall PyQt5: `pip install --force-reinstall PyQt5==5.15.10`

### Executable Not Working
- Test the application with `python gui.py` first
- Check that all dependencies are installed
- Review PyInstaller build logs for errors

## License

This project is provided as-is for educational and commercial use.