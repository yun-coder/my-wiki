---
name: ralph-loop
description: Ralph 自主 Agent 循环系统 - 长任务持续执行引擎
triggers:
  - 执行持久化 PRD 任务时
  - 需要长任务持续执行时
  - 需要断点续做功能时
  - 复杂任务需要分多次迭代完成时
---

# Ralph Loop - 长任务执行引擎

## 核心概念

### 状态持久化
- `prd.json` - 任务列表（JSON格式）
- `progress.txt` - 学习日志（追加写入）

### 小任务原则
每个 Story 必须在一次迭代内完成。

## 工作流程

```
1. 初始化 Ralph → ralph:init
2. 转换 PRD → ralph:convert
3. 运行 Ralph 循环 → ralph:run
4. 检查完成状态 → ralph:complete
```

## 停止条件

当所有 Story 的 `passes: true` 时，Ralph 输出 COMPLETE 并停止。

未完成退出：
- 达到 maxIterations
- 用户手动停止
- 连续失败超过阈值

## 与标准 Agent 的区别

| 特性 | 标准 Agent | Ralph Loop |
|------|-----------|------------|
| 任务长度 | 单次回复 | 循环直到完成 |
| 状态管理 | 内存 | 文件持久化 |
| 断点续做 | 不支持 | 支持 |
| 学习积累 | 无 | progress.txt 记录 |
