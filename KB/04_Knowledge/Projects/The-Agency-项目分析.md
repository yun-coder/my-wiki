# The Agency 项目分析

> **项目信息**
> - 名称: The Agency (agency-agents)
> - 仓库: https://github.com/msitarzewski/agency-agents
> - 作者: @msitarzewski
> - Stars: **94K+** | Forks: **15K+**
> - 许可: MIT
> - 定位: "A complete AI agency at your fingertips"
> - 语言: Shell + Markdown

---

## 📖 一、项目定位

**The Agency** 是目前 GitHub 上**最庞大的 AI Agent 人格/Skill 集合**——206 个精心设计的 AI 角色，覆盖 15 个业务领域。

> "Born from a Reddit thread and months of iteration"

### 核心特点
- 🎯 **高度专业化**：每个 Agent 都是领域专家，不是通用 prompt 模板
- 🧠 **人格驱动**：独特的性格、沟通风格和思维框架
- 📋 **交付物导向**：代码、流程、可度量成果
- ✅ **生产可用**：经过实战检验的工作流和成功指标

---

## 📊 二、Agent 全景图（206 个）

```
┌────────────────────────────────────────────────────────────────┐
│                    The Agency — 206 AI Agents                   │
├─────────────┬──────────────┬──────────────┬────────────────────┤
│ engineering │ marketing    │ specialized  │ game-development   │
│   29 agents │   30 agents  │   41 agents  │   21 agents        │
├─────────────┼──────────────┼──────────────┼────────────────────┤
│ design      │ sales        │ finance     │ paid-media         │
│   8 agents  │   8 agents   │   5 agents  │   7 agents         │
├─────────────┼──────────────┼──────────────┼────────────────────┤
│ testing     │ support      │ product     │ project-management │
│   8 agents  │   6 agents   │   5 agents  │   6 agents          │
├─────────────┼──────────────┼──────────────┼────────────────────┤
│ academic    │ spatial-comp │ strategy    │                    │
│   5 agents  │   6 agents   │  16 agents  │                    │
└─────────────┴──────────────┴──────────────┴────────────────────┘
```

### Engineering Division（29 个）
| Agent | 专长 |
|-------|------|
| Frontend Developer | React/Vue/Angular, Core Web Vitals |
| Backend Architect | API 设计、数据库架构、可扩展性 |
| Mobile App Builder | iOS/Android, React Native, Flutter |
| AI Engineer | ML 模型、AI 集成 |
| DevOps Automator | CI/CD、云基础设施 |
| Rapid Prototyper | 快速 POC、MVP |
| Senior Developer | Laravel/Livewire |
| Security Engineer | 威胁建模、安全审计 |
| Embedded Firmware | 裸机/RTOS, ESP32/STM32 |
| Incident Response Commander | 事故管理、事后分析 |
| Solidity Smart Contract | EVM 合约、DeFi |
| Code Reviewer | 代码审查 |
| Database Optimizer | 查询优化、Schema 设计 |
| Git Workflow Master | 分支策略、Conventional Commits |
| Software Architect | 系统设计、DDD |
| SRE | SLO、混沌工程 |
| Data Engineer | 数据管道、ETL/ELT |
| **Feishu Integration Developer** | **飞书开放平台** |
| WeChat Mini Program | 微信小程序 |
| CMS Developer | WordPress/Drupal |
| Voice AI Integration | 语音识别管道 |
| + 8 more | ... |

### Marketing Division（30 个）
覆盖 Douyin、Xiaohongshu、Bilibili、WeChat、Weibo、Zhihu、Kuaishou、SEO、ASO、Podcast、Livestream 等中国主流平台。

### Design Division（8 个）
UI/UX/Brand/Whimsy/Inclusive/Image Prompt

### Specialized Division（41 个）
最丰富的分类，涵盖：Agents Orchestrator、MCP Builder、Blockchain Security、Compliance Auditor、Developer Advocate、Legal 系列、Real Estate、Healthcare、Recruitment 等

---

## 🔌 三、OpenClaw 集成（直接支持！）

The Agency **原生支持 OpenClaw**：

```bash
# 生成转换文件
./scripts/convert.sh

# 安装到 OpenClaw
./scripts/install.sh --tool openclaw
# → 复制到 ~/.openclaw/agency-agents/
```

支持的 AI 工具有：Claude Code、GitHub Copilot、Gemini CLI、OpenCode、Cursor、Aider、Windsurf、**OpenClaw**、Qwen、Kimi Code。

---

## 🎨 四、Agent 文件格式

每个 Agent 是一个 `.md` 文件，包含 YAML frontmatter + Markdown body：

```markdown
---
name: Frontend Developer
description: Expert frontend developer specializing in modern web...
color: cyan
emoji: 🖥️
vibe: Builds responsive, accessible web apps with pixel-perfect precision.
---

# Frontend Developer Agent Personality

## 🧠 Your Identity & Memory
- Role / Personality / Memory / Experience

## 🎯 Your Core Mission
- Detailed workflows and deliverables

## 🚨 Critical Rules You Must Follow
- Hard constraints and quality gates

## 📋 Success Metrics
- Measurable outcomes
```

---

## 🎯 五、与 OpenClaw 的协同价值

### 直接可用
T​he Agency 的 206 个 Agent 可直接安装到 OpenClaw：

```bash
cd D:\gitCode\agency-agents
# Windows Git Bash:
bash scripts/convert.sh
bash scripts/install.sh --tool openclaw
```

### 可借鉴的设计
| 元素 | 说明 |
|------|------|
| **Agent 人格模板** | YAML frontmatter + 结构化指令，与 SKILL.md 同构 |
| **领域全覆盖** | Engineering/Design/Marketing/Finance/Legal... |
| **中国本土化** | 飞书/微信/抖音/小红书/B站/知乎/快手/微博/百度 |
| **游戏开发** | Unity/Unreal/Godot/Blender/Roblox 全引擎覆盖 |

### 精选可移植到 OpenClaw Skills 的角色

| Agent | 文件 | 适用场景 |
|-------|------|---------|
| Feishu Integration Developer | `engineering/engineering-feishu-integration-developer.md` | 飞书机器人开发 |
| Software Architect | `engineering/engineering-software-architect.md` | 架构设计（已有类似 skill） |
| Code Reviewer | `engineering/engineering-code-reviewer.md` | 代码审查（已有） |
| Frontend Developer | `engineering/engineering-frontend-developer.md` | Web 开发（已有） |
| Database Optimizer | `engineering/engineering-database-optimizer.md` | 数据库优化 |
| MCP Builder | `specialized/specialized-mcp-builder.md` | MCP Server 开发 |
| Security Engineer | `engineering/engineering-security-engineer.md` | 安全审计 |
| AI Engineer | `engineering/engineering-ai-engineer.md` | AI/ML 开发 |

---

## 📋 六、总结

| 维度 | 评价 |
|------|------|
| **规模** | ⭐⭐⭐⭐⭐ 206 个 Agent，15 个领域，无出其右 |
| **质量** | ⭐⭐⭐⭐⭐ 每个 Agent 有完整人格+流程+交付标准 |
| **中国本土化** | ⭐⭐⭐⭐⭐ 飞书/微信/抖音/小红书/知乎/B站 全覆盖 |
| **OpenClaw 兼容** | ⭐⭐⭐⭐⭐ 原生 `--tool openclaw` 支持 |
| **社区活跃度** | ⭐⭐⭐⭐⭐ 94K Stars, 15K Forks, 活跃 PR |

### 建议操作
1. **安装到 OpenClaw**：`bash scripts/install.sh --tool openclaw`
2. **精选 5-10 个高价值 Agent** 转为 OpenClaw Skills
3. **参考其人格模板** 优化现有 agent 的 SOUL.md 和 AGENTS.md

> 📌 这是一个里程碑级的 AI Agent 社区项目。206 个角色可直接增强 OpenClaw 的 agent 生态。
