#!/usr/bin/env python3
"""
更新验收状态

用法:
    python update-status.py --item AUTH-01 --status PASSED
    python update-status.py --item AUTH-01 --status FAILED --reason "密码加密强度不足"
    python update-status.py --batch items.json
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

STATUS_FILE = Path(__file__).parent.parent / "status" / "status.json"


def load_status():
    """加载状态文件"""
    with open(STATUS_FILE) as f:
        return json.load(f)


def save_status(data):
    """保存状态文件"""
    data["last_updated"] = datetime.now().isoformat()
    with open(STATUS_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def update_item(data, item_id, status, reason=None, evidence=None, tester=None):
    """更新单个项的状态"""
    # 查找项
    item = None
    for i in data["items"]:
        if i["id"] == item_id:
            item = i
            break
    
    if not item:
        print(f"❌ 未找到项: {item_id}")
        return False
    
    # 更新状态
    old_status = item["status"]
    item["status"] = status.lower()
    item["tested_at"] = datetime.now().isoformat()
    
    if tester:
        item["tested_by"] = tester
    if reason:
        item["reason"] = reason
    if evidence:
        item["evidence"] = evidence
    
    # 记录历史
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "item_id": item_id,
        "old_status": old_status,
        "new_status": status.lower(),
        "tester": tester
    }
    data["history"].append(history_entry)
    
    # 更新统计
    update_summary(data)
    
    print(f"✅ 已更新 {item_id}: {old_status} → {status.lower()}")
    return True


def update_summary(data):
    """更新汇总统计"""
    items = data["items"]
    
    data["summary"]["passed"] = sum(1 for i in items if i["status"] == "passed")
    data["summary"]["failed"] = sum(1 for i in items if i["status"] == "failed")
    data["summary"]["skipped"] = sum(1 for i in items if i["status"] == "skipped")
    data["summary"]["pending"] = sum(1 for i in items if i["status"] == "pending")
    
    total = data["summary"]["total_items"]
    passed = data["summary"]["passed"]
    data["summary"]["completion_rate"] = round(passed / total * 100, 1) if total > 0 else 0
    
    # 更新迭代统计
    for iter_id, iter_data in data["by_iteration"].items():
        iter_items = [i for i in items if i.get("iteration") == iter_id]
        iter_must = [i for i in iter_items if i["priority"] == "MUST"]
        iter_must_passed = sum(1 for i in iter_must if i["status"] == "passed")
        
        iter_data["must_passed"] = iter_must_passed
        
        if iter_must_passed == 0:
            iter_data["status"] = "pending"
        elif iter_must_passed == len(iter_must):
            iter_data["status"] = "completed"
        else:
            iter_data["status"] = "in_progress"


def main():
    parser = argparse.ArgumentParser(description="更新验收状态")
    parser.add_argument("--item", help="项ID (如 AUTH-01)")
    parser.add_argument("--status", choices=["passed", "failed", "skipped", "pending"],
                       help="新状态")
    parser.add_argument("--reason", help="失败原因 (如果 status=failed)")
    parser.add_argument("--evidence", help="证据链接或路径")
    parser.add_argument("--tester", default="subagent", help="测试人员")
    parser.add_argument("--batch", help="批量更新JSON文件")
    
    args = parser.parse_args()
    
    data = load_status()
    
    if args.batch:
        # 批量更新
        with open(args.batch) as f:
            batch_items = json.load(f)
        
        for item in batch_items:
            update_item(data, item["id"], item["status"], 
                       item.get("reason"), item.get("evidence"), args.tester)
    elif args.item and args.status:
        # 单个更新
        update_item(data, args.item, args.status, 
                   args.reason, args.evidence, args.tester)
    else:
        parser.print_help()
        return
    
    save_status(data)
    print(f"✅ 状态已保存到 {STATUS_FILE}")


if __name__ == "__main__":
    main()
