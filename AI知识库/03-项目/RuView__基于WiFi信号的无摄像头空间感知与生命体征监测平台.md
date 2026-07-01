# RuView: 基于WiFi信号的无摄像头空间感知与生命体征监测平台

**标签**: WiFi Sensing | CSI | IoT | Home Assistant | Privacy-Preserving | Edge AI

> **摘要**: RuView利用商用WiFi信号和ESP32传感器，通过CSI技术实现穿墙检测、呼吸心率监测及姿态估计，无需摄像头或可穿戴设备。

> 来源: [https://github.com/ruvnet/RuView](https://github.com/ruvnet/RuView)
> 原始分类: AI项目收藏

---

## 项目简介
RuView 是一个将普通 WiFi 信号转化为空间智能感知的平台。它利用信道状态信息（CSI）捕捉人体移动、呼吸甚至静止时对无线电波的扰动，实现非接触式监测。

## 核心功能
- **存在检测**：穿墙检测人员存在、计数及进出追踪。
- **生命体征**：实时监测呼吸率（6-30 BPM）和心率（40-120 BPM），支持睡眠阶段分类和呼吸暂停筛查。
- **活动识别**：识别行走、坐姿、手势及跌倒检测（<200ms响应）。
- **姿态估计**：基于 WiFi CSI 的 17 关键点姿态估计，SOTA 性能超越传统视觉方案。
- **环境映射**：RF指纹识别房间，检测家具移动。

## 硬件与部署
- **硬件需求**：ESP32-S3（约$9）或 ESP32-C6，支持 CSI 捕获。
- **边缘计算**：模型量化至 8KB，可在树莓派或 ESP32 上微秒级运行。
- **集成方式**：
  - 原生支持 Home Assistant (MQTT)。
  - 兼容 Apple Home, Google Home, Amazon Alexa (Matter Bridge)。
  - 提供 Python 库 (`pip install ruview`) 和 Docker 镜像。

## 关键资源
- **预训练模型**: [Hugging Face - ruvnet/wifi-densepose-pretrained](https://huggingface.co/ruvnet/wifi-densepose-pretrained)
- **GitHub 仓库**: [ruvnet/RuView](https://github.com/ruvnet/RuView)
- **安装命令**: `pip install ruview` 或 `docker pull ruvnet/wifi-densepose:latest`