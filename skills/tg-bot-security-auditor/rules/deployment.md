# Deployment, Infrastructure and Operations Audit Rules

## Configuration and secrets

- Inspect `.env` / `.env.*`, config YAML/TOML/JSON, CI definitions, Dockerfiles, compose files, systemd units, reverse-proxy config, deployment manifests.
- Report secret presence with **redacted** values only: file, variable name, type, and whether it is committed. Never print the value or the whole file.
- Check secret injection (env vs baked image), rotation path, least privilege of the token (bot admin rights, `delete_repo`, org scopes in CI tokens), and accidental inclusion in images or build artifacts.
- Check default credentials, debug flags enabled by default, and `ENV=dev` shipped to production.

## Runtime and host

- Process user (root?), filesystem permissions, writable directories, exposed ports, debug mode, admin interfaces, unnecessary capabilities.
- Containers: privileged mode, host path mounts, image pinning (tag vs digest), health checks, resource limits, network segmentation.
- systemd/service: restart policy, `Restart=always` loops on a failing config, log permissions, graceful shutdown timeout vs Telegram polling.
- Check that the bot token is not readable by other users on the host, and that `.env` is not world-readable.

## Webhook and reverse proxy

- TLS termination and certificate renewal, trusted proxy configuration (which IPs may set forwarded headers), request size limits, path exposure, access logs.
- Confirm webhook secret validation happens in the application or a trusted gateway — and that the gateway does not strip the header.
- Health endpoints must not disclose internals (versions, DB status with credentials, queue depth with customer data).
- Check for accidental exposure of admin panels, metrics endpoints, or the audit report itself.

## CI/CD and supply chain

- Workflow permissions (`GITHUB_TOKEN` scope), untrusted pull-request execution (`pull_request_target` with checkout of PR code), secret exposure in logs, artifact retention.
- Dependency pinning, lockfile commit, registry source, install scripts.
- Scripts downloaded and executed dynamically; suspicious install hooks; unexpected binaries committed.
- Never execute deployment or CI scripts during an audit.

## Backups, monitoring and recovery

- Backup schedule, encryption, off-host storage, restore testing, and whether backups include secrets.
- Monitoring: alerts for auth failures, payment anomalies, 429 storms; logs with retention and access control.
- Incident response hooks: can the operator revoke tokens, rotate the webhook secret, and disable a compromised admin?
