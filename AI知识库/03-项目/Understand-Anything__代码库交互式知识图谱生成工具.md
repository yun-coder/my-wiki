# Understand-Anything: 代码库交互式知识图谱生成工具

**标签**: knowledge-graph | code-analysis | claude-code | cursor | multi-agent | developer-tools

> **摘要**: 将任意代码库转换为可探索、搜索和问答的交互式知识图谱，支持多平台AI编程助手集成。

> 来源: [https://github.com/Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything)
> 原始分类: AI项目收藏

---

## Understand-Anything

**简介**
一个开源项目，利用多智能体管道分析代码库，构建包含文件、函数、类和依赖关系的知识图谱，并提供交互式仪表盘进行可视化探索。

**核心功能**
- **交互式知识图谱**: 以图形化方式展示代码结构，支持点击节点查看摘要和关系。
- **业务逻辑理解**: 切换至领域视图，映射代码到实际业务流程。
- **知识库分析**: 支持解析Wiki类文档，提取实体和隐含关系。
- **引导式学习**: 自动生成基于依赖关系的架构导览。
- **模糊与语义搜索**: 支持按名称或含义查找代码片段。
- **Diff影响分析**: 预览代码变更对系统其他部分的影响。
- **多语言支持**: 支持中、英、日、韩等多种语言输出。

**工作原理**
- **混合分析**: 结合 Tree-sitter（确定性静态分析）和 LLM（语义理解）。
- **多智能体管道**: 包含项目扫描器、文件分析器、架构分析器、导览构建器等6个专业代理。

**安装与使用**
- **支持平台**: Claude Code, Cursor, VS Code + Copilot, Codex, Gemini CLI, Kiro 等。
- **Claude Code**: `/plugin marketplace add Egonex-AI/Understand-Anything` 然后 `/plugin install understand-anything`
- **一键安装脚本**: `curl -fsSL https://raw.githubusercontent.com/Egonex-AI/Understand-Anything/main/install.sh | bash`
- **常用命令**:
  - `/understand`: 分析整个代码库
  - `/understand-dashboard`: 打开可视化仪表盘
  - `/understand-chat`: 对话式查询代码
  - `/understand-domain`: 提取业务领域知识

**相关链接**
- GitHub: https://github.com/Egonex-AI/Understand-Anything
- Demo: https://understand-anything.com