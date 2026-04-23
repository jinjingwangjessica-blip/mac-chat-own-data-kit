---
name: chat-own-data-export
description: Extract your own chat history and attachments from a macOS IM client into structured files. Decrypts SQLCipher v4 databases in pure Python, handles zstd-compressed message bodies, and supports Chinese OCR on long screenshots. Use when the user asks to export, summarize, archive, or analyze their own chat data on macOS — e.g. "export my chat history", "summarize my work conversations", "archive the family group", "解密我的微信数据库", "导出微信聊天记录", "整理客户跟进记录". Do NOT use this to access another person's account or device.
---

# chat-own-data-export

Extracts the user's own chat data from a macOS IM client. Always runs
against the logged-in account on the user's own machine.

## When to invoke

The user asks for any of:
- export / archive / summarize / analyze their own chat history
- extract attachments, voice notes, files from their IM
- read messages from a specific chat/group for research they own

Do NOT invoke when:
- The request targets someone else's account or device.
- The user asks for generic reverse-engineering help (not their data).

## Pipeline

Standard sequence — skip steps already satisfied.

1. **Check prerequisites**

   ```bash
   csrutil status           # must be "disabled"
   which lldb               # /usr/bin/lldb from Xcode CLT
   python3 -c "import cryptography, zstandard, PIL"   # pip deps
   ```

   If SIP is enabled, stop and instruct the user to boot into Recovery
   Mode and run `csrutil disable`. Re-enable afterward.

2. **Extract SQLCipher keys**

   ```bash
   PYTHONPATH=$(lldb -P) /Applications/Xcode.app/Contents/Developer/usr/bin/python3 \
       scripts/find_key_memscan.py \
       --process <ClientName> \
       --db-dir "$HOME/Library/.../<app-sandbox>/db_storage" \
       --out keys.json
   ```

3. **Decrypt all DBs (pure Python, no brew)**

   ```bash
   python scripts/decrypt_db_pure.py --keys keys.json \
       --src "$HOME/Library/.../db_storage" \
       -o ./decrypted/
   ```

4. **Parse messages**

   ```bash
   python scripts/parse_messages.py --src ./decrypted --out messages.jsonl
   # Or: --chat <wxid_or_chatroom_id> to target one conversation
   ```

5. **(Optional) OCR growth-card / screenshot photos**

   ```bash
   python scripts/vision_ocr_cn.py photo.jpg         # normal sizes
   python scripts/tiled_ocr.py long_screenshot.jpg   # > 8192 px
   ```

## Extractable surface

Tell the user this upfront so expectations match reality:

| Type | Status |
|---|:---:|
| Text messages (all chats) | ✅ Full |
| Videos (MP4) | ✅ Full, plaintext on disk |
| Files (PDF/Office/archives) | ✅ Full |
| Voice notes (SILK) | ✅ Full — convert with `ffmpeg -i in.silk out.mp3` |
| Contacts & chat rooms | ✅ Full |
| Moments / feed posts | ✅ Full |
| Favorites / stickers | ✅ Full |
| Images (legacy format) | ✅ Hardcoded key known |
| Images (newer 4.x format) | ⚠️ Upstream crypto unsolved. Tell the user to use the IM app's own UI ("save all images" in chat settings) to batch-export. |

## Data handling rules

- Never upload decrypted data to a remote API unless the user explicitly
  consents.
- Prefer local LLMs for summarization if the data is sensitive.
- Do not retain key files or decrypted DBs past the analysis session
  unless the user asks. Suggest deleting.
- If the user wants to publish or share an analysis: remind them to
  redact third-party wxids, phone numbers, and real names.

## Known friction

- macOS 26 support for lldb memory reading is still rolling in; stay
  current with the Thearas upstream.
- Some clients have started using a different per-chat key format for
  legacy image files; fall back to the IM app's UI export if the legacy
  image decryptor fails.
- SQLCipher v5 is rumored for future releases; check the page layout
  constants before panicking if decrypt_db_pure.py starts emitting
  corrupt output.
