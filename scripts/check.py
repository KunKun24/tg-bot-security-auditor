#!/usr/bin/env python3
"""Repository self-check for tg-bot-security-auditor.

Dependency-free. Verifies:
  1. SKILL.md frontmatter is valid and matches the documented contract
  2. bilingual pairs exist (README / SECURITY / docs and docs/en)
  3. relative markdown links resolve
  4. no trailing whitespace, no tabs, files end with a newline
  5. required files are present
  6. the findings schema parses and covers the documented enums

Usage:
    python3 scripts/check.py [--root .]
Exit code 0 = clean, 1 = problems found.
"""

import json
import os
import re
import sys

REQUIRED = [
    "SKILL.md", "SKILL.zh.md", "README.md", "README.en.md",
    "LICENSE", "SECURITY.md", "SECURITY.en.md", "CHANGELOG.md",
    ".gitignore", "assets/findings.schema.json",
    "rules/security.md", "rules/telegram-api.md", "rules/business-logic.md",
    "rules/database.md", "rules/dependencies.md", "rules/deployment.md",
    "rules/performance.md", "rules/code-quality.md",
    "references/audit-checklist.md", "references/vulnerability-levels.md",
    "references/report-template.md", "references/threat-model.md",
    "references/authorization-matrix.md", "references/framework-map.md",
    "references/safe-commands.md", "references/findings-schema.md",
    "docs/audit-method.md", "docs/en/audit-method.md",
]

PAIRS = [
    ("README.md", "README.en.md"),
    ("SECURITY.md", "SECURITY.en.md"),
    ("SKILL.md", "SKILL.zh.md"),
    ("docs/audit-method.md", "docs/en/audit-method.md"),
]

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)

problems = []


def fail(msg):
    problems.append(msg)


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as fh:
        return fh.read()


def check_frontmatter(root):
    text = read(root, "SKILL.md")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return fail("SKILL.md: missing YAML frontmatter block")
    body = m.group(1)
    keys = {}
    for line in body.splitlines():
        if not line.strip() or line.startswith("  "):
            continue
        if ":" not in line:
            fail(f"SKILL.md frontmatter: unparseable line {line!r}")
            continue
        k, v = line.split(":", 1)
        keys[k.strip()] = v.strip()
    for req in ("name", "description", "version", "license"):
        if req not in keys:
            fail(f"SKILL.md frontmatter: missing key {req!r}")
    if keys.get("name") != "tg-bot-security-auditor":
        fail(f"SKILL.md frontmatter: name is {keys.get('name')!r}")
    desc = keys.get("description", "")
    if len(desc) < 120:
        fail("SKILL.md frontmatter: description shorter than 120 chars (too vague for routing)")
    if len(desc) > 1024:
        fail("SKILL.md frontmatter: description longer than 1024 chars")
    if "use when" not in desc.lower() and "when" not in desc.lower():
        fail("SKILL.md frontmatter: description does not state when to use the skill")


def check_pairs(root):
    for zh, en in PAIRS:
        for rel in (zh, en):
            if not os.path.exists(os.path.join(root, rel)):
                fail(f"missing bilingual file: {rel}")


def check_links(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "node_modules", "__pycache__"}]
        for name in filenames:
            if not name.endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            text = read(root, rel)
            for target in LINK_RE.findall(text):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                target = target.split("#", 1)[0]
                if not target:
                    continue
                resolved = os.path.normpath(os.path.join(dirpath, target))
                if not os.path.exists(resolved):
                    fail(f"{rel}: broken link {target!r}")


def check_whitespace(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "node_modules", "__pycache__"}]
        for name in filenames:
            if not name.endswith((".md", ".json", ".py", ".yml", ".yaml")):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            with open(path, encoding="utf-8") as fh:
                data = fh.read()
            if not data.endswith("\n"):
                fail(f"{rel}: no trailing newline")
            for i, line in enumerate(data.splitlines(), 1):
                if line != line.rstrip():
                    fail(f"{rel}:{i}: trailing whitespace")
                if "\t" in line:
                    fail(f"{rel}:{i}: tab character")


def check_required(root):
    for rel in REQUIRED:
        if not os.path.exists(os.path.join(root, rel)):
            fail(f"missing required file: {rel}")


def check_schema(root):
    rel = "assets/findings.schema.json"
    try:
        data = json.loads(read(root, rel))
    except json.JSONDecodeError as exc:
        return fail(f"{rel}: invalid JSON ({exc})")
    if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        fail(f"{rel}: unexpected $schema")
    props = data.get("properties", {})
    for key in ("schema_version", "audit", "findings", "coverage"):
        if key not in props:
            fail(f"{rel}: missing top-level property {key!r}")
    finding = props.get("findings", {}).get("items", {}).get("properties", {})
    for key in ("id", "severity", "priority", "status", "confidence", "location",
                "impact", "remediation", "fingerprint"):
        if key not in finding:
            fail(f"{rel}: findings items missing {key!r}")
    sev = finding.get("severity", {}).get("enum", [])
    for s in ("Critical", "High", "Medium", "Low", "Informational"):
        if s not in sev:
            fail(f"{rel}: severity enum missing {s}")


def main():
    root = sys.argv[sys.argv.index("--root") + 1] if "--root" in sys.argv else "."
    root = os.path.abspath(root)
    check_required(root)
    check_pairs(root)
    check_frontmatter(root)
    check_links(root)
    check_whitespace(root)
    check_schema(root)
    if problems:
        print(f"FAIL: {len(problems)} problem(s)")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"OK: {len(REQUIRED)} required files, {len(PAIRS)} bilingual pairs, links and whitespace clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
