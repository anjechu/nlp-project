#!/usr/bin/env python3
"""
模型评估脚本
Evaluation script for trained sentiment analysis model

评估指标:
- 准确率 (Accuracy)
- 精确率、召回率、F1分数 (Precision, Recall, F1)
- 混淆矩阵 (Confusion Matrix)
- 跨语言一致性 (Cross-lingual Consistency)
"""

import argparse
import torch
import numpy as np
from transformers import AutoTokenizer
from training.data_loader import SteamReviewDataset
from training.trainer import SentimentModel
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix
import json
from collections import defaultdict
from tqdm import tqdm


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='评估训练好的情感分析模型')
    
    parser.add_argument('--checkpoint', type=str, required=True,
                       help='模型检查点路径')
    parser.add_argument('--data_path', type=str, required=True,
                       help='测试数据路径（JSON格式）')
    parser.add_argument('--model_name', type=str,
                       default='cardiffnlp/twitter-xlm-roberta-base-sentiment',
                       help='预训练模型名称')
    parser.add_argument('--batch_size', type=int, default=32,
                       help='批次大小')
    parser.add_argument('--device', type=str, default='cuda',
                       help='设备（cuda/cpu）')
    parser.add_argument('--output', type=str, default='evaluation_results.json',
                       help='输出文件路径')
    
    return parser.parse_args()


def evaluate_model(model, dataset, batch_size, device):
    """
    评估模型
    
    Returns:
        results: 评估结果字典
    """
    model.eval()
    
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=2
    )
    
    all_predictions = []
    all_labels = []
    all_languages = []
    all_texts = []
    
    print("📊 评估中...")
    with torch.no_grad():
        for batch in tqdm(dataloader):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels']
            
            # 预测
            logits, _ = model(input_ids, attention_mask, return_features=False)
            predictions = torch.argmax(logits, dim=1).cpu().numpy()
            
            all_predictions.extend(predictions)
            all_labels.extend(labels.numpy())
            all_languages.extend(batch['language'])
            all_texts.extend(batch['text'])
    
    all_predictions = np.array(all_predictions)
    all_labels = np.array(all_labels)
    
    # 计算基础指标
    accuracy = (all_predictions == all_labels).mean()
    
    # 分类报告
    report = classification_report(
        all_labels,
        all_predictions,
        target_names=['Negative', 'Neutral', 'Positive'],
        output_dict=True
    )
    
    # 混淆矩阵
    cm = confusion_matrix(all_labels, all_predictions)
    
    # 按语言统计
    lang_stats = defaultdict(lambda: {'correct': 0, 'total': 0})
    for pred, label, lang in zip(all_predictions, all_labels, all_languages):
        lang_stats[lang]['total'] += 1
        if pred == label:
            lang_stats[lang]['correct'] += 1
    
    lang_accuracy = {
        lang: stats['correct'] / stats['total']
        for lang, stats in lang_stats.items()
    }
    
    # 跨语言一致性（计算不同语言相同情感的预测一致性）
    cross_lingual_consistency = compute_cross_lingual_consistency(
        all_predictions, all_labels, all_languages
    )
    
    results = {
        'overall_accuracy': float(accuracy),
        'classification_report': report,
        'confusion_matrix': cm.tolist(),
        'language_accuracy': lang_accuracy,
        'cross_lingual_consistency': cross_lingual_consistency,
        'num_samples': len(all_labels),
        'language_distribution': dict(Counter(all_languages))
    }
    
    return results, all_predictions, all_labels, all_texts


def compute_cross_lingual_consistency(predictions, labels, languages):
    """
    计算跨语言一致性
    
    对于每个标签类别，计算不同语言预测的一致性
    """
    from collections import Counter
    
    # 按真实标签分组
    label_groups = defaultdict(lambda: defaultdict(list))
    for pred, label, lang in zip(predictions, labels, languages):
        label_groups[label][lang].append(pred)
    
    consistencies = {}
    
    for label, lang_preds in label_groups.items():
        # 计算该标签下，不同语言预测为该标签的比例
        label_consistencies = []
        for lang, preds in lang_preds.items():
            # 预测正确率
            correct_rate = sum(p == label for p in preds) / len(preds)
            label_consistencies.append(correct_rate)
        
        if label_consistencies:
            # 标准差越小，一致性越高
            std = np.std(label_consistencies)
            mean = np.mean(label_consistencies)
            
            consistencies[int(label)] = {
                'mean_accuracy': float(mean),
                'std': float(std),
                'consistency_score': float(1.0 - std)  # 1 - std作为一致性分数
            }
    
    # 总体一致性
    if consistencies:
        overall_consistency = np.mean([v['consistency_score'] for v in consistencies.values()])
    else:
        overall_consistency = 0.0
    
    return {
        'per_label': consistencies,
        'overall': float(overall_consistency)
    }


def print_results(results):
    """打印评估结果"""
    print("\n" + "="*70)
    print("📊 评估结果")
    print("="*70)
    
    print(f"\n🎯 总体准确率: {results['overall_accuracy']*100:.2f}%")
    print(f"📝 样本数量: {results['num_samples']}")
    
    print(f"\n📈 分类报告:")
    report = results['classification_report']
    for label in ['Negative', 'Neutral', 'Positive']:
        if label in report:
            metrics = report[label]
            print(f"   {label:10s}: P={metrics['precision']:.3f}, "
                  f"R={metrics['recall']:.3f}, F1={metrics['f1-score']:.3f}, "
                  f"Support={int(metrics['support'])}")
    
    print(f"\n🌍 各语言准确率:")
    for lang, acc in sorted(results['language_accuracy'].items()):
        count = results['language_distribution'].get(lang, 0)
        print(f"   {lang:15s}: {acc*100:.2f}% ({count} samples)")
    
    print(f"\n🔄 跨语言一致性:")
    consistency = results['cross_lingual_consistency']
    print(f"   总体一致性分数: {consistency['overall']:.3f}")
    for label, metrics in consistency['per_label'].items():
        label_name = ['Negative', 'Neutral', 'Positive'][label]
        print(f"   {label_name:10s}: mean={metrics['mean_accuracy']:.3f}, "
              f"std={metrics['std']:.3f}, consistency={metrics['consistency_score']:.3f}")
    
    print(f"\n📊 混淆矩阵:")
    cm = np.array(results['confusion_matrix'])
    labels = ['Neg', 'Neu', 'Pos']
    print("        " + "  ".join(f"{l:>5s}" for l in labels))
    for i, row in enumerate(cm):
        print(f"   {labels[i]:5s}" + "".join(f"{val:>7d}" for val in row))


def compare_with_baseline(results, baseline_checkpoint=None):
    """
    与基线模型对比
    
    Args:
        results: 当前模型的结果
        baseline_checkpoint: 基线模型检查点路径
    """
    if baseline_checkpoint is None:
        print("\n💡 提示: 使用 --baseline 参数可以与基线模型对比")
        return
    
    # TODO: 实现基线模型对比
    print("\n📊 基线模型对比:")
    print("   功能开发中...")


def main():
    """主函数"""
    args = parse_args()
    
    # 检查设备
    if args.device == 'cuda' and not torch.cuda.is_available():
        print("⚠️ CUDA不可用，切换到CPU")
        args.device = 'cpu'
    
    print("\n" + "="*70)
    print("🔍 模型评估")
    print("="*70)
    print(f"\n📋 配置:")
    print(f"   检查点: {args.checkpoint}")
    print(f"   数据: {args.data_path}")
    print(f"   设备: {args.device}")
    print()
    
    # 加载tokenizer
    print(f"📚 加载tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    
    # 加载数据集
    print(f"📂 加载测试数据...")
    dataset = SteamReviewDataset(
        data_path=args.data_path,
        tokenizer=tokenizer,
        auto_label=False  # 评估数据应该有标签
    )
    
    # 加载模型
    print(f"🔧 加载模型...")
    model = SentimentModel(
        model_name=args.model_name,
        num_classes=3,
        projection_dim=128
    )
    
    checkpoint = torch.load(args.checkpoint, map_location=args.device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(args.device)
    model.eval()
    
    print(f"✓ 模型加载完成")
    if 'epoch' in checkpoint:
        print(f"   Epoch: {checkpoint['epoch']+1}")
    if 'best_val_acc' in checkpoint:
        print(f"   训练时最佳验证准确率: {checkpoint['best_val_acc']:.2f}%")
    
    # 评估
    results, predictions, labels, texts = evaluate_model(
        model, dataset, args.batch_size, args.device
    )
    
    # 打印结果
    print_results(results)
    
    # 保存结果
    print(f"\n💾 保存结果到: {args.output}")
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 保存预测详情
    detail_output = args.output.replace('.json', '_details.json')
    print(f"💾 保存详细预测到: {detail_output}")
    
    details = []
    for text, pred, label, lang in zip(texts, predictions, labels, all_languages):
        details.append({
            'text': text,
            'predicted': int(pred),
            'true_label': int(label),
            'language': lang,
            'correct': bool(pred == label)
        })
    
    with open(detail_output, 'w', encoding='utf-8') as f:
        json.dump(details, f, indent=2, ensure_ascii=False)
    
    print("\n✅ 评估完成！")


if __name__ == '__main__':
    from collections import Counter
    main()
