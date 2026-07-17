# Task 004: Query Helpers And best_config

## 1. 这个 task 做了什么？

- 在 `hpc_agent/db.py` 中新增 `find_fastest_run(db_path, unknowns)` 查询 helper。
- 新增 `hpc_agent/tools.py`，实现第一个 benchmark tool：`best_config(db_path, unknowns)`。
- `best_config` 可以返回指定 `unknowns` 下 `time_sec` 最低的配置。
- 找不到数据时返回结构化空结果，而不是抛出模糊错误。
- 新增 `tests/test_tools.py`，覆盖最快配置和 missing `unknowns` 两种情况。

## 2. 为什么要这样做？

Task 4 把已经导入 SQLite 的 benchmark data 变成可查询的分析结果，形成第一条 tool calling 数据路径：

```text
benchmark_runs -> find_fastest_run -> best_config -> structured result
```

这一步是后续中文 router、CLI `ask`、Markdown report 的基础。没有这个 tool，Agent-style interface 只能识别问题，不能真正回答 benchmark 问题。

## 3. 为什么这样设计目录或模块？

- `db.py` 负责 SQLite 连接、schema 和底层查询 helper。
- `tools.py` 负责面向用户意图的工具函数，比如 `best_config`、后续的 `compare_modes` 和 `scaling_report`。
- 测试放在 `tests/test_tools.py`，因为验收目标是 tool 行为，而不是 SQL 语句本身。

这个边界让 SQL 查询可以复用，同时让上层 CLI 或 router 只处理结构化 tool result。

## 4. 为什么选择这种实现方式？

`find_fastest_run` 使用简单的 SQL：

```sql
WHERE unknowns = ?
ORDER BY time_sec ASC
LIMIT 1
```

这直接对应“最快配置”的定义，deterministic、容易测试，也适合当前 MVP。结果返回 `dict`，方便后续 CLI 输出、router 调用和 report generation。

缺失数据时返回：

```python
{"found": False, "unknowns": ..., "message": "..."}
```

这样 CLI 不需要用异常控制正常的“查不到数据”分支。

## 5. 为什么不使用其他方案？

- 不使用 Pandas：当前查询是 SQLite 擅长的 `ORDER BY + LIMIT`，不需要把数据拉到内存再排序。
- 不在 `tools.py` 里直接写 SQL：底层数据库访问留在 `db.py`，tool 层保持更接近业务问题。
- 不抛异常表示 missing `unknowns`：查不到数据是正常用户输入场景，结构化空结果更适合 CLI 和 report。
- 不做复杂对象模型：当前字段较少，`dict` 足够清楚，后续稳定后可再引入 dataclass。

## 6. 关键代码/设计点

- `find_fastest_run` 设置 `sqlite3.Row`，让查询结果可以按字段名转成 `dict`。
- SQL 使用参数绑定 `?`，避免拼接 SQL。
- 排序除了 `time_sec ASC`，还加了 `total_cores`、`ranks`、`threads` 作为 tie-breaker，让相同 runtime 时结果稳定。
- `best_config` 输出包含 ranks、threads、total cores、runtime、iterations、source file 和 logfile，满足 Task 4 acceptance criteria。

## 7. 面试官可能怎么问？

- 基础理解问题：`best_config` 的输入和输出是什么？
- 设计取舍问题：为什么把 SQL helper 放在 `db.py`，而不是直接写在 CLI 里？
- 替代方案对比问题：为什么不用 Pandas 找最小值？
- 面试追问问题：如果多个配置 runtime 相同，你如何保证结果稳定？

## 8. 我应该如何回答？

我先把 benchmark CSV 导入 SQLite，然后实现了第一个 deterministic tool：`best_config`。底层 `db.py` 用 SQL 查询指定 `unknowns` 下 `time_sec` 最低的 row，`tools.py` 把它整理成后续 router 和 CLI 都能使用的结构化结果。这样设计的好处是数据查询、业务 tool 和用户界面边界清楚，也方便测试和复现。

## 9. 自测问题

- 为什么最快配置用 `time_sec` 排序，而不是 `total_cores`？
- 如果用户问一个数据库里不存在的 `unknowns`，返回什么？
- `source_file` 和 `logfile` 对 benchmark reproducibility 有什么帮助？
- 为什么 SQL 要使用参数绑定？
- 如果未来要返回每个 `total_cores` 下的最快配置，应该扩展哪个模块？

## 10. 一句话总结

一句话：Task 004 实现了第一个可复现 benchmark analysis tool，让 SQLite memory 可以回答“某个 problem size 下最快配置是什么”。
