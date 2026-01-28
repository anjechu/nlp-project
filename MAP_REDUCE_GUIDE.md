# Map-Reduce Architecture Guide

## Overview

The Map-Reduce architecture prevents LLM context overflow by processing each [game + language] combination independently before aggregating results.

## Problem Solved

**Before Map-Reduce:**
- All game reviews (Chinese + Japanese + English) fed to LLM at once
- Context overflow → LLM forgets Chinese positive topics
- Topic names inconsistent (mixing languages)
- Some valuable topics lost in the noise

**After Map-Reduce:**
- Each [game + language] processed separately
- Full LLM attention on each specific context
- All positive AND negative valuable topics preserved
- Consistent dual-language naming

## Architecture

### Phase 1: MAP
```
Input: Report_comments_bf6_chinese_20260124_023938.json
       └─> 12 topics from bf6 Chinese reviews

Process independently with LLM:
  - Filter valuable topics (8 kept)
  - Generate dual-language names (Chinese + English)
  - Create summaries with full context

Output: 8 valuable Chinese topics with metadata
```

### Phase 2: REDUCE
```
Aggregate results from all MAP phases:
  - bf6 Chinese: 8 topics
  - bf6 Japanese: 6 topics  
  - bf6 English: 7 topics
  - silksong Chinese: 9 topics
  - ...

Total: 30+ valuable topics (no hardcoded limit)
```

### Phase 3: GLOBAL
```
Generate final report from aggregated valuable topics:
  - Cross-cultural analysis
  - Game-specific comparisons
  - Charts and visualizations
  - HTML report
```

## Usage

### GUI (Automatic)

The GUI automatically uses Map-Reduce when you click **"Generate Cross-Cultural Analysis"**:

1. Load multiple NLP reports (different games/languages)
2. Click "Generate Cross-Cultural Analysis" button
3. System automatically:
   - Detects game+language from filenames
   - Runs MAP phase on each combination
   - Aggregates results (REDUCE)
   - Generates final report (GLOBAL)

### Programmatic API

```python
from analysis_report_generator import AnalysisReportGenerator
from llm_report_generator import LLMReportGenerator

# Initialize
llm_gen = LLMReportGenerator(use_ollama=True)
report_gen = AnalysisReportGenerator(llm_generator=llm_gen)

# Load your NLP reports
nlp_reports = [
    load_json("Report_comments_bf6_chinese_20260124_023938.json"),
    load_json("Report_comments_bf6_japanese_20260124_023938.json"),
    load_json("Report_comments_bf6_english_20260124_023938.json"),
]

filenames = [
    "Report_comments_bf6_chinese_20260124_023938.json",
    "Report_comments_bf6_japanese_20260124_023938.json", 
    "Report_comments_bf6_english_20260124_023938.json",
]

# Generate with Map-Reduce
html_path = report_gen.generate_analysis_report_with_map_reduce(
    nlp_reports,
    output_dir="analysis",
    report_filenames=filenames
)

print(f"Report generated: {html_path}")
```

## Expected Output

### Console Output Example

```
================================================================================
🚀 STARTING MAP-REDUCE ANALYSIS
================================================================================
📊 Input: 3 game+language combinations
   • bf6 (chinese)
   • bf6 (japanese)
   • bf6 (english)

🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 
PHASE 1: MAP - Independent Processing
🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 🗺️ 

[1/3] Processing: bf6 - chinese
================================================================================
🔍 MAP PHASE: Processing [bf6] + [chinese] independently
================================================================================
📊 Input: 12 topics from bf6 (Chinese)
✅ LLM filtered 12 topics → 8 valuable topics
✅ MAP COMPLETE: 8 valuable topics extracted
   (Filtered from 12 original topics)

[2/3] Processing: bf6 - japanese
[3/3] Processing: bf6 - english

🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 
PHASE 2: REDUCE - Aggregation
🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 🔄 

📊 REDUCE COMPLETE:
   • Total valuable topics: 21
   • Games: bf6
   • Languages: chinese, japanese, english

🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 
PHASE 3: GLOBAL - Final Report Generation
🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 🌏 

📈 Generating charts from 21 valuable topics...
🌏 Generating cross-cultural summary...
📄 Creating HTML report...

================================================================================
✅ MAP-REDUCE ANALYSIS COMPLETE
================================================================================
📄 HTML Report: analysis/analysis_mapreduce_20260127_164532.html
📊 JSON Data: analysis/analysis_mapreduce_20260127_164532.json
🎯 Total Valuable Topics: 21
================================================================================
```

## Benefits

✅ **No Context Overflow**: Each [game + language] gets dedicated LLM focus

✅ **Preserves ALL Valuable Topics**: Chinese positive topics no longer forgotten

✅ **Better Topic Naming**: LLM generates accurate names in native language + English

✅ **Smarter Filtering**: LLM properly identifies valuable topics without hardcoded limits

✅ **Scalable**: Can process 10+ game+language combinations without issues

## Comparison

| Feature | Old Approach | Map-Reduce Approach |
|---------|--------------|---------------------|
| Context per LLM call | ALL reviews at once | Single [game+language] |
| Topics forgotten? | Yes (Chinese positive) | No |
| Topic naming consistency | Mixed languages | Dual-language (native+EN) |
| Valuable topic detection | Density-based top 5 | LLM intelligent filtering |
| Positive feedback preserved | Often lost | Always preserved |
| Scalability | Poor (>6 reports = overflow) | Excellent (unlimited) |

## File Naming Convention

The system automatically parses filenames to extract game and language:

**Format**: `Report_comments_<game>_<language>_<timestamp>.json`

**Examples**:
- `Report_comments_bf6_chinese_20260124_023938.json` → game: bf6, language: chinese
- `Report_comments_silksong_english_20260127_143022.json` → game: silksong, language: english
- `Report_comments_blackmyth_japanese_20260126_092145.json` → game: blackmyth, language: japanese

## Output Files

Map-Reduce generates files with `mapreduce` prefix:

- `analysis_mapreduce_20260127_164532.html` - Interactive HTML report
- `analysis_mapreduce_20260127_164532.json` - Complete data with metadata
- `sentiment_distribution_*.png` - Chart images
- `topic_density_*.png` - More charts

## Troubleshooting

**Q: "LLM not available, falling back to standard aggregation"**

A: Your LLM (Ollama) is not running. Start it with:
```bash
ollama serve
ollama pull qwen:7b
```

**Q: Can I use the old approach?**

A: Yes, use `generate_analysis_report()` instead of `generate_analysis_report_with_map_reduce()`. However, Map-Reduce is recommended for multi-game/multi-language analysis.

**Q: How many reports can I process?**

A: No hardcoded limit. Map-Reduce scales to 20+ game+language combinations.

**Q: Does it work with 1 report?**

A: Yes, but Map-Reduce benefits are most visible with 3+ reports. For single reports, both approaches work similarly.

## Technical Details

### Key Methods

**llm_report_generator.py**:
- `process_game_language_independently()` - MAP phase
- `aggregate_map_results()` - REDUCE phase

**analysis_report_generator.py**:
- `generate_analysis_report_with_map_reduce()` - Complete pipeline
- Falls back to standard approach if LLM unavailable

### Metadata Tracking

Each MAP result includes:
```json
{
  "map_metadata": {
    "game_name": "bf6",
    "language": "chinese",
    "processed_independently": true,
    "original_topic_count": 12,
    "valuable_topic_count": 8
  }
}
```

This helps track which topics came from which source during REDUCE phase.

## Future Enhancements

- [ ] Parallel MAP processing (concurrent.futures)
- [ ] Streaming progress updates to GUI
- [ ] Incremental REDUCE (add reports one at a time)
- [ ] Cache MAP results to avoid reprocessing

## Credits

Implemented by GitHub Copilot based on user requirements to solve LLM context overflow issues in cross-cultural game review analysis.
