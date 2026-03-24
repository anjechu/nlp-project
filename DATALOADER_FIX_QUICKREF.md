# Data Loader Fix - Quick Reference

## What Was Fixed

The curriculum learning data loader had an index mapping bug that would cause training to fail.

## The Problem (In Simple Terms)

When you split your dataset into train/val, PyTorch creates a "Subset" that references the original data. The curriculum scheduler was confused about which indices to use, causing errors like:

```
IndexError: index out of range
```

## The Solution

We now properly map indices between:
1. **Temp dataset** (used by curriculum scheduler) → indices 0, 1, 2, ...
2. **Original dataset** (the full dataset) → actual indices

This ensures the curriculum scheduler picks the right samples.

## How to Use

Just run your training script normally:

```bash
python train_sentiment.py \
  --data_path your_data.json \
  --epochs 10 \
  --batch_size 32
```

The fix is automatic - no changes needed to your usage!

## Verification

If you want to verify the fix works:

```bash
# Generate sample data
python generate_sample_training_data.py

# Try training
python train_sentiment.py \
  --data_path sample_train_small.json \
  --epochs 2 \
  --batch_size 8
```

You should see output like:
```
📚 计算样本难度...
✓ 难度计算完成
📊 样本按难度排序完成
📖 Epoch 1: 使用 30/100 样本 (难度比例: 30.00%)
```

## Technical Details

For developers who want to understand the fix:

See `DATALOADER_FIX.md` for:
- Detailed root cause analysis
- Code changes with explanations
- Index mapping flow diagram
- Test validation

## Still Having Issues?

If you encounter errors:

1. Check your data format (see TRAINING_GUIDE.md)
2. Verify PyTorch version: `pip list | grep torch`
3. Try with smaller batch size: `--batch_size 8`
4. Use CPU if GPU issues: `--device cpu`

## Summary

✅ **Fixed**: Index mapping in curriculum scheduler
✅ **Tested**: Logic validated with test scripts
✅ **Impact**: Training now works with curriculum learning + data splitting
✅ **No changes needed**: Your training scripts work as-is
