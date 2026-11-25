# Findings JSON

Machine-readable companion to the report. Schema: `assets/findings.schema.json` (JSON Schema 2020-12).

## Why

- CI can fail a build on `severity >= High && status == CONFIRMED`.
- Re-audits diff by `fingerprint`, so fixed issues do not resurface as "new".
- Dashboards and tickets can consume it without parsing Markdown.

## Shape

```json
{
  "schema_version": "1.0",
  "audit": {
    "project": "mybot",
    "commit": "9f3c2ab…",
    "branch": "main",
    "dirty": false,
    "date": "2026-11-25T12:00:00+08:00",
    "mode": "full",
    "languages": ["python"],
    "frameworks": ["aiogram 3.15"],
    "advisory_lookup": { "performed": false, "date": null, "sources": [] },
    "scope": {
      "included": ["app/", "deploy/", "pyproject.toml"],
      "excluded": [{ "path": "vendor/", "reason": "third-party copy, not maintained here" }]
    }
  },
  "findings": [
    {
      "id": "F-001",
      "title": "Callback credits own balance without entitlement check",
      "severity": "High",
      "priority": "P1",
      "status": "CONFIRMED",
      "confidence": "High",
      "category": "payments",
      "cwe": "CWE-639",
      "fingerprint": "sha256:…64 hex…",
      "location": { "path": "app/handlers/pay.py", "lines": "41-58", "symbol": "on_pay_callback" },
      "source": "callback_query.data",
      "sink": "services.balance.credit",
      "control_gap": "decoded user_id never compared with callback.from.id",
      "preconditions": ["attacker can press a button in their own chat"],
      "evidence_cmd": "rg -n \"credit\\(\" app/",
      "impact": "arbitrary self-credit",
      "remediation": "bind payload to actor, verify at service layer",
      "verification": "two-user fixture in isolated copy",
      "authorization_row": "A-03"
    }
  ],
  "coverage": [
    { "domain": "transport", "status": "Finding", "notes": "webhook secret verified" },
    { "domain": "dependencies", "status": "Not reviewed", "notes": "no network, advisory lookup declined" }
  ],
  "limitations": ["runtime configuration not available", "no staging DB"]
}
```

## Field rules

- `severity`, `status`, `confidence` must match section 7 of the report **exactly**; the report is the human view of the same data.
- `fingerprint` = `sha256(path + "::" + symbol + "::" + cwe)`; omit `symbol` as empty string when unknown. Keep it stable across renames only if the defect is unchanged — a moved file is a new fingerprint, and that is acceptable.
- `evidence_cmd` must be a command that was actually run or is safe to run (`references/safe-commands.md`).
- `impact` and `remediation` are required and free-text; do not put "see report" in them.
- `coverage` must contain every domain in the enum at most once; `Not reviewed` is a valid and honest answer.

## Validation

```bash
python3 -c "import json,sys; json.load(open('findings.json'))"          # syntax
python3 scripts/validate_findings.py findings.json                      # schema (repo copy)
```

If no JSON Schema tool is available offline, at minimum check: required keys present, enums in range, `location.path` exists in the audited tree, `lines` numeric range, ids unique, fingerprints well-formed.
