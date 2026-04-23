---
name: systematic-debugging
description: 系统性调试技能，用于 bug 定位和问题排查
triggers:
  - 遇到 bug、错误、异常行为时
  - 测试失败时
  - 发现性能问题时
  - 任何技术问题需要定位根因时
---

# Systematic Debugging - 系统性调试

## 核心原则

**永远先找根因，再尝试修复。**

## 四个阶段

### Phase 1: Root Cause Investigation
1. 仔细阅读错误信息
2. 一致地复现问题
3. 检查最近的变更
4. 收集多组件系统的证据

### Phase 2: Pattern Analysis
1. 找到类似的working代码
2. 与参考实现对比
3. 识别差异
4. 理解依赖

### Phase 3: Hypothesis and Testing
1. 形成单一假设
2. 最小化测试
3. 验证后再继续
4. 不知道时承认不知道

### Phase 4: Implementation
1. 创建失败的测试用例
2. 实现单一修复
3. 验证修复
4. 3次以上失败时质疑架构

## 铁律

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

如果还没完成第一阶段，不能提出修复方案。
