#!/usr/bin/env python3
"""Repository self-check for the tg-bot-security-auditor DSH bundle.

Dependency-free. Verifies:
  1. the plugin manifest (package.json) is valid and consistent with the
     bundle patch (cordis.patch.yml) and with the bundled skill
  2. every path listed in the manifest's `files` exists
  3. the skill's SKILL.md frontmatter matches the documented contract
  4. bilingual pairs exist (README / SECURITY / SKILL / docs and docs/en)
  5. every relative markdown link resolves
  6. no trailing whitespace, no tabs, files end with a newline
  7. required files are present
  8. the findings schema parses and covers the documented enums

Usage:
    python3 scripts/check.py [--root .]
Exit code 0 = clean, 1 = problems found.
"""

import json
import os
import re
import sys

NAME = "tg-bot-security-auditor"
SKILL_DIR = f"skills/{NAME}"

REQUIRED = [
    "package.json", "index.js", "cordis.patch.yml",
    "examples/config.example.yml",
    f"{SKILL_DIR}/SKILL.md", f"{SKILL_DIR}/SKILL.zh.md",
    "README.md", "README.en.md",
    "LICENSE", "SECURITY.md", "SECURITY.en.md", "CHANGELOG.md",
    ".gitignore", f"{SKILL_DIR}/assets/findings.schema.json",
    f"{SKILL_DIR}/assets/findings.example.json",
    f"{SKILL_DIR}/rules/security.md", f"{SKILL_DIR}/rules/telegram-api.md",
    f"{SKILL_DIR}/rules/business-logic.md", f"{SKILL_DIR}/rules/database.md",
    f"{SKILL_DIR}/rules/dependencies.md", f"{SKILL_DIR}/rules/deployment.md",
    f"{SKILL_DIR}/rules/performance.md", f"{SKILL_DIR}/rules/code-quality.md",
    f"{SKILL_DIR}/rules/langs/_index.md",
    f"{SKILL_DIR}/references/audit-checklist.md",
    f"{SKILL_DIR}/references/vulnerability-levels.md",
    f"{SKILL_DIR}/references/report-template.md",
    f"{SKILL_DIR}/references/threat-model.md",
    f"{SKILL_DIR}/references/authorization-matrix.md",
    f"{SKILL_DIR}/references/framework-map.md",
    f"{SKILL_DIR}/references/safe-commands.md",
    f"{SKILL_DIR}/references/findings-schema.md",
    f"{SKILL_DIR}/scripts/validate_findings.py",
    "docs/audit-method.md", "docs/en/audit-method.md",
    "docs/submission.md", "docs/en/submission.md",
    "docs/images/icon.png", "docs/images/cover.png",
    "docs/images/audit-flow.png", "docs/images/finding-card.png",
    "docs/images/terminal.png",
]

PAIRS = [
    ("README.md", "README.en.md"),
    ("SECURITY.md", "SECURITY.en.md"),
    (f"{SKILL_DIR}/SKILL.md", f"{SKILL_DIR}/SKILL.zh.md"),
    ("docs/audit-method.md", "docs/en/audit-method.md"),
    ("docs/submission.md", "docs/en/submission.md"),
]

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")

problems = []


def fail(msg):
    problems.append(msg)


def read(root, rel):
    """Return file content, or "" after recording a readable problem.

    A missing file must never raise here: the caller turns it into a FAIL line.
    A traceback in CI tells the reader nothing about which file is absent.
    """
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        fail(f"cannot read {rel}: file is missing")
        return ""
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError as exc:
        fail(f"cannot read {rel}: {exc.strerror or exc}")
        return ""
    except UnicodeDecodeError:
        fail(f"cannot read {rel}: not valid UTF-8")
        return ""


def parse_frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    keys = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.startswith("  "):
            continue
        if ":" not in line:
            fail(f"frontmatter: unparseable line {line!r}")
            continue
        k, v = line.split(":", 1)
        keys[k.strip()] = v.strip()
    return keys


def check_frontmatter(root):
    rel = f"{SKILL_DIR}/SKILL.md"
    text = read(root, rel)
    if not text:
        return
    keys = parse_frontmatter(text)
    if keys is None:
        return fail(f"{rel}: missing YAML frontmatter block")
    for req in ("name", "description", "version", "license"):
        if req not in keys:
            fail(f"{rel} frontmatter: missing key {req!r}")
    if keys.get("name") != NAME:
        fail(f"{rel} frontmatter: name is {keys.get('name')!r}, expected {NAME!r}")
    desc = keys.get("description", "")
    if len(desc) < 120:
        fail(f"{rel} frontmatter: description shorter than 120 chars (too vague for routing)")
    if len(desc) > 1024:
        fail(f"{rel} frontmatter: description longer than 1024 chars")
    if "when" not in desc.lower():
        fail(f"{rel} frontmatter: description does not state when to use the skill")


def check_manifest(root):
    rel = "package.json"
    text = read(root, rel)
    if not text:
        return
    try:
        pkg = json.loads(text)
    except json.JSONDecodeError as exc:
        return fail(f"{rel}: invalid JSON ({exc})")

    for key in ("name", "version", "description", "type", "main", "files",
                "license", "repository", "peerDependencies", "dsh"):
        if key not in pkg:
            fail(f"{rel}: missing key {key!r}")
    if pkg.get("name") != NAME:
        fail(f"{rel}: name is {pkg.get('name')!r}, expected {NAME!r}")
    if not SEMVER_RE.match(str(pkg.get("version", ""))):
        fail(f"{rel}: version is not semver: {pkg.get('version')!r}")
    if pkg.get("type") != "module":
        fail(f"{rel}: type must be 'module' (index.js is ESM)")
    if len(str(pkg.get("description", ""))) < 40:
        fail(f"{rel}: description too short for a market listing")

    main = pkg.get("main")
    if main and not os.path.isfile(os.path.join(root, main)):
        fail(f"{rel}: main {main!r} does not exist")

    bundle = (pkg.get("dsh") or {}).get("bundle") or {}
    patch = bundle.get("patch")
    if not patch:
        fail(f"{rel}: dsh.bundle.patch is missing — the profile would fail to boot")
    elif not os.path.isfile(os.path.join(root, patch.lstrip("./"))):
        fail(f"{rel}: dsh.bundle.patch {patch!r} does not exist")

    for peer in pkg.get("peerDependencies") or {}:
        if peer == "@deepseek-ai/dsh-skill-filesystem":
            break
    else:
        fail(f"{rel}: peerDependencies must declare @deepseek-ai/dsh-skill-filesystem")

    for entry in pkg.get("files") or []:
        if not os.path.exists(os.path.join(root, entry)):
            fail(f"{rel}: files entry {entry!r} does not exist")

    # The bundle patch must register exactly this package under this id.
    patch_rel = str(patch or "cordis.patch.yml").lstrip("./")
    patch_text = read(root, patch_rel)
    if f"id: {NAME}" not in patch_text:
        fail(f"{patch_rel}: does not register id {NAME!r}")
    names = {f"name: '{pkg.get('name')}'", f'name: "{pkg.get("name")}"',
             f"name: {pkg.get('name')}"}
    if not any(n in patch_text for n in names):
        fail(f"{patch_rel}: does not register name {pkg.get('name')!r}")

    # The skill's own version must track the package version.
    skill_rel = f"{SKILL_DIR}/SKILL.md"
    skill_text = read(root, skill_rel)
    if skill_text:
        keys = parse_frontmatter(skill_text) or {}
        if keys.get("version") and keys["version"] != str(pkg.get("version")):
            fail(f"{skill_rel}: version {keys['version']!r} != package.json {pkg.get('version')!r}")


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
            if not name.endswith((".md", ".json", ".py", ".yml", ".yaml", ".js")):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            try:
                with open(path, encoding="utf-8") as fh:
                    data = fh.read()
            except (OSError, UnicodeDecodeError) as exc:
                fail(f"cannot read {rel}: {exc}")
                continue
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
    rel = f"{SKILL_DIR}/assets/findings.schema.json"
    text = read(root, rel)
    if not text:
        return
    try:
        data = json.loads(text)
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
    check_manifest(root)
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
    print(f"OK: {len(REQUIRED)} required files, {len(PAIRS)} bilingual pairs, "
          "manifest, links and whitespace clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
