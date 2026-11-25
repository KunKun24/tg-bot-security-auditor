# Node.js / TypeScript Pack

Detection: `package.json`, `pnpm-lock.yaml`, `yarn.lock`, `tsconfig.json`, `*.js/.ts/.mjs`. SDK: `telegraf`, `grammy`, `node-telegram-bot-api`.

## Dangerous API → safe replacement

| Dangerous | Why | Safe |
| --- | --- | --- |
| `eval`, `new Function`, `vm.runIn*` | code execution | no dynamic code |
| `child_process.exec/execSync` with interpolation | shell injection | `execFile`/`spawn` with arg array |
| `require(userInput)` / dynamic `import()` | arbitrary module load | static map |
| template literals into SQL / `sequelize.query` raw | injection | bound params |
| `fs.readFile(path.join(base, user))` | traversal | `path.resolve` + prefix check |
| `fetch(userUrl)` / `axios(userUrl)` | SSRF | allowlist, protocol check, no redirects or revalidate |
| `JSON.parse` on huge body | DoS | body size limit |
| `crypto.randomBytes` ok; `Math.random()` for tokens | predictable | `crypto.randomUUID` / `randomBytes` |
| `==` on tokens, `timingSafeEqual` misuse | timing | `crypto.timingSafeEqual` with equal lengths |
| `{ ...req.body }` into model | mass assignment | explicit field pick |
| `res.send(err.stack)` | disclosure | generic error |

## Telegram pitfalls

- Telegraf: middleware order is registration order; `bot.use(authMiddleware)` **must precede** `bot.command('admin')`. `ctx.from.id` is the actor, `ctx.chat.id` the conversation — code often mixes them.
- grammY: `bot.use` and `Composer`; `ctx.callbackQuery.data` is untrusted; `bot.callbackQuery(/^admin:/, ...)` regex is not authorization.
- `node-telegram-bot-api`: polling `options.polling.interval`, `autoStart`; handlers receive raw `msg` where `msg.chat.id` may differ from `msg.from.id` (anonymous admin, channel).
- Express webhook route: check `secret_token` header before parsing body, and that `express.json()` size limit is set.
- `console.log(ctx)` leaks tokens in file URLs and user data.

## Useful searches

```bash
rg -n "eval\(|new Function|vm\.run|child_process|execSync"
rg -n "query\(\`|query\(.*\+|sequelize\.query"
rg -n "fetch\(|axios\."
rg -n "bot\.use|bot\.command|bot\.on|bot\.callbackQuery"
rg -n "isAdmin|ADMIN_IDS|adminIds"
```
