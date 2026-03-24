# Data Loader Fix - Curriculum Scheduler Index Mapping

## Problem

The data loader had an index mapping issue when using curriculum learning with PyTorch's `random_split`. 

### Root Cause

When `torch.utils.data.random_split` is used, it creates a `Subset` object that maintains its own indices into the original dataset. The curriculum scheduler was operating on a temporary dataset with samples from the train split, and returning indices relative to that temporary dataset (0, 1, 2, ...). However, these indices needed to be mapped back to the original dataset indices before creating a new `Subset`.

### Error Scenario

```
Original Dataset: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                     ↓ random_split
Train Subset: indices [0, 1, 2, 3, 4, 5, 6, 7]  → references original dataset
Val Subset: indices [8, 9]                       → references original dataset
                     ↓
Temp Dataset: 8 samples (for curriculum learning)
  - Sample 0 → original index 0
  - Sample 1 → original index 1
  - ...
                     ↓
Curriculum selects: [0, 1, 2, 3]  ← These are temp_dataset indices!
                     ↓
WITHOUT FIX: Subset(train_dataset, [0,1,2,3])  ← Wrong! train_dataset is already a Subset
WITH FIX: Subset(full_dataset, [0,1,2,3])      ← Correct! Uses original indices
```

## Solution

### Changes Made

1. **train_sentiment.py** (Line 166-169)
   - Modified `TempDataset` class to store `original_indices` mapping
   - Pass `train_dataset.indices` when creating temp dataset

2. **training/curriculum.py** (Line 221-222)
   - Store `original_indices` attribute from dataset if available
   - Used `getattr(dataset, 'original_indices', None)` for safety

3. **training/curriculum.py** (Line 309-316)
   - In `get_curriculum_indices()`, map selected indices back to original dataset indices
   - Return `[self.original_indices[idx] for idx in selected_indices]`

4. **training/trainer.py** (Line 242-249)
   - Use `self.train_dataset.dataset` (the original full dataset) when creating Subset
   - Pass `curriculum_indices` which are now properly mapped to original indices

### How It Works

```python
# 1. Create temp dataset with index mapping
train_samples = [full_dataset.samples[i] for i in train_dataset.indices]
temp_dataset = TempDataset(train_samples, list(train_dataset.indices))
#                                         ^^^^^^^^^^^^^^^^^^^^^^^^
#                                         Save original indices!

# 2. Curriculum scheduler stores this mapping
self.original_indices = getattr(dataset, 'original_indices', None)

# 3. When returning indices, map them back
if self.original_indices is not None:
    mapped_indices = [self.original_indices[idx] for idx in selected_indices]
    return mapped_indices

# 4. Create Subset with original dataset and mapped indices
curriculum_subset = Subset(self.train_dataset.dataset, curriculum_indices)
#                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^  Original full dataset
#                                                      ^^^^^^^^^^^^^^^^^^^ Mapped indices
```

## Testing

Created test script `/tmp/test_index_mapping.py` that validates the logic:
- ✓ Index mapping from temp dataset to original dataset works correctly
- ✓ Subset creation uses correct dataset and indices
- ✓ All indices are within valid range

## Impact

- **Before**: Training would fail with index out of range errors
- **After**: Training works correctly with curriculum learning and data splitting

## Files Modified

1. `train_sentiment.py` - Modified TempDataset class
2. `training/curriculum.py` - Added index mapping support
3. `training/trainer.py` - Fixed Subset creation in train_epoch
