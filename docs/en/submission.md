# Submission notes

This page records how the repository satisfies the listing requirements of [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin) (dshmarket / awesome-dsh-plugin.com), plus the fields, screenshots and links used in the submission. Regular users do not need to read it.

## 1. Requirement checklist

| Market requirement | How this repository satisfies it |
|---|---|
| A real, working DSH plugin | `package.json` declares `dsh.bundle.patch`; `cordis.patch.yml` registers `tg-bot-security-auditor`; `index.js` exposes `skills/` through `applyFilesystemProvider()` |
| Real code, not a stub | `index.js` plus 40+ files of skill content (8 domain rules, 9 language maps, 8 examples, JSON Schema) |
| Repository at least one day old | The gate computes age from `created_at`; it posts a hint and re-runs automatically while the repo is younger |
| Carries the `dsh-plugin` topic | Set on the repository |
| Honest description | Matches the "What it is / What it does not do" sections; promises no automated fixes and no compliance certification |
| Entry YAML `url` equals the repo | `https://github.com/KunKun24/tg-bot-security-auditor` |

## 2. Catalog entry (`data/plugins/KunKun24__tg-bot-security-auditor.yml`)

The listing PR adds exactly one file; never edit the catalog README by hand (CI generates it):

```yaml
url: https://github.com/KunKun24/tg-bot-security-auditor
name: KunKun24/tg-bot-security-auditor
category: skill
description:
  en: 'Read-only security, authorization and business-logic audit of Telegram Bot repositories in any language. Produces file:line findings with severity, confidence and a reproducible read-only command; ships rules for 8 audit domains, 9 language sink tables, a threat model, an authorization matrix and a findings JSON schema that validates in CI.'
  zh: '只读审计 Telegram Bot 仓库的安全、授权与业务逻辑问题，语言不限。每条发现都锚定 file:line，标注严重度、置信度并附可复现的只读命令；内置 8 个审计域规则、9 种语言的危险 API 对照、威胁模型、授权矩阵，以及可在 CI 校验的 findings JSON Schema。'
icon: https://raw.githubusercontent.com/KunKun24/tg-bot-security-auditor/main/docs/images/icon.png
tarball: https://github.com/KunKun24/tg-bot-security-auditor/releases/latest/download/tg-bot-security-auditor.tgz
```

- `description.en` is mandatory, written as a full sentence, quoted as a whole when it contains a colon.
- `icon` points at the 512×512 PNG inside the repository; market cards use it directly.
- `tarball` points at the `tg-bot-security-auditor.tgz` uploaded by hand to the `v2.1.0` release (the asset name carries no version, so `latest/download/` never 404s after a release); a prebuilt install skips the build-approval step.
- `category` comes from the market's enum; `skill` is the skill-bundle category.

## 3. Screenshots

The catalog CI picks images out of the README. These five assets under `docs/images/` are what the detail page uses:

| File | Size | Purpose | URL |
|---|---|---|---|
| `cover.png` | 1600×840 | detail-page hero, social card | https://raw.githubusercontent.com/KunKun24/tg-bot-security-auditor/main/docs/images/cover.png |
| `audit-flow.png` | 1700×800 | seven phases plus the four verdicts | https://raw.githubusercontent.com/KunKun24/tg-bot-security-auditor/main/docs/images/audit-flow.png |
| `finding-card.png` | 1440×700 | what one finding looks like (real example F-001) | https://raw.githubusercontent.com/KunKun24/tg-bot-security-auditor/main/docs/images/finding-card.png |
| `terminal.png` | 1440×700 | real terminal output: self-check and findings validation | https://raw.githubusercontent.com/KunKun24/tg-bot-security-auditor/main/docs/images/terminal.png |
| `icon.png` | 512×512 | icon candidate for the `icon` field | https://raw.githubusercontent.com/KunKun24/tg-bot-security-auditor/main/docs/images/icon.png |

Screenshot rules: only real UI and real command output, nothing staged, no edited numbers; `finding-card.png` matches F-001 in `skills/tg-bot-security-auditor/assets/findings.example.json` exactly.

## 4. Links

| Name | URL |
|---|---|
| Repository | https://github.com/KunKun24/tg-bot-security-auditor |
| Market detail page (once listed) | https://awesome-dsh-plugin.com/plugins/KunKun24/tg-bot-security-auditor |
| Listing PR | https://github.com/awesome-dsh-plugin/awesome-dsh-plugin/pulls |
| Chinese docs | https://github.com/KunKun24/tg-bot-security-auditor/blob/main/README.md |
| English docs | https://github.com/KunKun24/tg-bot-security-auditor/blob/main/README.en.md |
| Audit methodology | https://github.com/KunKun24/tg-bot-security-auditor/blob/main/docs/en/audit-method.md |
| Issues | https://github.com/KunKun24/tg-bot-security-auditor/issues |

## 5. Install command shown in the market

```bash
dsh plugin --profile web add tg-bot-security-auditor   # once published to npm
dsh plugin --profile web add github:KunKun24/tg-bot-security-auditor
```

After `dsh plugin add`, the host reads the package's `dsh.bundle.patch` and appends `tg-bot-security-auditor` to the profile's bundle list automatically, so no manual configuration is needed.

## 6. PR body template

```markdown
### Add KunKun24/tg-bot-security-auditor

- Repo: https://github.com/KunKun24/tg-bot-security-auditor
- Category: skill
- What it does: read-only security / authorization / business-logic audit for Telegram Bot repositories, delivered as a DSH skill bundle. Findings carry file:line evidence and a reproducible read-only command; the audited project is never modified.
- Bundle declaration: package.json → dsh.bundle.patch → cordis.patch.yml (id: tg-bot-security-auditor), index.js registers skills/ via applyFilesystemProvider().
- Topics: dsh-plugin, deepseek-harness, telegram, security-audit
- License: MIT
- Note: repository was created on 2026-11-25; the age gate self-clears once the repo is one day old.
```

## 7. Security disclosure

The skill audits locally and statically: it uploads no code and makes no outbound requests (advisory lookups require explicit permission). To report a wrong, missing or noisy rule, open an issue with the audited language and framework, the rule file, the shortest snippet that reproduces the result, and the expected verdict. Never paste real secrets, tokens or user data into a public issue.
