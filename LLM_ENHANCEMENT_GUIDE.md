# LLM-Enhanced Report Generation

This document describes the new LLM-enhanced report generation features added to the NLP project.

## Overview

The system now integrates with Qwen (or compatible) local LLM models to generate enhanced insights from NLP analysis results.

## Features

### 1. **LLM-Powered Topic Naming**
Instead of generic "Topic 1", "Topic 2" labels, the system now generates meaningful names based on the content:
- **Before**: "Topic 4"
- **After**: "Art Style & Graphics" or "Gameplay Mechanics" or "Music & Sound"

The LLM analyzes representative sentences and sample texts to determine the most appropriate topic name.

### 2. **Enhanced Insight Summaries**
Each topic now includes an LLM-generated summary that provides:
- Key themes and patterns in player feedback
- Contextual understanding of sentiment
- Actionable insights for developers

### 3. **Statistical Visualizations**
The enhanced reports include chart-ready data:
- **Sentiment Distribution**: Breakdown of positive/neutral/negative feedback
- **Topic Density**: Top topics by number of mentions
- **Sentiment Statistics**: Mean, std deviation, min/max scores

### 4. **Improved Report Display**
The GUI now shows:
- 📌 Named topics with clear hierarchy
- 😊😐😞 Sentiment indicators with emojis
- 👥 Player mention counts
- 💡 LLM-generated insights
- 💬 Representative examples
- 📊 Statistical summaries

## Usage

### In the GUI

1. **Load or Generate Reports**: Use the "Data Processing" tab to analyze game feedback
2. **Navigate to Insights Report Tab**: View the basic analysis results
3. **Click "Enhance with LLM"**: The system will:
   - Generate topic names for all topics
   - Create insight summaries
   - Add statistical chart data
4. **View Enhanced Reports**: The display will update with rich, contextualized insights

### Programmatic Usage

```python
from llm_report_generator import LLMReportGenerator

# Initialize generator
generator = LLMReportGenerator(model_path="/path/to/qwen/model")  # Optional

# Load NLP results
with open('analysis_result.json', 'r') as f:
    nlp_result = json.load(f)

# Generate enhanced report
enhanced_report = generator.generate_enhanced_report(
    nlp_result, 
    include_charts=True
)

# Access enhanced data
for topic in enhanced_report['topics']:
    print(f"Topic: {topic['topic_name']}")
    print(f"Summary: {topic['summary']}")
    print(f"Sentiment: {topic['sentiment_label']} ({topic['sentiment_score']})")
    print(f"Density: {topic['density']} players")
```

## Configuration

### Using Qwen Model

The system is designed to work with Qwen models. To use a local Qwen model:

1. **Download Qwen Model**: Download Qwen-7B-Chat or similar model from HuggingFace
2. **Set Model Path**: Pass the path when initializing:
   ```python
   generator = LLMReportGenerator(model_path="/path/to/Qwen-7B-Chat")
   ```
3. **Or Use Default**: Leave empty to use default HuggingFace model (requires internet)

### Fallback Mode

If LLM is not available, the system automatically falls back to:
- Keyword-based topic naming
- Template-based summaries
- Full statistical analysis still available

## Architecture

```
┌─────────────────┐
│  NLP Processor  │ ─┐
└─────────────────┘  │
                     │ Raw Topics
                     ↓
            ┌────────────────────┐
            │ LLMReportGenerator │
            └────────────────────┘
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
   Topic Names   Summaries    Charts
        │            │            │
        └────────────┴────────────┘
                     ↓
            Enhanced Report JSON
```

## Example Output

### Before Enhancement:
```
🎮 File: cyberpunk_feedback.json
   - Review Count: 1000
   - Top Topic (positive): 来夜之城当来生的传奇吧...
```

### After Enhancement:
```
🎮 FILE: cyberpunk_feedback.json
────────────────────────────────────────────────────────────────────────────────
📊 Review Count: 1000 total | 950 analyzed
🏷️  Topics Found: 15
✨ LLM Enhanced

  1. 📌 NIGHT CITY ATMOSPHERE
     😊 Sentiment: Positive (+0.210)
     👥 Mentions: 179 players
     💡 Insight: Players consistently praise the immersive atmosphere of Night City, 
     highlighting the game's world-building and the emotional journey of becoming 
     a legend in the city. The setting resonates strongly with the community.
     💬 Example: "来夜之城当来生的传奇吧"

  📊 SENTIMENT OVERVIEW:
     😊 Positive: 650 | 😐 Neutral: 200 | 😞 Negative: 100
     Average Score: 0.215 (σ=0.312)
```

## Benefits

1. **Better Understanding**: Topic names make it immediately clear what players are discussing
2. **Actionable Insights**: LLM summaries provide context that raw sentences lack
3. **Time Saving**: No need to manually analyze hundreds of topics
4. **Scalability**: Works across multiple games and languages
5. **Developer-Friendly**: Clear visualizations and statistics for decision-making

## Future Enhancements

- Real-time chart generation with matplotlib
- Export to PDF with visualizations
- Trend analysis across multiple game versions
- Comparative analysis between different games
- Integration with more LLM models (GPT, Claude, etc.)
