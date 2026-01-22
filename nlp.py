"""
NLP Processing Module
Advanced sentiment analysis and text processing with GPU acceleration.
Integrates transformer models, clustering, and topic modeling.
"""

import re
import json
import numpy as np
import pandas as pd
import hdbscan
import torch
import os
from typing import Dict, List, Any

from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA 
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm


# ==========================================
# 0. 硬件环境检测
# ==========================================
def get_device():
    try:
        import torch_directml
        device = torch_directml.device()
        print(f"🚀 成功激活 AMD GPU 加速: {torch_directml.device_name(0)}")
        return device
    except ImportError:
        pass
    if torch.cuda.is_available():
        print("🚀 成功激活 NVIDIA GPU (CUDA)")
        return torch.device("cuda")
    print("🐢 未检测到 GPU，使用 CPU。")
    return torch.device("cpu")

GPU_DEVICE = get_device()


# ==========================================
# 1. 数据清洗模块 (指纹去重版 V5)
# ==========================================
class DataCleaner:
    @staticmethod
    def get_fingerprint(text):
        """生成文本指纹：转小写 + 移除所有标点符号 + 移除空格"""
        # 仅保留汉字、字母、数字
        fingerprint = re.sub(r'[^\w\u4e00-\u9fa5]', '', text)
        return fingerprint.lower()

    @staticmethod
    def clean_text(text):
        if not text: return None
        
        # 1. 基础清理
        text = re.sub(r'\[\/?[a-zA-r0-9*=\s]+\]', '', text) # Steam BBCode
        text = re.sub(r'http\S+', '', text) # URL
        text = re.sub(r'[\u2800-\u28FF]+', '', text) # 盲文画
        
        # 2. 核心清洗：日期与元数据猎杀
        text = re.sub(r'^(编辑于|发布于|更新于|追评).*', '', text)
        text = re.sub(r'.*(更新|追评)$', '', text)
        # 移除各类日期格式
        text = re.sub(r'(\d{2,4}\s?年)?\s?\d{1,2}\s?月\s?\d{1,2}\s?日?', '', text)
        text = re.sub(r'\d{2,4}[./-]\d{1,2}[./-]\d{1,2}', '', text)
        # 移除"说说缺点"等废话
        text = re.sub(r'^(接下来|再来|这里|首先|最后)?(说|谈|讲)(说|谈|讲)?(优|缺)点.*$', '', text)
        text = re.sub(r'^(优|缺)点[:：]', '', text)
        # 移除分割线
        text = re.sub(r'[=\-—_]{3,}', '', text)
        
        # 3. 收尾
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 4. 严格过滤
        if len(text) < 5: return None # 太短的不要
        # 必须包含中文或字母
        if not re.search(r'[\u4e00-\u9fa5a-zA-Z]', text): return None
            
        return text

    @staticmethod
    def split_to_statements(reviews, progress_callback=None):
        pool = []
        # ⚠️ 关键修改：使用指纹集合来去重，而不是原文本集合
        seen_fingerprints = set()
        
        split_pattern = r'[。！!？?\n|；;：:]'
        
        print("🧹 正在清洗与拆分数据 (指纹去重版)...")
        total = len(reviews)
        for idx, r in enumerate(reviews):
            content = r.get("review", "") or r.get("comment", "") or r.get("text", "") or r.get("content", "")
            parts = re.split(split_pattern, content)
            
            for p in parts:
                cleaned = DataCleaner.clean_text(p)
                if cleaned:
                    # 计算指纹
                    fp = DataCleaner.get_fingerprint(cleaned)
                    
                    # 只有当指纹没出现过，才算有效数据
                    if fp and fp not in seen_fingerprints:
                        pool.append({
                            "text": cleaned,
                            "id": r.get("recommendationid", r.get("id", "0")),
                            "lang": r.get("language", r.get("lang", "unknown"))
                        })
                        seen_fingerprints.add(fp)
            
            if progress_callback and idx % 10 == 0:
                progress_callback(idx + 1, total)
        
        if progress_callback:
            progress_callback(total, total)
        
        return pool


# ==========================================
# 2. 情感分析 (GPU)
# ==========================================
class SentimentEngine:
    def __init__(self, force_cpu=False):
        print("❤️ 正在初始化情感分析模型...")
        model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
        
        # Determine device to use
        target_device = torch.device("cpu") if force_cpu else GPU_DEVICE
        
        try:
            print(f"  📥 下载/加载 tokenizer...")
            import sys
            sys.stdout.flush()  # Force flush to ensure message is printed
            
            # Add timeout and retry logic
            import time
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        model_name,
                        local_files_only=False,  # Allow downloading
                        resume_download=True      # Resume if interrupted
                    )
                    break
                except Exception as retry_error:
                    if attempt < max_retries - 1:
                        print(f"  ⚠️ Tokenizer 加载失败 (尝试 {attempt + 1}/{max_retries}): {retry_error}")
                        print(f"  🔄 等待 2 秒后重试...")
                        sys.stdout.flush()
                        time.sleep(2)
                    else:
                        raise
            
            print(f"  ✅ Tokenizer 加载完成")
            sys.stdout.flush()
            
            print(f"  📥 下载/加载模型 (首次运行可能需要几分钟，~500MB)...")
            print(f"  ⏳ 请耐心等待，不要关闭窗口...")
            sys.stdout.flush()
            
            # Load model with retry logic
            for attempt in range(max_retries):
                try:
                    self.model = AutoModelForSequenceClassification.from_pretrained(
                        model_name, 
                        use_safetensors=True,
                        local_files_only=False,
                        resume_download=True
                    )
                    break
                except Exception as retry_error:
                    if attempt < max_retries - 1:
                        print(f"  ⚠️ 模型加载失败 (尝试 {attempt + 1}/{max_retries}): {retry_error}")
                        print(f"  🔄 等待 3 秒后重试...")
                        sys.stdout.flush()
                        time.sleep(3)
                    else:
                        raise
            
            print(f"  ✅ 模型下载完成")
            sys.stdout.flush()
            
            print(f"  🎯 将模型移至 {target_device}...")
            sys.stdout.flush()
            
            try:
                self.model = self.model.to(target_device)
                self.device = target_device
                print(f"  ✅ 模型成功加载到 {target_device}")
            except Exception as gpu_error:
                print(f"  ⚠️ GPU 加载失败: {gpu_error}")
                print(f"  🔄 回退到 CPU 模式...")
                sys.stdout.flush()
                self.model = self.model.to(torch.device("cpu"))
                self.device = torch.device("cpu")
                print(f"  ✅ 模型已加载到 CPU")
            
            self.model.eval()
            sys.stdout.flush()
            print(f"  ✅ 模型初始化完成！使用设备: {self.device}")
            sys.stdout.flush()
            
        except Exception as e:
            import traceback
            error_msg = f"模型加载失败: {type(e).__name__}: {str(e)}"
            print(f"❌ {error_msg}")
            print(f"详细错误:\n{traceback.format_exc()}")
            sys.stdout.flush()
            
            # Provide more helpful error message
            if "out of memory" in str(e).lower() or "oom" in str(e).lower():
                error_msg += "\n\n建议：尝试关闭其他占用GPU的程序，或设置 force_cpu=True 使用CPU模式"
            elif "connection" in str(e).lower() or "network" in str(e).lower() or "timeout" in str(e).lower():
                error_msg += "\n\n建议：检查网络连接，模型需要从 huggingface.co 下载"
            elif "torch" in str(e).lower() and "directml" in str(e).lower():
                error_msg += "\n\n建议：AMD GPU 可能存在兼容性问题，尝试使用 CPU 模式"
            elif "http" in str(e).lower() or "ssl" in str(e).lower():
                error_msg += "\n\n建议：网络连接问题，请检查防火墙或代理设置"
            
            raise RuntimeError(error_msg) from e

    def analyze(self, texts, batch_size=32, progress_callback=None):
        results = []
        print(f"❤️ 正在 {self.device} 上计算情感分数 (Batch: {batch_size})...")
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for batch_idx, i in enumerate(range(0, len(texts), batch_size)):
            batch_texts = texts[i : i + batch_size]
            inputs = self.tokenizer(
                batch_texts, return_tensors="pt", padding=True, truncation=True, max_length=128
            ).to(self.device)
            with torch.no_grad():
                outputs = self.model(**inputs)
                scores = torch.nn.functional.softmax(outputs.logits, dim=1)
            scores_cpu = scores.cpu().numpy()
            for score in scores_cpu:
                results.append(float(score[2] - score[0]))
            
            if progress_callback:
                progress_callback(batch_idx + 1, total_batches)
        
        return results


# ==========================================
# 3. 辅助函数
# ==========================================
def get_representative_sentences(df_topic, embeddings_topic, top_n=3):
    if len(df_topic) == 0: return []
    centroid = np.mean(embeddings_topic, axis=0).reshape(1, -1)
    sims = cosine_similarity(centroid, embeddings_topic)[0]
    best_indices = np.argsort(sims)[-top_n:][::-1]
    return df_topic.iloc[best_indices]['text'].tolist()


# ==========================================
# 4. NLPProcessor 类 (与 GUI 兼容)
# ==========================================
class NLPProcessor:
    """
    Advanced NLP processor with GPU acceleration.
    Provides transformer-based sentiment analysis and topic clustering.
    """
    
    def __init__(self):
        """Initialize the advanced NLP processor."""
        print("🚀 初始化高级 NLP 处理器...")
        self.sentiment_engine = None  # Lazy initialization
        self.embedder = None  # Lazy initialization
    
    def _ensure_models_loaded(self):
        """Lazy load models only when needed."""
        if self.sentiment_engine is None:
            self.sentiment_engine = SentimentEngine()
        if self.embedder is None:
            print(f"🧠 加载向量编码器...")
            self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device='cpu')
    
    def process_file(self, input_path: str, output_path: str, progress_callback=None) -> Dict[str, Any]:
        """
        Process a JSON file containing comments with advanced NLP pipeline.
        
        Args:
            input_path: Path to input JSON file
            output_path: Path to save output JSON file
            progress_callback: Optional callback function for progress updates
        
        Returns:
            Dictionary with processing statistics
        """
        # Ensure models are loaded
        self._ensure_models_loaded()
        
        # 1. Read input file
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                raw_reviews = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {e}")
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")
        
        # Extract comments from data
        if isinstance(raw_reviews, list):
            comments = raw_reviews
        elif isinstance(raw_reviews, dict) and 'comments' in raw_reviews:
            comments = raw_reviews['comments']
        else:
            raise ValueError("JSON must be a list or contain a 'comments' key")
        
        if not comments:
            raise ValueError("No comments found in file")
        
        # 2. 清洗与拆分 (带指纹去重)
        statements = DataCleaner.split_to_statements(comments, progress_callback)
        df = pd.DataFrame(statements)
        print(f"📊 有效观点数: {len(df)}")
        
        if len(df) == 0:
            raise ValueError("No valid statements after cleaning")
        
        # 3. 情感分析 (GPU)
        df['sentiment'] = self.sentiment_engine.analyze(
            df['text'].tolist(), 
            batch_size=32, 
            progress_callback=progress_callback
        )
        
        # 4. 向量编码 (CPU)
        print(f"🧠 生成向量 (CPU)...")
        embeddings = self.embedder.encode(
            df['text'].tolist(), 
            show_progress_bar=True, 
            batch_size=32
        )
        embeddings = normalize(embeddings)
        
        # 5. PCA 降维
        print(f"📉 正在降维 (384 -> 50)...")
        pca = PCA(n_components=min(50, len(df) - 1))
        reduced_embeddings = pca.fit_transform(embeddings)
        
        # 6. 聚类 (Leaf 模式)
        print("🛰️ 正在聚类 (Leaf 模式)...")
        min_cluster_size = min(10, max(2, len(df) // 10))
        min_samples = min(15, max(2, len(df) // 20))
        
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size, 
            min_samples=min_samples, 
            metric='euclidean',
            cluster_selection_method='leaf', 
            core_dist_n_jobs=1,
            prediction_data=True
        )
        labels = clusterer.fit_predict(reduced_embeddings)
        df['topic_id'] = labels
        
        num_topics = len(set(labels)) - (1 if -1 in labels else 0)
        print(f"✅ 识别出 {num_topics} 个话题")
        
        # 7. 生成报告
        print("📝 生成报告...")
        output_topics = []
        unique_topics = set(labels)
        
        for t_id in unique_topics:
            if t_id == -1: continue
            
            topic_mask = (df['topic_id'] == t_id)
            topic_data = df[topic_mask]
            topic_embeds = embeddings[topic_mask]

            cultural_dist = topic_data['lang'].value_counts().to_dict()
            avg_sentiment = float(topic_data['sentiment'].mean())
            
            label = "neutral"
            if avg_sentiment > 0.05: label = "positive"
            elif avg_sentiment < -0.05: label = "negative"

            output_topics.append({
                "topic_id": int(t_id),
                "density": len(topic_data),
                "sentiment_score": round(avg_sentiment, 4),
                "sentiment_label": label,
                "cultural_distribution": cultural_dist,
                "representative_sentences": get_representative_sentences(topic_data, topic_embeds),
                "sample_texts": topic_data['text'].head(5).tolist()
            })
        
        output_topics = sorted(output_topics, key=lambda x: x['density'], reverse=True)
        
        # 计算统计信息
        sentiment_distribution = {
            'positive': sum(1 for t in output_topics if t['sentiment_label'] == 'positive'),
            'negative': sum(1 for t in output_topics if t['sentiment_label'] == 'negative'),
            'neutral': sum(1 for t in output_topics if t['sentiment_label'] == 'neutral')
        }
        
        # 保存结果
        output_data = {
            'statistics': {
                'total_comments': len(comments),
                'valid_statements': len(df),
                'topics_identified': num_topics,
                'sentiment_distribution': sentiment_distribution
            },
            'topics': output_topics
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
        
        print(f"💾 结果保存至 {output_path}")
        
        # 返回统计信息 (与 GUI 兼容)
        return {
            'total_comments': len(comments),
            'successful': len(df),
            'errors': len(comments) - len(df),
            'sentiment_distribution': sentiment_distribution
        }


# ==========================================
# 5. 主流程 (命令行使用)
# ==========================================
def run_analysis_pipeline(raw_data_path, output_path='refined_topics_perfect.json'):
    """命令行入口函数"""
    if not os.path.exists(raw_data_path):
        print(f"❌ 找不到文件: {raw_data_path}")
        return
    
    processor = NLPProcessor()
    try:
        stats = processor.process_file(raw_data_path, output_path)
        print(f"\n✅ 处理完成！")
        print(f"   总评论数: {stats['total_comments']}")
        print(f"   有效观点: {stats['successful']}")
        print(f"   情感分布: {stats['sentiment_distribution']}")
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else 'refined_topics_perfect.json'
        run_analysis_pipeline(input_file, output_file)
    else:
        print("用法: python nlp.py <input.json> [output.json]")

