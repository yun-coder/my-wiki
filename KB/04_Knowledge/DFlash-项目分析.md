---
created: 2026-05-08
tags: #开源项目 #LLM推理加速 #推测解码 #vLLM #SGLang #块扩散
source: "DFlash: Block Diffusion for Flash Speculative Decoding"
source_url: https://github.com/z-lab/dflash
author: Chen Jian, Liang Yesheng, Liu Zhijian (z-lab)
publish_date: 2026-02
---

# DFlash — 块扩散推测解码加速框架

> **项目信息**
> - 仓库: [github.com/z-lab/dflash](https://github.com/z-lab/dflash)
> - 论文: [arXiv:2602.06036](https://arxiv.org/abs/2602.06036)
> - 博客: [z-lab.ai/projects/dflash](https://z-lab.ai/projects/dflash/)
> - 模型: [HuggingFace z-lab 集合](https://huggingface.co/collections/z-lab/dflash)
> - 组织: z-lab
> - 定位: 轻量级块扩散模型，专为推测解码设计

---

## 摘要
> DFlash 用**块扩散（Block Diffusion）** 替代传统逐 token 自回归 draft，实现高效高质量并行起草，已集成到 vLLM 和 SGLang 核心代码，支持 Qwen 全系列、Gemma-4、LLaMA、MiniMax、Kimi 等主流模型。

---

## 📖 一、核心原理

### 推测解码（Speculative Decoding）
```
传统自回归:  target → token1 → token2 → token3 → ... (逐个生成)
推测解码:    draft(并行生成块) → target(一步验证) → 接受/拒绝 → 吞吐翻倍
```

### DFlash 的创新：块扩散
- **不走逐 token 自回归**，而是并行生成一整块 token
- 由 target 模型一步并行验证整个块
- 块级预测比逐 token 准确率更高，接受率更好

---

## 🏗️ 二、技术架构

```
┌─────────────────────────────────────────────────┐
│              DFlash 推测解码流程                  │
├─────────────────────────────────────────────────┤
│                                                   │
│  输入 prompt                                       │
│      ↓                                            │
│  ┌──────────────────────┐                        │
│  │  DFlash Draft Model  │                        │
│  │  (块扩散并行生成)     │                        │
│  │  → 一次生成 N 个 token │                        │
│  └──────────┬───────────┘                        │
│             ↓                                     │
│  ┌──────────────────────┐                        │
│  │  Target Model        │                        │
│  │  (一步并行验证)       │                        │
│  │  → 接受/拒绝每个 token │                        │
│  └──────────┬───────────┘                        │
│             ↓                                     │
│  输出: 验证通过的 token 序列                       │
│                                                   │
│  后端: vLLM / SGLang / Transformers / MLX        │
│                                                   │
└─────────────────────────────────────────────────┘
```

---

## 🔧 三、支持的模型与后端

### 支持的后端

| 后端 | 说明 |
|------|------|
| **vLLM** | v0.20.1+ 核心集成 |
| **SGLang** | 完整支持，可选 schedule overlapping |
| **Transformers** | Qwen3 和 LLaMA-3.1 |
| **MLX** | Apple Silicon (M5 Pro 测试) |

### 支持的 Target 模型（20+）

| 模型系列 | 具体模型 | 状态 |
|----------|---------|------|
| **Qwen3.5** | 4B, 9B, 27B, 35B-A3B, 122B-A10B | ✅ |
| **Qwen3-Coder** | Next, 30B-A3B | ✅ |
| **Qwen3.6** | 27B, 35B-A3B | ✅ |
| **Qwen3** | 4B, 8B (non-thinking) | ✅ |
| **Gemma-4** | 26B-A4B-it, 31B-it | ✅ |
| **LLaMA** | 3.1-8B-Instruct | ✅ |
| **MiniMax** | M2.5 | ✅ |
| **Kimi** | K2.5 | ✅ |
| **gpt-oss** | 20b, 120b | ✅ |
| **DeepSeek** | V4-Flash, V4-Pro | 🔜 |
| **GLM** | 5.1 | 🔜 |

---

## 🚀 四、快速部署

### vLLM（推荐）
```bash
vllm serve Qwen/Qwen3.5-27B \
  --speculative-config '{"method": "dflash", "model": "z-lab/Qwen3.5-27B-DFlash", "num_speculative_tokens": 15}' \
  --attention-backend flash_attn \
  --max-num-batched-tokens 32768
```

### SGLang
```bash
python -m sglang.launch_server \
    --model-path Qwen/Qwen3.5-35B-A3B \
    --speculative-algorithm DFLASH \
    --speculative-draft-model-path z-lab/Qwen3.5-35B-A3B-DFlash \
    --speculative-num-draft-tokens 16
```

### Docker（Gemma4）
```bash
docker run --rm -it --gpus all --ipc=host --shm-size=16g -p 8000:8000 \
  ghcr.io/z-lab/vllm-openai:gemma4-dflash-cu130 \
  google/gemma-4-26B-A4B-it \
  --speculative-config '{"method": "dflash", "model": "z-lab/gemma-4-26B-A4B-it-DFlash", "num_speculative_tokens": 15}'
```

---

## 📊 五、评测基准

- **数据集**: gsm8k, math500, humaneval, mbpp, mt-bench
- **所有后端**共享统一评测脚本
- 支持思考型模型（enable_thinking）

```bash
python -m dflash.benchmark --backend vllm \
    --base-url http://127.0.0.1:8000 --model Qwen/Qwen3.5-27B \
    --dataset gsm8k --num-prompts 128 --concurrency 1 --enable-thinking
```

---

## 💡 六、核心价值

1. **块扩散 > 逐 token** — 并行度更高，接受率更好
2. **生态集成深** — vLLM 核心代码内置，一行配置开启
3. **模型覆盖广** — 20+ 模型 draft 权重已发布
4. **即将开源训练配方** — 可训练任意 LLM 的 DFlash draft
5. **Apple Silicon 支持** — MLX 后端，Mac 也能用

### 与其他推测解码方案对比

| 方案 | Draft 方式 | 生态集成 | 模型覆盖 |
|------|-----------|---------|---------|
| **DFlash** | 块扩散 | vLLM + SGLang + MLX | 20+ 模型 |
| Medusa | 多头并行 | vLLM | 有限 |
| EAGLE | 小模型 draft | vLLM | 有限 |
| Draft-SKD | 蒸馏小模型 | 部分 | 需自训练 |

---

## 📎 相关资源
- [GitHub 仓库](https://github.com/z-lab/dflash)
- [论文](https://arxiv.org/abs/2602.06036)
- [博客](https://z-lab.ai/projects/dflash/)
- [HuggingFace 模型](https://huggingface.co/collections/z-lab/dflash)

## 标签
#开源项目 #LLM推理加速 #推测解码 #vLLM #SGLang #块扩散 #Qwen #Gemma

---
*分析时间: 2026-05-08*
