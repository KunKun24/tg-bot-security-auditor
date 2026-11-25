# User-Controlled Outbound Request

## Pattern

```javascript
const r = await fetch(ctx.message.text);
await ctx.reply(await r.text());
```

## Why it is suspicious

If the bot fetches URLs supplied by users from its own host, it becomes a proxy into the internal network and cloud metadata.

## What to trace

1. Can an untrusted actor control the URL? (message text, `start` payload, admin-only input, config)
2. Is the call server-side? (frontend `fetch` is not SSRF)
3. Scheme allowlist? `file:`, `gopher:`, `ftp:` handling?
4. Host allowlist or resolved-IP blocklist (private, loopback, link-local, `169.254.169.254`, IPv6 equivalents)?
5. Redirects followed? Re-validated after each hop?
6. Timeouts and response size limits?
7. Is the response echoed back to the user (blind vs full-read SSRF)?

## Verdict

- Any authenticated user + no restrictions + response returned → High.
- Admin-only + no restrictions → Medium (privilege already high, but pivot to metadata is real).
- Allowlist of expected hosts, no redirects, timeouts → `OK`.

## Safe verification (read-only)

```bash
rg -n "fetch\(|axios|requests\.(get|post)|http\.Get|curl_exec|file_get_contents\("
rg -n "allowlist|private|127\.0\.0\.1|169\.254|resolve|redirect"
```

Do not test against production; a local fixture with a metadata-like address is acceptable only in an isolated environment you create outside the repo.

## Remediation direction

Allowlist scheme + host, resolve DNS and reject private/reserved ranges, disable or revalidate redirects, cap response size and time.

## Misjudgement to avoid

Flagging every `fetch` call. The finding requires a tainted source reaching it.
