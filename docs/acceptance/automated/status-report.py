#!/usr/bin/env python3
"""
验收状态报告生成器

生成可视化的验收状态报告
"""

import json
import sys
from pathlib import Path
from datetime import datetime

STATUS_FILE = Path(__file__).parent.parent / "status" / "status.json"


def load_status():
    """加载状态文件"""
    if not STATUS_FILE.exists():
        print(f"❌ 状态文件不存在: {STATUS_FILE}")
        sys.exit(1)
    
    with open(STATUS_FILE) as f:
        return json.load(f)


def print_progress_bar(percent, width=30):
    """打印进度条"""
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percent:.1f}%"


def generate_report():
    """生成状态报告"""
    data = load_status()
    summary = data["summary"]
    
    print("=" * 60)
    print("  📊 AI PPT Platform - 验收状态报告")
    print("=" * 60)
    print()
    print(f"项目: {data['project']}")
    print(f"版本: {data['version']}")
    print(f"更新时间: {data['last_updated']}")
    print()
    
    # 总体进度
    print("-" * 60)
    print("  📈 总体进度")
    print("-" * 60)
    print()
    
    total = summary["total_items"]
    passed = summary["passed"]
    failed = summary["failed"]
    pending = summary["pending"]
    rate = summary["completion_rate"]
    
    print(f"总计: {print_progress_bar(rate)}")
    print(f"      {passed}/{total} 项已完成")
    print()
    
    # 优先级分布
    print("-" * 60)
    print("  🎯 优先级分布")
    print("-" * 60)
    print()
    
    must_total = summary["must_total"]
    must_passed = data["by_iteration"]["1"]["must_passed"] + \
                  data["by_iteration"]["2"]["must_passed"] + \
                  data["by_iteration"]["3"]["must_passed"] + \
                  data["by_iteration"]["4"]["must_passed"] + \
                  data["by_iteration"]["5"]["must_passed"]
    must_rate = (must_passed / must_total * 100) if must_total > 0 else 0
    
    print(f"🔴 MUST:   {print_progress_bar(must_rate)} ({must_passed}/{must_total})")
    print(f"🟡 SHOULD: 待验收 ({summary['should_total']} 项)")
    print(f"🟢 COULD:  待验收 ({summary['could_total']} 项)")
    print()
    
    # 按迭代统计
    print("-" * 60)
    print("  📦 按迭代统计")
    print("-" * 60)
    print()
    
    for iter_id, iter_data in data["by_iteration"].items():
        name = iter_data["name"]
        must_total_iter = iter_data["must_total"]
        must_passed_iter = iter_data["must_passed"]
        rate = (must_passed_iter / must_total_iter * 100) if must_total_iter > 0 else 0
        
        status_icon = "⬜"
        if iter_data["status"] == "completed":
            status_icon = "✅"
        elif iter_data["status"] == "in_progress":
            status_icon = "🔄"
        
        print(f"迭代 {iter_id}: {name}")
        print(f"  {print_progress_bar(rate)} ({must_passed_iter}/{must_total_iter})")
        print(f"  状态: {status_icon} {iter_data['status']}")
        print()
    
    # 最近通过的项
    print("-" * 60)
    print("  ✅ 最近通过的项")
    print("-" * 60)
    print()
    
    passed_items = [item for item in data["items"] if item["status"] == "passed"]
    
    if passed_items:
        # 按时间倒序，最多显示 5 个
        passed_items.sort(key=lambda x: x.get("tested_at", ""), reverse=True)
        for item in passed_items[:5]:
            print(f"  • {item['id']}: {item['description'][:40]}...")
            if item.get("tested_at"):
                print(f"    测试时间: {item['tested_at']}")
    else:
        print("  暂无通过的项")
    
    print()
    
    # 待测试的 MUST 项
    print("-" * 60)
    print("  ⏳ 待测试的 MUST 项 (Top 5)")
    print("-" * 60)
    print()
    
    pending_must = [item for item in data["items"] 
                    if item["status"] == "pending" and item["priority"] == "MUST"]
    
    if pending_must:
        for item in pending_must[:5]:
            print(f"  ⬜ {item['id']}: {item['description'][:50]}")
    else:
        print("  所有 MUST 项已完成！🎉")
    
    print()
    print("=" * 60)
    
    # 结论
    if must_passed == must_total:
        print("  🎉 所有 MUST 项已通过！项目可以上线！")
    elif must_passed >= must_total * 0.8:
        print(f"  🟡 进度良好 ({must_rate:.0f}%)，继续完成剩余 MUST 项")
    else:
        print(f"  🔴 进度不足 ({must_rate:.0f}%)，需要加快验收速度")
    
    print("=" * 60)


def main():
    """主函数"""
    try:
        generate_report()
    except Exception as e:
        print(f"❌ 生成报告失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
