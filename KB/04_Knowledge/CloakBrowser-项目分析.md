---
created: 2026-05-11
tags: #项目分析 #浏览器 #反检测 #自动化 #Chromium #Playwright
source: "CloakBrowser"
source_url: https://github.com/CloakHQ/CloakBrowser
author: CloakHQ
publish_date: 2025
---

# CloakBrowser 项目分析

## 摘要
> 源码级 C++ 修改 Chromium 的反检测浏览器，Playwright/Puppeteer 直接替换品，reCAPTCHA v3 达到 0.9 人类分数。

## 项目概况

| 项 | 内容 |
|---|---|
| **仓库** | https://github.com/CloakHQ/CloakBrowser |
| **版本** | v0.3.26（Chromium 146.0.7680.177.4） |
| **语言** | C++（Chromium 源码级修改）+ Python + JavaScript |
| **协议** | MIT（开源免费） |
| **分发** | PyPI / npm / Docker |

## 核心原理

**不是 JS 注入，不是配置补丁，而是从 C++ 源码层面修改 Chromium 二进制文件。**

- 传统方案（playwright-stealth、undetected-chromedriver）通过 JS 运行时注入或配置修补，Chrome 每次更新就可能失效
- CloakBrowser 修改 Chromium C++ 源码后编译，指纹在编译期固化，反检测系统看到的是"正常浏览器"

## 核心能力

### 指纹伪装（57 个 C++ 补丁）
- Canvas、WebGL、Audio、Fonts、GPU、Screen
- WebRTC、网络时序、硬件报告
- CDP 输入行为、WebAuthn、AAC 音频、窗口位置
- `navigator.webdriver = false`、TLS 指纹与真实 Chrome 一致（ja3/ja4/akamai）

### 行为模拟
- `humanize=True` 一键启用
- 贝塞尔曲线鼠标移动 + 真实瞄准点
- 逐字键盘输入（含偶尔打错+自我纠正）
- 加速→巡航→减速的真实滚动模式

### 反检测成绩

| 检测服务 | Stock Playwright | CloakBrowser |
|---|---|---|
| reCAPTCHA v3 | 0.1 (bot) | **0.9 (human)** |
| Cloudflare Turnstile | FAIL | **PASS** |
| FingerprintJS | DETECTED | **PASS** |
| BrowserScan | DETECTED | **NORMAL (4/4)** |
| CDP 检测 | Detected | **Not detected** |
| TLS 指纹 | Mismatch | **Identical to Chrome** |

## API 使用

### Python
```python
# 3 行代码迁移
from cloakbrowser import launch
browser = launch()  # headless, 默认隐身
page = browser.new_page()
page.goto("https://protected-site.com")

# 常用配置
browser = launch(headless=False, proxy="socks5://user:pass@host:port", humanize=True, geoip=True)

# 持久化 profile（cookie/localStorage 跨会话保留）
from cloakbrowser import launch_persistent_context
ctx = launch_persistent_context("./my-profile", headless=False)
```

### JavaScript (Playwright)
```javascript
import { launch } from 'cloakbrowser';
const browser = await launch({ humanize: true, proxy: 'http://proxy:8080' });
```

### JavaScript (Puppeteer)
```javascript
import { launch } from 'cloakbrowser/puppeteer';
const browser = await launch({ headless: true });
```

### Docker
```bash
docker run --rm cloakhq/cloakbrowser cloaktest  # 一键验证
```

### 安装
```bash
pip install cloakbrowser                    # Python
npm install cloakbrowser playwright-core     # Node.js (Playwright)
npm install cloakbrowser puppeteer-core      # Node.js (Puppeteer)
```

## 关键 API

| 函数 | 用途 |
|---|---|
| `launch()` | 基础启动（headless） |
| `launch(headless=False)` | 有头模式 |
| `launch(proxy="...")` | 代理支持（HTTP/SOCKS5） |
| `launch(humanize=True)` | 人类行为模拟 |
| `launch(geoip=True)` | 根据代理 IP 自动设置时区/语言 |
| `launch_context()` | 一站式创建 browser + context |
| `launch_persistent_context()` | 持久化 profile |
| `launch_persistent_context_async()` | 异步版本 |

## 竞品对比

| 特性 | playwright-stealth | undetected-chromedriver | Camoufox | **CloakBrowser** |
|---|---|---|---|---|
| reCAPTCHA v3 | 0.3-0.5 | 0.3-0.7 | 0.7-0.9 | **0.9** |
| Cloudflare | ⚠️ 有时 | ⚠️ 有时 | ✅ | **✅** |
| 补丁层级 | JS 注入 | 配置修补 | C++ (Firefox) | **C++ (Chromium)** |
| 抗 Chrome 更新 | ❌ | ❌ | ✅ | **✅** |
| Playwright API | ✅ | ❌ | ❌ | **✅** |
| 维护状态 | ❌ 停滞 | ❌ 停滞 | ⚠️ 不稳定 | **✅ 活跃** |

## 附加工具

- **CloakBrowser Manager** — 自托管的浏览器 Profile 管理器（Multilogin/GoLogin/AdsPower 免费替代）
  - `docker run -p 8080:8080 -v cloakprofiles:/data cloakhq/cloakbrowser-manager`
  - 创建独立指纹 profile、绑定代理、通过 noVNC 远程操作

## 注意事项
- 二进制体积 ~200MB
- 不解决已出现的 CAPTCHA，目标是让 CAPTCHA 不出现
- 代理需自备，不内置代理轮换
- 每次 Chromium 大版本升级需重新适配 57 个补丁（团队维护）
- Puppeteer 版因 CDP 协议泄漏自动化信号，reCAPTCHA Enterprise 场景建议用 Playwright 版

## 适用场景
- 爬虫/数据采集（需绕过反爬检测）
- RPA 自动化操作（被目标网站拦截时）
- AI Agent 浏览器操控（需要真实浏览器指纹）
- 自动化测试（需真实浏览器环境）

## 与 OpenClaw 集成评估

**无法直接集成**（非 MCP Server），但可通过以下方式间接使用：
1. **exec 调用 Python 脚本** — 编写 CloakBrowser 脚本，通过 `exec` 执行
2. **包装为 MCP Server** — 开发一层 wrapper（成本较高）
3. **独立使用** — 作为独立工具处理需要反检测的浏览器任务

## 相关资源
- [[Chrome DevTools MCP]] — OpenClaw 已集成的官方浏览器调试 MCP
- [[UI-TARS Desktop]] — 字节跳动的多模态 GUI Agent

---
*捕获自: https://github.com/CloakHQ/CloakBrowser*
