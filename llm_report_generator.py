"""
LLM-Enhanced Report Generator
Integrates Qwen local LLM (via Ollama or HuggingFace) to generate enhanced insights with cross-cultural analysis
"""

import json
import os
import re
from typing import Dict, List, Optional
from collections import Counter
import numpy as np

class LLMReportGenerator:
    """Generates enhanced reports using local LLM (Qwen) for topic naming and cross-cultural insights"""
    
    # Language code mapping (used across the class)
    LANG_MAP = {
        'schinese': 'Chinese',
        'tchinese': 'Chinese',
        'japanese': 'Japanese',
        'english': 'English',
        'korean': 'Korean',
        'koreana': 'Korean'
    }
    
    # Topic naming configuration
    MAX_TOPIC_NAME_LENGTH = 50  # Maximum length for generated topic names
    
    # Language-specific instructions for topic naming
    LANGUAGE_INSTRUCTIONS = {
        'Chinese': 'IMPORTANT: Generate the topic name in Chinese (中文). Use 2-4 Chinese characters.',
        'Japanese': 'IMPORTANT: Generate the topic name in Japanese (日本語). Use 2-6 Japanese characters.',
        'English': 'Generate the topic name in English. Use 2-3 words.',
        'Korean': 'IMPORTANT: Generate the topic name in Korean (한국어). Use 2-5 Korean characters.'
    }
    
    def __init__(self, model_path: Optional[str] = None, use_ollama: bool = False, ollama_model: str = "qwen:7b"):
        """
        Initialize the LLM report generator
        
        Args:
            model_path: Path to local Qwen model via HuggingFace (if None, will try to auto-detect)
            use_ollama: If True, use Ollama API instead of loading model directly
            ollama_model: Ollama model name (default: "qwen:7b")
        """
        self.model_path = model_path
        self.use_ollama = use_ollama
        self.ollama_model = ollama_model
        self.llm_available = False
        self.model = None
        self.tokenizer = None
        self._init_llm()
    
    def _init_llm(self):
        """Initialize the Qwen LLM model (via Ollama or HuggingFace)"""
        if self.use_ollama:
            try:
                import requests
                # Test Ollama connection
                response = requests.get('http://localhost:11434/api/tags', timeout=2)
                if response.status_code == 200:
                    self.llm_available = True
                    print(f"✅ Connected to Ollama with model: {self.ollama_model}")
                else:
                    raise Exception("Ollama not responding")
            except Exception as e:
                print(f"⚠️ Ollama not available: {e}")
                print("📝 Make sure Ollama is running: ollama serve")
                print(f"📝 And model is pulled: ollama pull {self.ollama_model}")
                self.llm_available = False
        else:
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
    
    def _query_ollama(self, prompt: str, max_tokens: int = 100) -> str:
        """Query Ollama API"""
        import requests
        
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': self.ollama_model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'num_predict': max_tokens
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                return ""
        except Exception as e:
            print(f"⚠️ Ollama query failed: {e}")
            return ""
    
    def _query_llm(self, prompt: str, max_tokens: int = 100) -> str:
        """Query LLM (Ollama or HuggingFace)"""
        try:
            if self.use_ollama:
                return self._query_ollama(prompt, max_tokens)
            else:
                # HuggingFace transformers
                inputs = self.tokenizer(prompt, return_tensors="pt")
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_new_tokens=max_tokens,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id
                )
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                # Extract the response part (after the prompt)
                return response[len(prompt):].strip()
        except Exception as e:
            print(f"⚠️ LLM query failed: {e}")
            return ""
    
    def generate_topic_name(self, topic_data: Dict, game_name: str = None, language: str = None) -> str:
        """
        Generate a meaningful English topic name using LLM.
        
        Simplified approach: Generate only English names for consistency and performance.
        All report content uses English except for sample comments.
        
        Args:
            topic_data: Dictionary containing topic information
            game_name: Optional game name for context
            language: Optional language context (for understanding samples)
            
        Returns:
            A concise English topic name (2-3 words)
        """
        if not self.llm_available:
            topic_id = topic_data.get('topic_id', 'Unknown')
            return f"Topic {topic_id}"
        
        try:
            # Prepare context from representative sentences
            sentences = topic_data.get('representative_sentences', [])[:3]
            sample_texts = topic_data.get('sample_texts', [])[:5]
            sentiment = topic_data.get('sentiment_label', 'neutral')
            
            # Create prompt for English topic naming only
            prompt = f"""Analyze these player feedback samples and provide a concise English topic name.

Game: {game_name if game_name else 'Unknown Game'}
Sentiment: {sentiment}

Representative feedback:
{chr(10).join(f'- {s}' for s in sentences)}

Additional samples:
{chr(10).join(f'- {s}' for s in sample_texts)}

IMPORTANT: Provide ONLY an English topic name (2-3 words). NO Chinese, NO Japanese, NO Korean. Use English only!
Examples: "Art Style", "Gameplay Balance", "Audio Quality"

English topic name:"""
            
            # Query LLM
            response = self._query_llm(prompt, max_tokens=20)
            
            # Extract clean topic name
            topic_name = response.strip().split('\n')[0].strip()
            
            # Remove common unwanted prefixes/suffixes
            topic_name = topic_name.strip('"\'•–—: ').strip('-').strip('0123456789. ')
            
            # Remove "Line 1:" or similar artifacts
            if ':' in topic_name and len(topic_name.split(':')[0]) < 10:
                topic_name = topic_name.split(':', 1)[1].strip()
            
            # Check if it's actually English (basic check for non-Latin characters)
            if any(ord(c) > 127 for c in topic_name):
                # Contains non-Latin characters, use fallback
                print(f"⚠️ Non-English topic name detected: {topic_name}, using fallback")
                topic_name = self._extract_keywords(sentences)
            
            # Fallback if response is too long or invalid
            if len(topic_name) > self.MAX_TOPIC_NAME_LENGTH or len(topic_name) < 2:
                topic_name = self._extract_keywords(sentences)
            
            return topic_name
            
        except Exception as e:
            print(f"⚠️ Error generating topic name: {e}")
            topic_id = topic_data.get('topic_id', 'Unknown')
            return f"Topic {topic_id}"
    
    def _extract_keywords(self, sentences: List[str]) -> str:
        """
        Fallback method to extract English keywords if LLM fails.
        Only uses Latin characters to ensure English output.
        """
        # Simple keyword extraction based on frequency
        words = []
        for s in sentences[:3]:
            # Split and filter to only include words with Latin characters
            for word in s.split():
                # Only keep words that are mostly Latin characters (English)
                latin_chars = sum(1 for c in word if ord(c) < 128)
                if latin_chars > len(word) * 0.8 and len(word) > 2:  # 80% Latin chars and length > 2
                    words.append(word)
        
        # Filter common words and take most frequent
        word_freq = Counter(words)
        # Remove very common words
        common_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'of', 'to', 'in', 'for', 'and', 'but', 'with', 'this', 'that', 'from'}
        filtered = {w: c for w, c in word_freq.items() if w.lower() not in common_words and len(w) > 2}
        
        if filtered:
            top_words = sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:2]
            return ' '.join(w[0].title() for w in top_words)
        
        # Ultimate fallback - return generic English name
        return "Player Feedback"
    
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
            
            # Query LLM
            response = self._query_llm(prompt, max_tokens=150)
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
    
    def analyze_cross_cultural_preferences(self, topic_data: Dict, topic_name: str) -> Dict:
        """
        Analyze cross-cultural preferences for a topic
        
        Args:
            topic_data: Dictionary containing topic information
            topic_name: The generated topic name
            
        Returns:
            Dictionary with cultural analysis (likes, dislikes per culture)
        """
        cultural_dist = topic_data.get('cultural_distribution', {})
        
        # Basic analysis without LLM
        analysis = {
            'distribution': {self.LANG_MAP.get(lang, lang.capitalize()): count 
                           for lang, count in cultural_dist.items()},
            'dominant_culture': None,
            'cultural_insights': {}
        }
        
        if cultural_dist:
            dominant_lang = max(cultural_dist.items(), key=lambda x: x[1])[0]
            analysis['dominant_culture'] = self.LANG_MAP.get(dominant_lang, dominant_lang.capitalize())
        
        # If LLM available, generate deeper insights
        if self.llm_available and len(cultural_dist) > 1:
            try:
                # Get sentiment by culture
                sentiment = topic_data.get('sentiment_label', 'neutral')
                score = topic_data.get('sentiment_score', 0)
                samples = topic_data.get('sample_texts', [])[:10]
                
                prompt = f"""Analyze this game feedback topic "{topic_name}" from a cross-cultural perspective:

Cultural Distribution:
{chr(10).join(f'- {self.LANG_MAP.get(lang, lang)}: {count} players' for lang, count in cultural_dist.items())}

Sample Feedback (mixed languages):
{chr(10).join(f'- {s}' for s in samples[:5])}

Overall Sentiment: {sentiment} ({score:.2f})

Provide brief insights (2-3 sentences) on:
1. What aspects do different cultural groups particularly appreciate or dislike?
2. Are there any notable cultural differences in how this topic is perceived?

Answer:"""
                
                response = self._query_llm(prompt, max_tokens=200)
                analysis['llm_insight'] = response.strip()
                
            except Exception as e:
                print(f"⚠️ Error in cultural analysis: {e}")
        
        return analysis
    
    def filter_valuable_topics(self, topics: List[Dict]) -> List[Dict]:
        """
        Use LLM to intelligently filter out low-value/spam topics, keeping all valuable ones
        
        Args:
            topics: List of all topics from NLP analysis
            
        Returns:
            List of valuable topics (no hardcoded limit)
        """
        if not self.llm_available or len(topics) <= 3:
            # Without LLM or for small topic lists, use density-based filtering
            # Keep topics with density > 5 players or top 80% by density
            sorted_topics = sorted(topics, key=lambda x: x.get('density', 0), reverse=True)
            threshold = max(5, sorted_topics[int(len(sorted_topics) * 0.2)].get('density', 0) if sorted_topics else 5)
            return [t for t in topics if t.get('density', 0) >= threshold]
        
        try:
            # Prepare topic summaries for LLM evaluation
            topic_info = []
            for i, topic in enumerate(topics):
                sentences = topic.get('representative_sentences', [])[:2]
                density = topic.get('density', 0)
                sentiment = topic.get('sentiment_label', 'neutral')
                
                topic_info.append(f"""Topic {i+1}:
- Players: {density}
- Sentiment: {sentiment}
- Sample: {sentences[0] if sentences else 'N/A'}""")
            
            prompt = f"""You are evaluating {len(topics)} game feedback topics. Identify VALUABLE topics that provide ACTIONABLE INSIGHTS for game developers.

STRICT CRITERIA FOR VALUABLE TOPICS:
✅ KEEP if topic discusses:
  • Specific gameplay mechanics, features, or systems (POSITIVE OR NEGATIVE)
  • Graphics quality, art style, visual elements (POSITIVE OR NEGATIVE)
  • Music, sound design, audio quality (POSITIVE OR NEGATIVE)
  • Story, narrative, characters, dialogue (POSITIVE OR NEGATIVE)
  • Bugs, technical issues, performance problems
  • Game balance, difficulty, progression
  • UI/UX issues or praise
  • Specific game content (levels, missions, items)
  • Multiplayer functionality, matchmaking
  • Monetization, pricing, DLC value

⚠️ CRITICAL: Positive feedback regarding specific mechanics/art/features IS VALUABLE!
   - "Beautiful graphics" with specific mentions → KEEP
   - "Great gameplay mechanics" with examples → KEEP
   - "Love the art style" with details → KEEP
   Developers need to know what players LIKE to preserve those elements.

❌ REJECT ONLY if topic is:
  • Generic praise without substance ("great game", "love it", "amazing")
  • Generic complaints without specifics ("bad game", "boring", "terrible")
  • Off-topic content (unrelated to game)
  • Spam, memes, or nonsense
  • Pure emotion without actionable feedback (just "wow", "lol", "wtf")
  • Vague statements with no development value

GOAL: Help developers understand BOTH what to improve AND what to preserve in their games. Include topics that provide CLEAR, ACTIONABLE insights about specific game aspects.

{chr(10).join(topic_info)}

List ONLY the numbers of VALUABLE topics (comma-separated, e.g., "1,3,5,7,8,10"):"""
            
            response = self._query_llm(prompt, max_tokens=100)
            
            # Parse response to extract topic indices
            numbers = re.findall(r'\d+', response)
            valuable_indices = {int(n) - 1 for n in numbers if n.isdigit() and 0 < int(n) <= len(topics)}
            
            if valuable_indices:
                filtered = [topics[i] for i in sorted(valuable_indices) if i < len(topics)]
                print(f"✅ LLM filtered {len(topics)} topics → {len(filtered)} valuable topics")
                return filtered
            else:
                # Fallback if parsing fails
                print("⚠️ LLM filtering failed, using density-based filtering")
                return self._filter_by_density(topics)
                
        except Exception as e:
            print(f"⚠️ LLM filtering error: {e}, using fallback")
            return self._filter_by_density(topics)
    
    def _filter_by_density(self, topics: List[Dict]) -> List[Dict]:
        """Fallback: Filter topics by density (keep top 80% or min 5 players)"""
        sorted_topics = sorted(topics, key=lambda x: x.get('density', 0), reverse=True)
        threshold = max(5, sorted_topics[int(len(sorted_topics) * 0.2)].get('density', 0) if len(sorted_topics) > 5 else 5)
        filtered = [t for t in topics if t.get('density', 0) >= threshold]
        print(f"📊 Density-based filtering: {len(topics)} topics → {len(filtered)} topics (threshold: {threshold} players)")
        return filtered

    def generate_enhanced_report(self, nlp_result: Dict, game_name: str = None, language: str = None, include_charts: bool = True, include_cultural_analysis: bool = True) -> Dict:
        """
        Generate an enhanced report with LLM-generated English topic names and insights
        
        Simplified approach: All content in English for consistency and performance.
        
        Args:
            nlp_result: The original NLP processing result
            game_name: Optional game name for context in topic naming
            language: Optional language for this specific report (for Map phase)
            include_charts: Whether to generate chart data
            include_cultural_analysis: Whether to include cross-cultural analysis
            
        Returns:
            Enhanced report dictionary with English topic names, summaries, and cultural insights
        """
        # Step 1: Filter topics using LLM (removes hardcoded 5-topic limit)
        all_topics = nlp_result.get('topics', [])
        valuable_topics = self.filter_valuable_topics(all_topics)
        
        print(f"📝 Processing {len(valuable_topics)} valuable topics (from {len(all_topics)} total)")
        
        enhanced_topics = []
        
        for topic in valuable_topics:
            # Generate English topic name using LLM
            topic_name = self.generate_topic_name(topic, game_name=game_name, language=language)
            
            # Generate summary using LLM
            summary = self.generate_topic_summary(topic, topic_name)
            
            # Create enhanced topic entry
            enhanced_topic = {
                **topic,  # Keep all original data
                'topic_name': topic_name,  # English name
                'summary': summary
            }
            
            # Add cross-cultural analysis if requested
            if include_cultural_analysis:
                cultural_analysis = self.analyze_cross_cultural_preferences(topic, topic_name)
                enhanced_topic['cultural_analysis'] = cultural_analysis
            
            enhanced_topics.append(enhanced_topic)
        
        # Create enhanced report
        enhanced_report = {
            'statistics': nlp_result.get('statistics', {}),
            'topics': enhanced_topics,
            'llm_enhanced': self.llm_available,
            'cross_cultural': include_cultural_analysis,
            'total_topics_analyzed': len(all_topics),
            'valuable_topics_count': len(valuable_topics),
            'game_name': game_name,  # Add game context
            'language': language  # Add language context
        }
        
        # Add chart data if requested
        if include_charts:
            enhanced_report['charts'] = self._generate_chart_data(enhanced_topics)
        
        # Add overall cross-cultural summary if requested
        if include_cultural_analysis and self.llm_available:
            enhanced_report['cultural_summary'] = self._generate_cultural_summary(enhanced_topics)
        
        return enhanced_report
    
    def _generate_cultural_summary(self, topics: List[Dict]) -> str:
        """
        Generate an overall cross-cultural summary across ALL valuable topics
        
        Important: This receives ALL LLM-filtered valuable topics and uses them all
        to generate the summary, not just a subset.
        """
        if not self.llm_available:
            return "Cross-cultural analysis requires LLM support."
        
        try:
            # Aggregate cultural data from ALL topics
            all_cultures = {}
            for topic in topics:
                dist = topic.get('cultural_distribution', {})
                for lang, count in dist.items():
                    all_cultures[lang] = all_cultures.get(lang, 0) + count
            
            # Map to readable names using class constant
            cultural_summary = {self.LANG_MAP.get(lang, lang.capitalize()): count 
                              for lang, count in all_cultures.items()}
            
            # Categorize ALL topics by sentiment for comprehensive analysis
            sorted_topics = sorted(topics, key=lambda x: x.get('sentiment_score', 0), reverse=True)
            positive_topics = [t for t in sorted_topics if t.get('sentiment_score', 0) > 0]
            negative_topics = [t for t in sorted_topics if t.get('sentiment_score', 0) < 0]
            neutral_topics = [t for t in sorted_topics if t.get('sentiment_score', 0) == 0]
            
            # Handle large datasets: limit prompt size to prevent token overflow
            # If too many topics, show top/bottom topics with count summary
            max_topics_per_category = 15
            
            def format_topic_list(topic_list, max_count):
                """Format topic list with truncation if needed"""
                if len(topic_list) <= max_count:
                    return chr(10).join([f"  • {t.get('topic_name', 'Topic')} ({t.get('density', 0)} players)" 
                                        for t in topic_list])
                else:
                    shown = topic_list[:max_count]
                    remaining = len(topic_list) - max_count
                    result = chr(10).join([f"  • {t.get('topic_name', 'Topic')} ({t.get('density', 0)} players)" 
                                          for t in shown])
                    result += f"\n  • ... and {remaining} more topics"
                    return result
            
            prompt = f"""Provide a cross-cultural analysis summary for this game feedback.

Player Distribution:
{chr(10).join(f'- {culture}: {count} players' for culture, count in cultural_summary.items())}

Total {len(topics)} Valuable Topics Analyzed:

Positive Topics ({len(positive_topics)}):
{format_topic_list(positive_topics, max_topics_per_category)}

Negative Topics ({len(negative_topics)}):
{format_topic_list(negative_topics, max_topics_per_category)}

Neutral Topics ({len(neutral_topics)}):
{format_topic_list(neutral_topics, max_topics_per_category)}

Provide a comprehensive 3-4 sentence summary considering all {len(topics)} topics, highlighting:
1. Key differences in preferences between Chinese, Japanese, and English-speaking players
2. Common themes across all cultures
3. Notable cultural insights for developers

Summary:"""
            
            response = self._query_llm(prompt, max_tokens=300)
            return response.strip()
            
        except Exception as e:
            print(f"⚠️ Error generating cultural summary: {e}")
            return "Unable to generate cultural summary."
    
    def _generate_chart_data(self, topics: List[Dict]) -> Dict:
        """
        Generate data for charts and visualizations
        
        Important: This receives ONLY the LLM-filtered valuable topics.
        We show ALL of them without further limiting.
        Uses English names for consistency across all charts.
        """
        
        # Sentiment distribution
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        for topic in topics:
            label = topic.get('sentiment_label', 'neutral').lower()
            sentiment_counts[label] = sentiment_counts.get(label, 0) + topic.get('density', 0)
        
        # Topic density chart (ALL valuable topics, not limited)
        # LLM has already filtered to keep only valuable topics, so show all of them
        # Use English names for consistency
        sorted_topics = sorted(topics, key=lambda x: x.get('density', 0), reverse=True)
        density_chart = {
            'labels': [t.get('topic_name', f"Topic {t['topic_id']}") for t in sorted_topics],
            'values': [t.get('density', 0) for t in sorted_topics]
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
    
    def process_game_language_independently(self, nlp_result: Dict, game_name: str, language: str) -> Dict:
        """
        MAP PHASE: Process a single [game + language] combination independently.
        
        This is Phase 1 of the Map-Reduce architecture. By processing each combination
        separately, we prevent LLM context overflow that was causing Chinese players'
        positive topics to be forgotten.
        
        Args:
            nlp_result: NLP analysis result for a single game+language combination
            game_name: Name of the game (e.g., "bf6", "silksong")
            language: Language of the reviews (e.g., "chinese", "japanese", "english")
            
        Returns:
            Enhanced report with dual-language names and summaries for this specific combination
        """
        print(f"\n{'='*80}")
        print(f"🔍 MAP PHASE: Processing [{game_name}] + [{language}] independently")
        print(f"{'='*80}")
        
        # Set language context for this specific combination
        language_display = self.LANG_MAP.get(language.lower(), language.capitalize())
        
        print(f"📊 Input: {len(nlp_result.get('topics', []))} topics from {game_name} ({language_display})")
        
        # Process with language context to ensure proper naming
        enhanced = self.generate_enhanced_report(
            nlp_result, 
            game_name=game_name, 
            language=language_display,
            include_charts=False,  # Charts generated later in REDUCE phase
            include_cultural_analysis=False  # Cross-cultural done in REDUCE phase
        )
        
        # Add metadata for tracking
        enhanced['map_metadata'] = {
            'game_name': game_name,
            'language': language,
            'processed_independently': True,
            'original_topic_count': len(nlp_result.get('topics', [])),
            'valuable_topic_count': len(enhanced.get('topics', []))
        }
        
        print(f"✅ MAP COMPLETE: {len(enhanced.get('topics', []))} valuable topics extracted")
        print(f"   (Filtered from {len(nlp_result.get('topics', []))} original topics)")
        
        return enhanced
    
    def aggregate_map_results(self, map_results: List[Dict]) -> Dict:
        """
        REDUCE PHASE: Aggregate independently processed [game + language] results.
        
        This is Phase 2 of the Map-Reduce architecture. Takes the cleaned, 
        LLM-enhanced results from each combination and merges them intelligently.
        
        Args:
            map_results: List of enhanced reports from MAP phase
            
        Returns:
            Single aggregated report with all valuable topics
        """
        print(f"\n{'='*80}")
        print(f"🔄 REDUCE PHASE: Aggregating {len(map_results)} independently processed results")
        print(f"{'='*80}")
        
        # Collect all valuable topics with their metadata
        all_topics = []
        all_stats = {
            'total_comments': 0,
            'total_valid': 0,
            'games_processed': set(),
            'languages_processed': set()
        }
        
        topic_id_counter = 1
        
        for result in map_results:
            metadata = result.get('map_metadata', {})
            game = metadata.get('game_name', 'Unknown')
            lang = metadata.get('language', 'unknown')
            
            all_stats['games_processed'].add(game)
            all_stats['languages_processed'].add(lang)
            
            # Add topics with source tracking
            for topic in result.get('topics', []):
                aggregated_topic = {
                    **topic,
                    'topic_id': topic_id_counter,
                    'source_game': game,
                    'source_language': lang
                }
                all_topics.append(aggregated_topic)
                topic_id_counter += 1
            
            # Aggregate statistics
            stats = result.get('statistics', {})
            all_stats['total_comments'] += stats.get('total', 0)
            all_stats['total_valid'] += stats.get('valid', 0)
        
        # Convert sets to lists for JSON serialization
        all_stats['games_processed'] = list(all_stats['games_processed'])
        all_stats['languages_processed'] = list(all_stats['languages_processed'])
        
        print(f"📊 REDUCE COMPLETE:")
        print(f"   • Total valuable topics: {len(all_topics)}")
        print(f"   • Games: {', '.join(all_stats['games_processed'])}")
        print(f"   • Languages: {', '.join(all_stats['languages_processed'])}")
        
        return {
            'topics': all_topics,
            'statistics': all_stats,
            'llm_enhanced': True,
            'map_reduce_processed': True,
            'total_valuable_topics': len(all_topics)
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
