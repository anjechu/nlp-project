# PowerShell 使用指南 - PowerShell Usage Guide

## 我做了什么修改？(What Changes Were Made?)

修复了数据文件路径问题，现在程序可以：
1. **自动搜索子目录** - 会自动在 `steam_reviews/`, `data/` 等子目录中查找JSON文件
2. **提供详细提示** - 如果找不到文件，会告诉你在哪里发现了文件
3. **新增查找工具** - 添加了 `find_data_files.py` 帮你找到所有JSON文件

---

## 在PowerShell中应该输入什么？(What to Enter in PowerShell?)

### 步骤1️⃣: 先找到你的JSON文件在哪里

```powershell
# 进入training目录
cd D:\桌面\v1\nlp-project-copilot-add-s-dai-evaluation-model\training

# 运行文件查找工具
python find_data_files.py
```

**这个命令会显示**：
- 所有JSON文件的位置
- 每个目录有多少个文件
- 建议使用的命令

---

### 步骤2️⃣: 根据情况选择合适的命令

#### 场景A：文件在 `steam_reviews/` 子目录 (最常见)

```powershell
# 方法1: 加载所有JSON文件 (推荐)
python train_sentiment.py --data_path "steam_reviews/*.json" --epochs 10

# 方法2: 加载特定文件
python train_sentiment.py --data_path "steam_reviews/steam_reviews_黑神话悟空.json" --epochs 10

# 方法3: 简化写法 (会自动搜索子目录)
python train_sentiment.py --data_path "*.json" --epochs 10
```

#### 场景B：文件在当前目录

```powershell
# 加载当前目录的所有JSON文件
python train_sentiment.py --data_path "*.json" --epochs 10
```

#### 场景C：文件在其他位置

```powershell
# 使用完整路径
python train_sentiment.py --data_path "D:\数据\*.json" --epochs 10
```

---

## 完整示例命令 (Complete Example Commands)

### 示例1: 训练模型（基本）

```powershell
# 进入training目录
cd D:\桌面\v1\nlp-project-copilot-add-s-dai-evaluation-model\training

# 训练模型 - 自动从steam_reviews/加载所有JSON文件
python train_sentiment.py --data_path "steam_reviews/*.json" --epochs 10 --batch_size 32
```

### 示例2: 训练模型（完整参数）

```powershell
python train_sentiment.py `
    --data_path "steam_reviews/*.json" `
    --epochs 10 `
    --batch_size 32 `
    --learning_rate 0.00002 `
    --auto_label
```

**参数说明**：
- `--data_path`: 数据文件路径（支持通配符 `*.json`）
- `--epochs`: 训练轮数（默认10）
- `--batch_size`: 批次大小（默认32）
- `--learning_rate`: 学习率（默认2e-5）
- `--auto_label`: 自动标注数据

### 示例3: 评估模型

```powershell
# 评估已训练的模型
python evaluate_model.py --model_path "checkpoints/best_model.pt" --data_path "steam_reviews/*.json"
```

---

## 常见问题 (FAQ)

### Q1: 我不知道文件在哪里？

**答**: 运行文件查找工具：
```powershell
python find_data_files.py
```
它会告诉你所有JSON文件的位置。

### Q2: 找不到文件怎么办？

**答**: 程序现在会自动提示你。如果看到错误消息，它会告诉你：
```
❌ 错误: 未找到匹配 '*.json' 的文件！

已搜索的位置:
   - steam_reviews/: ✓ 发现 3 个 JSON 文件
     💡 尝试使用: --data_path 'steam_reviews/*.json'
```

按照提示修改命令即可。

### Q3: 如何加载多个文件？

**答**: 使用通配符 `*`：
```powershell
# 加载所有JSON文件
python train_sentiment.py --data_path "steam_reviews/*.json"

# 加载特定模式的文件
python train_sentiment.py --data_path "steam_reviews/steam_reviews_*.json"
```

### Q4: PowerShell中路径要用引号吗？

**答**: 
- 如果路径包含空格或通配符，**必须使用引号**：
  ```powershell
  --data_path "steam_reviews/*.json"  ✅ 正确
  --data_path steam_reviews/*.json    ❌ 错误
  ```
- 使用双引号 `"..."` 而不是单引号

### Q5: 如何查看所有可用参数？

**答**: 
```powershell
python train_sentiment.py --help
```

---

## 快速参考卡 (Quick Reference)

| 你想做什么 | PowerShell命令 |
|-----------|---------------|
| 查找JSON文件位置 | `python find_data_files.py` |
| 从steam_reviews/训练 | `python train_sentiment.py --data_path "steam_reviews/*.json" --epochs 10` |
| 从当前目录训练 | `python train_sentiment.py --data_path "*.json" --epochs 10` |
| 加载单个文件 | `python train_sentiment.py --data_path "steam_reviews/file.json"` |
| 查看帮助 | `python train_sentiment.py --help` |

---

## 推荐工作流程 (Recommended Workflow)

### 第一次使用：

```powershell
# 1. 进入项目目录
cd D:\桌面\v1\nlp-project-copilot-add-s-dai-evaluation-model\training

# 2. 查找数据文件
python find_data_files.py

# 3. 根据提示运行训练（假设文件在steam_reviews/）
python train_sentiment.py --data_path "steam_reviews/*.json" --epochs 10 --batch_size 32

# 4. 等待训练完成，模型会保存到checkpoints/
```

### 后续使用：

```powershell
# 直接运行训练（因为你已经知道文件位置）
cd D:\桌面\v1\nlp-project-copilot-add-s-dai-evaluation-model\training
python train_sentiment.py --data_path "steam_reviews/*.json" --epochs 10
```

---

## 注意事项 (Important Notes)

1. **使用正斜杠或反斜杠都可以**：
   ```powershell
   "steam_reviews/*.json"   ✅ 推荐
   "steam_reviews\*.json"   ✅ 也可以
   ```

2. **文件名中的中文**：
   - PowerShell支持中文文件名
   - 确保使用UTF-8编码
   ```powershell
   --data_path "steam_reviews/steam_reviews_黑神话悟空.json"  ✅
   ```

3. **路径中的空格**：
   ```powershell
   --data_path "my data/steam_reviews/*.json"  ✅ 使用引号
   ```

4. **多行命令**：
   在PowerShell中使用反引号 `` ` `` 续行：
   ```powershell
   python train_sentiment.py `
       --data_path "steam_reviews/*.json" `
       --epochs 10 `
       --batch_size 32
   ```

---

## 错误排查 (Troubleshooting)

### 错误: "python不是内部或外部命令"

**解决方案**: 
```powershell
# 使用python3或py
python3 train_sentiment.py --data_path "steam_reviews/*.json"
# 或
py train_sentiment.py --data_path "steam_reviews/*.json"
```

### 错误: "ModuleNotFoundError"

**解决方案**: 安装依赖
```powershell
pip install -r requirements.txt
```

### 错误: "数据集为空"

**解决方案**: 
1. 检查JSON文件是否有内容
2. 确认文件格式正确
3. 查看是否有文本长度过滤（默认最小10字符）

---

## 总结 (Summary)

**最简单的使用方式**：

```powershell
# 1. 进入目录
cd training

# 2. 找文件
python find_data_files.py

# 3. 运行（使用提示的路径）
python train_sentiment.py --data_path "steam_reviews/*.json" --epochs 10
```

**就这么简单！** 🎉

---

## 获取更多帮助

- 查看 `DATA_PATH_FIX.md` - 详细的修复说明
- 查看 `DATALOADER_COMPLETE_SUMMARY.md` - 完整的功能总结
- 运行 `python train_sentiment.py --help` - 查看所有参数

如有问题，程序会提供详细的错误消息和建议！
