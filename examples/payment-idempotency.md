# Payment Fulfillment Not Idempotent

## Pattern

```python
@router.message(F.successful_payment)
async def paid(message: Message, db):
    await db.credit(message.from_user.id, message.successful_payment.total_amount / 100)
    await message.answer("已到账")
```

## Why it is suspicious

Telegram retries updates when the webhook does not acknowledge quickly or the process crashes mid-handler. Fulfillment keyed on the *event* rather than the *charge* doubles credit on retry.

## What to trace

1. Is there a uniqueness constraint or lookup on `telegram_payment_charge_id` / `provider_payment_charge_id`?
2. Is the credit and the "processed" marker in one transaction?
3. Does the handler validate `currency`, `total_amount` and `invoice_payload` against the order record?
4. Can the same charge be delivered through two paths (message handler + reconciliation job)?

## Verdict

- No idempotency key + retries possible → `CONFIRMED` duplicate-credit defect (severity by amount and rate limit).
- Key exists but checked then inserted non-atomically → `POTENTIAL` race; confirm with constraint presence.
- Key exists with unique index and transaction → `OK`.

## Safe verification (read-only)

```bash
rg -n "successful_payment|telegram_payment_charge_id|provider_payment_charge_id"
rg -n "credit|balance|fulfill"
rg -n "UNIQUE|unique|idempot"
```

## Remediation direction

Insert the charge ID into a ledger with a unique constraint, then credit in the same transaction; treat `INSERT` conflict as "already fulfilled". Validate amount/currency/payload before any effect.

## Misjudgement to avoid

Assuming retries never happen because the handler is fast. Crashes, deploys and 5xx responses all cause redelivery.
