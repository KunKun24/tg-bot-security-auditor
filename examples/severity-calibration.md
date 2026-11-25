# Severity Calibration

Four versions of one defect type. The point is that the code shape does not set the severity; the actor, the asset and the blast radius do.

## Case A — self-credit in a private chat

A callback lets the caller add a fixed 1-credit bonus to their own account, repeatable.

- Actor: any user, no precondition
- Asset: credits (money-equivalent)
- Verdict: **High**, P1 — direct financial loss, trivially repeatable.

## Case B — same defect, one-time per user with server-side dedupe

The bonus is granted once per user; replay is blocked by a unique key.

- Verdict: **Low**, P3 — residual logic bug, no unbounded gain.

## Case C — missing ownership check on another user's order view

Callback shows `order_id` data for any ID; fields include masked address.

- Actor: any user; enumeration over sequential IDs
- Verdict: **Medium**, P2 — privacy exposure, enumerable.

## Case D — same, but full address, phone, and payment reference

- Verdict: **High**, P1 — personal data + payment reference, mass-enumerable.

## The rule

Write the sentence "attacker is X, they need Y, they get Z, repeatable N times". If X is "an admin", or Y requires a second unrelated bug, downgrade. If Z is money and N is unbounded, upgrade.

## What never changes severity

- The CWE number.
- The file being security-related.
- The project being small.
- The reviewer's gut feeling about the code style.

## Confidence is separate

Case A read in full, no middleware → High confidence. Case A but middleware registration order unclear → still High severity, Medium confidence, and the finding says what would settle it.
