# Rust Pack

Detection: `Cargo.toml`, `Cargo.lock`, `*.rs`. SDK: `teloxide`, `frankenstein`, `telegram-bot`.

## Dangerous API → safe replacement

| Dangerous | Why | Safe |
| --- | --- | --- |
| `Command::new("sh").arg("-c").arg(input)` | shell injection | `.args([...])`, no shell |
| `sqlx::query(&format!(...))` | SQLi | `query!` / bound params |
| `std::fs` with user path | traversal | `canonicalize` + prefix check |
| `unsafe { transmute }` / raw pointers | memory corruption | safe abstractions |
| `reqwest::get(user_url)` | SSRF | client with timeout + allowlist |
| `serde_json::from_str` huge | DoS | size limit |
| `==` on tokens | timing | `subtle::ConstantTimeEq` |
| `unwrap()` on untrusted parse | panic → DoS | handle error |
| `rand::thread_rng` for secrets | ok for non-crypto only | `OsRng` |

## Telegram pitfalls

- teloxide: `Dispatcher` with `Update::filter_message()` and dptree — authorization must be a branch in the tree, not a check inside the handler that can be bypassed by another branch.
- `Bot::from_env()` reads `TELOXIDE_TOKEN`; check it is not logged by `tracing` with debug level on the whole request.
- `teloxide` parse mode: use `Html`/`MarkdownV2` escaping helpers; manual `format!` with user text is injectable.
- Blocking work inside `async` handler without `spawn_blocking` stalls the dispatcher.

## Useful searches

```bash
rg -n "Command::new|unsafe\s*\{|transmute"
rg -n "format!\(.*(SELECT|INSERT|UPDATE)"
rg -n "dispatcher|dptree|filter_command|filter_message"
rg -n "parse_mode|Html|MarkdownV2"
rg -n "is_admin|admin_ids|ADMIN"
```
