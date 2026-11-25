# Code Quality and Architecture Audit Rules

- Map module boundaries, entry points, dependency direction, and shared mutable state.
- Identify duplicated security-sensitive logic (three copies of `is_admin`, two role checks that differ) and inconsistent validation between paths.
- Check exception handling: swallowed errors that skip authorization or rollback, bare `except`/`catch` around money paths, missing cleanup.
- Review type boundaries and input schemas: nullability, integer vs decimal for money, unsafe casts, unvalidated dict access into SQL.
- Check configuration validation and fail-fast behavior: missing required setting must crash at boot, not default to "open".
- Inspect tests for authorization boundaries, negative cases, duplicate events, races and failure recovery — and check whether tests assert the *absence* of a control that exists.
- Comments and docs drift from code; code is authoritative for observed behavior.
- Distinguish maintainability observations from exploitable defects, and say which is which.
- Do not recommend broad rewrites where a boundary-level improvement suffices; a rewrite request is not a finding.
