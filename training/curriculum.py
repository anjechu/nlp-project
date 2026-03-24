"""
课程学习 (Curriculum Learning) - 难度评估与调度
Curriculum Learning for Sentiment Analysis

基于以下论文:
- "Curriculum Learning" (Bengio et al., ICML 2009)
- "On The Power of Curriculum Learning in Training Deep Networks" (Hacohen & Weinshall, ICML 2019)

针对跨文化情感分析的特点:
1. 语言复杂度（多音节、委婉表达、文化特定表达）
2. 情感强度（明确 vs 模糊）
3. 跨语言难度（East Asian languages的委婉表达）
"""

import numpy as np
from typing import List, Dict, Tuple
import re
from collections import Counter


class DifficultyEstimator:
    """
    样本难度评估器
    
    评估维度:
    1. 语言复杂度 (linguistic complexity)
    2. 情感模糊度 (sentiment ambiguity)
    3. 文化特异性 (cultural specificity)
    """
    
    def __init__(self):
        # 东亚语言的委婉表达模式
        self.east_asian_patterns = {
            'chinese': [
                r'还[行好可以]', r'不[太]?[错差]', r'尚可', r'马马虎虎',
                r'一般般', r'凑合', r'勉强'
            ],
            'japanese': [
                r'まあまあ', r'そこそこ', r'普通', r'まぁ', 
                r'悪くない', r'いいんじゃない'
            ],
            'korean': [
                r'그냥', r'괜찮', r'나쁘지 않', r'그럭저럭'
            ]
        }
        
        # 情感强度词
        self.strong_sentiment_words = {
            'positive': [
                'amazing', 'excellent', 'perfect', 'outstanding', 'brilliant',
                '完美', '极好', '超棒', '绝了', '神作',
                '素晴らしい', '最高', '完璧'
            ],
            'negative': [
                'terrible', 'horrible', 'awful', 'worst', 'disaster',
                '垃圾', '糟糕', '太差', '烂', '坑',
                'ひどい', '最悪', 'クソ'
            ]
        }
    
    def estimate_difficulty(self, text: str, language: str = 'unknown') -> float:
        """
        估计文本难度（0-1，越大越难）
        
        Args:
            text: 文本内容
            language: 语言标识
            
        Returns:
            难度分数 (0=简单, 1=困难)
        """
        scores = []
        
        # 1. 语言复杂度 (30%)
        ling_difficulty = self._linguistic_complexity(text, language)
        scores.append(('linguistic', ling_difficulty, 0.30))
        
        # 2. 情感模糊度 (40%)
        sent_difficulty = self._sentiment_ambiguity(text, language)
        scores.append(('sentiment', sent_difficulty, 0.40))
        
        # 3. 文化特异性 (30%)
        cult_difficulty = self._cultural_specificity(text, language)
        scores.append(('cultural', cult_difficulty, 0.30))
        
        # 加权平均
        total_difficulty = sum(score * weight for _, score, weight in scores)
        
        return total_difficulty
    
    def _linguistic_complexity(self, text: str, language: str) -> float:
        """语言复杂度评估"""
        # 基础指标
        text_len = len(text)
        word_count = len(text.split())
        
        # 长度惩罚（长文本更难）
        length_factor = min(text_len / 200.0, 1.0)
        
        # 标点复杂度（多句子更难）
        punctuation_count = len(re.findall(r'[。！？,.!?;；]', text))
        punct_factor = min(punctuation_count / 5.0, 1.0)
        
        # CJK vs 西方语言
        cjk_chars = len(re.findall(r'[\u4e00-\u9fa5\u3040-\u30ff\uac00-\ud7af]', text))
        if cjk_chars > text_len * 0.3:
            # CJK语言：字数少但信息密度高
            cjk_factor = min(cjk_chars / 50.0, 1.0)
            return (cjk_factor * 0.5 + punct_factor * 0.3 + length_factor * 0.2)
        else:
            # 西方语言：词数多
            word_factor = min(word_count / 30.0, 1.0)
            return (word_factor * 0.5 + punct_factor * 0.3 + length_factor * 0.2)
    
    def _sentiment_ambiguity(self, text: str, language: str) -> float:
        """情感模糊度评估"""
        text_lower = text.lower()
        
        # 检测强情感词
        strong_pos = sum(1 for word in self.strong_sentiment_words['positive'] 
                        if word.lower() in text_lower)
        strong_neg = sum(1 for word in self.strong_sentiment_words['negative'] 
                        if word.lower() in text_lower)
        
        # 有明确强情感词 → 简单
        if strong_pos > 0 or strong_neg > 0:
            return 0.2
        
        # 检测中性词和混合情感
        neutral_patterns = [
            r'\b(okay|ok|fine|acceptable|decent)\b',
            r'\b(还行|还好|可以|一般|普通)\b',
            r'\b(普通|まあまあ|そこそこ)\b'
        ]
        
        neutral_count = sum(1 for pattern in neutral_patterns 
                           if re.search(pattern, text_lower))
        
        # 中性表达 → 困难
        if neutral_count > 0:
            return 0.8
        
        # 检测转折词（but, however, although）
        contrast_patterns = [
            r'\b(but|however|although|though)\b',
            r'\b(但是|不过|虽然|然而)\b',
            r'\b(でも|しかし|けど)\b'
        ]
        
        contrast_count = sum(1 for pattern in contrast_patterns 
                            if re.search(pattern, text_lower))
        
        # 有转折 → 较难
        if contrast_count > 0:
            return 0.7
        
        # 默认中等难度
        return 0.5
    
    def _cultural_specificity(self, text: str, language: str) -> float:
        """文化特异性评估"""
        lang_normalized = language.lower()
        
        # 检测东亚委婉表达
        if lang_normalized in self.east_asian_patterns:
            patterns = self.east_asian_patterns[lang_normalized]
            for pattern in patterns:
                if re.search(pattern, text):
                    return 0.9  # 委婉表达 → 高难度
        
        # 检测跨语言混合（code-switching）
        scripts = []
        if re.search(r'[a-zA-Z]', text):
            scripts.append('latin')
        if re.search(r'[\u4e00-\u9fa5]', text):
            scripts.append('chinese')
        if re.search(r'[\u3040-\u30ff]', text):
            scripts.append('japanese')
        if re.search(r'[\uac00-\ud7af]', text):
            scripts.append('korean')
        
        # 多文字系统混合 → 较难
        if len(scripts) > 1:
            return 0.7
        
        return 0.3  # 默认较简单


class CurriculumScheduler:
    """
    课程学习调度器
    
    策略:
    1. Easy-to-Hard: 从简单样本开始
    2. Pacing Function: 控制难度增长速度
    3. Dynamic Adjustment: 根据训练损失动态调整
    """
    
    def __init__(
        self,
        dataset,
        difficulty_estimator: DifficultyEstimator = None,
        pacing_fn: str = 'linear',  # 'linear', 'quadratic', 'exponential'
        initial_easy_ratio: float = 0.3,  # 初始只用30%最简单的数据
        warmup_epochs: int = 3,  # 热身阶段的epoch数
    ):
        """
        Args:
            dataset: 数据集
            difficulty_estimator: 难度评估器
            pacing_fn: 难度增长函数
            initial_easy_ratio: 初始简单样本比例
            warmup_epochs: 热身epoch数
        """
        self.dataset = dataset
        self.estimator = difficulty_estimator or DifficultyEstimator()
        self.pacing_fn = pacing_fn
        self.initial_easy_ratio = initial_easy_ratio
        self.warmup_epochs = warmup_epochs
        
        # 保存原始索引映射（如果dataset有的话）
        self.original_indices = getattr(dataset, 'original_indices', None)
        
        # 计算所有样本的难度
        print("📚 计算样本难度...")
        self._compute_difficulties()
        
        # 按难度排序
        self._sort_by_difficulty()
    
    def _compute_difficulties(self):
        """计算所有样本的难度"""
        self.difficulties = []
        
        for i, sample in enumerate(self.dataset.samples):
            text = sample['text']
            language = sample.get('language', 'unknown')
            
            difficulty = self.estimator.estimate_difficulty(text, language)
            self.difficulties.append({
                'index': i,
                'difficulty': difficulty,
                'language': language
            })
            
            if (i + 1) % 1000 == 0:
                print(f"   进度: {i+1}/{len(self.dataset.samples)}")
        
        print(f"✓ 难度计算完成")
        
        # 统计难度分布
        diff_values = [d['difficulty'] for d in self.difficulties]
        print(f"   难度分布: min={min(diff_values):.3f}, "
              f"mean={np.mean(diff_values):.3f}, "
              f"max={max(diff_values):.3f}")
    
    def _sort_by_difficulty(self):
        """按难度排序"""
        self.difficulties.sort(key=lambda x: x['difficulty'])
        self.sorted_indices = [d['index'] for d in self.difficulties]
        
        print(f"📊 样本按难度排序完成")
        
        # 显示难度分段统计
        n_samples = len(self.sorted_indices)
        easy_cutoff = int(n_samples * 0.33)
        medium_cutoff = int(n_samples * 0.67)
        
        print(f"   简单样本 (0-0.33): {easy_cutoff} 个")
        print(f"   中等样本 (0.33-0.67): {medium_cutoff - easy_cutoff} 个")
        print(f"   困难样本 (0.67-1.0): {n_samples - medium_cutoff} 个")
    
    def get_curriculum_indices(self, epoch: int, total_epochs: int) -> List[int]:
        """
        获取当前epoch应使用的样本索引
        
        Args:
            epoch: 当前epoch (0-based)
            total_epochs: 总epoch数
            
        Returns:
            样本索引列表
        """
        n_samples = len(self.sorted_indices)
        
        # 计算当前难度比例（从initial_easy_ratio到1.0）
        if epoch < self.warmup_epochs:
            # 热身阶段：固定使用简单样本
            ratio = self.initial_easy_ratio
        else:
            # 主训练阶段：逐步增加难度
            progress = (epoch - self.warmup_epochs) / (total_epochs - self.warmup_epochs)
            
            if self.pacing_fn == 'linear':
                ratio = self.initial_easy_ratio + (1.0 - self.initial_easy_ratio) * progress
            elif self.pacing_fn == 'quadratic':
                ratio = self.initial_easy_ratio + (1.0 - self.initial_easy_ratio) * (progress ** 2)
            elif self.pacing_fn == 'exponential':
                ratio = self.initial_easy_ratio * (1.0 / self.initial_easy_ratio) ** progress
            else:
                ratio = 1.0  # 默认使用全部数据
        
        ratio = min(ratio, 1.0)
        
        # 选择样本
        n_selected = int(n_samples * ratio)
        selected_indices = self.sorted_indices[:n_selected]
        
        # 如果有原始索引映射，则映射回去
        if self.original_indices is not None:
            # selected_indices是相对于temp_dataset的索引
            # 需要映射到原始dataset的索引
            mapped_indices = [self.original_indices[idx] for idx in selected_indices]
            print(f"📖 Epoch {epoch+1}: 使用 {len(mapped_indices)}/{n_samples} 样本 "
                  f"(难度比例: {ratio:.2%})")
            return mapped_indices
        else:
            print(f"📖 Epoch {epoch+1}: 使用 {len(selected_indices)}/{n_samples} 样本 "
                  f"(难度比例: {ratio:.2%})")
            return selected_indices
    
    def get_difficulty_stats(self) -> Dict:
        """获取难度统计信息"""
        diff_values = [d['difficulty'] for d in self.difficulties]
        
        return {
            'min': float(np.min(diff_values)),
            'max': float(np.max(diff_values)),
            'mean': float(np.mean(diff_values)),
            'std': float(np.std(diff_values)),
            'quartiles': [
                float(np.percentile(diff_values, 25)),
                float(np.percentile(diff_values, 50)),
                float(np.percentile(diff_values, 75))
            ]
        }
