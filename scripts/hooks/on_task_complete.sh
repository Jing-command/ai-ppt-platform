#!/bin/bash
#
# on_task_complete.sh - 任务完成钩子
# 自动更新项目状态文件
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TASK_NAME="${1:-Unknown Task}"
STATUS="${2:-success}"
COMMIT_SHA="${3:-}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[HOOK]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

cd "$PROJECT_ROOT"

log "任务完成钩子执行中..."
info "任务: $TASK_NAME"
info "状态: $STATUS"

# 1. 更新 task-queue.md
if [ -f "task-queue.md" ]; then
    log "更新 task-queue.md..."
    
    # 将任务标记为完成
    # 支持多种格式: - [ ] Task / - [x] Task / - [ ] **Task** / 等等
    if grep -q "\- \[ \].*$TASK_NAME" task-queue.md; then
        sed -i "s/\- \[ \]\(.*\)$TASK_NAME/\- [x]\1$TASK_NAME/g" task-queue.md
        log "✓ 已标记任务完成"
    else
        warn "在 task-queue.md 中未找到任务: $TASK_NAME"
    fi
    
    # 添加完成时间
    echo "" >> task-queue.md
    echo "<!-- Completed at: $(date '+%Y-%m-%d %H:%M:%S') -->" >> task-queue.md
else
    warn "task-queue.md 不存在"
fi

# 2. 更新 PROJECT_STATE.md
if [ -f "PROJECT_STATE.md" ]; then
    log "更新 PROJECT_STATE.md..."
    
    # 更新 "最近更新" 部分
    UPDATES_SECTION=$(cat << EOF

### $(date '+%Y-%m-%d'): $TASK_NAME
**状态**: ${STATUS}  
**提交**: ${COMMIT_SHA:-未提交}  
**时间**: $(date '+%H:%M:%S')

EOF
)
    
    # 在 "## 最近更新" 后插入
    if grep -q "## 最近更新" PROJECT_STATE.md; then
        # 使用临时文件
        awk -v updates="$UPDATES_SECTION" '/## 最近更新/{print; print updates; next}1' PROJECT_STATE.md > PROJECT_STATE.md.tmp
        mv PROJECT_STATE.md.tmp PROJECT_STATE.md
        log "✓ 已更新 PROJECT_STATE.md"
    else
        warn "PROJECT_STATE.md 中没有 '最近更新' 部分"
    fi
fi

# 3. 生成提交信息建议（如果成功）
if [ "$STATUS" = "success" ] && [ -z "$COMMIT_SHA" ]; then
    COMMIT_MSG="feat: $TASK_NAME"
    log "建议提交信息: $COMMIT_MSG"
    
    # 保存到临时文件
    echo "$COMMIT_MSG" > /tmp/ai-ppt-commit-msg.txt
    log "提交信息已保存到: /tmp/ai-ppt-commit-msg.txt"
fi

# 4. 记录到记忆文件
MEMORY_DIR="$PROJECT_ROOT/memory"
mkdir -p "$MEMORY_DIR"

{
    echo ""
    echo "## [$(date '+%Y-%m-%d %H:%M:%S')] Task Completed"
    echo ""
    echo "- **任务**: $TASK_NAME"
    echo "- **状态**: $STATUS"
    echo "- **提交**: ${COMMIT_SHA:-N/A}"
    echo ""
} >> "$MEMORY_DIR/completed-tasks.md"

# 5. 触发 CI/CD 检查（如果配置了）
if [ -f ".github/workflows/ci.yml" ] && [ "$STATUS" = "success" ]; then
    info "CI/CD 配置存在，准备推送..."
    
    if [ -d ".git" ]; then
        # 检查是否有未提交的更改
        if [ -n "$(git status --porcelain)" ]; then
            log "检测到未提交的更改"
            git add -A
            git commit -m "auto: $TASK_NAME completed"
            log "✓ 自动提交完成"
        fi
    fi
fi

# 6. 记录到钩子日志
{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] on_task_complete: $TASK_NAME -> $STATUS"
} >> "$MEMORY_DIR/hooks.log"

log "任务完成钩子执行完毕!"

exit 0
