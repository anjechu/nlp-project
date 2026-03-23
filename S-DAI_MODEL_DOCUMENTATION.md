# S-DAI 模型文档 (Sentiment-adjusted Developer Actionable Index)

> **⚠️ 架构更新通知 (2026-03-23)**
> 
> S-DAI 模型已从 `llm_report_generator.py` 迁移至 `nlp.py`，实现了以下重要改进：
> - ✅ **行级精度**：在每条评论级别应用文化修正
> - ✅ **向量空间原生访问**：直接计算真实的聚类紧密度
> - ✅ **GPU 加速**：全流程 GPU 并行计算
> - ✅ **架构优化**：更好的关注点分离
> 
> **详细信息请参考**：[S-DAI_ARCHITECTURE_REFACTORING.md](./S-DAI_ARCHITECTURE_REFACTORING.md)
> 
> 本文档保留作为算法理论参考。实现细节已更新至 `nlp.py`。

---

## 1. 模型概述

S-DAI（Sentiment-adjusted Developer Actionable Index，情感调整的开发者可执行指数）是一个用于游戏评论优先级评估的数学模型。该模型在 Map-Reduce 架构的 Reduce 阶段对来自不同文化背景的玩家反馈进行科学排序，帮助开发者快速识别最需要关注的游戏问题。

## 2. 核心创新点

### 2.1 文化敏感性考虑
传统的情感分析模型往往忽视了不同文化背景下情感表达的差异。S-DAI 模型创新性地引入了**文化修正系数**，专门针对东亚玩家（中文、日文）在表达负面情绪时更为含蓄的语言特点进行调整。

### 2.2 多维度综合评估
S-DAI 不仅考虑情感强度，还综合了：
- **声量（Volume）**：提及该话题的玩家数量
- **情感强度（Sentiment）**：经过文化修正的情感得分
- **一致性（Consistency）**：话题内部的聚类紧密度

## 3. 数学模型

### 3.1 第一步：文化加权情感得分（S_adj）

**公式：**
```
S_adj = S_raw × (1 + α)
```

**参数说明：**
- `S_raw`：原始情感得分（来自 NLP 情感分析，范围 -1 到 +1）
- `α`：文化修正系数
  - 当语言为东亚语言（chinese/japanese）且 `S_raw < 0` 时，`α = 0.2`
  - 其他情况 `α = 0`

**理论依据：**
东亚文化中，负面情绪的表达倾向于更加委婉含蓄。例如：
- 东亚玩家："希望能改进一下性能问题"
- 西方玩家："This game runs like garbage!"

两者表达的不满程度相似，但 NLP 模型会低估东亚玩家的负面情绪强度。通过放大 20% 来平衡这种文化差异。

**示例：**
```python
# 中文负面评论
S_raw = -0.6
S_adj = -0.6 × (1 + 0.2) = -0.72  # 放大20%

# 英文负面评论
S_raw = -0.6
S_adj = -0.6 × (1 + 0) = -0.6    # 不做修正
```

### 3.2 第二步：开发者可执行指数（DAI）

**公式：**
```
DAI = log(1 + V) × |S_adj| × C
```

**参数说明：**
- `V`（Volume）：声量，即提及该话题的玩家数量
- `|S_adj|`：文化修正后的情感强度的绝对值
- `C`（Consistency）：聚类紧密度（范围 0-1，默认 1.0）

**设计原理：**

1. **log(1 + V)：对数变换**
   - 体现边际效益递减原理
   - 10 人 → 20 人的增量价值 > 1000 人 → 1010 人的增量价值
   - 避免极端高声量话题完全压制其他重要反馈

2. **|S_adj|：情感强度绝对值**
   - 无论正面还是负面，强烈的情感都值得关注
   - 正面反馈：确认做对的方向
   - 负面反馈：识别需要改进的问题

3. **C：一致性系数**
   - 高一致性意味着玩家诉求明确，更易于采取行动
   - 低一致性可能表示话题内部意见分散

**示例计算：**
```python
# 中文负面高优先级话题
V = 100 (玩家数)
S_raw = -0.8
S_adj = -0.8 × 1.2 = -0.96
C = 1.0
DAI = log(1 + 100) × |-0.96| × 1.0 = 4.615 × 0.96 × 1.0 = 4.43

# 英文中等优先级话题
V = 50
S_raw = -0.6
S_adj = -0.6
C = 1.0
DAI = log(1 + 50) × |-0.6| × 1.0 = 3.932 × 0.6 × 1.0 = 2.36
```

在上述例子中，中文话题获得了更高的 DAI 得分，会被优先展示给开发者。

## 4. 实现细节

### 4.1 代码结构

```python
class LLMReportGenerator:
    def _calculate_s_dai(self, topic: Dict, language: str) -> float:
        """
        计算单个 topic 的 S-DAI 得分
        
        输入：
        - topic: 包含 sentiment_score, density, consistency 的字典
        - language: 语言标识（如 'chinese', 'japanese', 'english'）
        
        输出：
        - dai_score: 优先级得分（同时更新 topic 字典）
        """
        # 步骤1：文化修正
        s_raw = topic.get('sentiment_score', 0)
        is_east_asian = language.lower() in ['chinese', 'japanese', 'schinese', 'tchinese']
        alpha = 0.2 if (is_east_asian and s_raw < 0) else 0
        s_adj = s_raw * (1 + alpha)
        
        # 步骤2：计算 DAI
        v = topic.get('density', 1)
        consistency = topic.get('consistency', 1.0)
        dai_score = np.log1p(v) * abs(s_adj) * consistency
        
        # 注入结果
        topic['s_adj'] = s_adj
        topic['dai_score'] = dai_score
        
        return dai_score
    
    def aggregate_map_results(self, map_results: List[Dict]) -> Dict:
        """
        在 Reduce 阶段聚合结果并应用 S-DAI 排序
        """
        # 收集所有 topics
        all_topics = []
        for result in map_results:
            lang = result['map_metadata']['language']
            for topic in result['topics']:
                # 计算 S-DAI
                self._calculate_s_dai(topic, lang)
                all_topics.append(topic)
        
        # 按 DAI 降序排序
        all_topics.sort(key=lambda x: x.get('dai_score', 0), reverse=True)
        
        return {'topics': all_topics, ...}
```

### 4.2 测试验证

运行测试：
```bash
python test_s_dai_model.py
```

测试覆盖：
1. 文化修正系数的正确应用（东亚负面 vs 其他情况）
2. DAI 公式的数学准确性
3. 排序逻辑的正确性
4. 边界情况处理（缺失字段等）

## 5. 应用场景

### 5.1 跨文化游戏开发
对于在全球市场发行的游戏（如《战地风云》、《原神》等），开发者需要同时处理来自不同文化背景的玩家反馈。S-DAI 模型确保：
- 中文玩家的含蓄负面反馈不会被忽视
- 日文玩家的细腻情感表达得到正确解读
- 所有语言的反馈在同一尺度下进行优先级排序

### 5.2 开发资源分配
有限的开发资源应该优先解决哪些问题？S-DAI 提供了量化依据：
- 高 DAI 分数：大量玩家强烈关注，应优先处理
- 中等 DAI 分数：重要但不紧急，列入迭代计划
- 低 DAI 分数：小众需求，视资源情况而定

## 6. 参数调优建议

当前版本中，文化修正系数 `α = 0.2` 是基于以下考虑选择的：
- 文献研究：东亚文化情感表达研究
- Pilot 实验：小规模数据集验证
- 实用性平衡：避免过度修正

**未来优化方向：**
1. **自适应 α**：根据具体游戏类型和玩家社区特点动态调整
2. **扩展语言支持**：为韩语、泰语等其他亚洲语言添加文化修正
3. **时间衰减因子**：考虑反馈的新鲜度
4. **玩家权重**：区分核心玩家和休闲玩家的反馈

## 7. 学术贡献

S-DAI 模型的创新性体现在：

1. **跨学科融合**
   - 文化语言学 + NLP + 软件工程
   - 将人文研究的文化洞察量化为工程实践

2. **实用价值**
   - 直接应用于游戏开发的实际场景
   - 提供可操作的优先级决策依据

3. **可扩展性**
   - 模块化设计，易于集成到现有系统
   - 参数可调，适应不同场景需求

## 8. 引用建议

如需在论文中引用本模型，建议描述为：

> 本研究提出了 S-DAI（Sentiment-adjusted Developer Actionable Index）模型，
> 用于在跨文化背景下对游戏玩家反馈进行优先级评估。该模型创新性地引入文化
> 修正系数，针对东亚玩家含蓄的情感表达特点进行量化调整，并结合声量、情感
> 强度和一致性三个维度计算开发者可执行指数。实验结果表明，S-DAI 模型能够
> 有效平衡不同文化背景下的反馈优先级，为游戏开发团队提供科学的决策依据。

---

**作者**：Your Name  
**日期**：2026年3月  
**版本**：1.0  
**适用范围**：NLP Project - Game Review Analysis System
