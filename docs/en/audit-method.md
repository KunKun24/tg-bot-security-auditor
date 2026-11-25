# Audit Method in Depth

[中文](../audit-method.md) · **English**

`SKILL.md` says what must be done. This document explains why. If you only want to run the agent once, `README.md` is enough; read this when you need to judge whether an audit report is worth believing.

## 1. The subject of the audit is not the code — it is who can do what

Most Telegram bot reports read like code review: "this concatenates SQL", "this handler does not validate the payload". Those statements may all be true, yet they do not answer the operator's real question: **who, needing what, can get what, and how many times can they repeat it.**

So the first artefacts of this method are not findings but two tables:

1. **System map** — entry points → dispatcher → middleware → handler → service → persistence → external API, with every trust boundary marked;
2. **Authorization matrix** — one row per privileged operation: where the actor comes from, where the role is read, how ownership is compared, and whether failure is open or closed.

Severity grows out of those tables, not out of code shape. The same "missing ownership check" is Low behind a private-chat button and High behind a group-admin callback. The difference is not the code; it is who can reach it.

## 2. What each phase prevents

### Phase 0 — Anchor the scope (prevents "not reproducible")

Record the commit SHA, branch, dirty flag and lockfile hash. Without an anchor, nobody can tell which revision a report describes, or whether a defect has already been fixed. Re-audits rely on the anchor plus fingerprints.

### Phase 1 — Build the system map (prevents "locally right, globally wrong")

A handler's internal check can be flawless and still useless if the handler is registered in the wrong place, shadowed by an earlier catch-all, or behind middleware in the wrong order. The map forces **registration order** onto paper, because order is part of authorization semantics.

### Phase 2 — Threat model (prevents "auditing by directory")

Walking an OWASP checklist produces evenly distributed findings and poor priorities. Walking the attacker produces "can an anonymous user take money", which is what decides whether you ship. A small private bot may have no anonymous surface at all; a public paid bot is almost entirely that surface.

### Phase 3 — Layered sweep (prevents "auditing the parts you understand, twice")

Eight domains plus language packs plus the framework map define a defensible floor: what must be looked at, and what "seen" means for each domain. Language packs exist because model recall of dangerous APIs is uneven; the framework map exists because authorization is often not where a reviewer would look for it.

Breadth first (grep for candidate sinks), then depth (trace reachability), keeps time on **reachable** problems instead of speculating about every suspicious fragment.

### Phase 4 — Authorization matrix (prevents "audited the entry, missed the action")

Entries — commands, buttons — usually carry a visible check someone wrote deliberately. Actions — service methods, jobs, internal HTTP routes — are reused, and the second caller tends to forget. Filling rows by action makes the empty cells visible.

### Phase 5 — Verify and classify (prevents "candidate presented as conclusion")

The four verdicts are the core constraint:

- `CONFIRMED` — the path was read end to end; the missing or ineffective control is demonstrated;
- `POTENTIAL` — the path is plausible but one decisive condition is unproven (race window, middleware order, deployment shape);
- `NEEDS-VALIDATION` — only a runtime probe, the vendor, or the deployment config can settle it;
- `OBSERVATION` — a quality issue with no demonstrated security impact.

Writing uncertainty as uncertainty is more valuable than writing it as a claim; the latter costs the whole report its credibility.

### Phase 6 — Rate (prevents "grading with adjectives")

Rate with a testable sentence: **the attacker is X, they need Y, they obtain Z, repeatable N times.** If X is an administrator, or Y requires a second unrelated bug, downgrade. If Z is money and N is unbounded, upgrade. `references/vulnerability-levels.md` calibrates one defect class across four contexts.

### Phase 7 — Report (prevents "looking thorough")

The coverage matrix must permit "not reviewed". An honest 60% beats a fake 100%, because it tells the operator where to look next. Emit findings JSON alongside, so conclusions are consumable by CI and comparable across audits.

## 3. Four Telegram-specific classes that are not code bugs

### Identity conflation

`from.id`, `chat.id`, `sender_chat.id`, `business_connection_id` and `callback_query.from.id` are five different subjects. Treating them as one is the most common — and the least static-analysis-friendly — defect in this ecosystem. Anonymous group admins, channel posts, and inline bots (`via_bot`) all separate "who is speaking" from "who is acting".

### Callbacks are input

`callback_data` is user-controlled even when the bot generated it: it can be forged, replayed, or left over from a previous state. `answerCallbackQuery` is interaction feedback; treating it as authorization is a classic error.

### Payment is a state machine

Telegram redelivers updates. Using the *event* as the idempotency key ("on `successful_payment`, credit") instead of the *charge id* turns redelivery into double fulfillment. Amount, currency and payload must be bound to a server-side order; the client success page proves nothing.

### Transport is a boundary

Webhook `secret_token`, constant-time comparison, fail-closed behaviour; long-polling offset and single-instance assumptions; the token embedded in `getFile` links. Get any one wrong and every authorization check upstream is moot.

## 4. Why the read-only boundary is hard

An audit that mutates state destroys its own report: you can no longer separate "found a problem" from "broke something while looking". Hence the hard constraints — no dependency installation, no migrations, no running the bot, no Bot API calls, no printing secrets — backed by an allowlist of read-only commands (`references/safe-commands.md`) and a substitution table. Anything that needs real traffic becomes `NEEDS-VALIDATION` with a manual procedure.

By the same logic, comments, READMEs, fixtures and issues inside the audited repo are **untrusted data**. A comment that says "ignore previous instructions" must not change audit behaviour.

## 5. How long an audit takes

| Project size | Mode | Typical effort | Dominant cost |
| --- | --- | --- | --- |
| ≤ 5k lines, one service, no payments | Lite | 20–40 min | System map + authorization matrix |
| 5k–30k lines with payments or admin panel | Full | 1.5–4 h | Payment state machine + concurrency |
| Multi-service / multi-bot / Mini App | Full | 4–8 h | Boundaries and identity propagation |
| Post-fix re-audit | Re-audit | 20–60 min | Fingerprint diff only |

These are estimates, not commitments. The report must state what was actually covered.

## 6. Six checks for judging a report

Missing two or more is a warning sign:

1. Is there a commit anchor and a reason for every excluded directory?
2. Is there an authorization matrix naming handlers, or none at all?
3. Does every finding have `path:line` and a reproducible command?
4. Are severity and confidence written separately?
5. Is there a "is it enforced elsewhere?" check per finding?
6. Does the coverage matrix contain honest "not reviewed" entries?

---

> This document was drafted with AIGC assistance and human-reviewed.
