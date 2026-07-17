# Task 003: CSV Importer

## 1. 这个 task 做了什么？

- 新增 `hpc_agent/importer.py`，实现 `import_csv(csv_path, db_path)`。
- 使用 Python 标准库 `csv.DictReader` 读取 `size_grid` CSV fixture。
- 将整数列转换为 `int`，`time_sec` 转换为 `float`。
- 校验 `unknowns == m * n`，避免把问题规模错误的数据写入 SQLite。
- 插入 `benchmark_runs` 表时补充 `source_file`，保留数据来源。
- 新增 `tests/test_importer.py`，验证导入行数、SQLite 类型、source tracking 和错误校验。

## 2. 为什么要这样做？

SQLite schema 只是存储结构，Task 3 让真实 CSV 数据进入这个结构，形成第一条可运行的数据流：

```text
examples/size_grid_1000000_sample.csv -> import_csv -> benchmark_runs
```

这一步之后，后续 `best_config`、`compare_modes`、`scaling_report` 才能基于真实数据查询，而不是写死样例。

## 3. 为什么这样设计目录或模块？

`importer.py` 只负责 CSV 到 SQLite 的 ingestion，不负责查询最优配置、不负责计算 speedup、不负责生成 Markdown。这样边界清楚：

- `db.py`: 创建连接和 schema。
- `importer.py`: 读取 CSV、转换类型、插入数据库。
- `tools.py`: 后续面向用户问题的 query tools。

这个边界让每个模块都能独立测试，也方便面试时解释 data pipeline。

## 4. 为什么选择这种实现方式？

第一版使用标准库 `csv.DictReader`，因为 fixture 是普通 CSV，字段名和 schema 基本一致，不需要一开始引入 Pandas。显式类型转换虽然朴素，但容易读、容易测试，也能清楚说明哪些字段是 benchmark metadata，哪些字段是 numeric metrics。

`import_csv` 返回导入行数，这让 CLI 或测试可以直接确认导入是否真的发生。

## 5. 为什么不使用其他方案？

- 不使用 Pandas：当前只是逐行导入 CSV，Pandas 会增加依赖和学习成本。
- 不直接用 SQLite `.import`：Python importer 可以做类型转换、source tracking 和 `unknowns == m * n` 校验。
- 不在 importer 里自动创建 schema：当前测试和 workflow 显式调用 `initialize_database`，让 storage 初始化和 data ingestion 边界更清楚。
- 不支持目录批量导入：Task 3 的目标是先导入一个 fixture，批量目录导入可以后续加到 CLI 或 importer wrapper。

## 6. 关键代码/设计点

- `INTEGER_COLUMNS` 和 `REAL_COLUMNS` 明确哪些字段需要数值化。
- `source_file` 使用传入的 CSV 路径，保证每条 row 可追溯。
- `ValueError` 在 `unknowns` 与 `m * n` 不一致时提前失败，避免 silent bad data。
- 测试用 SQLite 的 `typeof()` 验证 `unknowns` 是 `integer`、`time_sec` 是 `real`。

## 7. 面试官可能怎么问？

- 基础理解问题：这个 importer 的输入和输出是什么？
- 设计取舍问题：为什么 importer 不负责计算最快配置？
- 替代方案对比问题：为什么不用 Pandas 或 SQLite CLI 直接导入？
- 面试追问问题：如果 CSV 字段缺失、格式变化、或者要导入整个目录，你会怎么扩展？

## 8. 我应该如何回答？

我实现了一个小的 CSV ingestion layer，把 sanitized benchmark fixture 导入 SQLite 的 `benchmark_runs` 表。这里我刻意保持 importer 职责单一：只做 CSV parsing、type conversion、basic validation 和 source tracking，不做分析逻辑。这样后续 tool functions 可以在结构化数据上做 deterministic query，也方便测试每个阶段是否正确。

## 9. 自测问题

- 为什么 `time_sec` 必须转成 `float`，不能一直保存为字符串？
- `source_file` 对 reproducibility 有什么帮助？
- 为什么要校验 `unknowns == m * n`？
- 如果 importer 成功返回 36，但数据库里没有 36 行，应该先查哪里？
- 如果未来要导入多个 CSV，应该扩展 `import_csv` 还是增加一个 wrapper？

## 10. 一句话总结

一句话：Task 003 把真实 benchmark CSV fixture 可靠地导入 SQLite，让项目从“有 schema”进入“有可查询数据”的阶段。
