# Webhook Without Secret Validation

## Pattern

```python
@app.post("/webhook")
async def hook(request: Request):
    update = Update(**await request.json())
    await dp.feed_update(bot, update)
```

## Why it is suspicious

Anyone who learns the URL can post a forged `Update`. The consequence depends entirely on which handlers trust `from.id`.

## What to trace

1. Is `secret_token` compared anywhere between the request and `feed_update`?
2. Is the endpoint behind a gateway that authenticates (mTLS, shared header, IP allowlist)? An IP allowlist alone is weak but changes severity.
3. Do handlers treat `from.id` as identity? Then a forged update is full impersonation of any user, including admins.
4. Is `update_id` deduped? Forgery also allows replay.

## Verdict

| Situation | Severity |
| --- | --- |
| Public endpoint, no secret, privileged handlers | Critical |
| Public endpoint, no secret, only read-only handlers | High |
| Secret checked but not constant-time | Low (informational unless token is short) |
| Secret checked, fail-open on error | High |
| Gateway authenticates, app does not | Low–Medium (cite the gateway in control-elsewhere) |

## Safe verification (read-only)

```bash
rg -n "X-Telegram-Bot-Api-Secret-Token|secret_token|setWebhook"
rg -n "feed_update|webhook|/hook"
```

## Remediation direction

Generate a random secret per environment, compare with `hmac.compare_digest`, return 403 on mismatch **before** parsing the body, and keep the endpoint out of public indexing.

## Misjudgement to avoid

Reporting "webhook missing secret" as Critical without checking what a forged update can actually reach.
