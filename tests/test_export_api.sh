#!/bin/bash
# AI PPT Platform 导出系统 API 测试脚本

# 配置
BASE_URL="http://127.0.0.1:8000"
# 登录获取token
# TOKEN=$(curl -s -X POST $BASE_URL/api/v1/auth/login \
#   -H "Content-Type: application/json" \
#   -d '{"email": "test@example.com", "password": "123456"}' | jq -r '.accessToken')
TOKEN="your_access_token_here"

PRESENTATION_ID="your-presentation-id-here"

echo "=========================================="
echo "AI PPT Platform 导出系统 API 测试"
echo "=========================================="
echo ""

# 1. 导出 PPTX
echo "1. 导出 PPTX"
echo "POST /api/v1/exports/pptx"
curl -X POST "$BASE_URL/api/v1/exports/pptx?presentation_id=$PRESENTATION_ID&quality=high&slide_range=all&include_notes=false" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
echo ""
echo ""

# 2. 导出 PDF
echo "2. 导出 PDF"
echo "POST /api/v1/exports/pdf"
curl -X POST "$BASE_URL/api/v1/exports/pdf?presentation_id=$PRESENTATION_ID&quality=high&slide_range=all&include_notes=false" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
echo ""
echo ""

# 3. 导出 PNG 图片
echo "3. 导出 PNG 图片"
echo "POST /api/v1/exports/images"
curl -X POST "$BASE_URL/api/v1/exports/images?presentation_id=$PRESENTATION_ID&format=png&quality=high&slide_range=all" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
echo ""
echo ""

# 4. 查询导出状态 (需要替换为实际的任务ID)
echo "4. 查询导出状态"
echo "GET /api/v1/exports/{task_id}/status"
echo "curl -X GET \"
$BASE_URL/api/v1/exports/{task_id}/status \" \\"
echo "  -H \"Authorization: Bearer \$TOKEN\""
echo ""

# 5. 下载导出文件 (需要替换为实际的任务ID)
echo "5. 下载导出文件"
echo "GET /api/v1/exports/{task_id}/download"
echo "curl -X GET \"
$BASE_URL/api/v1/exports/{task_id}/download \" \\"
echo "  -H \"Authorization: Bearer \$TOKEN\" \""
echo "  -o presentation.pptx"
echo ""

echo "=========================================="
echo "测试完成"
echo "=========================================="
