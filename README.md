<h1 align="center">mac-chat-own-data-kit</h1>

<p align="center">
  <b>Get a clean, structured export of your own chat history from macOS IM apps.</b><br/>
  Pure-Python decryption · Chinese-optimized OCR · Claude Code skill.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT"></a>
  <img src="https://img.shields.io/badge/platform-macOS%2014%2B-lightgrey" alt="macOS 14+">
  <img src="https://img.shields.io/badge/arch-Apple%20Silicon-black" alt="Apple Silicon">
  <img src="https://img.shields.io/badge/python-3.10%2B-green" alt="Python 3.10+">
  <a href="https://anthropic.com/claude-code"><img src="https://img.shields.io/badge/Claude%20Code-skill-orange" alt="Claude Code skill"></a>
</p>

---

> **Your conversations are your memories.** This kit lets you walk away
> with a plaintext copy before the next software update eats them.

## Why you want this

After the **January 2026 takedown wave** of the most popular chat-export
repos, the macOS community has been stuck with half-working tools —
Windows-only forks, stale client versions, native-dep toolchains that
won't install on modern macOS, or extractors that silently mangle
Chinese text because they assume everything is English.

This kit was written by a parent trying to archive a child's first-year
chat records before they could be lost. It does the boring-but-essential
plumbing right:

- ✅ **Pure-Python SQLCipher v4 decryptor** — no `brew install
  sqlcipher`, no native build failures, no system Python breakage.
- ✅ **Handles zstd-compressed message bodies** — every other tool silently
  drops these.
- ✅ **Chinese-aware Apple Vision OCR** — via direct PyObjC, because the
  popular `ocrmac` wrapper rejects `zh-Hans` in its validator.
- ✅ **Tiles screenshots over 8192 px** — Apple Vision's hard limit
  quietly truncates tall Chinese notes to ~30 characters of garbage.
- ✅ **Ships as a Claude Code skill** — drop the `SKILL.md` in
  `~/.claude/skills/` and Claude will auto-run the right sequence the
  moment you ask it to export or summarize your chats.

## 60-second demo

```bash
# 1. Install prerequisites (Xcode CLT, venv, ffmpeg — see docs/setup.md)
# 2. Disable SIP temporarily (csrutil disable in Recovery Mode)
# 3. Log in to your IM client

./scripts/find_key_memscan.py           # pulls encryption keys from memory
./scripts/decrypt_db_pure.py -o ./out/  # turns SQLCipher into plain SQLite
./scripts/parse_messages.py ./out/      # emits JSONL keyed by day
```

Or, with Claude Code:

> **You:** "Summarize my work conversations from the last 3 months
> — top 5 unresolved customer issues, grouped by sender."
>
> **Claude** (with this skill installed): *runs the pipeline, joins
> messages across DBs, decompresses zstd, clusters by thread, produces
> summary.*

## Feature matrix vs. the field

| | This kit | Thearas | ylytdeng | WeChatMsg | cocohahaha |
|---|:---:|:---:|:---:|:---:|:---:|
| macOS native | ✅ | ✅ | ❌ | ❌ | ✅ |
| IM client 4.1.x | ✅ | key-only | ❌ | partial | ✅ |
| Pure-Python SQLCipher v4 (no brew) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Handles zstd message body | ✅ | ❌ | ❌ | ❌ | ❌ |
| Chinese OCR (Vision + zh-Hans) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Handles > 8192 px screenshots | ✅ | ❌ | ❌ | ❌ | ❌ |
| Claude Code skill | ✅ | ❌ | ❌ | ❌ | ❌ |
| MCP server | roadmap | ❌ | ❌ | ❌ | ✅ |

## What extracts cleanly vs. what doesn't

Honest table so you don't get surprised:

| Type | Status | Notes |
|---|:---:|---|
| Text messages | ✅ Full | All chats, groups, DMs |
| Videos (MP4) | ✅ Full | Plaintext on disk |
| Files (PDF/Office/zip) | ✅ Full | Original format preserved |
| Voice notes (SILK) | ✅ Full | Convert with `ffmpeg -i in.silk out.mp3` |
| Contacts & chat rooms | ✅ Full | Names, remarks, member lists |
| Moments (feed posts) | ✅ Full | Including older-format images |
| Favorites / stickers | ✅ Full | |
| Images (legacy format) | ✅ Full | Hardcoded key known |
| Images (newer format) | ⚠️ Blocked | Upstream crypto unsolved; use the app's built-in "save all" |

## Install as a Claude Code skill

```bash
git clone https://github.com/<you>/mac-chat-own-data-kit.git \
    ~/.claude/skills/chat-own-data/
```

That's it. Ask Claude to "export my chat history" or "总结我的微信工作聊天"
and the skill auto-loads. See [`SKILL.md`](SKILL.md) for trigger phrases
and custom invocations.

## Roadmap

- [ ] MCP server mode for non-Claude-Code clients
- [ ] Windows port (pending community interest — open an issue!)
- [ ] Built-in LLM-based OCR correction pipeline (currently runs as a
      separate subagent)
- [ ] Voice → text pipeline (SILK → WAV → Whisper)
- [ ] Moments export as HTML archive

## Contributing

PRs welcome for:
- **Newer client versions** — drop a sample schema; don't send other
  people's messages.
- **OCR backends** — if you have PaddleOCR, TencentOCR, or Qwen-VL
  benchmarks against our Chinese corpus, we'd love them.
- **Reflow heuristics** — paragraph reconstruction for OCR output is
  still art + regex. Better ideas welcome.

**Please don't submit sample data from other people's accounts.** Tests
should use synthetic fixtures.

## Ethics & legal

Read [`DISCLAIMER.md`](DISCLAIMER.md). TL;DR: **your own account, your
own machine, your own data**. This is a portability tool, not a surveillance
one. The authors disclaim responsibility for misuse.

## Credits

- Key-extraction memory-scan originates from
  [`Thearas/wechat-db-decrypt-macos`](https://github.com/Thearas/wechat-db-decrypt-macos).
  Full attribution in [`CREDITS.md`](CREDITS.md).
- SQLCipher v4 spec: [zetetic/sqlcipher](https://github.com/sqlcipher/sqlcipher).
- Apple Vision framework docs.

## License

MIT — see [`LICENSE`](LICENSE).

---

<p align="center">
  <i>If this saved your memories, please ⭐ — it helps other parents and
  archivists find the tool.</i>
</p>
