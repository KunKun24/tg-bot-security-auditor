# 收录与提交说明

本页记录本仓库如何满足 [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin)（dshmarket / awesome-dsh-plugin.com）的收录标准，以及提交收录申请时使用的字段、截图与链接。日常使用者不需要读这一页。

## 一、收录条件对照

| 市场要求 | 本仓库的满足方式 |
|---|---|
| 仓库为真实可用的 DSH 插件 | `package.json` 声明 `dsh.bundle.patch`，`cordis.patch.yml` 注册 `tg-bot-security-auditor`，`index.js` 通过 `applyFilesystemProvider()` 内嵌 `skills/` |
| 有真实代码，不是空壳 | `index.js` + 技能本体 40+ 文件（8 域规则、9 语言对照、8 类示例、JSON Schema） |
| 仓库创建满 1 天 | CI 按 `created_at` 计算，不足时 gate 会提示并自动重跑 |
| 带 `dsh-plugin` topic | 已在仓库设置中添加 |
| 描述属实 | 描述与 README 的「这是什么 / 它不做什么」一致，不承诺自动化修复或合规认证 |
| 条目 YAML 的 `url` 与仓库一致 | `https://github.com/KunKun24/tg-bot-security-auditor` |

## 二、目录条目（`data/plugins/KunKun24__tg-bot-security-auditor.yml`）

向收录仓库提 PR 时只新增这一个文件，不要手改 README（它由 CI 生成）：

```yaml
url: https://github.com/KunKun24/tg-bot-security-auditor
name: KunKun24/tg-bot-security-auditor
category: skill
description:
  en: "Read-only security, authorization and business-logic audit for Telegram Bot repositories, with file:line evidence and a DSH skill bundle that never modifies the audited project."
  zh: "只读审计 Telegram Bot 仓库的 DSH 技能包，覆盖授权、支付、注入与业务逻辑，结论带 文件:行号 证据，从不改动被审项目。"
```

- `description.en` 是必填项，写成完整句子，包含冒号时整体加引号。
- 可选项 `icon`：目前留空，市场侧会回落到仓库头像；如后续单独托管图标 URL 再补。
- `category` 取值来自市场枚举，`skill` 为技能包分类。

## 三、截图清单

收录 CI 会从 README 抓取图片，下面五张即市场详情页使用的素材，均存放在 `docs/images/`：

| 文件 | 尺寸 | 用途 | 地址 |
|---|---|---|---|
| `cover.png` | 1600×840 | 详情页头图、社交分享卡片 | https://raw.githubusercontent.com/KunKun24/tg-bot-security-auditor/main/docs/images/cover.png |
| `audit-flow.png` | 1700×800 | 七阶段流程 + 四档结论说明 | https://raw.githubusercontent.com/KunKun24/tg-bot-security-auditor/main/docs/images/audit-flow.png |
| `finding-card.png` | 1440×700 | 单条发现的字段长什么样（真实示例 F-001） | https://raw.githubusercontent.com/KunKun24/tg-bot-security-auditor/main/docs/images/finding-card.png |
| `terminal.png` | 1440×700 | 真实终端输出：仓库自检 + findings 校验 | https://raw.githubusercontent.com/KunKun24/tg-bot-security-auditor/main/docs/images/terminal.png |
| `icon.png` | 512×512 | 图标候选，可用于市场 `icon` 字段 | https://raw.githubusercontent.com/KunKun24/tg-bot-security-auditor/main/docs/images/icon.png |

截图规则：只用真实界面与真实命令输出，不摆拍、不改数字；`finding-card.png` 的内容与 `skills/tg-bot-security-auditor/assets/findings.example.json` 中的 F-001 完全一致。

## 四、链接清单

| 名称 | 地址 |
|---|---|
| 仓库 | https://github.com/KunKun24/tg-bot-security-auditor |
| 插件市场详情页（收录后） | https://awesome-dsh-plugin.com/plugins/KunKun24/tg-bot-security-auditor |
| 条目 PR | https://github.com/awesome-dsh-plugin/awesome-dsh-plugin/pulls |
| 中文文档 | https://github.com/KunKun24/tg-bot-security-auditor/blob/main/README.md |
| English docs | https://github.com/KunKun24/tg-bot-security-auditor/blob/main/README.en.md |
| 审计方法论 | https://github.com/KunKun24/tg-bot-security-auditor/blob/main/docs/audit-method.md |
| 问题反馈 | https://github.com/KunKun24/tg-bot-security-auditor/issues |

## 五、安装方式（收录后展示）

```bash
dsh plugin --profile web add tg-bot-security-auditor   # npm 发布后
dsh plugin --profile web add github:KunKun24/tg-bot-security-auditor
```

`dsh plugin add` 安装后，宿主会读取包内的 `dsh.bundle.patch` 并自动把 `tg-bot-security-auditor` 加入 profile 的 bundle 列表，因此无需手工编辑配置。

## 六、提交收录申请（PR 正文模板）

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

## 七、安全披露

本技能只做本地静态审计，不上传代码、不发起外部请求（依赖漏洞查询需显式许可）。发现技能自身的规则错误、误报或漏报，请走仓库 issue，附上：被审语言与框架、规则文件名、能复现的最短代码片段、期望结论。不要在公开 issue 里贴真实项目的密钥、token 或用户数据。
