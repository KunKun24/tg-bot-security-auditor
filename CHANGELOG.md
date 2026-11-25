# Changelog

本文件记录本 skill 的变更。版本遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## 2.0.0 — 2026-11-25

首个公开发布版本，相对 1.0 的内部草稿做了结构性重写。

### 新增

- `rules/langs/`：Python、Node.js、PHP、Go、Java/Kotlin、Rust、C#、Ruby 八种语言的高危 API 对照表，附各语言在 TG 场景下的特有坑与检索命令。
- `references/framework-map.md`：aiogram 2/3、python-telegram-bot、Telegraf、grammY、telebot、teloxide、Telegram.Bot 等框架的分发器与授权落点对照。
- `references/threat-model.md`：攻击者画像、资产清单、信任边界与排序方法，把「按清单审」变成「按风险审」。
- `references/authorization-matrix.md`：`操作 × 入口 × 鉴权位置 × 失败模式` 矩阵模板与判定规则。
- `references/safe-commands.md`：只读命令白名单 / 黑名单，替代原来含糊的「自行判断工具行为」。
- `assets/findings.schema.json` + `references/findings-schema.md`：机器可读 findings，支持进 CI 与复审计差异。
- 三种模式：Lite / Full / Re-audit，报告规模随项目大小收敛。
- 报告锚定 `commit SHA`、分支、锁文件哈希，审计可复现、可对比。
- `examples/` 扩展到 8 个可复用推理样例：回调越权、webhook 密钥、支付幂等、`initData` 校验、核销竞态、SSRF、SQL 注入、严重度校准。
- `scripts/check.py`：文档自检（frontmatter、双语文档配对、内部链接、行尾空白）。
- `scripts/validate_findings.py`：findings JSON 校验，带 jsonschema 时走真实 schema，缺依赖时降级为结构化检查。
- `assets/findings.example.json`：四态齐全的示例报告数据，CI 会校验它。
- `.github/workflows/docs.yml`：push / PR 跑自检与示例校验。

### 变更

- `SKILL.md` 收紧 `description`，补 `When not to use`，避免被非 TG 项目误触发。
- Telegram 基线补充：业务连接（`business_connection_id`）、Stars (XTR) 与订阅、`chat_member` / 加入请求、内联模式、媒体组、`edited_message`、`getFile` 下载 URL 内嵌 token、4096 字符与 parse-mode 注入。
- 严重度模型补校准样例：同一缺陷在不同上下文中如何从 Medium 上升到 High，以及严重度膨胀的常见写法。

### 移除

- 「候选即发现」的模糊表述，改为「追通之前不算发现」。
- `git diff --check` 一句自相矛盾的表述。

## 1.0.0 — 2026-11-20

内部草稿：`SKILL.md` + 8 份通用规则 + 严重度模型 + 报告模板 + 3 个示例。

---

> 本文档为 AIGC 辅助生成、已人工审计。
