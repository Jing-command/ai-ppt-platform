#!/bin/bash
# Quick security scan - Check for security red lines

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${RED}🛡️  Security Red Line Scanner${NC}"
echo ""

PROJECT_DIR="${1:-.}"
cd "$PROJECT_DIR"

VIOLATIONS=0

# Function to report violation
report_violation() {
    echo -e "${RED}❌ SECURITY VIOLATION: $1${NC}"
    echo "   File: $2"
    echo "   Line: $3"
    echo ""
    ((VIOLATIONS++))
}

echo "Scanning for security violations..."
echo ""

# 1. SQL Injection patterns
echo "Checking for SQL injection..."
SQL_INJECTION=$(grep -rn "execute.*f\"" --include="*.py" . 2>/dev/null || true)
if [ -n "$SQL_INJECTION" ]; then
    while IFS= read -r line; do
        file=$(echo "$line" | cut -d: -f1)
        lineno=$(echo "$line" | cut -d: -f2)
        report_violation "Possible SQL injection (f-string in execute)" "$file" "$lineno"
    done <<< "$SQL_INJECTION"
fi

# 2. Command injection patterns
echo "Checking for command injection..."
CMD_INJECTION=$(grep -rn "os\.system\|subprocess\.call.*shell=True" --include="*.py" . 2>/dev/null || true)
if [ -n "$CMD_INJECTION" ]; then
    while IFS= read -r line; do
        file=$(echo "$line" | cut -d: -f1)
        lineno=$(echo "$line" | cut -d: -f2)
        report_violation "Possible command injection" "$file" "$lineno"
    done <<< "$CMD_INJECTION"
fi

# 3. XSS patterns (innerHTML)
echo "Checking for XSS vulnerabilities..."
XSS=$(grep -rn "innerHTML\s*=" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" . 2>/dev/null || true)
if [ -n "$XSS" ]; then
    while IFS= read -r line; do
        file=$(echo "$line" | cut -d: -f1)
        lineno=$(echo "$line" | cut -d: -f2)
        report_violation "XSS vulnerability (innerHTML)" "$file" "$lineno"
    done <<< "$XSS"
fi

# 4. Hardcoded secrets
echo "Checking for hardcoded secrets..."
SECRETS=$(grep -rn "password\s*=\s*[\"']\|secret\s*=\s*[\"']\|key\s*=\s*[\"']" --include="*.py" --include="*.ts" --include="*.js" . 2>/dev/null | grep -v "getenv\|environ" || true)
if [ -n "$SECRETS" ]; then
    while IFS= read -r line; do
        file=$(echo "$line" | cut -d: -f1)
        lineno=$(echo "$line" | cut -d: -f2)
        report_violation "Possible hardcoded secret" "$file" "$lineno"
    done <<< "$SECRETS"
fi

# 5. Path traversal
echo "Checking for path traversal..."
PATH_TRAVERSAL=$(grep -rn "open(.*f\"\|open(.*f'" --include="*.py" . 2>/dev/null || true)
if [ -n "$PATH_TRAVERSAL" ]; then
    while IFS= read -r line; do
        file=$(echo "$line" | cut -d: -f1)
        lineno=$(echo "$line" | cut -d: -f2)
        report_violation "Possible path traversal" "$file" "$lineno"
    done <<< "$PATH_TRAVERSAL"
fi

# Summary
echo ""
if [ $VIOLATIONS -eq 0 ]; then
    echo -e "${GREEN}✅ No security violations found!${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  Found $VIOLATIONS security violation(s)${NC}"
    echo -e "${RED}These MUST be fixed before committing.${NC}"
    echo ""
    exit 1
fi
