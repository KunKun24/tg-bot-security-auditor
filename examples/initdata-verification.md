# Mini App initData Trusted Client-Side

## Pattern

```javascript
const user = JSON.parse(new URLSearchParams(location.hash.slice(1)).get("tgWebAppData"));
fetch("/api/me", { headers: { "X-User-Id": JSON.parse(decodeURIComponent(user)).user.id } });
```

Or server-side:

```python
user_id = request.json["initDataUnsafe"]["user"]["id"]
```

## Why it is suspicious

`initData` and every field inside it are client-supplied. Only the HMAC proves Telegram issued it, and only freshness bounds replay.

## What to trace

1. Where is `initData` verified — browser, backend, or not at all?
2. Is the HMAC computed over the **data-check-string** (sorted `key=value` pairs excluding `hash`, joined by `\n`) with secret key `HMAC_SHA256("WebAppData", bot_token)`?
3. Is `auth_date` compared against a policy window? Is a nonce/`query_id` tracked for one-time use where required?
4. Does the backend bind its session to the verified user, or does it still trust a client-supplied ID header?
5. Third-party hosted app: Ed25519 signature over `bot_id + initData` verified?

## Verdict

- Client-side only or `initDataUnsafe` used as identity → `CONFIRMED` authentication bypass.
- HMAC present but `auth_date` unbounded → `POTENTIAL` replay; severity by what a replayed session can do.
- Full validation with freshness and session binding → `OK`.

## Safe verification (read-only)

```bash
rg -n "initData|initDataUnsafe|tgWebAppData|WebAppData"
rg -n "hmac|sha256|auth_date|query_id"
```

Then reimplement the HMAC in a scratch script against a **test** bot token; never the live one.

## Remediation direction

Validate server-side on every request, reject stale `auth_date`, bind session to the verified `user.id`, and never send the bot token to the client.

## Misjudgement to avoid

Treating "the value looks like JSON from Telegram" as proof. Only the HMAC is proof.
