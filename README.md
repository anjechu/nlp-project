# NLP Comment Processor

A PyQt5-based GUI application for processing and analyzing user comments using Natural Language Processing (NLP).

## Features

- **User-Friendly GUI**: Simple and intuitive interface built with PyQt5
- **JSON File Processing**: Upload JSON files containing user comments
- **Sentiment Analysis**: Automatic sentiment analysis (positive, negative, neutral)
- **Progress Tracking**: Real-time progress bar during processing
- **Error Handling**: Clear error messages for invalid inputs or processing issues
- **Standalone Executable**: Can be packaged as a standalone .exe file

## Installation

### Requirements

- Python 3.7 or higher
- PyQt5
- PyInstaller (for creating .exe)

### Install Dependencies

```bash
pip install -r requirements.txt
```

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
   - Results will be saved as a JSON file

3. **Process Comments**: Click the "Process Comments" button
   - A progress bar will show the processing status
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

Note: Each comment must have a `text`, `comment`, or `content` field containing the comment text.

### Output Format

The output JSON file contains:
- Processing statistics (total, successful, errors, sentiment distribution)
- Processed comments with sentiment analysis results

```json
{
  "statistics": {
    "total_comments": 5,
    "successful": 5,
    "errors": 0,
    "sentiment_distribution": {
      "positive": 2,
      "negative": 2,
      "neutral": 1
    }
  },
  "processed_comments": [
    {
      "original_text": "This product is amazing!",
      "cleaned_text": "this product is amazing",
      "sentiment_score": 1.0,
      "sentiment_label": "positive",
      "positive_words_count": 1,
      "negative_words_count": 0,
      "word_count": 4,
      "index": 0
    }
  ]
}
```

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

The `nlp.py` module can also be used independently:

```python
from nlp import NLPProcessor

processor = NLPProcessor()

# Process a single comment
comment = {'text': 'This is great!'}
result = processor.process_comment(comment)
print(result['sentiment_label'])  # Output: positive

# Process a file
stats = processor.process_file('input.json', 'output.json')
print(stats)
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