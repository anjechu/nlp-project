# Where to Find Your Enhanced Reports and Charts

This guide shows you exactly where the LLM-enhanced reports and generated charts are saved after using the "Enhance with LLM" feature.

## File Locations

After clicking "Enhance with LLM" in the Insights Report tab, the system generates and saves several files:

### 1. Enhanced Reports (JSON files)

**Location**: `reports/` directory

**Naming Convention**: `Report_{original_name}_{timestamp}_enhanced.json`

**Example**:
```
reports/
├── Report_game_feedback_20260127_143052.json          (Original NLP analysis)
└── Report_game_feedback_20260127_143052_enhanced.json (LLM-enhanced version)
```

**What's Inside Enhanced Reports**:
- Original NLP data (topics, sentiment, statistics)
- LLM-generated topic names (e.g., "Graphics & Art Style" instead of "Topic 1")
- Insight summaries for each topic
- Cross-cultural analysis (if multi-language data present)
- Chart data (statistical information)
- Chart file paths (references to generated images)

### 2. Chart Images (PNG files)

**Location**: `charts/` directory (created automatically)

**Files Generated** (for each report):
1. `{report_name}_sentiment_dist.png` - Sentiment distribution pie chart
2. `{report_name}_topic_density.png` - Topic density bar chart  
3. `{report_name}_sentiment_scores.png` - Sentiment score histogram

**Example**:
```
charts/
├── game_feedback_20260127_143052_sentiment_dist.png
├── game_feedback_20260127_143052_topic_density.png
└── game_feedback_20260127_143052_sentiment_scores.png
```

**Chart Details**:
- All charts use dark theme (#1a1a2e background) matching the GUI
- High resolution (150 DPI) PNG format
- Violet/blue accent colors matching the UI theme

## How to Access Your Files

### Method 1: GUI Log Messages

After enhancement completes, check the log box in "Data Processing" tab:

```
✨ Enhanced report saved: reports/Report_game_feedback_20260127_143052_enhanced.json
📊 Generated 3 charts in charts/ directory
```

### Method 2: GUI Report Display

In the "Insights Report" tab, scroll to the bottom of each enhanced report to see:

```
📈 GENERATED CHARTS:
   • Sentiment Distribution: charts/game_feedback_20260127_143052_sentiment_dist.png
   • Topic Density: charts/game_feedback_20260127_143052_topic_density.png
   • Sentiment Scores: charts/game_feedback_20260127_143052_sentiment_scores.png
```

### Method 3: Direct Folder Navigation

1. **Find your project directory**: Where you have `gui.py` and `nlp.py`
2. **Open subdirectories**:
   - `reports/` - Contains all JSON reports (original and enhanced)
   - `charts/` - Contains all generated chart images

### Method 4: File Explorer / Terminal

**Windows**:
```cmd
cd C:\path\to\nlp-project
dir reports\*_enhanced.json
dir charts\*.png
```

**macOS/Linux**:
```bash
cd /path/to/nlp-project
ls reports/*_enhanced.json
ls charts/*.png
```

## Viewing the Files

### Enhanced Reports (JSON)
- Open with any text editor (VS Code, Notepad++, etc.)
- Or use JSON viewer for better formatting
- Contains all analysis data in structured format

### Chart Images (PNG)
- Open with any image viewer
- Or insert into presentations/documents
- Ready to share with stakeholders

## Example: Complete Workflow

1. **Generate NLP Report**:
   - Select JSON file → Click "Start NLP Engine"
   - Result: `reports/Report_game_feedback_20260127_143052.json`

2. **Enhance with LLM**:
   - Go to "Insights Report" tab → Click "Enhance with LLM"
   - Results:
     - `reports/Report_game_feedback_20260127_143052_enhanced.json`
     - `charts/game_feedback_20260127_143052_sentiment_dist.png`
     - `charts/game_feedback_20260127_143052_topic_density.png`
     - `charts/game_feedback_20260127_143052_sentiment_scores.png`

3. **View Results**:
   - In GUI: "Insights Report" tab shows enhanced text analysis
   - On disk: JSON files for data, PNG files for charts
   - Share: Copy charts to presentations, reports to data analysis tools

## File Structure Summary

```
nlp-project/
├── gui.py
├── nlp.py
├── llm_report_generator.py
├── chart_generator.py
├── reports/                          # ← Enhanced reports saved here
│   ├── Report_*.json                 # Original NLP analysis
│   └── Report_*_enhanced.json        # LLM-enhanced with insights
└── charts/                           # ← Chart images saved here
    ├── *_sentiment_dist.png          # Sentiment pie charts
    ├── *_topic_density.png           # Topic bar charts
    └── *_sentiment_scores.png        # Sentiment histograms
```

## Troubleshooting

**Q: I don't see the charts/ directory**
- A: It's created automatically on first enhancement. If LLM enhancement hasn't been run yet, the directory won't exist.

**Q: Charts are not being generated**
- A: Check the log for error messages. Ensure matplotlib is installed: `pip install matplotlib`

**Q: Where are the original reports?**
- A: Original NLP reports are in `reports/Report_*.json` (without "_enhanced" suffix)

**Q: Can I delete old charts?**
- A: Yes, charts can be regenerated anytime by clicking "Enhance with LLM" again

## Tips

1. **Backup Important Reports**: Copy enhanced JSON files to a safe location
2. **Share Charts**: PNG files are ready for presentations and documents
3. **Compare Versions**: Keep both original and enhanced reports for comparison
4. **Organize by Date**: Reports include timestamps in filenames for easy tracking
5. **Reload Anytime**: Use "Load Historical Reports" to reload any saved report

The system automatically manages file organization - you just need to know where to look!
