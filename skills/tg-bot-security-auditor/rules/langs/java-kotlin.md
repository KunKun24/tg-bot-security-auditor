# Java / Kotlin Pack

Detection: `pom.xml`, `build.gradle(.kts)`, `*.java`, `*.kt`. SDK: `rubenlagus/TelegramBots`, `kotlin-telegram-bot`, raw `HttpClient` to Bot API.

## Dangerous API → safe replacement

| Dangerous | Why | Safe |
| --- | --- | --- |
| `ObjectInputStream.readObject`, `XMLDecoder` | deserialization RCE | JSON with explicit types |
| `Runtime.exec(String)`, `ProcessBuilder("sh","-c",input)` | shell injection | argument arrays, no shell |
| `Statement.execute(sql + input)` | SQLi | `PreparedStatement` |
| `ScriptEngine.eval`, `SpEL`, `OGNL` on input | expression injection | no dynamic expressions |
| `new File(base + input)` | traversal | `Path.resolve().normalize()` + `startsWith` |
| `URL(userInput).openConnection()` | SSRF | allowlist + resolved IP check |
| `MessageDigest` for passwords w/o salt/iterations | weak | bcrypt/argon2 |
| `==` / `equals` on secrets | timing | `MessageDigest.isEqual` |
| `@PreAuthorize` missing on admin controller | authz gap | enforce in service layer |
| `application.properties` with secrets committed | leak | env injection |

## Telegram pitfalls

- TelegramBots: `TelegramLongPollingBot.onUpdateReceived` is called from a pool; shared mutable state without synchronization is a race. `getBotUsername` mismatch breaks command routing.
- `SendMessage` parse mode `HTML` with unescaped user text — same injection class as XSS but in Telegram.
- Spring backend for Mini App: `initData` HMAC check must be in a filter/interceptor before controllers; `@CrossOrigin(origins="*")` with credentials is a real finding.
- Kotlin coroutines: `GlobalScope.launch` per update without a dispatcher limit is unbounded concurrency.

## Useful searches

```bash
rg -n "readObject|XMLDecoder|ScriptEngine|SpelExpression"
rg -n "Runtime\.getRuntime|ProcessBuilder"
rg -n "createStatement|executeQuery\(|executeUpdate\("
rg -n "onUpdateReceived|setWebhook|SendMessage"
rg -n "isAdmin|is_admin|ADMIN_ID"
```
