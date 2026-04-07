# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| main    | Yes       |

## Scope

vault-library-pipeline is a **local-first tool** that runs entirely on your machine.
It does not expose any network services, APIs, or web interfaces.

Potential security considerations:

- **File system access** — the pipeline reads from `input_pdfs/` and writes to
  `processed/`, `metadata/`, and `exports/`. Ensure only trusted PDFs are placed
  in `input_pdfs/`.
- **PDF metadata** — malicious PDF metadata is read as plain strings and written
  to JSON / markdown. No `eval`, `exec`, or shell interpolation is performed on
  metadata values.
- **Watch mode** — `--watch` polls the filesystem on a fixed interval. It does
  not use privileged OS APIs.
- **Dependencies** — `PyPDF2` and `PyYAML` are the only runtime dependencies.
  Keep them up to date via `pip install -r requirements.txt --upgrade`.

## Reporting a vulnerability

If you discover a security issue, **do not open a public issue**.

Please email the maintainer directly or use
[GitHub's private vulnerability reporting](https://github.com/PtiCalin/vault-library-pipeline/security/advisories/new).

Include:
- A description of the vulnerability
- Steps to reproduce
- The potential impact
- Any suggested fix (optional)

You will receive an acknowledgement within 5 business days.
