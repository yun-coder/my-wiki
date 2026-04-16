# Archon 详细配置和使用指南

## 📋 概述

Archon 是一个 AI 编码工作流引擎，用于为 AI 编码代理定义结构化的开发流程。它使用 YAML 配置工作流，让 AI 在预定义的框架内执行任务，而不是随意操作。

## 🎯 核心概念

### Archon-First Rule
AI 代理在执行任何操作前，必须先检查 Archon 的可用性，这强制执行了研究阶段。

### 工作流结构
- **规划 (Planning)**：从需求到实现
- **验证 (Validation)**：代码审查、测试
- **PR 创建 (PR Creation)**：提交变更
- **知识增强 (RAG)**：通过 Archon 的 RAG 功能增强开发

## 🚀 快速开始

### 1. 初始化项目
```bash
archon dev init
```
这将创建 `.archon` 目录和 `archon.yaml` 配置文件。

### 2. 创建角色
在 `archon.yaml` 中添加角色配置：
```yaml
policy:
  roles:
    - name: developer
      description: Normal user access
      permissions: [read, write]
```

### 3. 定义工作流
在 `.archon/workflows/` 目录下创建 YAML 工作流文件。

## 📝 工作流配置示例

### 基本工作流结构
```yaml
name: "代码审查工作流"
description: "自动执行代码审查流程"
steps:
  - name: "代码分析"
    command: "analyze-code"
    description: "分析代码质量和风格"
  
  - name: "生成审查报告"
    command: "generate-review"
    description: "生成详细的审查报告"
  
  - name: "建议修复"
    command: "suggest-fixes"
    description: "提供具体的修复建议"
```

### 完整示例：功能开发工作流
```yaml
name: "功能开发工作流"
description: "从需求到部署的完整开发流程"
steps:
  - name: "需求分析"
    command: "analyze-requirements"
    description: "分析用户需求和功能规格"
  
  - name: "技术设计"
    command: "create-design"
    description: "创建技术设计方案和架构"
  
  - name: "代码实现"
    command: "implement-code"
    description: "编写功能代码"
  
  - name: "代码审查"
    command: "code-review"
    description: "执行代码质量检查"
  
  - name: "测试验证"
    command: "run-tests"
    description: "运行单元测试和集成测试"
  
  - name: "部署上线"
    command: "deploy-feature"
    description: "部署到测试环境"
```

## 📁 目录结构

```
.project/
├── .archon/
│   ├── archon.yaml      # 主配置文件
│   ├── workflows/      # 工作流定义
│   │   ├── code-review.yaml
│   │   └── feature-dev.yaml
│   └── commands/       # 自定义命令
│       └── custom-command.js
└── src/               # 项目源代码
```

## 🔧 常用命令

### 列出所有工作流
```bash
archon workflow list
```

### 运行工作流
```bash
archon workflow run <workflow-name> "任务描述"
```

### 查看工作流详情
```bash
archon workflow show <workflow-name>
```

## 📋 最佳实践

### 1. 工作流设计原则
- **单一职责**：每个工作流专注于一个特定任务
- **清晰步骤**：每个步骤应该有明确的输入和输出
- **错误处理**：包含错误恢复机制
- **日志记录**：记录每个步骤的执行情况

### 2. 权限管理
```yaml
policy:
  roles:
    - name: admin
      description: 管理员权限
      permissions: [all]
    
    - name: developer
      description: 开发者权限
      permissions: [read, write, execute]
    
    - name: viewer
      description: 只读权限
      permissions: [read]
```

### 3. 监控和调试
```bash
# 查看工作流执行日志
archon logs --workflow <name>

# 调试模式运行
archon workflow run <name> "任务" --debug
```

## 🔗 集成示例

### 与 Git 集成
```yaml
workflows:
  git-PR:
    name: "Git PR 创建"
    steps:
      - name: "代码提交"
        command: "git-commit"
      
      - name: "创建 Pull Request"
        command: "create-pr"
        description: "在 GitHub/GitLab 创建 PR"
```

### 与 CI/CD 集成
```yaml
workflows:
  ci-pipeline:
    name: "CI/CD 流水线"
    steps:
      - name: "代码检查"
        command: "code-lint"
      
      - name: "构建打包"
        command: "build-package"
      
      - name: "自动化测试"
        command: "run-tests"
      
      - name: "部署发布"
        command: "deploy-production"
```

## 📈 高级功能

### 1. RAG 能力
Archon 内置 RAG 功能，可以：
- 检索项目文档
- 分析代码历史
- 提供上下文感知的建议

### 2. 多代理协作
```yaml
workflows:
  team-collaboration:
    name: "团队协作工作流"
    steps:
      - name: "任务分配"
        command: "assign-tasks"
        description: "分配任务给不同代理"
      
      - name: "并行开发"
        command: "parallel-development"
        description: "多个代理并行工作"
      
      - name: "代码合并"
        command: "merge-code"
        description: "合并不同代理的代码"
```

## 🛠️ 故障排除

### 常见问题
1. **工作流找不到**：检查 `.archon/workflows/` 目录结构
2. **权限错误**：验证角色权限配置
3. **命令执行失败**：检查命令文件是否存在

### 调试技巧
```bash
# 详细日志
archon --verbose

# 检查配置
archon config validate

# 重置配置
archon dev reset
```

## 📚 学习资源

- [官方文档](https://archon.inc/docs/)
- [示例工作流](https://github.com/coleam00/Archon/tree/main/archon-example-workflow)
- [CLI 文档](https://joseph-fajen.github.io/archon-cli-docs/)

---

*最后更新：2026-04-13*