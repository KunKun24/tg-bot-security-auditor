# Safe Commands

The read-only contract is only credible if the command whitelist is concrete. Use this instead of "inspect whether the command is safe".

## Allowed

| Purpose | Command |
| --- | --- |
| Anchor | `git rev-parse HEAD`, `git status --porcelain`, `git branch --show-current`, `git log -n 20 --oneline` |
| Read history | `git show <ref>:<path>`, `git log -p -- <path>` |
| Hash | `sha256sum <lockfile>`, `shasum -a 256 <lockfile>` |
| Search | `rg`, `grep -rn`, `find` (read-only), `git grep` |
| Read | `cat`, `head`, `tail`, `wc -l`, `file`, `stat` (no write) |
| Structure | `tree -L 3`, `ls -la` |
| Manifests | `cat package.json`, `cat go.mod`, `cat composer.lock` (never `.env`) |
| Syntax only | `python -m py_compile` **into a temp dir you create outside the repo**, `node --check`, `php -l`, `go vet` (verify it does not write `go.sum`; prefer `GOFLAGS=-mod=readonly go vet ./...`), `cargo check` writes `target/` — **do not run** |
| Existing scans | read output files the user already produced |

Syntax checks that emit artifacts (compilers, `cargo check`, `dotnet build`, `composer install`) are **out of scope**. Prefer reading code.

## Forbidden

| Command class | Why |
| --- | --- |
| `npm/pip/composer/go get/cargo add` (install, update) | mutates environment and lockfiles |
| `migrate`, `db push`, `seed`, `fixtures load` | mutates database |
| `systemctl start/restart`, `docker compose up`, `pm2 start` | starts services, may contact Telegram |
| `python main.py`, `node bot.js`, `go run .` | runs the bot; may poll and consume updates |
| `pytest`, `npm test`, `go test ./...` | project scripts, may hit network or DB; only with explicit user permission and a non-production profile |
| `curl https://api.telegram.org/...` | live Bot API call |
| `curl` to project endpoints | may mutate state or leak tokens |
| `git checkout/reset/clean/stash` | changes working tree |
| `chmod`, `chown`, `mv`, `rm`, `>` redirects into the repo | writes |

## If a check needs state change

Do not run it. Write the manual procedure into the finding:

```text
Verification (manual, by the owner):
1. Take a DB snapshot or use a staging copy.
2. Create user A and user B; give A a card.
3. Issue two concurrent redeem requests for A's card.
4. Expect exactly one success and one "already redeemed".
5. If both succeed, invariant violated; attach row state before/after.
```

## Substitution table

| Wanted | Instead |
| --- | --- |
| Run the bot to see routing | read dispatcher registration order |
| Test the webhook | read the handler's first lines and the proxy config |
| Check DB constraints | read migrations/schema, not `\d` on production |
| Verify dependency CVE | read lockfile version + advisory DB, cite lookup date |
| Prove a race | reason from isolation level and SQL shape; propose an isolated fixture |
| Confirm `initData` | reimplement HMAC in a scratch script with a **test** token, never the live one |

## Token handling

- Never place a token on a command line (shell history, process list, logs).
- Never `cat .env`. Read the key names with `rg -n "TOKEN|SECRET|KEY" .env.example` and report only names.
- If a token is found committed, report file + line + "redacted" and recommend rotation; do not verify it against the API.
