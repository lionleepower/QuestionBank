# Interview Questions

这个目录保存每个 task 完成后的面试导向理解检查问题。

目标不是背答案，而是帮助你确认自己真的理解了：

- 为什么要这样做
- 为什么要这样设计目录或模块
- 为什么选择这种实现方式
- 为什么暂时不使用其他替代方案
- 这个 task 背后的核心工程思想是什么
- 如果面试官问到这个设计，应该怎么回答

## 使用规则

每完成一个 task，就新增或更新一个对应文件。完成这个问题文件之后，才把 `tasks/todo.md` 里的 task 标记为完成。

命名格式：

```text
task_001_project_skeleton.md
task_002_sqlite_schema.md
task_003_csv_importer.md
```

建议流程：

1. 复制 `template.md`。
2. 按 task 编号和主题重命名。
3. 填入本次 task 实际改动过的文件、命令和设计选择。
4. 至少写出基础理解、设计取舍、替代方案、面试追问和一句话总结。
5. 用自己的话口头回答一遍“我应该如何回答”部分。

## 文件清单

- [task_001_project_skeleton.md](task_001_project_skeleton.md): 项目骨架、目录结构和样例 fixture
- [task_002_sqlite_schema.md](task_002_sqlite_schema.md): SQLite schema、索引和幂等初始化
- [task_003_csv_importer.md](task_003_csv_importer.md): CSV importer、类型转换和 source tracking

## 质量标准

好的问题文件应该：

- 中文为主，保留关键 English terms。
- 多问“为什么”，少问“是什么”。
- 能服务 README 讲解、简历项目描述和技术面试。
- 直接引用本仓库的文件名、模块名和命令。
- 明确哪些设计是 MVP 选择，哪些是未来扩展。
