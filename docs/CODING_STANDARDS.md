# 腾讯代码规范 - 详细指南

本文档包含项目代码规范的详细内容，所有 Agent 在生成代码时必须严格遵循。

---

## 一、前端代码规范（JavaScript / TypeScript）

> 来源：腾讯 AlloyTeam 前端代码规范 http://alloyteam.github.io/CodeGuide/

### 1. 文件与目录命名

- **项目与文件命名**：全部小写，使用下划线分割。例如：`my_project.js`
- **目录命名**：小写、下划线，有复数结构时使用复数。例如：`styles`、`scripts`
- **CSS 类名**：小写，使用中划线连接。例如：`my-class-name`

### 2. 缩进与格式

- **缩进**：使用 4 个空格（soft tab）
- **单行长度**：不超过 80 个字符
- **换行符**：统一使用 `LF`

### 3. 分号

以下情况后必须加分号：
- 变量声明
- 表达式
- `return`
- `throw`
- `break`
- `continue`
- `do-while`

```javascript
// 正确示例
var x = 1;
x++;
return x;

do {
    x++;
} while (x < 10);
```

### 4. 空格规则

**不需要空格的情况：**
- 对象属性名后
- 前缀/后缀一元运算符
- 函数调用括号前
- 数组的 `[` 后和 `]` 前
- 对象的 `{` 后和 `}` 前

**需要空格的情况：**
- 二元运算符前后
- 三元运算符 `?:` 前后
- 代码块 `{` 前
- 关键字 `else, while, catch, finally` 前
- 关键字 `if, else, for, while, do, switch, case, try, catch, finally, with, return, typeof` 后
- 单行注释 `//` 后
- for 循环分号后

```javascript
// 正确示例
var a = {
    b: 1,
    c: 2
};

++x;
y++;
z = x ? 1 : 2;

var doSomething = function(a, b, c) {
    // do something
};

for (i = 0; i < 6; i++) {
    x++;
}
```

### 5. 引号

- **最外层统一使用单引号**

```javascript
// 正确
var y = 'foo',
    z = '<div id="test"></div>';

// 错误
var x = "test";
```

### 6. 变量命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 标准变量 | 驼峰式 | `thisIsMyName` |
| ID | 全大写 | `goodID` |
| URL | 全大写 | `reportURL` |
| Android | 大写首字母 | `AndroidVersion` |
| iOS | 小写首字母，大写后两个 | `iOSVersion` |
| 常量 | 全大写，下划线连接 | `MAX_COUNT` |
| 构造函数 | 大写首字母 | `Person` |
| jQuery 对象 | `$` 开头 | `$body` |

### 7. 变量声明

- 一个函数作用域中所有变量声明尽量提到函数首部
- 使用一个 `var` 声明（或 `let`/`const`）

```javascript
// 正确示例
function doSomethingWithItems(items) {
    var value = 10,
        result = value + 10,
        i,
        len;

    for (i = 0, len = items.length; i < len; i++) {
        result += 10;
    }
}
```

### 8. null 使用

**适用场景：**
- 初始化将来可能被赋值为对象的变量
- 与已初始化的变量做比较
- 作为参数为对象的函数调用传参
- 作为返回对象的函数返回值

**不适用场景：**
- 不要用 `null` 判断函数调用时有无传参
- 不要与未初始化的变量做比较

### 9. undefined 判断

- 永远不要直接使用 `undefined` 进行变量判断
- 使用 `typeof` 和字符串 `'undefined'`

```javascript
// 正确
if (typeof person === 'undefined') {
    ...
}

// 错误
if (person === undefined) {
    ...
}
```

### 10. 比较运算符

- 使用 `===` 和 `!==` 代替 `==` 和 `!=`

### 11. for-in 循环

- 必须包含 `hasOwnProperty` 判断

```javascript
// 正确
for (key in obj) {
    if (obj.hasOwnProperty(key)) {
        console.log(obj[key]);
    }
}
```

### 12. 函数规范

- `'('` 前不要空格，`'{'` 前一定要有空格
- 立即执行函数外必须包一层括号
- 不要给 inline function 命名
- 参数之间用 `', '` 分隔

```javascript
// 正确
var doSomething = function(item) {
    // do something
};

(function() {
    return 1;
})();

[1, 2].forEach(function() {
    ...
});
```

### 13. 数组与对象

- 对象属性名不需要加引号
- 对象以缩进形式书写，不要写在一行
- 数组、对象最后不要有逗号

```javascript
// 正确
var a = {
    b: 1,
    c: 2
};

// 错误
var a = {
    'b': 1
};

var a = {b: 1};

var a = {
    b: 1,
    c: 2,
};
```

### 14. 括号与大括号

- 下列关键字后必须有大括号（即使代码块只有一行）：`if`, `else`, `for`, `while`, `do`, `switch`, `try`, `catch`, `finally`, `with`

```javascript
// 正确
if (condition) {
    doSomething();
}

// 错误
if (condition)
    doSomething();
```

### 15. 注释规范

**单行注释：**
- 双斜线后必须跟一个空格
- 缩进与下一行代码保持一致

**多行注释：**
- 最少三行
- `*` 后跟一个空格

**文档注释：**
- 所有常量、函数、类都应有文档注释
- 使用 JSDoc 格式

```javascript
/**
 * @func
 * @desc 一个带参数的函数
 * @param {string} a - 参数a
 * @param {number} b=1 - 参数b默认值为1
 * @returns {number} 返回值
 */
function foo(a, b = 1) {
    return a + b;
}
```

### 16. 杂项

- 不要混用 tab 和 space
- 对 `this` 的引用只能使用 `_this`、`that`、`self` 其中一个命名
- 行尾不要有空白字符
- `switch` 的 falling through 和 no default 情况要有注释说明
- 不允许有空的代码块
- `debugger` 不要出现在提交的代码里

---

## 二、后端代码规范（Python）

> 来源：PEP 8 - Python 代码风格指南 https://peps.python.org/pep-0008/

### 1. 缩进

- **使用 4 个空格缩进**
- 不要使用 Tab，更不能混用 Tab 和空格

### 2. 行长度

- **代码行最大长度：79 字符**
- **文档字符串和注释：72 字符**
- 长行使用括号换行，避免使用反斜杠

```python
# 正确
foo = long_function_name(var_one, var_two,
                         var_three, var_four)

def long_function_name(
        var_one, var_two, var_three,
        var_four):
    print(var_one)
```

### 3. 空行

- 顶层函数和类定义周围使用两个空行
- 类内方法定义周围使用一个空行
- 函数内使用空行分隔逻辑段落（谨慎使用）

### 4. 导入

- 导入应该分开写在不同的行
- 导入顺序：标准库 → 第三方库 → 本地应用库
- 每组导入之间空一行

```python
# 正确
import os
import sys

from subprocess import Popen, PIPE

import numpy as np

from mypackage import mymodule
```

### 5. 字符串引号

- 单引号和双引号等效，选择一种并保持一致
- 当字符串包含单引号时使用双引号，反之亦然
- 三引号字符串（文档字符串）统一使用双引号

### 6. 空格

**避免空格的情况：**
- 括号内部紧贴括号
- 逗号、分号、冒号前
- 函数调用括号前
- 索引或切片括号前

**需要空格的情况：**
- 二元运算符两侧
- 赋值运算符两侧
- 比较运算符两侧
- 布尔运算符两侧

```python
# 正确
spam(ham[1], {eggs: 2})
x = 1
y = 2
long_variable = 3

if x == 4: print(x, y)

# 错误
spam( ham[ 1 ], { eggs: 2 } )
x             = 1
y             = 2
long_variable = 3
```

### 7. 命名规范

| 类型 | 命名风格 | 示例 |
|------|----------|------|
| 模块 | 小写，可用下划线 | `my_module.py` |
| 包 | 小写，不用下划线 | `mypackage` |
| 类 | 驼峰式（CapWords） | `MyClass` |
| 异常 | 驼峰式 + Error 后缀 | `MyError` |
| 函数/方法 | 小写 + 下划线 | `my_function` |
| 变量 | 小写 + 下划线 | `my_variable` |
| 常量 | 全大写 + 下划线 | `MAX_OVERFLOW` |
| 私有属性 | 单下划线前缀 | `_private_var` |
| 强私有属性 | 双下划线前缀 | `__very_private` |

### 8. 函数和方法参数

- 实例方法第一个参数使用 `self`
- 类方法第一个参数使用 `cls`
- 如果参数名与关键字冲突，添加尾部下划线

```python
class MyClass:
    def __init__(self, name):
        self.name = name

    @classmethod
    def from_string(cls, string):
        return cls(string)

    def process(self, class_):  # 避免与关键字冲突
        pass
```

### 9. 比较运算

- 与 `None` 比较使用 `is` 或 `is not`
- 使用 `is not` 而非 `not ... is`

```python
# 正确
if foo is not None:

# 错误
if not foo is None:
if foo == None:
```

### 10. 异常处理

- 从 `Exception` 而非 `BaseException` 派生异常
- 异常类名以 `Error` 结尾
- 使用特定异常而非裸 `except:`
- 使用异常链 `raise X from Y`

```python
# 正确
try:
    value = collection[key]
except KeyError:
    return key_not_found(key)
else:
    return handle_value(value)

# 错误
try:
    return handle_value(collection[key])
except:  # 太宽泛
    return key_not_found(key)
```

### 11. 类型提示

- 使用 PEP 484 语法
- 冒号后有一个空格
- 默认值等号两侧有空格

```python
# 正确
def munge(input: AnyStr, sep: AnyStr = None) -> PosInt:
    ...

# 错误
def munge(input:AnyStr=None)->PosInt:
    ...
```

### 12. 文档字符串

- 使用三引号
- 简短摘要写在第一行
- 使用命令式语气

```python
def function_with_types_in_docstring(param1, param2):
    """函数功能简述。

    详细描述。

    Args:
        param1 (int): 第一个参数说明
        param2 (str): 第二个参数说明

    Returns:
        bool: 返回值说明

    Raises:
        ValueError: 异常说明
    """
    return True
```

### 13. 编程建议

- 使用 `startswith()` 和 `endswith()` 代替字符串切片
- 使用 `isinstance()` 代替类型比较
- 空序列判断使用 `if not seq:` 而非 `if len(seq):`
- 不要用 `==` 比较 `True` 或 `False`
- 使用 `with` 语句管理资源
- 返回语句保持一致

```python
# 正确
if foo.startswith('bar'):
if isinstance(obj, int):
if not seq:
if greeting:

# 错误
if foo[:3] == 'bar':
if type(obj) is type(1):
if len(seq):
if greeting == True:
```

---

## 三、CSS 规范

### 属性声明顺序

1. **定位相关**：`display`, `visibility`, `float`, `clear`, `overflow`, `position`, `top`, `right`, `bottom`, `left`, `z-index`
2. **盒模型**：`margin`, `border`, `padding`, `width`, `height`
3. **排版相关**：`font`, `line-height`, `text-align`, `vertical-align`
4. **视觉样式**：`color`, `background`
5. **其他**：`opacity`, `animation`, `transform`

---

## 四、通用规范

### 1. 注释语言

- 代码注释使用中文（与项目团队语言保持一致）
- 变量名、函数名使用英文

### 2. 代码审查

- 所有代码提交前必须通过 ESLint/Flake8 检查
- 所有代码提交前必须通过类型检查（TypeScript/mypy）

### 3. 版本控制

- 提交信息使用中文，格式清晰
- 每次提交应该是原子性的，只做一件事

---

## 五、检查命令

### 前端检查

```bash
cd frontend
npm run lint        # ESLint 检查
npm run type-check  # TypeScript 类型检查
```

### 后端检查

```bash
cd backend
black --check src/          # 格式检查
isort --check src/          # 导入排序检查
mypy src/                   # 类型检查
flake8 src/                 # 风格检查
```
