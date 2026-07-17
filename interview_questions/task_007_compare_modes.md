# Task 007: compare_modes（mpi_like vs hybrid_like 对比工具）

> 状态：Q1–Q5 已作答并批改（2026-07-14）。第 1–5、7–10 节由 Claude 代写（约定见 CLAUDE.md 工作流），模拟面试会从代写章节抽问。
> **返工清单（周末模拟必抽）**：Q1 后半（tool description 对应机制）、Q2 后两问（SQL 放 db.py 的真正理由、原 find_fastest_run 差在哪）、Q3 整题（语义边界）、Q5 第二三问（"快 1.13 倍"歧义、舍入放哪层）。

## 1. 这个 task 做了什么？

- `compare_modes(db_path, unknowns)`：对同一 problem size，分别找出 mpi_like（threads = 1）和 hybrid_like（threads > 1）两种模式各自最快的一次运行，返回结构化对比结果：两组配置、`faster` 标签、`time_ratio`（恒 ≥ 1 的 slower/faster）。缺任一模式或查无数据时返回 `found: False` + message。
- `db.find_fastest_run` 增加可选参数 `mode: str | None = None`：`None` 时行为与原来完全一致（`best_config` 零改动），传模式标签时通过固定谓词字典 `_MODE_PREDICATES` 追加 WHERE 条件。
- `router.route` 增加 COMPARE_KEYWORDS 分支（你主写）：命中"对比/比较" → `{"intent": "compare_modes", "unknowns": <int|None>}`，且该检查排在 BEST_KEYWORDS 之前——顺序即优先级。
- `router.ask` 增加 compare dispatch 分支（你主写）：缺规模反问、`found: False` 透传 tool 的 message、成功则渲染含两组配置和结论的中文回答。
- 主要文件：`hpc_agent/tools.py`、`hpc_agent/db.py`、`hpc_agent/router.py`
- 验证命令：`python -m pytest`（43 通过），以及现场 demo：

  ```bash
  python -m hpc_agent import-csv examples/size_grid_1000000_sample.csv
  python -m hpc_agent ask "对比一下100万规模下mpi和hybrid模式"
  ```

## 2. 为什么要这样做？

- 解决的实际问题：`best_config` 只能回答"谁最快"，回答不了 ARCHER2 数据里最有价值的问题——**同样的核数预算，纯 MPI 和 hybrid 哪种用法更划算**（样例数据里 128×1 vs 64×2 同为 128 核，时间差 13%）。这是论文 profiling 结论能接上的第一个工具。
- 服务可复现 data flow：两条确定性 SQL，同一 db 永远给同一结论；tie 规则显式写进 ORDER BY，不依赖插入顺序。
- 服务 Agent-style tool calling：这是第二个真正的 tool，router 因此第一次面对**多工具选择冲突**（"对比…最快…"同时命中两组关键词）——这正是 LLM function calling 里 tool selection 问题的最小复现（见 Q1）。

## 3. 为什么这样设计目录或模块？

- SQL 全部留在 `db.py`：沿用 `find_fastest_run` 的先例，`tools.py` 只做业务组装（调用、判空、组装 dict），`router.py` 只做渲染（见 Q2）。
- `compare_modes` 返回结构化 dict 而非文案：`found` / `message` 的形状与 `best_config` 对齐，`ask` 层对两种 `found: False` 一视同仁地透传 message，不需要区分是哪种失败。
- 刻意不放进来的：单模式降级回答（缺一个模式就整体 `found: False`，语义边界见 Q3）；efficiency/speedup 等派生指标（属于 metrics 模块，D4 报告再汇合）；数值四舍五入（tool 层保留全精度，舍入是渲染层的事，见 Q5）。

## 4. 为什么选择这种实现方式？

- **两条简单 SQL 而非一条窗口函数**：本地 SQLite + `(unknowns, ranks, threads, total_cores)` 索引，两次点查开销可忽略，可读性和"缺哪个模式"的判断都最直白（完整取舍见 Q2）。
- **可选参数而非新函数**：`mode=None` 默认值让老调用者一行不改——参数默认值的全部意义就在这里。
- **固定谓词字典**：`_MODE_PREDICATES[mode]` 拼进 SQL 的只可能是自己写死的两个字符串，未知标签 KeyError 快速失败；数据值仍走 `?` 占位符。f-string 拼 SQL 片段和参数绑定是两种机制，外部输入永远只走后者。
- **tie 规则复用 `find_fastest_run` 的 ORDER BY**（time_sec, total_cores, ranks, threads 全升序）；两模式打平时 `<=` 让 mpi_like 拿 `faster` 标签——测试未钉死这一点，但策略是显式选择而非碰巧。
- **`time_ratio` 定义为 slower/faster**：恒 ≥ 1，渲染层不需要判方向（语义取舍见 Q5）。

## 5. 为什么不使用其他方案？

- 替代方案 1：一条 SQL，`ROW_NUMBER() OVER (PARTITION BY (threads = 1) ORDER BY ...)` 取 `rn = 1`。
  为什么暂时不用：单机 SQLite 上没有往返成本可省，代价是可读性和"哪个模式缺失"的判断复杂度。但要求自己能在白板上写出这个形状（面试常问"能不能一条 SQL"）。
- 替代方案 2：新函数 `find_fastest_run_by_mode`。
  为什么暂时不用：与 `find_fastest_run` 只差一个 WHERE 片段，近乎复制粘贴；可选参数在不破坏任何调用者的前提下消掉了这份重复。
- 替代方案 3：SQL 写在 `tools.py` 里。
  为什么暂时不用：打破"SQL 只出现在 db.py"的既有分层，schema 变更时要改的文件从一个变成多个。

## 6. 核心问题 Q1–Q5（week1 验收题）

### Q1 路由优先级 与 LLM tool selection

"对比100万规模下最快的mpi和hybrid配置"同时命中"对比"和"最快"两组关键词——你的 route 怎么保证 compare 赢？"更具体的意图先查"这条路由原则，换到 LLM function calling 里对应什么机制（模型怎么在两个都像的 tool 之间选）？

答：
优先判断compare, compare判断完之后再去判断”最快“或是”更快“；
对应的是决策环节中的LLM绝对调用哪一个参数

批改：前半 ✅（顺序即优先级，compare 在前）。**后半没答到点**："LLM 决定调用哪一个参数"不对——function calling 里没有 if 链，模型是一次性读**所有** tool 的 schema（name + description + parameters）后做选择。"更具体的意图先查"对应的机制是 **description engineering**：把 `compare_modes` 的描述写得比 `best_config` 更具体（"当用户想比较两种模式时用这个"），并在 `best_config` 的描述里显式排除（"仅当用户只要单个最优配置时用"）。**写 tool description = 写路由规则**；你的 if 链顺序，在 LLM 世界里变成了描述里的边界措辞。→ 返工。


### Q2 一条 SQL 还是两条、SQL 放哪、能否复用

你的实现是一条 SQL（按模式分组/窗口函数）还是两条（`WHERE threads = 1` / `threads > 1`）？为什么？SQL 放 `db.py` 还是 `tools.py`——`find_fastest_run` 的先例给了什么理由？它本身能被复用吗，差在哪？

答：
我实现的是两条sql查询，因为在规模不大的本地运行，可视化程度的重要性要大于两条sql查询所需要的空间，减少阅读成本；SQL放到了db.py，这样做可以减少调用成本，同时也可以复用，但可能会造成性能成本增加

批改：第一小问 ✅（注意术语："可视化程度"应说**可读性** readability，面试里说错会减分）。**第二小问答偏**：SQL 放 db.py 不是为了"调用成本/性能"——放哪儿性能都一样。真正的理由是**分层**：schema 知识和 SQL 集中在一个模块，schema 变更只改一个文件；tools.py 不懂 SQL 也能被阅读和测试；这是 `find_fastest_run` 树立的先例。**第三小问没答**：原 `find_fastest_run` **不能**直接复用——它没有 mode 过滤，两次调用返回的都是全局最快的同一行（你踩过这个坑：`where` 死代码时正是这个现象）。差的就是一个 WHERE 片段，所以用可选参数补上而不是复制函数。→ 返工后两问。

### Q3 缺模式时的语义边界

缺任一模式时为什么整体返回 `found: False`，而不是"有什么给什么"？对比工具的语义边界是什么？面试官反驳"返回仅有的那种不是更有用吗"，你怎么接？

答：
防止给用户造成误解；不知道什么叫语义边界；防止用户误判，强制让用户指明类型

批改："防止误解"是对的种子，但整题要返工。**语义边界 = 工具合同承诺的范围**：`compare_modes` 承诺的是"一个对比"，对比的前提是两边都在场。缺一边还返回数据，语义就从"对比"**静默降级**成"单边查询"——上层（渲染层或将来的 LLM）会把它当成对比结论输出："mpi 最快 3.866 秒"看起来像赢了比赛，实际上根本没有对手。**接反驳的标准姿势**："返回仅有的那种"这个需求已经有工具了——`best_config`。工具各守各的合同，靠**组合**而不是让单个工具身兼两职；`found: False` + message 让上层自己决定下一步（改问 best_config？提示用户补数据？）。这是 agent tool 设计的通用原则：**宁可明确失败，不要含糊成功**。"强制让用户指明类型"不是这回事，删掉这个说法。→ 返工。


### Q4 为什么叫 mpi_like / hybrid_like

SPEC 为什么把标签叫 `mpi_like` / `hybrid_like`，而不是直接叫 MPI / OpenMP hybrid？（提示：数据里只有 ranks/threads 两个数字，你能证明程序真的在用 OpenMP 吗？conservative label 和"简历不声称未实现的东西"是同一条原则。）

答：
数据中的使用多线程不一定能保证是否真的使用了openmp; 若是--with_openmp_kernel没有打开也就有可能表面上看着的是使用了openMP，但是实际上没有使用，所以使用hybrid_like更加准确一点

批改：方向 ✅——threads > 1 不能证明程序真的在用 OpenMP。但注意：`--with_open_kernel` 是你臆造的 flag 名（PETSc 里是 `--with-openmp` 这类 configure 选项）——面试里**说错 flag 名比不说更糟**，不确定就说"编译期是否启用了线程支持"。打磨后的说法：数据里只有 ranks/threads 两个数字，threads > 1 只能说明"每个 rank 分到了多个核"，线程可能闲置、库可能没编译线程支持——**标签只声称数据能证明的事**，`_like` 后缀就是这份克制。与"简历不声称未实现的模块"同一条原则。→ 措辞打磨，不返工。

### Q5 time_ratio 的方向、中文歧义、舍入的层次

`time_ratio` 为什么定义成 slower/faster（恒 ≥ 1）而不是固定 mpi/hybrid 方向？渲染中文时"快 1.13 倍"有歧义（快 13% 还是 1.13 倍速？），你的文案怎么避免？四舍五入应该发生在 tool 层还是渲染层，为什么？

答：因为不能保证hybrid就一定要比mpi快，我们同时也要考虑到硬件的具体架构，不同的结构带来的效果也是截然不同的；若是mpi比hybrid更快就会带来用户的误解；快 13% 还是 1.13 倍速都是一个意思我觉得没有必要改变；tool层吧，提前处理数据，但是我不知道渲染层是什么意思

批改：第一小问方向 ✅ 但没说完：固定 mpi/hybrid 方向时会出现 **0.88 这种小于 1 的比值**（"mpi/hybrid=0.88"——谁快？读者要心算倒数）；slower/faster ≥ 1 配合 `faster` 标签，**方向和幅度分开表达**，永远读作"慢的是快的 X 倍"。**第二小问 ❌**："快 13%"和"快 1.13 倍"不是一个意思——中文"快一倍"= 2 倍速，所以"快 1.13 倍"按字面 = 2.13 倍速，而实际数据是 hybrid **耗时** 1.13 倍 = 慢 13%，差了整整一倍。无歧义写法：**"hybrid 耗时是 mpi 的 1.13 倍"**（比耗时，不比速度）或"mpi 快 13%"。router.py 里"快了有 1.13 倍"正踩在这个坑上，要改。**第三小问 ❌ 且概念缺失**：渲染层就是 `ask()` 里把 dict 拼成中文句子的那段 f-string；tool 层是 `compare_modes` 返回 dict 的部分。舍入应在**渲染层**：tool 的输出是给程序消费的（D4 报告、metrics 还要用这个数），提前舍入 = 不可逆地销毁精度；显示成几位小数是"展示"的职责。你的代码其实已经做对了（tool 返回全精度、f-string 里 `:.2f`）——只是没意识到这就是答案。→ 返工第二、三小问。



## 7. 结对过程中暴露的追问（本次 session 实际踩过的坑）

以下每条都是你写代码时真实犯过的错。答案由 Claude 代答（2026-07-14）——**模拟面试抽问时你要能脱稿复述**，尤其是 7.1 的两条数据流。

### 7.1 死代码 `where`

构造了 `where` 变量但 SQL 字符串没加 `f` 前缀，mode 过滤完全没生效——两个模式的查询都返回**全局最快**的同一行。追问：为什么两个测试的报错形态完全不同？

答：关键在两个测试的**数据分布**不同。
- `picks_fastest`（fixture 里两种模式都有数据）：全局最快恰好是 mpi 那行（128×1, 3.866s），所以 `mpi_like` 断言**碰巧通过**；但 `hybrid_like` 槽位里装的也是这行——一个 threads=1 的行出现在 hybrid 位置 → 报"值不对"。
- `needs_both`（fixture 只导入一种模式）：本该缺失的那个模式，查询照样返回"全局最快"→ 两边都非 None → 走进 `found: True` 分支 → 报"found 应为 False 却是 True"。

教训：同一个 bug 在不同数据分布下报错形态完全不同；诊断时先问"这个值是沿哪条数据流来的"，而不是盯着断言那一行。

### 7.2 docstring 伪代码当真代码（`...` 与 `<n>`）

追问：`#` 注释、docstring、孤悬三引号字符串三者在解释器眼里分别是什么？

答：`#` 注释在词法分析阶段就被丢弃，运行时不存在；docstring 是"函数/类/模块第一条语句"位置的字符串字面量，被存进 `__doc__`，是**运行时可访问的数据**；孤悬在其他位置的三引号字符串是普通表达式语句，求值后立刻丢弃（效果像注释，但不是注释）。`...` 是内置常量 `Ellipsis` 的合法字面量，`<n>` 是普通字符——所以前者静默塞进 dict、后者原样出现在文案里，**都不报语法错**，只能靠测试比对暴露。这就是"伪代码占位符抄进真代码"危险的原因。

### 7.3 声明语法混进调用处（`mode|None`）

追问：`mode: str | None = None` 这一行里类型标注和默认值各管什么？为什么 `best_config` 一行都不用改？

答：`: str | None` 是**类型标注**——给人和工具看的元数据，运行时不强制；`= None` 是**默认值**——调用者省略该参数时自动填入。调用处只有两种合法形态：不传，或 `mode="mpi_like"`；`mode|None` 是把声明语法搬进了调用处，变成对不存在变量的位或运算 → NameError。`best_config` 零改动的原因：它不传 mode → 默认 None → 谓词分支不触发 → SQL 与旧版逐字相同。**默认值的全部意义就是让既有调用者不用改**——这也是 Q2 选"可选参数"而非"新函数"的核心论据。

### 7.4 f-string 直接塞 dict

追问：为什么测试的 `"ranks=128" in answer` 匹配不到 `'ranks': 128`？

答：f-string 对 `{expr}` 求值后取其字符串形式，dict 的默认字符串形式是 repr：`{'ranks': 128, ...}`。而 `in` 是**逐字符的子串匹配**：`ranks=128`（等号连接）和 `'ranks': 128`（引号+冒号+空格）没有公共的完整片段 → False。正确做法是两层下标取出**标量**再自己拼文案：`f"ranks={result['mpi_like']['ranks']}"`。repr 是给程序员调试看的，永远不该直接出现在用户文案里。

### 7.5 `:2f` vs `:.2f`

追问：格式规约里 `.` 是什么开关？

答：f-string 格式规约的形状是 `[宽度][.精度][类型]`，`.` 是**精度**的开关。`:2f` = 最小宽度 2 + f 类型的默认 6 位小数（所以输出还是 1.130109）；`:.2f` = 保留 2 位小数。一个点的差别，"看起来格式化了"但精度根本没动——验证格式化是否生效要看输出，不能看代码"像不像改过"。

### 7.6 `==` 精确断言 vs `in` 宽松断言

追问：两种断言分别适合钉什么层的合同？为什么 tool 层用前者、渲染层用后者？

答：`==` 钉**结构合同**——tool 层输出给程序消费（router、将来的报告、LLM），字段名/类型/值必须逐位稳定，多一键少一键都是破坏合同；`in` 钉**要素合同**——渲染层输出给人看，文案要能自由打磨，测试只锁"必须出现的信息点"（规模、两组配置、耗时、谁快）。推论：改文案不应该跑挂任何 tool 测试，改 dict 字段必须跑挂 tool 测试——**测试的松紧度就是各层合同的松紧度**。"把测试注释抄成文案"能碰巧通过，正说明宽松断言锁不住语义，所以渲染质量要靠 review 而不是测试兜底。

## 8. 我应该如何回答？

> 我给分析层加了第二个 tool：对同一规模比较纯 MPI 式和 hybrid 式各自最快的运行。实现上我把 mode 过滤下沉到 db 层的 `find_fastest_run`，用可选参数加固定谓词字典，`None` 默认值保证既有调用者零改动；两条索引点查代替窗口函数，是在本地 SQLite 的量级上用最小复杂度换最大可读性。语义上我选择缺任一模式就整体 `found: False`——对比工具的合同是"给出可比的两边"，部分数据静默降级会让上层误读结论。router 里 compare 分支排在 best 之前，"更具体的意图先查"，这和 function calling 里靠 tool description 区分相邻工具是同一个问题的两种解法。

## 9. 自测问题

- 不看代码，能写出 `compare_modes` 成功返回的完整 dict 形状吗（包括嵌套层）？
- 能在白板上写出窗口函数版的 SQL 吗？写完能说出为什么没采用吗？
- 再加第三个意图（比如"efficiency 是多少"），route 的 if 链要怎么排？"顺序即优先级"会在几个意图时开始腐化，怎么办？
- demo 现场 `ask` 输出错了：是路由错、解析错、tool 错还是渲染错——各用哪条命令最快定位？

## 10. 一句话总结

一句话：用一个可选的 mode 参数把"按模式找最快"下沉到 db 层，上层组装出第一个真正的对比工具，router 也第一次用"顺序即优先级"解决了多工具冲突——这正是 LLM tool selection 的最小可复现版本。
