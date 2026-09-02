#!/usr/bin/env python3
"""Append feedback entries and diff for Slack notifications."""
from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = ROOT / "data" / "feedback" / "entries.json"


def load_entries() -> dict:
    if not ENTRIES.exists():
        return {"schemaVersion": 1, "entries": []}
    return json.loads(ENTRIES.read_text(encoding="utf-8"))


def save_entries(data: dict) -> None:
    ENTRIES.parent.mkdir(parents=True, exist_ok=True)
    ENTRIES.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_entry(payload: dict) -> dict:
    data = load_entries()
    entry = {
        "id": f"fb-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}",
        "createdAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "lang": str(payload.get("lang") or "ko")[:8],
        "nickname": str(payload.get("nickname") or payload.get("nick") or "")[:40],
        "type": str(payload.get("type") or "Other")[:80],
        "content": str(payload.get("content") or "")[:4000],
        "source": str(payload.get("source") or "web"),
        "githubSent": False,
    }
    data.setdefault("entries", []).append(entry)
    save_entries(data)
    return entry


def pending_entries(data: dict) -> list[dict]:
    return [e for e in data.get("entries", []) if not e.get("githubSent", False)]


def mark_github_sent(data: dict, entry_ids: set[str]) -> None:
    for entry in data.get("entries", []):
        if entry.get("id") in entry_ids:
            entry["githubSent"] = True


def notify_pending() -> int:
    data = load_entries()
    pending = pending_entries(data)
    if not pending:
        print("No pending feedback entries")
        return 0

    print(f"Notifying Slack for {len(pending)} pending entries")
    send_slack(pending)
    mark_github_sent(data, {e["id"] for e in pending})
    save_entries(data)
    return len(pending)


def send_slack(entries: list[dict]) -> None:
    import requests

    url = os.environ.get("SLACK_WEBHOOK_URL")
    if not url or not entries:
        return

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"📩 New feedback ({len(entries)})", "emoji": True},
        }
    ]
    for entry in entries[:5]:
        nick = entry.get("nickname") or "Anonymous"
        body = entry.get("content", "")
        if len(body) > 500:
            body = body[:500] + "…"
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*{entry.get('type', 'Other')}* · `{entry.get('id')}` · {nick}\n"
                        f"_{entry.get('createdAt', '')}_ · lang `{entry.get('lang', 'ko')}`\n"
                        f"{body}"
                    ),
                },
            }
        )
    if len(entries) > 5:
        blocks.append(
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"+{len(entries) - 5} more in `data/feedback/entries.json`"}],
            }
        )
    blocks.append(
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": "🤖 Saved to repo · sent via GitHub Actions (no client webhook)"}],
        }
    )

    try:
        requests.post(url, json={"text": f"📩 New feedback ({len(entries)})", "blocks": blocks}, timeout=10)
    except Exception as exc:
        print(f"Slack error: {exc}", file=sys.stderr)


def validate_dispatch_secret() -> dict:
    raw = os.environ.get("CLIENT_PAYLOAD", "{}")
    payload = json.loads(raw)
    expected = os.environ.get("FEEDBACK_SUBMIT_SECRET", "")
    got = str(payload.get("secret") or "")
    if not expected or got != expected:
        print("Invalid or missing FEEDBACK_SUBMIT_SECRET", file=sys.stderr)
        sys.exit(1)
    content = str(payload.get("content") or "").strip()
    if len(content) < 3:
        print("Content too short", file=sys.stderr)
        sys.exit(1)
    if len(content) > 4000:
        payload["content"] = content[:4000]
    return payload


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "append-dispatch":
        entry = append_entry(validate_dispatch_secret())
        print(json.dumps(entry, ensure_ascii=False))
    elif cmd == "append-manual":
        entry = append_entry(
            {
                "nickname": os.environ.get("FB_NICK", ""),
                "type": os.environ.get("FB_TYPE", "Other"),
                "content": os.environ.get("FB_CONTENT", ""),
                "lang": os.environ.get("FB_LANG", "ko"),
                "source": "workflow_dispatch",
            }
        )
        print(json.dumps(entry, ensure_ascii=False))
    elif cmd == "notify-pending":
        notify_pending()
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
