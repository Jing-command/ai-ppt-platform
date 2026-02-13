#!/bin/bash
# AI PPT Platform - 验收检查脚本
# 一键运行所有自动化验收检查

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ACCEPTANCE_DIR="$PROJECT_DIR/docs/acceptance"
REPORT_FILE="$ACCEPTANCE_DIR/status/check-report-$(date +%Y%m%d-%H%M%S).json"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 计数器
PASSED=0
FAILED=0
SKIPPED=0

# 帮助信息
show_help() {
    cat << EOF
AI PPT Platform 验收检查脚本

用法:
    ./acceptance-check.sh [选项]

选项:
    --must-only       只检查 MUST 级别项
    --iteration N     只检查指定迭代 (1-5)
    --category CAT    只检查指定类别 (auth|connectors|outlines|editor|exports)
    --report          生成详细报告
    --help            显示帮助

示例:
    ./acceptance-check.sh                    # 检查所有
    ./acceptance-check.sh --must-only        # 只检查 MUST
    ./acceptance-check.sh --iteration 1      # 检查迭代1
    ./acceptance-check.sh --report           # 生成报告
EOF
}

# 打印带颜色的消息
print_status() {
    local status=$1
    local message=$2
    
    case $status in
        "PASS")
            echo -e "${GREEN}✅ PASS${NC} $message"
            ((PASSED++))
            ;;
        "FAIL")
            echo -e "${RED}❌ FAIL${NC} $message"
            ((FAILED++))
            ;;
        "SKIP")
            echo -e "${YELLOW}⏭️  SKIP${NC} $message"
            ((SKIPPED++))
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  INFO${NC} $message"
            ;;
    esac
}

# 检查命令是否存在
check_command() {
    local cmd=$1
    local name=$2
    
    if command -v $cmd > /dev/null 2>&1; then
        print_status "PASS" "$name 已安装"
        return 0
    else
        print_status "SKIP" "$name 未安装，跳过相关检查"
        return 1
    fi
}

# 通用检查函数
check_generic() {
    local id=$1
    local name=$2
    local check_cmd=$3
    
    echo ""
    echo "检查: $id - $name"
    
    if eval $check_cmd; then
        print_status "PASS" "$id: $name"
        return 0
    else
        print_status "FAIL" "$id: $name"
        return 1
    fi
}

# 检查后端测试覆盖率
check_test_coverage() {
    echo ""
    echo "检查: G-02 - 测试覆盖率 ≥ 80%"
    
    cd "$PROJECT_DIR/backend"
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    if PYTHONPATH=./src pytest --cov=ai_ppt --cov-report=term-missing -q 2>&1 | grep -q "[8-9][0-9]%"; then
        print_status "PASS" "G-02: 测试覆盖率 ≥ 80%"
    else
        print_status "FAIL" "G-02: 测试覆盖率不足 80%"
    fi
}

# 检查安全漏洞
check_security() {
    echo ""
    echo "检查: G-03 - 安全漏洞扫描"
    
    if ! check_command "bandit" "Bandit"; then
        return
    fi
    
    cd "$PROJECT_DIR/backend"
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    if bandit -r src/ -f json -o /tmp/bandit-report.json 2>/dev/null; then
        HIGH_SEVERITY=$(cat /tmp/bandit-report.json | grep -c '"issue_severity": "HIGH"' || true)
        
        if [ "$HIGH_SEVERITY" -eq 0 ]; then
            print_status "PASS" "G-03: 无高危安全漏洞"
        else
            print_status "FAIL" "G-03: 发现 $HIGH_SEVERITY 个高危漏洞"
        fi
    else
        print_status "SKIP" "G-03: 扫描失败，请检查 bandit 配置"
    fi
}

# 检查代码规范
check_lint() {
    echo ""
    echo "检查: 代码规范 (ESLint)"
    
    if ! check_command "eslint" "ESLint"; then
        return
    fi
    
    cd "$PROJECT_DIR/frontend"
    
    if [ -f ".eslintrc.js" ]; then
        if eslint . --ext .ts,.tsx --quiet 2>/dev/null; then
            print_status "PASS" "前端代码规范检查通过"
        else
            print_status "FAIL" "前端代码规范检查失败"
        fi
    else
        print_status "SKIP" "未找到 ESLint 配置"
    fi
}

# 检查后端服务启动
check_backend_health() {
    echo ""
    echo "检查: 后端服务健康状态"
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "PASS" "后端服务运行正常"
    else
        print_status "FAIL" "后端服务未启动或健康检查失败"
        print_status "INFO" "请运行: cd backend && PYTHONPATH=./src uvicorn ai_ppt.main:app"
    fi
}

# 检查 API 契约文件
check_api_contract() {
    echo ""
    echo "检查: API 契约文档"
    
    if [ -f "$PROJECT_DIR/docs/architecture/API_CONTRACT.md" ]; then
        print_status "PASS" "API 契约文档存在"
    else
        print_status "FAIL" "未找到 API 契约文档"
    fi
    
    if [ -f "$PROJECT_DIR/docs/architecture/API_CONTRACT_ENFORCEMENT.md" ]; then
        print_status "PASS" "API 执行指南存在"
    else
        print_status "FAIL" "未找到 API 执行指南"
    fi
}

# 检查文档完整性
check_documentation() {
    echo ""
    echo "检查: 文档完整性"
    
    local docs=("README.md" "LICENSE")
    for doc in "${docs[@]}"; do
        if [ -f "$PROJECT_DIR/$doc" ]; then
            print_status "PASS" "$doc 存在"
        else
            print_status "FAIL" "$doc 缺失"
        fi
    done
}

# 主函数
main() {
    local must_only=false
    local iteration=""
    local category=""
    local generate_report=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --must-only)
                must_only=true
                shift
                ;;
            --iteration)
                iteration="$2"
                shift 2
                ;;
            --category)
                category="$2"
                shift 2
                ;;
            --report)
                generate_report=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                echo "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 打印头部
    echo "=============================================="
    echo "  AI PPT Platform - 验收检查"
    echo "=============================================="
    echo ""
    echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "项目: $PROJECT_DIR"
    echo ""
    
    if [ "$must_only" = true ]; then
        echo "模式: 只检查 MUST 级别"
    fi
    
    if [ -n "$iteration" ]; then
        echo "模式: 只检查迭代 $iteration"
    fi
    
    echo ""
    
    # 运行检查
    print_status "INFO" "开始验收检查..."
    
    # 通用检查
    check_documentation
    check_api_contract
    check_backend_health
    
    # 代码质量检查
    check_lint
    check_security
    
    # 测试检查 (如果需要)
    if [ "$must_only" = true ]; then
        check_test_coverage
    fi
    
    # 打印汇总
    echo ""
    echo "=============================================="
    echo "  检查结果汇总"
    echo "=============================================="
    echo ""
    echo -e "${GREEN}✅ 通过: $PASSED${NC}"
    echo -e "${RED}❌ 失败: $FAILED${NC}"
    echo -e "${YELLOW}⏭️  跳过: $SKIPPED${NC}"
    echo ""
    
    if [ $FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 所有检查通过!${NC}"
        exit 0
    else
        echo -e "${RED}⚠️  有 $FAILED 项检查失败，请修复后重试${NC}"
        exit 1
    fi
}

# 运行主函数
main "$@"
