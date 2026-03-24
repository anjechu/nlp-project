"""
集成示例 - 将训练好的模型集成到现有的NLP pipeline

演示如何:
1. 加载训练好的模型
2. 替换原有的SentimentEngine
3. 保持API兼容性
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from training.trainer import SentimentModel
import torch.nn.functional as F


class CustomSentimentEngine:
    """
    使用自定义训练模型的情感引擎
    
    与原有SentimentEngine保持API兼容
    """
    
    def __init__(self, checkpoint_path: str, device='cuda'):
        """
        Args:
            checkpoint_path: 训练好的模型检查点路径
            device: 设备
        """
        print(f"❤️ 初始化自定义情感模型...")
        
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        
        # 加载tokenizer
        model_name = "cardiffnlp/twitter-xlm-roberta-base-sentiment"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # 加载训练好的模型
        self.model = SentimentModel(
            model_name=model_name,
            num_classes=3,
            projection_dim=128
        )
        
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        print(f"✓ 自定义情感模型加载完成 (设备: {self.device})")
        if 'best_val_acc' in checkpoint:
            print(f"   最佳验证准确率: {checkpoint['best_val_acc']:.2f}%")
    
    def analyze(self, texts, batch_size=32, progress_callback=None):
        """
        分析情感（与原有API兼容）
        
        Args:
            texts: 文本列表
            batch_size: 批次大小
            progress_callback: 进度回调函数
            
        Returns:
            情感分数列表 (范围: -1 到 1)
        """
        results = []
        total = len(texts)
        
        if str(self.device) == 'cpu':
            batch_size = 16
        
        for i in range(0, total, batch_size):
            batch_texts = texts[i : i + batch_size]
            
            try:
                # Tokenize
                inputs = self.tokenizer(
                    batch_texts,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=128
                ).to(self.device)
                
                # 预测
                with torch.no_grad():
                    logits, _ = self.model(
                        inputs['input_ids'],
                        inputs['attention_mask'],
                        return_features=False
                    )
                    scores = F.softmax(logits, dim=1)
                
                # 转换为情感分数 (positive - negative)
                scores_cpu = scores.cpu().numpy()
                for score in scores_cpu:
                    # score[0]=negative, score[1]=neutral, score[2]=positive
                    sentiment_score = float(score[2] - score[0])
                    results.append(sentiment_score)
                
                # 进度回调
                if progress_callback:
                    progress = (i + len(batch_texts)) / total
                    progress_callback(progress)
                    
            except Exception as e:
                print(f"⚠️ Batch Error: {e}")
                results.extend([0.0] * len(batch_texts))
        
        return results


def integrate_custom_model_example():
    """
    集成示例：如何在现有代码中使用自定义模型
    """
    # 方法1: 直接替换
    from nlp import NLPProcessor
    
    # 创建处理器
    processor = NLPProcessor()
    
    # 替换情感引擎为自定义训练的模型
    processor.sentiment_engine = CustomSentimentEngine(
        checkpoint_path='./checkpoints/best_model.pt',
        device='cuda'
    )
    
    # 使用
    test_texts = [
        "这个游戏真的很棒！",
        "Terrible game, waste of money.",
        "このゲームは素晴らしい！"
    ]
    
    sentiments = processor.sentiment_engine.analyze(test_texts)
    
    for text, score in zip(test_texts, sentiments):
        label = "正面" if score > 0.2 else "负面" if score < -0.2 else "中性"
        print(f"文本: {text}")
        print(f"情感分数: {score:.3f} ({label})")
        print()


def create_standalone_sentiment_analyzer():
    """
    创建独立的情感分析器
    """
    class StandaloneSentimentAnalyzer:
        """独立的情感分析器"""
        
        def __init__(self, checkpoint_path):
            self.engine = CustomSentimentEngine(checkpoint_path)
        
        def analyze_text(self, text: str) -> dict:
            """
            分析单条文本
            
            Returns:
                {
                    'score': float,  # -1 到 1
                    'label': str,    # 'positive', 'neutral', 'negative'
                    'confidence': float  # 0 到 1
                }
            """
            scores = self.engine.analyze([text])
            score = scores[0]
            
            # 确定标签
            if score > 0.2:
                label = 'positive'
            elif score < -0.2:
                label = 'negative'
            else:
                label = 'neutral'
            
            # 计算置信度
            confidence = abs(score)
            
            return {
                'score': score,
                'label': label,
                'confidence': confidence
            }
        
        def analyze_batch(self, texts: list) -> list:
            """批量分析"""
            scores = self.engine.analyze(texts)
            
            results = []
            for text, score in zip(texts, scores):
                if score > 0.2:
                    label = 'positive'
                elif score < -0.2:
                    label = 'negative'
                else:
                    label = 'neutral'
                
                results.append({
                    'text': text,
                    'score': score,
                    'label': label,
                    'confidence': abs(score)
                })
            
            return results
    
    return StandaloneSentimentAnalyzer


if __name__ == '__main__':
    print("=" * 70)
    print("🔌 集成示例 - 使用自定义训练的情感分析模型")
    print("=" * 70)
    
    # 示例1: 直接使用自定义引擎
    print("\n📝 示例1: 直接使用")
    try:
        engine = CustomSentimentEngine('./checkpoints/best_model.pt')
        
        test_texts = [
            "This game is amazing!",
            "这个游戏很垃圾",
            "まあまあです",
        ]
        
        scores = engine.analyze(test_texts)
        
        for text, score in zip(test_texts, scores):
            label = "正面" if score > 0.2 else "负面" if score < -0.2 else "中性"
            print(f"   文本: {text}")
            print(f"   分数: {score:.3f} ({label})")
    except Exception as e:
        print(f"   ⚠️ 需要先训练模型: {e}")
    
    # 示例2: 独立分析器
    print("\n📝 示例2: 独立分析器")
    print("   (需要先运行训练脚本生成模型)")
    
    # 示例3: 集成到现有pipeline
    print("\n📝 示例3: 集成到NLP pipeline")
    print("   参见 integrate_custom_model_example() 函数")
    
    print("\n✅ 集成示例完成")
    print("\n💡 提示:")
    print("   1. 先运行训练: python train_sentiment.py --data_path data.json")
    print("   2. 然后使用: engine = CustomSentimentEngine('./checkpoints/best_model.pt')")
    print("   3. 分析: scores = engine.analyze(texts)")
