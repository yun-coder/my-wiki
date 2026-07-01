# SAM 2: 视频分割模型

**标签**: Video Segmentation | Real-time Processing | Transformer

> **摘要**: SAM的扩展版本，支持实时视频分割，采用Transformer架构并引入流式内存机制。

> 来源: [https://github.com/facebookresearch/segment-anything-2](https://github.com/facebookresearch/segment-anything-2)
> 原始分类: AI项目收藏

---

## SAM 2 (Segment Anything Model 2)

**简介**
将SAM扩展至视频领域的基础模型，能够处理图像序列中的实时分割任务。

**核心特性**
- **视频分割**：将单帧图像视为视频序列进行处理。
- **流式内存**：采用Transformer架构结合流式内存机制，实现实时处理。
- **数据引擎**：通过用户交互改进模型和数据，构建了最大的视频分割数据集 SA-V。

**资源链接**
- 代码仓库: https://github.com/facebookresearch/segment-anything-2
- 在线演示: https://sam2.metademolab.com/
- 论文: https://arxiv.org/abs/2408.00714