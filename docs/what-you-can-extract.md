# What you can extract

Honest table, so you don't discover missing pieces after you've committed to
an analysis.

## Clean extraction (full fidelity)

| Type | Storage | How |
|---|---|---|
| **Text messages** | `db_storage/message/message_[0,1].db` → `Msg_<md5(chat)>` tables | `decrypt_db_pure.py` + `parse_messages.py` |
| **Videos** | `msg/video/YYYY-MM/<md5>.mp4` | Plaintext on disk; just copy |
| **Files** (PDF, Office, archives) | `msg/attach/<room_md5>/YYYY-MM/File/` and `msg/file/` | Plaintext on disk; just copy |
| **Contacts** | `db_storage/contact/contact.db` | Plaintext after `decrypt_db_pure.py` |
| **Chat rooms** | `contact.db` `chat_room` / `chat_room_info_detail` tables | Plaintext after decryption |
| **Sessions / recent chats** | `db_storage/session/session.db` | Plaintext after decryption |
| **Favorites** | `db_storage/favorite/favorite.db` + attached files | Plaintext after decryption |
| **Moments / feed posts** | `db_storage/sns/sns.db` | Plaintext after decryption |
| **Stickers / emoticons** | `db_storage/emoticon/emoticon.db` + `emoticon_cache/` | Plaintext after decryption |

## With one extra step

| Type | How |
|---|---|
| **Voice notes (SILK)** | `media_0.db` → `VoiceInfo` table BLOBs or standalone `.silk` files. Convert with `ffmpeg -i in.silk -c:a libopus out.ogg`. |
| **Legacy-format images (.dat V1)** | AES-128-ECB with hardcoded key `cfcd208495d565ef` (md5("0")[:16]); single-byte XOR on the tail. See `LC044/WeChatMsg` for reference implementation. |

## Not extractable without manual UI work

| Type | Why |
|---|---|
| **Newer-format images (.dat V2)** | Client 4.1.x switched to a per-user AES key that the community hasn't recovered yet (chatlog has a FIXME, my exhaustive ~4.85 GB stride-1 memory scan found no matching 16-byte window). **Workaround**: in the IM app, open a chat → settings → "images & videos" view → multi-select → save to a folder. The resulting files are plain JPEG/HEIC. |

## Things you can infer from metadata even when content is blocked

- Image **md5** of the original file is in `message_content` (zstd-compressed XML).
- Local `.dat` filename md5 is in `packed_info_data` (protobuf; grep for a
  32-char hex string).
- CDN URL (`cdnmidimgurl`, `cdnthumburl`) and per-image `aeskey` are in the
  XML if you ever want to re-download from the server with an authorized
  session.

## Message type cheatsheet

`local_type` values seen in practice (high 32 bits sometimes encode subtype;
mask with `& 0xFFFFFFFF` to get the main type):

| type | meaning |
|---|---|
| 1 | text |
| 3 | image |
| 34 | voice |
| 42 | name card |
| 43 | video |
| 47 | emoji / sticker |
| 48 | location |
| 49 | link / file / mini-program |
| 10000 | system (group notifications, name changes, etc.) |

## Chat room naming

The per-chat table `Msg_<md5>` uses `md5(chat_username)` where
`chat_username` is either a wxid (`wxid_xxx`) for private chats or a
room id (`NNNN@chatroom`) for groups. The same chat can appear in BOTH
`message_0.db` and `message_1.db` sharded by creation time.
