# Task 005: Metrics (speedup / efficiency / scaling_summary)

> 状态：Q1–Q10 已作答并批改（2026-07-09）。第 1–5、8–10 节由 Claude 代写（约定见 CLAUDE.md 工作流），模拟面试会从代写章节抽问。

## 1. 这个 task 做了什么？

- `speedup(baseline_time_sec, parallel_time_sec)`：计算 S(P) = T_baseline / T_parallel；任一时间 ≤ 0 抛 `ValueError`（fail fast，见 Q6）。
- `parallel_efficiency(baseline_time_sec, parallel_time_sec, workers)`：计算 E(P) = S(P) / P；workers ≤ 0 抛 `ValueError`；允许 E > 1（超线性，见 Q2）。
- `scaling_summary(db_path, unknowns)`：用窗口函数 SQL（`ROW_NUMBER() OVER (PARTITION BY total_cores ORDER BY time_sec)`）取每个核数下最快的一行，以单核最快 run 为 baseline，逐行算 speedup/efficiency，返回结构化 dict；无单核 baseline 时返回 `{"found": False, ...}` 而不抛异常。
- 主要文件：`hpc_agent/metrics.py`、`tests/test_metrics.py`
- 验证命令：`python -m pytest tests/test_metrics.py`

## 2. 为什么要这样做？

- 解决的实际问题：把 `benchmark_runs` 里的原始行（ARCHER2 真实运行数据）变成面试官/用户真正关心的问题的答案——"这个规模扩到 N 核还划算吗"。speedup/efficiency 是 HPC 性能分析的通用语言。
- 服务可复现 data flow：同一个 db 文件进来，结果完全确定（SQL 排序确定、纯函数无状态），CLI 跑两遍结果一致。
- 服务 Agent-style tool calling：`scaling_summary` 的返回值就是一个 tool result 的形状——结构化 dict、带 `found` 标志、查无数据时给可读的 message 而不是异常，router/agent 可以直接消费并转述给用户。

## 3. 为什么这样设计目录或模块？

- speedup/efficiency 是**纯函数**（输入数字、输出数字、无 I/O），可以脱离数据库单测，也能被任何上层复用；`scaling_summary` 是本模块唯一碰数据库的函数，SQL 和使用它的代码放在一起，改动时不用跨文件对照。
- 边界：`db.py` 管连接、schema、通用查询 helper；`metrics.py` 管性能指标的定义和计算；`tools.py` 管面向用户意图的工具封装。
- 刻意不放进来的：报告格式化（属于 report 层）、绘图、中文意图识别（属于 router）——metrics 只输出结构化数据，不关心展示。

## 4. 为什么选择这种实现方式？

- 窗口函数取组内最优行：语义精确（"每组最快的那一整行"）、跨数据库可移植（见 Q4），比 SQLite 特有的 bare-column 写法更站得住。
- `?` 占位符：防注入 + 类型绑定（见 Q8）。
- 输入校验 fail fast：坏数据在入口崩溃，而不是变成看似合理的 0/NaN 混进报告（见 Q6）。
- deterministic / testable / reproducible：纯函数 + 显式 ORDER BY + 固定 fixture 测试；同一 db 永远同一输出。

## 5. 为什么不使用其他方案？

- 替代方案 1：**pandas groupby**。暂时不用：数据量是几千行 SQLite 表，SQL 一步到位；引入 pandas 是新增重依赖（违反 Ask-first 边界），而且把"会写 SQL"这个面试信号换成了"会调库"。
- 替代方案 2：**SQLite bare-column 写法**（`GROUP BY total_cores` + `MIN(time_sec)` 直接 SELECT ranks/threads）。暂时不用：SQLite 文档保证但不可移植，PostgreSQL 直接报错；窗口函数是标准 SQL。
- 替代方案 3：**无单核 baseline 时抛异常**。不用：对 tool calling 来说"查无数据"是正常业务结果不是程序错误，结构化 miss 让 agent 能继续对话；异常会打断整条 tool 链。

## 6. 核心问题 Q1–Q5（week1 验收题）

### Q1 baseline 选取

baseline 为什么用「同规模最快的单核 run」，而不是 ranks=1 的任意 run、或所有单核 run 的平均值？如果数据里根本没有单核 run，你的 API 行为是什么、为什么这样设计？

答：同规模最快的单核 run可以在后续的多nodes环境中做一个很好的参照对比值，它是一个最接近理想性能上限的一个参考点；ranks=1 的任意 run不一定满足所有配置跑满128cores的要求，考虑到hpc的计算可能会有误差或是干扰，所有单核run的平均值将其也考虑进来便会拉大与理想性能的差距，也可能会对efficiency造成干扰；
{
            "found": False,
            "unknowns": unknowns,
            "message": f"No single-core baseline run found for unknowns={unknowns}.",
}

比起直接查无数据，这样可以直接说明原因，为后续的修改或是其它埋下伏笔

批改：
对 tool calling 来说**"查无数据"是正常业务结果，不是程序错误**；返回结构化 miss，agent 拿到后还能继续对话，抛异常则打断整条工具链。另外"ranks=1 的任意 run"那句你答跑偏了（128 cores 跟这题没关系）——正确的点很简单：ranks=1 不等于单核，threads 可能是 8，真正的判据是 total_cores = ranks × threads = 1。这两句改进文件里。

### Q2 efficiency > 100%

面试官问「parallel efficiency 大于 100% 合理吗？」——超线性加速物理上什么时候发生（提示：cache）？你的代码允许它出现吗？

答：合理的，
在使用多个计算节点时并且baseline选取不合理时就有可能会发生,造成t(1)缓慢，原因是；
1.单个cpu一次处理的数据量有限，可能会出现cache miss
2.bandwidth问题，多核一般bandwidth也更高，一次性处理的数据量会变多
允许，虽然效率增大，但是这也同样具有参考价值
单核时 数据装不进 cache，每轮迭代都要访问 DRAM；分到 16 核后每核的 工作集 变成 1/16，装进了 cache，访问全变成 cazhe hit，所以每个核单位速度变快，总加速超过 16 倍。

### Q3 min vs mean

同一个 total_cores 有多个配置/rep 时，为什么取 min(time_sec) 而不是 mean？什么场景下 mean（或 median）反而更对？

答：HPC 系统噪声是单向的——干扰只会让程序变慢，不会变快，我们要考虑到接近理想状态，取min(time_sec)是一个非常好的选择；但如果我们实验的次数足够多或是寻找那些”典型等待时间"，那些误差可能会被拉低，这时候取mean(median)反而可能是一个更好的选择

### Q4 GROUP BY 陷阱与窗口函数

`GROUP BY total_cores` + `MIN(time_sec)` 再顺手 SELECT ranks/threads，在标准 SQL 里为什么是错的？SQLite 为什么"碰巧"能用（bare column 语义）？窗口函数写法为什么更可移植？

答：GROUP BY会把相同的total cores直接压缩，但是在这里我们的rank and threads配置是多样化的，直接压缩或丢失消息；SQLite对这种语法更加宽容，SQLite 的 bare column 语义有一条具体保证：当聚合函数恰好是单个 MIN() 或 MAX() 时，裸列保证来自取到 min/max 的那一行——所以在 SQLite 里那种写法不是"碰巧"，是文档保证的行为；但 PostgreSQL 会直接报错拒绝执行，MySQL 的 ONLY_FULL_GROUP_BY 模式同样拒绝，这才是"窗口函数更可移植"的准确含义

### Q5 浮点比较

测试里为什么用 `pytest.approx` 而不是 `==`？浮点比较的坑一句话讲清。

答：pytest.approx是大概估计，==的要求则比较严格，经常会因为浮点的位数而报错，但是实际上答案是对的

## 7. 结对过程中暴露的追问（本次 session 实际踩过的坑）

### Q6 报错 vs 返回 0/NaN

time 为 0 或负数时，speedup 为什么必须 raise ValueError，而不是返回 0 或 `float('nan')`？提示：下游 `parallel_efficiency` 拿到 0 之后会发生什么？静默的错误值和立刻崩溃哪个更危险？

答：报错会直接终止流程的运行，而return 0或nan则不影响程序的继续执行，可能会插入错误的数据从而污染下游的分析结果以及报告，因为efficiency插在里面看起来就是一个正常的结果;静默的错误值对数据库来说更加危险

### Q7 ROW_NUMBER vs RANK

同一个 total_cores 下有两行 time_sec 并列最小时，`ROW_NUMBER()` 会返回几行？换成 `RANK()` 呢？对本 task 的输出契约（每个 total_cores 恰好一行）哪个才是对的？

答：ROW()只会返回一行，若是想保证CLI可复现应该加一个窗口的决胜列，RANK()会并列返回，但是可能直接跳号



### Q8 `?` 占位符 vs f-string 拼接

为什么 SQL 参数必须用 `?` 占位符，而不能用 f-string 把 unknowns 拼进 SQL 字符串？这个安全问题叫什么名字？给一个恶意输入的例子。

答：因为全部都是string的话数据和代码的边界就会消失，这是经典的sql injection 问题，比如说输入：` OR `1`=1`;可能会直接将整张表都返回；而且驱动会做类型绑定和语句预编译，不只是安全问题。

### Q9 两个 ORDER BY 各管什么

`OVER (PARTITION BY ... ORDER BY time_sec)` 里的 ORDER BY 和最外层的 `ORDER BY total_cores` 分别控制什么？删掉外层那个，测试还能稳定通过吗？为什么？（提示：`scaling_summary` 的 Python 代码对 `rows[0]` 有什么假设？）

答：内层升序排列time_sec，外层升序排列total_cores，外层删除之后排列的顺序就不固定，可能就与total_cores无关，而且我们的baseline本来假设的就是同等规模下跑的最快的数量，rows[0] 被 Python 代码假设为单核 baseline，没有外层 ORDER BY 这个假设就不成立。

### Q10 SQL 字符串的本质

`FROM conn` 为什么报 `no such table`？SQL 字符串和 Python 变量是什么关系？SQLite 的表名去哪里查（两种办法）？

答：因为第一个就是python变量，sql里根本不存在这个东西，sql字符串只是可以引用真实存在的数据库

1. grep -rn "CREATE TABLE" 
2. .schema benchmark_runs?我不知道这个命令是否正确，但我没有成功过

## 8. 我应该如何回答？

> 我在 metrics 模块实现了 speedup/efficiency 两个纯函数和 scaling_summary 查询。设计上把指标计算和数据库访问分开，SQL 用窗口函数保证取到的是"每个核数最快的那一整行"且跨数据库可移植。相比 pandas 或 SQLite 的 bare-column 捷径，这个写法依赖最少、语义最标准。输入校验 fail fast，查无 baseline 返回结构化 miss——因为下游是 agent tool calling，不能让脏数据静默污染报告，也不能让正常的"查无数据"打断工具链。后续扩展方向是把它接进 CLI ask 和 Markdown report。

## 9. 自测问题

- 不看代码，能说清楚 scaling_summary 的输入和输出结构吗？
- 面试官问「为什么不用 pandas 做这个聚合」，能回答吗？
- 换成 PostgreSQL，这段 SQL 要改什么？（提示：Q4 的 bare column、`?` 占位符风格）
- 出现 bug 时，知道先检查哪个文件或命令吗？

## 10. 一句话总结

一句话：以同规模最快单核 run 为 baseline，用窗口函数取每个核数的最优配置，输出带 speedup/efficiency 的可复现 scaling 表，作为后续 agent tool calling 的第一个分析型 tool。
