# Telegram Bot Platform Audit Rules

Platform behavior evolves. Treat every statement here as a hypothesis to confirm against the project's pinned Bot API version and the actual code path.

## Update authenticity and transport

Webhook:
- Verify `secret_token` against `X-Telegram-Bot-Api-Secret-Token`, constant-time, **fail closed** (return 403; never continue processing on mismatch).
- HTTPS termination, body size cap before parsing, and framework-level request limits.
- Reverse-proxy headers (`X-Forwarded-For`, `CF-Connecting-IP`) trusted only behind known proxies; a source-IP allowlist alone is not authentication.
- Endpoint must not be reachable by arbitrary callers with a valid body; check for a debug/health path that leaks token state.
- Check `setWebhook` configuration source: is the secret generated per environment or hard-coded/shared?

Polling:
- Offset persistence (in memory across restarts ⇒ duplicates), single poller per token (multiple replicas ⇒ split updates), `update_id` dedupe, graceful shutdown, bounded retries, no `getUpdates` flood.
- Mixed webhook + polling in one deployment is a duplicate-processing hazard.

Never call live `setWebhook`, `deleteWebhook`, `getUpdates`, `getMe`, `getFile` or any other Bot API method during an audit.

## Identity and chat context

- Use immutable numeric IDs; usernames are mutable and optional; display names are user-controlled.
- These are **different principals**: `from.id`, `chat.id`, `sender_chat.id`, `callback_query.from.id`, `message.from.id`, `business_connection_id` owner, and the resource owner stored in DB.
- `from` may be absent: channel posts, anonymous admins (where the visible sender is the group), service messages, some `chat_member` updates.
- `via_bot` means an inline bot authored the visible message; the human is behind it.
- Private chat vs group vs channel changes who can trigger a command; check bot privacy mode and whether the bot receives all group messages or only commands/mentions.
- Bind every action to actor + chat + resource and re-check at execution time. Prevent replay of a callback created for one user/chat by another.

## Callback queries and keyboards

- Callback data is untrusted input even when the bot generated it; it can be forged, replayed, or stale.
- Validate: actor, chat, message, action, resource ownership, expiry, one-time use.
- `callback_data` is limited to 64 bytes — truncation produces ambiguity or collisions between actions.
- Never put secrets, prices, user IDs used for authorization, or amounts in callback data without server-side binding.
- `answerCallbackQuery` is UX only; it must not be the only place a permission check happens.
- Check stale keyboards after state changes (e.g. old "confirm" still live after `cancel`), double taps, and concurrent taps on a one-time action.

## Commands, routing and permissions

- Handler registration order, filters, middleware order, fallthrough, overlapping routes, and default handler behavior.
- Commands in private chats vs groups vs channels must be authorized independently; a command may be safe in DM and dangerous in a group.
- Admin commands, admin callbacks, and admin web routes must enforce authorization in the service/action layer, not only via a filter or a button.
- Deep links (`t.me/bot?start=payload`) carry user-controlled parameters; check parsing, length, and whether they grant anything.

## Payments and commerce

- Telegram Payments: `pre_checkout_query` must validate amount, currency, payload and availability; answer within the window.
- `successful_payment`: verify `currency`, `total_amount`, `invoice_payload` binding to the order, and provider charge identifiers (`telegram_payment_charge_id`, `provider_payment_charge_id`).
- Fulfillment must be idempotent on provider IDs; a retried update must not deliver twice.
- Stars (XTR): refund flows, `subscription_period` / `is_recurring` semantics, renewal stacking.
- Never trust a client success screen, a screenshot, or a message text as proof of payment.
- Reconcile against provider records via a read-only process; never issue refunds during audit.

## Files and media

- `getFile` result content is untrusted: validate size, type by magic bytes, decompression bounds, and storage location.
- File URLs embed the bot token — logging them leaks credentials.
- Check quota accounting, orphaned files, and whether download paths are derived from user input.
- Check media group handling (multiple messages, partial failures) and `editMessageMedia` type changes.

## Outbound messaging

- Parse-mode escaping per mode; user text must not be able to inject links, mentions, or break message structure.
- 4096 chars for text, 1024 for captions, 64 bytes for callback data, 20 MB download limit for bots.
- 429 `retry_after` respected with jittered backoff; retry storms and unbounded queues.
- Message edit/delete edge cases: "message is not modified", "message to edit not found", deleting messages the bot no longer owns.
- Check that errors from Telegram are not echoed verbatim to users (they can contain chat/user data).

## Web Apps / Mini Apps

- Backend must validate `initData` with HMAC-SHA256 per Telegram's documented procedure (`secret = HMAC_SHA256("WebAppData", bot_token)`), then check `auth_date` freshness and replay policy.
- `initDataUnsafe` is never proof of identity; it is client-supplied.
- Third-party validation via Ed25519 signature when the app is served by a third party; bot token never reaches the browser.
- Origin/CORS/CSRF boundaries, `postMessage` origin checks, session binding to the verified user, and storage of tokens in the frontend.

## Update lifecycle edge cases

- Duplicate and out-of-order delivery; ensure handlers are idempotent where they mutate state.
- `edited_message` / `edited_channel_post`: does editing re-trigger fulfillment or re-run validation?
- `chat_member` / `my_chat_member` / join requests: role changes must invalidate caches and active sessions.
- `business_connection` / `business_message`: a different principal owns the connection; verify which ID the code uses.
- Inline mode (`inline_query`, `chosen_inline_result`): results are public; check for data leakage into result text.
