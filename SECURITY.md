# 安全策略

**中文** · [English](SECURITY.en.md)

## 报告问题

本仓库是**审计方法**的分发物，自身不含可执行的服务端代码。仍然有两类问题值得报告：

1. **方法缺陷**：某条规则会把安全实现误判为漏洞，或者漏掉一类真实存在的 Telegram Bot 缺陷（例如某个框架的中间件语义写错、某条 Telegram API 行为过时）。
2. **提示词注入面**：`rules/`、`examples/`、`references/` 中的文本会被模型读取；如果某处措辞会诱导模型越过只读边界（例如暗示可以执行仓库内指令、可以调用 Bot API），属于高危缺陷。

请通过 GitHub 的 [Private vulnerability reporting](https://github.com/KunKun24/tg-bot-security-auditor/security/advisories/new) 提交，或开 issue 时**不要**附带真实 token、生产域名、用户数据与未修复的第三方漏洞细节。

## 我们不接受的做法

- 在 issue 或 PR 中粘贴真实 bot token、支付凭据、用户隐私数据；
- 用本 skill 对未授权目标做「审计」并公开其漏洞细节；
- 把本 skill 的输出当作合规证明或渗透测试报告的替代品。

## 处理预期

维护者为个人项目，通常 7 天内确认收到，30 天内给出结论或修复计划；安全公告会在修复发布后公开。

## 支持范围

| 版本 | 支持 |
| --- | --- |
| 2.x | 是 |
| 1.x | 否（仅记录，不再修） |

---

> 本文档为 AIGC 辅助生成、已人工审计。
