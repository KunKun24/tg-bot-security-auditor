# Expert Audit Checklist

Track coverage per domain. Every item gets one of `Reviewed` / `Finding` / `N/A` / `Not reviewed`, plus evidence. "Reviewed" without evidence is not reviewed.

## 0. Anchor

- [ ] `git rev-parse HEAD`, branch, dirty state recorded
- [ ] Lockfiles present and hashed
- [ ] Excluded paths listed **with reason**
- [ ] Deployment model identified (webhook / polling / both, host, container)
- [ ] Network policy for advisory lookup stated

## 1. Architecture and attack surface

- [ ] Languages, frameworks, versions, entry points
- [ ] Dispatcher → middleware → handler order mapped with `path:line`
- [ ] Services, repositories, jobs, queues, external integrations
- [ ] Trust boundaries and sensitive sinks
- [ ] Identity sources and role sources
- [ ] Threat model actors selected and ranked

## 2. Telegram transport and update lifecycle

- [ ] Webhook `secret_token` verification (constant-time, fail-closed)
- [ ] HTTPS, body limits, proxy trust, request throttling
- [ ] Polling offset, single poller, `update_id` dedupe
- [ ] Malformed / unsupported / unknown update behavior
- [ ] Duplicate and out-of-order delivery, idempotent handlers
- [ ] `edited_message`, `channel_post`, media groups, `chat_member`

## 3. Identity and authorization

- [ ] Immutable numeric IDs used as identity
- [ ] `from.id` / `chat.id` / `sender_chat.id` / `business_connection_id` not conflated
- [ ] Authorization matrix complete, every privileged operation present
- [ ] Admin checks at the action boundary, not only in filters
- [ ] Callback actor / chat / message / resource checks
- [ ] Stale callback, replay, double tap, one-time semantics
- [ ] Group / channel / anonymous-admin edge cases
- [ ] Role change, bootstrap, revocation, cache invalidation

## 4. Input, injection and output

- [ ] SQL / NoSQL / ORM injection (language pack consulted)
- [ ] Shell / process / dynamic evaluation
- [ ] SSRF, redirects, outbound URL controls, timeouts
- [ ] Path traversal, uploads, archive extraction
- [ ] Telegram parse-mode escaping; Web App XSS/CSRF
- [ ] Unsafe deserialization, ReDoS
- [ ] Body size limits before parsing

## 5. Commerce and business logic

- [ ] Payment authenticity, amount / currency / payload binding
- [ ] Idempotent fulfillment and refunds (provider IDs)
- [ ] Balance ledger, atomicity, non-negative constraint
- [ ] Card / license generation, entropy, one-time redemption
- [ ] Membership expiry, renewal stacking, quota reset
- [ ] Referral / reward replay, self-referral, coupon stacking
- [ ] State machine invalid transitions, cancellation, partial completion

## 6. Data and operations

- [ ] Secrets in code, config, CI, images, history (redacted report)
- [ ] DB constraints, transactions, isolation, races
- [ ] Cache scoping and invalidation; queue duplicate delivery
- [ ] Logs, errors, privacy, token leakage in file URLs
- [ ] Container / host permissions, exposed ports, debug mode
- [ ] CI/CD permissions, artifact secrets, PR-triggered execution
- [ ] Dependency inventory and advisory status (with lookup date)
- [ ] Backups, restore, retention, exposure

## 7. Resilience

- [ ] Blocking work in async paths
- [ ] Timeouts, bounded retries, backoff, `retry_after`
- [ ] Unbounded state / queues / fan-out
- [ ] Graceful shutdown, offset persistence
- [ ] Rate limits and abuse controls

## 8. Reporting discipline

- [ ] Every finding has `location` + `evidence_cmd`
- [ ] Control-elsewhere check documented
- [ ] Severity and confidence separated, calibrated
- [ ] Coverage matrix honest (`Not reviewed` where true)
- [ ] Findings JSON validates against `assets/findings.schema.json`
- [ ] Read-only contract upheld (no writes, no live calls)
