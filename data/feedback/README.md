# Feedback archive (`data/feedback/entries.json`)

Web form submissions are appended here via GitHub Actions (`repository_dispatch`).
A separate workflow sends Slack when new rows land in this file.

## Repo secrets (required for form → JSON)

| Secret | Purpose |
|--------|---------|
| `FEEDBACK_SUBMIT_SECRET` | Must match `patParts` / `secretParts` in `js/site.js` |
| `SLACK_WEBHOOK_URL` | Slack notify on new entries (same as patch crawler) |
| `FEEDBACK_DISPATCH_PAT` | Fine-grained PAT: this repo **Contents** read/write + **Metadata** read |

In `js/site.js` → `FEEDBACK_GITHUB`, set `patParts` and `secretParts` (split strings like the Slack webhook).

## Manual test

```bash
gh workflow run feedback-ingest.yml -f type="test" -f content="hello" -f nickname="dev"
```

Or push a new object to `entries[]` — `feedback-notify.yml` will Slack on push.
