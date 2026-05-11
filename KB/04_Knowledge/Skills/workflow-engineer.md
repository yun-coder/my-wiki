---
name: workflow-engineer
description: AI 驱动的开发工作流工程师。基于 Archon 理念，用 YAML 定义标准化开发流程，实现从需求到交付的确定性执行。适用于复杂任务拆分、多代理协作、质量门禁验证。
triggers:
  - 复杂开发任务需要标准化流程时
  - 需要多代理并行/串行执行时
  - 需要质量门禁和验收标准时
  - 团队需要统一开发流程时
  - 用户提到"工作流"、"流程"、"步骤"时
---

# Workflow Engineer - AI 开发工作流引擎

> 灵感来源: Archon (coleam00/Archon)
> 核心理念: 用 YAML 定义开发流程，AI 在结构内即兴发挥

## 核心概念

### 工作流 vs 任务

| 维度 | 单任务 | 工作流 |
|------|--------|--------|
| 规模 | 单次完成 | 多步骤串联/并联 |
| 状态 | 无持久化 | 文件状态追踪 |
| 断点 | 不支持 | 支持从中断恢复 |
| 质量门禁 | 无 | 每步验证 |
| 可重复性 | 低 | 高 |

## YAML 工作流定义

```yaml
name: feature-development
description: 新功能开发标准流程

config:
  agent_type: subagent
  max_retries: 3

steps:
  - id: plan
    name: 需求分析与规划
    agent: subagent
    prompt: "分析以下需求..."
    validation:
      type: manual
      check: "输出包含功能拆解和技术方案"

  - id: backend
    name: 后端开发
    agent: claude-code
    depends_on: [plan]
    prompt: "根据技术方案开发后端..."

  - id: frontend
    name: 前端开发
    agent: claude-code
    depends_on: [plan]
    prompt: "根据技术方案开发前端..."
```

## 验证类型

| 类型 | 说明 |
|------|------|
| none | 无验证，直接进入下一步 |
| auto | 自动验证，检查输出是否包含关键词 |
| manual | 人工确认，暂停等待用户确认 |

## 整合关系

```
workflow-engineer (工作流编排)
    │
    ├── 调用 → fullstack-development (开发规范)
    ├── 调用 → subagent-driven-development (子代理驱动)
    ├── 调用 → ralph-loop (长任务循环)
    └── 调用 → verification-before-completion (完成验证)
```
