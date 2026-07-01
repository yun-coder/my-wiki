# Segment Anything Model (SAM)

**标签**: Computer Vision | Segmentation | Foundation Model | Meta AI

> **摘要**: Meta推出的图像分割基础模型，支持点/框提示生成高质量掩码，具备强大的零样本泛化能力。

> 来源: [https://github.com/facebookresearch/segment-anything](https://github.com/facebookresearch/segment-anything)
> 原始分类: AI项目收藏

---

## Segment Anything Model (SAM)

**简介**
由 Meta AI Research (FAIR) 开发的基础视觉模型，旨在解决可提示的图像分割任务。训练于包含1100万张图像和11亿个掩码的数据集上。

**核心功能**
- **交互式分割**：通过输入点、框或文本提示生成对象掩码。
- **自动掩码生成**：无需提示即可为图像中所有对象生成掩码。
- **零样本性能**：在多种未见过任务中表现强劲。

**使用方式**
1. **安装**:
   ```bash
   pip install git+https://github.com/facebookresearch/segment-anything.git
   ```
2. **代码示例**:
   ```python
   from segment_anything import SamPredictor, sam_model_registry
   sam = sam_model_registry["<model_type>"](checkpoint="<path/to/checkpoint>")
   predictor = SamPredictor(sam)
   predictor.set_image(<your_image>)
   masks, _, _ = predictor.predict(<input_prompts>)
   ```

**模型版本**
- `vit_h`: ViT-Huge (默认)
- `vit_l`: ViT-Large
- `vit_b`: ViT-Base

**相关链接**
- 项目主页: https://github.com/facebookresearch/segment-anything
- SAM 2 (视频版): https://github.com/facebookresearch/segment-anything-2
- 论文: https://arxiv.org/abs/2304.02643
- 数据集 (SA-1B): 需申请访问权限