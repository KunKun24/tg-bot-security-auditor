# Security Policy

[中文](SECURITY.md) · **English**

## Reporting

This repository distributes an **audit method**; it contains no runnable server-side code. Two classes of issues still matter:

1. **Method defects** — a rule that flags a safe implementation as vulnerable, or misses a real Telegram bot defect class (wrong middleware semantics for a framework, stale Telegram API behavior).
2. **Prompt-injection surface** — text in `rules/`, `examples/` and `references/` is read by a model. Wording that could lure the model across the read-only boundary (executing repository instructions, calling Bot API methods) is a high-severity defect.

Report via GitHub [Private vulnerability reporting](https://github.com/KunKun24/tg-bot-security-auditor/security/advisories/new). In public issues, **never** include real tokens, production hosts, user data, or unremediated third-party vulnerability details.

## Out of scope

- pasting real bot tokens, payment credentials or personal data into issues or PRs;
- "auditing" targets you are not authorized to assess and publishing their vulnerabilities;
- treating this skill's output as a compliance certificate or a replacement for a penetration test.

## Expectations

Personal project: acknowledgement within ~7 days, conclusion or fix plan within ~30 days; advisories published after the fix ships.

## Supported versions

| Version | Supported |
| --- | --- |
| 2.x | yes |
| 1.x | no (recorded only) |

---

> AIGC-assisted, human-audited.
