"""
主训练器 - 对比学习 + 课程学习
Main Trainer for Contrastive Learning + Curriculum Learning

功能:
1. 完整的训练pipeline
2. 验证与早停
3. 模型检查点
4. TensorBoard可视化
5. AMD GPU支持
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from transformers import AutoModel, AutoTokenizer, get_linear_schedule_with_warmup
from typing import Dict, List, Optional, Tuple
import os
import json
import time
from datetime import datetime
from tqdm import tqdm
import numpy as np

try:
    from torch.utils.tensorboard import SummaryWriter
    TENSORBOARD_AVAILABLE = True
except ImportError:
    TENSORBOARD_AVAILABLE = False
    print("⚠️ TensorBoard不可用，训练日志将只保存到文件")


class SentimentModel(nn.Module):
    """
    情感分析模型（带对比学习）
    
    架构:
    1. XLM-RoBERTa encoder
    2. Projection head (用于对比学习)
    3. Classification head (用于情感分类)
    """
    
    def __init__(
        self,
        model_name: str = "cardiffnlp/twitter-xlm-roberta-base-sentiment",
        num_classes: int = 3,
        projection_dim: int = 128,
        dropout: float = 0.1
    ):
        """
        Args:
            model_name: 预训练模型名称
            num_classes: 分类类别数
            projection_dim: 投影维度（用于对比学习）
            dropout: Dropout率
        """
        super(SentimentModel, self).__init__()
        
        # 加载预训练模型
        print(f"🔧 加载预训练模型: {model_name}")
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden_size = self.encoder.config.hidden_size
        
        # Projection head (对比学习)
        self.projection_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, projection_dim)
        )
        
        # Classification head (情感分类)
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, num_classes)
        )
        
        print(f"✓ 模型构建完成")
        print(f"   Encoder hidden size: {hidden_size}")
        print(f"   Projection dim: {projection_dim}")
        print(f"   Num classes: {num_classes}")
    
    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        return_features: bool = True
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        """
        前向传播
        
        Args:
            input_ids: 输入token IDs
            attention_mask: 注意力mask
            return_features: 是否返回特征（用于对比学习）
            
        Returns:
            logits: 分类logits
            features: 投影特征（如果return_features=True）
        """
        # Encoder
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # [CLS] token的表示
        cls_output = outputs.last_hidden_state[:, 0, :]  # [batch_size, hidden_size]
        
        # Classification
        logits = self.classifier(cls_output)
        
        # Projection (用于对比学习)
        if return_features:
            features = self.projection_head(cls_output)
            return logits, features
        else:
            return logits, None


class SentimentTrainer:
    """
    情感分析训练器
    """
    
    def __init__(
        self,
        model: SentimentModel,
        train_dataset,
        val_dataset,
        curriculum_scheduler,
        loss_fn,
        learning_rate: float = 2e-5,
        weight_decay: float = 0.01,
        batch_size: int = 32,
        num_epochs: int = 10,
        warmup_ratio: float = 0.1,
        device: str = 'cuda',
        output_dir: str = './checkpoints',
        log_dir: str = './logs',
        save_every: int = 1,
        eval_every: int = 1,
        early_stopping_patience: int = 3
    ):
        """
        Args:
            model: 模型
            train_dataset: 训练数据集
            val_dataset: 验证数据集
            curriculum_scheduler: 课程学习调度器
            loss_fn: 损失函数
            learning_rate: 学习率
            weight_decay: 权重衰减
            batch_size: 批次大小
            num_epochs: 训练轮数
            warmup_ratio: 预热比例
            device: 设备
            output_dir: 输出目录
            log_dir: 日志目录
            save_every: 每N个epoch保存一次
            eval_every: 每N个epoch评估一次
            early_stopping_patience: 早停耐心值
        """
        self.model = model.to(device)
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.curriculum_scheduler = curriculum_scheduler
        self.loss_fn = loss_fn
        self.batch_size = batch_size
        self.num_epochs = num_epochs
        self.device = device
        self.output_dir = output_dir
        self.log_dir = log_dir
        self.save_every = save_every
        self.eval_every = eval_every
        self.early_stopping_patience = early_stopping_patience
        
        # 创建目录
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)
        
        # 优化器
        self.optimizer = optim.AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        
        # 学习率调度器
        total_steps = (len(train_dataset) // batch_size) * num_epochs
        warmup_steps = int(total_steps * warmup_ratio)
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=total_steps
        )
        
        # TensorBoard
        if TENSORBOARD_AVAILABLE:
            self.writer = SummaryWriter(log_dir=log_dir)
        else:
            self.writer = None
        
        # 训练状态
        self.global_step = 0
        self.best_val_loss = float('inf')
        self.best_val_acc = 0.0
        self.patience_counter = 0
        
        # 训练历史
        self.train_history = {
            'loss': [],
            'acc': [],
            'lr': []
        }
        self.val_history = {
            'loss': [],
            'acc': []
        }
        
        print(f"🚀 训练器初始化完成")
        print(f"   Device: {device}")
        print(f"   Batch size: {batch_size}")
        print(f"   Num epochs: {num_epochs}")
        print(f"   Learning rate: {learning_rate}")
        print(f"   Total steps: {total_steps}")
        print(f"   Warmup steps: {warmup_steps}")
    
    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """训练一个epoch"""
        self.model.train()
        
        # 获取课程学习的样本索引
        curriculum_indices = self.curriculum_scheduler.get_curriculum_indices(
            epoch, self.num_epochs
        )
        
        # 创建子数据集
        curriculum_subset = Subset(self.train_dataset, curriculum_indices)
        train_loader = DataLoader(
            curriculum_subset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=2,
            pin_memory=True
        )
        
        total_loss = 0.0
        total_ce_loss = 0.0
        total_contrastive_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{self.num_epochs}")
        
        for batch in pbar:
            # 移动到设备
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            # 前向传播
            logits, features = self.model(input_ids, attention_mask, return_features=True)
            
            # 计算损失
            loss, loss_dict = self.loss_fn(logits, features, labels)
            
            # 反向传播
            self.optimizer.zero_grad()
            loss.backward()
            
            # 梯度裁剪
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            # 更新参数
            self.optimizer.step()
            self.scheduler.step()
            
            # 统计
            total_loss += loss_dict['total_loss']
            total_ce_loss += loss_dict['ce_loss']
            total_contrastive_loss += loss_dict['contrastive_loss']
            
            _, predicted = torch.max(logits, 1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
            
            # 更新进度条
            pbar.set_postfix({
                'loss': f"{loss_dict['total_loss']:.4f}",
                'acc': f"{100.0 * correct / total:.2f}%"
            })
            
            # TensorBoard
            if self.writer:
                self.writer.add_scalar('Train/Loss', loss_dict['total_loss'], self.global_step)
                self.writer.add_scalar('Train/CE_Loss', loss_dict['ce_loss'], self.global_step)
                self.writer.add_scalar('Train/Contrastive_Loss', loss_dict['contrastive_loss'], self.global_step)
                self.writer.add_scalar('Train/LR', self.scheduler.get_last_lr()[0], self.global_step)
            
            self.global_step += 1
        
        # Epoch统计
        avg_loss = total_loss / len(train_loader)
        avg_ce_loss = total_ce_loss / len(train_loader)
        avg_contrastive_loss = total_contrastive_loss / len(train_loader)
        accuracy = 100.0 * correct / total
        
        return {
            'loss': avg_loss,
            'ce_loss': avg_ce_loss,
            'contrastive_loss': avg_contrastive_loss,
            'accuracy': accuracy,
            'lr': self.scheduler.get_last_lr()[0]
        }
    
    def validate(self) -> Dict[str, float]:
        """验证"""
        self.model.eval()
        
        val_loader = DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=2,
            pin_memory=True
        )
        
        total_loss = 0.0
        correct = 0
        total = 0
        
        # 混淆矩阵
        num_classes = 3
        confusion_matrix = torch.zeros(num_classes, num_classes)
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Validating"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                # 前向传播
                logits, features = self.model(input_ids, attention_mask, return_features=True)
                
                # 计算损失
                loss, loss_dict = self.loss_fn(logits, features, labels)
                total_loss += loss_dict['total_loss']
                
                # 预测
                _, predicted = torch.max(logits, 1)
                correct += (predicted == labels).sum().item()
                total += labels.size(0)
                
                # 更新混淆矩阵
                for t, p in zip(labels.view(-1), predicted.view(-1)):
                    confusion_matrix[t.long(), p.long()] += 1
        
        # 统计
        avg_loss = total_loss / len(val_loader)
        accuracy = 100.0 * correct / total
        
        # 每类精确率和召回率
        per_class_metrics = {}
        for i in range(num_classes):
            tp = confusion_matrix[i, i].item()
            fp = confusion_matrix[:, i].sum().item() - tp
            fn = confusion_matrix[i, :].sum().item() - tp
            
            precision = tp / (tp + fp + 1e-12)
            recall = tp / (tp + fn + 1e-12)
            f1 = 2 * precision * recall / (precision + recall + 1e-12)
            
            per_class_metrics[f'class_{i}'] = {
                'precision': precision,
                'recall': recall,
                'f1': f1
            }
        
        return {
            'loss': avg_loss,
            'accuracy': accuracy,
            'per_class_metrics': per_class_metrics,
            'confusion_matrix': confusion_matrix.tolist()
        }
    
    def train(self):
        """完整训练流程"""
        print("\n" + "="*70)
        print("🚀 开始训练")
        print("="*70)
        
        start_time = time.time()
        
        for epoch in range(self.num_epochs):
            print(f"\n{'='*70}")
            print(f"Epoch {epoch+1}/{self.num_epochs}")
            print(f"{'='*70}")
            
            # 训练
            train_metrics = self.train_epoch(epoch)
            self.train_history['loss'].append(train_metrics['loss'])
            self.train_history['acc'].append(train_metrics['accuracy'])
            self.train_history['lr'].append(train_metrics['lr'])
            
            print(f"\n📊 训练结果:")
            print(f"   Loss: {train_metrics['loss']:.4f}")
            print(f"   CE Loss: {train_metrics['ce_loss']:.4f}")
            print(f"   Contrastive Loss: {train_metrics['contrastive_loss']:.4f}")
            print(f"   Accuracy: {train_metrics['accuracy']:.2f}%")
            print(f"   LR: {train_metrics['lr']:.2e}")
            
            # 验证
            if (epoch + 1) % self.eval_every == 0:
                val_metrics = self.validate()
                self.val_history['loss'].append(val_metrics['loss'])
                self.val_history['acc'].append(val_metrics['accuracy'])
                
                print(f"\n📊 验证结果:")
                print(f"   Loss: {val_metrics['loss']:.4f}")
                print(f"   Accuracy: {val_metrics['accuracy']:.2f}%")
                
                # 每类指标
                for class_name, metrics in val_metrics['per_class_metrics'].items():
                    print(f"   {class_name}: P={metrics['precision']:.3f}, "
                          f"R={metrics['recall']:.3f}, F1={metrics['f1']:.3f}")
                
                # TensorBoard
                if self.writer:
                    self.writer.add_scalar('Val/Loss', val_metrics['loss'], epoch)
                    self.writer.add_scalar('Val/Accuracy', val_metrics['accuracy'], epoch)
                
                # 早停检查
                if val_metrics['loss'] < self.best_val_loss:
                    self.best_val_loss = val_metrics['loss']
                    self.best_val_acc = val_metrics['accuracy']
                    self.patience_counter = 0
                    
                    # 保存最佳模型
                    self.save_checkpoint(epoch, is_best=True)
                    print(f"   ✨ 新的最佳模型！")
                else:
                    self.patience_counter += 1
                    print(f"   耐心计数: {self.patience_counter}/{self.early_stopping_patience}")
                    
                    if self.patience_counter >= self.early_stopping_patience:
                        print(f"\n⏹️ 早停触发！")
                        break
            
            # 定期保存
            if (epoch + 1) % self.save_every == 0:
                self.save_checkpoint(epoch, is_best=False)
        
        # 训练结束
        total_time = time.time() - start_time
        print(f"\n{'='*70}")
        print(f"✅ 训练完成！")
        print(f"{'='*70}")
        print(f"总时间: {total_time/60:.2f} 分钟")
        print(f"最佳验证损失: {self.best_val_loss:.4f}")
        print(f"最佳验证准确率: {self.best_val_acc:.2f}%")
        
        # 保存训练历史
        self.save_training_history()
        
        if self.writer:
            self.writer.close()
    
    def save_checkpoint(self, epoch: int, is_best: bool = False):
        """保存检查点"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'best_val_loss': self.best_val_loss,
            'best_val_acc': self.best_val_acc,
            'train_history': self.train_history,
            'val_history': self.val_history
        }
        
        if is_best:
            path = os.path.join(self.output_dir, 'best_model.pt')
            print(f"   💾 保存最佳模型: {path}")
        else:
            path = os.path.join(self.output_dir, f'checkpoint_epoch_{epoch+1}.pt')
            print(f"   💾 保存检查点: {path}")
        
        torch.save(checkpoint, path)
    
    def save_training_history(self):
        """保存训练历史"""
        history_path = os.path.join(self.output_dir, 'training_history.json')
        
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump({
                'train_history': self.train_history,
                'val_history': self.val_history,
                'best_val_loss': self.best_val_loss,
                'best_val_acc': self.best_val_acc
            }, f, indent=2)
        
        print(f"   💾 训练历史已保存: {history_path}")
    
    def load_checkpoint(self, checkpoint_path: str):
        """加载检查点"""
        print(f"📂 加载检查点: {checkpoint_path}")
        
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.best_val_loss = checkpoint['best_val_loss']
        self.best_val_acc = checkpoint['best_val_acc']
        self.train_history = checkpoint['train_history']
        self.val_history = checkpoint['val_history']
        
        print(f"✓ 检查点加载完成")
        print(f"   Epoch: {checkpoint['epoch']+1}")
        print(f"   Best Val Loss: {self.best_val_loss:.4f}")
        print(f"   Best Val Acc: {self.best_val_acc:.2f}%")
