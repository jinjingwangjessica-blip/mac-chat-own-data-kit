# Example: quarterly work-chat summary

Suppose you want a summary of all the work conversations in the last
quarter. After running the decrypt + parse pipeline, you have
`messages.jsonl` with all your chats.

## 1. Filter to work chats by chat-room id

Identify your work groups (either by name in the decrypted `contact.db`
or by remembering their wxids):

```bash
# List groups with names containing "工作" or "work"
sqlite3 decrypted/contact/contact.db \
    "SELECT username, nick_name FROM contact
     WHERE nick_name LIKE '%工作%' OR nick_name LIKE '%work%'
        OR username LIKE '%@chatroom';" \
    | head -30
```

Note the chat ids you care about (e.g. `12345678@chatroom`).

## 2. Slice messages.jsonl

```python
import json, hashlib
WORK = {"12345678@chatroom", "wxid_colleague_alice"}
work_hashes = {hashlib.md5(c.encode()).hexdigest() for c in WORK}

with open("messages.jsonl") as f, open("work.jsonl", "w") as out:
    for line in f:
        r = json.loads(line)
        if r["chat_hash"] in work_hashes:
            out.write(line)
```

## 3. Hand to an LLM for summary

Feed `work.jsonl` to Claude Code with a prompt like:

> Read work.jsonl (one message per line). Identify the top 5 unresolved
> customer issues from the last 90 days. For each: date first raised,
> who raised it, current status (resolved / in-progress / stalled), and
> the last relevant message. Output as a markdown table.

The skill handles everything above (`chat-own-data-export` at the top
of this repo) automatically when you ask Claude to "summarize my work
conversations."

## Privacy reminder

Before pasting any excerpt into a shared notes app, meeting agenda, or
public post: **redact colleagues' real names and wxids.** Use initials
or role titles.
