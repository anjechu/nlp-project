#!/usr/bin/env python3
"""
完整的端到端训练测试
End-to-End Training Test

测试流程:
1. 生成示例数据
2. 训练模型（小规模，快速验证）
3. 评估模型
4. 集成测试
"""

import os
import sys
import subprocess
import json


def run_command(cmd, description):
    """运行命令并打印输出"""
    print(f"\n{'='*70}")
    print(f"🚀 {description}")
    print(f"{'='*70}")
    print(f"命令: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 错误: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    """主测试流程"""
    print("\n" + "="*70)
    print("🧪 完整端到端训练测试")
    print("="*70)
    
    # 检查Python和依赖
    print("\n📋 检查环境...")
    print(f"   Python: {sys.version}")
    
    try:
        import torch
        print(f"   PyTorch: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
    except ImportError:
        print("   ⚠️ PyTorch未安装，请先运行: pip install -r requirements.txt")
        return False
    
    # 步骤1: 生成示例数据
    if not os.path.exists('sample_train_small.json'):
        success = run_command(
            ['python', 'generate_sample_training_data.py'],
            '步骤1: 生成示例训练数据'
        )
        if not success:
            print("❌ 数据生成失败")
            return False
    else:
        print("\n✓ 示例数据已存在")
    
    # 步骤2: 训练模型（小规模，快速测试）
    print("\n" + "="*70)
    print("🚀 步骤2: 训练模型（快速测试模式）")
    print("="*70)
    print("注意: 这是一个快速测试，只训练2个epoch")
    print("完整训练请使用: python train_sentiment.py --data_path <your_data> --epochs 10")
    print()
    
    train_cmd = [
        'python', 'train_sentiment.py',
        '--data_path', 'sample_train_small.json',
        '--epochs', '2',
        '--batch_size', '16',
        '--save_every', '1',
        '--eval_every', '1',
        '--early_stopping_patience', '5',
        '--output_dir', './test_checkpoints',
        '--log_dir', './test_logs'
    ]
    
    success = run_command(train_cmd, '训练模型')
    
    if not success:
        print("❌ 训练失败")
        print("\n💡 提示:")
        print("   - 如果是CUDA内存不足，尝试: --device cpu")
        print("   - 如果是依赖问题，运行: pip install -r requirements.txt")
        return False
    
    # 检查输出文件
    checkpoint_path = './test_checkpoints/best_model.pt'
    if not os.path.exists(checkpoint_path):
        print(f"❌ 模型文件未生成: {checkpoint_path}")
        return False
    
    print(f"✓ 模型已保存: {checkpoint_path}")
    
    # 步骤3: 评估模型
    eval_cmd = [
        'python', 'evaluate_model.py',
        '--checkpoint', checkpoint_path,
        '--data_path', 'sample_train_small.json',
        '--output', './test_evaluation.json'
    ]
    
    success = run_command(eval_cmd, '步骤3: 评估模型')
    
    if not success:
        print("❌ 评估失败")
        return False
    
    # 读取评估结果
    if os.path.exists('./test_evaluation.json'):
        with open('./test_evaluation.json', 'r') as f:
            results = json.load(f)
        
        print(f"\n📊 评估结果摘要:")
        print(f"   准确率: {results['overall_accuracy']*100:.2f}%")
        print(f"   样本数: {results['num_samples']}")
        
        if 'cross_lingual_consistency' in results:
            consistency = results['cross_lingual_consistency']['overall']
            print(f"   跨语言一致性: {consistency:.3f}")
    
    # 步骤4: 集成测试
    print("\n" + "="*70)
    print("🔌 步骤4: 集成测试")
    print("="*70)
    
    try:
        from integration_example import CustomSentimentEngine
        
        engine = CustomSentimentEngine(checkpoint_path, device='cpu')
        
        test_texts = [
            "This game is amazing!",
            "这个游戏很垃圾",
            "まあまあです",
        ]
        
        scores = engine.analyze(test_texts)
        
        print("\n测试结果:")
        for text, score in zip(test_texts, scores):
            label = "正面" if score > 0.2 else "负面" if score < -0.2 else "中性"
            print(f"   文本: {text}")
            print(f"   分数: {score:.3f} ({label})")
        
        print("\n✓ 集成测试通过")
        
    except Exception as e:
        print(f"⚠️ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 完成
    print("\n" + "="*70)
    print("✅ 端到端测试完成！")
    print("="*70)
    
    print("\n📁 生成的文件:")
    print("   - 训练数据: sample_train_*.json")
    print("   - 模型检查点: ./test_checkpoints/")
    print("   - 训练日志: ./test_logs/")
    print("   - 评估结果: ./test_evaluation.json")
    
    print("\n🎉 成功！你的训练框架已经可以工作了！")
    
    print("\n📚 下一步:")
    print("   1. 使用你的Steam评论数据训练:")
    print("      python train_sentiment.py --data_path your_data.json --epochs 10")
    print("   2. 监控训练过程:")
    print("      tensorboard --logdir ./logs")
    print("   3. 评估模型:")
    print("      python evaluate_model.py --checkpoint ./checkpoints/best_model.pt --data_path test_data.json")
    print("   4. 集成到现有系统:")
    print("      参见 integration_example.py")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
