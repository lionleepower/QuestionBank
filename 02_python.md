# 问题与批改记录

这个文件用于记录学习 Bash、CSV、Slurm 和 benchmark 脚本时问过的问题、自己的回答、批改反馈和最后应记住的结论。

以后新增问题时，建议使用这个格式：

```markdown
## YYYY-MM-DD：问题标题

**我的问题**

...

**我的理解 / 回答**

...

**批改**

...

**记住**

...
```

## 2026-06-17：Bash 是什么，是编译器还是 shell？

**我的问题**

Bash 是什么？它像编译器一样，还是类似 shell？

**批改**

Bash 更像 shell，不是编译器。Shell 是你和操作系统对话的命令解释器；Bash 是 shell 的一种。

Bash 可以做两件事：

- 交互式执行命令，例如 `ls`、`cd`、`bash script.sh`。
- 按顺序解释执行 `.sh` 脚本里的命令。

**记住**

```text
Bash = 终端里的命令解释器 + 脚本执行器
```

在 benchmark 项目里，Bash 负责指挥流程：读取 CSV、循环参数、设置环境变量、运行程序、保存日志、生成结果 CSV。

## 2026-06-17：`RANKS=16` 一次只能设一个数字吗？

**我的问题**

在 shell 中，设定 `RANKS=16` 之类的是不是一次只能设定一个数字，除非使用 `"${}"`？

**批改**

不是。Shell 变量本质上通常是字符串。它可以保存一个数字，也可以保存一串用空格分开的数字。

可以这样写：

```bash
RANKS=16
RANKS="1 2 4 8 16"
```

如果值里面有空格，赋值时要加引号。原因不是 `"${}"`，而是空格在 shell 里会分隔命令和参数。

这个写法是错的：

```bash
RANKS=1 2 4 8
```

Bash 会理解成：临时设置 `RANKS=1`，然后尝试执行一个叫 `2` 的命令。

**记住**

```text
赋值时：有空格就加引号，例如 RANKS="1 2 4 8"
使用时：推荐写 "${RANKS}"
```

## 2026-06-17：Bash 变量赋值等号两边能不能有空格？

**我的问题 / 理解**

我懂了，等号两边不能有空格。

**批改**

对，这是 Bash 变量赋值的关键规则。

正确：

```bash
RANKS=16
RANKS="1 2 4"
MAX_CORES=128
```

错误：

```bash
RANKS = 16
RANKS= 16
RANKS =16
```

`RANKS = 16` 会被 Bash 理解成：执行一个叫 `RANKS` 的命令，参数是 `=` 和 `16`。

**记住**

```text
Bash 变量赋值：等号两边不能有空格。
值里有空格：值整体加引号。
```

## 2026-06-17：`#!/usr/bin/env bash`

**我的回答**

告诉系统，使用 `/usr/bin/env` 中的 bash 来运行下面的指令。

**批改**

方向对，但更准确是：告诉系统用 `/usr/bin/env` 在当前 `PATH` 里找到 `bash`，然后用这个 Bash 执行脚本。

不是 `/usr/bin/env` 里面有一个 Bash，而是 `env` 帮你查找 Bash。

**记住**

```text
#!/usr/bin/env bash
= 用当前环境能找到的 bash 来运行这个脚本
```

## 2026-06-17：`set -euo pipefail`

**我的回答**

`-e` 是 exit，一有错误就中断；`-u` 是 undefined，有未定义的变量就中断；`-o pipefail` 是管道传输中途失败也算失败。

**批改**

这个回答合格。

可以再记细一点：

- `set -e`：命令失败就停止。
- `set -u`：读取未定义变量就停止。
- `set -o pipefail`：管道中任意一步失败，整个管道都算失败。

**记住**

benchmark 脚本宁可早停，也不要生成错误 CSV。

## 2026-06-17：为什么推荐 `"${PROJECT_ROOT}"` 而不是 `$PROJECT_ROOT`？

**我的回答**

`""` 可以确保变量名被保留为一个完整的路径，不用的话 Bash 可能会造成 word splitting 和 glob expansion。

**批改**

回答正确。小拼写：是 `word splitting`。

更准确地说，双引号保护的是变量展开后的值。如果路径里有空格，例如 `/some/path with space/project`，写 `$PROJECT_ROOT` 可能会被拆成多个参数；写 `"${PROJECT_ROOT}"` 会保留成一个完整路径。

**记住**

```bash
cd "${PROJECT_ROOT}"
```

比：

```bash
cd $PROJECT_ROOT
```

更安全。

## 2026-06-17：`SCALES="${SCALES:-small}"`

**我的回答**

`SCALES` 的默认值就是 `small`，`:-` 就是设置默认值的意思。

**批改**

方向对。更准确是：如果 `SCALES` 没有设置，或者是空字符串，就使用 `small`；然后把结果赋值给 `SCALES`。

注意，真正表示“默认值”的是 `:-` 这个组合，不是单独的 `-`。

**记住**

```bash
SCALES="${SCALES:-small}"
```

可以理解为：

```text
如果外部传了 SCALES，就用外部的。
否则默认用 small。
```

## 2026-06-17：为什么 benchmark 不适合手动一条条跑？

**我的回答**

命令太多，可能会漏掉参数。

**批改**

正确。可以再补充：还容易复制错参数、日志文件名不统一、结果 CSV 不完整、实验不可复现。

**记住**

脚本的价值是把重复、机械、容易出错的 benchmark 流程自动化。

## 2026-06-17：`"$(dirname "${BASH_SOURCE[0]}")"` 是什么意思？

**我的问题**

`"$(dirname "${BASH_SOURCE[0]}")"` 这个是什么意思？

**批改**

这段代码的作用是：找到当前脚本文件所在的目录。

它可以拆成三层：

- `${BASH_SOURCE[0]}`：当前这个脚本文件的路径。
- `dirname ...`：取出路径里的目录部分。
- `$(...)`：先运行括号里的命令，再把命令输出替换到这里。

例如脚本路径是：

```text
/home/leyan/leyan/jobSkill/scriptlearning/scripts/02_read_sizes_csv.sh
```

那么：

```bash
dirname "${BASH_SOURCE[0]}"
```

输出：

```text
/home/leyan/leyan/jobSkill/scriptlearning/scripts
```

**记住**

```bash
"$(dirname "${BASH_SOURCE[0]}")"
```

可以理解为：

```text
当前脚本所在的文件夹
```

## 2026-06-17：`while ... done < file` 和 `if ... fi` 怎么理解？

**我的问题**

`while IFS=, read -r SCALE M N UNKNOWNS; do ... done < "${SIZE_TABLE}"` 里，`while` 和 `done` 是并列的吗？`done < "${SIZE_TABLE}"` 是不是把文件传给了 `while`？`fi` 是不是表示 `if` 结束？

**批改**

`while` 和 `done` 是一组结构的开头和结尾，不是两个独立命令的并列关系。

```bash
while 条件; do
  循环体
done
```

`done < "${SIZE_TABLE}"` 的意思是：把 `${SIZE_TABLE}` 这个文件作为整个 `while` 循环的输入。于是每循环一次，`read` 就从这个文件里读一行。

`if` 的结束确实是 `fi`：

```bash
if 条件; then
  条件成立时执行
fi
```

**记住**

```text
if 的结束是 fi
while/for 的结束是 done
case 的结束是 esac
```

`fi` 就是 `if` 反过来写，`esac` 就是 `case` 反过来写。

## 2026-06-17：`dirname` 有什么用，必须配合 `BASH_SOURCE[0]` 吗？

**我的问题**

`dirname` 到底有什么用？它必须和 `BASH_SOURCE[0]` 配合使用吗？如果只是显示路径，`"$(dirname "${BASH_SOURCE[0]}")"` 好像和 `(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)` 等价。

**批改**

`dirname` 的作用是：从一个路径里取出“目录部分”。它不必须和 `BASH_SOURCE[0]` 配合，可以处理任何路径。

例如：

```bash
dirname "/home/leyan/a/b.txt"
```

输出：

```text
/home/leyan/a
```

`"$(dirname "${BASH_SOURCE[0]}")"` 和 `(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)` 不完全等价。

- 前者只取目录，可能是相对路径，例如 `scripts`。
- 后者先进入这个目录，再用 `pwd` 输出绝对路径，例如 `/home/leyan/leyan/jobSkill/scriptlearning/scripts`。

**记住**

```bash
dirname path
```

只负责“切掉文件名，留下目录”。

```bash
cd "$(dirname path)" && pwd
```

负责“切掉文件名，进入目录，再得到绝对路径”。

## 2026-06-17：`if (( line_no == 1 )); then continue; fi` 能不能写成 `[[line_no == 1]] && continue`？

**我的问题**

`if (( line_no == 1 )); then continue; fi` 是不是和 `[[line_no == 1]] && continue` 等价？

**批改**

不等价。你写的 `[[line_no == 1]]` 有两个问题：

- `[[` 和 `]]` 两边必须有空格。
- `line_no` 在 `[[ ... ]]` 里如果不写 `$line_no`，会被当成普通字符串 `line_no`，不是变量值。

原写法：

```bash
if (( line_no == 1 )); then
  continue
fi
```

可以简写成：

```bash
(( line_no == 1 )) && continue
```

如果用 `[[ ... ]]`，应该写：

```bash
[[ "${line_no}" == "1" ]] && continue
```

**记住**

数字比较优先用：

```bash
(( line_no == 1 ))
```

字符串比较才常用：

```bash
[[ "${name}" == "small" ]]
```

## 2026-06-17：`RANKS_LIST[@]` 的 `@` 是什么，为什么写 `P=$(( R * T ))`？

**我的问题**

`RANKS_LIST[@]` 里的 `@` 是不是代表等待传入的参数？还有 `P=$(( R * T ))` 为什么不能写成 `P=(( R * T ))`？

**批改**

`"${RANKS_LIST[@]}"` 是 Bash 数组展开，意思是取出数组里的所有元素。这里的 `@` 不是等待传入参数。

例如：

```bash
RANKS_LIST=(1 2 4)
for R in "${RANKS_LIST[@]}"; do
  echo "${R}"
done
```

会依次得到 `1`、`2`、`4`。

`P=$(( R * T ))` 的意思是：先计算 `R * T`，再把结果赋值给 `P`。

`$(( ... ))` 是算术展开，会产生一个值。例如 `R=2`、`T=4` 时：

```bash
P=$(( R * T ))
```

等价于：

```bash
P=8
```

`P=(( R * T ))` 是错误写法，因为 Bash 变量赋值右边需要是一个值，而 `(( R * T ))` 本身是算术判断/命令，不是可直接放在 `=` 右边的值。

**记住**

```bash
"${array[@]}"
```

表示数组中的所有元素。

```bash
P=$(( R * T ))
```

表示计算 `R * T`，并把计算结果赋值给 `P`。

## 2026-06-17：`((...))`、`$((...))` 和 `P=$R * $T` 的区别

**我的问题**

`((...))` 就像是条件判断，只会返回 0 或者 1；但是 `P=$(( R * T ))` 会返回一个数值。那么写成 `P=$R * $T` 是不是也可以？

**批改**

`(( ... ))` 是算术命令，常用于判断。它的退出状态是：

- 表达式结果非 0：命令成功，退出状态是 `0`。
- 表达式结果为 0：命令失败，退出状态是 `1`。

`$(( ... ))` 是算术展开，会把表达式计算成一个文本数值，适合赋值。

```bash
P=$(( R * T ))
```

会先计算 `R * T`，再把结果放进 `P`。

`P=$R * $T` 不可以表示乘法。Bash 会把空格分成不同的命令词，可能理解成：临时设置 `P=$R`，然后尝试执行 `*` 这个命令或展开当前目录文件名。

即使写成：

```bash
P=$R*$T
```

也只是把字符串 `2*4` 赋值给 `P`，不会计算成 `8`。

**记住**

```bash
P=$(( R * T ))
```

是 Bash 里做整数乘法并赋值的推荐写法。

## 2026-06-17：`local candidate="$1"` 里的 `$1` 是什么意思？

**我的问题**

`local candidate="$1"` 里面的 `$1` 是什么意思？

**批改**

`$1` 是第一个位置参数。在函数里面，它表示调用这个函数时传进来的第一个参数。

例如：

```bash
want_scale "small"
```

进入函数后：

```bash
$1
```

就是：

```text
small
```

所以：

```bash
local candidate="$1"
```

意思是：创建一个只在函数内部使用的局部变量 `candidate`，并把第一个参数保存进去。

**记住**

```text
$1 = 第一个参数
$2 = 第二个参数
$@ = 所有参数
```

在函数里，它们表示传给函数的参数；在脚本最外层，它们表示传给脚本的命令行参数。
