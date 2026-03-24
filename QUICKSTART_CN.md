# 快速开始 - 在PowerShell中运行训练

## 🚀 三步开始训练

### 步骤1: 打开PowerShell，进入training目录

```powershell
cd D:\桌面\v1\nlp-project-copilot-add-s-dai-evaluation-model\training
```

### 步骤2: 查找你的JSON数据文件

```powershell
python find_data_files.py
```

**输出示例**：
```
📂 数据文件查找工具
✅ 找到 3 个JSON文件

📂 steam_reviews/ (3 个文件)
   1. steam_reviews_黑神话悟空.json
   2. steam_reviews_只狼.json
   3. steam_reviews_艾尔登法环.json

💡 使用建议:
   python train_sentiment.py --data_path 'steam_reviews/*.json'
```

### 步骤3: 运行训练（复制建议的命令）

```powershell
python train_sentiment.py --data_path "steam_reviews/*.json" --epochs 10
```

**完成！** 🎉

---

## 📝 我做的修改

### 修改前的问题：
```
❌ 错误：在当前文件夹没有找到任何类似 'steam_reviews_xxx.json' 的文件！
```

### 修改后的解决方案：

1. ✅ **自动搜索子目录**
   - 程序现在会自动在 `steam_reviews/`、`data/` 等子目录中查找JSON文件
   - 不需要把文件移到同一个文件夹

2. ✅ **智能提示**
   - 如果找不到文件，会告诉你在哪个目录发现了文件
   - 提供正确的命令建议

3. ✅ **文件查找工具**
   - 新增 `find_data_files.py` 工具
   - 帮你快速找到所有JSON文件的位置

---

## 💡 常用命令

### 训练模型（推荐）
```powershell
# 从steam_reviews/目录加载所有JSON文件
python train_sentiment.py --data_path "steam_reviews/*.json" --epochs 10 --batch_size 32
```

### 加载单个文件
```powershell
python train_sentiment.py --data_path "steam_reviews/steam_reviews_黑神话悟空.json" --epochs 10
```

### 查看所有参数
```powershell
python train_sentiment.py --help
```

---

## ⚠️ 重要提示

1. **必须使用引号**（因为有通配符 `*`）：
   ```powershell
   --data_path "steam_reviews/*.json"  ✅ 正确
   --data_path steam_reviews/*.json    ❌ 错误
   ```

2. **支持中文文件名**：
   ```powershell
   --data_path "steam_reviews/steam_reviews_黑神话悟空.json"  ✅
   ```

3. **如果不确定文件位置**，先运行：
   ```powershell
   python find_data_files.py
   ```

---

## 🎯 完整示例

```powershell
# 打开PowerShell

# 1. 进入目录
cd D:\桌面\v1\nlp-project-copilot-add-s-dai-evaluation-model\training

# 2. 查找文件（可选，帮助你确认文件位置）
python find_data_files.py

# 3. 开始训练
python train_sentiment.py --data_path "steam_reviews/*.json" --epochs 10 --batch_size 32

# 训练过程中会显示进度：
# 📂 正在扫描路径: steam_reviews/*.json
# 💡 提示: 在子目录 'steam_reviews' 中找到文件
# 🔍 成功匹配到 3 个 JSON 文件，开始合并加载...
# ✓ 加载完成: 150 条有效样本
# 训练集: 135 样本
# 验证集: 15 样本
# Epoch 1/10...
```

---

## ❓ 遇到问题？

### 找不到python命令
```powershell
# 尝试使用
python3 train_sentiment.py --data_path "steam_reviews/*.json"
# 或
py train_sentiment.py --data_path "steam_reviews/*.json"
```

### 找不到文件
```powershell
# 运行文件查找工具，看看文件在哪
python find_data_files.py
```

### 数据集为空
- 检查JSON文件是否有内容
- 确认文件格式是否正确（需要有 `comments`、`reviews` 或 `data` 字段）

---

## 📚 更多信息

- 详细说明：查看 `POWERSHELL_USAGE_GUIDE.md`
- 技术细节：查看 `DATA_PATH_FIX.md`
- 完整文档：查看 `DATALOADER_COMPLETE_SUMMARY.md`

**祝训练顺利！** 🚀
