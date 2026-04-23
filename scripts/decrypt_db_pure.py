#!/usr/bin/env python3
"""Pure-Python SQLCipher v4 → plain SQLite decryptor.

No brew, no sqlcipher CLI, no native build. Operates entirely in Python
with the `cryptography` package (hazmat AES-CBC) plus stdlib.

Why this file exists:
  Many chat-export pipelines die at this step because `brew install
  sqlcipher` fails on modern macOS, or because the user's Python was
  compiled against a different OpenSSL. This implements the SQLCipher
  v4 default page layout from first principles so you just need
  `pip install cryptography`.

SQLCipher v4 defaults assumed (match the schema emitted by mainstream
IM clients as of 2025):

    page_size        = 4096
    reserved_sz      = 80  (IV 16 + HMAC-SHA512 64)
    cipher           = AES-256-CBC
    HMAC             = HMAC-SHA512
    kdf_iter         = 256000   (not used here; we already have the
                                 derived 32-byte encryption key)

Page 1 layout:
    [0:16]        : salt (stored plaintext)
    [16:4016]     : AES-CBC(enc_key, iv)  → 4000 bytes plaintext
    [4016:4032]   : IV
    [4032:4096]   : HMAC-SHA512 tag
Plaintext page 1 = b"SQLite format 3\\x00" + decrypted 4000 bytes
                 + 80 bytes zero (reserved, ignored by sqlite3)

Pages 2+:
    [0:4016]      : AES-CBC ciphertext
    [4016:4032]   : IV
    [4032:4096]   : HMAC-SHA512 tag
Plaintext page = decrypted 4016 bytes + 80 zero bytes
"""

import argparse
import glob
import hashlib
import hmac
import json
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

PAGE_SZ = 4096
RESERVED = 80
IV_SZ = 16
HMAC_SZ = 64
SALT_SZ = 16
KEY_SZ = 32
SQLITE_MAGIC = b"SQLite format 3\x00"


def derive_mac_key(enc_key: bytes, salt: bytes) -> bytes:
    """Derive the HMAC key from the AES key and the DB salt."""
    mac_salt = bytes(b ^ 0x3A for b in salt)
    return hashlib.pbkdf2_hmac("sha512", enc_key, mac_salt, 2, dklen=KEY_SZ)


def decrypt_page(page: bytes, page_no: int, enc_key: bytes, mac_key: bytes,
                 verify_hmac: bool = True) -> bytes:
    is_first = (page_no == 1)
    ct_start = SALT_SZ if is_first else 0
    ct_end = PAGE_SZ - RESERVED
    ciphertext = page[ct_start:ct_end]
    iv = page[ct_end:ct_end + IV_SZ]
    stored_hmac = page[ct_end + IV_SZ:ct_end + IV_SZ + HMAC_SZ]

    if verify_hmac:
        pno_bytes = page_no.to_bytes(4, "little")
        mac_input = page[ct_start:ct_end + IV_SZ] + pno_bytes
        expected = hmac.new(mac_key, mac_input, hashlib.sha512).digest()
        if not hmac.compare_digest(expected, stored_hmac):
            raise ValueError(f"HMAC mismatch on page {page_no}")

    cipher = Cipher(algorithms.AES(enc_key), modes.CBC(iv), backend=default_backend())
    plain_body = cipher.decryptor().update(ciphertext) + cipher.decryptor().finalize()

    if is_first:
        out = SQLITE_MAGIC + plain_body + b"\x00" * RESERVED
    else:
        out = plain_body + b"\x00" * RESERVED
    assert len(out) == PAGE_SZ
    return out


def decrypt_file(src: Path, dst: Path, enc_key: bytes, verify_hmac: bool = True):
    size = os.path.getsize(src)
    if size < PAGE_SZ or size % PAGE_SZ != 0:
        return 0, f"bad size {size}"
    total_pages = size // PAGE_SZ
    with open(src, "rb") as f:
        page1 = f.read(PAGE_SZ)
        salt = page1[:SALT_SZ]
        mac_key = derive_mac_key(enc_key, salt)

        os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
        with open(dst, "wb") as out:
            try:
                out.write(decrypt_page(page1, 1, enc_key, mac_key, verify_hmac))
            except Exception as e:
                return 0, f"page 1: {e}"
            for n in range(2, total_pages + 1):
                p = f.read(PAGE_SZ)
                if len(p) != PAGE_SZ:
                    break
                try:
                    out.write(decrypt_page(p, n, enc_key, mac_key, verify_hmac))
                except Exception as e:
                    return n - 1, f"page {n}: {e}"
    return total_pages, "OK"


def main():
    ap = argparse.ArgumentParser(description="Decrypt SQLCipher v4 databases (pure Python)")
    ap.add_argument("--keys", required=True,
                    help="JSON file mapping relative-db-path -> 32-byte hex encryption key")
    ap.add_argument("--src", required=True,
                    help="Root directory containing the encrypted .db files")
    ap.add_argument("-o", "--output", default="decrypted",
                    help="Output directory for plaintext SQLite files (default: decrypted)")
    ap.add_argument("--no-hmac", action="store_true",
                    help="Skip HMAC verification (not recommended)")
    args = ap.parse_args()

    keys_path = Path(args.keys)
    if not keys_path.is_file():
        print(f"key file not found: {keys_path}"); sys.exit(1)
    data = json.loads(keys_path.read_text())
    entries = {k: v for k, v in data.items() if not k.startswith("__")}

    src_root = Path(args.src)
    out_root = Path(args.output)
    print(f"source: {src_root}")
    print(f"output: {out_root.resolve()}")

    ok = fail = 0
    for rel, key_hex in sorted(entries.items()):
        src = src_root / rel
        dst = out_root / rel
        if not src.is_file():
            print(f"  [skip] {rel} (missing)"); continue
        n, msg = decrypt_file(src, dst, bytes.fromhex(key_hex), verify_hmac=not args.no_hmac)
        if msg == "OK":
            print(f"  [ok]   {rel}  pages={n}  size={os.path.getsize(dst)//1024} KB")
            ok += 1
        else:
            print(f"  [fail] {rel}  pages_ok={n}  err={msg}")
            fail += 1
    print(f"\ndone: {ok} ok, {fail} failed")


if __name__ == "__main__":
    main()
