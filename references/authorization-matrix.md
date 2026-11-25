# Authorization Matrix

Produced in step 4. One row per privileged operation — not per file, not per menu. A blank cell is unaudited surface and belongs in the report's "not reviewed" list.

## Columns

| Column | Meaning |
| --- | --- |
| ID | `A-01`, `A-02`, … |
| Operation | what the action does, in business terms ("credit balance", "broadcast to all users") |
| Entry | `command` / `callback` / `webhook` / `admin-http` / `job` / `start-payload` |
| Handler | `path:line` of the entry point |
| Actor check | where the acting identity is established (`from.id`, session, verified `initData`) |
| Role check | where the role is read and compared; `none` if absent |
| Ownership check | resource ownership comparison; `none` if absent |
| Guard type | `deny-by-default` / `allowlist` / `role` / `ownership` / `one-time-token` / `none` |
| Fail mode | what happens on lookup error or missing identity: `deny` / `allow` / `crash` |
| Evidence | `evidence_cmd` reproducing the path |
| Status | `CONFIRMED` / `POTENTIAL` / `NEEDS-VALIDATION` / `OK` |

## Rules

1. **Authorization lives at the action boundary.** A filter on the command, a hidden button, or a check in the menu renderer is not evidence. Find the check in the function that performs the effect, or in a middleware that provably wraps it.
2. **Record the check, not the intention.** `if is_admin(...)` at `path:line`, or `none`.
3. **Fail-closed is a property, not a vibe.** If the role lookup throws and the handler continues, the fail mode is `allow`.
4. **Callbacks are separate entries** when they invoke a different effect than the command they mirror — they are frequently the unprotected copy.
5. **Jobs and admin HTTP routes count.** Scheduled retries and internal endpoints often skip checks that the UI path has.
6. **State the principal explicitly** when Telegram offers several (`from.id` vs `chat.id` vs `sender_chat.id` vs `business_connection_id`).

## Example

| ID | Operation | Entry | Handler | Actor check | Role check | Ownership | Guard | Fail mode | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-03 | Credit user balance | callback `pay:credit` | `app/handlers/pay.py:41` | `from.id` used as payer | n/a | **none** — target `user_id` decoded from callback data | none | allow | CONFIRMED |
| A-04 | Broadcast message | command `/broadcast` | `app/handlers/admin.py:112` | `from.id` | allowlist `ADMIN_IDS` at `admin.py:90` | n/a | allowlist | deny | OK |
| A-05 | Fulfill order | webhook `/pay/cb` | `app/http/pay.py:60` | signature check at `:44` | n/a | order lookup by `order_id`, no user binding | signature | deny | POTENTIAL (signature verifies provider, not order owner) |

## How it interacts with findings

- A row with `Guard: none` and a reachable actor is a finding; cite the row ID.
- A row with `Guard: role` but a check that runs *after* the effect is a finding (TOCTOU / order-of-operations), not an OK.
- A row marked `NEEDS-VALIDATION` must say what runtime fact is missing (e.g. "middleware registration order unverified").
- Rows marked `OK` are the positive controls section of the report — only include ones actually inspected.
