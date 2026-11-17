# 接口细节（鼠鼠工具 / MiniMax H3）

基址 `https://www.runlive.top/mnmx`，所有请求带 `X-Card-Key: sk_...`。

## POST /api/v1/tasks

multipart/form-data，成功 **202**，返回 `data.task_id`。

| 字段 | 必填 | 说明 |
|---|---|---|
| `task_name` | 是 | `minimax_h3_v2` / `minimax_h3_multi_ref` |
| `prompt` | 是 | 提示词 |
| `resolution` | 否 | `0.4`=480P / `1`=768P / `2`=1080P |
| `duration` | 否 | 4–15 秒 |
| `aspect_ratio` | 否 | 整串，见下 |
| `first_frame` / `last_frame` | 否 | 首帧/尾帧图（仅 v2） |
| `ref_0` ~ `ref_5` | 否 | 参考图 1~6（仅 multi_ref） |
| `ref_audio_0` ~ `ref_audio_2` | 否 | 参考音频 1~3（仅 multi_ref），总时长 ≤ 15 秒 |

`aspect_ratio`：`21:9 (Ultrawide)` / `16:9 (Widescreen)`（默认）/ `4:3 (Standard)` / `1:1 (Square)` / `3:4 (Portrait Standard)` / `9:16 (Portrait Widescreen)`。

每秒单价（积分/秒）：480P `0.4`、768P `1`、1080P `2`。

## GET /api/v1/tasks/{task_id}

`data.status`：`queued` / `processing` / `completed` / `failed`。建议轮询 ≥ 3 秒。

## GET /api/v1/tasks/{task_id}/file-url

仅 `completed` 可用，返回 `data.url`（签名直链，**不需再带头**）与 `data.filename`。`url` 末尾追加 `&download=1` 触发下载。

## 错误码

| 码 | 含义 | 处理 |
|---|---|---|
| 202 | 提交成功 | 记 `task_id` |
| 400 | 参数错误 | 检查字段 |
| 402 | 积分不足 | 充值 |
| 404 | 任务不存在 / 非本人 / 未完成 | 检查参数 |
| 429 | 查询/下载超 1 次/秒，或凌晨闲时并发超 5 个 | 放慢 / 等完成再提 |
| 502 | worker 未受理（自动退款） | 稍后重试 |
| 503 | 系统维护中 | 稍后再试 |

## 请求示例（raw HTTP，不经脚本）

```python
import requests
BASE = "https://www.runlive.top/mnmx"
H = {"X-Card-Key": "sk_..."}

r = requests.post(f"{BASE}/api/v1/tasks", headers=H, data={
    "task_name": "minimax_h3_v2",
    "prompt": "一只猫在草地上奔跑，阳光明媚，电影质感",
    "resolution": "0.4", "duration": "5", "aspect_ratio": "16:9 (Widescreen)",
})
task_id = r.json()["data"]["task_id"]

# 图生视频 / 首尾帧
files = {"first_frame": ("first.jpg", open("first.jpg", "rb"), "image/jpeg")}
# files["last_frame"] = ("last.jpg", open("last.jpg", "rb"), "image/jpeg")

# 多参考
files = {
    "ref_0": ("a.jpg", open("a.jpg", "rb"), "image/jpeg"),
    "ref_1": ("b.jpg", open("b.jpg", "rb"), "image/jpeg"),
    "ref_audio_0": ("voice.mp3", open("voice.mp3", "rb"), "audio/mpeg"),
}
```

提交后查状态、下载成品见 `SKILL.md` 的脚本用法或上面的接口表。
