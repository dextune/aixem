# Security Policy

Report path traversal, digest verification, remote-asset, generated HTML, archive integrity, schema validation, secret handling, or untrusted-input issues with a minimal reproducer and the affected artifact. Do not include credentials, private keys, private reasoning, or confidential circuit data.

## Security Boundaries

- Project-relative paths are confined to the repository or declared project root.
- Remote documentation and rendering assets are denied by default unless a contract explicitly permits them.
- Locked source digests are verified before deterministic output is trusted.
- The documentation site is static and has no database or server-side runtime.
- Search data is generated locally and does not transmit queries.
- Canonical path redirects are static, repository-generated, and validated against the migration registry.
- ZIP members are checked for absolute paths, parent traversal, duplicate members, and a single top-level directory.
- Release files are covered by a SHA-256 manifest with explicit self-referential exclusions.
- External executor descriptors contain approved environment-variable names, never secret values.

The repository-wide navigation path is documented in [`REFERENCE.md`](REFERENCE.md).

Technical trust boundaries are specified in [`docs/architecture/security.md`](docs/architecture/security.md). This root file owns reporting procedure, not system architecture.

## Reporting

Include the AIXEM version, affected path, exact command, observed behavior, expected behavior, and a reduced reproducer. Security reports should avoid distributing third-party proprietary assets or private circuit data.
