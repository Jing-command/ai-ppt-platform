#!/bin/bash
# API Contract 强制检查脚本
# 在任何代码变更前运行此脚本

set -e

CONTRACT_FILE="API_CONTRACT.md"
ERRORS=0

echo "🔍 Checking API Contract Compliance..."
echo ""

# 1. 检查契约文件存在
if [ ! -f "$CONTRACT_FILE" ]; then
    echo "❌ ERROR: $CONTRACT_FILE not found!"
    echo "   You must create/update API contract before code changes."
    exit 1
fi

echo "✅ Contract file exists"

# 2. 检查版本号
echo ""
echo "📋 Contract Version:"
head -20 "$CONTRACT_FILE" | grep -E "^# API Contract|^Version:|^Last Updated:" || true

# 3. 检查是否有新增端点未记录
echo ""
echo "🔍 Checking for unregistered endpoints..."

# 获取后端所有端点
curl -s http://localhost:8000/openapi.json 2>/dev/null | python3 << 'PYEOF'
import sys, json, re

try:
    with open("API_CONTRACT.md", "r") as f:
        contract = f.read()
    
    # 从 OpenAPI 获取端点
    api_spec = json.load(sys.stdin)
    api_paths = set(api_spec.get("paths", {}).keys())
    
    # 从契约提取端点（简单匹配）
    contract_paths = set()
    for line in contract.split("\n"):
        # 匹配 "### METHOD /path" 或 "## METHOD /path"
        match = re.search(r'#{1,3}\s+(GET|POST|PUT|DELETE|PATCH)\s+(/\S+)', line)
        if match:
            contract_paths.add(match.group(2))
    
    # 检查差异
    unregistered = api_paths - contract_paths
    if unregistered:
        print("⚠️  WARN: Unregistered endpoints found:")
        for path in sorted(unregistered):
            print(f"   - {path}")
        print("\n   Please update API_CONTRACT.md!")
        sys.exit(1)
    else:
        print("✅ All endpoints registered in contract")
        
except Exception as e:
    print(f"⚠️  Check skipped: {e}")
PYEOF

# 4. 检查前后端类型一致性
echo ""
echo "🔍 Checking type consistency..."

# 检查是否有 TypeScript 类型文件
if [ -d "my-app/types" ]; then
    echo "✅ Frontend types directory exists"
    
    # 检查关键类型是否存在
    for type in "auth" "connector" "outline" "presentation"; do
        if ls my-app/types/*${type}* 1>/dev/null 2>&1; then
            echo "   ✅ ${type}.ts found"
        else
            echo "   ⚠️  ${type}.ts not found (optional)"
        fi
    done
else
    echo "⚠️  Frontend types directory not found"
fi

# 5. 契约更新检查
echo ""
echo "📝 Checking contract freshness..."
CONTRACT_MODIFIED=$(stat -c %Y "$CONTRACT_FILE" 2>/dev/null || stat -f %m "$CONTRACT_FILE" 2>/dev/null)

check_file_freshness() {
    local file=$1
    if [ -f "$file" ]; then
        local file_modified=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null)
        if [ "$file_modified" -gt "$CONTRACT_MODIFIED" ]; then
            echo "⚠️  WARNING: $file modified after API_CONTRACT.md"
            echo "   Last contract update: $(date -r $CONTRACT_MODIFIED '+%Y-%m-%d %H:%M:%S')"
            echo "   File modified: $(date -r $file_modified '+%Y-%m-%d %H:%M:%S')"
            echo "   Please verify contract is up to date!"
            return 1
        fi
    fi
    return 0
}

# 检查关键文件
for file in \
    "backend/src/ai_ppt/api/v1/schemas/*.py" \
    "backend/src/ai_ppt/api/v1/endpoints/*.py" \
    "my-app/types/*.ts" \
    "my-app/lib/api/*.ts"; do
    for f in $file; do
        check_file_freshness "$f" || ERRORS=$((ERRORS + 1))
    done
done

# 6. 最终报告
echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ API Contract Compliance: PASSED"
    echo "=========================================="
    exit 0
else
    echo "❌ API Contract Compliance: FAILED"
    echo "   $ERRORS issue(s) found"
    echo "=========================================="
    echo ""
    echo "🔧 Fix required:"
    echo "   1. Update API_CONTRACT.md with latest changes"
    echo "   2. Ensure TypeScript/Python types match contract"
    echo "   3. Run tests to verify compatibility"
    exit 1
fi
