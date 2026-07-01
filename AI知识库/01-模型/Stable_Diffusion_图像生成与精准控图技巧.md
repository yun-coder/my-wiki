# Stable Diffusion 图像生成与精准控图技巧

**标签**: Stable Diffusion | ControlNet | Image Generation | Prompt Engineering

> **摘要**: 介绍利用 Stable Diffusion 进行文生图，结合 ControlNet 和 Negative Prompt 实现精准图像控制的方法。

> 来源: [https://github.com/phodal/understand-prompt](https://github.com/phodal/understand-prompt)
> 原始分类: stable-diffusion

---

## Stable Diffusion 图像生成指南

### 核心流程
1. **基础描述**：使用自然语言描述画面主体、背景、光影等。
2. **关键词优化**：将长句转化为紧凑的关键词组合（如 `women back view`, `flowing dress`）。
3. **负向提示词 (Negative Prompt)**：排除不需要的元素，如 `bad hands`, `worst quality`, `blurry` 等。

### 精准控图技术
- **ControlNet**：通过骨骼绑定、线稿、深度图等约束生成姿态和结构。
- **Inpainting**：对生成图中失真部分（如手部）进行局部重绘修复。
- **模型选择**：使用 Civitai 等平台寻找特定风格模型（如二次元、写实风）。

### 推荐资源
- [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [ControlNet](https://huggingface.co/lllyasviel/ControlNet)
- [Civitai 模型社区](https://civitai.com/)