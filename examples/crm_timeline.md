# Example: personal CRM — per-contact timeline

Build a chronological dossier of every interaction with a single
contact. Handy for re-establishing context before a meeting.

## 1. Identify the contact

```bash
sqlite3 decrypted/contact/contact.db \
    "SELECT username, nick_name, remark FROM contact
     WHERE remark LIKE '%ContactName%' OR nick_name LIKE '%ContactName%';"
```

Grab the `username` (wxid) of the match.

## 2. Parse only that conversation

```bash
python scripts/parse_messages.py \
    --src ./decrypted \
    --chat wxid_target_contact \
    --out target.jsonl
```

## 3. Render as a timeline

```python
import json
from datetime import datetime

with open("target.jsonl") as f:
    msgs = [json.loads(l) for l in f]
msgs.sort(key=lambda m: m["create_time"])

last_day = ""
for m in msgs:
    day = datetime.fromtimestamp(m["create_time"]).strftime("%Y-%m-%d")
    t   = datetime.fromtimestamp(m["create_time"]).strftime("%H:%M")
    if day != last_day:
        print(f"\n### {day}")
        last_day = day
    direction = "→" if m["sender_wxid"] != "wxid_target_contact" else "←"
    print(f"{t} {direction} {m['type']:<8} {m['text'] or '(blob)'}")
```

## 4. Ask an LLM to extract obligations

Feed the rendered timeline (or the raw JSONL) to an LLM with:

> Extract every commitment / promise / scheduled action mentioned in
> this conversation. Output as rows: (date mentioned, who committed,
> what, due date if any, fulfilled? yes/no/unknown). Skip casual
> pleasantries.

## Integration with other CRM tools

The JSONL format is importable into Airtable, Notion, or any scripting
environment. Keep the decrypted DB on-device — don't upload it to a
cloud spreadsheet provider unless you've reviewed their data-handling
policies.
