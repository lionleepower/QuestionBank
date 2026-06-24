# Python Runtime Scaling Learning Questions

这个文件用于记录学习过程中向 Codex 询问过的问题、简短答案和可复查命令。之后继续提问时，请把新的问题追加到这里，形成一个持续更新的问题库。

## 001. 如何检查当前 Python 环境里有没有 pandas 和 matplotlib？

可以用 `importlib.util.find_spec` 检查包是否能被当前 Python 找到：

```bash
python3 -c "import importlib.util; print('pandas', importlib.util.find_spec('pandas') is not None); print('matplotlib', importlib.util.find_spec('matplotlib') is not None)"
```

如果包已经安装，也可以直接查看版本：

```bash
python3 -c "import pandas, matplotlib; print('pandas', pandas.__version__); print('matplotlib', matplotlib.__version__)"
```

## 002. 可以在当前环境里直接使用 pip install 吗？

可以，但如果当前 Python 是系统 Python，例如 `/usr/bin/python3`，更推荐创建虚拟环境后再安装包，避免污染系统环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pandas matplotlib
```

检查 `pip` 是否可用：

```bash
python3 -m pip --version
```

## 003. 在 WSL 里可以直接写 `.py` 文件并运行吗？

可以。进入学习目录后创建 Python 文件，再用 `python3` 或虚拟环境里的 `python` 运行：

```bash
python3 hello.py
```

如果已经激活虚拟环境：

```bash
source .venv/bin/activate
python hello.py
```

## 004. `from __future__ import annotations` 是什么意思？

它启用 Python 的未来特性，让类型注解延迟处理。它主要服务于类型提示，不改变普通代码的主要运行逻辑。

例如：

```python
def load_data() -> pd.DataFrame:
    ...
```

这里的 `-> pd.DataFrame` 就是类型注解。

## 005. `from io import StringIO` 是什么意思？

`StringIO` 来自 Python 标准库 `io`，可以把字符串当成类似文件的对象读取。它常用于教学示例或小测试：

```python
from io import StringIO
import pandas as pd

text = """name,score
Alice,90
Bob,85
"""

df = pd.read_csv(StringIO(text))
```

## 006. `#!/usr/bin/env python3` 是注释吗？激活环境后还需要吗？

这一行叫 shebang。它看起来像注释，但主要是给 Linux/WSL shell 看的，用来说明直接执行这个脚本时应该使用哪个解释器。

如果这样运行：

```bash
python scripts/01_read_csv.py
```

这一行基本用不到。

如果这样运行：

```bash
chmod +x scripts/01_read_csv.py
./scripts/01_read_csv.py
```

shell 会根据：

```python
#!/usr/bin/env python3
```

去当前环境里寻找 `python3` 来执行脚本。激活 `.venv` 后，它通常会找到虚拟环境里的 `python3`。

## 007. shell 中 `find` 怎么用？

`find` 用来从某个目录开始按条件查找文件或目录。

常用命令：

```bash
find . -name "*.py"
find . -name "common.py"
find . -type f
find . -type d
find . -maxdepth 1 -type f
```

含义示例：

```bash
find . -type f -name "*.py"
```

从当前目录开始，查找所有 Python 文件。

## 008. 为什么 `Path(__file__).resolve().parents[1]` 里是 `parents[1]`？

假设当前文件是：

```text
python_runtime_scaling_learning/scripts/common.py
```

那么：

```text
parents[0] -> python_runtime_scaling_learning/scripts
parents[1] -> python_runtime_scaling_learning
parents[2] -> analysis
```

所以：

```python
LEARNING_DIR = Path(__file__).resolve().parents[1]
```

是为了得到 `python_runtime_scaling_learning` 这个学习目录，而不是 `scripts` 目录。

## 009. 查看文件内容是不是用 `cat`？

是。比如：

```bash
cat scripts/common.py
```

常用替代命令：

```bash
less scripts/common.py
sed -n '1,40p' scripts/common.py
nl -ba scripts/common.py
```

`cat` 适合小文件，`less` 适合长文件，`nl -ba` 可以带行号查看。

## 010. `pd.read_csv(SOURCE_CSV)` 是自带函数吗？

`read_csv` 不是 Python 自带函数，而是 pandas 提供的函数。通常先这样导入：

```python
import pandas as pd
```

然后使用：

```python
df = pd.read_csv(SOURCE_CSV)
```

它会读取 CSV 文件，并返回一个 `pandas.DataFrame`，也就是 pandas 里的表格对象。

下面这个函数：

```python
def load_runtime_results() -> pd.DataFrame:
    """Read the source CSV into a pandas DataFrame."""
    return pd.read_csv(SOURCE_CSV)
```

意思是：定义一个函数，读取 `SOURCE_CSV` 指向的 CSV 文件，并把读出来的表格返回。

## 011. 如何维护这个问题库？

之后继续向 Codex 提问时，如果问题和这个学习项目有关，请把问题、核心解释和必要命令追加到本文件。每个问题使用递增编号，格式保持为：

````markdown
## 012. 问题标题

简短解释。

```bash
可复查命令
```
````

## 012. Python 如何打印变量、参数和文件路径？

最常用的是 `print()`：

```python
name = "runtime_results.csv"
print(name)
```

打印多个参数时，可以用逗号分隔。`print()` 会自动在它们之间加空格：

```python
nodes = 2
runtime = 12.5
print("nodes =", nodes, "runtime =", runtime)
```

也可以用 f-string，把变量嵌入字符串里：

```python
print(f"nodes = {nodes}, runtime = {runtime}")
```

如果要打印文件路径，推荐使用 `pathlib.Path`：

```python
from pathlib import Path

path = Path("outputs") / "result.csv"
print(path)
```

## 013. 可以直接使用 `__file__` 吗？比如 `SET_DIR = __file__`

可以直接使用 `__file__`，但要注意它表示的是“当前这个 `.py` 文件的路径”，不是目录。

例如在：

```text
python_runtime_scaling_learning/exercises/oneTry.py
```

里面写：

```python
SET_DIR = __file__
print(SET_DIR)
```

得到的是当前脚本文件本身的路径，类似：

```text
/home/.../python_runtime_scaling_learning/exercises/oneTry.py
```

如果目标是得到当前文件所在目录，推荐转换成 `Path` 后再取 `.parent`：

```python
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
CURRENT_DIR = CURRENT_FILE.parent
```

如果目标是从 `exercises/oneTry.py` 找到学习项目根目录 `python_runtime_scaling_learning`，可以用：

```python
from pathlib import Path

LEARNING_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = LEARNING_DIR / "scripts"
```

注意：`.parent` 是单个父目录，不能写 `.parent[1]`；如果要按层级取父目录，应使用 `.parents[1]`。

可复查命令：

```bash
cd ~/leyan/jobSkill/petsc-benchmark-suite/s2795693/analysis/python_runtime_scaling_learning
python exercises/oneTry.py
```

如果想打印绝对路径：

```python
print(path.resolve())
```

如果想打印当前 Python 文件的位置：

```python
from pathlib import Path

print(Path(__file__))
print(Path(__file__).resolve())
```

如果想打印函数收到的参数：

```python
def show_file(path):
    print("path =", path)
    print("absolute path =", Path(path).resolve())

show_file("outputs/result.csv")
```

## 013. 为什么推荐慢慢习惯 f-string？它相比普通 `print` 有哪些优缺点？

f-string 是 Python 3.6 之后推荐使用的字符串格式化方式。它可以把变量或表达式直接写进字符串里：

```python
nodes = 2
runtime = 12.5

print(f"nodes = {nodes}, runtime = {runtime}")
```

相比用逗号分隔的 `print()`：

```python
print("nodes =", nodes, "runtime =", runtime)
```

f-string 的优点是输出格式更容易控制，代码更接近最终显示出来的文本，也方便控制小数位数：

```python
print(f"runtime = {runtime:.2f} seconds")
```

其中 `:.2f` 表示保留两位小数。

f-string 也可以直接打印路径：

```python
from pathlib import Path

path = Path("outputs") / "result.csv"
print(f"output path = {path.resolve()}")
```

缺点是：刚开始看起来会比普通 `print("x =", x)` 稍微复杂一点；如果字符串里有很多 `{}`，需要注意转义；另外 f-string 只适合 Python 3.6 及以上版本。

学习阶段可以两种都用：快速调试时用逗号分隔的 `print()` 很方便；当输出要更清楚、更像报告文本时，用 f-string 更合适。

## 014. 为什么 Python 经常在名字前后加双下划线，例如 `__main__`？

Python 里前后都有双下划线的名字通常有特殊含义，常被称为 dunder name，也就是 double underscore name。

例如：

```python
__name__
__main__
__file__
__init__
```

这些名字一般由 Python 解释器或 Python 的特殊机制使用，不建议随便自己发明新的 `__xxx__` 名字。

最常见的是：

```python
if __name__ == "__main__":
    main()
```

含义是：只有当这个文件被直接运行时，才执行 `main()`。

比如：

```bash
python scripts/01_read_csv.py
```

这时这个文件里的 `__name__` 会等于 `"__main__"`。

但如果这个文件是被别的 Python 文件导入：

```python
import scripts.common
```

那么被导入文件里的 `__name__` 就不是 `"__main__"`，而是它自己的模块名。

所以 `if __name__ == "__main__":` 的作用是区分“直接运行这个文件”和“被别人导入使用”。

另外：

```python
__file__
```

表示当前 Python 文件的路径。

```python
__init__
```

常用于类的初始化方法：

```python
class User:
    def __init__(self, name):
        self.name = name
```

总结：双下划线名字通常是 Python 的特殊约定。看到它时，要先假设它和解释器、模块、类或某种特殊行为有关。

## 015. dunder name 有规律性记忆吗？需要专门学习吗？

dunder name 不建议一开始死背完整列表。更好的学习方式是：先记住分类和常见场景，遇到一个再理解一个。

可以先按用途记：

1. 脚本和模块相关：

```python
__name__
__main__
__file__
```

它们常用于判断文件是被直接运行还是被导入，以及定位当前文件路径。

2. 类和对象相关：

```python
__init__
__str__
__repr__
```

它们用于定义对象如何初始化、如何被打印、如何被显示。

3. 运算符或内置函数相关：

```python
__len__
__add__
__getitem__
```

它们会影响 `len(obj)`、`obj1 + obj2`、`obj[index]` 这些行为。

学习策略：

- 初学阶段只需要主动掌握 `__name__`、`__main__`、`__file__`。
- 学到 class 时再学 `__init__`、`__str__`、`__repr__`。
- 学到高级对象行为时再学 `__len__`、`__getitem__`、`__add__` 等。
- 不要自己随便创造新的 `__xxx__` 名字，因为这类名字通常预留给 Python 特殊机制。

简单记法：dunder name 的规律是“Python 在背后会自动看这些名字，并用它们决定某些特殊行为”。因此不需要一次性背完，只需要知道它们是特殊钩子，遇到时查清楚它控制了什么行为。

## 016. `from ../scripts import common` 这种写法对吗？

不对。`../scripts` 是 shell 或文件路径写法，Python 的 `import` 语法里不能直接这样写。

在 Python 里，导入模块通常写模块名或包名：

```python
import common
from common import load_runtime_results
```

但这些写法要求 Python 能在 `sys.path` 里找到 `common.py`。

当前项目里 `common.py` 位于：

```text
scripts/common.py
```

如果脚本也在 `scripts/` 目录里，例如 `scripts/01_read_csv.py`，可以直接写：

```python
from common import SOURCE_CSV, load_runtime_results
```

如果脚本在 `exercises/` 目录里，例如 `exercises/oneTry.py`，可以在文件开头临时把 `scripts/` 加到 Python 的搜索路径：

```python
from pathlib import Path
import sys

LEARNING_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = LEARNING_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from common import SOURCE_CSV, load_runtime_results
```

然后从学习目录根目录运行：

```bash
python exercises/oneTry.py
```

核心区别：

```bash
../scripts
```

是文件系统路径写法。

```python
from common import ...
```

是 Python 模块导入写法。

## 017. `import sys` 是什么意思？为什么要写 `sys.path.insert(0, str(SCRIPTS_DIR))`？

`sys` 是 Python 标准库里的一个模块，用来访问当前 Python 解释器相关的信息和设置。

导入它：

```python
import sys
```

之后就可以使用：

```python
sys.path
```

`sys.path` 是一个列表，里面保存了 Python 执行 `import` 时会去搜索模块的目录。

可以打印出来观察：

```python
import sys

for path in sys.path:
    print(path)
```

当 `exercises/oneTry.py` 想导入 `scripts/common.py` 时，Python 默认不一定会去 `scripts/` 目录里找。因此可以手动把 `scripts/` 加进搜索路径：

```python
from pathlib import Path
import sys

LEARNING_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = LEARNING_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from common import load_runtime_results
```

这里：

```python
str(SCRIPTS_DIR)
```

是把 `Path` 对象转换成字符串路径，因为 `sys.path` 里通常存放字符串。

这里：

```python
insert(0, ...)
```

表示把 `scripts/` 放到搜索路径列表最前面。这样当 Python 执行：

```python
from common import load_runtime_results
```

它会优先去 `scripts/` 目录寻找 `common.py`。

这是一种适合学习项目和小脚本的写法。更正式的项目通常会把代码组织成 package，再用包导入或安装项目本身。

## 018. `insert(0, value)` 里的 `0`、`1`、`2` 代表什么？

在 Python 列表里，位置编号叫 index，索引从 `0` 开始。

例如：

```python
items = ["a", "b", "c"]
```

对应位置是：

```text
index 0 -> "a"
index 1 -> "b"
index 2 -> "c"
```

`insert(index, value)` 的意思是：把 `value` 插入到指定 index 的前面。

例如：

```python
items = ["a", "b", "c"]
items.insert(0, "x")
print(items)
```

结果：

```text
["x", "a", "b", "c"]
```

如果写：

```python
items = ["a", "b", "c"]
items.insert(1, "x")
print(items)
```

结果：

```text
["a", "x", "b", "c"]
```

所以：

```python
sys.path.insert(0, str(SCRIPTS_DIR))
```

意思是把 `SCRIPTS_DIR` 放到 `sys.path` 的最前面，让 Python import 时优先搜索这个目录。

## 019. `sys.path.insert(0, ...)` 改成 `insert(1, ...)`、`insert(2, ...)` 也可以找到吗？

很多情况下也可以找到，只要 `SCRIPTS_DIR` 被加入了 `sys.path`，Python import 时最终就会搜索到它。

但是 `0`、`1`、`2` 会影响搜索顺序。

Python import 会按照 `sys.path` 里的顺序从前往后找模块。假设：

```python
sys.path = [
    "exercises",
    "some_other_dir",
    "scripts",
]
```

当执行：

```python
import common
```

Python 会先找 `exercises/common.py`，再找 `some_other_dir/common.py`，最后才找 `scripts/common.py`。

如果别的目录里也有一个同名的 `common.py`，那搜索顺序就很重要。先找到哪个，就导入哪个。

所以：

```python
sys.path.insert(0, str(SCRIPTS_DIR))
```

更明确，意思是“优先使用我指定的 `scripts/` 目录里的模块”。

如果只是追加到最后：

```python
sys.path.append(str(SCRIPTS_DIR))
```

通常也能工作，但优先级最低。

## 020. 为什么写 `from common import load_runtime_results`，而不是 `load_runtime_results()`？

`import` 语句的作用是把某个名字从模块里拿进来。它导入的是“名字本身”，不会在导入位置调用函数。

例如：

```python
from common import SOURCE_CSV, load_runtime_results
```

这里导入了两个名字：

```python
SOURCE_CSV
load_runtime_results
```

`SOURCE_CSV` 是变量名。

`load_runtime_results` 是函数名。

导入函数时不写括号：

```python
from common import load_runtime_results
```

真正调用函数时才写括号：

```python
df = load_runtime_results()
```

可以这样理解：

```python
load_runtime_results
```

表示“这个函数对象本身”。

```python
load_runtime_results()
```

表示“现在执行这个函数，并拿到它的返回值”。

所以完整流程通常是：

```python
from common import SOURCE_CSV, load_runtime_results

print(SOURCE_CSV)
df = load_runtime_results()
```

如果在 `import` 里写括号，Python 语法是不允许的：

```python
from common import load_runtime_results()
```

这是错误写法。

## 021. `df.shape[0]` 是行数，`df.shape[1]` 是列数吗？

是的。pandas DataFrame 的 `shape` 会返回一个二元组：

```python
(number_of_rows, number_of_columns)
```

例如：

```python
print(df.shape)
```

可能输出：

```text
(120, 8)
```

表示这个 DataFrame 有 120 行、8 列。

所以：

```python
df.shape[0]
```

是行数 rows。

```python
df.shape[1]
```

是列数 columns。

常见写法：

```python
print(f"{df.shape[0]} rows x {df.shape[1]} columns")
```

也可以拆开写得更清楚：

```python
n_rows, n_cols = df.shape
print(f"{n_rows} rows x {n_cols} columns")
```

## 022. `df.shape[1]` 和 `df.columns` 是同一个意思吗？

不是同一个意思，但它们有关联。

```python
df.shape[1]
```

表示列的数量，也就是有多少列。

```python
df.columns
```

表示列名，也就是每一列叫什么名字。

例如一个 DataFrame 有 3 列：

```text
name, runtime_seconds, total_cores
```

那么：

```python
df.shape[1]
```

结果是：

```text
3
```

而：

```python
df.columns
```

结果类似：

```text
Index(['name', 'runtime_seconds', 'total_cores'], dtype='object')
```

如果想把列名变成普通 Python list：

```python
list(df.columns)
```

如果想得到列数，也可以写：

```python
len(df.columns)
```

它通常和下面这个相等：

```python
df.shape[1]
```

## 023. f-string 自带 `\n` 换行吗？

f-string 本身不会自动加换行。它只是生成一个字符串。

自动换行通常来自 `print()`。默认情况下，`print()` 会在输出末尾加一个换行符。

例如：

```python
name = "Alice"
print(f"name = {name}")
print("done")
```

输出是两行：

```text
name = Alice
done
```

这是因为每次 `print()` 结束时都会自动加换行。

如果不想让 `print()` 自动换行，可以设置 `end`：

```python
print(f"name = {name}", end="")
print("done")
```

输出：

```text
name = Alicedone
```

如果想在 f-string 里面主动换行，可以写 `\n`：

```python
print(f"name = {name}\nstatus = ok")
```

输出：

```text
name = Alice
status = ok
```

所以：

- f-string 负责把变量放进字符串。
- `print()` 默认负责在末尾加换行。
- `\n` 是手动写进字符串里的换行符。

## 024. VS Code 里有没有快速换行或快速移动到行末的快捷键？

有。常用快捷键如下。

无论光标在当前行的哪个位置，直接在下面新开一行：

```text
Ctrl + Enter
```

无论光标在当前行的哪个位置，直接在上面新开一行：

```text
Ctrl + Shift + Enter
```

把光标移动到当前行末：

```text
End
```

把光标移动到当前行首：

```text
Home
```

在有些笔记本键盘上，可能需要：

```text
Fn + Right Arrow
Fn + Left Arrow
```

常见用法：

- 想快速继续写下一行：用 `Ctrl + Enter`。
- 想先去行末再输入：用 `End`。
- 想回到行首：用 `Home`。

如果在 macOS 上使用 VS Code，常见对应是：

```text
Cmd + Enter
Cmd + Shift + Enter
Cmd + Right Arrow
Cmd + Left Arrow
```

## 025. `StringIO` 在 `df.info(buf=buffer)` 里到底起什么作用？

`StringIO` 可以理解成一个“内存里的临时文本文件”或“文本 buffer”。

平时：

```python
df.info()
```

会直接把 DataFrame 的信息打印到屏幕上。

如果写成：

```python
from io import StringIO

buffer = StringIO()
df.info(buf=buffer)
text = buffer.getvalue()
print(text)
```

意思是：

1. 创建一个临时文本 buffer。
2. 让 `df.info()` 不要直接打印到屏幕，而是把内容写进 `buffer`。
3. 用 `buffer.getvalue()` 把刚才写进去的文本取出来。
4. 再由 `print()` 打印这段文本。

这里真正检查 DataFrame 行数、列名、non-null 数量、数据类型的是：

```python
df.info()
```

不是 `StringIO`。

`StringIO` 只负责接住这段文本输出。

为什么要这样做？因为 `df.info()` 的返回值不是一段普通字符串，它默认直接打印。如果想把这段输出保存起来、加工、写入文件，或者统一控制打印位置，就可以用 `StringIO` 接住它。

简单记法：

```text
df.info()      -> 生成 DataFrame 信息
StringIO()     -> 临时接住这段文本
getvalue()     -> 把接住的文本拿出来
```

## 026. `sorted(df[column].dropna().unique())` 是什么意思？

这行代码的作用是：取出某一列，去掉空值，找出不重复的值，然后排序。

原代码：

```python
values = sorted(df[column].dropna().unique())
```

可以拆成几步理解：

```python
df[column]
```

表示从 DataFrame 里取出名字为 `column` 的这一列。

例如当：

```python
column = "status"
```

那么：

```python
df[column]
```

就等价于：

```python
df["status"]
```

接着：

```python
df[column].dropna()
```

表示去掉这一列里的空值。`dropna()` 里的 `na` 指的是 missing value，例如 `NaN`。

再接着：

```python
df[column].dropna().unique()
```

表示找出这一列中出现过的不重复值。

例如一列数据是：

```text
completed
completed
failed
completed
```

`unique()` 之后可能得到：

```text
completed, failed
```

最后：

```python
sorted(...)
```

把这些唯一值排序，方便阅读和比较。

所以完整含义是：

```python
values = sorted(df[column].dropna().unique())
```

等价于：

```python
one_column = df[column]
without_missing = one_column.dropna()
unique_values = without_missing.unique()
values = sorted(unique_values)
```

这段循环：

```python
for column in ["scale", "status", "threads", "total_cores"]:
    values = sorted(df[column].dropna().unique())
    print(f" - {column}: {values}")
```

意思是：分别查看 `scale`、`status`、`threads`、`total_cores` 这些重要列里面有哪些不同取值。

## 027. `sorted()` 是按照字母表顺序排序吗？

如果排序对象是字符串，`sorted()` 通常按字典序，也就是接近字母表顺序排序。

例如：

```python
print(sorted(["weak", "strong", "completed", "failed"]))
```

结果：

```text
['completed', 'failed', 'strong', 'weak']
```

如果排序对象是数字，`sorted()` 会按数值大小排序：

```python
print(sorted([128, 32, 64]))
```

结果：

```text
[32, 64, 128]
```

所以在这段代码里：

```python
sorted(df[column].dropna().unique())
```

如果 `column` 是 `status` 或 `scale`，通常按字符串字典序排。

如果 `column` 是 `threads` 或 `total_cores`，通常按数字大小排。

注意：如果一个列表里混合了字符串和数字，例如：

```python
["1", 2, "3"]
```

直接 `sorted()` 可能会报错，因为 Python 不知道应该按字符串还是数字规则比较。

## 028. `df["runtime_seconds"].describe().to_string()` 是什么意思？不加 `to_string()` 可以吗？

这句代码：

```python
df["runtime_seconds"].describe().to_string()
```

可以拆成三步：

```python
df["runtime_seconds"]
```

取出 DataFrame 里的 `runtime_seconds` 这一列。

```python
df["runtime_seconds"].describe()
```

让 pandas 对这一列做统计摘要，通常包括：

```text
count
mean
std
min
25%
50%
75%
max
```

最后：

```python
.to_string()
```

把 pandas 的结果显式转换成字符串。

在很多情况下：

```python
print(df["runtime_seconds"].describe())
```

也可以正常打印，因为 `print()` 会自动把对象转换成字符串。

写成：

```python
print(df["runtime_seconds"].describe().to_string())
```

主要是为了让输出更明确、更可控，尤其是在表格较宽、较长，或者要保存到文件时。

简单记法：

```text
describe()   -> 生成统计摘要
to_string()  -> 把 pandas 结果转成普通文本
```

学习阶段，不加 `to_string()` 通常也没问题：

```python
print(df["runtime_seconds"].describe())
```

## 029. 可以在每个 lesson 文件里加小问题来帮助对照学习吗？

可以。每节 lesson 末尾可以加一个统一的小节：

```markdown
## Quick Check

1. 小问题 1
2. 小问题 2
3. 小问题 3
```

这些问题不需要很长，重点是帮助快速验证：

- 是否理解本节核心概念。
- 是否知道关键代码在做什么。
- 是否能把输出和分析目标对应起来。
- 是否能发现自己还不确定的地方。

在这个学习目录里，`lessons/` 下每个文件都已经加入了 `## Quick Check` 小节。之后新增 lesson 时，也建议在末尾保留类似的小检查问题。

## 030. 为什么报错 `'function' object has no attribute 'copy'`？

这个报错通常说明：本来应该传入一个 pandas `DataFrame`，但实际传入了一个函数对象。

例如：

```python
raw = load_runtime_results
clean = clean_runtime_results(raw)
```

这里 `raw` 保存的是函数 `load_runtime_results` 本身，并没有真正执行读取 CSV 的动作。

应该加上括号调用函数：

```python
raw = load_runtime_results()
clean = clean_runtime_results(raw)
```

原因是 `clean_runtime_results(df)` 内部会执行：

```python
clean = df.copy()
```

`DataFrame` 有 `.copy()` 方法，但函数对象没有 `.copy()` 方法，所以 Python 报：

```text
AttributeError: 'function' object has no attribute 'copy'
```

简单记法：

```text
load_runtime_results    -> 函数本身
load_runtime_results()  -> 执行函数，得到返回值 DataFrame
```

可复查命令：

```bash
cd ~/leyan/jobSkill/petsc-benchmark-suite/s2795693/analysis/python_runtime_scaling_learning
python3 exercises/oneTry.py
```

## 033. 为什么 `clean["threads"]` 计算前要加 `.astype(int)`？

这句代码：

```python
calculated = clean["nodes"] * clean["ppn"] * clean["threads"].astype(int)
```

里的 `.astype(int)` 是为了把 `threads` 临时转换回整数再参与乘法。

原因在 `scripts/common.py` 的 `clean_runtime_results()` 里。清洗过程先把 `threads` 转成整数：

```python
clean[column] = clean[column].astype(int)
```

这样可以检查：

```python
total_cores == nodes * ppn * threads
```

但在函数后面，又把 `threads` 转成了 pandas 的有序分类类型：

```python
thread_type = pd.CategoricalDtype(categories=THREAD_ORDER, ordered=True)
clean["threads"] = clean["threads"].astype(thread_type)
```

这样做是为了让统计和排序时按照学习项目指定的顺序：

```text
1, 2, 4, 8
```

而不是让 pandas 自己猜顺序。

所以从 `clean_runtime_results(raw)` 返回以后，`clean["threads"]` 已经不是普通整数列，而是 categorical 列。categorical 适合分类、排序、统计，但不适合直接参与数学乘法。

因此重新计算 `total_cores` 时要写：

```python
calculated = clean["nodes"] * clean["ppn"] * clean["threads"].astype(int)
```

这里不是 pandas 自动转换，而是我们明确告诉 pandas：先把 `threads` 当成整数，再做乘法。

可复查 dtype：

```python
print(clean["threads"].dtype)
print(clean["threads"].astype(int).dtype)
```

可复查命令：

```bash
cd ~/leyan/jobSkill/petsc-benchmark-suite/s2795693/analysis/python_runtime_scaling_learning
python3 scripts/02_clean_and_filter.py
```

## 032. `value_counts()` 是自带函数吗？像 `to_string()` 一样吗？

`value_counts()` 不是 Python 语言自带函数，而是 pandas 对象提供的方法。

在当前练习里：

```python
clean["threads"].value_counts(sort=False)
```

含义是：取出 `threads` 这一列，然后统计每个不同取值出现了多少次。

例如如果 `threads` 这一列里有：

```text
1, 1, 2, 4, 4, 4
```

那么 `value_counts()` 会得到类似：

```text
1    2
2    1
4    3
```

`to_string()` 也不是 Python 语言自带函数，它也是 pandas 对象常见的方法，用来把 pandas 结果转换成更适合打印的文本。

常见写法：

```python
print(clean["threads"].value_counts(sort=False).to_string())
```

注意 Python 方法名区分大小写，应写：

```python
to_string()
```

不要写成：

```python
to_String()
```

简单记法：

```text
value_counts() -> 统计每个值出现几次
to_string()    -> 把 pandas 结果转成普通文本方便打印
```

可复查命令：

```bash
cd ~/leyan/jobSkill/petsc-benchmark-suite/s2795693/analysis/python_runtime_scaling_learning
python3 scripts/02_clean_and_filter.py
```

## 031. `len(raw)` 和 `raw.shape[0]` 是一个意思吗？

如果 `raw` 是 pandas `DataFrame`，它们通常表示同一个意思：DataFrame 的行数。

```python
len(raw)
raw.shape[0]
```

区别在于表达角度不同：

```python
len(raw)
```

更像是在问：“这个表有多少行？”

```python
raw.shape
```

会返回一个二元组：

```text
(行数, 列数)
```

所以：

```python
raw.shape[0]  # 行数
raw.shape[1]  # 列数
```

在当前练习里，这两句输出的行数应该相同：

```python
print(f"Raw rows: {len(raw)}")
print(f"Raw rows: {raw.shape[0]}")
```

学习阶段可以这样记：

```text
len(df)       -> 行数
df.shape[0]   -> 行数
df.shape[1]   -> 列数
df.shape      -> (行数, 列数)
```

可复查命令：

```bash
cd ~/leyan/jobSkill/petsc-benchmark-suite/s2795693/analysis/python_runtime_scaling_learning
python3 exercises/oneTry.py
```
