---
name: "tencent-code-guide"
description: "Enforces Tencent coding standards for frontend (AlloyTeam) and backend (PEP 8). Invoke when writing, reviewing, or refactoring code to ensure compliance with Tencent code conventions."
---

# 腾讯代码规范指南

本 Skill 提供腾讯代码规范的完整指南，帮助 Agent 在生成代码时遵循统一的编码标准。

## 规范来源

- **前端规范**：腾讯 AlloyTeam 前端代码规范 http://alloyteam.github.io/CodeGuide/
- **后端规范**：PEP 8 - Python 代码风格指南 https://peps.python.org/pep-0008/

---

## 一、前端代码规范（JavaScript / TypeScript）

### 1. 文件与目录命名

```
项目与文件：全部小写，下划线分割 → my_project.js
目录命名：小写、下划线，复数结构 → styles, scripts
CSS 类名：小写，中划线 → my-class-name
```

### 2. 缩进与格式

- **缩进**：2 个空格（soft tab）
- **单行长度**：不超过 120 字符
- **换行符**：统一使用 `LF`

### 3. 分号

以下情况后必须加分号：
- 变量声明、表达式、`return`、`throw`、`break`、`continue`、`do-while`

```javascript
// 正确示例
var x = 1;
x++;
return x;
```

### 4. 引号

- **最外层统一使用单引号**

```javascript
// 正确
var y = 'foo';
var z = '<div id="test"></div>';

// 错误
var x = "test";
```

### 5. 空格规则

**不需要空格：**
- 对象属性名后、一元运算符、函数调用括号前、数组/对象括号内侧

**需要空格：**
- 二元运算符前后、三元运算符前后、代码块 `{` 前、关键字前后

```javascript
// 正确
var a = { b: 1, c: 2 };
++x;
y++;
z = x ? 1 : 2;
for (i = 0; i < 6; i++) { }
```

### 6. 变量命名

| 类型 | 规范 | 示例 |
|------|------|------|
| 标准变量 | 驼峰式 | `thisIsMyName` |
| ID | 全大写 | `goodID` |
| URL | 全大写 | `reportURL` |
| Android | 大写首字母 | `AndroidVersion` |
| iOS | 小写首字母 | `iOSVersion` |
| 常量 | 全大写，下划线 | `MAX_COUNT` |
| 构造函数 | 大写首字母 | `Person` |
| jQuery 对象 | `$` 开头 | `$body` |

### 7. 比较运算符

- 使用 `===` 和 `!==` 代替 `==` 和 `!=`

### 8. for-in 循环

- 必须包含 `hasOwnProperty` 判断

```javascript
for (key in obj) {
    if (obj.hasOwnProperty(key)) {
        console.log(obj[key]);
    }
}
```

### 9. 大括号

- 下列关键字后必须有大括号：`if`, `else`, `for`, `while`, `do`, `switch`, `try`, `catch`, `finally`, `with`

```javascript
// 正确
if (condition) {
    doSomething();
}

// 错误
if (condition)
    doSomething();
```

### 10. undefined 判断

- 使用 `typeof` 和字符串 `'undefined'`

```javascript
// 正确
if (typeof person === 'undefined') { }

// 错误
if (person === undefined) { }
```

---

## 二、后端代码规范（Python）

### 1. 缩进

- **使用 4 个空格缩进**
- 不要使用 Tab，更不能混用 Tab 和空格

### 2. 行长度

- **代码行最大长度：79 字符**
- **文档字符串和注释：72 字符**

### 3. 空行

- 顶层函数和类定义周围：2 个空行
- 类内方法定义周围：1 个空行

### 4. 导入

```python
# 正确：分开导入，按顺序分组
import os
import sys

from subprocess import Popen, PIPE

import numpy as np

from mypackage import mymodule
```

### 5. 命名规范

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

### 6. 函数参数

- 实例方法第一个参数：`self`
- 类方法第一个参数：`cls`
- 参数名与关键字冲突时：添加尾部下划线

```python
class MyClass:
    def __init__(self, name):
        self.name = name

    @classmethod
    def from_string(cls, string):
        return cls(string)
```

### 7. 比较运算

- 与 `None` 比较使用 `is` 或 `is not`

```python
# 正确
if foo is not None:

# 错误
if not foo is None:
if foo == None:
```

### 8. 异常处理

```python
# 正确：使用特定异常
try:
    value = collection[key]
except KeyError:
    return key_not_found(key)
else:
    return handle_value(value)

# 错误：裸 except
try:
    ...
except:
    ...
```

### 9. 类型提示

```python
# 正确
def munge(input: AnyStr, sep: AnyStr = None) -> PosInt:
    ...

# 错误
def munge(input:AnyStr=None)->PosInt:
    ...
```

### 10. 文档字符串

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

---

## 三、检查命令

### 前端检查

```bash
cd frontend
npm run lint        # ESLint 检查
npm run type-check  # TypeScript 类型检查
```

### 后端检查

```bash
cd backend
ruff check src/             # 代码检查
ruff format src/ --check    # 格式检查
mypy src/                   # 类型检查
```

---

## 四、重要提醒

1. **所有 Agent 在生成代码时必须严格遵循以上规范**
2. **代码注释使用中文，变量名、函数名使用英文**
3. **提交代码前必须通过所有检查**
4. **保持代码风格一致、可读性强、易于维护**
