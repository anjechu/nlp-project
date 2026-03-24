# Empty Dataset Fix - Complete Guide

## Problem Summary

Users were experiencing crashes when running `train_sentiment.py` with empty or invalid datasets:

```
✓ 加载完成: 0 条有效样本

✂️ 划分数据集...
   训练集: 0 样本
   验证集: 0 样本

📚 初始化课程学习调度器...
📚 计算样本难度...
✓ 难度计算完成
Traceback (most recent call last):
  File "train_sentiment.py", line 247, in <module>
```

## Root Causes

### Issue 1: Empty Dataset Not Validated
The code didn't check if the dataset had samples before attempting to train, leading to crashes in downstream code.

### Issue 2: Unprotected Statistics on Empty Data
When computing difficulty statistics, the code called `min()` and `max()` on empty lists:
```python
diff_values = []  # Empty when no samples
min(diff_values)  # ValueError: min() arg is an empty sequence
```

### Issue 3: Missing Glob Pattern Support
Users wanted to load multiple files with patterns like `*.json`, but the code only supported single file paths.

## Solutions Implemented

### 1. Empty Dataset Validation (train_sentiment.py)

**Location**: After loading the dataset (line 141)

**What it does**:
- Checks if `len(full_dataset) == 0`
- Displays helpful error message
- Exits early before attempting to train

**Code**:
```python
# 验证数据集不为空
if len(full_dataset) == 0:
    print("\n❌ 错误: 数据集为空！")
    print("   可能的原因:")
    print("   1. 数据文件不存在或路径错误")
    print("   2. 数据文件格式不正确")
    print("   3. 所有样本都被过滤掉了（文本太短）")
    print(f"\n   请检查数据路径: {args.data_path}")
    print(f"   最小文本长度要求: {args.min_text_length} 字符")
    return
```

**User Experience**:
Instead of a crash, users see a clear explanation of what went wrong and how to fix it.

### 2. Protected Statistics Computation (curriculum.py)

**Location**: `_compute_difficulties()` and `_sort_by_difficulty()` methods

**What it does**:
- Checks list length before calling `min()`, `max()`, `mean()`
- Shows warning message for empty data
- Prevents crashes while still being informative

**Code**:
```python
# In _compute_difficulties (line 251)
diff_values = [d['difficulty'] for d in self.difficulties]
if len(diff_values) > 0:
    print(f"   难度分布: min={min(diff_values):.3f}, "
          f"mean={np.mean(diff_values):.3f}, "
          f"max={max(diff_values):.3f}")
else:
    print(f"   ⚠️ 警告: 没有样本数据")

# In _sort_by_difficulty (line 264)
n_samples = len(self.sorted_indices)
if n_samples > 0:
    easy_cutoff = int(n_samples * 0.33)
    # ... show statistics
else:
    print(f"   ⚠️ 警告: 没有样本可排序")
```

### 3. Glob Pattern Support (data_loader.py)

**Location**: `SteamReviewDataset.__init__()` method

**What it does**:
- Detects glob patterns (`*` or `?` in path)
- Uses `glob.glob()` to find matching files
- Loads and merges data from all matched files
- Handles per-file errors gracefully
- Falls back to single file loading for regular paths

**Code**:
```python
# Check if glob pattern
if '*' in data_path or '?' in data_path:
    # Glob mode: load multiple files
    print(f"📂 正在扫描路径: {data_path}")
    file_list = glob.glob(data_path)
    
    if not file_list:
        print(f"⚠️ 警告: 未找到匹配 '{data_path}' 的文件")
        self.reviews = []
    else:
        print(f"🔍 成功匹配到 {len(file_list)} 个 JSON 文件，开始合并加载...")
        self.reviews = []
        for file_path in file_list:
            try:
                print(f"   加载: {os.path.basename(file_path)}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                
                # Parse and merge data
                if isinstance(raw_data, list):
                    self.reviews.extend(raw_data)
                elif isinstance(raw_data, dict):
                    file_reviews = (
                        raw_data.get('comments', []) or 
                        raw_data.get('reviews', []) or
                        raw_data.get('data', [])
                    )
                    self.reviews.extend(file_reviews)
            except Exception as e:
                print(f"   ⚠️ 加载失败 {os.path.basename(file_path)}: {e}")
                continue
        
        print(f"✓ 合并完成: 共 {len(self.reviews)} 条原始评论")
else:
    # Single file: load directly
    print(f"📂 加载数据: {data_path}")
    # ... existing single file code
```

## Usage Examples

### Example 1: Empty Dataset Detection

**Command**:
```bash
python train_sentiment.py --data_path empty_data.json
```

**Output**:
```
📂 加载数据集: empty_data.json
✓ 加载完成: 0 条有效样本

❌ 错误: 数据集为空！
   可能的原因:
   1. 数据文件不存在或路径错误
   2. 数据文件格式不正确
   3. 所有样本都被过滤掉了（文本太短）
   
   请检查数据路径: empty_data.json
   最小文本长度要求: 10 字符
```

### Example 2: Glob Pattern Loading

**Command**:
```bash
python train_sentiment.py --data_path "data/*.json"
```

**Output**:
```
📂 正在扫描路径: data/*.json
🔍 成功匹配到 3 个 JSON 文件，开始合并加载...
   加载: game1.json
   加载: game2.json
   加载: game3.json
✓ 合并完成: 共 456 条原始评论
✓ 加载完成: 389 条有效样本

✂️ 划分数据集...
   训练集: 311 样本
   验证集: 78 样本
```

### Example 3: Single File (Still Works)

**Command**:
```bash
python train_sentiment.py --data_path reviews.json
```

**Output**:
```
📂 加载数据: reviews.json
✓ 加载完成: 150 条有效样本

✂️ 划分数据集...
   训练集: 120 样本
   验证集: 30 样本
```

## Common Scenarios and Solutions

### Scenario 1: Files Matched But 0 Samples

**Symptom**:
```
🔍 成功匹配到 3 个 JSON 文件，开始合并加载...
✓ 合并完成: 共 50 条原始评论
✓ 加载完成: 0 条有效样本

❌ 错误: 数据集为空！
```

**Possible Causes**:
1. **Text too short**: All reviews are shorter than `min_text_length` (default 10)
2. **Missing text fields**: Reviews don't have 'text', 'review', 'comment', or 'content' fields
3. **Missing labels**: Reviews don't have 'sentiment' or 'label', and `auto_label=False`

**Solutions**:
- Lower `min_text_length`: `--min_text_length 5`
- Check your JSON structure matches expected format
- Enable auto-labeling: `--auto_label True` (default)

### Scenario 2: No Files Matched

**Symptom**:
```
📂 正在扫描路径: *.json
⚠️ 警告: 未找到匹配 '*.json' 的文件
✓ 加载完成: 0 条有效样本
```

**Possible Causes**:
1. Wrong directory (glob patterns are relative to current directory)
2. No JSON files in the directory
3. Wrong file extension

**Solutions**:
- Use absolute path or relative path with directory: `data/*.json`
- Check file exists: `ls *.json`
- Verify current directory: `pwd`

### Scenario 3: Curriculum Scheduler Warning

**Symptom**:
```
📚 计算样本难度...
✓ 难度计算完成
   ⚠️ 警告: 没有样本数据
```

**Cause**:
Empty dataset passed to curriculum scheduler (should be caught earlier by dataset validation)

**Solution**:
This is a safety check. The real issue should be caught by the empty dataset validation earlier in the process.

## File Changes Summary

| File | Changes | Lines |
|------|---------|-------|
| `train_sentiment.py` | Added empty dataset validation | 141-155 |
| `training/curriculum.py` | Protected min/max calls (2 places) | 251-259, 269-277 |
| `training/data_loader.py` | Added glob support + imports | 1-19, 51-110 |

## Testing

All fixes have been validated:
- ✓ Glob pattern detection works
- ✓ Multiple file loading and merging
- ✓ Empty list protection prevents crashes
- ✓ Clear error messages displayed
- ✓ Backward compatible with single files

## Migration Guide

**No changes needed!** These are backward-compatible improvements:

- Existing single-file paths work exactly as before
- New glob patterns now supported
- Empty datasets now handled gracefully instead of crashing

## Troubleshooting

If you still encounter issues:

1. **Check file format**:
   ```python
   import json
   with open('your_file.json') as f:
       data = json.load(f)
       print(data.keys())  # Should have 'comments', 'reviews', or 'data'
   ```

2. **Check sample content**:
   ```python
   print(data['comments'][0])  # Should have 'text' or similar field
   ```

3. **Lower minimum length**:
   ```bash
   python train_sentiment.py --data_path *.json --min_text_length 1
   ```

4. **Enable debug mode** (if available):
   ```bash
   python train_sentiment.py --data_path *.json --verbose
   ```

## Related Documentation

- `DATALOADER_FIX.md` - Index mapping fix for curriculum scheduler
- `DATALOADER_FIX_QUICKREF.md` - Quick reference for all data loader fixes
- This document - Empty dataset and glob pattern handling
