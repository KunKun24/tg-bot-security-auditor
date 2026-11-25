# C# / .NET Pack

Detection: `*.csproj`, `*.sln`, `packages.lock.json`, `*.cs`. SDK: `Telegram.Bot`.

## Dangerous API → safe replacement

| Dangerous | Why | Safe |
| --- | --- | --- |
| `BinaryFormatter`, `LosFormatter`, `NetDataContractSerializer` | deserialization RCE | System.Text.Json |
| `Type.GetType(userInput)`, `Activator.CreateInstance` | type confusion | allowlist |
| `Process.Start("cmd", "/c " + input)` | shell injection | `ProcessStartInfo.ArgumentList` |
| `SqlCommand` with concatenation | SQLi | `Parameters.AddWithValue` |
| `Path.Combine(root, user)` | traversal | `Path.GetFullPath` + prefix |
| `HttpClient.GetAsync(userUrl)` | SSRF | allowlist, `SocketsHttpHandler.AllowAutoRedirect=false` |
| `MD5`/`SHA1` passwords | weak | `Rfc2898DeriveBytes` / bcrypt |
| `==` on tokens | timing | `CryptographicOperations.FixedTimeEquals` |
| `[Authorize]` missing on admin controller | authz gap | policy at service layer |
| `app.UseDeveloperExceptionPage()` in prod | disclosure | off |

## Telegram pitfalls

- Telegram.Bot: `UpdateHandler` receives updates from the polling loop; exceptions in a handler can kill the loop if not caught. `ITelegramBotClient` is thread-safe but your state is not.
- `message.From` can be null; use `message.From?.Id`, and treat `message.SenderChat` as a distinct principal.
- Webhook controller: verify `X-Telegram-Bot-Api-Secret-Token` in a filter before model binding; `[FromBody]` with default size limits.
- `Html` parse mode with `WebUtility.HtmlEncode` on user content; note Telegram's HTML subset differs from browser HTML.

## Useful searches

```bash
rg -n "BinaryFormatter|Activator\.CreateInstance|Type\.GetType"
rg -n "Process\.Start|ProcessStartInfo"
rg -n "new SqlCommand|ExecuteNonQuery|ExecuteReader"
rg -n "HandleUpdateAsync|SetWebhook|SendTextMessage"
rg -n "IsAdmin|AdminIds|ADMIN"
```
