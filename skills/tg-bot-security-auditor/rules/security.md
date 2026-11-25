# General Security Audit Rules

Applies to every stack. Language-specific sink tables live in `rules/langs/`; framework idioms in `references/framework-map.md`.

## Trust boundaries and data flow

- Enumerate untrusted sources: Telegram updates (text, caption, entities, file names, callback data, `start` payload), webhook body/headers, uploaded files, admin input, config/env, third-party API responses, queue messages, and **database rows that an untrusted party can write**.
- Enumerate sinks: SQL/NoSQL queries, shell/process exec, template render, filesystem paths, archive extraction, deserialization, dynamic eval, outbound HTTP, redirects, HTML/Markdown output, log sinks, and every authorization decision.
- Build the path source → transform → sink. A sink with no reachable source is a hardening note, not a vulnerability.
- Validation must be server-side and as close to the sink as practical; client-side checks and UI-only constraints are not controls.

## Injection

- Check query construction (string interpolation, ORM raw escape hatches, dynamic identifiers, `ORDER BY` from user input, NoSQL operators like `$ne`/`$where`).
- Check command execution, template evaluation, LDAP/XPath, regex construction (ReDoS), and `eval`/`Function`-style dynamic code.
- Confirm parameters are bound and identifiers are allowlisted; authorization predicates must be **inside** the query or enforced atomically, not only in a prior read.
- Never call a keyword match a confirmed injection without a traced tainted path to the sink.

## Authentication vs authorization

- Authentication = who is acting. Authorization = what that principal may do. Audit them separately.
- Check every privileged operation at the action boundary: admin commands, callbacks, webhook endpoints, jobs, admin HTTP routes.
- Look for IDOR/BOLA, role escalation, missing ownership checks, confused deputy, insecure default admin bootstrap, stale role caches, and **fail-open** behavior when identity or role lookup errors.
- Verify deny-by-default: unknown actor, missing field, deleted user, and unexpected role must all deny.
- Sessions/tokens: entropy, expiry, revocation, storage, rotation, scope.

## Secrets and cryptography

- Search source, config, CI, Dockerfiles, fixtures, logs and git history (only if explicitly in scope) for tokens, keys, passwords, signing secrets and connection strings.
- **Report location and type only.** Never print the value, not even truncated, and never paste `.env` contents.
- Check weak randomness for security-sensitive values, hard-coded keys, ECB / static IV, missing integrity (MAC/AEAD), custom crypto, and non-constant-time comparison of secrets.
- Telegram specifics: bot token appears in `getFile` result URLs and in `https://api.telegram.org/file/bot<token>/...`; `secret_token` must be compared constant-time.

## Web and network

- SSRF: does user input reach an outbound request? Then check scheme allowlist, host allowlist, DNS resolution to private/link-local/metadata ranges, redirect following, response size, and timeouts.
- Open redirect, TLS verification disabled, user-controlled URL construction, missing timeouts, unrestricted fan-out.
- Webhook endpoint: request authenticity, body size limit, content-type assumptions, proxy header trust, rate limiting.

## Files, uploads and deserialization

- Path traversal (including `..%2f`, absolute paths, symlinks), predictable temp names, permissions on written files.
- Upload limits: size, count, type by content not by extension, storage quota, malware policy.
- Archive extraction: zip-slip, symlink entries, decompression bombs.
- Deserialization: can untrusted bytes instantiate executable types (pickle, `unserialize`, `BinaryFormatter`, Java `readObject`, `yaml.load`)?
- Check that user-visible paths and internal topology are not leaked in errors.

## Output encoding

- Telegram HTML and MarkdownV2 escaping are **different from each other and from browser HTML**. Audit per parse mode; user text concatenated into `parse_mode` can break structure or inject links/mentions.
- Check link construction, `tg://user?id=` mentions, 4096-char limits, and entity offsets when rebuilding messages.
- Mini Apps are browser apps: CSP, origin validation, XSS, CSRF, storage, `postMessage` origin checks, and server-side `initData` verification.

## Error handling and disclosure

- Stack traces, debug endpoints, verbose provider errors, exception text echoed to users, logs containing tokens or full update payloads.
- Verify logs are access-controlled and retained appropriately; ensure personal data and payment identifiers are minimized.

## Concurrency and resource exhaustion

- Unbounded queues, worker fan-out, recursive handlers, per-user limits, expensive regex, large payload parsing.
- Missing locks/atomicity around money, quotas and one-time tokens; unbounded retries and retry storms.
- Denial-of-service surface: any handler that does heavy work synchronously before acknowledging an update.
