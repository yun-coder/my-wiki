# DSH 插件与配置

> 这页解决一个问题：**本机 DSH 装了哪些插件、各自负责什么、加装或排查时去哪看。**
> 记录时点：2026-11-17，profile = `desktop`。

## 一、配置在哪

| 位置 | 内容 | 说明 |
|---|---|---|
| `C:\Users\dsh\.dsh\profiles\desktop\package.json` | 插件依赖 + `dsh.profile.bundles` 启用清单 | 加插件 = 加依赖并写进 bundles |
| `C:\Users\dsh\.dsh\profiles\desktop\cordis.yml` / `cordis.patch.yml` | 主配置与插件补丁 | 插件自己的配置项在各自 `cordis.patch.yml` |
| `C:\Users\dsh\.dsh\profiles\desktop\node_modules\` | 已安装插件实体 | `link:` 形式的插件指向本地源码目录 |
| `C:\Users\dsh\.dsh\skills\` | 用户级技能 | 4 个：douyin-teardown、easyframe-h3-video、minimax-video-api、shot-contract |
| `C:\Users\dsh\.dsh\<功能名>\` | 各插件运行时数据 | 如 `video-h3`、`dsh-market`、`sessions`、`storages` |

## 二、已启用插件（16 个 bundle）

| 插件 | 版本 | 作用 | 配置/入口 |
|---|---|---|---|
| `@deepseek-ai/dsh-base` | 运行时内置 | 核心框架、工具、会话 | — |
| `@deepseek-ai/dsh-web-app` | 运行时内置 | Web GUI 外壳 | 浏览器访问 `http://127.0.0.1:58173` |
| `dshmarket` | 1.73.19 | 可视化插件市场，搜索/一键安装 | 设置里的插件市场 |
| `@tt-a1i/archify-dsh` | 1.1.0 | 架构/流程图技能包（纯技能，无 UI） | 技能 `archify` |
| `dsh-guizang-design` | 0.1.4 | 网页 PPT、图文卡片、单页排版、去 AI 味 4 个技能 + 作品库 | 侧栏「歸藏设计」 |
| `dsh-web-search-pro` | 0.2.4 | 多引擎检索 + 缓存 + 页面渲染，`web_call` | 工具 `web_call` / `web_index` |
| `dsh-notify-me` | 1.21.1 | 离开页面也能收到提醒、审批、外部推送 | 设置 → 通知 |
| `@local/dsh-mcp-chrome-devtools` | 1.0.0 | Chrome DevTools MCP（浏览器调试、快照、网络） | MCP server `chrome-devtools` |
| `@local/dsh-mcp-gbrain` | 1.0.0 | 长期记忆 MCP（实体卡、事实、检索） | MCP server `gbrain` |
| `@local/doc-ingest` | 1.0.0 | Word/PPT/PDF → Markdown，供知识库收录 | 工具 `doc_ingest` |
| `@local/shot-video` | 0.1.0 | 分镜 JSON → H3 出片，右侧栏 13 道质量门、选段、预览、保存 | 侧栏「分镜出片」 |
| `@local/video-h3` | 0.1.0 | MiniMax-H3 视频工作台：直连 EasyFrame，五种模式、队列、历史、拼接 | 侧栏「AI 视频」 |
| `dsh-plugin-chatgpt2api` | 0.6.3 | 账号池 + 本地 OpenAI 兼容的图/文 API（生图走本机号池） | 插件配置 |
| `dsh-better-sidebar` | 0.32.1 | 文件树、编辑器、变更、任务、侧聊一列化 | 设置 → Side card |
| `dsh-context` | 0.84.1 | 上下文洞察与管理面板 | `context` 命令 / 面板 |
| `dsh-dream-skin` | 11.16.0 | 主题皮肤（8 套） | 设置 → 外观 |

## 三、自建插件与本地源码

profile 里用 `link:` 引用了三个本地目录，改源码即生效（client 端改动需重新构建并刷新页面）：

| 插件 | 源码目录 | 说明 |
|---|---|---|
| `@local/video-h3` | `D:\智贸\video-h3` | 本机唯一视频工作台；配置在插件自己的 config（apiKey/model/resolution/seconds/aspectRatio/dataDir/ffmpegPath），数据在 `~/.dsh/video-h3` |
| `@local/shot-video` | `C:\Users\dsh\dsh-bundles\shot-video` | 从分镜 JSON 批量出片 |
| `@local/doc-ingest` | `C:\Users\dsh\dsh-bundles\doc-ingest` | 文档批量转 Markdown |

同一目录下还有 `dsh-mcp-chrome-devtools`、`dsh-mcp-gbrain` 两个 MCP 桥。

## 四、加装插件的两种路径

1. **插件市场**：设置 → 插件市场 → 搜索 → 安装。装完立即生效，包会被写进 `package.json`。
2. **手动**：在 profile 的 `package.json` 加依赖（本地插件用 `link:`），跑 `pnpm install`，再把包名写进 `dsh.profile.bundles`。

**版本闸门**：DSH 会校验插件的 `dsh` 兼容范围（`engines.dsh` 或 peer 依赖）。对不上就直接拦下，不要绕过——例如 `oebeliever/dsh-video-gen@0.3.0` 要求核心包 `0.1.0-rc.6`，而当前运行时是 `0.2.2-rc.3`，装不上，绕过后大概率运行时崩溃。

## 五、排查顺序

1. 插件在不在 `package.json` 与 bundles 里？
2. `node_modules` 里有没有实体？（`link:` 的目标目录是否存在）
3. 插件自己的 `cordis.patch.yml` 有没有配置必填项（key、路径）？
4. DSH 日志/插件管理器日志在 `~/.dsh/profiles/desktop/.plugin-manager/logs/`。
5. client 端插件改动后，页面是否需要重新构建与刷新。
6. 权限类问题（Windows 沙箱、文件被拒）先看 [DSH实战要点](DSH实战要点.md)。
