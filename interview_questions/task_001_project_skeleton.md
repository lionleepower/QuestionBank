# Task 001: Project Skeleton And Sample Fixture

## 1. 这个 task 做了什么？

- 创建了 MVP 项目的基础目录：`hpc_agent/`、`tests/`、`examples/`、`data/`、`reports/`。
- 增加了一个 sanitized CSV fixture：`examples/size_grid_1000000_sample.csv`。
- 增加了基础测试，确认目录存在、fixture 存在、公开样例没有暴露本地或集群绝对路径。

## 2. 为什么要这样做？

这个 task 的目标是先做出一个最小、可运行、可复现的项目骨架。对于 benchmark 项目，不能只写代码，还要能说明数据从哪里来、结果放在哪里、测试怎么验证。

`examples/` 里的 small fixture 让后续 importer、SQLite schema、query tools 都可以在本地快速验证，不依赖完整 ARCHER2 数据目录。

## 3. 为什么这样设计目录或模块？

- `hpc_agent/` 放 Python package，后续 CLI、importer、tools、router 都在这里。
- `tests/` 放自动化测试，让每个 task 有可验证结果。
- `examples/` 放小型公开样例，服务 README demo 和单元测试。
- `data/` 放本地 SQLite 数据库，默认是生成物。
- `reports/` 放 Markdown 报告，服务展示和复盘。

这个边界让 source code、input fixture、generated data、generated report 分开，后续不会混乱。

## 4. 为什么选择这种实现方式？

项目先使用普通目录和 Markdown，而不是一开始引入复杂框架。这样更适合 MVP，因为每个文件的职责都容易解释，面试时也能清楚说明数据流：

```text
examples CSV -> importer -> SQLite data -> tools -> reports
```

## 5. 为什么不使用其他方案？

- 不直接使用完整原始 benchmark 目录：原始数据太大、路径可能包含敏感环境信息，不适合作为公开 demo 的第一步。
- 不一开始做 Docker 或 FastAPI：当前最重要的是证明数据流和分析逻辑能跑通，服务化可以等 CLI 稳定后再加。
- 不把 fixture 放进 `tests/`：fixture 也服务 README 和演示，不只是测试内部数据。

## 6. 关键代码/设计点

- `tests/test_project_skeleton.py` 检查项目目录和 fixture。
- fixture 中保留必要 benchmark 字段，但 redacts absolute paths。
- `data/.gitkeep` 和 `reports/.gitkeep` 让空目录能进入版本控制。

## 7. 面试官可能怎么问？

- 基础理解问题：这个项目的输入、处理过程、输出分别是什么？
- 设计取舍问题：为什么要单独建 `examples/`、`data/`、`reports/`？
- 替代方案对比问题：为什么不直接读完整原始数据目录？
- 面试追问问题：如果后续数据量变大，你会怎样组织 fixture 和真实数据？

## 8. 我应该如何回答？

我先搭了一个可复现的最小项目骨架，把代码、测试、样例输入、本地数据库和报告输出分开。这样做是为了让后续每个功能都能有明确输入和输出，也方便 README demo 和自动化测试。第一版只放 sanitized fixture，不直接依赖完整集群数据，避免路径泄露和环境不可复现的问题。

## 9. 自测问题

- 为什么 benchmark 项目需要 fixture？
- `examples/` 和 `data/` 的区别是什么？
- 为什么公开样例要 redacts absolute paths？
- 如果一个新 Codex session 接手，它应该先读哪些文件？

## 10. 一句话总结

一句话：Task 001 建立了项目的可复现骨架，让后续 benchmark memory 和 Agent-style analysis 可以从一个小而真实的 CSV fixture 开始。
