"""
NLP Processing Module (V10.0 Fixed - Date & Viral Patch)
修复日志：
1. [修复] 中文日期清洗：完美移除 "10月21日", "10月22追评", "2023年5月" 等时间戳残留。
2. [升级] 病毒/重复内容分层处理：
   - 刷屏歌词/台词 (出现>10次) -> 全部抹除
   - 普通重复观点 (如"好评") -> 仅保留一条 (去重)
3. [优化] 提升了短句清洗的准确度。
"""

import os
import sys
import logging
import traceback
import re
import json
import numpy as np
import pandas as pd
import hdbscan
import torch
import time

# 依赖库检查
try:
    try:
        import torch_directml
        HAS_DIRECTML = True
    except ImportError:
        HAS_DIRECTML = False

    from sentence_transformers import SentenceTransformer
    from sklearn.preprocessing import normalize
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.decomposition import PCA 
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
except ImportError as e:
    raise RuntimeError(f"缺少依赖库: {e}")

# ==========================================
# 0. 环境配置
# ==========================================
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

logging.basicConfig(
    filename='nlp_error_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def log_print(message):
    print(message)
    logging.info(message)

# ==========================================
# 1. 硬件检测
# ==========================================
def get_device():
    if HAS_DIRECTML:
        log_print(f"🚀 [AMD模式] 激活显卡: {torch_directml.device_name(0)}")
        return torch_directml.device()
    if torch.cuda.is_available():
        log_print("🚀 [NVIDIA模式] 激活 CUDA")
        return torch.device("cuda")
    log_print("🐢 [CPU模式] 使用 CPU")
    return torch.device("cpu")

GLOBAL_DEVICE = get_device()

# ==========================================
# 2. 深度清洗模块 (Updated)
# ==========================================
class DataCleaner:
    STOP_PHRASES = set()
    CONFIG_LOADED = False

    @classmethod
    def load_external_config(cls, filepath="stopWord.txt"):
        cls.STOP_PHRASES = set()
        # Try multiple possible file names
        possible_files = [filepath, "stopWord.txt.txt", "stopWord.txt", "stopwords.txt"]
        
        for possible_file in possible_files:
            if os.path.exists(possible_file):
                try:
                    with open(possible_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            # Remove numbering like "1. ", "2. " etc
                            line = re.sub(r'^\d+\.\s*', '', line)
                            word = line.strip().lower()
                            if word and not word.startswith("#"):
                                cls.STOP_PHRASES.add(word)
                    log_print(f"📖 已加载外部过滤词库: {len(cls.STOP_PHRASES)} 条 (from {possible_file})")
                    cls.CONFIG_LOADED = True
                    return
                except Exception as e:
                    log_print(f"❌ 读取 {possible_file} 出错: {e}")
        
        log_print(f"⚠️ 未找到停用词文件，使用内置列表")
        cls.CONFIG_LOADED = True

    @staticmethod
    def is_cjk(text):
        """检测是否包含 中文、日文、韩文 字符"""
        return re.search(r'[\u4e00-\u9fa5\u3040-\u30ff\uac00-\ud7af]', text) is not None

    @staticmethod
    def clean_text(text):
        if not text: return None
        
        # --- 0. 预处理：移除HTML和特殊乱码 ---
        text = re.sub(r'&[a-z]+;', '', text)
        if re.search(r'[\u2610-\u2612]', text): return None
        if re.search(r'(.)\1{4,}', text): return None # AAAAAA
        if re.search(r'[☐☑☒✅✓✔✖❌]', text): return None 

        # --- 1. [关键修复] 日期与时间戳清洗 ---
        # 移除标准日期: 2023-10-21, 2023.10.21
        text = re.sub(r'\d{4}[-./]\d{1,2}[-./]\d{1,2}', '', text)
        
        # 移除中文日期: 10月21日, 2023年5月, 10月22号, 10.21
        # 解释: (年份可选) + 1-2位数字 + 月 + 1-2位数字 + (日/号 可选) + (追评/更新 可选)
        text = re.sub(r'(?:20\d{2}[年.-])?\d{1,2}[月.-]\d{1,2}[日号]?(?:[\s]*(?:追评|更新|edit))?', '', text, flags=re.IGNORECASE)
        # 移除单独的"追评"字样
        text = re.sub(r'^\s*(?:追评|更新|update)\s*[:：]?', '', text, flags=re.IGNORECASE)
        # 移除括号内的纯日期: (10月21日)
        text = re.sub(r'\(\d{1,2}月\d{1,2}[日号]?\)', '', text)

        # --- 2. 基础清洗 ---
        text = re.sub(r'\[/?code\]', '', text)
        text = re.sub(r'\[/?.*?\]', '', text) # 去除 Steam 标签
        
        # 保留中日韩字符、单词字符、空格
        pure_text = re.sub(r'[^\w\u4e00-\u9fa5\u3040-\u30ff]', ' ', text).strip()
        
        # --- 3. 分语言处理与长度校验 ---
        if DataCleaner.is_cjk(pure_text):
            # 移除所有空格后检查长度
            cjk_content = re.sub(r'\s', '', pure_text)
            # 这里的 < 4 配合上面的日期清洗，可以有效过滤掉只剩 "10月" 这种情况
            if len(cjk_content) < 4: return None 
            return text.strip()
        else:
            if len(pure_text) < 12: return None # 英文长度惩罚
            words = pure_text.split()
            if len(words) < 3: return None
            
            # 停用词清洗
            if DataCleaner.STOP_PHRASES:
                meaningful_words = [w for w in words if w.lower() not in DataCleaner.STOP_PHRASES]
                if len(meaningful_words) < 1: return None
            
            # 简单去重词检查 (aaaa aaaa)
            if len(words) > 4:
                unique_ratio = len(set([w.lower() for w in words])) / len(words)
                if unique_ratio < 0.2: return None

            return text.strip()

    @staticmethod
    def split_to_statements(reviews, progress_callback=None):
        if not DataCleaner.CONFIG_LOADED:
            DataCleaner.load_external_config()

        pool = []
        # 这里的指纹仅用于单条评论内的简单去重
        split_pattern = r'[。！!？?\n|；;~]' 
        
        for idx, r in enumerate(reviews):
            content = r.get("review", "") or r.get("comment", "") or r.get("text", "") or r.get("content", "")
            if not content: continue
            
            # 简单去重set，防止单个人复读
            local_fingerprints = set()

            parts = re.split(split_pattern, content)
            for p in parts:
                cleaned = DataCleaner.clean_text(p)
                if cleaned:
                    fp = re.sub(r'\s', '', cleaned).lower()
                    if fp and fp not in local_fingerprints:
                        pool.append({
                            "text": cleaned,
                            "id": r.get("recommendationid", r.get("id", str(idx))),
                            "lang": r.get("language", "unknown")
                        })
                        local_fingerprints.add(fp)
        return pool

    # ========================================================
    # 3. [核心升级] 病毒式传播/重复内容清洗
    # ========================================================
    @staticmethod
    def filter_viral_content(df_statements, viral_threshold=10, strict_len=6):
        """
        双重清洗逻辑：
        1. Viral Filter (杀毒): 出现次数极高且句子较长的(如歌词/台词)，全部删除，防止聚类成"歌词"话题。
        2. Deduplication (去重): 普通重复内容(如"好评")，仅保留一条，防止权重偏差。
        """
        if len(df_statements) == 0: return df_statements
        
        original_count = len(df_statements)
        log_print("🧹 正在进行 [病毒查杀] 与 [观点去重]...")

        # 1. 生成“骨架指纹” (移除标点/空格/大小写)
        # 比如: "Wake up, Samurai..." -> "wakeupsamurai"
        df_statements['temp_fp'] = df_statements['text'].apply(
            lambda x: re.sub(r'[^\w\u4e00-\u9fa5]', '', str(x)).lower()
        )
        
        # 2. 统计指纹频次
        fp_counts = df_statements['temp_fp'].value_counts()
        
        # ----------------------------------------------------
        # 策略 A: 病毒式内容查杀 (全部移除)
        # 条件: 重复次数 > 10 (默认) 且 长度 > 6 (防止误杀短语)
        # ----------------------------------------------------
        viral_fps = fp_counts[
            (fp_counts >= viral_threshold) & 
            (fp_counts.index.str.len() >= strict_len)
        ].index
        
        if len(viral_fps) > 0:
            top_viral = viral_fps[0]
            example = df_statements[df_statements['temp_fp'] == top_viral]['text'].iloc[0]
            log_print(f"   ⚠️ 检测到刷屏内容 (TOP 1): '{example}' (重复 {fp_counts[top_viral]} 次) -> 全部移除")
        
        # 执行删除
        df_clean = df_statements[~df_statements['temp_fp'].isin(viral_fps)].copy()
        viral_removed = original_count - len(df_clean)
        
        # ----------------------------------------------------
        # 策略 B: 普通观点去重 (只保留一条)
        # 条件: 剩下的内容中，如果有重复，只留第一条
        # ----------------------------------------------------
        count_before_dedup = len(df_clean)
        # keep='first' 确保同一种观点只留一个代表，不影响聚类中心，但能减少计算量和密度偏差
        df_clean = df_clean.drop_duplicates(subset=['temp_fp'], keep='first')
        dedup_removed = count_before_dedup - len(df_clean)
        
        # 5. 清理临时列
        df_clean = df_clean.drop(columns=['temp_fp'])
        
        log_print(f"📉 清洗报告: 剔除刷屏 {viral_removed} 条 | 归并重复观点 {dedup_removed} 条")
        log_print(f"✅ 最终有效语句: {len(df_clean)} 条")
            
        return df_clean

# ==========================================
# 4. 情感分析引擎
# ==========================================
class SentimentEngine:
    def __init__(self):
        log_print(f"❤️ 初始化情感模型 (GPU: {GLOBAL_DEVICE})...")
        model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name, use_safetensors=True 
            ).to(GLOBAL_DEVICE)
            self.model.eval()
        except Exception as e:
            log_print(f"❌ 情感模型加载失败: {e}")
            raise e

    def analyze(self, texts, batch_size=32, progress_callback=None):
        results = []
        total = len(texts)
        if str(GLOBAL_DEVICE) == 'cpu': batch_size = 16
        
        log_print(f"❤️ 计算情感分 (Total: {total})...")
        
        for i in range(0, total, batch_size):
            batch_texts = texts[i : i + batch_size]
            try:
                inputs = self.tokenizer(
                    batch_texts, return_tensors="pt", padding=True, truncation=True, max_length=128
                ).to(GLOBAL_DEVICE)
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    scores = torch.nn.functional.softmax(outputs.logits, dim=1)
                
                scores_cpu = scores.cpu().numpy()
                for score in scores_cpu:
                    results.append(float(score[2] - score[0]))
            except Exception as e:
                log_print(f"⚠️ Batch Error: {e}")
                results.extend([0.0] * len(batch_texts))
                if HAS_DIRECTML: 
                    try: torch.cuda.empty_cache()
                    except: pass

            if progress_callback:
                curr_pct = 20 + int((i / total) * 50)
                progress_callback(curr_pct, f"分析情感 ({i}/{total})...")
                
        return results

# ==========================================
# 5. 主处理器
# ==========================================
class NLPProcessor:
    def __init__(self):
        log_print("🚀 引擎准备就绪")
        self.sentiment_engine = None
        self.embedder = None 
    
    def _ensure_models_loaded(self):
        if self.sentiment_engine is None:
            self.sentiment_engine = SentimentEngine()
        if self.embedder is None:
            log_print("🧠 加载 Embedding (强制 CPU 以节省显存)...")
            self.embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device='cpu')
    
    def get_representative_sentences(self, df_topic, embeddings_topic, top_n=3):
        if len(df_topic) == 0: return []
        centroid = np.mean(embeddings_topic, axis=0).reshape(1, -1)
        sims = cosine_similarity(centroid, embeddings_topic)[0]
        lengths = df_topic['text'].str.len()
        def length_weight(l):
            if l < 17: return 0.6
            if 17 <= l <= 50: return 1.2 
            return 1.0
        weights = lengths.apply(length_weight)
        final_scores = sims * weights
        best_indices = np.argsort(final_scores)[-top_n:][::-1]
        return df_topic.iloc[best_indices]['text'].tolist()

    def merge_similar_topics(self, df, embeddings, similarity_threshold=0.96):
        unique_topics = [t for t in df['topic_id'].unique() if t != -1]
        if not unique_topics: return df
        
        topic_centroids = {}
        for t_id in unique_topics:
            topic_vectors = embeddings[df['topic_id'] == t_id]
            centroid = np.mean(topic_vectors, axis=0)
            norm = np.linalg.norm(centroid)
            topic_centroids[t_id] = centroid / norm if norm > 0 else centroid

        merge_map = {t: t for t in unique_topics}
        sorted_topics = sorted(unique_topics)

        log_print(f"🔄 话题合并 (阈值: {similarity_threshold})...")
        merged_count = 0
        for i in range(len(sorted_topics)):
            id_a = sorted_topics[i]
            if merge_map[id_a] != id_a: continue
            for j in range(i + 1, len(sorted_topics)):
                id_b = sorted_topics[j]
                if merge_map[id_b] != id_b: continue
                if np.dot(topic_centroids[id_a], topic_centroids[id_b]) > similarity_threshold:
                    merge_map[id_b] = id_a
                    merged_count += 1

        df['topic_id'] = df['topic_id'].map(lambda x: merge_map.get(x, x))
        log_print(f"✅ 合并完成，减少了 {merged_count} 个冗余话题")
        return df

    def process_file(self, input_path: str, output_path: str, progress_callback=None) -> dict:
        log_print(f"📂 读取文件: {input_path}")
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                raw_reviews = json.load(f)
            comments = raw_reviews if isinstance(raw_reviews, list) else raw_reviews.get('comments', [])
            
            # 1. 基础分句 (含日期清洗)
            statements = DataCleaner.split_to_statements(comments, progress_callback)
            df = pd.DataFrame(statements)
            log_print(f"📊 基础分句后: {len(df)} 条")
            
            if len(df) == 0: raise ValueError("数据清洗后为空！")

            # ==========================================================
            # 2. [升级] 病毒/重复内容双重清洗
            # viral_threshold=10: 同样的句子重复超过10次且较长 -> 视为刷屏歌词，全删
            # ==========================================================
            df = DataCleaner.filter_viral_content(df, viral_threshold=10, strict_len=8)

            if len(df) == 0: raise ValueError("全都是复读机，清洗后数据为空！")

            if progress_callback: progress_callback(20, "加载 AI 模型...")
            self._ensure_models_loaded()

            # 3. 情感分析
            df['sentiment'] = self.sentiment_engine.analyze(df['text'].tolist(), batch_size=32, progress_callback=progress_callback)

            if progress_callback: progress_callback(70, "生成语义向量...")
            embeddings = self.embedder.encode(df['text'].tolist(), batch_size=32, show_progress_bar=False)
            normalized_embeddings = normalize(embeddings) 

            if progress_callback: progress_callback(80, "聚类分析...")
            pca = PCA(n_components=min(50, len(df) - 1))
            reduced_embeddings = pca.fit_transform(normalized_embeddings)
            
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=min(15, max(5, len(df) // 100)), 
                min_samples=min(15, max(2, len(df) // 200)),
                metric='euclidean',
                cluster_selection_method='leaf'
            )
            df['topic_id'] = clusterer.fit_predict(reduced_embeddings)

            if progress_callback: progress_callback(85, "优化话题...")
            df = self.merge_similar_topics(df, normalized_embeddings, similarity_threshold=0.88)

            if progress_callback: progress_callback(90, "生成报告...")
            output_topics = []
            unique_topics = set(df['topic_id'].unique())
            
            for t_id in unique_topics:
                if t_id == -1: continue 
                mask = (df['topic_id'] == t_id)
                topic_data = df[mask]
                
                score = float(topic_data['sentiment'].mean())
                label = "neutral"
                if score > 0.05: label = "positive"
                elif score < -0.05: label = "negative"

                output_topics.append({
                    "topic_id": int(t_id),
                    "density": len(topic_data),
                    "sentiment_score": round(score, 4),
                    "sentiment_label": label,
                    "cultural_distribution": topic_data['lang'].value_counts().to_dict(),
                    "representative_sentences": self.get_representative_sentences(topic_data, normalized_embeddings[mask]),
                    "sample_texts": topic_data['text'].head(10).tolist()
                })

            output_topics = sorted(output_topics, key=lambda x: x['density'], reverse=True)
            final_data = {'statistics': {'total': len(comments), 'valid': len(df)}, 'topics': output_topics}
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, ensure_ascii=False, indent=4)
            
            if progress_callback: progress_callback(100, "处理完成！")
            return final_data

        except Exception as e:
            error_msg = traceback.format_exc()
            log_print(f"❌ 错误:\n{error_msg}")
            raise RuntimeError(f"后端错误: {str(e)}")

# ==========================================
# 6. Google Embedding Projector Export
# ==========================================
def export_to_projector(embeddings, dataframe, output_dir=".", vectors_filename="vectors.tsv", metadata_filename="metadata.tsv"):
    """
    Export embeddings and metadata to TSV files compatible with Google Embedding Projector.
    
    Args:
        embeddings: numpy array of shape (n_samples, n_dimensions) - the embedding vectors
        dataframe: pandas DataFrame containing at least 'text' and 'topic_id' columns
        output_dir: directory where TSV files will be saved (default: current directory)
        vectors_filename: name for the vectors TSV file (default: "vectors.tsv")
        metadata_filename: name for the metadata TSV file (default: "metadata.tsv")
    
    Usage:
        processor = NLPProcessor()
        result = processor.process_file("input.json", "output.json")
        # After processing, you can export embeddings from the dataframe
        export_to_projector(embeddings, df, output_dir="analysis")
    
    Google Embedding Projector: https://projector.tensorflow.org/
    """
    import os
    import numpy as np
    import pandas as pd
    
    # Language detection lambda function
    detect_language = lambda text: (
        'Chinese' if any('\u4e00' <= c <= '\u9fff' for c in str(text)) else
        'Japanese' if any('\u3040' <= c <= '\u30ff' or '\u31f0' <= c <= '\u31ff' for c in str(text)) else
        'English'
    )
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    vectors_path = os.path.join(output_dir, vectors_filename)
    metadata_path = os.path.join(output_dir, metadata_filename)
    
    # Validate inputs
    if embeddings is None or len(embeddings) == 0:
        raise ValueError("Embeddings array is empty or None")
    
    if dataframe is None or len(dataframe) == 0:
        raise ValueError("DataFrame is empty or None")
    
    if len(embeddings) != len(dataframe):
        raise ValueError(f"Embeddings length ({len(embeddings)}) must match DataFrame length ({len(dataframe)})")
    
    # Check required columns
    required_cols = ['text', 'topic_id']
    missing_cols = [col for col in required_cols if col not in dataframe.columns]
    if missing_cols:
        raise ValueError(f"DataFrame missing required columns: {missing_cols}")
    
    log_print(f"📊 Exporting to Google Embedding Projector format...")
    log_print(f"   - Embeddings shape: {embeddings.shape}")
    log_print(f"   - DataFrame rows: {len(dataframe)}")
    
    # 1. Save vectors.tsv (no header, tab-separated)
    try:
        np.savetxt(vectors_path, embeddings, delimiter='\t', fmt='%.8f')
        log_print(f"✅ Saved vectors to: {vectors_path}")
    except Exception as e:
        raise RuntimeError(f"Failed to save vectors: {e}")
    
    # 2. Create and save metadata.tsv
    try:
        # Create metadata dataframe with required columns
        metadata_df = pd.DataFrame()
        
        # Add text column (clean it for TSV format - remove tabs and newlines)
        metadata_df['text'] = dataframe['text'].astype(str).apply(
            lambda x: x.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ').strip()
        )
        
        # Add topic_id column
        metadata_df['topic_id'] = dataframe['topic_id'].astype(str)
        
        # Add language column using detection lambda
        metadata_df['language'] = dataframe['text'].apply(detect_language)
        
        # Save with tab separator and include header
        metadata_df.to_csv(metadata_path, sep='\t', index=False, encoding='utf-8')
        
        log_print(f"✅ Saved metadata to: {metadata_path}")
        
        # Log language distribution
        lang_counts = metadata_df['language'].value_counts()
        log_print(f"   Language distribution:")
        for lang, count in lang_counts.items():
            log_print(f"     - {lang}: {count} ({count/len(metadata_df)*100:.1f}%)")
        
    except Exception as e:
        raise RuntimeError(f"Failed to save metadata: {e}")
    
    log_print(f"🎉 Export complete! Load these files at https://projector.tensorflow.org/")
    log_print(f"   1. Upload {vectors_filename}")
    log_print(f"   2. Upload {metadata_filename}")
    
    return {
        'vectors_path': vectors_path,
        'metadata_path': metadata_path,
        'num_samples': len(embeddings),
        'dimensions': embeddings.shape[1] if len(embeddings.shape) > 1 else 1,
        'languages': lang_counts.to_dict()
    }

# 调试入口
if __name__ == "__main__":
    input_file = "input.json" 
    output_file = f"debug_result_{int(time.time())}.json"
    def simple_progress(pct, msg): print(f"[Progress {pct}%] {msg}")
    if os.path.exists(input_file):
        processor = NLPProcessor()
        processor.process_file(input_file, output_file, progress_callback=simple_progress)