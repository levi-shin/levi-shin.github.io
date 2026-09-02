# Feedback archive (`data/feedback/entries.json`)

## Flow (no Slack URL in site JS)

```
Web form → repository_dispatch → entries.json (githubSent: false)
         → daily GHA 19:00 KST → Slack (SLACK_WEBHOOK_URL secret) → githubSent: true
```

| Step | What happens |
|------|----------------|
| 1 | User submits feedback; browser calls GitHub `repository_dispatch` only |
| 2 | `feedback-ingest.yml` appends entry with `"githubSent": false` |
| 3 | `feedback-notify.yml` runs **every day at 19:00 KST** (and on manual dispatch) |
| 4 | Script finds `githubSent: false`, posts to Slack, flips to `true`, commits |

Slack webhook URL lives **only** in repo Secret `SLACK_WEBHOOK_URL` — never in client code.

## Entry shape

```json
{
  "id": "fb-20260902-abc12345",
  "createdAt": "2026-09-02T10:00:00Z",
  "lang": "ko",
  "nickname": "nick",
  "type": "Bug",
  "content": "...",
  "source": "web",
  "githubSent": false
}
```

## Repo secrets

| Secret | Purpose |
|--------|---------|
| `FEEDBACK_SUBMIT_SECRET` | Must match `secretParts` in `js/site.js` |
| `SLACK_WEBHOOK_URL` | Slack notify (patch crawler uses the same) |

`patParts` in `js/site.js` is the dispatch PAT (split). Regenerate if dispatch stops working.

## Manual test

```bash
# Append test entry
gh workflow run feedback-ingest.yml -f type="test" -f content="hello" -f nickname="dev"

# Run notify immediately (don't wait for 19:00 KST)
gh workflow run feedback-notify.yml
```
