#!/bin/bash
#
# on_session_start.sh - 新会话启动钩子
# 自动加载项目上下文到 OpenClaw
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MEMORY_DIR="$PROJECT_ROOT/memory"
CONTEXT_FILE="/tmp/ai-ppt-context-$(date +%s).txt"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[HOOK]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 确保目录存在
mkdir -p "$MEMORY_DIR"

log "会话启动钩子执行中..."
log "项目根目录: $PROJECT_ROOT"

# 清空之前的上下文
> "$CONTEXT_FILE"

# 加载项目状态
cd "$PROJECT_ROOT"

log "加载项目上下文..."

# 1. 加载 PROJECT_STATE.md
if [ -f "PROJECT_STATE.md" ]; then
    log "✓ 加载 PROJECT_STATE.md"
    {
        echo ""
        echo "=========================================="
        echo "📊 PROJECT STATE"
        echo "=========================================="
        head -100 PROJECT_STATE.md
        echo ""
    } >> "$CONTEXT_FILE"
else
    warn "PROJECT_STATE.md 不存在"
fi

# 2. 加载 task-queue.md
if [ -f "task-queue.md" ]; then
    log "✓ 加载 task-queue.md"
    {
        echo ""
        echo "=========================================="
        echo "📋 TASK QUEUE"
        echo "=========================================="
        cat task-queue.md
        echo ""
    } >> "$CONTEXT_FILE"
else
    warn "task-queue.md 不存在"
fi

# 3. 加载 API_CONTRACT.md（如果存在）
if [ -f "API_CONTRACT.md" ]; then
    log "✓ 加载 API_CONTRACT.md"
    {
        echo ""
        echo "=========================================="
        echo "🔌 API CONTRACT"
        echo "=========================================="
        head -50 API_CONTRACT.md
        echo ""
    } >> "$CONTEXT_FILE"
fi

# 4. 加载最近的记忆
if [ -d "memory" ]; then
    LATEST_MEMORY=$(ls -t memory/*.md 2>/dev/null | head -1)
    if [ -n "$LATEST_MEMORY" ]; then
        log "✓ 加载最近记忆: $LATEST_MEMORY"
        {
            echo ""
            echo "=========================================="
            echo "🧠 RECENT MEMORY"
            echo "=========================================="
            head -50 "$LATEST_MEMORY"
            echo ""
        } >> "$CONTEXT_FILE"
    fi
fi

# 5. 记录加载事件
{
    echo ""
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Session started, context loaded"
    echo "Files loaded: PROJECT_STATE.md, task-queue.md"
    echo "Context file: $CONTEXT_FILE"
    echo ""
} >> "$MEMORY_DIR/hooks.log"

# 输出上下文文件路径（供 OpenClaw 读取）
echo "$CONTEXT_FILE"

log "上下文加载完成!"
log "总文件数: $(wc -l < "$CONTEXT_FILE") 行"
log "上下文文件: $CONTEXT_FILE"

# 可选: 将上下文输出到 stdout（供 OpenClaw 捕获）
if [ "${HOOK_OUTPUT_CONTEXT:-false}" = "true" ]; then
    cat "$CONTEXT_FILE"
fi

exit 0
