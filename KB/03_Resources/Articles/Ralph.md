# Ralph - 自主 AI Agent 循环系统

## 项目概述

**Ralph** 是一个自主 AI Agent 循环系统，通过反复运行 AI 编码工具（Amp 或 Claude Code）直到所有 PRD 条目完成。每个迭代都是全新的实例（干净上下文），通过 git 历史、`progress.txt` 和 `prd.json` 实现记忆持久化。

> 基于 Geoffrey Huntley 的 Ralph 模式开发

**GitHub:** https://github.com/snarktank/ralph  
**Star:** 15.2k ⭐  
**作者:** snarktank

---

## 核心工作流程

```
┌─────────────────────────────────────────────────────────┐
│  1️⃣ 创建 PRD (使用 prd skill)                             │
│      用户描述需求 → AI 追问澄清问题 → 生成 PRD.md          │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  2️⃣ 转换格式 (使用 ralph skill)                            │
│      PRD.md → prd.json (用户故事 JSON 格式)               │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│  3️⃣ 运行 Ralph 循环                                       │
│      for 迭代 in 最大次数:                                │
│        ├── 创建/切换到特性分支                             │
│        ├── 选取最高优先级 passes=false 的故事              │
│        ├── 实现该故事                                      │
│        ├── 运行质量检查 (typecheck/lint/test)            │
│        ├── 提交代码                                        │
│        ├── 更新 prd.json passes=true                      │
│        └── 追加 learnings 到 progress.txt                 │
└────────────────────────┬────────────────────────────────┘
                         ▼
                   完成 ✓ 或 达到最大迭代
```

---

## 核心文件说明

| 文件 | 用途 |
|------|------|
| `ralph.sh` | 主循环脚本，生成新的 AI 实例 |
| `prompt.md` | Amp 工具的 prompt 模板 |
| `CLAUDE.md` | Claude Code 的 prompt 模板 |
| `prd.json` | 用户故事任务列表（含 passes 状态） |
| `progress.txt` | 追加式学习日志 |
| `skills/prd/` | PRD 生成技能 |
| `skills/ralph/` | PRD → prd.json 转换技能 |
| `flowchart/` | 交互式流程图（React Flow） |

---

## 三种安装方式

### 方式一：复制到项目

```bash
mkdir -p scripts/ralph
cp ralph/ralph.sh scripts/ralph/
cp ralph/prompt.md scripts/ralph/    # Amp 用
# 或
cp ralph/CLAUDE.md scripts/ralph/    # Claude Code 用
chmod +x scripts/ralph/ralph.sh
```

### 方式二：全局安装 Skills

```bash
# For Amp
cp -r skills/prd ~/.config/amp/skills/
cp -r skills/ralph ~/.config/amp/skills/

# For Claude Code
cp -r skills/prd ~/.claude/skills/
cp -r skills/ralph ~/.claude/skills/
```

### 方式三：Claude Code Marketplace

```bash
/plugin marketplace add snarktank/ralph
/plugin install ralph-skills@ralph-marketplace
```

---

## 使用命令

```bash
# 使用 Amp（默认）
./scripts/ralph/ralph.sh [最大迭代次数]

# 使用 Claude Code
./scripts/ralph/ralph.sh --tool claude [最大迭代次数]

# 示例
./scripts/ralph/ralph.sh 20          # 最多 20 次迭代
./scripts/ralph/ralph.sh --tool claude  # 使用 Claude Code
```

---

## prd.json 格式

```json
{
  "project": "MyApp",
  "branchName": "ralph/task-priority",
  "description": "Task Priority System - Add priority levels to tasks",
  "userStories": [
    {
      "id": "US-001",
      "title": "Add priority field to database",
      "description": "As a developer, I need to store task priority so it persists across sessions.",
      "acceptanceCriteria": [
        "Add priority column to tasks table: 'high' | 'medium' | 'low' (default 'medium')",
        "Generate and run migration successfully",
        "Typecheck passes"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

---

## 关键设计原则

### 1. 每次迭代 = 全新上下文

每个迭代启动一个**全新的 AI 实例**，记忆仅通过以下方式传递：
- Git 历史（提交记录）
- `progress.txt`（学习笔记）
- `prd.json`（完成状态）

### 2. 故事必须足够小

每个 PRD 条目必须能在**单次上下文窗口**内完成。

✅ 合适的故事：
- 添加数据库列和迁移
- 在现有页面上添加 UI 组件
- 更新服务端 Action 的逻辑
- 在列表中添加筛选下拉框

❌ 太大（需要拆分）：
- "构建整个仪表盘"
- "添加认证功能"
- "重构 API"

### 3. 反馈循环必须存在

- Typecheck 捕获类型错误
- 测试验证行为
- CI 必须保持绿色（断代码会跨迭代累积）

### 4. AGENTS.md 更新至关重要

每次迭代后，Ralph 会更新相关 `AGENTS.md` 文件，记录：
- 发现的模式（"此代码库用 X 做 Y"）
- 踩过的坑（"修改 W 时不要忘记更新 Z"）
- 有用的上下文（"设置面板在组件 X 中"）

### 5. 前端故事必须浏览器验证

包含 UI 变更的故事必须包含 "Verify in browser using dev-browser skill" 作为验收标准。

---

## Agent 任务执行步骤

1. 读取 `prd.json`
2. 读取 `progress.txt`（先看 Codebase Patterns 部分）
3. 确认在正确的分支上（PRD 的 `branchName`）
4. 选取**最高优先级**且 `passes: false` 的故事
5. 实现该故事
6. 运行质量检查
7. 如检查通过，提交所有变更
8. 更新 PRD 中该故事的 `passes: true`
9. 追加进度到 `progress.txt`
10. 检查是否全部完成 → 输出 `<promise>COMPLETE</promise>`

---

## 进度报告格式

```markdown
## [日期时间] - [故事 ID]
- 已实现的内容
- 修改的文件
- **对未来迭代的学习：**
  - 发现的模式
  - 遇到的坑
  - 有用的上下文
---
```

---

## 调试命令

```bash
# 查看哪些故事已完成
cat prd.json | jq '.userStories[] | {id, title, passes}'

# 查看学习日志
cat progress.txt

# 查看 git 历史
git log --oneline -10
```

---

## 与 OpenClaw 产品 Agent 的类比

Ralph 和 OpenClaw 产品 Agent 流程非常相似：

| Ralph | OpenClaw 产品 Agent |
|-------|---------------------|
| prd skill | 产品小王 PRD 输出 |
| ralph skill | 需求分配给团队成员 |
| ralph.sh 循环 | 总控协调流程 |
| prd.json | requirements/ 目录 |
| progress.txt | MEMORY.md |
| Amp/Claude Code | Web 小张 / backend 等 |

---

## 资料链接

- [GitHub 仓库](https://github.com/snarktank/ralph)
- [交互式流程图](https://snarktank.github.io/ralph/)
- [Geoffrey Huntley Ralph 文章](https://ghuntley.com/ralph/)
- [Amp CLI 文档](https://ampcode.com)
- [Claude Code 文档](https://docs.anthropic.com/en/docs/claude-code)
