# DSH 技能手册

这页解决一件事：**本机 DSH 装了哪些技能、各自能干什么、什么时候该加载哪一个。** 共 18 个技能，外加 `skill` 工具本身（共 19 项）。
技能有两个来源：一是用户目录 `C:\Users\dsh\.dsh\skills\`（本地自建/自装），二是插件包随身携带（如 `node_modules\dsh-guizang-design\skills\`、`@tt-a1i\archify-dsh\skills\`、`dsh-web-search-pro\assets\skills\`）。
触发方式有两种：任务匹配技能描述时自动加载；或直接调用 `skill` 工具按名称加载全文。会话里能看到的只是摘要，未加载前不应照摘要执行。
本页只写 SKILL.md 与目录里可证实的内容，命令、参数、价格均照原文转述。

---

## 技能总表

| 技能 | 类别 | 一句话定位 | 典型触发 |
|---|---|---|---|
| archify | 创作产出 | 十类原生架构图 + 一页解释图，输出可交互单文件 HTML | 「画个架构图 / 时序图 / ER 图 / 做成一页 / 用页面讲」 |
| guizang-page-skill | 创作产出 | Markdown 精排成单页 HTML（杂志风 / 瑞士风），可导 PDF 与长图 | 「把文档排成网页 / 做成页面 / 排版」 |
| guizang-ppt-skill | 创作产出 | 单文件 HTML 横向翻页 PPT，两种风格 + 演讲者视图 | 「网页 PPT / 杂志风 PPT / 瑞士风 PPT / Swiss Style」 |
| guizang-social-card-skill | 创作产出 | 小红书图文、实况照片、公众号封面等社交图集 | 「小红书图文 / 3:4 封面 / 实况照片 / 公众号封面」 |
| easyframe-h3-video | 视频影像 | 本机出片主链路：插件直连 EasyFrame MiniMax-H3 | 「生成视频 / 出个片 / 跑条 H3 / 首尾帧 / 分镜出片」 |
| minimax-video-api | 视频影像 | 鼠鼠工具 runlive.top 的 H3 API：提交→轮询→下载 | 「用 MiniMax 生成视频 / 多参考视频 / 下成品」 |
| shot-contract | 视频影像 | 拆节拍→镜头认领→现场表→锁行提示词→13 道质量门 | 「分镜 / 镜头表 / 切镜 / 多镜连续性 / 人物瞬移」 |
| douyin-teardown | 视频影像 | 抖音爆款拉片：下载→切分镜→转录→结构化报告→复刻分镜 | 「拉片 / 拆解这个视频 / 为什么火 / 爆款复刻」 |
| office | 文档办公 | Office/PDF 读取、渲染、转换、重算；加载后才启用相关工具 | 「渲染 Office / 转格式 / 重算表格」 |
| office-docx | 文档办公 | Word 创建、读取、编辑、校验 | 「做个 Word / 改 docx / 校验文档」 |
| office-pptx | 文档办公 | PowerPoint 创建、读取、编辑、校验 | 「做个 PPT 文件 / 改 pptx」 |
| office-xlsx | 文档办公 | Excel 读取、创建、编辑、校验 | 「做张表 / 改 xlsx / 看公式」 |
| dsh-web-search-pro | 检索浏览器 | `web_call search.run` 证据包搜索 + `read.fetch` 长页续读 | 「查证 / 调研 / 核实 / 读这个链接」 |
| ego-browser | 检索浏览器 | Chromium（ego-lite）浏览器自动化，可复用登录态 | 「打开网页 / 填表 / 截图 / 前端测试」 |
| dsh-doc | DSH 运维 | DSH 自身事实查询 + 插件/工具/技能开发指南 | 「DSH 这个设置怎么配 / 写个插件 / 工具怎么定义」 |
| diagnose-windows-sandbox-acl | DSH 运维 | Windows 沙箱 ACL 拒绝诊断与一次性修复 | 「工作区写不进去 / 明明能读的路径读不了」 |
| skill | DSH 运维 | 按名称加载任意技能全文 | 「加载 xx 技能 / 用 xx 技能做」 |
| humanizer-zh | 文本打磨 | 中文去空话、去模板化，保留事实与作者声音 | 「润色 / 去 AI 味 / 太像模板了」 |
| guizang-voice | 文本打磨 | 个人语气档案的读写与持续学习 | 「学我的语气 / 用我的口吻写 / 建语气档案」 |

---

## 分类详解

### 一、创作产出类

#### archify

- **定位**：把系统、流程、调用链、数据管线、状态、表结构、类关系、树、时间线、耗时画成**可探索的独立 HTML**（深/浅色、动效、图片/SVG/WebM 导出）；也能把一个答案做成一页解释图（explainer）。
- **什么时候用**：要画图、要"做成一页/用页面讲"、要把对比或诊断结果做成有结构的页面；不用于看板。
- **输入与输出**：输入是需求描述、Mermaid、或真实代码仓库证据；原生图写 `candidate.json`，解释图可写 `candidate.archify.md`；输出 `<slug>.html`。每个新需求独立目录 `.archify/<type>-<slug>-<YYYYMMDD-HHMMSS>/`。
- **关键规则与限制**：
  - 类型路由固定十种：`architecture`、`workflow`、`sequence`、`dataflow`、`lifecycle`、`erd`、`class`、`tree`、`timeline`、`waterfall`；不确定时用 `node bin/archify.mjs guide "<scenario>" --json`。
  - 一次 `finalize` 串起 validate、deliver、check、browser-check 四道门：`node bin/archify.mjs finalize <type> <candidate.json> <output.html> --quality showcase --json`。**非零退出码不算成功**，要按失败的 gate 修完再整条重跑。
  - Mermaid 只读拓扑与语义，图要重新按 Archify 的 JSON 写，不机械复制 Mermaid 样式。
  - 不许编日期、金额、规则；缺个人信息就问，不臆造。解释页只在用户要求、或上下文有 `[archify explainer: ...]` 规则行时才做。
  - 更新提示由 receipt 给出（`update.noticeRequired`），不主动安装或升级。
- **前置依赖**：技能包内无需安装；自检 `node bin/archify.mjs doctor` 与 `node bin/archify.mjs demo <output-directory>`。

#### guizang-page-skill

- **定位**：Markdown → 精排单文件 HTML 页面，克制、内容优先。核心分工是"模型做标注判断，脚本做确定性渲染"：原文 → `annotations.json` → `render.mjs` → `output.html`。
- **什么时候用**：文档排版、文章展示、知识笔记可视化、PRD 格式化、读书笔记、双语文档单语渲染。不适合 PPT（用 guizang-ppt-skill）、社交卡片（用 guizang-social-card-skill）、公众号排版（原文明确指出已移除公众号导出，改用 wechat-formatter）。
- **输入与输出**：输入 `.md` + `annotations.json`；输出单文件 HTML，另可由脚本导出 PDF / 长图。
- **关键规则与限制**：
  - 两风格：杂志风（衬线、米白纸色、默认墨水经典）、瑞士风（无衬线、冷灰、单一锚点色）；两模式：忠实（原文全量保留，10–20 条标注）、解释（每千字约 3–5 个解释组件）。
  - `line` 是原文 1-based 行号；行号打空行或类型对不上，渲染器会警告，按警告改。
  - 不要大幅删减用户内容；瑞士风用背景和间距分隔，不加分割线。
  - 单语文档不要设 `meta.lang`（只有双语文档才用语言过滤）。
  - `embed` 的 SVG 必须纯内联，颜色用 `currentColor` / `var(--accent)`，不写死。
  - `hero_image` 只能用照片或视频帧，不能用表格、图表、榜单、文字截图；不确定写 `"auto"`。
  - 只转录看得清的数字，看不清标 `?`，不估读、不编造。
- **前置依赖**：渲染 `node scripts/render.mjs <input.md> <annotations.json> <output.html> --style swiss|magazine`；导出 PDF/长图用 `node scripts/export.mjs`，需要 Chrome + `puppeteer-core`（首次在 skill 目录 `npm install`，`CHROME_PATH` 可指定）；`--embed` 也要先在 skill 目录 `npm install`。

#### guizang-ppt-skill

- **定位**：生成**单文件 HTML** 的横向翻页网页 PPT，两种视觉体系，共享演讲者视图、观众屏同步、讲稿备注、章节幕封、数据大字报、图片网格等能力。
- **什么时候用**：线下分享、行业讲话、发布会/demo day、带个人风格的演讲。不适合大段表格图表叠加、培训课件、多人协作编辑。
- **输入与输出**：输入主题或大纲 + 素材（文档、数据、旧 PPT、截图）；输出 `.../ppt/index.html` 与同级 `images/`。
- **关键规则与限制**：
  - **风格 A 电子杂志 × 电子墨水**（默认）：WebGL 流体背景、衬线标题、暖色；模板 `assets/template.html`，主题见 `references/themes.md`（5 套）。
  - **风格 B 瑞士国际主义**：极细网格点阵、全无衬线、IKB/柠檬黄/柠檬绿/安全橙四选一；模板 `assets/template-swiss.html`，主题见 `references/themes-swiss.md`。
  - 两种风格**不能混用**：类名只在各自模板的 `<style>` 里定义；写 slide 前必须读模板 `<style>` 并核对 layouts 的 Pre-flight 清单。
  - 页数换算：15 分钟≈10 页，30 分钟≈20 页，45 分钟≈25–30 页。
  - 颜色不直接用用户给的 hex：先用预设，用户有品牌色时跑 `scripts/gz-theme.mjs` 生成受约束主题。
  - 正式演讲每页要有稳定 `data-slide-id` 与对应 `SPEAKER_NOTES`（按 ID 存，不用页码/下标）。
  - 启动前先查上游更新（`git fetch` + `rev-list`），有更新先问用户，不自动 pull。
- **前置依赖**：拷贝种子模板即可运行；校验脚本 `scripts/validate-presenter-mode.mjs`（两风格共用）、`scripts/validate-swiss-deck.mjs`（风格 B）；离线动效靠 `assets/motion.min.js`。

#### guizang-social-card-skill

- **定位**：社交图集生产：小红书/Rednote 图文（3:4）、实况照片动卡、实况拼图、公众号封面成对（21:9 + 1:1）、截图型产品帖、文章封面。
- **什么时候用**：要出图集、要 3:4 封面、要实况照片卡、要公众号双封面。不用于整份幻灯片、长视频生成、无版式的纯图片编辑。
- **输入与输出**：输入文章/脚本/截图/产品笔记/字幕/照片/用户视频；输出 PNG 图集（`output/<poster-id>.png` + 配对预览）、实况照片 `.pvt` 包（含 JPG + MOV）。
- **关键规则与限制**：
  - 风格二选一、不混：Editorial Magazine × E-ink（衬线 + 纸墨 + 氛围层）或 Swiss International（Inter 风、严格左对齐网格、单一高饱和锚点色）。主题：杂志 6 套、瑞士 4 套，均用 `data-theme` 指定。
  - 从种子模板起步（`assets/template-editorial-card.html` / `assets/template-swiss-card.html`），不手写空白 HTML。
  - 产物只能放任务文件夹（默认 `local-tests/<slug>/` 或用户指定目录），**不许放在 skill 根目录**。
  - 3:4 卡内容要占画布高度 ≥75%，禁止用空白把内容夹到中段。
  - 不造数据、不造百分比、不造发布细节；不裁脸和关键 UI。
  - 文字压图必须做主体测绘（face/focal 位置）与缩略图可读性检查，每张图 inline 写 `object-position`。
  - 用户完全没图时只问一次 A（自己传）/B（图库）/C（AI 生成），不反复追问。
  - 交付顺序：**先给用户看渲染结果，再问要不要跑自动核查**，不静默跑校验。
  - 实况照片时长：小红书 5s，公众号 3s；首帧必须过静态 3:4 版式检查才渲染 MOV。
- **前置依赖**：skill 根 `npm install`（Playwright 渲染/校验 + subset-font）；渲染 `node scripts/render.mjs <task-dir>`；校验 `node validate-social-deck.mjs <task-dir>`；`.pvt` 打包用 `makelive`。

### 二、视频与影像类

#### easyframe-h3-video

- **定位**：本机出片的**首选链路**——已装自建插件 `@local/video-h3`（侧栏「AI 视频」）直连 EasyFrame 的 MiniMax-H3，不再走团团TV 与本机桥。
- **什么时候用**：任何"生成一段视频"的请求，含文生、首帧、首尾帧、多参考、任务查询、拼接。
- **输入与输出**：
  - `h3_generate_video({ prompt, mode?, seconds?, resolution?, aspectRatio?, firstFrame?, lastFrame?, references? })`；`mode` 取 `t2va`（文生）/ `i2va`（首帧）/ `fl2va`（首尾帧）/ `ref2va`（多参考）；图片参数是本机绝对路径。
  - `h3_video_tasks({ taskId? })` 查任务；`h3_concat_videos({ taskIds })` 拼接。
  - 成品落 `%USERPROFILE%\.dsh\video-h3\videos\`，任务索引 `index.json`。
- **关键规则与限制**：
  - 单条 5–15 秒整数，480p/720p，画幅 16:9、9:16、1:1、4:3、3:4、21:9、9:21、4:5、5:4（同价）；并发 20，排队不计费。
  - 计费（人民币余额，按输出秒数）：`minimax-h3-mini` 480p 约 ¥0.04/秒、720p 约 ¥0.05/秒；`minimax-h3-fast` 约 ¥0.05/秒；`minimax-h3-base` 约 ¥0.07/秒。
  - EasyFrame 有双层内容审查（原文 + AI 优化后），被拒不建任务、不扣费；出图提示别写真人写真类描述。
  - 配置在插件 → AI 视频 → 配置，或 `D:\智贸\video-h3\cordis.patch.yml`（`apiKey / model / resolution / seconds / aspectRatio / promptOptimization / dataDir / ffmpegPath`）。
  - 排查顺序：`curl http://127.0.0.1:18091/model-capabilities`（旧桥）→ 重启桥 → 看 `bridge.log` → 比对常见错误；`insufficient_user_quota` 表示余额不足。
  - 旧桥 `C:\Users\dsh\dsh-bridges\` 已停用、开机自启已移除，仅留兜底，要改桥改 `h3-bridge.mjs`（`D:\智贸\_plugin-check` 里是开发副本，改了不生效）。`oebeliever/dsh-video-gen` 因版本闸门装不上，别再试。
- **前置依赖**：插件 `@local/video-h3` 与其配置好的 key、EasyFrame 余额；拼接需要 `ffmpegPath`。

#### minimax-video-api

- **定位**：直接调鼠鼠工具（runlive.top）的 MiniMax H3 API 出片，覆盖文生、图生（首帧）、首尾帧、多参考（1–6 图 + 0–3 音频），是 `easyframe-h3-video` 之外的另一个可用通道（也是"分镜出片"插件的底座）。
- **什么时候用**：用户点名用 MiniMax / H3 API、要下某个 `task_id` 的成品，或主链路不可用时兜底。
- **输入与输出**：`node scripts/mnmx.mjs gen --prompt "..." [--first a.jpg] [--last b.jpg] [--ref r.jpg] [--audio v.mp3] --res 480|768|1080 --duration N`；提交得 `task_id`，轮询到 `completed` 后拿签名直链下载 mp4。也支持 `status` / `download` / `--no-wait` / `--dry-run`。
- **关键规则与限制**：
  - 积分 = 时长 × 每秒单价，480P `0.4`、768P `1`、1080P `2`，**提交那一刻就扣**，先 `--dry-run` 核表单。
  - 查询与下载各 1 次/秒；凌晨 0–8 点每账号最多 5 个在途任务，满额 429；脚本把轮询下限压到 3 秒并本地错开 1.1 秒。
  - `minimax_h3_multi_ref` **不支持 1080P**；1080P 首尾帧最长 10 秒；音频最多 3 段且总时长 ≤15 秒（脚本不解析时长，自己核）。
  - 状态机 `queued → processing → completed / failed`；只有 `completed` 能调 `file-url`，直链下载不再带卡密，追加 `&download=1`。
  - 密钥即账户：同一张卡提交的任务只有它查得到、下得了；换卡查别人的 `task_id` 会 404。脚本内已内置密钥，也可用 `MNMX_CARD_KEY` 或 `--key` 覆盖（本页不抄录密钥值）。
  - 错误码：402 积分不足、502 worker 未受理（自动退款，可重试）、503 维护中。
  - PowerShell 下进度写 stderr 会把退出码显示成 1，以 stdout JSON 为准。
- **前置依赖**：Node；有效卡密与积分；图片 jpg/png/webp 单张 ≤100MB 且 MIME 对应。

#### shot-contract

- **定位**：不绑定任何视频模型的**结构层**技能——把一段戏变成可下单的镜头：拆节拍 → 镜头认领连续节拍 → 填七格现场表 → 由表生成带锁行的提示词 → 13 道确定性质量门验收。
- **什么时候用**：出分镜/镜头表/切镜/首尾帧提示词；已有生成结果要诊断（人物瞬移、切镜后光变、动作糊、台词对不上口型）；多镜连续性。只在写文案、选音乐、剪辑时不需要。
- **输入与输出**：输入 `storyboard.json`（`params`、`beats`、`scenes[].beats[].shots[]`）；交付物三件一起给——分镜 JSON、现场表、每镜提示词。
- **关键规则与限制**：
  - 认领规则：一个节拍恰好被一个镜头认领、顺序不回退；一镜不跨场，换景必换镜；一镜至少一个动作拍；认领合计 ≈ 镜头时长，一段合计 ≤ 单段上限。
  - 现场表七格（机位侧含景别、画面里有谁、视线落点、唯一动作、别人在干什么、光、最后一帧）；任何一格写"默认/随意/同上/——"等于没写，门会拦。
  - 锁行不手写，用 `node scripts/check.mjs locks <file.json>` 生成后逐字贴入。
  - 13 道门全绿才交付：`node scripts/check.mjs check <file.json>`（失败退出码 1）。`table` 打印 Markdown 现场表，`selftest.mjs` 不调模型不花额度。
  - 默认参数（按模型改，不改规则）：单段上限 15 秒、单镜 2–5 秒、语速 4.5 字/秒、容差 0.15、同框 ≤3 人。
  - 不写任何模型专有语法，不生成图片或视频，不评判画质，也不替代剧本。
- **前置依赖**：脚本零依赖、只读 JSON、不联网、不用随机数和时钟。

#### douyin-teardown

- **定位**：抖音爆款拉片与复刻：回答"3 秒靠什么留住人、靠什么让人看完、靠什么让人转发"，并落成别人能照着复刻的方案。
- **什么时候用**：用户发来抖音链接/文案，或说「拉片」「拆解这个视频」「为什么火」「爆款复刻」。
- **输入与输出**：
  - 抓素材：`node scripts/fetch.mjs "<分享文案或链接>" "<目录>"` → `video.mp4` + `meta.json`；`node scripts/frames.mjs "<video.mp4>" "<目录>"` → `shots.json`、`frames/shot-XX.jpg`、`contact-sheet.jpg`、`audio.wav`。
  - 转写：`python scripts/asr.py "<audio.wav>" "<transcript.json>" --model small|medium`。
  - 产出：`report.md`（基本信息、3 秒钩子、镜头表、节奏曲线、情绪弧、爆款因子归因、复刻方案）、`replicate.json`（复刻分镜）。
- **关键规则与限制**：
  - 必须真的看图：先看联系表建印象，再逐镜看并记三件事（画面主体与景别、屏幕文字/字幕、这一镜在叙事里做什么）。
  - 结论必须有镜号或字幕原文作证据，写不出证据的标"推测"；不凭标题编内容，不拿点赞数当分析。
  - 镜头表的"作用"只能填：钩子 / 铺垫 / 冲突 / 转折 / 证据 / 爽点 / 收尾 / 引导。
  - 画面字幕与 ASR 对不上时以画面字幕为准，并在报告说明。
  - 抓不到就停下来说明卡在哪，不用二手描述冒充拉片；复刻方案要单独提示台词与 BGM 版权。
  - 要送「分镜出片」或 `h3_generate_video` 之前，**先加载 `shot-contract`** 过 13 道门，别绕过门禁生成。
- **前置依赖**：`yt-dlp`（`pip install yt-dlp`）、ffmpeg、faster-whisper（本机已装）。

### 三、文档与办公类

> 本会话另有一个 `doc_ingest` 工具（Word/PPT/PDF 批量转 Markdown 到 `_md` 目录），它属于工具而非技能清单，可与 office 系列配合使用。

#### office

- **定位**：Office 文件与 PDF 的读取、渲染、转换、重算的入口技能；**加载后才启用** `office_render`、`office_convert`、`office_recalculate` 这三个工具。
- **什么时候用**：要在 Office/PDF 上做渲染、格式转换、公式重算时，先加载它再调用上述工具。
- **输入与输出**：见会话工具清单（`office_render` / `office_convert` / `office_recalculate`）。
- **关键规则或限制**：不先加载就调用渲染/转换/重算工具，等于跳过技能前置。
- **原文**：未备份——原文封装在应用内，本机读不到，本页仅按用途描述与本会话工具清单写简介。

#### office-docx

- **定位**：Word 文档（.docx）的创建、读取、编辑、校验。
- **什么时候用**：要交 Word 成品、读现有 docx 内文、做批量修改或结构校验。
- **输入与输出**：会话内的 docx 工具链（读、写、编辑、校验）。
- **原文**：未备份（封装在应用内）。

#### office-pptx

- **定位**：PowerPoint（.pptx）的创建、读取、编辑、校验。
- **什么时候用**：要交 .pptx 成品（与 guizang-ppt-skill 的网页 PPT 不是一回事）、读现有 pptx、改版式或校验。
- **原文**：未备份（封装在应用内）。

#### office-xlsx

- **定位**：Excel 工作簿（.xlsx）的读取、创建、编辑、校验，含数据与公式。
- **什么时候用**：要交表格成品、读现有 xlsx、改数据或公式、做公式重算（配合 `office` 的 `office_recalculate`）。
- **原文**：未备份（封装在应用内）。

### 四、检索与浏览器类

#### dsh-web-search-pro

- **定位**：联网调研的默认入口。用 `web_call search.run` 拿**证据包**（只返回回答所需的段落，比 `web_search` + `web_fetch` 省上下文），用 `read.fetch` 读页并按 `offset` 续读长页。
- **什么时候用**：联网搜索、查证、核实、调研、对比来源、读某个 URL；中文请求也可用英文 query 配中文 task。
- **输入与输出**：
  - 搜：`{"action":"search.run","args":{"query":"...","task":"一句话目标","profile":"docs_code|news_fact|academic|experience|compare|general","needs":"用分号隔开的子问题","constraints":"[{...}]","budget":6000}}`；带 `task`/`profile` 才出证据包，否则只是来源列表。
  - 读：`{"action":"read.fetch","args":{"url":"...","offset":20000}}`；`history.expand` 展开某条 `evidenceId`；`read.contents` / `read.snapshot` / `search.recommend` 按需。
- **关键规则与限制**：
  - 覆盖是启发式的：`gaps` 里有条目或证据包为空，**不等于答案不存在**，要先扩展、抓页或换说法再说"没找到"（`gaps[].reason` 有 `no_candidates` / `no_page_content` / `weak_support` / `budget`）。
  - 引用证据 URL；每条摘录有 `evidenceId`。
  - 来源策略是"选 1–2 个，不是全上"；`engines` 显式指定时优先；平台搜索需用户自己登录。
  - `constraints` 是 `{kind,value,strength}` 数组，kind 有 10 种，`hard` 直接淘汰、`soft` 只偏好。
  - 预算：证据包默认 6000 字符、上限 30000；单页读取上限 20000 字符，`maxChars` 可调。
  - `cache.clear`、`history.delete`、`rules.*`、`sources.install`、`config.*` 会改本机状态，只在用户要求时执行。
  - `shellPage` / `pageClass`（js_shell、login_wall、captcha）说明拿到的不是正文，要跟链接或转交浏览器。
- **前置依赖**：匿名/免费来源可直接用；配了 key 的来源会被优先；`read.snapshot` 与浏览器类平台需要 dsh-browser 插件就绪。

#### ego-browser

- **定位**：Chromium 浏览器自动化（ego-lite）——开网页、填表、点按钮、截图、提取页面数据、登录、复用用户已登录站点，也用于 web app 测试、dogfooding、QA、bug 排查。
- **什么时候用**：需要"真的操作浏览器"时默认读它；静态页面读取仍优先 `dsh-web-search-pro` 的 `read.fetch`。
- **输入与输出**：见会话内浏览器工具清单（导航、快照、点击、填表、截图、控制台与网络等）。
- **原文**：未备份——原文封装在应用内，本机读不到，本页仅按用途描述写简介。

### 五、DSH 自身与运维类

#### dsh-doc

- **定位**：关于 DSH 本身的事实来源：某个功能、设置、插件、agent preset、工具或 Cordis API 在当前安装里怎么工作；同时也是插件、bundle、MCP 连接、agent preset、工具定义与技能的开发/评审/调试、以及插件升级到新版本 DSH 的指南。
- **什么时候用**：问"DSH 里这个怎么配/怎么用"、要写或改插件、要装/启用/排查插件、升级 profile 时。
- **关键规则或限制**：**加载它不授予改文件或改 profile 的权限**，只是知识入口；真正动手仍需按会话权限执行。
- **原文**：未备份（封装在应用内）。

#### diagnose-windows-sandbox-acl

- **定位**：Windows 上 DSH 沙箱 ACL 拒绝的诊断与一次性修复。一条随附命令会检查目标路径及**每一级祖先目录**，并在同一次运行里修好它证实的 ACL 问题。
- **什么时候用**：工作区写入或列目录失败、平时能读的路径突然读不了，且不像预期内的沙箱限制时。
- **关键规则或限制**：**预期内的沙箱拒绝不需要修 ACL**；不要用它去绕过本该被拒绝的访问。
- **原文**：未备份（封装在应用内）。

#### skill（工具本身）

- **定位**：按名称加载技能全文。会话技能目录只给名称与摘要，加载后才拿到完整的规则、脚本与参考文件路径。
- **什么时候用**：任务命中某个技能描述、或用户点名某个技能时，先加载再动手。
- **关键规则或限制**：不加载不照摘要执行；用户直接调用技能时，其内容会以技能块出现在对话里，不必重复加载。本页所有条目的"原文备份"均取自各技能的 SKILL.md。

### 六、文本打磨类

#### humanizer-zh

- **定位**：编辑中文文章、评论、文档里的空话、重复与模板化表达，让文字自然，同时保留事实、确定程度与作者声音。只润色，不判断作者身份，也不保证过 AI 检测器。
- **什么时候用**：已有文本要去 AI 味、去套话、去排比腔。
- **输入与输出**：输入待编辑文本（或文件）；输出默认只给最终改写稿，不附草稿、命中清单或自评分。
- **关键规则与限制**：
  - 优先级：保留信息与确定程度 > 遵守编辑范围与文体 > 匹配作者声音 > 处理具体表达问题。
  - 不新增原文没有的事实、数字、名字、日期、引文、实现细节或性能结论；不把"可能"写成"确定"、相关写成因果、计划写成已完成。
  - 31 条模式分 A–F 六组（铺垫代替陈述、公式化节奏、拔高与借权威、公式化排版、聊天与草稿残留、中文表达补充检查）；**模式是检查线索，不是词语黑名单**，没有问题的段落原样保留。
  - 代码块、行内代码、命令、路径、URL、链接目标、显式 ID、YAML front matter、表格数据与标题层级默认不动。
  - 只在用户要求改文件时写回；只要求审阅时给建议。
- **前置依赖**：无（纯文本编辑）。

#### guizang-voice

- **定位**：个人语气档案——从用户自己写过的文章与对话里的修改意见，学习句式、节奏、常用词、不用的词、标点与称呼习惯，存成本机 Markdown 档案；替用户写字前读它。
- **什么时候用**：要署用户名字的文章、改稿、PPT 讲稿、页面或卡片文案；用户说「学我的语气」「用我的口吻」「建语气档案」，或给出旧文章样本时。
- **输入与输出**：用插件注册的 `guizang_voice` 工具读写——`show`（读档案，没有档案会说明且不算错误）、`note`（追加一条「对话中学到的」）、`save`（整份覆盖）、`collect`（把用户发过的消息整理成学习素材并返回路径）。档案结构七节：节奏与结构、人称与称呼、常用词/不用的词、判断与语气、标点与混排、对话中学到的、原文参照。
- **关键规则与限制**：
  - **不要用 bash 或文件工具直接改**：数据目录在工作区外，沙箱写不进去。
  - 每条特征要能在样本里找到至少两处证据，并摘原文；找不到证据的不写。
  - 成段样本少于 3 篇文章的量时先建，标明"样本少，置信度低"。
  - 和 humanizer-zh 一起用时**以档案为准**：用户自己爱用的表达即使像模板也保留。
  - 档案只在本机，不外发；用户要求删除时直接删文件。
- **前置依赖**：插件注册的 `guizang_voice` 工具。

---

## 选型对照表

| 我想做什么 | 先加载哪个技能 | 备注 |
|---|---|---|
| 画架构、流程、时序、ERD、状态机、时间线 | archify | 真实代码仓库要带 `--repo-root` 证据 |
| 把一个结论做成一页解释图 | archify | 用户要求页面时才做 |
| 把 Markdown 排成好看的网页 / 导 PDF 长图 | guizang-page-skill | 公众号排版不在此列 |
| 做网页版演讲 PPT | guizang-ppt-skill | 要 .pptx 文件用 office-pptx |
| 做小红书图文 / 公众号双封面 / 实况照片 | guizang-social-card-skill | 实况卡先过首帧静态检查 |
| 生成一条视频 | easyframe-h3-video | 主链路，工具 `h3_generate_video` |
| 用 MiniMax H3 API 出片或下任务成品 | minimax-video-api | 兜底 / 指定卡密通道 |
| 写分镜、镜头表、提示词，或诊断镜头不连续 | shot-contract | 不产出图片视频，只管结构 |
| 拆解一条抖音爆款并复刻 | douyin-teardown | 要真出片，接 shot-contract → easyframe |
| 读/渲染/转换 Office 与 PDF | office | 加载后才启用 render/convert/recalculate |
| 生成 Word / Excel / PowerPoint 文件 | office-docx / office-xlsx / office-pptx | 按文件类型选一个 |
| 联网查证、调研、读某个链接 | dsh-web-search-pro | 优先证据包，不用 web_search+web_fetch |
| 要真正操作浏览器（登录、填表、截图、测试） | ego-browser | 静态内容读取仍走 read.fetch |
| 问 DSH 自身功能、写插件/工具/技能 | dsh-doc | 加载不授予改文件权限 |
| Windows 下工作区莫名写不进去 | diagnose-windows-sandbox-acl | 预期内的沙箱拒绝不用修 |
| 中文稿去空话、去模板腔 | humanizer-zh | 只润色，不改事实 |
| 让产出像用户本人写的 | guizang-voice（先 show） | 与 humanizer-zh 同用时以档案为准 |
| 不确定有哪些技能、要看某技能全文 | skill | 按名称加载 |

---

## 维护说明

### 新增技能放哪

| 来源 | 放置位置 | 本机实例 |
|---|---|---|
| 用户级（自建/自装，优先改这里） | `C:\Users\dsh\.dsh\skills\<技能名>\SKILL.md` | douyin-teardown、easyframe-h3-video、minimax-video-api、shot-contract |
| 插件携带（随插件升级，别在包里改） | 插件包内的 skills 目录 | `node_modules\dsh-guizang-design\skills\...`、`...\own-skills\guizang-voice`、`@tt-a1i\archify-dsh\skills\archify`、`dsh-web-search-pro\assets\skills\dsh-web-search-pro` |
| 应用内置（本机读不到原文） | 封装在应用内 | office、office-docx、office-pptx、office-xlsx、dsh-doc、ego-browser、diagnose-windows-sandbox-acl |

- 一个技能 = 一个目录 + 一份 `SKILL.md`；frontmatter 至少要有 `name`（与目录名一致）和 `description`（写清"什么时候用"，触发靠它）。本机 11 份可读原文都是 `name` + `description`，部分另有 `license`、`metadata`、`allowed-tools`。
- 目录内可带 `scripts/`（技能自己的确定性脚本）、`references/`（细则文档）、`assets/`（模板、字体、背景图）、`examples/`（可运行样例）。脚本路径在原文里通常写作相对路径，执行时按技能根目录解析。
- 同名冲突时以实际加载到的内容为准——先 `skill` 加载，别凭记忆。

### 如何备份

1. 建目录 `D:\my-wiki\30-DSH能力\skills原文\<技能名>\`。
2. 复制该技能根目录的 `SKILL.md`。
3. 若有 `references/`，整目录递归复制（`assets/`、`scripts/`、`examples/` 体积大且可随插件重装，本页未备份）。
4. 备份后比对字节数，与源文件一致即可。

本次备份：2026-11-17，11 个技能、62 个文件（11 份 SKILL.md + 51 份 references）。

| 技能 | 备份路径 | references |
|---|---|---|
| archify | [SKILL.md](skills原文/archify/SKILL.md) | 9 份 |
| douyin-teardown | [SKILL.md](skills原文/douyin-teardown/SKILL.md) | 无 |
| dsh-web-search-pro | [SKILL.md](skills原文/dsh-web-search-pro/SKILL.md) | 4 份 |
| easyframe-h3-video | [SKILL.md](skills原文/easyframe-h3-video/SKILL.md) | 无 |
| guizang-page-skill | [SKILL.md](skills原文/guizang-page-skill/SKILL.md) | 4 份 |
| guizang-ppt-skill | [SKILL.md](skills原文/guizang-ppt-skill/SKILL.md) | 12 份 |
| guizang-social-card-skill | [SKILL.md](skills原文/guizang-social-card-skill/SKILL.md) | 17 份 |
| guizang-voice | [SKILL.md](skills原文/guizang-voice/SKILL.md) | 无 |
| humanizer-zh | [SKILL.md](skills原文/humanizer-zh/SKILL.md) | 无 |
| minimax-video-api | [SKILL.md](skills原文/minimax-video-api/SKILL.md) | 1 份 |
| shot-contract | [SKILL.md](skills原文/shot-contract/SKILL.md) | 4 份 |

只有简介、**原文未备份**的 7 项：office、office-docx、office-pptx、office-xlsx、dsh-doc、ego-browser、diagnose-windows-sandbox-acl（原文封装在应用内，本机读不到）。

### 如何验证加载成功

1. 文件层：`SKILL.md` 存在、frontmatter 的 `name` 与目录名一致、`description` 写清触发场景。
2. 会话层：调用 `skill` 工具并传入技能名；返回的技能正文（技能块）出现，即加载成功。
3. 目录层：新会话的技能目录里出现该名称与描述；若没有，说明 DSH 未扫描到该目录或 frontmatter 有问题。
4. 功能层：按原文给的自检命令跑一次（如 archify 的 `doctor`、shot-contract 的 `selftest.mjs`、minimax-video-api 的 `gen --dry-run`、guizang-voice 的 `show`），不花钱、不改产物即可验证链路通。
