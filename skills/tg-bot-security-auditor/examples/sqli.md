# SQL Injection Through Interpolation

## Pattern

```php
$rows = $pdo->query("SELECT * FROM orders WHERE user_id = " . $_GET['uid']);
```

```python
await db.execute(f"SELECT * FROM cards WHERE code = '{code}'")
```

## Why it is suspicious

String interpolation into SQL lets input alter query structure — unless a later layer re-parameterizes (rare) or the value is provably numeric and cast.

## What to trace

1. Source: is the value user-controlled (Telegram text, callback data, `start` payload, admin form) or internal?
2. Sink: does it reach `query`/`execute` without binding? Is it inside quotes, an identifier position, or `ORDER BY`?
3. Is there an intervening cast/serializer (`intval`, `(int)`, `int()`)? Casts narrow but do not fix identifier injection.
4. Authorization: does the query carry an owner predicate, or is it added after the read?

## Verdict

- User-controlled into a quoted string with no cast → `CONFIRMED`.
- Into an identifier/`ORDER BY` position → `CONFIRMED` even with casts.
- Cast to integer at the boundary → `OBSERVATION` (style), not injection.
- ORM with bound params → `OK`.

## Safe verification (read-only)

```bash
rg -n "query\(|execute\(|raw\(|createStatement"
rg -n "f\"SELECT|format!\\(|\\+ .*SELECT|\\%s.*SELECT"
```

## Remediation direction

Bind all values; allowlist identifiers; keep ownership predicates in the query.

## Misjudgement to avoid

Reporting every f-string near SQL. The string must reach an execution sink with a tainted source.
