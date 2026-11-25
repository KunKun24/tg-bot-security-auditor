# Ruby Pack

Detection: `Gemfile`, `Gemfile.lock`, `*.rb`, `config.ru`. SDK: `telegram-bot-ruby`, `telegram_bot`.

## Dangerous API → safe replacement

| Dangerous | Why | Safe |
| --- | --- | --- |
| `eval`, `instance_eval`, `send(user_input)` | code execution | allowlist dispatch |
| `YAML.load(user_input)` | object deserialization | `YAML.safe_load` |
| `Marshal.load` | code execution | JSON |
| backticks / `system` / `%x{}` with input | shell injection | `system(*args)` array form, `Open3.capture3` |
| string interpolation into SQL | SQLi | `where("x = ?", v)` / binds |
| `File.read(File.join(root, user))` | traversal | `File.expand_path` + prefix |
| `open(user_url)` / `Net::HTTP.get(URI(user))` | SSRF | allowlist + `URI` validation |
| `rand` for tokens | predictable | `SecureRandom` |
| `==` on secrets | timing | `ActiveSupport::SecurityUtils.secure_compare` |
| `params.permit!` / mass assignment | over-posting | explicit permit |

## Telegram pitfalls

- telegram-bot-ruby: `Telegram::Bot::Client#listen` loop; handler blocks are looked up by command — a `when 'admin'` branch with no role check is the classic bug. `message.from.id` vs `message.chat.id`.
- Rails backend: `protect_from_forgery` state for the webhook controller (it is called by Telegram, so CSRF must be skipped **deliberately** and compensated by the secret token).
- `Rails.logger.info(params)` logs the bot token and user data.
- Sidekiq jobs for fulfillment: idempotency on `telegram_payment_charge_id`, retries can double-deliver.

## Useful searches

```bash
rg -n "eval\(|instance_eval|Marshal\.load|YAML\.load"
rg -n 'system\(|%x\{|Open3'  # plus: rg -n '\x60' for backticks
rg -n "where\(.*#\{|find_by_sql"
rg -n "Telegram::Bot|listen|webhook"
rg -n "admin\?|is_admin|ADMIN"
```
