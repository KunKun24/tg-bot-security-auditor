# PHP Pack

Detection: `composer.json`, `composer.lock`, `*.php`, `artisan`, `index.php`. SDK: `irazasyed/telegram-bot-sdk`, `nutgram`, `botman`, raw `file_get_contents` calls to Bot API.

## Dangerous API → safe replacement

| Dangerous | Why | Safe |
| --- | --- | --- |
| `eval`, `assert($_POST)`, `create_function` | code execution | none |
| `unserialize($input)` | object injection → POP chain | `json_decode` |
| `system/exec/shell_exec/passthru/popen` with input | shell injection | `proc_open` with array, `escapeshellarg` |
| string concatenation into `mysqli_query` | SQLi | prepared statements (PDO with `ATTR_EMULATE_PREPARES=false`) |
| `include/require` user path | LFI/RFI | allowlist map |
| `file_get_contents($userUrl)` | SSRF | allowlist, curl with protocol/host checks |
| `move_uploaded_file` without type check | upload abuse | magic-byte check, store outside webroot |
| `md5/sha1` for passwords | weak | `password_hash`/`password_verify` |
| `==` on hashes | type juggling (`0e...`) | `hash_equals` |
| `extract($_GET)` | variable injection | explicit reads |
| `display_errors=On` in prod | disclosure | off, log instead |

## Telegram pitfalls

- Raw cURL to `api.telegram.org/bot<token>/...` hard-codes the token in source or DB; check it is not committed and not in error logs.
- Webhook script: `file_get_contents('php://input')` then `json_decode` — verify `X-Telegram-Bot-Api-Secret-Token` **before** processing, and that the endpoint is not indexed/public with a permissive `.htaccess`.
- `$_GET['id']` / `$_POST` used directly as target user ID in an admin action = IDOR; Telegram identity must come from the verified update.
- Shared hosting: `error_log` and backup `.sql` files inside webroot are commonly exposed.
- Nutgram/Irazasyed middleware: confirm the middleware is attached to the route/command group, not only registered globally in a boot method that runs later.

## Useful searches

```bash
rg -n "unserialize\(|eval\(|system\(|exec\(|shell_exec"
rg -n 'mysqli_query|->query\(|PDO'
rg -n "php://input|X-Telegram-Bot-Api-Secret-Token"
rg -n '\$_GET|\$_POST|\$_REQUEST'
rg -n "display_errors|APP_DEBUG"
```
