# Dependency and Supply Chain Audit Rules

## Inventory

- Identify direct and transitive dependencies from manifests and lockfiles (`requirements.txt`, `poetry.lock`, `package.json` + lockfile, `composer.lock`, `go.sum`, `pom.xml`, `Cargo.lock`, `packages.lock.json`, `Gemfile.lock`).
- Record exact versions and whether the lockfile is committed; a missing lockfile means builds are unreproducible and the audit cannot pin what runs.
- Prefer existing lockfiles and any offline advisory database already present. **Do not install or update anything.**

## Risk signals

- Known vulnerable versions: cite an authoritative advisory (GHSA/CVE) with lookup date, or mark `NEEDS-VALIDATION` if online lookup was not permitted.
- Abandoned packages, typosquatting (names one character off a popular package), dependency confusion (internal names resolvable from a public registry).
- Install scripts / postinstall hooks, native binaries, prebuilt artifacts, packages pulled from git URLs or non-default registries.
- Unpinned version ranges on security-relevant packages (crypto, auth, Telegram SDK, DB driver).
- Dev dependencies leaking into production images.

## Integrity and provenance

- Registry source and integrity hashes; whether the lockfile records them.
- Reproducible build assumptions; Docker images referenced by tag only.
- Committed `node_modules`/`vendor/` directories: are they checked, and do they match the manifest?

## Judgement

- Do not label a package vulnerable because it is old; provide advisory evidence or mark it.
- Distinguish "audit could not verify" from "verified clean" in the report.
- Record lookup date and source for every advisory claim; never fabricate a CVE or a score.
