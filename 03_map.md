# Linaro Forge MAP 问题与批改记录

这个文件专门记录 Linaro Forge MAP、Slurm 下 profiling、MPI/OpenMP 程序启动方式，以及 MAP 命令常用语法。

## 2026-07-01：`map -n ... --mpi=slurm --mpiargs=...` 这段命令是什么意思？

**我的问题**

下面这段 MAP 命令的语法是什么意思？

```bash
map -n "${MAP_RANKS}" \
     --mpi=slurm \
     --mpiargs="--nodes=${NODES} --ntasks-per-node=${R} --cpus-per-task=${T} --exact --hint=nomultithread --distribution=block:block" \
     --profile \
     "${PETSC_DIR}/src/ksp/ksp/tutorials/ex2" \
     -m "${M}" -n "${N}" -ksp_converged_reason -log_view \
     -ksp_type cg \
     -pc_type gamg \
     -ksp_rtol 1e-5 -ksp_atol 1e-10 \
    < /dev/null \
  | tee "${LOG}"
```

**批改**

这是一条“用 Linaro Forge MAP 启动 PETSc MPI/OpenMP 程序，并把输出保存到日志”的命令。

可以先把它压缩成一行来理解：

```bash
map [MAP自己的参数] [你的可执行程序] [你的程序参数] < /dev/null | tee "${LOG}"
```

在这里：

- `map`：Linaro Forge MAP 的命令行工具，用来 profiling 程序。
- `-n "${MAP_RANKS}"`：告诉 MAP 要启动多少个 MPI rank。
- `--mpi=slurm`：告诉 MAP 这个 MPI 程序由 Slurm 启动。
- `--mpiargs="..."`：把里面这一整串参数交给 Slurm/srun。
- `--profile`：真正开始性能采样，生成 `.map` profiling 文件。
- `"${PETSC_DIR}/src/ksp/ksp/tutorials/ex2"`：要被 profiling 的 PETSc 可执行程序。
- `-m "${M}" -n "${N}" ...`：这些不是 MAP 参数，而是传给 PETSc `ex2` 程序的参数。
- `< /dev/null`：不给程序任何交互式输入，避免批处理作业卡住等输入。
- `| tee "${LOG}"`：把屏幕输出同时写入日志文件。

反斜杠 `\` 的意思是“这一行还没结束，下一行继续”。所以多行写法只是为了可读性，本质上还是一条长命令。

**记住**

```text
map 的参数放在可执行程序前面。
PETSc/ex2 的参数放在可执行程序后面。
--mpiargs 里面放的是传给 Slurm/srun 的参数。
```

## 2026-07-01：MAP 参数和 PETSc 参数怎么区分？

**我的问题**

在一条很长的 MAP 命令里，哪些是 MAP 的参数，哪些是我的程序参数？

**批改**

一般按“可执行程序路径”为分界线。

```bash
map -n 16 --mpi=slurm --profile ./my_program -m 1000 -n 1000 -log_view
```

这里：

```text
map -n 16 --mpi=slurm --profile
```

属于 MAP 的参数。

```text
./my_program
```

是要运行的程序。

```text
-m 1000 -n 1000 -log_view
```

属于 `my_program` 的参数。在 PETSc 里，这些会被 PETSc options database 读取。

**记住**

```text
可执行程序路径前面：MAP 怎么启动。
可执行程序路径后面：程序自己怎么运行。
```

## 2026-07-01：`--mpiargs="..."` 为什么要放一整串 Slurm 参数？

**我的问题**

为什么不直接写 `map --nodes=1 --ntasks-per-node=16 ...`，而要写到 `--mpiargs="..."` 里面？

**批改**

因为 `--nodes`、`--ntasks-per-node`、`--cpus-per-task`、`--exact`、`--hint`、`--distribution` 这些是 Slurm/srun 的启动参数，不是 MAP 自己的 profiling 参数。

MAP 需要知道两件事：

```text
1. 用什么 MPI 启动方式：--mpi=slurm
2. 启动 MPI 时额外传什么参数：--mpiargs="..."
```

所以 Slurm 相关参数放在 `--mpiargs` 里更清楚：

```bash
map -n 16 \
    --mpi=slurm \
    --mpiargs="--nodes=1 --ntasks-per-node=16 --cpus-per-task=8 --exact" \
    --profile \
    ./ex2
```

**记住**

```text
Slurm/srun 参数放进 --mpiargs。
MAP profiling 参数直接写在 map 后面。
```

## 2026-07-01：`-n "${MAP_RANKS}"` 和 `--ntasks-per-node="${R}"` 有什么关系？

**我的问题**

`map -n "${MAP_RANKS}"` 和 `--mpiargs="--ntasks-per-node=${R}"` 会不会重复？

**批改**

它们表达的是同一个运行布局的两个角度，通常要保持一致。

在单节点时：

```bash
NODES=1
R=16
MAP_RANKS=$(( R * NODES ))
```

所以：

```text
MAP_RANKS = 16
--ntasks-per-node = 16
```

在两节点时：

```bash
NODES=2
R=16
MAP_RANKS=$(( R * NODES ))
```

所以：

```text
MAP_RANKS = 32
--nodes = 2
--ntasks-per-node = 16
```

`-n` 告诉 MAP 总共多少个 MPI rank；`--ntasks-per-node` 告诉 Slurm 每个节点放多少个 rank。

**记住**

```text
MAP_RANKS = nodes * ntasks_per_node。
-n 是总 rank 数。
--ntasks-per-node 是每个节点的 rank 数。
```

## 2026-07-01：`--cpus-per-task` 和 `OMP_NUM_THREADS` 为什么要一致？

**我的问题**

脚本里有：

```bash
export OMP_NUM_THREADS="${T}"
export SRUN_CPUS_PER_TASK="${T}"
```

命令里又有：

```bash
--cpus-per-task=${T}
```

为什么这些都要用同一个 `T`？

**批改**

在 hybrid MPI + OpenMP 程序里：

```text
MPI rank 数 = 有多少个 task
OpenMP thread 数 = 每个 task 内部有多少线程
```

`--cpus-per-task=${T}` 是告诉 Slurm：每个 MPI rank 分配 `T` 个 CPU core。

`OMP_NUM_THREADS="${T}"` 是告诉 OpenMP：每个 MPI rank 里面开 `T` 个线程。

如果 Slurm 只给每个 task 1 个 CPU，但 OpenMP 开 8 个线程，就会超卖 CPU，性能会很差，绑定也可能混乱。

**记住**

```text
Hybrid MPI+OpenMP:
ntasks-per-node = 每节点 MPI ranks
cpus-per-task = 每个 rank 的 CPU cores
OMP_NUM_THREADS = 每个 rank 的 OpenMP threads

通常 cpus-per-task 要等于 OMP_NUM_THREADS。
```

## 2026-07-01：`< /dev/null | tee "${LOG}"` 是什么意思？

**我的问题**

命令最后这两段是什么意思？

```bash
< /dev/null \
| tee "${LOG}"
```

**批改**

`< /dev/null` 是输入重定向。意思是：这个程序的标准输入来自 `/dev/null`。

`/dev/null` 可以理解成一个永远没有内容的空文件。这样做的好处是，批处理程序如果不小心等待用户输入，会立刻读到 EOF，不容易挂在那里。

`| tee "${LOG}"` 是管道加日志保存：

```text
程序输出 -> tee -> 一边显示到终端/Slurm output，一边写入 LOG 文件
```

例如：

```bash
echo "hello" | tee out.log
```

屏幕会显示 `hello`，同时 `out.log` 里也会有 `hello`。

**记住**

```text
< /dev/null：不给程序交互输入。
| tee file.log：屏幕显示一份，日志保存一份。
```

## 2026-07-01：常用 MAP 命令模板

**我的问题**

我平时写 MAP 脚本时可以记哪些常用模板？

**批改**

最小单进程模板：

```bash
map --profile ./my_program arg1 arg2
```

MPI + Slurm 模板：

```bash
map -n "${RANKS}" \
    --mpi=slurm \
    --profile \
    ./my_program arg1 arg2
```

MPI + Slurm + 传递 srun 参数模板：

```bash
map -n "${RANKS}" \
    --mpi=slurm \
    --mpiargs="--nodes=${NODES} --ntasks-per-node=${RANKS_PER_NODE} --cpus-per-task=${THREADS}" \
    --profile \
    ./my_program arg1 arg2
```

PETSc `ex2` 模板：

```bash
map -n "${RANKS}" \
    --mpi=slurm \
    --mpiargs="--nodes=${NODES} --ntasks-per-node=${RANKS_PER_NODE} --cpus-per-task=${THREADS} --hint=nomultithread --distribution=block:block" \
    --profile \
    "${PETSC_DIR}/src/ksp/ksp/tutorials/ex2" \
    -m "${M}" -n "${N}" \
    -ksp_converged_reason -log_view
```

带日志模板：

```bash
map -n "${RANKS}" \
    --mpi=slurm \
    --mpiargs="--nodes=${NODES} --ntasks-per-node=${RANKS_PER_NODE} --cpus-per-task=${THREADS}" \
    --profile \
    ./my_program arg1 arg2 \
  < /dev/null \
  | tee "${LOG}"
```

**记住**

```text
先写能跑的 srun。
再把 srun 的资源参数放进 map 的 --mpiargs。
最后用 map --profile 包住真正的可执行程序。
```

## 2026-07-01：MAP 脚本最常见错误

**我的问题**

写 MAP 脚本时最容易错在哪里？

**批改**

常见错误有这些：

- 把 Slurm/srun 参数直接写成 `map --nodes=... --ntasks-per-node=...`。
- 忘记加载 Forge 模块，例如 `module load forge/25.0.1`。
- `map -n` 的总 rank 数和 `--nodes * --ntasks-per-node` 不一致。
- `--cpus-per-task` 和 `OMP_NUM_THREADS` 不一致。
- 把 PETSc 参数写到可执行程序前面，导致 MAP 误以为那是自己的参数。
- 最后引用了未定义变量，例如 `echo "${LOG_FILE}"`，但实际变量叫 `LOG`。
- 只用 `bash -n` 检查。`bash -n` 只能检查 Bash 语法，检查不出 MAP 参数是否正确。

**记住**

```text
MAP 命令分三层：
1. map 自己的 profiling 参数
2. --mpiargs 里的 Slurm/srun 参数
3. 可执行程序后面的 PETSc/程序参数
```
