# Card Redemption Check-Then-Act

## Pattern

```python
row = await db.fetchrow("SELECT redeemed FROM cards WHERE code=$1", code)
if row["redeemed"]:
    return "已使用"
await db.execute("UPDATE cards SET redeemed=true WHERE code=$1", code)
```

## Why it is suspicious

Two concurrent requests can both read `redeemed=false`. Whether that is exploitable depends on isolation, locking, constraints, and how many instances run.

## What to trace

1. Transaction boundaries — is `SELECT` inside a transaction with `FOR UPDATE`?
2. Unique/partial index preventing double redemption?
3. `UPDATE ... WHERE redeemed=false` with affected-row check?
4. Entry points: callback, command, HTTP API, admin panel — all can race.
5. Deployment: multiple workers/replicas increase the window.

## Verdict

- No transaction, no lock, no constraint, no row-count check → `CONFIRMED` race (severity by value).
- Constraint present that makes the second update fail → `OK`, cite it.
- Uncertain isolation or replication → `POTENTIAL`, confidence Medium, `NEEDS-VALIDATION` for the runtime fact.

## Safe verification (read-only)

```bash
rg -n "SELECT.*redeemed|UPDATE.*redeemed|FOR UPDATE|transaction|atomic"
rg -n "UNIQUE|CREATE INDEX|constraint"
```

Manual (owner, isolated DB): two concurrent requests, expect one success.

## Remediation direction

Single atomic statement: `UPDATE cards SET redeemed=true, redeemed_by=$2, redeemed_at=now() WHERE code=$1 AND redeemed=false` and require `rowcount == 1`; or `SELECT ... FOR UPDATE` inside a transaction.

## Misjudgement to avoid

Declaring a confirmed exploit from the code shape alone; concurrency needs entry points and timing, which is why `POTENTIAL` exists.
