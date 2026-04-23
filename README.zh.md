<h1 align="center">mac-chat-own-data-kit</h1>

<p align="center">
  <b>在 macOS 上把你自己的聊天记录完整、干净地导出成结构化文件。</b><br/>
  纯 Python 解密 · 中文 OCR · Claude Code skill 集成
</p>

---

> **你的聊天记录是你自己的记忆。** 这个工具包帮你在下一次客户端更新
> 之前把它们完整搬走。

## 为什么需要它

**2026 年 1 月那次大规模下架**之后，macOS 社区的聊天导出工具处境尴尬——
Windows-only 的 fork、停在老版本的项目、装不上新 macOS 的原生依赖、
遇到中文就悄无声息地糊掉。

这个工具是一位想把孩子第一年成长记录归档的家长写的，把关键的
"脏活累活" 做对：

- ✅ **纯 Python SQLCipher v4 解密器**——不用 `brew install sqlcipher`，
  不会遇到原生编译错误、系统 Python 被搞坏之类问题
- ✅ **正确处理 zstd 压缩的消息体**——其他工具会默默丢掉
- ✅ **中文 Apple Vision OCR**——用 PyObjC 直调系统 API，绕开
  `ocrmac` 封装包把 `zh-Hans` 拉黑的坑
- ✅ **对 8192 像素以上长截图做分块 OCR**——Vision 的硬限制会把中文长
  笔记静默截断到 30 字乱码
- ✅ **打包成 Claude Code skill**——把 `SKILL.md` 扔进
  `~/.claude/skills/`，你跟 Claude 说"导出聊天"或"总结工作消息"的瞬间
  它就会自动跑对的流水线

## 一分钟上手

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

## 能完整抽取 vs. 抽不出来

诚实列出来免得用的时候踩坑：

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

## 作为 Claude Code skill 安装

```bash
git clone https://github.com/<你>/mac-chat-own-data-kit.git \
    ~/.claude/skills/chat-own-data/
```

然后对 Claude 说"导出聊天记录"或"总结我的工作微信" 就会自动加载。
触发短语和自定义用法见 [`SKILL.md`](SKILL.md)。

## 路线图

- [ ] MCP server 模式（给非 Claude Code 客户端）
- [ ] Windows 移植（社区有需求再做——开 issue 留言！）
- [ ] 内置 LLM 的 OCR 纠错流水线（目前作为独立 subagent 跑）
- [ ] 语音转文字（SILK → WAV → Whisper）
- [ ] 朋友圈导出为静态 HTML 档案

## 贡献

欢迎 PR：
- **新客户端版本**——提供示意 schema 即可，**不要**提交别人的聊天内容
- **OCR 后端**——PaddleOCR、TencentOCR、Qwen-VL 的对比测试结果
- **段落重排启发式**——OCR 段落重建目前还是艺术+正则，欢迎更好的想法

**不要提交别人账号的数据。** 测试用合成数据即可。

## 伦理 & 法律

请看 [`DISCLAIMER.md`](DISCLAIMER.md)。一句话：**自己账号、自己机器、
自己数据**。这是数据可移植性工具，不是监控工具。作者不对滥用负责。

## 致谢

- 从内存抓密钥的部分来自
  [`Thearas/wechat-db-decrypt-macos`](https://github.com/Thearas/wechat-db-decrypt-macos)，
  完整出处见 [`CREDITS.md`](CREDITS.md)。
- SQLCipher v4 规范：[zetetic/sqlcipher](https://github.com/sqlcipher/sqlcipher)
- Apple Vision framework 文档

## License

MIT——见 [`LICENSE`](LICENSE)。

---

<p align="center">
  <i>如果它帮你留住了记忆，帮忙点个 ⭐ 让更多家长和档案爱好者看到。</i>
</p>
