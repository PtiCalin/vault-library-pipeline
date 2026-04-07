# Contributing to vault-library-pipeline

Thank you for your interest in contributing.
This is a local-first, personal-scale tool — contributions are welcome and should stay focused on keeping it simple and debuggable.

---

## Ground rules

- Keep each PR focused on **one concern** (one fix, one feature).
- Do not add new dependencies without discussion.
- Do not add network calls or cloud integrations without an opt-in config flag.
- All filenames produced by the pipeline must conform to the `TYPE_DOMAIN_YEAR_slug_author.pdf` pattern.
- Maintain Python 3.10+ compatibility.

---

## Development setup

```bash
git clone https://github.com/PtiCalin/vault-library-pipeline.git
cd vault-library-pipeline/library_pipeline
pip install -r requirements.txt
pip install flake8
```

---

## Workflow

1. **Fork** the repository and create a branch from `main`.
2. Branch naming: `feat/short-description`, `fix/short-description`, `docs/short-description`.
3. Make your changes.
4. Run the validation checks:
   ```bash
   python cli.py --validate
   flake8 . --max-line-length=100
   ```
5. Commit using the [commit message convention](.github/COMMIT-MESSAGE_TEMPLATE.md).
6. Open a pull request against `main` using the [PR template](.github/PULL-REQUEST_TEMPLATE.md).

---

## Commit message convention

```
<type>(<scope>): <short summary>
```

Types: `feat`, `fix`, `docs`, `refactor`, `chore`, `ci`, `pipeline`  
Scopes: `cli`, `config`, `metadata`, `rename`, `export`, `zotero`, `obsidian`, `templates`, `workflow`

Example:
```
feat(cli): add --dry-run flag to preview renames without moving files
```

---

## Reporting issues

Use the issue templates:
- **Bug report** — reproducible problem with the pipeline
- **Feature request** — new capability or improvement
- **Naming / metadata issue** — wrong TYPE/DOMAIN inference or bad slug

---

## What not to contribute

- GUI or web front-ends (out of scope for v1–v3)
- Cloud sync or remote storage integrations
- Major refactors before v1 is validated on real PDFs
