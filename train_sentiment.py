#!/usr/bin/env python3
"""
训练脚本 - 对比学习 + 课程学习
Training Script for Contrastive Learning + Curriculum Learning

使用方法:
    python train_sentiment.py --data_path <path_to_data.json> --epochs 10

示例:
    python train_sentiment.py --data_path sample_comments.json --epochs 10 --batch_size 32
"""

import argparse
import torch
from transformers import AutoTokenizer
from training.data_loader import SteamReviewDataset
from training.curriculum import CurriculumScheduler, DifficultyEstimator
from training.losses import CombinedLoss
from training.trainer import SentimentModel, SentimentTrainer
import os


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='训练情感分析模型（对比学习+课程学习）')
    
    # 数据参数
    parser.add_argument('--data_path', type=str, required=True,
                       help='训练数据路径（JSON格式）')
    parser.add_argument('--val_split', type=float, default=0.1,
                       help='验证集比例（默认：0.1）')
    parser.add_argument('--auto_label', action='store_true',
                       help='是否自动标注数据（使用预训练模型）')
    parser.add_argument('--min_text_length', type=int, default=10,
                       help='最小文本长度（默认：10）')
    
    # 模型参数
    parser.add_argument('--model_name', type=str, 
                       default='cardiffnlp/twitter-xlm-roberta-base-sentiment',
                       help='预训练模型名称')
    parser.add_argument('--projection_dim', type=int, default=128,
                       help='投影维度（对比学习，默认：128）')
    parser.add_argument('--dropout', type=float, default=0.1,
                       help='Dropout率（默认：0.1）')
    
    # 训练参数
    parser.add_argument('--batch_size', type=int, default=32,
                       help='批次大小（默认：32）')
    parser.add_argument('--epochs', type=int, default=10,
                       help='训练轮数（默认：10）')
    parser.add_argument('--learning_rate', type=float, default=2e-5,
                       help='学习率（默认：2e-5）')
    parser.add_argument('--weight_decay', type=float, default=0.01,
                       help='权重衰减（默认：0.01）')
    parser.add_argument('--warmup_ratio', type=float, default=0.1,
                       help='预热比例（默认：0.1）')
    
    # 损失函数参数
    parser.add_argument('--temperature', type=float, default=0.07,
                       help='对比学习温度（默认：0.07）')
    parser.add_argument('--alpha', type=float, default=0.5,
                       help='对比损失权重（0-1，默认：0.5）')
    parser.add_argument('--label_smoothing', type=float, default=0.1,
                       help='标签平滑（默认：0.1）')
    
    # 课程学习参数
    parser.add_argument('--pacing_fn', type=str, default='linear',
                       choices=['linear', 'quadratic', 'exponential'],
                       help='课程学习难度增长函数（默认：linear）')
    parser.add_argument('--initial_easy_ratio', type=float, default=0.3,
                       help='初始简单样本比例（默认：0.3）')
    parser.add_argument('--warmup_epochs', type=int, default=3,
                       help='课程学习热身轮数（默认：3）')
    
    # 其他参数
    parser.add_argument('--device', type=str, default='cuda',
                       help='设备（cuda/cpu，默认：cuda）')
    parser.add_argument('--output_dir', type=str, default='./checkpoints',
                       help='输出目录（默认：./checkpoints）')
    parser.add_argument('--log_dir', type=str, default='./logs',
                       help='日志目录（默认：./logs）')
    parser.add_argument('--save_every', type=int, default=1,
                       help='每N个epoch保存一次（默认：1）')
    parser.add_argument('--eval_every', type=int, default=1,
                       help='每N个epoch评估一次（默认：1）')
    parser.add_argument('--early_stopping_patience', type=int, default=3,
                       help='早停耐心值（默认：3）')
    parser.add_argument('--seed', type=int, default=42,
                       help='随机种子（默认：42）')
    
    return parser.parse_args()


def set_seed(seed: int):
    """设置随机种子"""
    import random
    import numpy as np
    
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def main():
    """主函数"""
    # 解析参数
    args = parse_args()
    
    # 设置随机种子
    set_seed(args.seed)
    
    # 打印配置
    print("\n" + "="*70)
    print("🚀 情感分析训练 - 对比学习 + 课程学习")
    print("="*70)
    print("\n📋 配置:")
    for arg, value in vars(args).items():
        print(f"   {arg}: {value}")
    print()
    
    # 检查设备
    if args.device == 'cuda' and not torch.cuda.is_available():
        print("⚠️ CUDA不可用，切换到CPU")
        args.device = 'cpu'
    print(f"🖥️ 使用设备: {args.device}")
    
    # 加载tokenizer
    print(f"\n📚 加载tokenizer: {args.model_name}")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    
    # 加载数据集
    print(f"\n📂 加载数据集: {args.data_path}")
    full_dataset = SteamReviewDataset(
        data_path=args.data_path,
        tokenizer=tokenizer,
        auto_label=args.auto_label,
        min_text_length=args.min_text_length
    )
    
    # 划分训练集和验证集
    print(f"\n✂️ 划分数据集...")
    dataset_size = len(full_dataset)
    val_size = int(dataset_size * args.val_split)
    train_size = dataset_size - val_size
    
    train_dataset, val_dataset = torch.utils.data.random_split(
        full_dataset, 
        [train_size, val_size],
        generator=torch.Generator().manual_seed(args.seed)
    )
    
    print(f"   训练集: {len(train_dataset)} 样本")
    print(f"   验证集: {len(val_dataset)} 样本")
    
    # 创建课程学习调度器
    print(f"\n📚 初始化课程学习调度器...")
    difficulty_estimator = DifficultyEstimator()
    
    # 注意：需要访问train_dataset的原始数据
    # 创建一个临时的完整训练数据集对象用于课程学习
    train_samples = [full_dataset.samples[i] for i in train_dataset.indices]
    
    # 创建临时数据集对象
    class TempDataset:
        def __init__(self, samples, original_indices):
            self.samples = samples
            self.original_indices = original_indices  # 保存原始索引映射
    
    temp_dataset = TempDataset(train_samples, list(train_dataset.indices))
    
    curriculum_scheduler = CurriculumScheduler(
        dataset=temp_dataset,
        difficulty_estimator=difficulty_estimator,
        pacing_fn=args.pacing_fn,
        initial_easy_ratio=args.initial_easy_ratio,
        warmup_epochs=args.warmup_epochs
    )
    
    # 打印难度统计
    diff_stats = curriculum_scheduler.get_difficulty_stats()
    print(f"\n📊 样本难度统计:")
    print(f"   最小: {diff_stats['min']:.3f}")
    print(f"   平均: {diff_stats['mean']:.3f}")
    print(f"   最大: {diff_stats['max']:.3f}")
    print(f"   标准差: {diff_stats['std']:.3f}")
    print(f"   四分位数: {diff_stats['quartiles']}")
    
    # 创建模型
    print(f"\n🔧 创建模型...")
    model = SentimentModel(
        model_name=args.model_name,
        num_classes=3,
        projection_dim=args.projection_dim,
        dropout=args.dropout
    )
    
    # 创建损失函数
    print(f"\n⚖️ 创建损失函数...")
    loss_fn = CombinedLoss(
        num_classes=3,
        temperature=args.temperature,
        alpha=args.alpha,
        label_smoothing=args.label_smoothing
    )
    print(f"   对比损失权重: {args.alpha}")
    print(f"   分类损失权重: {1-args.alpha}")
    
    # 创建训练器
    print(f"\n🎯 创建训练器...")
    trainer = SentimentTrainer(
        model=model,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        curriculum_scheduler=curriculum_scheduler,
        loss_fn=loss_fn,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        batch_size=args.batch_size,
        num_epochs=args.epochs,
        warmup_ratio=args.warmup_ratio,
        device=args.device,
        output_dir=args.output_dir,
        log_dir=args.log_dir,
        save_every=args.save_every,
        eval_every=args.eval_every,
        early_stopping_patience=args.early_stopping_patience
    )
    
    # 开始训练
    trainer.train()
    
    print("\n" + "="*70)
    print("✅ 训练完成！")
    print("="*70)
    print(f"\n📁 输出文件:")
    print(f"   检查点: {args.output_dir}")
    print(f"   日志: {args.log_dir}")
    print(f"\n💡 提示:")
    print(f"   - 查看训练日志: tensorboard --logdir {args.log_dir}")
    print(f"   - 加载最佳模型: {os.path.join(args.output_dir, 'best_model.pt')}")
    print()


if __name__ == '__main__':
    main()
