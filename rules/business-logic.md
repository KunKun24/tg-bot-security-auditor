# Business Logic and Integrity Audit Rules

Map each workflow end-to-end and write its invariants down **before** judging correctness. A logic bug is defined by a violated invariant, not by an ugly code shape.

## Accounts, roles and administration

- Identify the canonical user ID (numeric Telegram ID? internal UUID?) and the canonical role source.
- Check admin bootstrap: first-user-becomes-admin, env allowlist, hard-coded IDs, migration seed.
- Check role change paths: self-promotion, admin granting admin, removing the last admin, multi-admin policy, revocation latency.
- Ensure every sensitive operation re-checks permission at execution time; a role cached at `/start` is stale.
- Check whether a callback payload or a hidden/deleted keyboard can invoke a privileged action directly.

## Balances, wallets and credits

- Trace every increase and decrease, and the single source of truth for each.
- Check atomicity (single transaction or conditional update), non-negative constraints, precision/rounding, currency units and conversion.
- Prevent client-supplied amounts, negative quantities, integer overflow, duplicate credits, and ledger/balance divergence.
- Prefer an append-only ledger with a derived balance; flag mutable balance columns with no audit trail.
- Check refund/chargeback handling: does a refund revoke credit, and what if the user already spent it?

## Cards, licenses and entitlements

- Generation: sufficient entropy, no predictable sequence, no reuse.
- Redemption: one-time, atomic, bound to the intended user/product/device, expiring where designed, revocable, transferable only when specified.
- Validation and consumption must be a single atomic step; check affected-row counts.
- Quotas, device binding and admin overrides must be enforced server-side.
- Do not reveal whether a code exists or belongs to another user beyond necessary behavior (enumeration oracle).

## Orders, delivery and refunds

- Document lifecycle states and allowed transitions; find transitions that skip payment, skip authorization, or resurrect cancelled orders.
- Price, product, quantity, currency and user must be server-derived or independently verified.
- Fulfillment and refund must be idempotent and mutually consistent; a refund without revocation is a defect.
- Manual admin fulfillment/refund needs permission checks and an immutable audit record.

## Memberships, subscriptions and quotas

- Time arithmetic: timezone, DST, month length, expiry boundaries (`>=` vs `>`), grace periods.
- Renewal stacking rules: extend from now or from expiry? concurrent renewals must not lose or double time.
- Downgrade behavior and what happens to data/quota above the new limit.
- Quota resets: period boundaries, partial periods, failed actions consuming quota.
- Expired/revoked membership still usable through cache, JWT, or an active session is a real defect.

## Referrals, rewards and promotions

- Self-referral, cycles, duplicate claims, replay, attribution window, one reward per eligible event.
- Coupon stacking, usage limits, expiry, and race conditions on shared coupon codes.
- Fake-account farming feasibility is a business risk: state it as an observation unless there is a concrete control gap.

## State machines and user journeys

- States, transitions, guards, side effects; invalid transitions must be rejected, not silently ignored.
- Stale buttons, repeated messages, timeout recovery, cancellation, partial completion, and resumption after restart.
- State must be scoped to user + chat (+ thread/topic where relevant) and expire safely.
- Check that a wizard's intermediate state cannot be entered out of order or shared across users.

## Abuse and economics

- Rate limits per user/chat/command for expensive operations.
- Free-tier abuse, trial re-registration, invite farming, storage quota bypass.
- Anything where the cost of an action to the operator is higher than the cost to the attacker.
