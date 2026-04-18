# Changelog

All notable changes to **vault-library-pipeline** are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added

- Replace PyPDF2 with `pdfminer.six` for richer text extraction and embedded PDF info parsing
- Add optional GROBID integration for structured academic metadata enrichment
- Add optional CrossRef and Semantic Scholar DOI lookups to backfill title, author, year, and abstract

---

## [1.0.0] — 2026-04-06

### Added

#### Core pipeline

- `library_pipeline/cli.py` — PDF ingestion engine with `--file`, `--validate`, and `--watch` modes
- `library_pipeline/export_to_obsidian.py` — renders Obsidian markdown notes from metadata JSONs
- `library_pipeline/config.yaml` — keyword-driven TYPE/DOMAIN inference rules (editable without touching code)
- `library_pipeline/requirements.txt` — runtime dependencies (`PyPDF2`, `PyYAML`)

#### Folder structure

- `00_templates/` — Zotero and Obsidian note templates
- `01_input_pdfs/` — drop zone for raw PDFs
- `02_processed/` — destination for renamed PDFs
- `03_metadata/` — one JSON file per processed PDF
- `04_exports/` — Obsidian-ready `.md` notes

#### Naming convention

- Enforced `TYPE_DOMAIN_YEAR_short-title-slug_authorlastname.pdf` pattern
- Filename validation via `--validate` flag and regex `^[A-Z]+_[A-Z]+_\d{4}_[a-z0-9\-]+_[a-z]+\.pdf$`

#### Templates

- `00_templates/zotero-note-template.md` — structured note template for Zotero
- `00_templates/obsidian-note-template.md` — YAML frontmatter + section scaffold for Obsidian

#### GitHub materials

- `.github/PULL-REQUEST_TEMPLATE.md` — pipeline-specific PR checklist
- `.github/COMMIT-MESSAGE_TEMPLATE.md` — conventional commits with `pipeline` type and domain scopes
- `.github/CODEOWNERS` — auto-review requests routed to `@PtiCalin`
- `.github/SECURITY.md` — vulnerability scope and private reporting instructions
- `.github/dependabot.yml` — weekly pip and monthly Actions version bumps
- `.github/issue-templates/bug_report.yml` — structured bug form
- `.github/issue-templates/feature_request.yml` — feature proposal form with ROADMAP dropdown
- `.github/issue-templates/pipeline_issue.yml` — domain-specific form for naming/metadata errors
- `.github/workflows/ci.yml` — CI: Python syntax check, flake8 lint, config.yaml validation

#### Documentation

- `README` — architecture diagram, quick start, naming convention, dependency table
- `ROADMAP.md` — v1–v4 milestones and future ideas
- `CONTRIBUTION.md` — ground rules, dev setup, branch/commit conventions

---

[Unreleased]: https://github.com/PtiCalin/vault-library-pipeline/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/PtiCalin/vault-library-pipeline/releases/tag/v1.0.0
