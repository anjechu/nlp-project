# Cross-Cultural Analysis Report System

## Overview

The system now generates **professional, unified HTML analysis reports** that combine LLM insights, cross-cultural comparisons, and embedded visualizations into a single, readable document.

## Key Changes

### 1. **Separated Concerns**
- **NLP Reports** (`reports/` folder): Original NLP processing results - **NEVER MODIFIED**
- **Analysis Reports** (`analysis/` folder): LLM-generated cross-cultural analysis - **NEWLY CREATED**

### 2. **Unified Reports**
Analysis reports are comprehensive HTML documents that include:
- Executive summary with key statistics
- Embedded charts (sentiment distribution, topic density, score histogram)
- Detailed cross-cultural comparisons
- LLM-generated topic names and insights
- Professional, readable layout with dark theme

### 3. **Folder Structure**

```
nlp-project/
├── reports/                          # NLP processing results (untouched)
│   ├── Report_game1_20260127.json    # Original NLP data
│   └── Report_game2_20260127.json    # Original NLP data
│
└── analysis/                         # Cross-cultural analysis reports (new)
    ├── analysis_20260127_120530.html # Complete HTML report
    ├── analysis_20260127_120530.json # Analysis data for reference
    ├── analysis_20260127_120530_sentiment_dist.png
    ├── analysis_20260127_120530_topic_density.png
    └── analysis_20260127_120530_sentiment_scores.png
```

## Workflow

### Step 1: Generate NLP Report
1. Load game feedback JSON file
2. Click "Start NLP Engine" in "Data Processing" tab
3. Result: `reports/Report_gamename_timestamp.json`

### Step 2: Generate Cross-Cultural Analysis
1. Go to "Insights Report" tab
2. Click "🌏 Generate Cross-Cultural Analysis Report"
3. System will:
   - Read original NLP data (without modifying it)
   - Use LLM to generate topic names and insights
   - Create cross-cultural comparisons
   - Generate charts and embed them in HTML
   - Save everything to `analysis/` folder
   - **Automatically open the report in your browser**

### Step 3: Review Analysis
The generated HTML report includes:

#### Executive Summary
- Total reviews analyzed
- Number of topics and cultures
- Key cross-cultural insights (LLM-generated)

#### Visual Overview
- Three embedded charts showing sentiment, topics, and scores
- Professional dark theme matching the GUI

#### Cross-Cultural Analysis Section
- Comparison of different cultural groups (Chinese, Japanese, English, Korean)
- Sentiment distribution per culture
- Top topics discussed by each cultural group
- Percentage breakdowns

#### Detailed Topic Analysis
- Each topic with:
  - LLM-generated name (e.g., "Graphics & Art Style" instead of "Topic 1")
  - Sentiment analysis
  - Cultural distribution
  - LLM-generated insights
  - Cross-cultural comparison insights
  - Representative examples in original languages

#### Methodology Section
- Data sources and analysis techniques
- Statistics and data quality metrics

## Features

### ✅ Professional Layout
- Clean, modern design with dark theme
- Responsive layout (works on mobile/desktop)
- Clear hierarchy and typography
- Embedded charts (no separate files to manage)

### ✅ Cross-Cultural Focus
- Dedicated section comparing cultures
- Per-topic cultural breakdowns
- LLM-generated cultural insights
- Shows what each culture likes/dislikes

### ✅ Integrated Visualizations
- Charts are embedded as base64 images in HTML
- Also saved as PNG files for presentations
- Dark theme matching the GUI
- High resolution (150 DPI)

### ✅ Non-Destructive
- Original NLP reports remain untouched
- Can regenerate analysis anytime
- Multiple analyses can coexist

### ✅ Shareable
- Single HTML file contains everything
- Open in any browser
- Easy to email or present
- No dependencies required to view

## Example Report Structure

```html
🌏 Cross-Cultural Game Feedback Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 EXECUTIVE SUMMARY
├── 1000 Total Reviews
├── 15 Topics Identified
├── 3 Cultures Analyzed
└── 10 Positive Topics

🗺️ Key Cross-Cultural Insights
Chinese players emphasize atmospheric storytelling and 
visual design, while English speakers focus more on 
gameplay mechanics and performance...

📈 VISUAL OVERVIEW
├── [Sentiment Distribution Pie Chart]
├── [Topic Density Bar Chart]
└── [Sentiment Score Histogram]

🌏 CROSS-CULTURAL ANALYSIS
├── 🏴 Chinese Players (580 mentions)
│   ├── 😊 65% Positive | 😞 15% Negative
│   └── Top Topics: Graphics (150), Music (120)...
│
├── 🏴 English Players (300 mentions)
│   ├── 😊 55% Positive | 😞 30% Negative
│   └── Top Topics: Gameplay (90), Bugs (80)...
│
└── 🏴 Japanese Players (120 mentions)
    ├── 😊 70% Positive | 😞 10% Negative
    └── Top Topics: Story (45), Music (30)...

🎯 DETAILED TOPIC ANALYSIS
├── 1. GRAPHICS & ART STYLE
│   ├── 😊 Positive (+0.450)
│   ├── 👥 250 mentions
│   ├── 🌍 Chinese: 150 | English: 70 | Japanese: 30
│   ├── 💡 Players consistently praise stunning visuals...
│   ├── 🗺️ Chinese players emphasize atmosphere...
│   └── 💬 Examples: "画面太美了", "Graphics amazing"
│
├── 2. MUSIC & SOUNDTRACK
│   └── ...
│
└── 3. BUGS & PERFORMANCE
    └── ...
```

## Button Text Update

The "Enhance with LLM" button has been renamed to:

**"🌏 Generate Cross-Cultural Analysis Report"**

This better reflects what it does: creates a comprehensive analysis report rather than modifying the original data.

## File Locations

| Type | Location | Purpose |
|------|----------|---------|
| NLP Reports (Original) | `reports/*.json` | Raw NLP processing results |
| Analysis Reports (HTML) | `analysis/*.html` | Professional cross-cultural analysis |
| Analysis Data (JSON) | `analysis/*.json` | Analysis data for reference |
| Chart Images | `analysis/*.png` | Individual chart files |

## Usage Tips

1. **Always start with NLP processing** - Generate the base data first
2. **Analysis is non-destructive** - Run it multiple times if needed
3. **Reports open automatically** - Check your browser after generation
4. **Share easily** - HTML files are self-contained and shareable
5. **Present professionally** - Use HTML reports in meetings or emails
6. **Reference data** - JSON files provide raw data for further analysis

## Benefits

✅ **Clear separation**: NLP data vs. Analysis reports
✅ **Professional presentation**: Ready for stakeholders
✅ **Cross-cultural focus**: Emphasizes cultural differences
✅ **Integrated charts**: Everything in one document
✅ **Easy sharing**: Single HTML file
✅ **Non-destructive**: Original data preserved
✅ **Reproducible**: Regenerate anytime

## Technical Details

### Report Generation Process

1. **Read NLP Data**: Load original report from `reports/` folder
2. **LLM Enhancement**: Generate topic names and insights using Qwen
3. **Cultural Analysis**: Analyze distribution and preferences per culture
4. **Chart Generation**: Create visualizations with matplotlib
5. **HTML Assembly**: Combine everything into styled HTML document
6. **Base64 Encoding**: Embed charts directly in HTML
7. **File Saving**: Save HTML, JSON, and PNG files to `analysis/` folder
8. **Auto-Open**: Open report in default browser

### LLM Features

- **Topic Naming**: Transforms "Topic 1" → "Graphics & Art Style"
- **Insight Generation**: 2-3 sentence summary per topic
- **Cultural Analysis**: Compares preferences across cultures
- **Overall Summary**: Key takeaways from all data

### Fallback Mode

If LLM is not available:
- Topic naming uses keyword extraction
- Summaries use templates
- Charts and cultural analysis still work
- Report is still generated (just without LLM insights)

## Migration from Old System

**Old Approach** (now removed):
- Modified NLP reports with `*_enhanced.json` suffix
- Charts saved separately in `charts/` folder
- No unified report document

**New Approach** (current):
- Original NLP reports untouched
- Comprehensive HTML analysis reports
- Charts embedded in HTML
- Professional, shareable format

## Troubleshooting

**Q: Where did the enhanced reports go?**
A: They're now called "analysis reports" and are in the `analysis/` folder as HTML files.

**Q: Can I still see the charts?**
A: Yes, they're embedded in the HTML report and also saved as PNG files in `analysis/` folder.

**Q: What happened to my original NLP reports?**
A: They're safe and untouched in the `reports/` folder.

**Q: Can I regenerate analysis?**
A: Yes, just click the button again. Original data is never modified.

**Q: How do I share the analysis?**
A: Share the HTML file - it's self-contained and opens in any browser.

## Summary

The new system provides **professional, comprehensive cross-cultural analysis reports** that are:
- Easy to generate (one click)
- Easy to share (single HTML file)
- Easy to understand (clear layout, integrated charts)
- Easy to reproduce (non-destructive)
- Focused on cross-cultural insights (the main goal)

This aligns with the project goal of providing actionable cross-cultural insights for game developers.
