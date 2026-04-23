# Credits

This project stands on the shoulders of the following work.

## Upstream

- **[Thearas/wechat-db-decrypt-macos](https://github.com/Thearas/wechat-db-decrypt-macos)**
  — lldb-based memory scan for SQLCipher keys on macOS Apple Silicon.
  Our `scripts/find_key_memscan.py` is a condensed, annotated re-implementation
  of that approach (MIT-compatible per upstream LICENSE).

- **[zetetic/sqlcipher](https://github.com/sqlcipher/sqlcipher)** — the
  SQLCipher v4 page format spec, reimplemented in pure Python in
  `scripts/decrypt_db_pure.py`.

- **Apple Vision framework** — `VNRecognizeTextRequest`, accessed directly
  via PyObjC to opt into Simplified/Traditional Chinese recognition
  languages that popular Python wrappers hide.

- **[ocrmac](https://pypi.org/project/ocrmac/)** — we don't use it because
  it rejects `zh-Hans`, but reading its source helped us write the PyObjC
  bridge correctly.

## Inspiration / prior art (not dependencies)

- **[LC044/WeChatMsg](https://github.com/LC044/WeChatMsg)** — legacy
  `.dat` V1 image decryption (fixed key `cfcd208495d565ef`, single-byte
  XOR tail). Worth reading when adding V1 image support.

- **[ylytdeng/wechat-decrypt](https://github.com/ylytdeng/wechat-decrypt)**
  — Windows-focused but clean reference for the key-search-in-memory
  pattern.

- **[sjzar/chatlog](https://github.com/sjzar/chatlog)** (removed via DMCA,
  Jan 2026) — dat2img.go documented the `0x07 0x08 V1/V2` image container
  structure before it was taken down. Community mirrors preserve the
  reference.

## Special thanks

To everyone who has contributed to macOS reverse-engineering docs, Apple
developer documentation on Vision, and the broader personal-data-portability
community.

If you believe a contribution from you or your project should be listed
here, please open an issue.
