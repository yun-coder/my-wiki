# 花叔内容创作 Skills 合集 (huashu-skills)

## 是什么
花叔的 Claude Code Skills 合集，包含 21 个经过实战验证的内容创作技能。覆盖从选题、调研、写作、视频创作到发布的全链路工作流。

GitHub 仓库: https://github.com/alchaincyf/huashu-skills

## 怎么用
在 Claude Code 环境中运行以下命令安装特定 Skill：

```bash
/install-skill https://github.com/alchaincyf/huashu-skills/tree/master/{skill名}
```

例如安装视频大纲 Skill：
```bash
/install-skill https://github.com/alchaincyf/huashu-skills/tree/master/huashu-video-outline
```

## 视频生成相关技能与方法论

### 1. huashu-video-outline (视频大纲)
- **功能**: 快速生成 2-3 个视频脚本大纲方案。
- **输出**: 标题、封面建议、时长预估、优劣分析。
- **场景**: 选题阶段快速评估方向，确定最优视频结构。

### 2. huashu-video-check (视频封标检查)
- **功能**: 基于 MrBeast 策略系统化检查标题、封面、开头钩子。
- **方法**: 
  - 5 种强对比标题公式（数量/价格/结果/强弱/时间）。
  - 封面策略选择（人脸表情 vs 结果展示）。
  - 内容承接检查：开头确认 → 中段惊喜 → 结尾兑现。
- **场景**: 视频发布前优化点击率和完播率。

### 3. huashu-douyin-script (抖音爆款脚本)
- **功能**: 从竞品视频到完整脚本的全流程。
- **步骤**: 下载视频 → Gemini AI 分析 → 爆款公式提炼 → 脚本+分镜生成 → 审校。
- **特点**: Gemini 7 维度视频深度分析，内置广审合规检查。
- **场景**: 制作高转化率的短视频脚本，特别是种草和千川素材。

### 4. huashu-script-polish (脚本口语化)
- **功能**: 让视频脚本适合“说”而不是“读”。
- **方法**: 删除书面腔，加入自然口语词，短句化处理，标注停顿和重音。
- **场景**: 录制前的最后一轮打磨，提升视频表现力。

## 其他相关技能

### 写作与审校
- **huashu-proofreading**: 三遍审校降 AI 味，降低检测率至 30% 以下。
- **huashu-article-edit**: 标准化编辑流程，防止会话截断。
- **huashu-material-search**: 从个人素材库检索经历和观点，增加内容“人味”。

### 选题与调研
- **huashu-topic-gen**: 快速输出选题方案，含标题、大纲、工作量评估。
- **huashu-research**: 结构化调研，实时持久化成果。

### 配图与展示
- **huashu-wechat-image**: 微信公众号配图生成。
- **huashu-xhs-image**: 小红书配图生成。
- **huashu-md-to-pdf**: Markdown 转专业 PDF 白皮书。

### 效率工具
- **huashu-agent-swarm**: 多 Agent 并行协作开发。
- **huashu-prompt-save**: Prompt 分类保存与索引。
