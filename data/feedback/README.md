# Feedback archive (`data/feedback/entries.json`)

Web form → `repository_dispatch` → `data/feedback/entries.json` → **Feedback Notify** workflow → Slack (`SLACK_WEBHOOK_URL` secret only; not in site JS).

## Repo secrets (required for form → JSON)

| Secret | Purpose |
|--------|---------|
| `FEEDBACK_SUBMIT_SECRET` | Must match `secretParts` in `js/site.js` — **set in repo Secrets** |
| `SLACK_WEBHOOK_URL` | Slack notify on new entries (same as patch crawler) |

**Current `FEEDBACK_SUBMIT_SECRET` value** (add in GitHub → Settings → Secrets → Actions):

```
2c61a8a3fb136c6077463c466a150ca2f21c718ecbdb0d3e
```

`patParts` in `js/site.js` holds the dispatch PAT (split). Regenerate a fine-grained PAT if dispatch stops working.

## Manual test

```bash
gh workflow run feedback-ingest.yml -f type="test" -f content="hello" -f nickname="dev"
```

Or push a new object to `entries[]` — `feedback-notify.yml` will Slack on push.
