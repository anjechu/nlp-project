"""
Supervised Contrastive Loss for Sentiment Analysis

基于以下论文:
- "Supervised Contrastive Learning" (Khosla et al., NeurIPS 2020)
- "A Simple Framework for Contrastive Learning of Visual Representations" (Chen et al., ICML 2020)

核心思想:
- 拉近同类情感的表示（positive pairs）
- 推远异类情感的表示（negative pairs）
- 支持多个正样本（one anchor, multiple positives）
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class SupervisedContrastiveLoss(nn.Module):
    """
    Supervised Contrastive Loss
    
    公式:
    L = -log [ Σ exp(z·z+/τ) / Σ exp(z·z-/τ) ]
    
    其中:
    - z: anchor的表示
    - z+: 正样本的表示 (相同标签)
    - z-: 负样本的表示 (不同标签)
    - τ: 温度参数
    """
    
    def __init__(
        self,
        temperature: float = 0.07,
        base_temperature: float = 0.07,
        contrast_mode: str = 'all'  # 'all' or 'one'
    ):
        """
        Args:
            temperature: 温度参数（越小，对比越强）
            base_temperature: 基础温度参数
            contrast_mode: 对比模式
                - 'all': 使用所有正样本
                - 'one': 每次只使用一个正样本
        """
        super(SupervisedContrastiveLoss, self).__init__()
        self.temperature = temperature
        self.base_temperature = base_temperature
        self.contrast_mode = contrast_mode
    
    def forward(
        self,
        features: torch.Tensor,
        labels: torch.Tensor,
        mask: torch.Tensor = None
    ) -> torch.Tensor:
        """
        计算对比损失
        
        Args:
            features: 特征向量 [batch_size, feature_dim]
            labels: 标签 [batch_size]
            mask: 可选的mask [batch_size, batch_size]
            
        Returns:
            对比损失值
        """
        device = features.device
        batch_size = features.shape[0]
        
        # 归一化特征（重要！）
        features = F.normalize(features, dim=1)
        
        # 计算余弦相似度矩阵
        similarity_matrix = torch.matmul(features, features.T)  # [B, B]
        
        # 创建标签mask（同类为1，异类为0）
        labels = labels.contiguous().view(-1, 1)
        mask_positive = torch.eq(labels, labels.T).float().to(device)  # [B, B]
        
        # 移除自身（对角线）
        logits_mask = torch.scatter(
            torch.ones_like(mask_positive),
            1,
            torch.arange(batch_size).view(-1, 1).to(device),
            0
        )
        mask_positive = mask_positive * logits_mask
        
        # 计算exp(similarity / temperature)
        logits = similarity_matrix / self.temperature
        
        # 数值稳定性：减去最大值
        logits_max, _ = torch.max(logits, dim=1, keepdim=True)
        logits = logits - logits_max.detach()
        
        # 计算exp
        exp_logits = torch.exp(logits) * logits_mask
        
        # 计算log_prob
        log_prob = logits - torch.log(exp_logits.sum(1, keepdim=True) + 1e-12)
        
        # 计算正样本的平均log概率
        mean_log_prob_pos = (mask_positive * log_prob).sum(1) / (mask_positive.sum(1) + 1e-12)
        
        # 损失（取负）
        loss = -(self.temperature / self.base_temperature) * mean_log_prob_pos
        loss = loss.mean()
        
        return loss


class CombinedLoss(nn.Module):
    """
    组合损失函数
    
    结合:
    1. Cross-Entropy Loss (分类损失)
    2. Supervised Contrastive Loss (对比学习损失)
    """
    
    def __init__(
        self,
        num_classes: int = 3,
        temperature: float = 0.07,
        alpha: float = 0.5,  # 对比损失的权重
        label_smoothing: float = 0.1
    ):
        """
        Args:
            num_classes: 类别数（情感分类：3类）
            temperature: 对比学习温度
            alpha: 对比损失权重（0-1，1-alpha为分类损失权重）
            label_smoothing: 标签平滑系数
        """
        super(CombinedLoss, self).__init__()
        self.num_classes = num_classes
        self.alpha = alpha
        
        # 分类损失
        self.ce_loss = nn.CrossEntropyLoss(label_smoothing=label_smoothing)
        
        # 对比学习损失
        self.contrastive_loss = SupervisedContrastiveLoss(temperature=temperature)
    
    def forward(
        self,
        logits: torch.Tensor,
        features: torch.Tensor,
        labels: torch.Tensor
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        计算组合损失
        
        Args:
            logits: 分类logits [batch_size, num_classes]
            features: 特征向量 [batch_size, feature_dim]
            labels: 标签 [batch_size]
            
        Returns:
            total_loss: 总损失
            loss_dict: 各部分损失的字典
        """
        # 分类损失
        ce_loss_val = self.ce_loss(logits, labels)
        
        # 对比学习损失
        contrastive_loss_val = self.contrastive_loss(features, labels)
        
        # 组合损失
        total_loss = (1 - self.alpha) * ce_loss_val + self.alpha * contrastive_loss_val
        
        # 返回详细信息
        loss_dict = {
            'total_loss': total_loss.item(),
            'ce_loss': ce_loss_val.item(),
            'contrastive_loss': contrastive_loss_val.item()
        }
        
        return total_loss, loss_dict


class TripletLoss(nn.Module):
    """
    Triplet Loss (可选的对比学习损失)
    
    公式:
    L = max(0, d(a, p) - d(a, n) + margin)
    
    其中:
    - a: anchor
    - p: positive (同类)
    - n: negative (异类)
    - d: 距离函数（通常用欧式距离）
    - margin: 间隔
    """
    
    def __init__(self, margin: float = 1.0, distance: str = 'euclidean'):
        """
        Args:
            margin: 间隔大小
            distance: 距离度量 ('euclidean' or 'cosine')
        """
        super(TripletLoss, self).__init__()
        self.margin = margin
        self.distance = distance
    
    def forward(
        self,
        anchor: torch.Tensor,
        positive: torch.Tensor,
        negative: torch.Tensor
    ) -> torch.Tensor:
        """
        计算triplet损失
        
        Args:
            anchor: anchor特征 [batch_size, feature_dim]
            positive: 正样本特征 [batch_size, feature_dim]
            negative: 负样本特征 [batch_size, feature_dim]
            
        Returns:
            triplet损失
        """
        if self.distance == 'euclidean':
            # 欧式距离
            dist_pos = torch.sum((anchor - positive) ** 2, dim=1)
            dist_neg = torch.sum((anchor - negative) ** 2, dim=1)
        elif self.distance == 'cosine':
            # 余弦距离
            anchor_norm = F.normalize(anchor, dim=1)
            positive_norm = F.normalize(positive, dim=1)
            negative_norm = F.normalize(negative, dim=1)
            
            dist_pos = 1 - torch.sum(anchor_norm * positive_norm, dim=1)
            dist_neg = 1 - torch.sum(anchor_norm * negative_norm, dim=1)
        else:
            raise ValueError(f"不支持的距离度量: {self.distance}")
        
        # 计算损失
        loss = F.relu(dist_pos - dist_neg + self.margin)
        
        return loss.mean()
