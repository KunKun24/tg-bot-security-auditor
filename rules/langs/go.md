# Go Pack

Detection: `go.mod`, `go.sum`, `*.go`. SDK: `go-telegram-bot-api/telegram-bot-api`, `tucnak/telebot`, `gopkg.in/telebot`.

## Dangerous API → safe replacement

| Dangerous | Why | Safe |
| --- | --- | --- |
| `database/sql` with `fmt.Sprintf` | SQLi | placeholders (`?`, `$1`) |
| `os/exec` with `sh -c` + input | shell injection | `exec.Command(name, args...)`, no shell |
| `text/template` with user data | template injection | `html/template` for HTML; plain string for bots |
| `filepath.Join(root, userInput)` | traversal | `filepath.Clean` + `strings.HasPrefix` on abs path |
| `http.Get(userURL)` | SSRF | `&http.Client{Timeout, CheckRedirect}` + allowlist |
| `unsafe.Pointer` on untrusted lengths | memory corruption | avoid |
| `math/rand` for tokens | predictable | `crypto/rand` |
| `==` on secrets | timing | `crypto/subtle.ConstantTimeCompare` |
| ignoring `RowsAffected()` | silent no-op updates | check `n == 1` |
| `defer resp.Body.Close()` missing | leak → DoS | always close, limit read |

## Telegram pitfalls

- go-telegram-bot-api: long polling via `bot.GetUpdatesChan`; the channel may drop updates if the consumer is slow — check buffered handling and shutdown. `Update.Message.From.ID` can be nil for channel posts.
- telebot: middleware (`bot.Use`) runs in order; `tb.OnText` handlers don't imply authorization.
- Webhook handler: verify secret header before decoding; Go's `json.Decoder` on an unbounded body is a memory hazard.
- Goroutine-per-update without a semaphore is an unbounded fan-out.

## Useful searches

```bash
rg -n "fmt\.Sprintf\(.*(SELECT|INSERT|UPDATE|DELETE)"
rg -n "exec\.Command|sh\", \"-c"
rg -n "http\.Get|http\.Post|http\.Client"
rg -n "GetUpdatesChan|UpdatesChan|SetWebhook"
rg -n "IsAdmin|AdminIDs|adminIDs"
```
