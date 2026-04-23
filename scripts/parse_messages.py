#!/usr/bin/env python3
"""Minimal reference parser for decrypted IM message DBs.

Reads plaintext SQLite files (produced by decrypt_db_pure.py) and emits
one JSONL record per message. Intended as a starting template — fork this
and adapt to your specific analysis (work summary, CRM timeline, family
archive, etc.).

Key details handled:
  • message_content blob may be **zstd-compressed** for non-text types
    (images, videos, voice, links). We detect via magic bytes and decode.
  • packed_info_data is a tiny protobuf containing a 32-char ASCII hex
    md5. That md5 is the **on-disk filename stem** for the attached
    image (.dat) or video (.mp4). We extract it with a plain regex to
    avoid requiring a protobuf schema.
  • Per-table-named Msg_<md5(chatroom_or_wxid)> pattern is the client's
    convention for isolating each conversation.
  • real_sender_id indexes into the per-DB Name2Id table.

Usage:
    python parse_messages.py --src ./decrypted --out messages.jsonl
"""

import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path

try:
    import zstandard as zstd
except ImportError:
    zstd = None

ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"
MD5_HEX_RE = re.compile(rb"[0-9a-f]{32}")

TYPE_MAIN_MAP = {
    1: "text", 3: "image", 34: "voice", 42: "card", 43: "video",
    47: "sticker", 48: "location", 49: "link", 10000: "system",
}


def chatroom_hash(username: str) -> str:
    return hashlib.md5(username.encode()).hexdigest()


def decode_content(blob):
    """Return (text, was_zstd). Handles bytes / str / zstd transparently."""
    if blob is None:
        return "", False
    if isinstance(blob, str):
        return blob, False
    if isinstance(blob, bytes):
        if blob[:4] == ZSTD_MAGIC:
            if zstd is None:
                return "<zstd blob; pip install zstandard>", True
            try:
                return zstd.ZstdDecompressor().decompress(blob).decode("utf-8", errors="replace"), True
            except Exception:
                return blob.hex(), True
        try:
            return blob.decode("utf-8"), False
        except Exception:
            return blob.hex(), False
    return str(blob), False


def extract_local_md5(packed_info: bytes) -> str:
    if not packed_info:
        return ""
    m = MD5_HEX_RE.search(packed_info)
    return m.group().decode() if m else ""


def load_senders(contact_db: Path) -> dict:
    out = {}
    if not contact_db.is_file():
        return out
    conn = sqlite3.connect(contact_db)
    try:
        for username, nick, remark in conn.execute(
            "SELECT username, nick_name, remark FROM contact"
        ):
            out[username] = {
                "nick_name": nick or "",
                "remark": remark or "",
                "display": remark or nick or username,
            }
    finally:
        conn.close()
    return out


def iter_msg_tables(conn):
    """Yield (table_name, username_for_this_table)."""
    # Name2Id holds rowid→wxid but also the chatroom's own id.
    # Msg_<md5(user_name)> is the convention.
    for (uname,) in conn.execute("SELECT user_name FROM Name2Id"):
        tbl = f"Msg_{chatroom_hash(uname)}"
        has = conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?", (tbl,)
        ).fetchone()[0]
        if has:
            yield tbl, uname


def parse_db(db_path: Path, contacts: dict, out_fh, only_chat: str | None):
    conn = sqlite3.connect(db_path)
    try:
        id_map = dict(conn.execute("SELECT rowid, user_name FROM Name2Id"))
        for table, chat_user in iter_msg_tables(conn):
            if only_chat and chat_user != only_chat:
                continue
            for local_id, stype, ts, sender_id, content, packed in conn.execute(
                f"SELECT local_id, local_type, create_time, real_sender_id, "
                f"message_content, packed_info_data FROM [{table}] ORDER BY create_time"
            ):
                sender_wxid = id_map.get(sender_id, "")
                sender = contacts.get(sender_wxid, {"display": sender_wxid or f"#{sender_id}"})
                text, was_zstd = decode_content(content)
                rec = {
                    "db": db_path.name,
                    "chat": chat_user,
                    "chat_hash": chatroom_hash(chat_user),
                    "local_id": local_id,
                    "type": TYPE_MAIN_MAP.get(stype & 0xFFFFFFFF, f"type:{stype}"),
                    "create_time": ts,
                    "sender_wxid": sender_wxid,
                    "sender_display": sender["display"],
                    "text": text if not was_zstd else "",
                    "content_xml": text if was_zstd else "",
                    "local_md5": extract_local_md5(packed) if packed else "",
                }
                out_fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    finally:
        conn.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True,
                    help="Decrypted database directory (output of decrypt_db_pure.py)")
    ap.add_argument("--out", default="messages.jsonl",
                    help="Output JSONL file")
    ap.add_argument("--chat",
                    help="Only export a specific chat (wxid or chatroom id)")
    args = ap.parse_args()

    src = Path(args.src)
    contacts = load_senders(src / "contact" / "contact.db")
    print(f"loaded {len(contacts)} contacts")

    msg_dbs = sorted((src / "message").glob("message_*.db"))
    print(f"found {len(msg_dbs)} message DB shard(s)")

    with open(args.out, "w", encoding="utf-8") as out_fh:
        for db in msg_dbs:
            parse_db(db, contacts, out_fh, args.chat)

    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
