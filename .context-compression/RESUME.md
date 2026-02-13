# 会话恢复指令

**压缩时间**: 2026-02-13 14:57  
**原会话**: agent:main:main  
**上下文**: 192K/262K (73%) → 压缩后 ~5K

---

## 🚀 快速恢复

在新会话中发送以下消息：

```markdown
请读取以下文件恢复项目上下文：

```bash
cat /root/.openclaw/workspace/ai-ppt-platform/PROJECT_STATE.md
cat /root/.openclaw/workspace/ai-ppt-platform/.context-compression/task-queue.md
cat /root/.openclaw/workspace/ai-ppt-platform/.context-compression/decisions.md
```

然后继续任务：
**Iteration 5: 导出系统** - 子代理 `58fcc93c` 开发中
- PPTX/PDF/图片导出
- Celery异步任务
- 前端导出按钮

请确认已恢复上下文，然后继续任务。
```

---

## 📁 文件清单

| 文件 | 用途 | 大小 |
|------|------|------|
| `PROJECT_STATE.md` | 项目状态 | ~2KB |
| `.context-compression/task-queue.md` | 任务队列 | ~1KB |
| `.context-compression/decisions.md` | 决策记录 | ~1KB |

---

## 🎯 当前状态

- **项目**: AI PPT Platform
- **迭代**: Iteration 5 (导出系统)
- **进度**: 4/5 迭代完成
- **子代理**: 开发中

---

## ⚡ 快捷命令

```bash
# 检查子代理进度
curl -s http://127.0.0.1:8000/health

# 查看服务状态
ps aux | grep -E "uvicorn|next"
```

---

*下次压缩阈值*: 75% (约 196K tokens)
