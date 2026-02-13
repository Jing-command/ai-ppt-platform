#!/bin/bash
# ESLint 批量修复脚本

cd /root/.openclaw/workspace/ai-ppt-platform/frontend

echo "=== 批量修复 ESLint 警告 ==="

# 1. 修复 ExportButton.tsx - 删除 FileImage
if [ -f "components/presentations/ExportButton.tsx" ]; then
    sed -i 's/, FileImage//g' components/presentations/ExportButton.tsx
    echo "✅ ExportButton.tsx"
fi

# 2. 修复 app/presentations/page.tsx - 删除未使用的图标
if [ -f "app/presentations/page.tsx" ]; then
    sed -i 's/, MoreHorizontal//g' app/presentations/page.tsx
    sed -i 's/, Activity//g' app/presentations/page.tsx
    echo "✅ presentations/page.tsx"
fi

# 3. 修复 hooks 依赖问题 - 添加 eslint-disable 注释
# 这需要更精确的处理，先跳过

echo "=== 基础修复完成 ==="
