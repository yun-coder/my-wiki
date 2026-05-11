---
created: 2026-05-08
tags: #开源项目 #Vercel #CodingAgent #Sandbox #Workflow #AI
source: "Open Agents by Vercel Labs"
source_url: https://github.com/vercel-labs/open-agents
author: Vercel Labs
publish_date: 2025
---

# Open Agents — Vercel Labs 开源后台编码 Agent 参考应用

> **项目信息**
> - 仓库: [github.com/vercel-labs/open-agents](https://github.com/vercel-labs/open-agents)
> - 组织: Vercel Labs
> - 许可: MIT
> - 演示: [open-agents.dev](https://open-agents.dev)
> - 定位: 在 Vercel 上构建和运行后台编码 Agent 的开源参考应用
> - 技术栈: Next.js, Bun, Vercel Workflow SDK, Vercel Sandboxes, PostgreSQL, Better Auth

---

## 摘要
> Open Agents 是 Vercel 官方开源的编码 Agent 参考实现，采用**三层架构（Web → Agent Workflow → Sandbox VM）**，核心设计理念是**Agent 与沙箱分离**——Agent 运行在 VM 外部，通过工具与沙箱交互，实现了持久化执行、独立生命周期管理和灵活的技术演进能力。

---

## 📖 一、项目定位

### 一句话定位
**"从 Prompt 到代码变更，不占用你的笔记本电脑"** — 一个完整的后台编码 Agent 参考实现。

### 核心能力
- 💬 聊天驱动的编码 Agent（文件、搜索、Shell、任务、技能、Web 工具）
- 🔄 基于 Workflow SDK 的持久化多步执行，支持流式输出和取消
- 📦 隔离的 Vercel 沙箱，支持快照恢复
- 🔀 沙箱内克隆仓库和分支工作
- 🚀 可选自动提交、推送和创建 PR
- 🔗 通过只读链接共享会话
- 🎤 可选 ElevenLabs 语音输入

---

## 🏗️ 二、核心架构

### 三层架构

```
┌─────────────────────────────────────────────────┐
│                  三层架构                          │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────────────────────────────────────┐    │
│  │  Layer 1: Web App                        │    │
│  │  认证、会话、聊天、流式 UI               │    │
│  │  (Next.js + Better Auth)                 │    │
│  └──────────────────┬───────────────────────┘    │
│                     ↓                             │
│  ┌──────────────────────────────────────────┐    │
│  │  Layer 2: Agent Workflow                 │    │
│  │  持久化工作流执行                         │    │
│  │  (Vercel Workflow SDK)                   │    │
│  │                                          │    │
│  │  ⚠️ Agent 运行在 VM 外部！              │    │
│  │  通过工具与沙箱交互                       │    │
│  └──────────────────┬───────────────────────┘    │
│                     ↓                             │
│  ┌──────────────────────────────────────────┐    │
│  │  Layer 3: Sandbox VM                     │    │
│  │  文件系统、Shell、Git、Dev Server         │    │
│  │  端口: 3000, 5173, 4321, 8000           │    │
│  │  (Vercel Sandboxes)                      │    │
│  └──────────────────────────────────────────┘    │
│                                                   │
└─────────────────────────────────────────────────┘
```

### ⭐ 核心设计决策：Agent ≠ Sandbox

> **Agent 不运行在 VM 内部，而是运行在外部，通过工具（文件读写、搜索、Shell 命令）与沙箱交互。**

这个分离带来的好处：

| 好处 | 说明 |
|------|------|
| **执行持久化** | Agent 不绑定到单个请求生命周期 |
| **沙箱独立生命周期** | 可以独立休眠和恢复 |
| **技术解耦** | 模型/Provider 选择和沙箱实现可以独立演进 |
| **沙箱纯粹** | VM 保持纯执行环境，不承担控制平面职责 |

---

## 📂 三、仓库结构

```
apps/web          Next.js 应用：工作流、认证、聊天 UI
packages/agent    Agent 实现：工具、子 Agent、技能
packages/sandbox  沙箱抽象层 + Vercel Sandbox 集成
packages/shared   共享工具函数
```

### 技术栈
- **前端**: Next.js (App Router)
- **运行时**: Bun
- **工作流引擎**: Vercel Workflow SDK
- **沙箱**: Vercel Sandboxes (快照恢复)
- **数据库**: PostgreSQL (Neon)
- **缓存**: Redis / Vercel KV (可选，回退到内存)
- **认证**: Better Auth (Vercel OAuth + GitHub OAuth)
- **语音**: ElevenLabs (可选)

---

## 🔧 四、运行机制

### 请求流程
```
用户发送 Chat 消息
       ↓
  启动 Workflow Run（非内联执行）
       ↓
  Agent 持久化多步执行
       ↓
  流式输出返回给前端
       ↓
  用户断开后可重新连接恢复
       ↓
  完成后可选: auto-commit → push → create PR
```

### 关键运行时细节
- 聊天请求启动 Workflow Run，而非内联执行 Agent
- 每个 Agent turn 可跨多个持久化 workflow steps
- 活跃 run 可通过重连到现有 workflow 的流来恢复
- 沙箱使用基础快照，暴露 3000/5173/4321/8000 端口，不活动后休眠
- Auto-commit 和 auto-PR 是偏好驱动的功能，非默认开启

---

## 🔐 五、集成与认证

### OAuth 认证
| Provider | 用途 |
|----------|------|
| **Vercel OAuth** | 登录认证 |
| **GitHub App** | 仓库访问、推送、PR 创建（同时作为 OAuth Provider） |

### 环境变量
| 类别 | 变量 | 说明 |
|------|------|------|
| **必需** | `POSTGRES_URL`, `BETTER_AUTH_SECRET` | 最小运行时 |
| **登录** | Vercel OAuth ID/Secret | Vercel 登录 |
| **GitHub** | App ID/Secret/Private Key/Slug/Webhook Secret | 仓库操作 + PR |
| **可选** | `REDIS_URL`, `KV_URL`, `ELEVENLABS_API_KEY` | 缓存和语音 |

---

## 💡 六、核心价值与启示

### 对 Vercel 生态的意义
- **Vercel Workflow SDK 的实战示范** — 持久化 Agent 工作流的最佳实践
- **Vercel Sandbox 的深度集成** — 展示了沙箱快照恢复的完整模式
- **Vercel AI 的"Agent 落地"方案** — 从概念到生产级参考实现

### 值得借鉴的架构决策

```
1. Agent-Sandbox 分离
   → 这是该项目最重要的设计决策
   → 控制平面和数据平面解耦
   → 允许独立扩展和演进

2. Workflow SDK 持久化
   → Agent 不绑定请求生命周期
   → 支持断点续传、流式输出、取消

3. 沙箱快照恢复
   → 基础快照 → 快速启动
   → 休眠 → 恢复 → 节省资源

4. 偏好驱动的自动化
   → auto-commit/PR 是可选功能，非默认
   → 用户掌控自动化边界
```

### 与同类项目对比

| 特性 | Open Agents | Claude Code | Cursor | OpenClaw |
|------|:-----------:|:-----------:|:------:|:--------:|
| 开源 | ✅ | ❌ | ❌ | ✅ |
| 沙箱隔离 | ✅ VM | 本地 | 本地 | 可选 |
| 持久化执行 | ✅ Workflow | ❌ | ❌ | ✅ |
| 多 Provider | ❌ 仅 Vercel | ❌ | ❌ | ✅ |
| 自托管 | ✅ Vercel | ❌ | ❌ | ✅ |
| GitHub 集成 | ✅ PR/分支 | ✅ | ✅ | ✅ |
| 多 Agent | ✅ 子 Agent | ❌ | ❌ | ✅ |

---

## 🔍 七、局限性与思考

### 局限
1. **强绑定 Vercel 生态** — Workflow SDK、Sandboxes 都是 Vercel 专属服务
2. **单一模型 Provider** — 未展示多模型切换能力
3. **沙箱仅限 Vercel** — 不支持自托管沙箱或 Docker
4. **Bun 依赖** — 不是 Node.js 原生

### 延伸思考
- **Agent-Sandbox 分离**是一个通用模式，可以应用到任何 Agent 架构中
- **Workflow SDK 持久化**思路值得在非 Vercel 环境中用 Temporal/Cadence 复现
- **偏好驱动的自动化**（opt-in auto-commit/PR）是好的 UX 设计模式
- 整体思路与 OpenClaw 的 Agent 架构有相似之处，但 Vercel 更偏向 SaaS 化部署

---

## 📎 相关资源
- [GitHub 仓库](https://github.com/vercel-labs/open-agents)
- [在线演示](https://open-agents.dev)
- [Vercel Workflow SDK](https://vercel.com/docs/workflow-sdk)
- [Vercel Sandboxes](https://vercel.com/docs/sandboxes)
- [Better Auth](https://www.better-auth.com/)

## 标签
#开源项目 #Vercel #CodingAgent #Sandbox #Workflow #持久化执行 #Agent架构 #Next.js

---
*分析时间: 2026-05-08*
