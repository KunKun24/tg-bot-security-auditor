#!/usr/bin/env python3
"""Validate a findings.json produced by the audit against assets/findings.schema.json.

Uses jsonschema when available, otherwise falls back to a dependency-free
structural check that covers every constraint the report actually relies on.

Usage:
    python3 scripts/validate_findings.py findings.json [--schema assets/findings.schema.json]
        [--allow-missing-paths]   skip the "path exists in this tree" check (for example documents)
Exit code 0 = valid, 1 = invalid, 2 = unusable input.
"""

import json
import os
import re
import sys

SEVERITIES = {"Critical", "High", "Medium", "Low", "Informational"}
PRIORITIES = {"P0", "P1", "P2", "P3"}
STATUSES = {"CONFIRMED", "POTENTIAL", "NEEDS-VALIDATION", "OBSERVATION"}
CONFIDENCES = {"High", "Medium", "Low"}
DOMAINS = {
    "transport", "identity-authz", "injection", "payments", "database",
    "files-network", "dependencies", "deployment", "performance", "quality",
}
COVERAGE = {"Reviewed", "Finding", "N/A", "Not reviewed"}

errors = []


def err(msg):
    errors.append(msg)


def structural_check(doc, schema, repo_root, allow_missing=False):
    if doc.get("schema_version") != "1.0":
        err("schema_version must be '1.0'")
    audit = doc.get("audit")
    if not isinstance(audit, dict):
        return err("audit is missing")
    for key in ("project", "date", "mode"):
        if not audit.get(key):
            err(f"audit.{key} is required")
    if audit.get("mode") not in {"lite", "full", "re-audit"}:
        err(f"audit.mode {audit.get('mode')!r} not in lite/full/re-audit")
    if not audit.get("commit"):
        err("audit.commit is null — reports without an anchor are not reproducible")
    if not audit.get("dirty") in (True, False, None):
        err("audit.dirty must be boolean or null")
    if audit.get("dirty") is True:
        err("audit.dirty is true — commit or stash before auditing, or say so in limitations")

    findings = doc.get("findings")
    if not isinstance(findings, list):
        return err("findings must be an array")
    seen_ids, seen_fp = set(), set()
    for i, f in enumerate(findings):
        where = f"findings[{i}]"
        if not isinstance(f, dict):
            err(f"{where} is not an object")
            continue
        fid = f.get("id", "")
        if not re.match(r"^F-\d{3,}$", str(fid)):
            err(f"{where}.id {fid!r} must look like F-001")
        if fid in seen_ids:
            err(f"duplicate finding id {fid}")
        seen_ids.add(fid)
        for key in ("severity", "priority", "status", "confidence"):
            if f.get(key) not in {"severity": SEVERITIES, "priority": PRIORITIES,
                                  "status": STATUSES, "confidence": CONFIDENCES}[key]:
                err(f"{where}.{key} {f.get(key)!r} invalid")
        fp = f.get("fingerprint")
        if fp is not None:
            if not re.match(r"^sha256:[a-f0-9]{64}$", str(fp)):
                err(f"{where}.fingerprint malformed")
            elif fp in seen_fp:
                err(f"{where}.fingerprint duplicates another finding")
            seen_fp.add(fp)
        loc = f.get("location")
        if not isinstance(loc, dict) or not loc.get("path"):
            err(f"{where}.location.path is required")
        else:
            lines = loc.get("lines")
            if lines is not None and not re.match(r"^\d+(-\d+)?$", str(lines)):
                err(f"{where}.location.lines {lines!r} must be 'N' or 'N-M'")
            if repo_root and not allow_missing:
                target = os.path.join(repo_root, loc["path"])
                if not os.path.exists(target):
                    err(f"{where}.location.path {loc['path']!r} does not exist in the repo")
        for key in ("impact", "remediation"):
            if len(str(f.get(key, ""))) < 3:
                err(f"{where}.{key} is required and must be substantive")
            if "see report" in str(f.get(key, "")).lower():
                err(f"{where}.{key} must stand alone, not defer to the report")
        cwe = f.get("cwe")
        if cwe is not None and not re.match(r"^CWE-\d+$", str(cwe)):
            err(f"{where}.cwe malformed")
        status = f.get("status")
        if status == "CONFIRMED" and not f.get("evidence"):
            err(f"{where}: CONFIRMED requires evidence")
        if status == "CONFIRMED" and f.get("confidence") != "High":
            err(f"{where}: CONFIRMED with confidence != High — downgrade to POTENTIAL or justify")
        if status == "POTENTIAL" and f.get("confidence") == "High":
            err(f"{where}: POTENTIAL with High confidence — either confirm it or set Medium/Low")

    coverage = doc.get("coverage")
    if not isinstance(coverage, list) or not coverage:
        err("coverage must be a non-empty array")
    else:
        seen = set()
        for c in coverage:
            if c.get("domain") not in DOMAINS:
                err(f"coverage.domain {c.get('domain')!r} not in the domain set")
            if c.get("domain") in seen:
                err(f"coverage.domain {c.get('domain')!r} listed twice")
            seen.add(c.get("domain"))
            if c.get("status") not in COVERAGE:
                err(f"coverage {c.get('domain')}: status {c.get('status')!r} invalid")
        if "Not reviewed" not in {c.get("status") for c in coverage}:
            print("note: no 'Not reviewed' entries — confirm coverage really was complete")


def _load_validator(jsonschema, schema_path):
    """Return a validator instance, or None when unavailable.

    Tolerates old or partial jsonschema builds: some environments ship a stub
    without Draft202012, and vendored copies vary by version.
    """
    if jsonschema is None or not os.path.exists(schema_path):
        return None
    try:
        with open(schema_path, encoding="utf-8") as fh:
            schema = json.load(fh)
        cls = getattr(jsonschema, "Draft202012Validator", None)
        if cls is None:
            from jsonschema import validators  # type: ignore

            cls = validators.validator_for(schema)
        return cls(schema)
    except Exception as exc:  # noqa: BLE001 - any failure falls back to structural checks
        print(f"note: jsonschema unavailable ({exc}); using structural checks only")
        return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    doc_path = args[0]
    schema_path = "assets/findings.schema.json"
    if "--schema" in sys.argv:
        schema_path = sys.argv[sys.argv.index("--schema") + 1]
    try:
        with open(doc_path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read {doc_path}: {exc}")
        return 2
    repo_root = os.getcwd()

    try:
        import jsonschema  # type: ignore
    except ImportError:
        jsonschema = None

    validator = _load_validator(jsonschema, schema_path)
    if validator is not None:
        for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
            loc = ".".join(str(p) for p in e.path) or "<root>"
            err(f"{loc}: {e.message}")

    structural_check(doc, None, repo_root, allow_missing="--allow-missing-paths" in sys.argv)

    if errors:
        print(f"INVALID: {len(errors)} problem(s)")
        for e in errors:
            print(f"  - {e}")
        return 1
    n = len(doc.get("findings", []))
    print(f"VALID: {n} finding(s), coverage {len(doc.get('coverage', []))} domain(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
