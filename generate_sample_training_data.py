#!/usr/bin/env python3
"""
生成示例训练数据
Generate sample training data for sentiment analysis

生成多语言的Steam风格评论数据，用于测试训练流程
"""

import json
import random

# 多语言示例评论
sample_reviews = {
    'positive_english': [
        "This game is absolutely amazing! Best purchase ever!",
        "Fantastic gameplay and beautiful graphics. Highly recommended!",
        "Perfect game! Love everything about it!",
        "Outstanding! This is exactly what I was looking for.",
        "Brilliant game design. Can't stop playing!",
        "Excellent experience. Worth every penny!",
        "Amazing storyline and great characters!",
        "Best game I've played in years!",
        "Superb quality. Totally satisfied!",
        "Wonderful game! Highly addictive!",
    ],
    
    'negative_english': [
        "Terrible game. Complete waste of money.",
        "Awful experience. So many bugs and crashes.",
        "Worst game ever. Don't buy it!",
        "Horrible gameplay. Very disappointed.",
        "Disaster! Nothing works properly.",
        "Poor quality. Not worth the price.",
        "Frustrating and buggy. Stay away!",
        "Terrible graphics and boring gameplay.",
        "Awful design. Regret buying this.",
        "Disappointing. Expected much better.",
    ],
    
    'neutral_english': [
        "It's okay. Nothing special but decent.",
        "The game is fine. Not great, not terrible.",
        "Average game. Could be better.",
        "It's alright. Has some good and bad parts.",
        "Decent but nothing extraordinary.",
        "The game works as expected. Nothing more.",
        "Okay for the price. Not amazing though.",
        "It's fine. Just average.",
        "Acceptable quality. Nothing impressive.",
        "The game is okay. Could use improvements.",
    ],
    
    'positive_chinese': [
        "这个游戏真的超级棒！强烈推荐！",
        "太好玩了！画面精美，玩法出色！",
        "神作！完全停不下来！",
        "非常优秀的游戏，值得购买！",
        "超棒的体验！完美！",
        "剧情感人，画面精致，好评！",
        "玩法创新，内容丰富，强推！",
        "最好的游戏之一！",
        "品质卓越，物超所值！",
        "太精彩了！五星好评！",
    ],
    
    'negative_chinese': [
        "太垃圾了，完全不值得买。",
        "差评！Bug太多，经常崩溃。",
        "史上最烂的游戏，别买！",
        "太失望了，完全浪费钱。",
        "烂透了！玩不下去！",
        "画面差，玩法无聊，差评。",
        "优化太差，体验极差。",
        "坑爹游戏，后悔购买。",
        "太糟糕了，不推荐。",
        "质量堪忧，不值这个价格。",
    ],
    
    'neutral_chinese': [
        "还行吧，没什么特别的。",
        "一般般，不算好也不算差。",
        "马马虎虎，凑合能玩。",
        "还可以，有优点也有缺点。",
        "普通水平，中规中矩。",
        "不错，但也没有很惊艳。",
        "勉强及格，可以改进。",
        "尚可，符合预期。",
        "还行，不是特别出色。",
        "一般，可以接受。",
    ],
    
    'positive_japanese': [
        "このゲームは素晴らしい！最高です！",
        "完璧なゲーム！とても楽しい！",
        "神ゲー！超おすすめ！",
        "素晴らしいクオリティ！",
        "最高の体験！大満足！",
        "グラフィックが美しい！面白い！",
        "傑作！やめられない！",
        "優れたゲームデザイン！",
        "素晴らしいストーリー！",
        "最高のゲーム体験！",
    ],
    
    'negative_japanese': [
        "最悪のゲーム。買わない方がいい。",
        "ひどい。バグだらけ。",
        "クソゲー。時間の無駄。",
        "がっかりした。期待外れ。",
        "つまらない。つまらない。",
        "品質が悪い。残念。",
        "最悪の体験。おすすめしない。",
        "ひどいゲームデザイン。",
        "退屈。飽きた。",
        "失敗作。買って後悔。",
    ],
    
    'neutral_japanese': [
        "まあまあです。普通。",
        "悪くないけど、特別でもない。",
        "そこそこ。平凡。",
        "普通のゲーム。可もなく不可もなく。",
        "まぁまぁです。期待通り。",
        "悪くはない。普通。",
        "そこそこ楽しめる。",
        "普通。特に印象に残らない。",
        "まあまあの出来。",
        "可もなく不可もなく。",
    ],
    
    # 跨文化难例（混合语言、委婉表达）
    'hard_mixed': [
        "游戏还行吧，but有点boring to be honest",
        "Graphics良い but gameplay微妙",
        "まあまあかな。没有特别好也没有特别差。",
        "It's okay I guess, 不过还可以再改进一下",
        "還不錯啦，although有些bug需要fix",
        "ゲームは普通。Nothing special但也not bad",
        "还可以吧，虽然not perfect但acceptable",
        "そこそこ楽しい。勉強になった感じ。",
    ]
}

def generate_training_data(num_samples: int = 1000):
    """
    生成训练数据
    
    Args:
        num_samples: 生成的样本数量
        
    Returns:
        包含评论的列表
    """
    data = []
    
    # 计算每类样本数量
    samples_per_category = num_samples // 10
    
    categories = [
        ('positive_english', 'english', 2),
        ('negative_english', 'english', 0),
        ('neutral_english', 'english', 1),
        ('positive_chinese', 'schinese', 2),
        ('negative_chinese', 'schinese', 0),
        ('neutral_chinese', 'schinese', 1),
        ('positive_japanese', 'japanese', 2),
        ('negative_japanese', 'japanese', 0),
        ('neutral_japanese', 'japanese', 1),
        ('hard_mixed', 'mixed', 1),  # 困难样本
    ]
    
    idx = 0
    for category, language, sentiment in categories:
        reviews = sample_reviews[category]
        
        # 生成该类别的样本
        for i in range(samples_per_category):
            # 随机选择一条评论（可重复）
            review_text = random.choice(reviews)
            
            # 随机添加一些变化（模拟真实数据）
            if random.random() < 0.3:
                # 30%概率添加额外的emoji或标点
                emojis = ['!', '!!', '...', '!!!', '?', '!?']
                review_text += random.choice(emojis)
            
            data.append({
                'id': idx,
                'text': review_text,
                'language': language,
                'sentiment': sentiment,
                'label': sentiment  # 同时提供label字段
            })
            
            idx += 1
    
    # 打乱顺序
    random.shuffle(data)
    
    return data

def main():
    """主函数"""
    print("🎲 生成示例训练数据...")
    
    # 生成不同规模的数据集
    datasets = [
        (100, 'sample_train_small.json'),
        (1000, 'sample_train_medium.json'),
        (5000, 'sample_train_large.json')
    ]
    
    for num_samples, filename in datasets:
        print(f"\n📝 生成 {filename}...")
        data = generate_training_data(num_samples)
        
        # 统计
        label_counts = {}
        for review in data:
            label = review['sentiment']
            label_counts[label] = label_counts.get(label, 0) + 1
        
        print(f"   总样本数: {len(data)}")
        print(f"   标签分布: {label_counts}")
        
        # 保存
        output = {
            'comments': data,
            'metadata': {
                'num_samples': len(data),
                'label_distribution': label_counts,
                'languages': list(set(r['language'] for r in data))
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"   ✓ 已保存: {filename}")
    
    print("\n✅ 完成！")
    print("\n💡 使用示例:")
    print("   python train_sentiment.py --data_path sample_train_small.json --epochs 5")
    print("   python train_sentiment.py --data_path sample_train_medium.json --epochs 10")
    print("   python train_sentiment.py --data_path sample_train_large.json --epochs 15")

if __name__ == '__main__':
    main()
