# Language Pack Index

Detect the stack from repository evidence, then load only the matching pack(s). A monorepo may need several.

## Detection heuristics

| Evidence | Stack |
| --- | --- |
| `requirements.txt`, `pyproject.toml`, `poetry.lock`, `*.py`, `Pipfile` | `python.md` |
| `package.json`, `pnpm-lock.yaml`, `yarn.lock`, `*.ts`, `*.js`, `tsconfig.json` | `nodejs.md` |
| `composer.json`, `composer.lock`, `*.php`, `artisan` | `php.md` |
| `go.mod`, `go.sum`, `*.go` | `go.md` |
| `pom.xml`, `build.gradle(.kts)`, `*.java`, `*.kt` | `java-kotlin.md` |
| `Cargo.toml`, `Cargo.lock`, `*.rs` | `rust.md` |
| `*.csproj`, `*.sln`, `packages.lock.json`, `*.cs` | `dotnet.md` |
| `Gemfile`, `Gemfile.lock`, `*.rb` | `ruby.md` |

Mixed stacks: audit each service with its own pack, and check the boundary (e.g. PHP webhook writing to a Python worker's queue) for duplicated or divergent authorization logic.

## Telegram SDK first

For each pack, find the SDK before the generic API list:

- Python: `python-telegram-bot`, `aiogram`, `telethon`, `pyTelegramBotAPI`
- Node: `telegraf`, `grammy`, `node-telegram-bot-api`
- PHP: `irazasyed/telegram-bot-sdk`, `nutgram`, `botman`
- Go: `go-telegram-bot-api/telegram-bot-api`, `tucnak/telebot`, `paulsonofltd`-style forks
- Java/Kotlin: `rubenlagus/TelegramBots`, `kotlin-telegram-bot`
- Rust: `teloxide`, `frankenstein`
- C#: `Telegram.Bot`
- Ruby: `telegram-bot-ruby`

Then answer one question per pack: **where does authorization normally live in this SDK, and is it actually wired?** See `references/framework-map.md`.

## Pack structure

Each pack keeps four sections: detection, dangerous API → safe replacement, TG-specific pitfalls, and useful read-only searches. Add new packs in the same shape and register them here.
