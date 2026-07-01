# AI_DesktopCat_Qwen3.5Omni：基于Qwen3.5 Omni的桌面机器猫硬件项目

**标签**: Qwen3.5 Omni | ESP32 | 机器人 | 硬件开发 | 语音交互 | DashScope

> **摘要**: 一个结合ESP32硬件与Qwen3.5 Omni模型的桌面AI机器猫项目，集成语音交互、视觉反馈和舵机动作控制。

> 来源: [https://github.com/AI-FanGe/AI_DesktopCat_Qwen3.5Omni](https://github.com/AI-FanGe/AI_DesktopCat_Qwen3.5Omni)
> 原始分类: AI项目收藏

---

## 项目简介
**AI_DesktopCat_Qwen3.5Omni** 是一个开源的AI硬件项目，旨在打造一款具有情感交互能力的桌面机器猫。该项目利用 **Qwen3.5 Omni** 作为核心大模型，实现了语音识别（ASR）、自然语言处理（LLM）和语音合成（TTS）的全链路闭环。

## 核心功能
- **多模态交互**：通过麦克风采集语音，调用阿里云 DashScope API 进行 ASR 和 LLM 推理，并通过扬声器播放回复。
- **视觉反馈**：使用 ST7789 SPI 屏幕显示表情动画和文字状态；通过板载摄像头将画面传输至电脑端网页。
- **肢体动作**：
  - 使用 PCA9685 驱动普通 PWM 舵机控制嘴巴、尾巴、耳朵。
  - 使用 STS3032 总线舵机控制四条腿，支持走路、坐下、跳跃等复杂动作。
- **Web 控制台**：提供基于浏览器的调试界面，实时查看视频流、控制表情和舵机动作。

## 硬件架构
- **主控**：Seeed XIAO ESP32S3 Sense（集成摄像头和麦克风）。
- **显示**：1.83寸 ST7789 SPI LCD。
- **音频**：MAX98357A I2S 功放模块。
- **运动控制**：PCA9685 (PWM舵机) + STS3032 (总线舵机)。

## 软件栈
- **前端/后端**：Python (FastAPI/Flask implied) 后端服务，WebSocket 通信。
- **嵌入式**：C++ (Arduino IDE)，使用 LittleFS 存储表情素材。
- **AI 模型**：Qwen3.5 Omni (通过 DashScope API 接入)。

## 相关链接
- **GitHub 仓库**: https://github.com/AI-FanGe/AI_DesktopCat_Qwen3.5Omni
- **关键代码路径**:
  - ESP32 固件: `upload_facial_expression/integrated/integrated.ino`
  - Python 后端: `upload_facial_expression/integrated/server/app.py`
- **依赖库**: ESP32Servo, Adafruit GFX, ArduinoWebsockets, SCServo 等。

## 注意事项
- 需自备阿里云 DashScope API Key。
- 舵机需独立供电并与 ESP32 共地，防止重启。
- 表情素材需转换为头文件写入 ESP32 的 LittleFS 分区。