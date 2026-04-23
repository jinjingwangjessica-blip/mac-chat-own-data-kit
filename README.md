<h1 align="center">mac-chat-own-data-kit</h1>

<p align="center">
  <b>在 macOS 上把你自己的聊天记录完整、干净地导出成结构化文件</b><br/>
  <b>Export your own chat archive from macOS IM apps — cleanly, fully, programmatically.</b>
</p>

<p align="center">
  纯 Python 解密 · 中文 OCR · Claude Code skill<br/>
  Pure-Python decryption · Chinese-optimized OCR · Claude Code skill
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT"></a>
  <img src="https://img.shields.io/badge/platform-macOS%2014%2B-lightgrey" alt="macOS 14+">
  <img src="https://img.shields.io/badge/arch-Apple%20Silicon-black" alt="Apple Silicon">
  <img src="https://img.shields.io/badge/python-3.10%2B-green" alt="Python 3.10+">
  <a href="https://anthropic.com/claude-code"><img src="https://img.shields.io/badge/Claude%20Code-skill-orange" alt="Claude Code skill"></a>
</p>

<p align="center">
  <a href="#-中文说明">🇨🇳 中文说明</a> · <a href="#-english">🇺🇸 English</a>
</p>

---

## 🇨🇳 中文说明

> **你的聊天记录是你自己的记忆。** 这个工具包帮你在下一次客户端更新
> 之前把它们完整搬走。

### 为什么需要

**2026 年 1 月那次大规模下架**之后，macOS 社区的聊天导出工具处境尴尬——
Windows-only 的 fork、停在老版本的项目、装不上新 macOS 的原生依赖、
遇到中文就悄无声息地糊掉。

这个工具是一位想把孩子第一年成长记录归档的家长写的，把关键的
"脏活累活" 做对：

- ✅ **纯 Python SQLCipher v4 解密器**——不用 `brew install sqlcipher`，
  不会遇到原生编译错误
- ✅ **正确处理 zstd 压缩的消息体**——其他工具会默默丢掉
- ✅ **中文 Apple Vision OCR**——用 PyObjC 直调系统 API，绕开
  `ocrmac` 封装包把 `zh-Hans` 拉黑的坑
- ✅ **对 8192 像素以上长截图做分块 OCR**——Vision 的硬限制会把中文
  长笔记静默截断到 30 字乱码
- ✅ **打包成 Claude Code skill**——把 `SKILL.md` 扔进
  `~/.claude/skills/`，你跟 Claude 说"导出聊天"或"总结工作消息"
  它就会自动跑对的流水线

### 一分钟上手

```bash
# 1. 装依赖（Xcode CLT、Python venv、ffmpeg，详见 docs/setup.md）
# 2. 临时关闭 SIP（恢复模式下 csrutil disable）
# 3. 让 IM 客户端保持登录

./scripts/find_key_memscan.py           # 从内存抓加密密钥
./scripts/decrypt_db_pure.py -o ./out/  # SQLCipher 转成普通 SQLite
./scripts/parse_messages.py ./out/      # 按天产出 JSONL
```

配合 Claude Code：

> **你：** "总结我过去三个月的工作群聊天，按发送人分组列出最重要
> 的五个未完成客户问题。"
>
> **Claude（装了这个 skill 之后）**：*自动跑流水线、跨库 join 消息、
> 解压 zstd、按线索聚类、产出总结。*

### 能完整抽取 vs. 抽不出来

| 类型 | 状态 | 备注 |
|---|:---:|---|
| 文字消息 | ✅ 全量 | 所有群 / 私聊 |
| 视频（MP4） | ✅ 全量 | 磁盘上就是明文 |
| 文件（PDF/Office/压缩包） | ✅ 全量 | 保留原始格式 |
| 语音（SILK） | ✅ 全量 | `ffmpeg -i in.silk out.mp3` 转码即可播放 |
| 联系人 / 群信息 | ✅ 全量 | 昵称、备注、成员 |
| 朋友圈 | ✅ 全量 | 含旧格式图片 |
| 收藏、表情包 | ✅ 全量 | |
| 旧格式图片 | ✅ 全量 | 硬编码 key 可用 |
| 新格式图片 | ⚠️ 未解 | 上游加密社区没破；改用客户端 UI "全部保存" |

详情见 [`docs/what-you-can-extract.md`](docs/what-you-can-extract.md)。

### 作为 Claude Code skill 安装

```bash
git clone https://github.com/jinjingwangjessica-blip/mac-chat-own-data-kit.git \
    ~/.claude/skills/chat-own-data/
```

然后对 Claude 说"导出聊天记录"或"总结我的工作微信" 就会自动加载。
触发短语和自定义用法见 [`SKILL.md`](SKILL.md)。

### 与现有项目的对比

| | 本项目 | Thearas | ylytdeng | WeChatMsg | cocohahaha |
|---|:---:|:---:|:---:|:---:|:---:|
| macOS 原生 | ✅ | ✅ | ❌ | ❌ | ✅ |
| 支持客户端 4.1.x | ✅ | 仅抓 key | ❌ | 部分 | ✅ |
| 纯 Python SQLCipher v4（无需 brew） | ✅ | ❌ | ❌ | ❌ | ❌ |
| 处理 zstd 消息体 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 中文 OCR（Vision + zh-Hans） | ✅ | ❌ | ❌ | ❌ | ❌ |
| 支持 > 8192 像素截图 | ✅ | ❌ | ❌ | ❌ | ❌ |
| Claude Code skill | ✅ | ❌ | ❌ | ❌ | ❌ |

### 路线图

- [ ] MCP server 模式（给非 Claude Code 客户端）
- [ ] Windows 移植（社区有需求就做——开 issue 留言！）
- [ ] 内置 LLM 的 OCR 纠错流水线（目前作为独立 subagent 跑）
- [ ] 语音转文字（SILK → WAV → Whisper）
- [ ] 朋友圈导出为静态 HTML 档案

### 贡献

欢迎 PR：
- **新客户端版本**——提供示意 schema，**不要**提交别人的聊天内容
- **OCR 后端**——PaddleOCR、TencentOCR、Qwen-VL 对比测试结果
- **段落重排启发式**——OCR 段落重建目前还是艺术+正则

**不要提交别人账号的数据。** 测试用合成数据即可。

### 伦理 & 法律

请看 [`DISCLAIMER.md`](DISCLAIMER.md)。一句话：**自己账号、自己机器、
自己数据**。这是数据可移植性工具，不是监控工具。作者不对滥用负责。

<details>
<summary>万一收到 DMCA 通知 → 点开</summary>

我们准备了应对模板：[`docs/dmca-response-template.md`](docs/dmca-response-template.md)。

关键点：
- 本项目**不重分发** IM 客户端的源代码/二进制/资产
- 定位是**个人数据可移植性**（GDPR 第 20 条、PIPL 第 45 条、CCPA）
- 可以提反通知；14 天等待期间镜像到 Codeberg
</details>

### 致谢

- 从内存抓密钥的部分来自
  [`Thearas/wechat-db-decrypt-macos`](https://github.com/Thearas/wechat-db-decrypt-macos)，
  完整出处见 [`CREDITS.md`](CREDITS.md)。
- SQLCipher v4 规范：[zetetic/sqlcipher](https://github.com/sqlcipher/sqlcipher)
- Apple Vision framework 文档

---

## 🇺🇸 English

> **Your conversations are your memories.** This kit lets you walk away
> with a plaintext copy before the next software update eats them.

### Why you want this

After the **January 2026 takedown wave** of the most popular chat-export
repos, the macOS community has been stuck with half-working tools —
Windows-only forks, stale client versions, native-dep toolchains that
won't install on modern macOS, or extractors that silently mangle
Chinese text because they assume everything is English.

This kit was written by a parent trying to archive a child's first-year
chat records before they could be lost. It does the boring-but-essential
plumbing right:

- ✅ **Pure-Python SQLCipher v4 decryptor** — no `brew install
  sqlcipher`, no native build failures.
- ✅ **Handles zstd-compressed message bodies** — every other tool
  silently drops these.
- ✅ **Chinese-aware Apple Vision OCR** — via direct PyObjC, because the
  popular `ocrmac` wrapper rejects `zh-Hans` in its validator.
- ✅ **Tiles screenshots over 8192 px** — Apple Vision's hard limit
  quietly truncates tall Chinese notes to ~30 characters of garbage.
- ✅ **Ships as a Claude Code skill** — drop the `SKILL.md` into
  `~/.claude/skills/` and Claude will auto-run the right sequence the
  moment you ask it to export or summarize your chats.

### 60-second demo

```bash
./scripts/find_key_memscan.py           # pulls encryption keys from memory
./scripts/decrypt_db_pure.py -o ./out/  # SQLCipher → plain SQLite
./scripts/parse_messages.py ./out/      # emits JSONL keyed by day
```

Or, with Claude Code:

> **You:** "Summarize my work conversations from the last 3 months —
> top 5 unresolved customer issues, grouped by sender."
>
> **Claude** (with this skill installed): *runs the pipeline, joins
> messages across DBs, decompresses zstd, clusters by thread, produces
> summary.*

### What extracts cleanly vs. what doesn't

| Type | Status | Notes |
|---|:---:|---|
| Text messages | ✅ Full | All chats, groups, DMs |
| Videos (MP4) | ✅ Full | Plaintext on disk |
| Files (PDF/Office/archives) | ✅ Full | Original format preserved |
| Voice notes (SILK) | ✅ Full | Convert with `ffmpeg` |
| Contacts & chat rooms | ✅ Full | Names, remarks, member lists |
| Moments / feed posts | ✅ Full | Including older-format images |
| Favorites / stickers | ✅ Full | |
| Images (legacy format) | ✅ Full | Hardcoded key known |
| Images (newer 4.x format) | ⚠️ Blocked | Upstream crypto unsolved; use the app's UI "save all" |

Details in [`docs/what-you-can-extract.md`](docs/what-you-can-extract.md).

### Install as a Claude Code skill

```bash
git clone https://github.com/jinjingwangjessica-blip/mac-chat-own-data-kit.git \
    ~/.claude/skills/chat-own-data/
```

Ask Claude to "export my chat history" and the skill auto-loads. See
[`SKILL.md`](SKILL.md) for trigger phrases.

### Roadmap

- [ ] MCP server mode for non-Claude-Code clients
- [ ] Windows port (open an issue if interested)
- [ ] Built-in LLM-based OCR correction pipeline
- [ ] Voice → text pipeline (SILK → WAV → Whisper)
- [ ] Moments export as HTML archive

### Ethics & legal

Read [`DISCLAIMER.md`](DISCLAIMER.md). TL;DR: **your own account, your
own machine, your own data**. This is a portability tool, not a
surveillance one.

### Credits

- Key-extraction memory-scan from
  [`Thearas/wechat-db-decrypt-macos`](https://github.com/Thearas/wechat-db-decrypt-macos)
  (see [`CREDITS.md`](CREDITS.md)).
- SQLCipher v4 spec: [zetetic/sqlcipher](https://github.com/sqlcipher/sqlcipher).
- Apple Vision framework docs.

---

## License

MIT — see [`LICENSE`](LICENSE).

<p align="center">
  <i>如果它帮你留住了记忆，帮忙点个 ⭐ 让更多家长和档案爱好者看到。</i><br/>
  <i>If this saved your memories, please ⭐ — it helps other parents and
  archivists find the tool.</i>
</p>
