# Context Compression 使用指南

快速上手指南，帮助你在上下文达到 75% 时自动压缩。

## 快速开始

### 1. 检查当前上下文

```bash
./scripts/check-context.sh
```

输出示例：
```
📊 Context Usage Monitor
========================

Results:
--------
Current Usage: 180000 / 256000 tokens
Percentage:    70%
Threshold:     75% (192000 tokens)

🟢 STATUS: ELEVATED
   Context is getting high.
   Consider completing current task soon.
```

### 2. 达到 75% 时自动压缩

当系统检测到上下文达到 75%：

```
⚠️  CONTEXT COMPRESSION REQUIRED
   Current: 76% >= Threshold: 75%

📝 Starting compression...

✅ Backed up PROJECT_STATE.md
✅ Backed up task-queue.md
✅ Created task-queue.md
✅ Created RESUME.md

================================
✅ COMPRESSION COMPLETE
================================

Next steps:
  1. Review PROJECT_STATE.md
  2. Update task-queue.md with current tasks
  3. End this session
  4. Start new session
  5. Use recovery command from .context-compression/RESUME.md
```

### 3. 手动触发压缩

如果需要立即压缩：

```bash
./scripts/auto-compress.sh --force
```

### 4. 新会话恢复

在新会话中，发送以下消息：

```markdown
请读取以下文件恢复项目上下文：

```bash
cat PROJECT_STATE.md
cat .context-compression/task-queue.md
cat .context-compression/decisions.md 2>/dev/null || echo "No decisions log"
```

然后继续任务：
[从 task-queue.md 中复制当前任务]

请确认已恢复上下文，然后继续任务。
```

## 工作流程图

```
┌─────────────────────────────────────────────────────────────┐
│                      正常工作                                │
│                          │                                  │
│                          ▼                                  │
│              ┌──────────────────────┐                      │
│              │ 检查上下文使用率      │                      │
│              │ ./check-context.sh   │                      │
│              └──────────────────────┘                      │
│                          │                                  │
│              ┌───────────┴───────────┐                      │
│              ▼                       ▼                      │
│         < 75%                     >= 75%                   │
│              │                       │                      │
│              ▼                       ▼                      │
│       继续工作                自动压缩                      │
│                               ./auto-compress.sh           │
│                                     │                      │
│                                     ▼                      │
│                           ┌──────────────────┐            │
│                           │ 保存关键信息      │            │
│                           │ - PROJECT_STATE   │            │
│                           │ - task-queue      │            │
│                           │ - decisions       │            │
│                           └──────────────────┘            │
│                                     │                      │
│                                     ▼                      │
│                           ┌──────────────────┐            │
│                           │ 生成恢复指令      │            │
│                           │ RESUME.md        │            │
│                           └──────────────────┘            │
│                                     │                      │
│                                     ▼                      │
│                           提示切换新会话                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      新会话恢复                              │
│                                                              │
│  1. 读取 PROJECT_STATE.md                                    │
│  2. 读取 task-queue.md                                       │
│  3. 读取 decisions.md (可选)                                 │
│  4. 继续任务                                                 │
│                                                              │
│  上下文: 5K tokens (3%)                                      │
│  性能: 100%                                                  │
└─────────────────────────────────────────────────────────────┘
```

## 文件说明

### PROJECT_STATE.md
**必须**，~2KB

包含：
- 项目概述
- 技术栈
- 当前迭代
- 关键决策
- 文件位置

### .context-compression/task-queue.md
**必须**，~1KB

包含：
- 进行中任务
- 待办任务
- 已完成任务

### .context-compression/decisions.md
**可选**，~2KB

包含：
- 架构决策
- 技术选型理由
- 变更历史

### .context-compression/RESUME.md
**自动生成**

包含：
- 恢复指令
- 文件清单
- 上次会话信息

## 最佳实践

### 1. 定期保存
不要等到 75%，在 60-70% 时就考虑：
- 完成当前子任务
- 运行 `./auto-compress.sh`
- 切换新会话

### 2. 保持文件更新
每次压缩后：
- 检查 PROJECT_STATE.md 是否最新
- 更新 task-queue.md 中的任务状态
- 添加重要的新决策到 decisions.md

### 3. 版本控制
```bash
# 提交压缩文件到 git
git add PROJECT_STATE.md
git add .context-compression/
git commit -m "docs: update project state and task queue"
```

### 4. 备份策略
压缩文件会自动备份到：
```
.context-compression/backup/YYYYMMDD-HHMMSS/
```

保留最近 5 个备份，防止数据丢失。

## 故障排除

### 问题 1: 无法检测上下文大小

**现象**：
```
⚠️  Unable to automatically detect context size
```

**解决**：
```bash
# 方法 1: 手动指定大小
./scripts/auto-compress.sh --estimate 180000

# 方法 2: 强制压缩
./scripts/auto-compress.sh --force
```

### 问题 2: 恢复后信息不完整

**现象**：新会话缺少关键上下文

**解决**：
1. 检查是否读取了所有必需文件
2. 查看 decisions.md 补充决策历史
3. 简短回顾关键上下文
4. 更新压缩策略

### 问题 3: 压缩文件冲突

**现象**：多个 Agent 同时修改压缩文件

**解决**：
1. 使用 git 管理压缩文件
2. 修改前 git pull
3. 修改后 git commit && git push

## 高级用法

### 集成到 CI/CD

```yaml
# .github/workflows/context-check.yml
- name: Check Context Health
  run: |
    ./scripts/check-context.sh
    if [ $? -eq 2 ]; then
      echo "Context critical, forcing compression"
      ./scripts/auto-compress.sh --force
    fi
```

### 自定义阈值

```bash
# 修改默认阈值（例如改为 80%）
export THRESHOLD=0.80
./scripts/auto-compress.sh
```

### 监控多个项目

```bash
# 为每个项目创建独立配置
mkdir -p .context-compression/project-a
mkdir -p .context-compression/project-b
```

## 性能对比

| 指标 | 不压缩 | 本方案 |
|------|--------|--------|
| 上下文大小 | 200K+ | 5-10K |
| 模型性能 | ⭐⭐ 下降 | ⭐⭐⭐⭐⭐ 最佳 |
| 响应速度 | 慢 | 快 |
| 信息完整性 | ⭐⭐⭐⭐⭐ 完整 | ⭐⭐⭐⭐ 核心保留 |
| 会话切换 | 困难 | 简单 |

## 总结

使用 Context Compression：
- ✅ 上下文压缩 95%+
- ✅ 模型性能始终最佳
- ✅ 核心信息 100% 保留
- ✅ 会话切换无缝衔接

**记住**：PROJECT_STATE.md 是项目的"心脏"，保持它最新！
