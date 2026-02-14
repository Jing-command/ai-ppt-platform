# 🤖 AI PPT Platform

## 状态
- 迭代1-3: ✅ 完成 (认证/连接器/PPT核心/导出/CI)
- 迭代4: ⏳ 待开始 (大纲编辑器)
- 测试: 83% 覆盖率, 780测试通过
- CI/CD: ✅ 全部通过

## 钩子系统

**on_session_start** - 新会话自动加载项目上下文  
**on_task_complete** - 任务完成自动更新状态  
**on_ci_complete** - CI完成处理结果

**使用**:
```bash
./scripts/hooks/on_session_start.sh
./scripts/hooks/on_task_complete.sh "任务名" success
```

## 下一步
1. 大纲编辑器开发
2. DeepSeek API集成
3. React前端搭建

---
**详细**: HOOKS.md | API_CONTRACT.md | task-queue.md
