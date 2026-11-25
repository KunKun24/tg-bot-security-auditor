# Database and Data Integrity Audit Rules

## Query safety

- Inspect raw SQL, string interpolation, f-strings/template literals, dynamic identifiers, ORM raw-query escape hatches, and NoSQL operator injection.
- Confirm parameters are bound; identifiers (table/column/sort direction) come from an allowlist.
- Authorization predicates must be part of the query or enforced atomically, otherwise a TOCTOU window exists.
- Check mass assignment / unsafe object-to-model binding from user payloads.

## Invariants and transactions

Written invariants to verify against code:

- one payment → exactly one fulfillment;
- one card/code → one redemption;
- balance never below its floor;
- one referral reward per eligible event;
- one active entitlement per rule;
- quota consumption ≤ quota granted.

Then check:
- multi-step state changes wrapped in a transaction or an atomic conditional update;
- isolation level and whether the chosen level permits the observed race;
- unique constraints / idempotency keys where the invariant requires them;
- error paths roll back all related writes;
- external side effects (messages, provider calls) handled via outbox/saga/idempotent retry, not inside an open transaction.

## Concurrency

- Trace read-modify-write on balances, inventory, quotas, card redemption, membership extension, referral rewards.
- Check atomic `UPDATE ... WHERE <guard>` with affected-row verification, `SELECT ... FOR UPDATE`, optimistic version columns, unique idempotency keys.
- A check-then-act without atomicity is a **potential** race; confirm the isolation level, the actual concurrent entry points, and whether a constraint saves it before escalating.
- Check advisory locks / distributed locks are actually held across the whole critical section and released on error.

## Migrations and schema

- Constraints, nullability, defaults, indexes on lookup columns, cascade behavior on user deletion.
- Check migration ordering, idempotency of re-runs, and whether a failed migration can leave a half-applied schema.
- Sensitive data: hashing for passwords (not general crypto), encryption at rest where required, retention, deletion, export.
- Backups: location, access control, and whether backup files are web-reachable.

Do not run migrations, repair commands or any write during audit.

## Caching and queues

- Cache keys scoped by user/tenant/resource; stale authorization data (role, membership, ban) with long TTL.
- Cache poisoning via user-controlled key fragments; invalidation on role/membership change.
- Queues: message authenticity, at-least-once delivery, retry/dead-letter, ordering assumptions, idempotent consumers.
- Duplicate job execution after crash and its effect on money/quota.

## Where to look

- Schema/migrations directory, ORM models, repository/service layer, raw SQL helpers, `*.sql` fixtures.
- Seed scripts and admin bootstrap (often embed real credentials in fixtures).
