"""
Chart generation utilities for enhanced reports
Creates visual charts from analysis data
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from typing import Dict, List
import os
import warnings

class ReportChartGenerator:
    """Generates charts and visualizations for enhanced reports"""
    
    def __init__(self, output_dir: str = "charts"):
        """
        Initialize chart generator
        
        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Configure fonts for CJK (Chinese/Japanese/Korean) character support
        self._configure_cjk_fonts()
        
        # Set style for modern dark theme
        plt.style.use('dark_background')
        self.colors = {
            'positive': '#6c5ce7',  # Violet
            'neutral': '#4a69bd',    # Blue
            'negative': '#e74c3c',   # Red
            'accent': '#2ecc71'      # Green
        }
    
    def _configure_cjk_fonts(self):
        """Configure matplotlib to support CJK characters"""
        # Try to find suitable CJK fonts
        cjk_fonts = []
        for font in fm.fontManager.ttflist:
            font_name_lower = font.name.lower()
            # Look for common CJK font families
            if any(cjk in font_name_lower for cjk in [
                'noto', 'droid', 'wqy', 'source han', 'microsoft yahei', 
                'simhei', 'simsun', 'meiryo', 'yu gothic', 'malgun'
            ]):
                cjk_fonts.append(font.name)
        
        if cjk_fonts:
            # Use the first available CJK font
            plt.rcParams['font.sans-serif'] = [cjk_fonts[0]] + plt.rcParams['font.sans-serif']
            print(f"✅ Using CJK font: {cjk_fonts[0]}")
        else:
            # Fallback: use DejaVu Sans and suppress warnings
            print("⚠️ No CJK fonts found, using fallback (some characters may not display)")
            warnings.filterwarnings('ignore', category=UserWarning, message='.*Glyph.*missing.*')
        
        # Set font fallback chain to handle missing glyphs gracefully
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.unicode_minus'] = False  # Fix minus sign display
    
    def generate_sentiment_pie_chart(self, sentiment_dist: Dict, output_name: str = "sentiment_dist.png") -> str:
        """
        Generate a pie chart showing sentiment distribution
        
        Args:
            sentiment_dist: Dictionary with positive/neutral/negative counts
            output_name: Output filename
            
        Returns:
            Path to saved chart
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        
        labels = []
        sizes = []
        colors = []
        
        for sentiment, count in sentiment_dist.items():
            if count > 0:
                labels.append(f"{sentiment.capitalize()}\n({count})")
                sizes.append(count)
                colors.append(self.colors.get(sentiment, '#95a5a6'))
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 12, 'weight': 'bold'})
        ax.set_title('Sentiment Distribution', fontsize=16, weight='bold', pad=20)
        
        output_path = os.path.join(self.output_dir, output_name)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
        plt.close()
        
        return output_path
    
    def generate_topic_density_bar_chart(self, chart_data: Dict, output_name: str = "topic_density.png") -> str:
        """
        Generate a bar chart showing topic densities
        
        Args:
            chart_data: Dictionary with labels and values
            output_name: Output filename
            
        Returns:
            Path to saved chart
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        labels = chart_data.get('labels', [])
        values = chart_data.get('values', [])
        
        # Truncate long labels
        short_labels = [l[:20] + '...' if len(l) > 20 else l for l in labels]
        
        bars = ax.bar(range(len(values)), values, color=self.colors['positive'], alpha=0.8)
        
        # Color code by value intensity
        max_val = max(values) if values else 1
        for i, bar in enumerate(bars):
            intensity = values[i] / max_val
            bar.set_color(plt.cm.viridis(intensity))
        
        ax.set_xlabel('Topics', fontsize=12, weight='bold')
        ax.set_ylabel('Number of Mentions', fontsize=12, weight='bold')
        ax.set_title('Top Topics by Player Mentions', fontsize=16, weight='bold', pad=20)
        ax.set_xticks(range(len(short_labels)))
        ax.set_xticklabels(short_labels, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)
        
        output_path = os.path.join(self.output_dir, output_name)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
        plt.close()
        
        return output_path
    
    def generate_sentiment_score_distribution(self, topics: List[Dict], output_name: str = "sentiment_scores.png") -> str:
        """
        Generate a histogram showing sentiment score distribution
        
        Args:
            topics: List of topic dictionaries
            output_name: Output filename
            
        Returns:
            Path to saved chart
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        scores = [t.get('sentiment_score', 0) for t in topics]
        
        # Create histogram
        n, bins, patches = ax.hist(scores, bins=20, color=self.colors['accent'], 
                                     alpha=0.7, edgecolor='white', linewidth=0.5)
        
        # Color code bars by sentiment
        for i, patch in enumerate(patches):
            bin_center = (bins[i] + bins[i+1]) / 2
            if bin_center > 0.05:
                patch.set_facecolor(self.colors['positive'])
            elif bin_center < -0.05:
                patch.set_facecolor(self.colors['negative'])
            else:
                patch.set_facecolor(self.colors['neutral'])
        
        # Add vertical lines for mean and quartiles
        mean_score = np.mean(scores)
        ax.axvline(mean_score, color='yellow', linestyle='--', linewidth=2, 
                   label=f'Mean: {mean_score:.3f}')
        ax.axvline(0, color='white', linestyle='-', linewidth=1, alpha=0.5)
        
        ax.set_xlabel('Sentiment Score', fontsize=12, weight='bold')
        ax.set_ylabel('Number of Topics', fontsize=12, weight='bold')
        ax.set_title('Sentiment Score Distribution', fontsize=16, weight='bold', pad=20)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        output_path = os.path.join(self.output_dir, output_name)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
        plt.close()
        
        return output_path
    
    def generate_all_charts(self, enhanced_report: Dict, report_name: str) -> Dict[str, str]:
        """
        Generate all available charts for a report
        
        Args:
            enhanced_report: Enhanced report dictionary
            report_name: Name prefix for output files
            
        Returns:
            Dictionary mapping chart type to file path
        """
        chart_paths = {}
        
        if 'charts' not in enhanced_report:
            return chart_paths
        
        charts_data = enhanced_report['charts']
        topics = enhanced_report.get('topics', [])
        
        # Generate sentiment distribution pie chart
        if 'sentiment_distribution' in charts_data:
            path = self.generate_sentiment_pie_chart(
                charts_data['sentiment_distribution'],
                f"{report_name}_sentiment_dist.png"
            )
            chart_paths['sentiment_distribution'] = path
        
        # Generate topic density bar chart
        if 'top_topics_by_density' in charts_data:
            path = self.generate_topic_density_bar_chart(
                charts_data['top_topics_by_density'],
                f"{report_name}_topic_density.png"
            )
            chart_paths['topic_density'] = path
        
        # Generate sentiment score distribution
        if topics:
            path = self.generate_sentiment_score_distribution(
                topics,
                f"{report_name}_sentiment_scores.png"
            )
            chart_paths['sentiment_scores'] = path
        
        return chart_paths


# Test/example usage
if __name__ == "__main__":
    import json
    import tempfile
    
    # Create sample data
    sample_report = {
        'topics': [
            {'topic_id': 1, 'density': 179, 'sentiment_score': 0.21, 'sentiment_label': 'positive'},
            {'topic_id': 2, 'density': 101, 'sentiment_score': 0.54, 'sentiment_label': 'positive'},
            {'topic_id': 3, 'density': 85, 'sentiment_score': -0.32, 'sentiment_label': 'negative'},
            {'topic_id': 4, 'density': 120, 'sentiment_score': 0.45, 'sentiment_label': 'positive'},
            {'topic_id': 5, 'density': 95, 'sentiment_score': 0.19, 'sentiment_label': 'positive'},
        ],
        'charts': {
            'sentiment_distribution': {'positive': 495, 'neutral': 0, 'negative': 85},
            'top_topics_by_density': {
                'labels': ['Night City', 'Graphics', 'Bugs', 'Music', 'Story'],
                'values': [179, 120, 101, 95, 85]
            }
        }
    }
    
    # Use temporary directory for cross-platform compatibility
    output_dir = os.path.join(tempfile.gettempdir(), 'charts')
    generator = ReportChartGenerator(output_dir=output_dir)
    paths = generator.generate_all_charts(sample_report, 'cyberpunk_demo')
    
    print("Generated charts:")
    for chart_type, path in paths.items():
        print(f"  {chart_type}: {path}")
