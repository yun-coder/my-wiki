---
name: easyframe-h3-video
description: 本机视频生成链路（团团TV → 本机桥 → EasyFrame MiniMax-H3）。用户说「生成视频 / 出个片 / 跑条 H3 / 首尾帧 / 图生视频 / 分镜出片 / 视频拼接」时用本技能：直接调 generate_video 或 generate_video_from_image，模型填 minimax-h3；含桥的路径、开机自启、计费、排查与兜底方案。
---

# 视频生成（本机桥 → EasyFrame MiniMax-H3）

一条链路，别再造轮子：

```
DSH agent / 团团TV 面板
   ↓ 团团TV 按 MiniMax 官方形态发请求
本机桥  http://127.0.0.1:18091   （字段翻译 + 上传转 multipart）
   ↓ EasyFrame /v1/videos
EasyFrame  minimax-h3-{mini|fast|base}，480p/720p，5–15 秒
```

## 怎么用（优先用工作台插件，不要再走团团TV 或本机桥）

本机已装自建插件 **`@local/video-h3`（侧栏「AI 视频」）**，直连 EasyFrame：

- 工具：`h3_generate_video({ prompt, mode?, seconds?, resolution?, aspectRatio?, firstFrame?, lastFrame?, references? })`
  - 文生：`mode: "t2va"`；首帧：`i2va` + `firstFrame`；首尾帧：`fl2va` + `firstFrame` + `lastFrame`；多参考：`ref2va` + `references[]`
  - 图片参数是本机绝对路径；工具会等到完成并返回 `file`
- 查任务：`h3_video_tasks({ taskId? })`；拼接：`h3_concat_videos({ taskIds: [...] })`
- 成品目录：`%USERPROFILE%\.dsh\video-h3\videos\`，任务索引 `index.json`
- 配置（独立配置行）：插件 → AI 视频 → 配置，或 `D:\智贸\video-h3\cordis.patch.yml` 里的 `apiKey / model / resolution / seconds / aspectRatio / promptOptimization / dataDir / ffmpegPath`

**旧链路（已停用，仅留文件兜底）**：本机桥 `C:\Users\dsh\dsh-bridges\`（进程已停、开机自启已移除，需要时手动 `wscript launch.vbs`）；团团TV 插件已卸载。生图走本机号池端点（插件配置 `imageBaseUrl` / `imageKey`），号池依赖 ChatGPT 连通性。

## 关键路径

| 东西 | 位置 |
|---|---|
| 桥（常驻运行的那份） | `C:\Users\dsh\dsh-bridges\h3-bridge.mjs` |
| 启动脚本 / 隐藏启动 | `start-bridge.cmd` / `launch.vbs`（端口守卫 + 崩溃 5 秒重启） |
| 开机自启 | `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\DSH-H3-Bridge.vbs` |
| EasyFrame key | `C:\Users\dsh\dsh-bridges\easyframe.key`（**不要外传**；`D:\智贸\_plugin-check` 里是同内容开发副本） |
| 日志 | `C:\Users\dsh\dsh-bridges\bridge.log`、`console.log` |
| 团团TV 渠道 | 「EasyFrameH3(本机桥)」→ `http://127.0.0.1:18091`，视频模型 id `minimax-h3` |

改桥请改 `C:\Users\dsh\dsh-bridges\h3-bridge.mjs`；`D:\智贸\_plugin-check\h3-bridge.mjs` 只是开发副本，改了不生效。

## 计费（人民币余额，按输出秒数）

| 档位 | 480p | 720p |
|---|---|---|
| minimax-h3-mini | ≈ ¥0.04/秒（5 秒 ¥0.20） | ≈ ¥0.05/秒（¥0.25） |
| minimax-h3-fast | ≈ ¥0.05/秒 | ≈ ¥0.05/秒 |
| minimax-h3-base | ≈ ¥0.07/秒 | ≈ ¥0.07/秒（¥0.35） |

桥默认档位由环境变量 `BRIDGE_MODEL` 决定（当前 `minimax-h3-mini`）；模型 id 里带 `mini` / `fast` / `base` 会覆盖。

## 排查顺序

1. 桥是否活着：`curl http://127.0.0.1:18091/model-capabilities`（200 = 正常）。
2. 重启桥：`wscript "C:\Users\dsh\dsh-bridges\launch.vbs"`（先确认 18091 没被别的进程占用）。
3. 看日志：`bridge.log` 里 `submit ...` / `poll ...` / `error ...` 三行就能定位。
4. 常见错误：
   - `images item url must be a valid http(s) URL` → 图片没走 multipart（桥的翻译层坏了）。
   - `references must be a JSON array` → 传的 JSON 带 BOM 或不是数组。
   - `insufficient_user_quota, 剩余额度: ¥0.000000` → EasyFrame 余额没了，去 `https://minimax.api.easyframe.cn/` 充值。
   - `fetch failed` → 单次网络抖动，桥会重试；连续出现查代理。
   - 模型 `model_temporarily_unavailable` → `pro` 档未开放，用 mini/fast/base。

## 边界与兜底

- EasyFrame 有**双层内容审查**（原文 + AI 优化后），被拒不建任务也不扣费；出图提示性别写真人写真类描述。
- 单条 5–15 秒整数，480p/720p，画幅 16:9 / 9:16 / 1:1 / 4:3 / 3:4 / 21:9 / 9:21 / 4:5 / 5:4（同价）。
- 并发 20；排队不计费。
- **兜底**：「分镜出片」插件（`@local/shot-video`，runlive 鼠鼠 H3，`/api/v1/tasks` + `X-Card-Key`）仍在，用户暂时保留不删；`oebeliever/dsh-video-gen` 因版本闸门（要 0.1.0-rc.6，运行时 0.2.2-rc.3）装不了，别再试。
