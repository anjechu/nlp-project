"""
NLP Processing Module
Provides sentiment analysis and text processing for user comments.
"""

import json
from typing import Dict, List, Any
import re


class NLPProcessor:
    """
    A simple NLP processor for analyzing user comments.
    Uses basic sentiment analysis without requiring heavy dependencies.
    """
    
    def __init__(self):
        """Initialize the NLP processor."""
        # Basic sentiment word lists
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'best', 'perfect', 'awesome', 'happy', 'liked', 'enjoyed',
            'beautiful', 'brilliant', 'outstanding', 'superb', 'nice', 'glad'
        }
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'poor', 'hate',
            'disappointing', 'disappointed', 'sad', 'angry', 'frustrated',
            'useless', 'waste', 'annoying', 'boring', 'dislike', 'ugly'
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of the text.
        Returns a dictionary with sentiment score and label.
        """
        cleaned_text = self.clean_text(text)
        words = cleaned_text.split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Calculate sentiment score (-1 to 1)
        total_sentiment_words = positive_count + negative_count
        # Handle case where no sentiment words are found
        if total_sentiment_words == 0:
            sentiment_score = 0.0
        else:
            # Safe division - denominator is guaranteed to be non-zero
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
        
        # Determine sentiment label
        if sentiment_score > 0.2:
            sentiment_label = 'positive'
        elif sentiment_score < -0.2:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'sentiment_score': round(sentiment_score, 2),
            'sentiment_label': sentiment_label,
            'positive_words_count': positive_count,
            'negative_words_count': negative_count,
            'word_count': len(words)
        }
    
    def process_comment(self, comment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single comment.
        Expects a dictionary with at least a 'text' or 'comment' field.
        """
        # Extract text from comment
        text = comment.get('text') or comment.get('comment') or comment.get('content', '')
        
        if not text:
            raise ValueError("Comment must contain 'text', 'comment', or 'content' field")
        
        # Analyze sentiment
        sentiment_analysis = self.analyze_sentiment(text)
        
        # Create processed comment
        processed_comment = {
            'original_text': text,
            'cleaned_text': self.clean_text(text),
            **sentiment_analysis
        }
        
        # Preserve original fields
        for key, value in comment.items():
            if key not in ['text', 'comment', 'content']:
                processed_comment[key] = value
        
        return processed_comment
    
    def process_comments(self, comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a list of comments.
        Returns a list of processed comments with sentiment analysis.
        """
        processed_comments = []
        
        for i, comment in enumerate(comments):
            try:
                processed = self.process_comment(comment)
                processed['index'] = i
                processed_comments.append(processed)
            except Exception as e:
                # Add error information but continue processing
                processed_comments.append({
                    'index': i,
                    'error': str(e),
                    'original_comment': comment
                })
        
        return processed_comments
    
    def process_file(self, input_path: str, output_path: str, progress_callback=None) -> Dict[str, Any]:
        """
        Process a JSON file containing comments.
        
        Args:
            input_path: Path to input JSON file
            output_path: Path to save output JSON file
            progress_callback: Optional callback function for progress updates
        
        Returns:
            Dictionary with processing statistics
        """
        # Read input file
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {e}")
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")
        
        # Extract comments from data
        if isinstance(data, list):
            comments = data
        elif isinstance(data, dict) and 'comments' in data:
            comments = data['comments']
        else:
            raise ValueError("JSON must be a list or contain a 'comments' key")
        
        if not comments:
            raise ValueError("No comments found in file")
        
        # Process comments with progress updates
        total = len(comments)
        processed_comments = []
        
        for i, comment in enumerate(comments):
            try:
                processed = self.process_comment(comment)
                processed['index'] = i
                processed_comments.append(processed)
            except Exception as e:
                processed_comments.append({
                    'index': i,
                    'error': str(e),
                    'original_comment': comment
                })
            
            # Update progress
            if progress_callback:
                progress_callback(i + 1, total)
        
        # Calculate statistics
        successful = sum(1 for c in processed_comments if 'error' not in c)
        errors = total - successful
        
        # Count sentiment distribution
        sentiment_distribution = {
            'positive': sum(1 for c in processed_comments if c.get('sentiment_label') == 'positive'),
            'negative': sum(1 for c in processed_comments if c.get('sentiment_label') == 'negative'),
            'neutral': sum(1 for c in processed_comments if c.get('sentiment_label') == 'neutral')
        }
        
        # Prepare output data
        output_data = {
            'statistics': {
                'total_comments': total,
                'successful': successful,
                'errors': errors,
                'sentiment_distribution': sentiment_distribution
            },
            'processed_comments': processed_comments
        }
        
        # Save output file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Error writing output file: {e}")
        
        return output_data['statistics']


if __name__ == '__main__':
    # Example usage
    processor = NLPProcessor()
    
    # Test with sample data
    sample_comments = [
        {'text': 'This is a great product! I love it!'},
        {'text': 'Terrible experience. Very disappointed.'},
        {'text': 'It is okay, nothing special.'}
    ]
    
    results = processor.process_comments(sample_comments)
    for result in results:
        print(f"Text: {result['original_text']}")
        print(f"Sentiment: {result['sentiment_label']} ({result['sentiment_score']})")
        print()
