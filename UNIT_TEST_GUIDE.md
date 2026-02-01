# Engineering Unit Tests - 工程测试套件

这是一个完整的单元测试套件，可以在本地运行来证明代码可以工作。

This is a comprehensive unit test suite that can be run locally to prove the code works.

## 快速开始 / Quick Start

### 运行所有测试 / Run All Tests

```bash
python test_suite_runner.py
```

### 只运行基础测试（无依赖）/ Run Basic Tests Only (No Dependencies)

```bash
python test_suite_runner.py --basic
```

### 详细输出 / Verbose Output

```bash
python test_suite_runner.py --verbose
```

## 测试分类 / Test Categories

### 🟢 Level 1: 基础测试 (无依赖) / Basic Tests (No Dependencies)

这些测试不需要任何ML库，可以在任何Python环境中运行。

These tests don't require any ML libraries and can run in any Python environment.

**测试文件 / Test Files:**
- `test_core_functions.py` - 核心函数测试 / Core function tests
  - 文本处理 / Text processing
  - 数据验证 / Data validation
  - JSON操作 / JSON operations
  - 工具函数 / Utility functions
  
- `test_file_operations.py` - 文件操作测试 / File operation tests
  - JSON读写 / JSON read/write
  - Unicode处理 / Unicode handling
  - 路径操作 / Path operations
  - TSV操作 / TSV operations

- `test_integration_basic.py` - 基础集成测试 / Basic integration tests
  - 模块导入 / Module imports
  - 文件结构 / File structure
  - 文档存在 / Documentation existence

**运行方式 / How to Run:**
```bash
python test_core_functions.py
python test_file_operations.py
python test_integration_basic.py
```

### 🟡 Level 2: 数据处理测试 (需要numpy/pandas) / Data Processing Tests (Requires numpy/pandas)

这些测试需要numpy和pandas库。

These tests require numpy and pandas libraries.

**测试文件 / Test Files:**
- `test_data_processing.py` - 数据处理测试 / Data processing tests
  - DataFrame操作 / DataFrame operations
  - 语言检测 / Language detection
  - 数组统计 / Array statistics
  - 向量归一化 / Vector normalization

**安装依赖 / Install Dependencies:**
```bash
pip install numpy pandas
```

**运行方式 / How to Run:**
```bash
python test_data_processing.py
```

### 🔴 Level 3: ML测试 (需要完整依赖) / ML Tests (Requires Full Dependencies)

这些测试需要完整的ML库栈。

These tests require the full ML library stack.

**安装依赖 / Install Dependencies:**
```bash
pip install torch transformers sentence-transformers scikit-learn hdbscan
```

## 测试结果示例 / Test Results Example

```
======================================================================
              NLP Comment Processor - Test Suite Runner               
======================================================================

Available Dependencies:
  • basic                     ✓ Installed
  • numpy                     ✓ Installed
  • pandas                    ✓ Installed
  • torch                     ✗ Not installed
  • transformers              ✗ Not installed
  • sentence_transformers     ✗ Not installed
  • sklearn                   ✗ Not installed
  • hdbscan                   ✗ Not installed

Test Categories:
  • Basic tests (no deps):     ✓ Available
  • NumPy tests:               ✓ Available
  • Pandas tests:              ✓ Available
  • ML tests (full pipeline):  ✗ Unavailable

Running Tests...

Category 1: Basic Tests (No Dependencies)
----------------------------------------------------------------------
✓ PASSED: test_core_functions.TestTextProcessing (8 tests)
✓ PASSED: test_core_functions.TestDataValidation (6 tests)
✓ PASSED: test_file_operations.TestFileOperations (7 tests)

Category 2: Data Processing Tests
----------------------------------------------------------------------
✓ PASSED: test_data_processing.TestDataCleaning (5 tests)
✓ PASSED: test_data_processing.TestLanguageDetection (3 tests)

Category 3: Integration Tests
----------------------------------------------------------------------
✓ PASSED: test_integration_basic.TestModuleIntegration (8 tests)

======================================================================
                             Test Summary                             
======================================================================

Results:
  Total tests run:    37
  Passed:             37
  Failed:             0
  Errors:             0
  Execution time:     0.15 seconds

🎉 ALL TESTS PASSED! (100%)
```

## 测试覆盖 / Test Coverage

### ✅ 已测试的功能 / Tested Features

1. **文本处理 / Text Processing**
   - HTML标签清除 / HTML tag removal
   - URL移除 / URL removal
   - 空白符标准化 / Whitespace normalization
   - 特殊字符处理 / Special character handling
   - 大小写转换 / Case conversion

2. **语言检测 / Language Detection**
   - 中文检测 / Chinese detection
   - 日文检测 / Japanese detection
   - 语言分类 / Language classification

3. **数据验证 / Data Validation**
   - 数字文本检测 / Numeric-only detection
   - 空文本检测 / Empty text detection
   - 重复检测 / Duplicate detection
   - 最小字数验证 / Minimum word count
   - 重复字符检测 / Repeated character detection

4. **文件操作 / File Operations**
   - JSON读写 / JSON read/write
   - Unicode处理 / Unicode handling
   - 文件存在检查 / File existence check
   - 目录创建 / Directory creation
   - TSV操作 / TSV operations

5. **数据处理 / Data Processing**
   - DataFrame创建 / DataFrame creation
   - 数据过滤 / Data filtering
   - 数据排序 / Data sorting
   - 缺失值处理 / Missing value handling
   - 分组统计 / Grouping operations

6. **集成测试 / Integration Tests**
   - 模块导入 / Module imports
   - 文件结构 / File structure
   - 函数存在性 / Function existence
   - 文档存在性 / Documentation existence

### ❌ 未测试的功能 / Untested Features

这些功能需要完整的ML依赖库：

These features require full ML dependencies:

1. 实际模型推理 / Actual model inference
2. GPU加速测试 / GPU acceleration tests
3. 端到端pipeline / End-to-end pipeline
4. LLM集成 / LLM integration
5. 聚类算法 / Clustering algorithms

## 为什么这样设计？/ Why This Design?

### 分层测试策略 / Layered Testing Strategy

**优点 / Advantages:**

1. **快速反馈 / Fast Feedback**
   - 基础测试运行 < 1秒
   - 无需安装大型依赖
   - 可以在CI/CD中快速运行

2. **渐进式验证 / Progressive Validation**
   - Level 1: 证明代码逻辑正确
   - Level 2: 证明数据处理正确
   - Level 3: 证明ML pipeline正确

3. **本地可运行 / Locally Runnable**
   - 不需要GPU
   - 不需要大量内存
   - 不需要网络访问

4. **易于调试 / Easy to Debug**
   - 测试独立
   - 清晰的错误消息
   - 详细的文档

### 适用场景 / Use Cases

**✅ 适合 / Good For:**
- 开发过程中快速验证 / Quick validation during development
- CI/CD pipeline / Continuous integration
- 代码审查 / Code review
- 学习和教学 / Learning and teaching
- 本地调试 / Local debugging

**❌ 不适合 / Not For:**
- 准确率验证 / Accuracy validation
- 性能基准测试 / Performance benchmarking
- 生产环境测试 / Production testing
- 模型质量评估 / Model quality assessment

## 常见问题 / FAQ

### Q1: 为什么有些测试被跳过？/ Why are some tests skipped?

A: 因为缺少依赖库。测试套件会自动检测可用的库，并智能地跳过无法运行的测试。

Because of missing dependencies. The test suite automatically detects available libraries and intelligently skips tests that cannot run.

### Q2: 如何运行完整测试？/ How to run full tests?

A: 安装所有依赖后运行：

Install all dependencies and run:

```bash
pip install -r requirements.txt
python test_suite_runner.py --full
```

### Q3: 测试通过就代表代码没问题吗？/ Does passing tests mean the code is bug-free?

A: **不是**。这些测试只验证基本逻辑，不验证ML模型准确率或实际性能。

**No.** These tests only validate basic logic, not ML model accuracy or actual performance.

### Q4: 我需要GPU吗？/ Do I need a GPU?

A: **不需要**。基础测试和数据处理测试都不需要GPU。

**No.** Basic tests and data processing tests don't require GPU.

## 技术细节 / Technical Details

### 测试框架 / Test Framework

- **Python unittest** - Python标准库
- **无额外依赖** - 不需要pytest
- **跨平台** - Windows, Linux, Mac

### 测试统计 / Test Statistics

- **总测试数 / Total Tests**: 29+ (基础) / 37+ (含数据处理)
- **测试文件 / Test Files**: 5个
- **测试类 / Test Classes**: 15+
- **代码覆盖 / Code Coverage**: 核心逻辑 ~40%

### 性能 / Performance

- **基础测试 / Basic Tests**: < 0.1秒
- **数据处理测试 / Data Processing**: < 0.5秒
- **集成测试 / Integration**: < 1秒
- **总计 / Total**: < 2秒 (无ML依赖)

## 贡献 / Contributing

欢迎添加更多测试！

Welcome to add more tests!

**测试要求 / Test Requirements:**
1. 使用unittest框架
2. 添加清晰的文档字符串
3. 遵循现有命名约定
4. 包含中英文注释

## 许可 / License

与主项目相同 / Same as main project

---

**总结 / Summary:**

这是一个**工程级别**的测试套件，可以：
- ✅ 在本地运行
- ✅ 证明代码逻辑正确
- ✅ 不需要ML依赖
- ✅ 快速反馈（< 1秒）
- ✅ 易于理解和扩展

This is an **engineering-grade** test suite that:
- ✅ Runs locally
- ✅ Proves code logic works
- ✅ Doesn't require ML dependencies
- ✅ Fast feedback (< 1 second)
- ✅ Easy to understand and extend
