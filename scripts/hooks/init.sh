#!/bin/bash
#
# init.sh - 初始化钩子系统
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🚀 初始化 AI PPT Platform 钩子系统"
echo "======================================"
echo ""

cd "$PROJECT_ROOT"

# 1. 设置脚本可执行权限
echo "1. 设置脚本权限..."
chmod +x scripts/hooks/*.sh
echo "   ✓ 所有钩子脚本已设为可执行"

# 2. 创建必要的目录
echo "2. 创建目录结构..."
mkdir -p memory
mkdir -p recovery
echo "   ✓ memory/ 目录已创建"
echo "   ✓ recovery/ 目录已创建"

# 3. 检查配置文件
echo "3. 检查配置文件..."
if [ ! -f ".hooks.yml" ]; then
    if [ -f ".hooks.yml.example" ]; then
        cp .hooks.yml.example .hooks.yml
        echo "   ✓ 已从示例创建 .hooks.yml"
    else
        echo "   ⚠️  .hooks.yml 不存在，请手动创建"
    fi
else
    echo "   ✓ .hooks.yml 已存在"
fi

# 4. 创建初始记忆文件
echo "4. 创建初始记忆文件..."
if [ ! -f "memory/hooks.log" ]; then
    echo "# Hooks Execution Log" > memory/hooks.log
    echo "Created at: $(date)" >> memory/hooks.log
    echo "" >> memory/hooks.log
    echo "   ✓ memory/hooks.log 已创建"
fi

if [ ! -f "memory/completed-tasks.md" ]; then
    echo "# Completed Tasks" > memory/completed-tasks.md
    echo "" >> memory/completed-tasks.md
    echo "   ✓ memory/completed-tasks.md 已创建"
fi

# 5. 测试钩子
echo "5. 测试钩子..."
echo ""
echo "   测试 on_session_start.sh..."
CONTEXT_FILE=$(./scripts/hooks/on_session_start.sh)
if [ -f "$CONTEXT_FILE" ]; then
    LINES=$(wc -l < "$CONTEXT_FILE")
    echo "   ✓ 测试成功，加载了 $LINES 行上下文"
    rm -f "$CONTEXT_FILE"
else
    echo "   ⚠️  测试未生成上下文文件"
fi

echo ""
echo "======================================"
echo "✅ 钩子系统初始化完成!"
echo ""
echo "使用方法:"
echo "  1. 手动触发: ./scripts/hooks/on_session_start.sh"
echo "  2. 新会话时自动触发（需配置 OpenClaw）"
echo "  3. 任务完成时: ./scripts/hooks/on_task_complete.sh '任务名' 'success'"
echo ""
echo "配置文件: .hooks.yml"
echo "日志文件: memory/hooks.log"
echo ""
