#!/bin/bash
#
# on_ci_complete.sh - CI/CD 完成钩子
# 处理 CI 结果并自动修复
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CI_STATUS="${1:-success}"  # success / failure
CI_JOB="${2:-unknown}"

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

log "CI/CD 完成钩子执行中..."
info "状态: $CI_STATUS"
info "任务: $CI_JOB"

MEMORY_DIR="$PROJECT_ROOT/memory"
mkdir -p "$MEMORY_DIR"

# 记录 CI 结果
{
    echo ""
    echo "## [$(date '+%Y-%m-%d %H:%M:%S')] CI/CD $CI_STATUS"
    echo ""
    echo "- **Job**: $CI_JOB"
    echo "- **Status**: $CI_STATUS"
    echo "- **Commit**: $(git rev-parse --short HEAD 2>/dev/null || echo 'N/A')"
    echo ""
} >> "$MEMORY_DIR/ci-history.md"

# 1. CI 成功处理
if [ "$CI_STATUS" = "success" ]; then
    log "✅ CI 成功!"
    
    # 更新 PROJECT_STATE.md
    if [ -f "PROJECT_STATE.md" ]; then
        # 标记 CI 状态为通过
        sed -i "s/- \[ \] CI\/CD 修复/- [x] CI\/CD 修复 (通过)/g" PROJECT_STATE.md 2>/dev/null || true
        log "✓ 已更新 PROJECT_STATE.md"
    fi
    
    # 发送成功通知（如果配置了）
    if [ -f ".hooks.yml" ] && grep -q "notify_on_success: true" .hooks.yml 2>/dev/null; then
        info "发送成功通知..."
        # TODO: 实现通知逻辑
    fi

# 2. CI 失败处理
else
    error "❌ CI 失败!"
    
    # 读取错误日志（如果存在）
    ERROR_LOG=""
    if [ -f "/tmp/ci-error.log" ]; then
        ERROR_LOG=$(head -50 /tmp/ci-error.log)
    fi
    
    # 创建修复任务
    REPAIR_TASK=$(cat << EOF

## 🚨 CI 修复任务

**创建时间**: $(date '+%Y-%m-%d %H:%M:%S')  
**失败任务**: $CI_JOB  
**错误日志**:
\`\`\`
${ERROR_LOG}
\`\`\`

**修复步骤**:
1. [ ] 分析错误原因
2. [ ] 修复代码
3. [ ] 本地测试
4. [ ] 重新提交

EOF
)
    
    # 添加到 task-queue.md
    if [ -f "task-queue.md" ]; then
        echo "" >> task-queue.md
        echo "$REPAIR_TASK" >> task-queue.md
        log "✓ 已创建修复任务到 task-queue.md"
    fi
    
    # 保存错误上下文
    RECOVERY_DIR="$PROJECT_ROOT/recovery/ci-$(date +%s)"
    mkdir -p "$RECOVERY_DIR"
    
    # 保存相关文件
    cp -r backend/src "$RECOVERY_DIR/" 2>/dev/null || true
    git status > "$RECOVERY_DIR/git-status.txt" 2>/dev/null || true
    git diff > "$RECOVERY_DIR/git-diff.txt" 2>/dev/null || true
    
    info "错误上下文已保存到: $RECOVERY_DIR"
    
    # 自动派 sub-agent 修复（如果配置了）
    if [ -f ".hooks.yml" ] && grep -q "auto_fix: true" .hooks.yml 2>/dev/null; then
        log "🤖 自动派 sub-agent 修复..."
        
        # 创建修复任务文件
        cat > /tmp/ai-ppt-repair-task.txt <> EOF
任务: 修复 CI 失败
错误: $CI_JOB
日志: ${ERROR_LOG:0:500}

请分析错误原因并修复代码。
EOF
        
        info "修复任务已创建: /tmp/ai-ppt-repair-task.txt"
        # TODO: 调用 sub-agent 进行修复
    fi
fi

# 记录到钩子日志
{
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] on_ci_complete: $CI_JOB -> $CI_STATUS"
} >> "$MEMORY_DIR/hooks.log"

log "CI/CD 完成钩子执行完毕!"

exit 0
