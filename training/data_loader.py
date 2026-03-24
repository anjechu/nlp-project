"""
数据加载器 - 支持对比学习和课程学习
Data Loader for Contrastive Learning + Curriculum Learning

支持:
- Steam评论数据加载
- 自动标签生成（基于情感分数）
- 对比学习的正负样本对构建
- 多语言支持
- Glob模式加载多个文件
"""

import json
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
from typing import List, Dict, Tuple, Optional
import random
from collections import defaultdict
import glob
import os


class SteamReviewDataset(Dataset):
    """
    Steam评论数据集
    
    数据格式支持:
    1. 原始Steam评论 (带review字段)
    2. 已处理评论 (带text字段)
    3. 带标注数据 (带sentiment/label字段)
    """
    
    def __init__(
        self,
        data_path: str,
        tokenizer,
        max_length: int = 128,
        auto_label: bool = True,
        min_text_length: int = 10
    ):
        """
        Args:
            data_path: JSON数据文件路径（支持glob模式，如 "*.json" 或 "data/*.json"）
            tokenizer: HuggingFace tokenizer
            max_length: 最大序列长度
            auto_label: 是否自动生成标签（基于XLM-RoBERTa预测）
            min_text_length: 最小文本长度
        """
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.auto_label = auto_label
        
        # 检查是否是glob模式
        if '*' in data_path or '?' in data_path:
            # Glob模式：加载多个文件
            print(f"📂 正在扫描路径: {data_path}")
            file_list = glob.glob(data_path)
            if not file_list:
                print(f"⚠️ 警告: 未找到匹配 '{data_path}' 的文件")
                self.reviews = []
            else:
                print(f"🔍 成功匹配到 {len(file_list)} 个 JSON 文件，开始合并加载...")
                self.reviews = []
                for file_path in file_list:
                    try:
                        print(f"   加载: {os.path.basename(file_path)}")
                        with open(file_path, 'r', encoding='utf-8') as f:
                            raw_data = json.load(f)
                        
                        # 解析数据格式并合并
                        if isinstance(raw_data, list):
                            self.reviews.extend(raw_data)
                        elif isinstance(raw_data, dict):
                            # 尝试不同的字段名
                            file_reviews = (
                                raw_data.get('comments', []) or 
                                raw_data.get('reviews', []) or
                                raw_data.get('data', [])
                            )
                            self.reviews.extend(file_reviews)
                    except Exception as e:
                        print(f"   ⚠️ 加载失败 {os.path.basename(file_path)}: {e}")
                        continue
                
                print(f"✓ 合并完成: 共 {len(self.reviews)} 条原始评论")
        else:
            # 单个文件：直接加载
            print(f"📂 加载数据: {data_path}")
            if not os.path.exists(data_path):
                raise FileNotFoundError(f"数据文件不存在: {data_path}")
            
            with open(data_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # 解析数据格式
            if isinstance(raw_data, list):
                self.reviews = raw_data
            elif isinstance(raw_data, dict):
                # 尝试不同的字段名
                self.reviews = (
                    raw_data.get('comments', []) or 
                    raw_data.get('reviews', []) or
                    raw_data.get('data', [])
                )
            else:
                raise ValueError(f"不支持的数据格式: {type(raw_data)}")
        
        # 清洗和预处理
        self.samples = []
        for idx, review in enumerate(self.reviews):
            # 提取文本
            text = (
                review.get('text', '') or
                review.get('review', '') or
                review.get('comment', '') or
                review.get('content', '')
            ).strip()
            
            if len(text) < min_text_length:
                continue
            
            # 提取语言
            language = review.get('language', 'unknown')
            
            # 提取或生成标签
            if 'sentiment' in review:
                label = self._sentiment_to_label(review['sentiment'])
            elif 'label' in review:
                label = review['label']
            elif auto_label:
                label = -1  # 稍后批量预测
            else:
                continue
            
            self.samples.append({
                'text': text,
                'language': language,
                'label': label,
                'original_idx': idx
            })
        
        print(f"✓ 加载完成: {len(self.samples)} 条有效样本")
        
        # 如果需要自动标注，批量预测
        if auto_label and any(s['label'] == -1 for s in self.samples):
            print("🤖 自动标注中...")
            self._auto_label_samples()
    
    def _sentiment_to_label(self, sentiment) -> int:
        """将情感转换为标签"""
        if isinstance(sentiment, (int, np.integer)):
            return int(sentiment)
        elif isinstance(sentiment, float):
            # 情感分数: -1 到 1
            if sentiment > 0.2:
                return 2  # positive
            elif sentiment < -0.2:
                return 0  # negative
            else:
                return 1  # neutral
        elif isinstance(sentiment, str):
            sentiment = sentiment.lower()
            if sentiment in ['positive', 'pos', '正面']:
                return 2
            elif sentiment in ['negative', 'neg', '负面']:
                return 0
            else:
                return 1
        else:
            return 1  # default neutral
    
    def _auto_label_samples(self):
        """使用预训练模型自动标注样本"""
        from transformers import AutoModelForSequenceClassification
        import torch.nn.functional as F
        
        # 加载预训练模型
        model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
        print(f"   加载模型: {model_name}")
        
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name, use_safetensors=True
        ).to(device)
        model.eval()
        
        # 批量预测
        batch_size = 32
        unlabeled_indices = [i for i, s in enumerate(self.samples) if s['label'] == -1]
        
        with torch.no_grad():
            for i in range(0, len(unlabeled_indices), batch_size):
                batch_indices = unlabeled_indices[i:i+batch_size]
                batch_texts = [self.samples[idx]['text'] for idx in batch_indices]
                
                # Tokenize
                inputs = self.tokenizer(
                    batch_texts,
                    return_tensors='pt',
                    padding=True,
                    truncation=True,
                    max_length=self.max_length
                ).to(device)
                
                # 预测
                outputs = model(**inputs)
                probs = F.softmax(outputs.logits, dim=1)
                labels = torch.argmax(probs, dim=1).cpu().numpy()
                
                # 更新标签
                for idx, label in zip(batch_indices, labels):
                    self.samples[idx]['label'] = int(label)
                
                if (i // batch_size + 1) % 10 == 0:
                    print(f"   进度: {i+len(batch_indices)}/{len(unlabeled_indices)}")
        
        print(f"✓ 自动标注完成")
        
        # 统计标签分布
        label_counts = defaultdict(int)
        for s in self.samples:
            label_counts[s['label']] += 1
        print(f"   标签分布: {dict(label_counts)}")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        # Tokenize
        encoding = self.tokenizer(
            sample['text'],
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'labels': torch.tensor(sample['label'], dtype=torch.long),
            'language': sample['language'],
            'text': sample['text']
        }
    
    def get_label_distribution(self) -> Dict[int, int]:
        """获取标签分布"""
        label_counts = defaultdict(int)
        for sample in self.samples:
            label_counts[sample['label']] += 1
        return dict(label_counts)
    
    def get_samples_by_label(self, label: int) -> List[Dict]:
        """获取特定标签的所有样本"""
        return [s for s in self.samples if s['label'] == label]


class ContrastiveDataLoader:
    """
    对比学习数据加载器
    
    功能:
    1. 为每个anchor样本找到正样本（同类）和负样本（异类）
    2. 支持hard negative mining
    3. 支持跨语言对比（相同情感的不同语言表达）
    """
    
    def __init__(
        self,
        dataset: SteamReviewDataset,
        batch_size: int = 32,
        num_positives: int = 2,
        num_negatives: int = 2,
        shuffle: bool = True,
        cross_lingual: bool = True
    ):
        """
        Args:
            dataset: Steam评论数据集
            batch_size: 批次大小
            num_positives: 每个anchor的正样本数量
            num_negatives: 每个anchor的负样本数量
            shuffle: 是否打乱
            cross_lingual: 是否使用跨语言对比
        """
        self.dataset = dataset
        self.batch_size = batch_size
        self.num_positives = num_positives
        self.num_negatives = num_negatives
        self.shuffle = shuffle
        self.cross_lingual = cross_lingual
        
        # 按标签和语言索引样本
        self._build_indices()
    
    def _build_indices(self):
        """构建标签和语言索引"""
        self.label_indices = defaultdict(list)
        self.label_lang_indices = defaultdict(lambda: defaultdict(list))
        
        for idx, sample in enumerate(self.dataset.samples):
            label = sample['label']
            lang = sample['language']
            
            self.label_indices[label].append(idx)
            self.label_lang_indices[label][lang].append(idx)
        
        print(f"📊 对比学习索引构建完成:")
        for label in sorted(self.label_indices.keys()):
            print(f"   标签 {label}: {len(self.label_indices[label])} 样本")
    
    def _sample_positives(self, anchor_idx: int, anchor_label: int, anchor_lang: str) -> List[int]:
        """为anchor采样正样本（同类情感）"""
        if self.cross_lingual:
            # 跨语言正样本：相同标签，不同语言
            candidates = []
            for lang, indices in self.label_lang_indices[anchor_label].items():
                if lang != anchor_lang:
                    candidates.extend(indices)
            
            # 如果跨语言样本不足，添加同语言样本
            if len(candidates) < self.num_positives:
                candidates.extend(self.label_indices[anchor_label])
        else:
            candidates = self.label_indices[anchor_label]
        
        # 排除anchor自己
        candidates = [idx for idx in candidates if idx != anchor_idx]
        
        if len(candidates) == 0:
            return []
        
        # 随机采样
        num_to_sample = min(self.num_positives, len(candidates))
        return random.sample(candidates, num_to_sample)
    
    def _sample_negatives(self, anchor_label: int) -> List[int]:
        """为anchor采样负样本（异类情感）"""
        candidates = []
        for label, indices in self.label_indices.items():
            if label != anchor_label:
                candidates.extend(indices)
        
        if len(candidates) == 0:
            return []
        
        num_to_sample = min(self.num_negatives, len(candidates))
        return random.sample(candidates, num_to_sample)
    
    def __iter__(self):
        """迭代器"""
        indices = list(range(len(self.dataset)))
        if self.shuffle:
            random.shuffle(indices)
        
        for i in range(0, len(indices), self.batch_size):
            batch_indices = indices[i:i+self.batch_size]
            batch_data = []
            
            for anchor_idx in batch_indices:
                anchor_sample = self.dataset.samples[anchor_idx]
                anchor_label = anchor_sample['label']
                anchor_lang = anchor_sample['language']
                
                # 采样正负样本
                positive_indices = self._sample_positives(anchor_idx, anchor_label, anchor_lang)
                negative_indices = self._sample_negatives(anchor_label)
                
                # 构建对比样本组
                contrastive_group = {
                    'anchor': self.dataset[anchor_idx],
                    'positives': [self.dataset[idx] for idx in positive_indices],
                    'negatives': [self.dataset[idx] for idx in negative_indices],
                }
                
                batch_data.append(contrastive_group)
            
            yield self._collate_batch(batch_data)
    
    def _collate_batch(self, batch_data: List[Dict]) -> Dict:
        """整理批次数据"""
        batch = {
            'anchor_input_ids': [],
            'anchor_attention_mask': [],
            'anchor_labels': [],
            'positive_input_ids': [],
            'positive_attention_mask': [],
            'positive_labels': [],
            'negative_input_ids': [],
            'negative_attention_mask': [],
            'negative_labels': [],
        }
        
        for group in batch_data:
            # Anchor
            batch['anchor_input_ids'].append(group['anchor']['input_ids'])
            batch['anchor_attention_mask'].append(group['anchor']['attention_mask'])
            batch['anchor_labels'].append(group['anchor']['labels'])
            
            # Positives
            for pos in group['positives']:
                batch['positive_input_ids'].append(pos['input_ids'])
                batch['positive_attention_mask'].append(pos['attention_mask'])
                batch['positive_labels'].append(pos['labels'])
            
            # Negatives
            for neg in group['negatives']:
                batch['negative_input_ids'].append(neg['input_ids'])
                batch['negative_attention_mask'].append(neg['attention_mask'])
                batch['negative_labels'].append(neg['labels'])
        
        # 转换为tensor
        for key in batch:
            if len(batch[key]) > 0:
                batch[key] = torch.stack(batch[key])
        
        return batch
    
    def __len__(self):
        return (len(self.dataset) + self.batch_size - 1) // self.batch_size
