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

## 2026-06-25：`bash -n` 是检查语法吗？

**我的问题**

`bash -n` 是检查语法吗？

**批改**

是。`bash -n` 会读取 Bash 脚本并检查语法，但不会真正执行脚本里的命令。

例如在本地 WSL 可以写：

```bash
bash -n scripts/run/ksp/3d/run_3d_sizes.sbatch
```

如果没有输出，通常表示 Bash 语法检查通过。如果有语法错误，会显示 `syntax error` 之类的信息。

但它只检查语法，不检查运行时逻辑。

**记住**

```text
bash -n = 只解析脚本语法，不运行脚本。
```

它检查不出变量是否未定义、文件路径是否存在、`cc` 是否能编译成功、`srun` 参数是否合理。

## 2026-06-25：为什么 `bash -n` 检查不出很多 sbatch 问题？

**我的问题**

感觉 `bash -n 3d/run_3d_sizes.sbatch` 很多问题检查不出来。

**批改**

这个感觉是对的。`bash -n` 只回答“这是不是合法 Bash 语法”，不能回答“这个 benchmark 脚本能不能正确跑”。

例如这些问题，`bash -n` 通常检查不出来：

```bash
echo "${MAX_CORES}"
```

如果 `MAX_CORES` 没定义，语法仍然合法。只有真正运行脚本，并且脚本里有：

```bash
set -u
```

才会在读取未定义变量时报错。

它也检查不出：

- `SIZE_TABLE` 文件是否存在。
- `M`、`N`、`P`、`UNKNOWNS` 是否在使用前已经有值。
- PETSc 路径是否正确。
- `cc` 是否能链接 PETSc。
- `srun` 是否能在 HPC 集群上正常启动任务。

**记住**

```text
bash -n 检查语法。
set -euo pipefail + 小规模真实运行，才能暴露更多运行时问题。
```

本地 WSL 可以先做语法检查；HPC 集群上再用小规模参数做真实测试。

## 2026-06-25：`bash -2n` 是什么意思？

**我的问题**

`bash -2n` 是什么意思？

**批改**

`bash -2n` 不是常用的 Bash 语法检查写法，大概率是把 `bash -n` 打错了。

正确写法是：

```bash
bash -n script.sh
```

如果写成：

```bash
bash -2n script.sh
```

Bash 会尝试解析 `-2n` 这组选项，但 `-2` 不是 Bash 的合法选项，通常会报 `invalid option`。

**记住**

```text
检查 Bash 语法：bash -n 文件名
```

## 2026-06-25：3D 脚本里的 `cc ... -lpetsc -o "${EXE}"` 是什么意思？

**我的问题**

在 3D 脚本里，这段是什么意思？

```bash
echo "[BUILD] Compiling ${SRC_PROG} -> ${EXE}"
cc -O3 -fopenmp \
  -I"${PETSC_DIR}/include" -I"${PETSC_DIR}/${PETSC_ARCH}/include" \
  "${SRC_PROG}" -L"${PETSC_DIR}/${PETSC_ARCH}/lib" -Wl,-rpath,"${PETSC_DIR}/${PETSC_ARCH}/lib" -lpetsc -o "${EXE}"
```

**批改**

这段是在把自己的 3D C 程序编译成可执行文件。

整体意思是：

```text
用 Cray 的 C 编译器 wrapper cc，打开优化和 OpenMP，
找到 PETSc 的头文件和库文件，
把 3d-stencil.c 编译并链接成 3d-stencil 可执行程序。
```

各部分含义：

- `cc`：Cray 环境里的 C 编译器 wrapper，会配合 `PrgEnv-gnu` 和 `cray-mpich` 处理编译环境。
- `-O3`：开启较高级别优化，适合 benchmark。
- `-fopenmp`：开启 OpenMP 支持。
- `-I.../include`：告诉编译器去哪里找 PETSc 头文件，比如 `petscksp.h`。
- `"${SRC_PROG}"`：要编译的 C 源文件。
- `-L.../lib`：告诉链接器去哪里找 PETSc 库文件。
- `-Wl,-rpath,.../lib`：把 PETSc 库路径写进可执行文件，帮助运行时找到 `libpetsc.so`。
- `-lpetsc`：链接 PETSc 库。
- `-o "${EXE}"`：指定输出的可执行文件路径。

**记住**

2D 的 `ex2` 是 PETSc 自带 tutorial，所以可以用 PETSc 的 Makefile：

```bash
make -j PETSC_DIR="${PETSC_DIR}" PETSC_ARCH="${PETSC_ARCH}" ex2
```

3D 的 `3d-stencil.c` 是自己的程序，所以脚本手动写 `cc ...` 来编译和链接 PETSc。

## 2026-06-25：`(( T in THREADS_LIST )) && continue` 对吗？

**我的问题**

这个语法对吗？

```bash
(( T in THREADS_LIST )) && continue
```

**批改**

不对。Bash 的 `(( ... ))` 是算术表达式，里面不能用 Python 那种 `in` 来判断某个值是否在列表里。

如果只是遍历线程列表，应该直接写：

```bash
for T in "${THREADS_LIST[@]}"; do
  ...
done
```

这样 `T` 本来就只会来自 `THREADS_LIST`。

如果要判断 `R * T` 是否满足满节点 128 核，可以写：

```bash
(( R * T != 128 )) && continue
```

如果真的要判断某个值是否在数组里，可以写函数：

```bash
contains_thread() {
  local needle="$1"
  local t
  for t in "${THREADS_LIST[@]}"; do
    [[ "${t}" == "${needle}" ]] && return 0
  done
  return 1
}

contains_thread "${T}" || continue
```

**记住**

```text
Bash 里没有 (( x in array )) 这种数组包含判断。
```

数组包含判断通常用循环函数完成。

## 2026-06-25：`T=$(( 128 / R ))` 语法对吗？

**我的问题**

这个语法是对的吧？

```bash
T=$(( 128 / R ))
```

**批改**

对。这是 Bash 的整数算术表达式。意思是计算 `128 / R`，然后把结果赋值给 `T`。

例如：

```bash
R=16
T=$(( 128 / R ))
echo "${T}"
```

输出：

```text
8
```

注意 Bash 这里是整数除法。如果不能整除，会截断小数。

**记住**

```text
$(( ... )) = Bash 整数算术计算。
```

在 ARCHER2 单节点 128 物理核的设置里，如果 `R=16 32 64 128`，那么 `T=8 4 2 1`，可以保持：

```text
R * T = 128
```

## 2026-06-25：`contains_thread "${T}" || continue` 里的 `||` 是什么意思？

**我的问题**

这里面的 `||` 是什么意思？

```bash
contains_thread "${T}" || continue
```

就是 or 还是 if else 中的 else？

**批改**

`||` 是 OR，但在 Bash 里常用作“前面的命令失败时，才执行后面的命令”。

这句等价于：

```bash
if ! contains_thread "${T}"; then
  continue
fi
```

Bash 命令有返回状态：

- 返回 `0`：成功，表示真。
- 返回非 `0`：失败，表示假。

所以：

```bash
A || B
```

可以读成：

```text
如果 A 失败，就执行 B。
```

**记住**

```bash
contains_thread "${T}" || continue
```

可以读成：

```text
如果 T 不在允许的线程列表里，就跳过当前循环。
```

## 2026-06-25：`ts()` 函数是什么意思？

**我的问题**

`ts()` 这个函数是什么意思？

**批改**

`ts` 大概是 `timestamp` 的缩写。在脚本里：

```bash
ts() { date -Iseconds; }
```

意思是定义一个 Bash 函数。每次调用 `ts`，就执行：

```bash
date -Iseconds
```

它会输出当前时间，例如：

```text
2026-06-25T16:42:10+01:00
```

后面这样用：

```bash
echo "[RUN] $(ts) scale=${SCALE} ppn=${R} threads=${T}"
```

`$(ts)` 会运行 `ts` 函数，并把它输出的时间插入到字符串里。

**记住**

```text
ts() = 一个小函数，用来给日志和 CSV 记录当前时间。
```

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

## 2026-06-21：`--cpus-per-task="${T}"` 和 `OMP_NUM_THREADS="${T}"` 有什么区别？

**我的问题**

`--cpus-per-task="${T}"` 和 `OMP_NUM_THREADS="${T}"` 有什么区别？

**批改**

`--cpus-per-task="${T}"` 是给 Slurm 调度器看的，意思是：每个 task 向 Slurm 申请 `T` 个 CPU core。

`OMP_NUM_THREADS="${T}"` 是给 OpenMP 程序运行时看的，意思是：程序内部最多启动 `T` 个 OpenMP 线程。

它们控制的对象不同：

- `--cpus-per-task` 控制资源分配：Slurm 给这个 task 分多少 CPU。
- `OMP_NUM_THREADS` 控制程序行为：OpenMP 程序实际开多少线程。

所以在 MPI + OpenMP 或 hybrid benchmark 里，这两个值通常要对应起来：

```bash
export OMP_NUM_THREADS="${T}"
srun --ntasks="${R}" --cpus-per-task="${T}" ./my_program
```

这里总核心数通常可以理解为：

```text
总核心数 = RANKS * THREADS = ntasks * cpus-per-task
```

如果只写 `--cpus-per-task="${T}"`，Slurm 会分配 CPU，但程序不一定自动开 `T` 个 OpenMP 线程。

如果只写 `OMP_NUM_THREADS="${T}"`，程序可能开 `T` 个线程，但 Slurm 没有明确给每个 task 分配这么多 CPU，可能造成资源使用不匹配。

**记住**

```text
--cpus-per-task="${T}"：向 Slurm 申请每个 task 用 T 个 CPU。
OMP_NUM_THREADS="${T}"：告诉 OpenMP 程序每个进程开 T 个线程。
```

## 2026-06-21：第五章 Slurm/MPI/OpenMP 映射作业批改

**我的问题**

批改第五章：Slurm、MPI 和 OpenMP 的映射关系。

**批改**

整体方向正确，尤其是能看出 `--ntasks` 对应 MPI ranks，`--cpus-per-task` 对应 Slurm 分配的 CPU cores，`OMP_NUM_THREADS` 对应 OpenMP threads。

需要修正两个细节：

- `#SBATCH` 不是 Bash 命令。它对 Bash 来说像注释，但 `sbatch` 提交脚本时会读取这些行作为 Slurm 作业配置。
- `OMP_NUM_THREADS` 不是分配线程资源，而是告诉 OpenMP 程序每个 rank 内部开多少线程。真正向 Slurm 申请 CPU 资源的是 `--cpus-per-task`。

如果 `OMP_NUM_THREADS=8` 但 `--cpus-per-task=1`，就是 8 个线程抢 1 个 CPU core，容易造成 oversubscription，程序可能变慢，也可能影响同节点上的其他作业。

**记住**

```text
#SBATCH：Slurm 提交时读取的作业配置。
--ntasks="${R}"：通常对应 R 个 MPI ranks。
--cpus-per-task="${T}"：每个 rank 向 Slurm 申请 T 个 CPU cores。
OMP_NUM_THREADS="${T}"：每个 rank 内部开 T 个 OpenMP threads。
```

## 2026-06-21：CPU core 和 thread 的座位比喻

**我的问题**

开的线程就像是一个座位？而 CPU cores 就像是一个乘客？

**批改**

这个比喻方向反了。

更准确的理解是：

- CPU core 更像“座位”，是 Slurm / 机器分给你的硬件资源。
- thread 更像“乘客”或“干活的人”，是程序内部创建出来执行计算的单位。

例如：

```text
--cpus-per-task=4
OMP_NUM_THREADS=4
```

可以理解为：Slurm 给这个 task 分了 4 个座位，OpenMP 程序派出 4 个线程去坐这些座位干活。

如果：

```text
--cpus-per-task=1
OMP_NUM_THREADS=8
```

就是 1 个座位上有 8 个线程抢着用，容易造成 oversubscription，程序可能变慢。

**记住**

```text
CPU core = 硬件资源，像座位。
thread = 程序执行单位，像坐上去干活的人。
```

## 2026-06-21：awk 日志解析语法怎么用？

**我的问题**

`awk '/Time \(sec\):/{t=$3} END{print t}' "${LOG}"` 这种语法是如何使用的？请设计几个题目和文件，帮助快速了解这个语法的常用用法和相关衍生。

**批改**

这类 awk 命令的基本结构是：

```bash
awk 'pattern { action } END { final_action }' file
```

以这条命令为例：

```bash
awk '/Time \(sec\):/{t=$3} END{print t}' "${LOG}"
```

可以拆成四部分：

- `/Time \(sec\):/`：匹配包含 `Time (sec):` 的行。
- `{t=$3}`：对匹配到的行执行动作，把第 3 列保存到变量 `t`。
- `END{print t}`：所有行都处理完以后，打印变量 `t` 的最终值。
- `"${LOG}"`：awk 要读取的文件。

常用衍生：

- `$1`、`$2`、`$3` 表示当前行的第 1、第 2、第 3 个字段。
- `$NF` 表示当前行的最后一个字段。
- `NR > 1` 常用来跳过第一行表头。
- `-F,` 表示用逗号作为字段分隔符，适合处理简单 CSV。
- `sum += $4; count += 1` 可以做聚合统计，例如计算平均值。

已经新增练习文件：

- `examples/awk_practice.log`
- `examples/awk_practice.csv`
- `scripts/06_awk_practice.sh`

**记住**

```text
awk = 按行读文件；匹配 pattern；执行 action；最后可执行 END。
```

```text
/Time \(sec\):/{t=$3} END{print t}
= 找到时间行，把第 3 列存进 t，最后打印最后一次保存的 t。
```

## 2026-06-21：awk 基本语法和常用用法

**我的问题**

再给我一套 awk 的基本语法以及用法。

**批改**

awk 的核心思路是：逐行读取文件，把每一行按字段切开，然后对匹配条件的行执行动作。

基本格式：

```bash
awk '条件 { 动作 }' 文件
```

常见格式：

```bash
awk '{print $1}' file.txt
awk '/pattern/{print $0}' file.txt
awk -F, '{print $1, $3}' file.csv
awk 'NR > 1 {print $0}' file.csv
awk '{sum += $3} END{print sum}' file.txt
```

常用内置变量：

- `$0`：整行内容。
- `$1`、`$2`、`$3`：第 1、第 2、第 3 个字段。
- `$NF`：最后一个字段。
- `NF`：当前行有多少个字段。
- `NR`：当前是第几行。
- `FS`：输入字段分隔符，常用 `-F,` 设置。

常用动作：

```bash
awk '{print $0}' file.txt
```

打印整行。

```bash
awk '{print $1, $3}' file.txt
```

打印第 1 列和第 3 列。

```bash
awk '/Time/{print $0}' log.txt
```

只打印包含 `Time` 的行。

```bash
awk '/Time \(sec\):/{print $3}' log.txt
```

找到 `Time (sec):` 行，并打印第 3 列。

```bash
awk -F, 'NR > 1 {print $1, $4}' file.csv
```

用逗号切 CSV，跳过表头，打印第 1 列和第 4 列。

```bash
awk -F, 'NR > 1 && $1 == "small" {print $0}' file.csv
```

只打印 `scale` 等于 `small` 的数据行。

```bash
awk -F, 'NR > 1 {sum += $4; count += 1} END{print sum / count}' file.csv
```

计算第 4 列的平均值。

**记住**

```text
awk = 按行读取 + 按列切分 + 条件筛选 + 动作输出/统计
```

```text
最常用结构：
awk '条件 {动作} END{最后动作}' 文件
```

## 2026-06-21：awk 条件的常用语法

**我的问题**

awk 里 `条件 {动作}` 的条件常用语法是什么？条件是怎么规定的？

**批改**

awk 的条件写在 `{动作}` 前面，用来决定“这一行要不要执行动作”。

基本形式：

```bash
awk '条件 {动作}' file
```

如果当前行满足条件，就执行 `{动作}`；不满足就跳过。

常用条件有几类：

1. 正则匹配整行：

```bash
awk '/Time/{print $0}' log.txt
```

意思是：如果整行包含 `Time`，就打印整行。

2. 某一列正则匹配：

```bash
awk '$1 ~ /small/ {print $0}' file.txt
```

意思是：如果第 1 列匹配 `small`，就打印整行。

3. 某一列不匹配：

```bash
awk '$1 !~ /small/ {print $0}' file.txt
```

意思是：如果第 1 列不匹配 `small`，就打印整行。

4. 字符串相等：

```bash
awk -F, '$1 == "small" {print $0}' file.csv
```

意思是：如果第 1 列等于字符串 `small`，就打印整行。

5. 数字比较：

```bash
awk -F, '$4 > 10 {print $0}' file.csv
```

意思是：如果第 4 列大于 10，就打印整行。

6. 行号条件：

```bash
awk 'NR > 1 {print $0}' file.csv
```

意思是：跳过第 1 行，从第 2 行开始打印。

7. 多个条件组合：

```bash
awk -F, 'NR > 1 && $1 == "small" {print $0}' file.csv
```

意思是：行号大于 1，并且第 1 列等于 `small`。

```bash
awk -F, '$1 == "small" || $1 == "medium" {print $0}' file.csv
```

意思是：第 1 列等于 `small` 或者 `medium`。

8. 没有条件：

```bash
awk '{print $1}' file.txt
```

意思是：每一行都执行动作。

**记住**

```text
awk 条件 = 决定当前这一行要不要执行动作。
```

```text
/abc/           整行包含 abc
$1 == "small"  第 1 列等于 small
$4 > 10         第 4 列大于 10
NR > 1          从第 2 行开始
&&              并且
||              或者
```

## 2026-06-21：awk 正则里为什么括号要写成 `\(sec\)`？

**我的问题**

为什么是 `'/Time \(sec\):/{print $3}'`，而不是 `'/Time (sec):/{print $3}'`？

**批改**

因为 awk 的 `/.../` 里面写的是正则表达式，不是普通字符串。

在正则表达式里，括号 `(` 和 `)` 通常有特殊含义，表示分组。如果你想匹配日志里真正出现的括号字符，就要用反斜杠转义：

```bash
awk '/Time \(sec\):/{print $3}' log.txt
```

这里的意思是：匹配文本里的字面量 `Time (sec):`。

如果写成：

```bash
awk '/Time (sec):/{print $3}' log.txt
```

括号可能会被 awk 当成正则分组，而不是要匹配的真实括号字符。在常见 awk 正则里，它更像是在匹配 `Time sec:`，所以可能匹配不到日志里的 `Time (sec):`。

如果不想处理正则转义，也可以用字符串判断：

```bash
awk 'index($0, "Time (sec):") {print $3}' log.txt
```

这里 `index($0, "Time (sec):")` 是检查整行 `$0` 里是否包含普通字符串 `Time (sec):`。

**记住**

```text
awk 的 /.../ 是正则，不是普通字符串。
想匹配真正的括号字符，就写 \( 和 \)。
```

## 2026-06-21：awk 正则和转义注意事项

**我的问题**

awk 里除了括号，还有其它需要转义的吗？有哪些相关注意点？

**批改**

awk 里最容易混淆的是：`/.../` 里面是正则表达式，所以有些字符不是普通字符，而是有特殊含义。

常见需要注意或转义的字符：

```text
.   匹配任意一个字符
*   前一个模式重复 0 次或多次
+   前一个模式重复 1 次或多次
?   前一个模式出现 0 次或 1 次
^   行开头
$   行结尾
[]  字符集合
()  分组
|   或者
\   转义符本身
```

如果想匹配这些字符本身，通常要加反斜杠。例如：

```bash
awk '/3\.14/{print $0}' file.txt
```

匹配真正的 `3.14`，而不是 `3任意字符14`。

```bash
awk '/Time \(sec\):/{print $3}' log.txt
```

匹配真正的 `Time (sec):`。

```bash
awk '/error\[0\]/{print $0}' log.txt
```

匹配真正的 `error[0]`。

如果要匹配反斜杠本身，写法会更绕，通常要写成：

```bash
awk '/\\\\/{print $0}' file.txt
```

因为 shell 和 awk 都会处理反斜杠。

另一个重要注意点是 shell 引号：

```bash
awk '{print $3}' file.txt
```

推荐用单引号包住 awk 程序，这样 `$3` 不会被 shell 当成 shell 变量展开。

不要写成：

```bash
awk "{print $3}" file.txt
```

因为双引号里 `$3` 可能会先被 shell 展开，awk 就收不到真正的 `$3`。

如果只是想查找普通字符串，不想处理正则转义，可以用 `index`：

```bash
awk 'index($0, "Time (sec):") {print $3}' log.txt
```

**记住**

```text
awk '/.../' 里面是正则：特殊字符要小心。
awk 程序外面优先用单引号：保护 $1、$2、$3 不被 shell 提前展开。
复杂普通字符串匹配可以用 index($0, "文本")。
```

## 2026-06-21：`awk '/Time \(sec\):/&&NR==-1{print $NF}' $LOG` 错在哪？

**我的问题**

这个语法对吗？错在哪？

```bash
awk '/Time \(sec\):/&&NR==-1{print $NF}' $LOG
```

**批改**

这条命令接近 awk 的合法写法，但逻辑错在：

```awk
NR == -1
```

`NR` 是 awk 当前读到的行号，从 `1` 开始递增，不会等于 `-1`。所以这个条件永远不成立，`{print $NF}` 永远不会执行。

这部分：

```awk
/Time \(sec\):/ && NR == -1
```

意思是：当前行既要包含 `Time (sec):`，又要是第 `-1` 行。第二个条件不可能成立。

如果只是想打印 `Time (sec):` 这一行的最后一列，应该写：

```bash
awk '/Time \(sec\):/{print $NF}' "${LOG}"
```

在这一行里：

```text
Time (sec): 12.345
```

`$NF` 就是最后一列 `12.345`。

如果想打印最后一次出现的 `Time (sec):` 的值，应该写：

```bash
awk '/Time \(sec\):/{t=$NF} END{print t}' "${LOG}"
```

另外，文件变量建议写成：

```bash
"${LOG}"
```

不要写裸的：

```bash
$LOG
```

因为如果路径里有空格，裸 `$LOG` 会被 shell 拆开。

**记住**

```text
NR 是当前行号，从 1 开始，不会是 -1。
多个 awk 条件可以用 && 连接，但每个条件都必须可能成立。
文件路径变量推荐写成 "${LOG}"。
```

## 2026-06-21：为什么 `{t=$NF} END{print t}` 打印最后一次匹配的值？

**我的问题**

为什么这个是最后一行的最后一列？请拆解语法：

```bash
awk '/Time \(sec\):/{t= $NF} END{print t}' $LOG
```

**批改**

这句不是“直接取整个文件最后一行的最后一列”，而是：

1. awk 从上到下一行一行读文件。
2. 遇到匹配 `/Time \(sec\):/` 的行，就执行 `{t=$NF}`。
3. `$NF` 是当前匹配行的最后一列。
4. 每匹配一次，变量 `t` 就被重新赋值一次。
5. 文件全部读完后，`END{print t}` 只执行一次，打印的是最后一次保存进 `t` 的值。

所以如果日志里有三行：

```text
Time (sec): 12.345
Time (sec): 11.980
Time (sec): 25.500
```

awk 的过程是：

```text
读到第一行 Time：t = 12.345
读到第二行 Time：t = 11.980
读到第三行 Time：t = 25.500
文件结束：print t，所以输出 25.500
```

注意：

```awk
t= $NF
```

和：

```awk
t=$NF
```

在 awk 里都可以，空格不影响赋值。但为了清楚，推荐写成：

```bash
awk '/Time \(sec\):/{t=$NF} END{print t}' "${LOG}"
```

另外，`$LOG` 推荐写成 `"${LOG}"`，避免路径里有空格时出错。

**记住**

```text
{t=$NF} 是每次匹配时保存当前行最后一列。
END{print t} 是文件读完后打印变量 t。
如果匹配多次，t 会被后面的值覆盖，所以最后打印最后一次匹配的值。
```

## 2026-06-21：`tee "${LOG}"` 和 `> "${LOG}"` 有什么区别？

**我的问题**

`tee "${LOG}"` 和 `> "${LOG}"` 有什么区别？

**批改**

它们都可以把命令输出保存到文件，但显示方式不同。

```bash
command > "${LOG}"
```

意思是：把 `command` 的标准输出写入 `${LOG}` 文件。默认不会在屏幕上显示输出。

```bash
command | tee "${LOG}"
```

意思是：把 `command` 的标准输出同时做两件事：

- 显示在屏幕上。
- 写入 `${LOG}` 文件。

所以 `tee` 很适合 benchmark：运行时你能在终端看到程序输出，同时也把完整日志保存下来，方便之后用 awk 解析。

注意：默认情况下，二者都会覆盖旧文件。如果想追加到旧日志末尾：

```bash
command >> "${LOG}"
command | tee -a "${LOG}"
```

**记住**

```text
> file        只写入文件，不显示到屏幕。
| tee file    既显示到屏幕，也写入文件。
>> file       追加写入文件。
| tee -a file 既显示到屏幕，也追加写入文件。
```

## 2026-06-21：第 6、7 节日志和 awk 练习批改

**我的问题**

帮我批改一下我的 plan，重点是第 6 节日志与结果 CSV、第 7 节 awk 日志解析入门。

**批改**

整体方向不错，几个核心概念已经抓住了：

- `tee` 可以一边显示一边保存。
- `TIMESEC` 为空时应该停止，因为缺少 benchmark 的关键结果。
- `$3` 是第 3 个字段，`$NF` 是最后一个字段。
- `-F,` 是用逗号分隔字段。

需要修正和补充的点：

- `awk '/Time \(sec\):/{t=$3} END{print t}'` 不是打印 `/Time \(sec\):/` 这个模式，而是匹配时间行、保存第 3 列，最后打印最后一次保存的时间。
- `END{print t}` 只打印一次，是因为 `END{...}` 只在 awk 读完整个文件后执行一次；`t` 被覆盖只是它最后打印最后一次值的原因。
- `awk -F,` 是大写 `-F`，不是小写 `-f`。
- benchmark 同时保存 log 和 summary CSV，是因为 log 负责可追溯，summary CSV 负责可分析。

**记住**

```text
普通 awk 动作按行执行；END 动作在文件读完后执行一次。
log 保存原始输出，方便追查；summary CSV 保存结构化结果，方便分析。
```

## 2026-06-21：`[[ -z "${TIMESEC}" ]]` 里的 `-z` 是什么意思？

**我的问题**

`[[ -z "${TIMESEC}" ]]` 这个条件里面的 `-z` 是什么意思？还有通常情况下，`''` 就是表示 shell 中的条件吗？

**批改**

`-z` 是 Bash 条件测试里的一个操作符，意思是：字符串长度是不是 0。

```bash
[[ -z "${TIMESEC}" ]]
```

意思是：如果变量 `TIMESEC` 是空字符串，就条件成立。

例如：

```bash
TIMESEC=""
[[ -z "${TIMESEC}" ]]
```

成立。

```bash
TIMESEC="12.345"
[[ -z "${TIMESEC}" ]]
```

不成立。

和它相反的是 `-n`：

```bash
[[ -n "${TIMESEC}" ]]
```

意思是：如果 `TIMESEC` 不是空字符串，就条件成立。

注意：`''` 或 `'...'` 不是 shell 条件结构。单引号只是 shell 的引用方式，用来保护里面的文字不被变量展开、不被特殊解释。

真正表示条件测试的是：

```bash
[[ 条件 ]]
```

例如：

```bash
[[ -z "${TIMESEC}" ]]
[[ "${SCALE}" == "small" ]]
[[ -f "${LOG}" ]]
```

**记住**

```text
-z 字符串：字符串为空就成立。
-n 字符串：字符串非空就成立。
[[ ... ]]：Bash 条件测试。
'...'：单引号，只是保护文字，不是条件。
```

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
