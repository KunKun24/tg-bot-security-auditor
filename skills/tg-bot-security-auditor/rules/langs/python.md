# Python Pack

Detection: `requirements.txt`, `pyproject.toml`, `poetry.lock`, `Pipfile`, `*.py`. SDK: `aiogram`, `python-telegram-bot`, `telethon`, `pyTelegramBotAPI`, `telegram` (raw).

## Dangerous API → safe replacement

| Dangerous | Why | Safe |
| --- | --- | --- |
| `eval` / `exec` / `compile` on input | code execution | no dynamic code; dispatch tables |
| `pickle.loads`, `dill`, `torch.load` | arbitrary object construction | JSON; `safe_load` |
| `yaml.load` (no Loader) | instantiation | `yaml.safe_load` |
| `subprocess.*(shell=True)`, `os.system`, `os.popen` | shell injection | argument list, `shell=False` |
| f-string / `%` / `.format` into SQL | injection | bound params; allowlisted identifiers |
| `os.path.join(base, user)` without normalization | traversal | `pathlib` + resolve + `is_relative_to(base)` |
| `requests`/`httpx` without `timeout` | hang / DoS | explicit timeout tuple |
| `requests.get(user_url)` | SSRF | allowlist + resolved-IP check |
| `tarfile.extractall`, `zipfile.extractall` | zip-slip | validate members, reject absolute/`..` |
| `random` for tokens/codes | predictable | `secrets` |
| `==` on secrets/tokens | timing | `hmac.compare_digest` |
| `flask`/`fastapi` debug=True | RCE console / traceback | off in prod |

## Telegram pitfalls

- aiogram: filters on `router.message` apply **per router**; a `IsAdmin()` filter registered on a different router does not protect this handler. Check `Dispatcher` include order and middleware registration (`dp.update.middleware` vs `router.message.middleware`).
- aiogram 2 vs 3: `executor.start_polling(skip_updates=...)`, `state` storage, and `F.text` semantics differ; confirm the pinned major version before judging.
- python-telegram-bot: `ApplicationBuilder` handler groups and `filters.ChatType`; `ConversationHandler` state is per chat/user — check persistence if `PicklePersistence` is used (deserialization + file perms).
- Telethon userbots: `session` files are credentials — check they are not committed; `events.NewMessage` with `chats=` filtering is not authorization.
- `logging` of `update` objects prints full payloads (tokens in file URLs, user data).

## Useful searches (read-only)

```bash
rg -n "eval\(|exec\(|pickle\.loads|yaml\.load\(|shell=True|os\.system"
rg -n "execute\(f\"|execute\(.*%|execute\(.*\.format\("
rg -n "requests\.(get|post)\(|httpx\.(get|post)\("
rg -n "verify=False|debug=True"
rg -n "def is_admin|ADMIN_IDS|admin_ids"
```
