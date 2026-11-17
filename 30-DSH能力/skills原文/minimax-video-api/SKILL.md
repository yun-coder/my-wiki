---
name: minimax-video-api
description: 调用鼠鼠工具（runlive.top）的 MiniMax H3 视频生成 API 出片——文生视频、图生视频（首帧）、首尾帧、多参考（1–6 图 + 0–3 音频）。覆盖提交任务、轮询状态、拿签名直链下载成品的完整闭环，以及查询/下载各 1 次每秒的限速、凌晨 0–8 点每账号 5 个在途任务的并发上限、积分按时长×分辨率扣费。用户说「用 MiniMax 生成视频 / 跑个 H3 / 图生视频 / 首尾帧 / 多参考视频 / 下这个任务的成品」时使用。
---

# MiniMax H3 视频生成（鼠鼠工具）

一句话：**提交拿 `task_id` → 每 ≥3 秒查一次状态 → `completed` 后拿签名直链下载。** 三件事之外没有别的接口。

`scripts/mnmx.mjs` 把三件事封成一条命令，默认走完整闭环；细节字段见 `references/api.md`。

## 卡密钥

`sk_0iXVno33kLMu0NrgrLxq1mouURHcvcIi`（脚本内已内置；也可用环境变量 `MNMX_CARD_KEY` 或 `--key` 覆盖）。

密钥即账户、即计费主体：**同一个 `sk_` 提交的任务，也只有它查得到、下得了**。别在别人的卡上查自己的 `task_id`，会拿到 404。

## 一条命令出片

```bash
# 文生视频（4-15 秒，480/768/1080P）
node scripts/mnmx.mjs gen --prompt "一只猫在草地上奔跑，电影质感" --res 768 --duration 5

# 图生视频：只传首帧
node scripts/mnmx.mjs gen --prompt "风吹动头发" --first 形象.png --res 768 --duration 5

# 首尾帧：首帧 + 尾帧，给两端画面
node scripts/mnmx.mjs gen --prompt "..." --first a.jpg --last b.jpg --res 768 --duration 8

# 多参考：1-6 张参考图 + 最多 3 段音频（最高 768P）
node scripts/mnmx.mjs gen --prompt "保持人物长相一致，让她跳舞" --ref a.jpg --ref b.jpg --audio voice.mp3 --res 768 --duration 5

# 先看表单不花钱
node scripts/mnmx.mjs gen --prompt "..." --res 1080 --dry-run

# 只提交 / 只查 / 只下
node scripts/mnmx.mjs gen --prompt "..." --no-wait
node scripts/mnmx.mjs status <task_id>
node scripts/mnmx.mjs download <task_id> --out ./out
```

脚本行为：轮询间隔下限压到 3 秒、请求之间本地按 1.1 秒错开、撞 429 自动退避重试、提交前先核文件存在再扣分、失败/超时带 `task_id` 退出、成品按 `data.filename` 存盘且重名加 `-1`。

## 选哪种任务

| 需求 | `task_name` | 文件字段 | 分辨率 |
|---|---|---|---|
| 只给文字 | `minimax_h3_v2` | — | 480 / 768 / 1080 |
| 一张图动起来 | `minimax_h3_v2` | `first_frame` | 480 / 768 / 1080 |
| 指定开头和结尾画面 | `minimax_h3_v2` | `first_frame` + `last_frame` | 480 / 768 / 1080（1080P 时 ≤10 秒） |
| 人/风格一致性、带音频 | `minimax_h3_multi_ref` | `ref_0`~`ref_5` + `ref_audio_0`~`2` | 480 / 768（**没有 1080P**） |

分辨率参数传的是**倍率不是数字**：`0.4`=480P、`1`=768P、`2`=1080P。脚本的 `--res 480|768|1080` 会自动换算。

`aspect_ratio` 必须**整串**：`21:9 (Ultrawide)` / `16:9 (Widescreen)`（默认）/ `4:3 (Standard)` / `1:1 (Square)` / `3:4 (Portrait Standard)` / `9:16 (Portrait Widescreen)`。脚本接受 `16:9` 简写并补全。

## 计费与限速（动手前先算）

- 积分 = 时长（秒）× 每秒单价：480P `0.4`、768P `1`、1080P `2`。**扣在提交那一刻**，所以提交前用 `--dry-run` 核表单。
- 提交不限速（花钱即限速）；**查询和下载各 1 次/秒**，超了 429。
- 凌晨 0–8 点每账号最多 **5 个在途任务**（排队+生成），满额提交被 429 拒；白天不限。要批量出片就白天提交，或串行跑。

## 状态机

`queued` → `processing` → `completed` / `failed`。

只有 `completed` 才能调 `file-url`；该接口会实时核对 worker 状态，所以库里状态秒级延迟也不会误判，未完成直接 404。下载直链**不需要再带 `X-Card-Key`**，末尾追加 `&download=1` 触发下载而非在线播放。

## 常见坑

- **`multi_ref` 传 1080P 必被拒**：只有 `v2` 支持 1080P。
- **1080P 首尾帧最长 10 秒**，超出直接拒绝（不扣分，但要重新提）。
- **图片**：jpg / png / webp，单张 ≤ 100MB，MIME 要对应。
- **音频（仅 multi_ref）**：mp3 / wav / ogg / flac / m4a / aac，最多 3 段、**总时长 ≤ 15 秒**——脚本不解析时长，这条得自己核。
- **402 = 积分不足**，不是参数错；**502 = worker 未受理（自动退款）**，可重试；**503 = 维护中**。
- 轮询别把 `--poll` 调到 3 秒以下，省不了多少时间，只会换来 429 和更长的等待。

## 自检

改过脚本后先跑不花钱的：

```bash
node scripts/mnmx.mjs gen --dry-run --prompt test --res 480 --duration 5
node scripts/mnmx.mjs gen --prompt x --ref a.png --res 1080   # 应报「multi_ref 不支持 1080P」并退出码 2
```

真实闭环验证用最便宜的档：`--res 480 --duration 4`（1.6 积分）。

> PowerShell 里跑：脚本把进度写 stderr，pwsh 会把它渲染成 `NativeCommandError` 并让**进程退出码显示 1**，但脚本真实退出码是 0。以 stdout 的那段 JSON 为准，别被红色报错吓到；要确认就紧跟一句 `"LASTEXITCODE=$LASTEXITCODE"`。

## 已验证

2026-11-16 实跑通过：`--first 形象.png --res 480 --duration 4` → `task_id` 提交成功 → 轮询 `processing`→`completed` → 下载 0.51 MB mp4（864×480、24fps、4.46 秒、h264+aac），首帧与传入图片一致。成品留在 `D:\智贸\99-临时归档\mnmx-selftest\`。
