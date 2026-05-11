# jcode 项目分析

> **项目信息**
> - 名称: jcode (Coding Agent Harness)
> - 仓库: https://github.com/1jehuang/jcode
> - 作者: @1jehuang
> - 语言: Rust
> - Stars: 4.3K+ | Forks: 416+
> - 许可: 开源
> - 定位: "Next generation coding agent harness. Built for multi-session workflows, infinite customizability, and performance."

---

## 📖 一、项目定位

**jcode** 是一个用 **Rust** 构建的**下一代编码 Agent 框架**——定位为 Claude Code / Codex CLI / OpenAI Codex 的替代品，在**性能、内存效率、多 Agent 协作**上全面超越同类。

> "Raise the skill ceiling" — 提升编码 Agent 能力上限

### 性能对比（与主流工具）

**单 Session 内存 (PSS)**：jcode 27.8~167MB vs 竞品 140~387MB

| 工具 | 内存 (1会话) | 内存 (10会话) | 启动时间 |
|------|-------------|-------------|---------|
| **jcode** | **27.8~167 MB** | **117~261 MB** | **14 ms** |
| pi | 144 MB | 833 MB | 591 ms |
| Codex CLI | 140 MB | 335 MB | 883 ms |
| Claude Code | **387 MB** | **2,301 MB** | **3,437 ms** |
| OpenCode | 372 MB | 3,237 MB | 1,036 ms |
| Cursor Agent | 215 MB | 1,632 MB | 1,950 ms |

**关键结论**：
- jcode 单 Session 仅 27-167MB（Claude Code 的 1/5 ~ 1/14）
- 10 个并发 Session 仅 117-261MB（Claude Code 的 1/9 ~ 1/20）
- 启动时间 14ms（Claude Code 的 1/245）

---

## 🏗️ 二、技术架构

### 技术栈

| 层 | 技术 |
|----|------|
| **内核** | Rust（Cargo 构建） |
| **TUI** | 自定义终端渲染引擎（1000+ fps） |
| **渲染** | 自定义 Mermaid 渲染库 (mermaid-rs-renderer, 1800x 加速) |
| **终端** | 自定义终端 Handterm（原生滚动 API） |
| **嵌入** | 本地语义向量嵌入（可选关闭） |
| **存储** | 内存图数据库（记忆系统） |
| **构建** | cargo, sccache, clang+lld |

---

## 🧠 三、核心特性

### 1. 记忆系统（Agent Memory）

**最核心的创新之一**——无需记忆工具，模型自动感知关联记忆。

```
每轮对话 → 语义向量嵌入 → 记忆图检索（余弦相似度）
  → 命中 → 注入对话流
  → 可选：侧边 Agent 验证相关性后注入

记忆提取时机：
  - 语义漂移检测
  - K 轮对话后
  - Session 结束
  - 自动整理（Ambient Mode）
```

| 特性 | 说明 |
|------|------|
| 主动记忆 | 提供显式记忆工具（search/store） |
| 被动记忆 | 自动语义嵌入，每轮隐式检索 |
| Session 搜索 | 传统 RAG 检索历史会话 |
| 记忆整理 | Ambient Mode 自动重组、防过期、防冲突 |

### 2. Swarm 多 Agent 协作

```
jcode serve（持久服务）
  ├── jcode connect（客户端 A）
  ├── jcode connect（客户端 B）
  └── 自动冲突通知 → 文件编辑冲突感知
       ├── Agent A 编辑 file.txt
       ├── Agent B 也打开过 file.txt → 收到变更通知
       └── Agent B 检查 diff，决定是否需要调整
```

| 能力 | 说明 |
|------|------|
| **冲突感知** | 自动检测代码覆盖问题，代理间通知 |
| **Agent 间通信** | DM 单 Agent / 广播全部 / 按仓库筛选 |
| **自主扩缩容** | Agent 可自动 spawn 子 swarm 并行工作 |
| **Headless/Headed** | 支持无头模式和可见模式 |

### 3. 自我开发（Self-Dev）

jcode 可以**修改自己的源代码**：告知 Agent 进入自我开发模式，它会编辑、构建、测试自己的代码，然后重载二进制继续工作。

- 推荐使用前沿模型（GPT-5.5 或最新 Claude）
- 有完善的自我开发基础设施（编辑/构建/测试/重载）

### 4. 技能系统（Skills）

与 OpenClaw 的 SKILL.md 概念类似，但更智能：

- **非启动加载**：Skills 不在启动时全部加载
- **语义注入**：对话嵌入作为语义向量，命中时自动注入技能
- **手动触发**：Agent 可通过 skill 工具主动激活，也可用斜杠命令

### 5. OAuth + 多 Provider 支持

**原生登录**支持 11 种订阅体验，**Provider 集成**涵盖 40+ 服务：

```
原生登录: Claude / OpenAI / Google Gemini / GitHub Copilot /
          Azure OpenAI / Alibaba Cloud / Fireworks / MiniMax /
          LM Studio / Ollama / 自定义 OpenAI 兼容端点

Provider: 40+ 集成：OpenRouter, DeepSeek, HuggingFace, Mistral,
          Perplexity, TogetherAI, Groq, xAI, Zai/Kimi, 302AI...
```

### 6. Mermaid 渲染（1800x 加速）

为了在终端内渲染 Mermaid 图，作者创建了独立的 Rust 渲染库：
- 无需浏览器 / TypeScript 依赖
- 渲染速度比 js 版快 1800 倍
- 支持侧边面板 + 对话流内联渲染

### 7. 浏览器自动化

内置 `browser` 工具，基于 Firefox Agent Bridge：

```
20+ 操作：status / open / snapshot / click / type / fill_form /
          select / scroll / screenshot / eval / press...
```

---

## 📡 四、服务端/客户端架构

```bash
jcode serve          # 启动持久后台服务
jcode connect        # 客户端连接
jcode                # TUI 交互模式
jcode run "..."      # 单次非交互运行
jcode --resume fox   # 按名称恢复会话
```

支持来自不同框架的 Session 恢复：
```
jcode --resume <session-name>
→ 支持恢复: Codex / Claude Code / OpenCode / pi 的会话
```

---

## 🔌 五、与 OpenClaw 的关系

项目明确提及 iOS 应用程序将包含 **OpenClaw 功能**：

> "An iOS application version of jcode is coming soon... OpenClaw like features will be bundled with this iOS application."

### 交叉对比

| 特性 | jcode | OpenClaw |
|------|-------|----------|
| 语言 | Rust | Node.js |
| 定位 | 终端编码 Agent | 通用 AI 助手平台 |
| 记忆系统 | 语义嵌入+图数据库 | 内存搜索 |
| Skills | 语义注入 + 手动 | SKILL.md + extraDirs |
| 多 Agent | Swarm（冲突感知） | sessions_spawn |
| Mermaid | 原生 Rust 渲染（1800x） | 无 |
| 性能 | 极优（14ms 启动, 27MB） | 一般（依赖 Node） |
| iOS 客户端 | 开发中 | 已有 |

---

## 📋 六、总结

| 维度 | 评价 |
|------|------|
| **性能** | ⭐⭐⭐⭐⭐ 行业最低内存占用、最快启动（14ms） |
| **记忆系统** | ⭐⭐⭐⭐⭐ 语义嵌入+图数据库，自动/双模记忆 |
| **Swarm** | ⭐⭐⭐⭐⭐ 原生冲突感知，自主扩缩容 |
| **Provider 支持** | ⭐⭐⭐⭐⭐ 40+ 集成，11 种原生 OAuth |
| **OpenClaw 兼容** | ⭐⭐⭐ 计划集成 iOS 端 OpenClaw 功能 |
| **项目成熟度** | ⭐⭐⭐ v0.9，dev 阶段，功能迭代快 |

### 本地安装方式

```powershell
# Windows PowerShell 一键安装
irm https://raw.githubusercontent.com/1jehuang/jcode/master/scripts/install.ps1 | iex
```

或源码构建（需 Rust）：
```bash
git clone https://github.com/1jehuang/jcode.git
cd jcode
cargo build --release
```

> 📌 这是一个与 OpenClaw 互补的项目——jcode 专注于**终端编码 Agent** 的性能极致优化，可作为 OpenClaw 的 `coding-agent` 子 Agent 使用。
