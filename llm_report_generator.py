"""
LLM-Enhanced Report Generator
Integrates Qwen local LLM to generate enhanced insights with topic naming and visualizations
"""

import json
import os
from typing import Dict, List, Optional
import numpy as np

class LLMReportGenerator:
    """Generates enhanced reports using local LLM (Qwen) for topic naming and insights"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the LLM report generator
        
        Args:
            model_path: Path to local Qwen model (if None, will try to auto-detect or use API)
        """
        self.model_path = model_path
        self.llm_available = False
        self.model = None
        self.tokenizer = None
        self._init_llm()
    
    def _init_llm(self):
        """Initialize the Qwen LLM model"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            # Try to load Qwen model
            model_name = self.model_path or "Qwen/Qwen-7B-Chat"  # Default to Qwen chat model
            
            print(f"🤖 Loading LLM model: {model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name, 
                trust_remote_code=True
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                trust_remote_code=True
            ).eval()
            
            self.llm_available = True
            print("✅ LLM model loaded successfully")
            
        except Exception as e:
            print(f"⚠️ LLM not available: {e}")
            print("📝 Will generate basic reports without LLM enhancement")
            self.llm_available = False
    
    def generate_topic_name(self, topic_data: Dict) -> str:
        """
        Generate a meaningful name for a topic using LLM
        
        Args:
            topic_data: Dictionary containing topic information
            
        Returns:
            A concise topic name (e.g., "Art Style", "Gameplay Mechanics")
        """
        if not self.llm_available:
            return f"Topic {topic_data['topic_id']}"
        
        try:
            # Prepare context from representative sentences
            sentences = topic_data.get('representative_sentences', [])[:3]
            samples = topic_data.get('sample_texts', [])[:5]
            sentiment = topic_data.get('sentiment_label', 'neutral')
            
            # Create prompt for topic naming
            prompt = f"""Based on these player feedback samples, provide a concise 2-3 word topic name:

Representative feedback:
{chr(10).join(f'- {s}' for s in sentences)}

Additional samples:
{chr(10).join(f'- {s}' for s in samples)}

Sentiment: {sentiment}

Topic name (2-3 words only, no explanation):"""
            
            # Generate response
            response, _ = self.model.chat(self.tokenizer, prompt, history=None)
            
            # Extract clean topic name (remove any extra explanation)
            topic_name = response.strip().split('\n')[0].strip()
            
            # Fallback if response is too long or invalid
            if len(topic_name) > 30 or len(topic_name.split()) > 4:
                topic_name = self._extract_keywords(sentences)
            
            return topic_name
            
        except Exception as e:
            print(f"⚠️ Error generating topic name: {e}")
            return f"Topic {topic_data['topic_id']}"
    
    def _extract_keywords(self, sentences: List[str]) -> str:
        """Fallback method to extract keywords if LLM fails"""
        # Simple keyword extraction based on frequency
        words = []
        for s in sentences[:3]:
            words.extend(s.split())
        
        # Filter common words and take most frequent
        from collections import Counter
        word_freq = Counter(words)
        # Remove very common words
        common_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'of', 'to', 'in', 'for'}
        filtered = {w: c for w, c in word_freq.items() if w.lower() not in common_words}
        
        if filtered:
            top_words = sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:2]
            return ' '.join(w[0].title() for w in top_words)
        
        return "General Feedback"
    
    def generate_topic_summary(self, topic_data: Dict, topic_name: str) -> str:
        """
        Generate a detailed summary for a topic using LLM
        
        Args:
            topic_data: Dictionary containing topic information
            topic_name: The generated topic name
            
        Returns:
            A detailed summary paragraph
        """
        if not self.llm_available:
            return self._generate_basic_summary(topic_data, topic_name)
        
        try:
            sentences = topic_data.get('representative_sentences', [])[:3]
            samples = topic_data.get('sample_texts', [])[:8]
            sentiment = topic_data.get('sentiment_label', 'neutral')
            density = topic_data.get('density', 0)
            
            prompt = f"""Analyze these player feedback samples about "{topic_name}" and provide a 2-3 sentence insight summary:

Key feedback:
{chr(10).join(f'- {s}' for s in sentences)}

Additional comments ({len(samples)} samples):
{chr(10).join(f'- {s}' for s in samples[:5])}

Sentiment: {sentiment}
Number of players mentioning this: {density}

Provide a concise insight summary (2-3 sentences):"""
            
            response, _ = self.model.chat(self.tokenizer, prompt, history=None)
            return response.strip()
            
        except Exception as e:
            print(f"⚠️ Error generating summary: {e}")
            return self._generate_basic_summary(topic_data, topic_name)
    
    def _generate_basic_summary(self, topic_data: Dict, topic_name: str) -> str:
        """Generate basic summary without LLM"""
        density = topic_data.get('density', 0)
        sentiment = topic_data.get('sentiment_label', 'neutral')
        score = topic_data.get('sentiment_score', 0)
        
        sentiment_desc = {
            'positive': 'positively',
            'negative': 'negatively',
            'neutral': 'neutrally'
        }
        
        return (f"{density} players discussed {topic_name}, expressing {sentiment_desc.get(sentiment, 'mixed')} "
                f"sentiment (score: {score:.2f}). This represents a significant theme in player feedback.")
    
    def generate_enhanced_report(self, nlp_result: Dict, include_charts: bool = True) -> Dict:
        """
        Generate an enhanced report with LLM-generated topic names and insights
        
        Args:
            nlp_result: The original NLP processing result
            include_charts: Whether to generate chart data
            
        Returns:
            Enhanced report dictionary with topic names, summaries, and chart data
        """
        enhanced_topics = []
        
        for topic in nlp_result.get('topics', []):
            # Generate topic name using LLM
            topic_name = self.generate_topic_name(topic)
            
            # Generate summary using LLM
            summary = self.generate_topic_summary(topic, topic_name)
            
            # Create enhanced topic entry
            enhanced_topic = {
                **topic,  # Keep all original data
                'topic_name': topic_name,
                'summary': summary
            }
            
            enhanced_topics.append(enhanced_topic)
        
        # Create enhanced report
        enhanced_report = {
            'statistics': nlp_result.get('statistics', {}),
            'topics': enhanced_topics,
            'llm_enhanced': self.llm_available
        }
        
        # Add chart data if requested
        if include_charts:
            enhanced_report['charts'] = self._generate_chart_data(enhanced_topics)
        
        return enhanced_report
    
    def _generate_chart_data(self, topics: List[Dict]) -> Dict:
        """Generate data for charts and visualizations"""
        
        # Sentiment distribution
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        for topic in topics:
            label = topic.get('sentiment_label', 'neutral').lower()
            sentiment_counts[label] = sentiment_counts.get(label, 0) + topic.get('density', 0)
        
        # Topic density chart (top topics)
        top_topics = sorted(topics, key=lambda x: x.get('density', 0), reverse=True)[:10]
        density_chart = {
            'labels': [t.get('topic_name', f"Topic {t['topic_id']}") for t in top_topics],
            'values': [t.get('density', 0) for t in top_topics]
        }
        
        # Sentiment score distribution
        sentiment_scores = [t.get('sentiment_score', 0) for t in topics]
        
        return {
            'sentiment_distribution': sentiment_counts,
            'top_topics_by_density': density_chart,
            'sentiment_score_stats': {
                'mean': float(np.mean(sentiment_scores)) if sentiment_scores else 0,
                'std': float(np.std(sentiment_scores)) if sentiment_scores else 0,
                'min': float(np.min(sentiment_scores)) if sentiment_scores else 0,
                'max': float(np.max(sentiment_scores)) if sentiment_scores else 0
            }
        }


# Standalone usage example
if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        'statistics': {'total': 1000, 'valid': 950},
        'topics': [
            {
                'topic_id': 1,
                'density': 179,
                'sentiment_score': 0.21,
                'sentiment_label': 'positive',
                'representative_sentences': ['Great art style', 'Beautiful graphics', 'Amazing visuals'],
                'sample_texts': ['Love the art', 'Graphics are stunning', 'Visual design is perfect']
            }
        ]
    }
    
    generator = LLMReportGenerator()
    enhanced = generator.generate_enhanced_report(sample_data)
    print(json.dumps(enhanced, indent=2, ensure_ascii=False))
