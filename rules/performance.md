# Performance, Reliability and Resilience Audit Rules

## Event loop and blocking work

- Blocking calls inside async handlers / event loops: sync HTTP, sync DB driver, `sleep`, heavy CPU (hashing, image processing, PDF), file IO.
- Work done synchronously before acknowledging an update, delaying the webhook response and causing Telegram retries.
- Unbounded task creation (`create_task` per update) with no pool or backpressure.

## Timeouts, retries and backoff

- Every outbound call has an explicit timeout; database pools have acquire timeouts.
- Retries are bounded, exponential, jittered; no retry on non-idempotent operations without an idempotency key.
- Telegram 429 `retry_after` honored; no parallel flood after a rate limit.
- Timeouts on `sendMessage` / `editMessageText` handled without duplicating messages.

## Queues and state growth

- Unbounded in-memory state: conversations, sessions, caches keyed by user, uploaded files.
- Queue depth limits, dead-letter handling, worker pool sizing, graceful shutdown draining.
- Memory growth from retained message entities, media caches, per-chat locks.

## Resilience

- Circuit breakers / degradation for external providers (payment, AI upstream, storage).
- Partial failure handling: message sent but DB write failed; payment recorded but fulfillment failed.
- Idempotent handlers for duplicate updates; ordering assumptions between webhook and worker.
- Graceful shutdown: in-flight updates finished or re-queued; polling offset saved.

## Limits and observability

- Rate limits per user, chat, command, IP and expensive operation; global send limits.
- Structured logs with update/correlation IDs, metrics, alerting — without leaking tokens or personal data.
- Do not benchmark production or run load tests against live services; recommend isolated staging with explicit limits.
