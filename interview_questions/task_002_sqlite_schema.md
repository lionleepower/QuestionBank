# Task 002: SQLite Schema Design

## 1. 这个 task 做了什么？

- 在 `hpc_agent/db.py` 中实现了 SQLite 连接和 schema 初始化。
- 创建了 `benchmark_runs` 表，保存 PETSc benchmark run 的元数据和性能结果。
- 创建了面向查询的 indexes：`unknowns`、`unknowns + total_cores`、`unknowns + ranks + threads + total_cores`。
- 增加了 `tests/test_db.py`，验证 parent directory 创建、schema 字段、indexes 和 idempotent initialization。

## 2. 为什么要这样做？

CSV 适合记录原始实验结果，但不适合反复做查询、筛选和分析。SQLite 把 benchmark CSV 转成 structured benchmark memory，让后续工具可以稳定回答：

- 某个 `unknowns` 下最快配置是什么？
- 不同 `total_cores` 的 runtime 如何变化？
- `threads = 1` 和 `threads > 1` 的配置有什么差异？

这一步是 Agent-style tool calling 的基础：Agent 或 router 不应该直接在杂乱 CSV 上临时搜索，而应该调用 deterministic tools 查询结构化数据。

## 3. 为什么这样设计目录或模块？

`hpc_agent/db.py` 只负责 database connection、schema creation 和后续 database helpers。它不负责 CSV parsing，也不负责计算 speedup 或生成报告。

这个边界让模块职责清楚：

- `db.py`: storage layer
- `importer.py`: CSV -> SQLite
- `metrics.py`: performance metric calculation
- `tools.py`: user-facing benchmark queries
- `report.py`: Markdown presentation

## 4. 为什么选择这种实现方式？

SQLite 是 Python 标准库直接支持的 embedded database，不需要启动服务，也不需要 Docker。对这个 MVP 来说，它足够支持结构化查询、索引和本地复现。

schema initialization 使用 `CREATE TABLE IF NOT EXISTS` 和 `CREATE INDEX IF NOT EXISTS`，所以重复运行不会破坏已有数据库。这对学习项目和 CLI workflow 很重要，因为用户可能多次运行初始化或导入命令。

## 5. 为什么不使用其他方案？

- 不使用 Pandas DataFrame 作为主存储：DataFrame 适合一次性分析，但不适合作为长期 queryable memory。
- 不使用 PostgreSQL：功能更强，但需要服务配置，增加 WSL 初期复杂度。
- 不使用 Redis：Redis 更适合 cache，不适合保存可复现 benchmark history 的第一版主存储。
- 不使用 graph database 或 MCP memory：当前数据是表格型 benchmark runs，relational schema 更简单、更容易解释。

## 6. 关键代码/设计点

- `connect(db_path)` 会创建数据库 parent directory，降低 CLI 使用门槛。
- `benchmark_runs` 保留 `source_file`，保证每条记录能追溯到原始 CSV。
- `unknowns` 是核心查询维度，因为项目约定 2D problem size 为 `m * n`。
- indexes 服务后续 `best_config`、`compare_modes` 和 scaling report 查询。

## 7. 面试官可能怎么问？

- 基础理解问题：为什么要把 CSV 导入 SQLite？
- 设计取舍问题：为什么第一版使用单表 `benchmark_runs`，而不是拆成多张表？
- 替代方案对比问题：为什么不直接用 Pandas 分析 CSV？
- 面试追问问题：如果数据量增加或需要多人访问，这个 storage layer 怎么演进？

## 8. 我应该如何回答？

我把 CSV benchmark 数据先结构化进 SQLite，因为后续的 Agent-style tools 需要稳定、可测试、可追溯的查询接口。第一版用单表是因为每一行就是一次 benchmark run，字段之间关系简单，避免过早设计复杂 schema。SQLite 不需要额外服务，适合 WSL 本地开发；如果后续数据量或并发需求变大，可以把 `db.py` 的接口保留，底层迁移到 PostgreSQL。

## 9. 自测问题

- `benchmark_runs` 表里的 `unknowns` 为什么重要？
- 为什么 schema initialization 要 idempotent？
- `source_file` 字段解决了什么复现问题？
- 当前 indexes 分别服务哪些查询？
- 如果没有 1-core baseline，后续 speedup 应该怎么处理？

## 10. 一句话总结

一句话：Task 002 把 CSV 文件背后的 benchmark runs 变成了可查询、可测试、可追溯的 SQLite benchmark memory。
