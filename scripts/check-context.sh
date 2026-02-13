#!/bin/bash
# Context Monitor - 检查当前上下文使用情况
# 可以集成到心跳或定期检查中

echo "📊 Context Usage Monitor"
echo "========================"
echo ""

# 尝试多种方式获取上下文大小

# 方法 1: 从 session_status（如果 OpenClaw 支持）
if command -v openclaw &> /dev/null; then
    echo "Checking via openclaw CLI..."
    openclaw status 2>/dev/null || echo "  CLI not available"
fi

# 方法 2: 从环境变量
if [ -n "$OPENCLAW_CONTEXT_TOKENS" ]; then
    echo "Environment variable found:"
    echo "  Tokens: $OPENCLAW_CONTEXT_TOKENS"
    CURRENT=$OPENCLAW_CONTEXT_TOKENS
fi

# 方法 3: 估算（基于工作目录大小）
if [ -z "$CURRENT" ]; then
    echo "Estimating from project files..."
    
    # 统计代码行数作为粗略估算
    if [ -d "src" ] || [ -d "backend/src" ]; then
        CODE_LINES=$(find . -name "*.py" -o -name "*.ts" -o -name "*.tsx" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
        echo "  Code lines: ~$CODE_LINES"
        
        # 粗略估算：每行代码约 5-10 tokens，对话历史约 50-100K
        ESTIMATED=$((CODE_LINES * 7 + 50000))
        echo "  Estimated tokens: ~$ESTIMATED"
        CURRENT=$ESTIMATED
    fi
fi

# 方法 4: 询问用户
if [ -z "$CURRENT" ]; then
    echo ""
    echo "⚠️  Unable to automatically detect context size"
    echo ""
    read -p "Enter current context size in tokens (or press Enter for 150000 estimate): " USER_INPUT
    CURRENT=${USER_INPUT:-150000}
fi

# 计算
LIMIT=256000
THRESHOLD=$((LIMIT * 75 / 100))
PERCENTAGE=$((CURRENT * 100 / LIMIT))

echo ""
echo "Results:"
echo "--------"
echo "Current Usage: $CURRENT / $LIMIT tokens"
echo "Percentage:    $PERCENTAGE%"
echo "Threshold:     75% ($THRESHOLD tokens)"
echo ""

# 状态判断
if [ "$PERCENTAGE" -ge "90" ]; then
    echo "🔴 STATUS: CRITICAL"
    echo "   Context is critically high!"
    echo "   Immediate compression required."
    echo ""
    echo "Run: ./scripts/auto-compress.sh --force"
    exit 2
elif [ "$PERCENTAGE" -ge "75" ]; then
    echo "🟡 STATUS: WARNING"
    echo "   Context reached 75% threshold."
    echo "   Compression recommended."
    echo ""
    echo "Run: ./scripts/auto-compress.sh"
    exit 1
elif [ "$PERCENTAGE" -ge "60" ]; then
    echo "🟢 STATUS: ELEVATED"
    echo "   Context is getting high."
    echo "   Consider completing current task soon."
    exit 0
else
    echo "🟢 STATUS: HEALTHY"
    echo "   Context usage normal."
    echo "   Continue working."
    exit 0
fi
