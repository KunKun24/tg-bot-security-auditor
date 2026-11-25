# Framework Map

Use this to answer one question fast: **in this SDK, where does authorization normally live, and is it actually wired?** Confirm against the pinned version — behavior changes between majors.

| SDK / stack | Update entry | Middleware / hook | Authorization belongs in | Common wiring bug |
| --- | --- | --- | --- | --- |
| aiogram 3 (Python) | `Dispatcher` → `Router` → handler | `dp.update.outer_middleware`, `router.message.middleware`, `include_router` | per-handler filter (`IsAdmin()`) or shared service check | filter attached to a different router; `include_router` order puts a catch-all first |
| aiogram 2 (Python) | `Dispatcher` → `@dp.message_handler` | `dp.middleware.setup()` | filter classes on the handler | global middleware assumed to cover all routers; `states` group drift |
| python-telegram-bot v20+ | `Application.add_handler(handler, group=N)` | `TypeHandler`, `filters`, `concurrent_updates` | inside the handler callback or a wrapper callback | handler groups run independently — a "global" handler in another group does not gate this one |
| pyTelegramBotAPI (telebot) | `@bot.message_handler(func=…)` | none; `register_next_step_handler` for flows | inside handler function | registration order and `func` filters; state in memory shared across users if keyed wrongly |
| Telethon (userbot) | `@client.on(events.NewMessage(...))` | `events` filters | inside handler; session is the credential | session file committed; `chats=` filter mistaken for auth |
| Telegraf (Node) | `bot.on/command/hears` | `bot.use()` (order matters), `Composer`, `Stage` | middleware before the handler | `bot.on()` registered before `bot.use(auth)` never sees auth |
| grammY (Node) | `bot.use`, `Composer`, `bot.callbackQuery` | middleware chain with `next()` | middleware or per-handler guard | `await next()` omitted ⇒ downstream handlers silently skipped (or auth skipped depending on order) |
| node-telegram-bot-api | `bot.onText`, `bot.on('callback_query')` | none | inside the single switch | one big callback switch — one branch without a role check |
| go-telegram-bot-api | `bot.GetUpdatesChan` + `bot.Handle` | none | inside each handler | unbuffered channel drops updates; no shared auth helper ⇒ duplicated checks |
| tucnak/telebot (Go) | `bot.Handle("/cmd", …)` | `bot.Use(mw)` | middleware registered before handlers | `Use` after `Handle` has no effect on that handler |
| teloxide (Rust) | `Dispatcher` + `dptree` | `Update::filter_message().branch(...)` | a dptree branch that gates privileged branches | branch order; `filter_command` matches the command, it does not authorize |
| Telegram.Bot (C#) | `StartReceiving` + `UpdateHandler` | none built in | a service/policy called from each handler | giant `switch (update.Type)` with one unchecked admin case |
| TelegramBots (Java) | `onUpdateReceived(Update)` | none built in | service layer | shared mutable state across pool threads; `getBotUsername` mismatch routes nothing |
| Nutgram (PHP) | `Nutgram::run()` + `->onCommand` | `->middleware(Class::class)` per handler | middleware attached to the handler | middleware registered globally but handler group bypasses it |
| irazasyed/telegram-bot-sdk (PHP) | `Telegram::commandsHandler(true)` | command classes | inside `handle()` | command class resolves target user from update without role check |
| BotMan (PHP) | `hears()` / `on()` | `->middleware()` | middleware before conversation | conversation state keyed only by user, not chat |
| telegram-bot-ruby | `client.listen` with a `case message.text` block | none | inside `when` branches | `when '/admin'` with no role branch; `message.chat.id` used as actor |
| longman/php-telegram-bot | `->command()` / `->hears()` | `->middleware()` | command callback | admin helper (`->admin()`) present in another command only |

## How to verify wiring (read-only)

1. Find the registration site (`bot.use`, `include_router`, `add_handler`, `Handle`, `middleware(...)`) and record its line.
2. Find the handler's line and check the registration order between the two.
3. Look for a second path to the same effect — a callback, a job, an admin HTTP route — that skips the wrapper.
4. If the framework has no middleware concept, expect per-handler duplication; check that every copy is identical in strictness.

Record the result in the authorization matrix with `path:line` of the wiring, not just of the check.
