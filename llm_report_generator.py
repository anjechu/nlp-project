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

# Import stopwords from nlp module
try:
    from nlp import DataCleaner
    STOPWORDS_AVAILABLE = True
except ImportError:
    STOPWORDS_AVAILABLE = False
    print("⚠️ Warning: Could not import DataCleaner for stopwords")

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
        'Chinese': 'IMPORTANT: Generate the topic name in Chinese (中文). Use Chinese characters.',
        'Japanese': 'IMPORTANT: Generate the topic name in Japanese (日本語). Use Japanese characters.',
        'English': 'Generate the topic name in English. Use words.',
        'Korean': 'IMPORTANT: Generate the topic name in Korean (한국어). Use Korean characters.'
    }
    
    def __init__(self, model_path: Optional[str] = None, use_ollama: bool = False, ollama_model: str = "qwen2.5:7b"):
        """
        Initialize the LLM report generator
        
        Args:
            model_path: Path to local Qwen model via HuggingFace (if None, will try to auto-detect)
            use_ollama: If True, use Ollama API instead of loading model directly
            ollama_model: Ollama model name (default: "qwen2.5:7b")
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
        使用 LLM 生成有意义的英文主题名称。
        采用早返回机制确保翻译结果不被覆盖，并使用正则清洗非 ASCII 字符。
        """
        # 0. 保底：如果 LLM 不可用，直接返回数字编号
        if not self.llm_available:
            topic_id = topic_data.get('topic_id', 'Unknown')
            return f"Topic {topic_id}"
        
        topic_id = topic_data.get('topic_id', 'Unknown')

        try:
            # 准备上下文
            sentences = topic_data.get('representative_sentences', [])[:3]
            sample_texts = topic_data.get('sample_texts', [])[:5]
            sentiment = topic_data.get('sentiment_label', 'neutral')
            
            # Get stopword examples for prompt
            stopword_examples = ""
            if STOPWORDS_AVAILABLE and DataCleaner.STOP_PHRASES:
                # Get a few English stopword examples
                english_stops = [w for w in list(DataCleaner.STOP_PHRASES)[:20] 
                               if all(ord(c) < 128 for c in w)][:10]
                if english_stops:
                    stopword_examples = f"\n- AVOID generic words like: {', '.join(english_stops[:5])}"
            
            # 1. 构造 Prompt（保持你原有的高质量 Prompt + 添加停用词指示）
            prompt = f"""Analyze these player feedback samples and provide a SPECIFIC English topic name.

Game: {game_name if game_name else 'Unknown Game'}
Sentiment: {sentiment}

Representative feedback:
{chr(10).join(f'- {s}' for s in sentences)}

Additional samples:
{chr(10).join(f'- {s}' for s in sample_texts)}

IMPORTANT: 
- Provide ONLY a SPECIFIC English topic name (more than 3 words, less than 6 words, IMPORTANT!!!!).
- Only answer with topics names! Don't put any extra explanation or punctuation. （IMPORTATNT!!!!!!!) 
- ONLY GIVE ME THE TOPIC NAME, no need for any other text, including how you generated it.
- NO Chinese, NO Japanese, NO Korean - Use English only!
- Be SPECIFIC to the feedback content - NOT generic!
- FORBIDDEN generic names: "Player Feedback", "Game Feedback", "User Feedback", "General Feedback"{stopword_examples}

English topic name:"""

            # 2. 第一次查询 LLM
            response = self._query_llm(prompt, max_tokens=20)
            topic_name = response.strip().split('\n')[0].strip()
            
            # 基础清洗：去掉引号、数字前缀等
            topic_name = topic_name.strip('"\'•–—: ').strip('-').strip('0123456789. ')
            if ':' in topic_name and len(topic_name.split(':')[0]) < 10:
                topic_name = topic_name.split(':', 1)[1].strip()

            # 3. 核心判断：如果包含非拉丁字符（中日韩文），进行二次翻译
            if any(ord(c) > 127 for c in topic_name):
                print(f"⚠️ Non-English detected: {topic_name}, attempting translation...")
                try:
                    translation_prompt = f"Translate this topic name to concise English (2-3 words): {topic_name}"
                    translated_res = self._query_llm(translation_prompt, max_tokens=20).strip()
                    
                    # 【关键修复点】：正则清洗。
                    # 哪怕翻译结果里还带着括号或中文，我们也只取英文部分，不放弃！
                    topic_name = re.sub(r'[^\x00-\x7F]+', ' ', translated_res).strip()
                    topic_name = ' '.join(topic_name.split()) # 清理多余空格
                    
                    if len(topic_name) >= 2:
                        print(f"   → Successfully translated and cleaned: {topic_name}")
                        return topic_name # 翻译成功，立刻返回，防止被后续逻辑覆盖
                except Exception as trans_error:
                    print(f"   → Translation failed: {trans_error}")
            
            # 4. 泛化名称判定 (Generic Names Check)
            generic_names = {
                'player feedback', 'game feedback', 'user feedback', 'general feedback',
                'player opinion', 'game opinion', 'user opinion', 'general opinion',
                'game issues', 'general issues', 'positive feedback', 'negative feedback'
            }
            
            # 如果经过翻译清洗后，名字还是太短、还是有中文，或者是泛泛而谈的废话
            if len(topic_name) < 2 or any(ord(c) > 127 for c in topic_name) or topic_name.lower() in generic_names:
                print(f"⚠️ Topic name '{topic_name}' invalid or generic, using keyword extraction")
                topic_name = self._extract_keywords(sentences, topic_id=topic_id)
            
            # 5. 长度校验
            if len(topic_name) > self.MAX_TOPIC_NAME_LENGTH:
                topic_name = topic_name[:self.MAX_TOPIC_NAME_LENGTH].rsplit(' ', 1)[0]

            # 6. 最后的保险：如果返回的是 Topic + 数字，强行加一段原文内容提示，增加可读性
            if topic_name.startswith("Topic ") and sentences:
                # 提取第一句反馈中的纯字母部分
                hint = re.sub(r'[^\w\s]', '', sentences[0])[:12].strip()
                if hint:
                    return f"{topic_name} ({hint}...)"

            return topic_name

        except Exception as e:
            print(f"❌ Critical error in generate_topic_name: {e}")
            return f"Topic {topic_data.get('topic_id', 'Error')}"
    
    def _extract_keywords(self, sentences: List[str], topic_id: str = None) -> str:
        """
        Fallback method to extract keywords if LLM fails.
        Uses loaded stopwords from DataCleaner to filter out common words.
        
        Args:
            sentences: List of sentences to extract keywords from
            topic_id: Optional topic ID to use as final fallback
        """
        # Get stopwords from DataCleaner if available
        if STOPWORDS_AVAILABLE and DataCleaner.STOP_PHRASES:
            # Use loaded stopwords from stopWord.txt.txt
            stopwords = DataCleaner.STOP_PHRASES
            print(f"🔍 Using {len(stopwords)} stopwords from external file for keyword extraction")
        else:
            # Fallback to hardcoded common words
            stopwords = {
                'the', 'a', 'an', 'is', 'are', 'was', 'were', 'of', 'to', 'in', 'for', 'and', 'but', 
                'with', 'this', 'that', 'from', 'has', 'have', 'had', 'will', 'would', 'could', 'should',
                'can', 'may', 'might', 'must', 'its', 'it', 'be', 'been', 'being', 'not', 'no', 'yes',
                'so', 'as', 'at', 'by', 'on', 'or', 'if', 'than', 'then', 'when', 'where', 'why', 'how',
                'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
                'very', 'really', 'just', 'also', 'too', 'only', 'even', 'much', 'many', 'well',
                'get', 'got', 'make', 'made', 'like', 'good', 'bad', 'better', 'best', 'worst',
                'game', 'games', 'playing', 'played',
                'feedback', 'comment', 'review', 'opinion'
            }
            print(f"⚠️ Using fallback stopwords ({len(stopwords)} words)")
        
        # Extract words from sentences
        words = []
        for s in sentences[:5]:
            for word in s.split():
                # Clean punctuation
                word_clean = word.strip('.,!?;:()[]{}"\'-').lower()
                if len(word_clean) > 2:
                    words.append(word_clean)
        
        # Count word frequencies
        word_freq = Counter(words)
        
        # Filter out stopwords and get most frequent meaningful words
        filtered = {w: c for w, c in word_freq.items() 
                   if w not in stopwords and len(w) > 3}
        
        if filtered:
            # Get top 2 most frequent specific words
            top_words = sorted(filtered.items(), key=lambda x: x[1], reverse=True)[:2]
            keywords = ' '.join(w[0].title() for w in top_words)
            
            if len(keywords) > 4:
                print(f"   ✓ Extracted keywords (filtered by stopwords): {keywords}")
                return keywords
        
        # Second pass: Be more lenient with word length
        filtered_lenient = {w: c for w, c in word_freq.items() 
                           if w not in stopwords and len(w) > 2}
        
        if filtered_lenient:
            top_words = sorted(filtered_lenient.items(), key=lambda x: x[1], reverse=True)[:2]
            keywords = ' '.join(w[0].title() for w in top_words)
            if len(keywords) > 3:
                print(f"   ✓ Extracted keywords (lenient): {keywords}")
                return keywords
        
        # Third pass: Extract any words not in stopwords
        potential_topics = []
        for w in words:
            if w not in stopwords and len(w) > 3:
                potential_topics.append(w.title())
        
        if potential_topics:
            seen = set()
            unique_topics = []
            for topic in potential_topics:
                if topic.lower() not in seen and len(unique_topics) < 2:
                    unique_topics.append(topic)
                    seen.add(topic.lower())
            if unique_topics:
                result = ' '.join(unique_topics)
                print(f"   ✓ Extracted unique topics: {result}")
                return result
        
        # Fourth pass: Just get ANY words that aren't stopwords
        any_words = [w.title() for w in words if w not in stopwords][:2]
        if any_words:
            result = ' '.join(any_words)
            print(f"   ✓ Extracted any non-stopwords: {result}")
            return result
        
        # Last resort: use topic_id
        if topic_id:
            return f"Topic {topic_id}"
        return "Unlabeled Topic"
    
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
        Generate a comprehensive cross-cultural analysis across ALL valuable topics
        
        Important: This receives ALL LLM-filtered valuable topics and generates
        an in-depth, insightful analysis of cultural preference differences.
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
            
            # Organize topics by culture and sentiment for deep analysis
            culture_topics = {culture: {'positive': [], 'negative': [], 'neutral': []} 
                            for culture in cultural_summary.keys()}
            
            for topic in topics:
                topic_dist = topic.get('cultural_distribution', {})
                if not topic_dist:
                    continue
                
                # Find primary culture for this topic
                primary_lang = max(topic_dist.items(), key=lambda x: x[1])[0] if topic_dist else None
                if primary_lang:
                    primary_culture = self.LANG_MAP.get(primary_lang, primary_lang.capitalize())
                    if primary_culture in culture_topics:
                        sentiment = topic.get('sentiment_label', 'neutral').lower()
                        culture_topics[primary_culture][sentiment].append({
                            'name': topic.get('topic_name', 'Topic'),
                            'density': topic.get('density', 0),
                            'score': topic.get('sentiment_score', 0)
                        })
            
            # Sort topics by density within each category
            for culture in culture_topics:
                for sentiment in ['positive', 'negative', 'neutral']:
                    culture_topics[culture][sentiment].sort(key=lambda x: x['density'], reverse=True)
            
            # Format detailed topic breakdowns for each culture
            max_topics_per_sentiment = 8  # Show top 8 per sentiment category
            
            def format_culture_breakdown(culture_name):
                """Format comprehensive topic list for a culture"""
                culture_data = culture_topics[culture_name]
                sections = []
                
                for sentiment_type, sentiment_label in [('positive', 'LIKE'), ('negative', 'DISLIKE'), ('neutral', 'NEUTRAL')]:
                    topics_list = culture_data[sentiment_type][:max_topics_per_sentiment]
                    if topics_list:
                        topic_strs = [f"{t['name']} ({t['density']} mentions)" for t in topics_list]
                        sections.append(f"  {sentiment_label}: {', '.join(topic_strs[:5])}" + 
                                      (f" and {len(topics_list)-5} more" if len(topics_list) > 5 else ""))
                
                return chr(10).join(sections) if sections else "  No significant topics"
            
            # Build comprehensive prompt for deep cultural analysis
            culture_breakdowns = []
            for culture in sorted(cultural_summary.keys()):
                breakdown = f"{culture} Players ({cultural_summary[culture]} total):\n{format_culture_breakdown(culture)}"
                culture_breakdowns.append(breakdown)
            
            prompt = f"""Based on analysis of {len(topics)} valuable player feedback topics across different cultures, provide a COMPREHENSIVE, INSIGHTFUL paragraph (6-8 sentences minimum) analyzing crucial cultural preference differences.

Player Distribution & Topic Preferences:
{chr(10).join(culture_breakdowns)}

Your analysis MUST:
1. Identify 3-4 SPECIFIC examples of divergent preferences between cultures (e.g., Chinese players prioritize X while Japanese players prefer Y)
2. Explain WHY these differences exist based on cultural gaming values and expectations
3. Highlight any surprising or counterintuitive findings
4. Provide ACTIONABLE insights for developers on how to address each culture's priorities
5. Discuss which features are universally valued vs. culturally specific
6. Mention potential localization strategies that could improve satisfaction for each market

Write a detailed, analytical paragraph that developers can use to make crucial decisions. Be specific, cite topics by name, and provide genuine cultural insights beyond surface observations.

Comprehensive Cultural Analysis:"""
            
            response = self._query_llm(prompt, max_tokens=500)
            return response.strip()
            
        except Exception as e:
            print(f"⚠️ Error generating cultural summary: {e}")
            return "Unable to generate cultural summary."
    
    def _generate_chart_data(self, topics: List[Dict]) -> Dict:
        """
        Generate data for charts and visualizations
        
        Important: This receives ONLY the LLM-filtered valuable topics.
        Uses English names for consistency across all charts.
        """
        
        # Sentiment distribution (uses all topics)
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        for topic in topics:
            label = topic.get('sentiment_label', 'neutral').lower()
            sentiment_counts[label] = sentiment_counts.get(label, 0) + topic.get('density', 0)
        
        # Topic density chart - limit to top 15 for readability
        # Use English names for consistency
        sorted_topics = sorted(topics, key=lambda x: x.get('density', 0), reverse=True)
        top_15_topics = sorted_topics[:15]  # Show only top 15 topics
        density_chart = {
            'labels': [t.get('topic_name', f"Topic {t['topic_id']}") for t in top_15_topics],
            'values': [t.get('density', 0) for t in top_15_topics]
        }
        
        # Sentiment score distribution (uses all topics for statistical accuracy)
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
        # 添加这行，看看进入 Reduce 阶段前数据对不对
        for r in map_results:
            for t in r.get('topics', []):
                print(f"DEBUG: Map Result Topic Name: {t.get('topic_name')}")
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
        
        # Generate chart data from aggregated topics
        charts_data = self._generate_chart_data(all_topics)
        
        print(f"📊 REDUCE COMPLETE:")
        print(f"   • Total valuable topics: {len(all_topics)}")
        print(f"   • Games: {', '.join(all_stats['games_processed'])}")
        print(f"   • Languages: {', '.join(all_stats['languages_processed'])}")
        print(f"   • Charts data generated: {list(charts_data.keys())}")
        
        return {
            'topics': all_topics,
            'statistics': all_stats,
            'charts': charts_data,  # Add charts field for chart generation
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
