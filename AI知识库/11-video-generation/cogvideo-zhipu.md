# CogVideo / CogVideoX (智谱)

## 是什么
CogVideo 是由智谱 AI (Zhipu AI) 开源的视频生成模型系列。该系列从最初的 CogVideo 演进至 CogVideoX，目前主流版本包括 CogVideoX-2B、CogVideoX-5B 以及最新的 CogVideoX1.5-5B。

核心特点：
- **多任务支持**：支持文本生成视频 (Text-to-Video)、图像生成视频 (Image-to-Video/I2V) 以及视频延续 (Video Continuation)。
- **高性能架构**：基于 3D Causal VAE 和 Transformer 架构，能够生成高质量、连贯的视频片段。
- **开源生态**：提供 SAT 和 Diffusers 两种推理框架支持，并配套有 CogKit 微调框架和 Finetrainers 等第三方高效微调工具。
- **商业化对接**：可通过智谱清言 (QingYing) 或智谱 AI 开放平台 API 体验更大规模的商业模型。

## 怎么用

### 1. 环境准备
推荐使用 Python 环境，安装 PyTorch (建议 2.5.1+) 及 `diffusers` 库。
```bash
pip install torch torchvision
pip install diffusers transformers accelerate
```

### 2. 推理示例 (Diffusers 版)
使用 Hugging Face `diffusers` 库加载模型进行文本生成视频：
```python
from diffusers import CogVideoXPipeline
import torch

pipe = CogVideoXPipeline.from_pretrained("THUDM/CogVideoX1.5-5B", torch_dtype=torch.float16)
pipe.to("cuda")

video = pipe(
    prompt="一只猫在太空中跳跃",
    num_frames=49,
    guidance_scale=6.0,
    num_inference_steps=50
).frames[0]
```

### 3. 微调 (Fine-tuning)
- **官方方式**：使用 [CogKit](https://github.com/THUDM/CogKit) 框架，支持 CogView4 和 CogVideoX 系列的微调与推理。
- **轻量级方式**：使用 [finetrainers](https://github.com/a-r-r-o-w/cogvideox-factory) 或 `cogvideox-factory`，仅需单张 RTX 4090 即可进行 LoRA 微调，支持多分辨率和内存优化。

### 4. 高级功能
- **DDIM Inverse**：支持逆向过程，可用于视频编辑或风格迁移 (CogVideoX-5B/1.5-5B)。
- **LoRA 微调**：更新后的代码支持低显存 LoRA 训练，适合消费级显卡。

## 什么场景

1. **创意视频制作**：根据文本描述快速生成短视频素材，用于广告预览、故事板绘制或社交媒体内容创作。
2. **图像动态化 (I2V)**：将静态图片转化为动态视频，适用于老照片修复、艺术创作增强或电商产品展示。
3. **视频续写与补帧**：基于已有视频片段生成后续动作，或提升视频帧率，用于影视后期制作。
4. **研究与开发**：作为视频生成基座模型，用于探索多模态生成、3D 视觉理解及可控视频合成算法研究。

## 关键资源
- GitHub: [zai-org/CogVideo](https://github.com/zai-org/CogVideo)
- HuggingFace Demo: [CogVideoX-5B](https://huggingface.co/spaces/THUDM/CogVideoX-5B)
- 技术报告: [arXiv:2408.06072](https://arxiv.org/abs/2408.06072)
- 微调文档: [飞书文档](https://zhipu-ai.feishu.cn/wiki/DHCjw1TrJiTyeukfc9RceoSRnCh)
