# Callback Authorization Gap

## Pattern

```python
@router.callback_query(F.data.startswith("admin:"))
async def admin_action(cb: CallbackQuery):
    await perform(cb.data.split(":")[1])
```

## Why it is suspicious

The payload selects an action, but nothing in the visible handler ties the actor to a role, and `perform` may be a public service function reachable from other paths.

## What to trace

1. Every registration of `perform` (callers, jobs, HTTP routes).
2. `perform`'s first lines: role check, ownership check, or none.
3. The middleware chain on `router.callback_query` — does an outer middleware gate `admin:*`? Record its `path:line`.
4. Whether the callback data can be forged (it can; treat as user input).

## Verdict

- No check anywhere in the chain → `CONFIRMED` authorization bypass.
- Check exists in `perform` → `OK`; note it in the authorization matrix.
- Check exists only in the keyboard renderer → `CONFIRMED` (UI is not a control).
- Middleware exists but registration order is unclear → `POTENTIAL`, confidence Medium.

## Safe verification (read-only)

```bash
rg -n "def perform|perform\(" app/
rg -n "callback_query.middleware|__middlewares__|middleware"
rg -n "is_admin|IsAdmin|ADMIN"
```

## Remediation direction

Authorize inside the service boundary using the immutable numeric ID and current role; bind the action to actor + chat + message; add one-time tokens for destructive actions.

## Misjudgement to avoid

Calling it a vulnerability because `admin:` appears in the string. The string is a label; the finding is the missing check on the effect.
