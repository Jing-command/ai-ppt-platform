# 🪝 AI PPT Platform - 钩子系统 (Hook System)

**版本**: 1.0  
**用途**: 自动化上下文管理和工作流触发

---

## 📋 钩子类型

### 1. on_session_start
**触发时机**: 新对话/会话开始时  
**用途**: 自动加载项目上下文

**加载内容**:
- ✅ PROJECT_STATE.md - 项目状态和进度
- ✅ task-queue.md - 当前任务队列
- ✅ memory/ - 历史会话记忆
- ✅ API_CONTRACT.md - API 契约（如存在）

**钩子脚本**: `scripts/hooks/on_session_start.sh`

### 2. on_task_complete
**触发时机**: 子任务完成时  
**用途**: 自动更新项目状态

**执行操作**:
- 更新 task-queue.md（标记 ✅）
- 更新 PROJECT_STATE.md 进度
- 生成 commit message 建议
- 触发 CI/CD 检查

**钩子脚本**: `scripts/hooks/on_task_complete.sh`

### 3. on_ci_complete
**触发时机**: CI/CD 运行完成时  
**用途**: 自动处理 CI 结果

**执行操作**:
- CI 成功 → 更新状态为 ✅
- CI 失败 → 创建修复任务
- 发送通知

**钩子脚本**: `scripts/hooks/on_ci_complete.sh`

### 4. on_error
**触发时机**: 发生错误或异常时  
**用途**: 记录和恢复

**执行操作**:
- 记录错误到 error-log.md
- 保存当前上下文到 recovery/
- 生成故障报告

**钩子脚本**: `scripts/hooks/on_error.sh`

---

## 🔧 钩子配置

配置文件: `.hooks.yml` (项目根目录)

```yaml
version: "1.0"

hooks:
  on_session_start:
    enabled: true
    auto_load:
      - PROJECT_STATE.md
      - task-queue.md
      - memory/latest.md
    priority: high
    
  on_task_complete:
    enabled: true
    auto_update:
      - task-queue.md
      - PROJECT_STATE.md
    notify: true
    
  on_ci_complete:
    enabled: true
    auto_fix: false  # 是否自动派 sub-agent 修复
    
  on_error:
    enabled: true
    save_context: true
    max_recovery_files: 5

# 上下文加载配置
context:
  max_files: 5
  max_tokens: 4000
  order:  # 加载顺序
    - PROJECT_STATE.md
    - task-queue.md
    - API_CONTRACT.md
    - decisions.md
    - memory/

# Sub-agent 配置
subagent:
  model: "kimi-coding/k2p5"
  timeout: 600
  max_concurrent: 3
```

---

## 📁 文件结构

```
ai-ppt-platform/
├── .hooks.yml              # 钩子配置
├── HOOKS.md                # 本文档
├── PROJECT_STATE.md        # 项目状态（自动更新）
├── task-queue.md          # 任务队列（自动更新）
├── memory/                # 会话记忆
│   ├── index.md
│   ├── 2026-02-14-session-1.md
│   └── ...
├── recovery/              # 错误恢复文件
│   └── error-2026-02-14-001/
└── scripts/
    └── hooks/
        ├── on_session_start.sh
        ├── on_task_complete.sh
        ├── on_ci_complete.sh
        └── on_error.sh
```

---

## 🚀 快速开始

### 1. 初始化钩子系统

```bash
# 运行初始化脚本
./scripts/hooks/init.sh

# 或手动创建配置文件
cp .hooks.yml.example .hooks.yml
```

### 2. 配置自动加载

编辑 `.hooks.yml`:
```yaml
hooks:
  on_session_start:
    enabled: true
    auto_load:
      - PROJECT_STATE.md
      - task-queue.md
```

### 3. 测试钩子

```bash
# 手动触发会话启动钩子
./scripts/hooks/on_session_start.sh

# 查看加载的上下文
cat /tmp/openclaw-context-loaded.txt
```

---

## 📝 使用示例

### 场景 1: 新会话自动加载

**用户**: 开启新对话

**系统自动执行**:
1. 触发 `on_session_start`
2. 加载 PROJECT_STATE.md
3. 加载 task-queue.md
4. 将内容注入系统提示
5. 用户立即看到项目状态

### 场景 2: 任务完成自动更新

**Sub-agent**: 完成任务 "修复 API 认证"

**系统自动执行**:
1. 触发 `on_task_complete`
2. 在 task-queue.md 标记 ✅
3. 更新 PROJECT_STATE.md 进度
4. 生成 commit message
5. 推送代码并检查 CI

### 场景 3: CI 失败自动修复

**GitHub Actions**: CI 运行失败

**系统自动执行**:
1. 触发 `on_ci_complete`
2. 读取 CI 错误日志
3. 创建修复任务到 task-queue.md
4. 派 sub-agent 修复
5. 修复后重新提交

---

## 🔌 集成 OpenClaw

### 方案 1: 通过 AGENTS.md 触发

在 `AGENTS.md` 中添加:
```markdown
## 会话启动钩子

每次新会话开始时，自动执行:
```bash
./scripts/hooks/on_session_start.sh
```

## 任务完成钩子

Sub-agent 完成任务后，自动执行:
```bash
./scripts/hooks/on_task_complete.sh "$TASK_NAME" "$STATUS"
```
```

### 方案 2: 通过 OpenClaw 插件

创建 OpenClaw 插件 `hooks-plugin.js`:
```javascript
export default {
  name: "ai-ppt-hooks",
  onSessionStart: async () => {
    await exec("./scripts/hooks/on_session_start.sh");
  },
  onTaskComplete: async (task) => {
    await exec(`./scripts/hooks/on_task_complete.sh "${task.name}"`);
  }
};
```

### 方案 3: 通过 cron 定时触发

```bash
# 每 5 分钟检查 CI 状态
*/5 * * * * cd /path/to/ai-ppt-platform && ./scripts/hooks/check-ci.sh
```

---

## 🛠️ 钩子脚本 API

### on_session_start.sh

**输入**: 无  
**输出**: 加载的上下文文件列表

```bash
#!/bin/bash
# 加载项目上下文
CONTEXT_FILES=(
  "PROJECT_STATE.md"
  "task-queue.md"
)

for file in "${CONTEXT_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "Loading: $file"
    cat "$file" >> /tmp/openclaw-context.txt
  fi
done

echo "Context loaded successfully"
```

### on_task_complete.sh

**输入**: $1=任务名, $2=状态(success/failed)  
**输出**: 更新后的状态文件

```bash
#!/bin/bash
TASK_NAME="$1"
STATUS="$2"

# 更新 task-queue.md
sed -i "s/- \[ \] $TASK_NAME/- [x] $TASK_NAME/" task-queue.md

# 更新 PROJECT_STATE.md
if [ "$STATUS" = "success" ]; then
  echo "Task completed: $TASK_NAME" >> memory/completed-tasks.md
fi

echo "Updated: $TASK_NAME -> $STATUS"
```

---

## 📊 状态跟踪

钩子执行日志: `memory/hooks.log`

```
[2026-02-14 18:00:01] on_session_start: OK, loaded 3 files
[2026-02-14 18:15:30] on_task_complete: OK, "修复 API 认证" -> success
[2026-02-14 18:16:00] on_ci_complete: OK, CI passed
[2026-02-14 18:30:00] on_error: ERROR, mypy failed, recovery saved
```

---

## 🎯 下一步

1. [ ] 创建钩子脚本目录结构
2. [ ] 实现 on_session_start.sh
3. [ ] 实现 on_task_complete.sh
4. [ ] 实现 PROJECT_STATE.md 自动更新
5. [ ] 集成到 OpenClaw AGENTS.md
6. [ ] 测试完整工作流

---

**创建者**: Tagilla  
**创建时间**: 2026-02-14
