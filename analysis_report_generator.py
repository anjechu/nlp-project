"""
Cross-Cultural Analysis Report Generator
Creates professional, comprehensive analysis reports with integrated charts and insights
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import base64
from io import BytesIO

class AnalysisReportGenerator:
    """Generates comprehensive cross-cultural analysis reports in HTML format"""
    
    def __init__(self, llm_generator=None, chart_generator=None):
        """
        Initialize the analysis report generator
        
        Args:
            llm_generator: LLMReportGenerator instance for generating insights
            chart_generator: ReportChartGenerator instance for generating charts
        """
        self.llm_generator = llm_generator
        self.chart_generator = chart_generator
    
    def generate_analysis_report(self, nlp_data: Dict, output_dir: str = "analysis") -> str:
        """
        Generate a complete cross-cultural analysis report
        
        Args:
            nlp_data: Original NLP processing result (untouched)
            output_dir: Directory to save analysis reports
            
        Returns:
            Path to generated HTML report
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"analysis_{timestamp}"
        
        # Step 1: Enhance with LLM (topic naming, summaries, cultural analysis)
        enhanced_data = self._enhance_with_llm(nlp_data)
        
        # Step 2: Generate charts and get base64 encoded images
        chart_images = self._generate_chart_images(enhanced_data, base_name, output_dir)
        
        # Step 3: Generate HTML report
        html_content = self._generate_html_report(enhanced_data, chart_images, nlp_data)
        
        # Step 4: Save report
        html_path = os.path.join(output_dir, f"{base_name}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Step 5: Save enhanced JSON for reference
        json_path = os.path.join(output_dir, f"{base_name}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
        
        return html_path
    
    def _enhance_with_llm(self, nlp_data: Dict) -> Dict:
        """Enhance NLP data with LLM insights"""
        if self.llm_generator and self.llm_generator.llm_available:
            return self.llm_generator.generate_enhanced_report(
                nlp_data, 
                include_charts=True, 
                include_cultural_analysis=True
            )
        else:
            # Fallback: return original data with basic enhancements
            return {
                **nlp_data,
                'llm_enhanced': False,
                'cross_cultural': False
            }
    
    def _generate_chart_images(self, enhanced_data: Dict, base_name: str, output_dir: str) -> Dict:
        """Generate charts and return as base64 encoded strings for HTML embedding"""
        chart_images = {}
        
        if not self.chart_generator or 'charts' not in enhanced_data:
            return chart_images
        
        try:
            # Generate charts to temporary location
            import tempfile
            temp_dir = tempfile.mkdtemp()
            
            # Generate all charts
            chart_paths = self.chart_generator.generate_all_charts(enhanced_data, base_name)
            
            # Read charts and convert to base64
            for chart_type, chart_path in chart_paths.items():
                if os.path.exists(chart_path):
                    with open(chart_path, 'rb') as f:
                        img_data = f.read()
                        img_base64 = base64.b64encode(img_data).decode('utf-8')
                        chart_images[chart_type] = img_base64
                    
                    # Also copy to output directory
                    import shutil
                    dest_path = os.path.join(output_dir, os.path.basename(chart_path))
                    shutil.copy(chart_path, dest_path)
        
        except Exception as e:
            print(f"⚠️ Chart generation error: {e}")
        
        return chart_images
    
    def _generate_html_report(self, enhanced_data: Dict, chart_images: Dict, original_data: Dict) -> str:
        """Generate comprehensive HTML report with embedded charts"""
        
        # Extract data
        topics = enhanced_data.get('topics', [])
        stats = enhanced_data.get('statistics', {})
        charts = enhanced_data.get('charts', {})
        cultural_summary = enhanced_data.get('cultural_summary', '')
        is_llm_enhanced = enhanced_data.get('llm_enhanced', False)
        
        # Start HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cross-Cultural Game Feedback Analysis Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #16213e;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #6c5ce7 0%, #4a69bd 100%);
            padding: 40px;
            text-align: center;
            border-bottom: 3px solid #2d2d44;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            color: #ffffff;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            color: #d0d0e8;
            margin-top: 10px;
        }}
        
        .header .meta {{
            margin-top: 15px;
            font-size: 0.9em;
            color: #b0b0c0;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 50px;
            padding: 30px;
            background: #1a1a2e;
            border-radius: 8px;
            border: 1px solid #2d2d44;
        }}
        
        .section h2 {{
            font-size: 1.8em;
            color: #6c5ce7;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #2d2d44;
        }}
        
        .section h3 {{
            font-size: 1.4em;
            color: #4a69bd;
            margin: 25px 0 15px 0;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: #0f1419;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #2d2d44;
            text-align: center;
        }}
        
        .stat-card .value {{
            font-size: 2.5em;
            color: #6c5ce7;
            font-weight: bold;
            display: block;
            margin-bottom: 10px;
        }}
        
        .stat-card .label {{
            font-size: 1em;
            color: #a0a0a0;
        }}
        
        .topic-card {{
            background: #0f1419;
            padding: 25px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 4px solid #6c5ce7;
        }}
        
        .topic-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .topic-title {{
            font-size: 1.5em;
            color: #ffffff;
            font-weight: bold;
        }}
        
        .sentiment-badge {{
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .sentiment-positive {{
            background: rgba(108, 92, 231, 0.2);
            color: #6c5ce7;
        }}
        
        .sentiment-negative {{
            background: rgba(231, 76, 60, 0.2);
            color: #e74c3c;
        }}
        
        .sentiment-neutral {{
            background: rgba(74, 105, 189, 0.2);
            color: #4a69bd;
        }}
        
        .topic-meta {{
            display: flex;
            gap: 30px;
            margin: 15px 0;
            font-size: 0.95em;
            color: #b0b0b0;
        }}
        
        .topic-meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .insight-box {{
            background: rgba(108, 92, 231, 0.1);
            border-left: 3px solid #6c5ce7;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        
        .cultural-box {{
            background: rgba(74, 105, 189, 0.1);
            border-left: 3px solid #4a69bd;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }}
        
        .cultural-dist {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin: 10px 0;
        }}
        
        .cultural-item {{
            background: #1a1a2e;
            padding: 8px 15px;
            border-radius: 6px;
            border: 1px solid #2d2d44;
        }}
        
        .chart-container {{
            margin: 30px 0;
            text-align: center;
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            border: 1px solid #2d2d44;
        }}
        
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }}
        
        .examples {{
            background: #0f1419;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
        }}
        
        .example-item {{
            padding: 10px;
            margin: 8px 0;
            border-left: 2px solid #2d2d44;
            padding-left: 15px;
            font-style: italic;
            color: #d0d0d0;
        }}
        
        .summary-highlight {{
            background: linear-gradient(135deg, rgba(108, 92, 231, 0.15) 0%, rgba(74, 105, 189, 0.15) 100%);
            padding: 25px;
            border-radius: 8px;
            border: 1px solid #2d2d44;
            margin: 20px 0;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            background: #0f1419;
            color: #808080;
            font-size: 0.9em;
            border-top: 1px solid #2d2d44;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.8em; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
            .chart-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌏 Cross-Cultural Game Feedback Analysis</h1>
            <div class="subtitle">Comprehensive Player Sentiment & Cultural Insights Report</div>
            <div class="meta">
                Generated: {datetime.now().strftime("%B %d, %Y at %H:%M:%S")} | 
                Analysis Mode: {'✨ LLM-Enhanced' if is_llm_enhanced else '📝 Basic Analysis'}
            </div>
        </div>
        
        <div class="content">
"""
        
        # Executive Summary Section
        html += self._generate_executive_summary(stats, topics, cultural_summary, is_llm_enhanced)
        
        # Visual Overview Section with Charts
        if chart_images:
            html += self._generate_visual_overview(chart_images, charts)
        
        # Cultural Analysis Section
        html += self._generate_cultural_analysis_section(topics, cultural_summary, is_llm_enhanced)
        
        # Detailed Topic Analysis Section
        html += self._generate_topics_section(topics, is_llm_enhanced)
        
        # Methodology Section
        html += self._generate_methodology_section(stats, original_data)
        
        # Close HTML
        html += """
        </div>
        
        <div class="footer">
            <p>This report was automatically generated by the NLP Cross-Cultural Analysis System</p>
            <p>For questions or feedback, please refer to the project documentation</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def _generate_executive_summary(self, stats: Dict, topics: List[Dict], cultural_summary: str, is_llm: bool) -> str:
        """Generate executive summary section"""
        total = stats.get('total', 0)
        valid = stats.get('valid', total)
        
        # Calculate sentiment distribution
        positive_count = sum(1 for t in topics if t.get('sentiment_label', '').lower() == 'positive')
        negative_count = sum(1 for t in topics if t.get('sentiment_label', '').lower() == 'negative')
        neutral_count = len(topics) - positive_count - negative_count
        
        # Get cultural distribution
        all_cultures = {}
        for topic in topics:
            dist = topic.get('cultural_distribution', {})
            for lang, count in dist.items():
                culture_name = self._get_culture_name(lang)
                all_cultures[culture_name] = all_cultures.get(culture_name, 0) + count
        
        html = """
            <div class="section">
                <h2>📊 Executive Summary</h2>
                
                <div class="stats-grid">
"""
        
        html += f"""
                    <div class="stat-card">
                        <span class="value">{total}</span>
                        <span class="label">Total Reviews</span>
                    </div>
                    <div class="stat-card">
                        <span class="value">{len(topics)}</span>
                        <span class="label">Topics Identified</span>
                    </div>
                    <div class="stat-card">
                        <span class="value">{len(all_cultures)}</span>
                        <span class="label">Cultures Analyzed</span>
                    </div>
                    <div class="stat-card">
                        <span class="value">{positive_count}</span>
                        <span class="label">Positive Topics</span>
                    </div>
"""
        
        html += """
                </div>
"""
        
        if cultural_summary and is_llm:
            html += f"""
                <div class="summary-highlight">
                    <h3>🗺️ Key Cross-Cultural Insights</h3>
                    <p style="font-size: 1.1em; line-height: 1.8;">{cultural_summary}</p>
                </div>
"""
        
        html += """
            </div>
"""
        
        return html
    
    def _generate_visual_overview(self, chart_images: Dict, charts: Dict) -> str:
        """Generate visual overview section with charts"""
        html = """
            <div class="section">
                <h2>📈 Visual Overview</h2>
                <p style="margin-bottom: 30px; color: #b0b0b0;">
                    The following visualizations provide a quick overview of sentiment distribution, 
                    topic density, and score patterns across all player feedback.
                </p>
                
                <div class="chart-grid">
"""
        
        for chart_type, img_base64 in chart_images.items():
            chart_title = chart_type.replace('_', ' ').title()
            html += f"""
                    <div class="chart-container">
                        <h3>{chart_title}</h3>
                        <img src="data:image/png;base64,{img_base64}" alt="{chart_title}" />
                    </div>
"""
        
        html += """
                </div>
            </div>
"""
        
        return html
    
    def _generate_cultural_analysis_section(self, topics: List[Dict], cultural_summary: str, is_llm: bool) -> str:
        """Generate dedicated cross-cultural comparison section"""
        html = """
            <div class="section">
                <h2>🌏 Cross-Cultural Analysis</h2>
                <p style="margin-bottom: 30px; color: #b0b0b0;">
                    This section highlights differences in player preferences across cultural backgrounds, 
                    helping identify market-specific insights and opportunities.
                </p>
"""
        
        # Aggregate cultural data
        culture_topics = {}
        for topic in topics:
            dist = topic.get('cultural_distribution', {})
            for lang, count in dist.items():
                culture = self._get_culture_name(lang)
                if culture not in culture_topics:
                    culture_topics[culture] = {'total': 0, 'positive': 0, 'negative': 0, 'topics': []}
                
                culture_topics[culture]['total'] += count
                sentiment = topic.get('sentiment_label', '').lower()
                if sentiment == 'positive':
                    culture_topics[culture]['positive'] += count
                elif sentiment == 'negative':
                    culture_topics[culture]['negative'] += count
                
                culture_topics[culture]['topics'].append({
                    'name': topic.get('topic_name', f"Topic {topic.get('topic_id')}"),
                    'count': count,
                    'sentiment': sentiment
                })
        
        # Display cultural comparison
        for culture, data in sorted(culture_topics.items(), key=lambda x: x[1]['total'], reverse=True):
            pos_pct = (data['positive'] / data['total'] * 100) if data['total'] > 0 else 0
            neg_pct = (data['negative'] / data['total'] * 100) if data['total'] > 0 else 0
            
            html += f"""
                <div class="cultural-box">
                    <h3>🏴 {culture} Players ({data['total']} mentions)</h3>
                    <div class="topic-meta">
                        <div class="topic-meta-item">
                            <span>😊 {pos_pct:.1f}% Positive</span>
                        </div>
                        <div class="topic-meta-item">
                            <span>😞 {neg_pct:.1f}% Negative</span>
                        </div>
                    </div>
                    <p style="margin-top: 15px;"><strong>Top Discussion Topics:</strong></p>
                    <div class="cultural-dist">
"""
            
            # Show top 5 topics for this culture
            for topic_info in sorted(data['topics'], key=lambda x: x['count'], reverse=True)[:5]:
                html += f"""
                        <div class="cultural-item">
                            {topic_info['name']}: {topic_info['count']} mentions
                        </div>
"""
            
            html += """
                    </div>
                </div>
"""
        
        html += """
            </div>
"""
        
        return html
    
    def _generate_topics_section(self, topics: List[Dict], is_llm: bool) -> str:
        """Generate detailed topics section"""
        html = """
            <div class="section">
                <h2>🎯 Detailed Topic Analysis</h2>
                <p style="margin-bottom: 30px; color: #b0b0b0;">
                    In-depth analysis of each major topic identified in player feedback, 
                    including sentiment, cultural distribution, and key insights.
                </p>
"""
        
        # Sort topics by density
        sorted_topics = sorted(topics, key=lambda x: x.get('density', 0), reverse=True)
        
        for idx, topic in enumerate(sorted_topics[:15], 1):  # Top 15 topics
            topic_id = topic.get('topic_id', idx)
            topic_name = topic.get('topic_name', f'Topic {topic_id}')
            density = topic.get('density', 0)
            sentiment = topic.get('sentiment_label', 'neutral')
            score = topic.get('sentiment_score', 0)
            
            sentiment_class = f"sentiment-{sentiment.lower()}"
            sentiment_emoji = {'positive': '😊', 'negative': '😞', 'neutral': '😐'}.get(sentiment.lower(), '😐')
            
            html += f"""
                <div class="topic-card">
                    <div class="topic-header">
                        <div class="topic-title">{idx}. {topic_name}</div>
                        <div class="sentiment-badge {sentiment_class}">
                            {sentiment_emoji} {sentiment.capitalize()} ({score:+.3f})
                        </div>
                    </div>
                    
                    <div class="topic-meta">
                        <div class="topic-meta-item">
                            <span>👥 {density} mentions</span>
                        </div>
"""
            
            # Add cultural distribution
            if 'cultural_analysis' in topic:
                cultural = topic['cultural_analysis']
                dist = cultural.get('distribution', {})
                if dist:
                    cultures_str = ', '.join([f"{c}: {cnt}" for c, cnt in dist.items()])
                    html += f"""
                        <div class="topic-meta-item">
                            <span>🌍 {cultures_str}</span>
                        </div>
"""
            
            html += """
                    </div>
"""
            
            # Add LLM summary
            if 'summary' in topic and is_llm:
                html += f"""
                    <div class="insight-box">
                        <strong>💡 Insight:</strong> {topic['summary']}
                    </div>
"""
            
            # Add cultural insights
            if 'cultural_analysis' in topic and 'llm_insight' in topic['cultural_analysis']:
                html += f"""
                    <div class="cultural-box">
                        <strong>🗺️ Cross-Cultural Insight:</strong> {topic['cultural_analysis']['llm_insight']}
                    </div>
"""
            
            # Add examples
            examples = topic.get('representative_sentences', [])
            if examples:
                html += """
                    <div class="examples">
                        <strong>💬 Representative Examples:</strong>
"""
                for example in examples[:3]:
                    html += f"""
                        <div class="example-item">"{example}"</div>
"""
                html += """
                    </div>
"""
            
            html += """
                </div>
"""
        
        html += """
            </div>
"""
        
        return html
    
    def _generate_methodology_section(self, stats: Dict, original_data: Dict) -> str:
        """Generate methodology and data source section"""
        html = """
            <div class="section">
                <h2>📋 Methodology & Data Sources</h2>
                
                <h3>Data Collection</h3>
                <p style="margin: 15px 0; line-height: 1.8; color: #d0d0d0;">
                    This analysis is based on player reviews collected from multiple platforms and languages. 
                    The data underwent preprocessing including language detection, sentiment analysis, 
                    and topic modeling using advanced NLP techniques.
                </p>
                
                <h3>Analysis Techniques</h3>
                <ul style="margin: 15px 0 15px 20px; line-height: 2; color: #d0d0d0;">
                    <li><strong>Sentiment Analysis:</strong> Automated sentiment scoring using trained models</li>
                    <li><strong>Topic Modeling:</strong> HDBSCAN clustering to identify discussion themes</li>
                    <li><strong>Cultural Analysis:</strong> Language-based segmentation and comparison</li>
                    <li><strong>LLM Enhancement:</strong> Qwen model for topic naming and insight generation</li>
                </ul>
                
                <h3>Data Statistics</h3>
                <div class="stats-grid">
"""
        
        total = stats.get('total', 0)
        valid = stats.get('valid', total)
        
        html += f"""
                    <div class="stat-card">
                        <span class="value">{total}</span>
                        <span class="label">Raw Reviews</span>
                    </div>
                    <div class="stat-card">
                        <span class="value">{valid}</span>
                        <span class="label">Processed Reviews</span>
                    </div>
                    <div class="stat-card">
                        <span class="value">{(valid/total*100) if total > 0 else 0:.1f}%</span>
                        <span class="label">Data Quality</span>
                    </div>
"""
        
        html += """
                </div>
            </div>
"""
        
        return html
    
    def _get_culture_name(self, lang_code: str) -> str:
        """Convert language code to readable culture name"""
        mapping = {
            'schinese': 'Chinese',
            'tchinese': 'Chinese',
            'japanese': 'Japanese',
            'english': 'English',
            'korean': 'Korean'
        }
        return mapping.get(lang_code.lower(), lang_code.capitalize())


# Standalone test
if __name__ == "__main__":
    print("Analysis Report Generator module loaded successfully")
