#!/usr/bin/env python3
"""Memory-scan encryption keys from a running IM client process.

Adapted from https://github.com/Thearas/wechat-db-decrypt-macos (see
CREDITS.md). Uses lldb Python bindings (no third-party AES library needed
for this step — we only need to find the raw 32-byte key bytes that
already exist in process memory).

Prerequisites:
  • SIP disabled (csrutil disable)
  • Apple Silicon + macOS
  • Xcode Command Line Tools installed (for /usr/bin/lldb)
  • Client app is running and logged in

Run with Xcode's Python 3.9 so lldb bindings load:
  PYTHONPATH=$(lldb -P) /Applications/Xcode.app/Contents/Developer/usr/bin/python3 find_key_memscan.py \\
      --process MyClient --db-dir /path/to/db_storage --out keys.json
"""

import argparse
import glob
import hashlib
import hmac as hmac_mod
import json
import os
import re
import struct
import sys
from pathlib import Path

import lldb

PAGE_SZ = 4096
KEY_SZ = 32
SALT_SZ = 16
HEX_PATTERN = re.compile(rb"x'([0-9a-fA-F]{64,192})'")


def collect_db_files(db_dir: Path):
    """Read every SQLCipher .db under db_dir; collect (rel, salt_hex, page1)."""
    dbs = []
    salt_to_dbs = {}
    for root, _, files in os.walk(db_dir):
        for f in files:
            if not f.endswith(".db") or f.endswith("-wal") or f.endswith("-shm"):
                continue
            path = Path(root) / f
            if path.stat().st_size < PAGE_SZ:
                continue
            with open(path, "rb") as fh:
                page1 = fh.read(PAGE_SZ)
            salt = page1[:SALT_SZ].hex()
            rel = str(path.relative_to(db_dir))
            dbs.append((rel, path, salt, page1))
            salt_to_dbs.setdefault(salt, []).append(rel)
    return dbs, salt_to_dbs


def verify_key(enc_key: bytes, page1: bytes) -> bool:
    """Confirm enc_key decrypts page 1 by re-computing its HMAC."""
    salt = page1[:SALT_SZ]
    mac_salt = bytes(b ^ 0x3A for b in salt)
    mac_key = hashlib.pbkdf2_hmac("sha512", enc_key, mac_salt, 2, dklen=KEY_SZ)
    hmac_data = page1[SALT_SZ:PAGE_SZ - 80 + 16]
    stored = page1[PAGE_SZ - 64:PAGE_SZ]
    h = hmac_mod.new(mac_key, hmac_data, hashlib.sha512)
    h.update(struct.pack("<I", 1))
    return h.digest() == stored


def attach(process_name: str):
    dbg = lldb.SBDebugger.Create()
    dbg.SetAsync(False)
    target = dbg.CreateTarget("")
    err = lldb.SBError()
    proc = target.AttachToProcessWithName(dbg.GetListener(), process_name, False, err)
    if not err.Success():
        print(f"attach failed: {err.GetCString()}", file=sys.stderr)
        sys.exit(1)
    return proc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--process", required=True,
                    help="Client process name to attach to")
    ap.add_argument("--db-dir", required=True,
                    help="Directory containing the encrypted db_storage tree")
    ap.add_argument("--out", default="keys.json",
                    help="Output JSON (relative-db-path → 32-byte hex key)")
    args = ap.parse_args()

    db_dir = Path(os.path.expanduser(args.db_dir))
    dbs, salt_to_dbs = collect_db_files(db_dir)
    print(f"[*] {len(dbs)} DBs, {len(salt_to_dbs)} unique salts under {db_dir}")

    proc = attach(args.process)
    print(f"[+] attached pid={proc.GetProcessID()}")

    key_map = {}
    remaining = set(salt_to_dbs.keys())

    region_info = lldb.SBMemoryRegionInfo()
    addr = 0
    while True:
        e = proc.GetMemoryRegionInfo(addr, region_info)
        if e.Fail():
            break
        base = region_info.GetRegionBase()
        end = region_info.GetRegionEnd()
        if end <= base:
            break
        if region_info.IsReadable() and not region_info.IsExecutable():
            size = end - base
            if 0 < size < 500 * 1024 * 1024:
                err = lldb.SBError()
                data = proc.ReadMemory(base, size, err)
                if err.Success() and data:
                    for m in HEX_PATTERN.finditer(data):
                        hex_str = m.group(1).decode()
                        if len(hex_str) < 96 or len(hex_str) % 2 != 0:
                            if len(hex_str) != 64:
                                continue
                        enc_key_hex = hex_str[:64]
                        # Salt often follows; but fall back to testing against
                        # all remaining salts.
                        if len(hex_str) >= 96:
                            salt_hex = hex_str[64:96]
                            if salt_hex in remaining:
                                enc_key = bytes.fromhex(enc_key_hex)
                                for rel, path, s, page1 in dbs:
                                    if s != salt_hex:
                                        continue
                                    if verify_key(enc_key, page1):
                                        key_map[rel] = enc_key_hex
                                        remaining.discard(salt_hex)
                                        print(f"  [FOUND] salt={salt_hex}  {rel}")
                                        break
        addr = end
        if addr == 0 or not remaining:
            break

    proc.Detach()
    print(f"\n[*] found {len(key_map)}/{len(dbs)} keys")
    with open(args.out, "w") as f:
        json.dump(key_map, f, indent=2)
    print(f"[*] wrote {args.out}")


if __name__ == "__main__":
    main()
