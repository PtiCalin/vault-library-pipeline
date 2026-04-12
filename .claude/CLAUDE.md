# CLAUDE.md Project Context for AI Assistance

## Project Identity

**Name:** vault-library-pipeline  
**Owner:** PtiCalin (Charlie)  
**Type:** local-first Python document-processing pipeline  
**Primary goal:** turn raw PDFs into consistently named files, metadata JSON, and Obsidian-ready notes  
**Status:** active workflow and naming-system refinement

---

## Project Purpose

This repository is a personal knowledge-ingestion pipeline for academic and technical PDFs.

The workflow is intentionally simple and debuggable:

1. Drop PDFs into `library_pipeline/01_input_pdfs/`
2. Run the CLI to extract metadata and rename each file using a strict `TYPE_DOMAIN_YEAR_slug_author.pdf` convention
3. Save one metadata JSON per processed PDF in `library_pipeline/03_metadata/`
4. Export Obsidian markdown notes from metadata and templates into `library_pipeline/04_exports/`
5. Use Zotero and note templates as the manual bridge into the wider reading workflow

This project is local-first. Each stage should be understandable in isolation, safe to rerun, and easy to inspect from the filesystem.

---

## System Architecture

```txt
PDF -> cli.py -> renamed PDF + metadata JSON
                     |
                     +-> optional metadata enrichment
                         (GROBID / CrossRef / Semantic Scholar)
                     |
                     +-> export_to_obsidian.py -> markdown note
                                                  using template placeholders
```

The system is designed around files, not a database. Output artifacts are part of the user-visible workflow.

---

## Repository Structure

```txt
vault-library-pipeline/
├── README
├── CHANGE-LOG.md
├── ROADMAP.md
├── library_pipeline/
│   ├── cli.py
│   ├── export_to_obsidian.py
│   ├── config.yaml
│   ├── requirements.txt
│   ├── 00_templates/
│   │   ├── obsidian-note-template.md
│   │   └── zotero-note-template.md
│   ├── 01_input_pdfs/
│   ├── 02_processed/
│   ├── 03_metadata/
│   └── 04_exports/
└── .claude/
    └── CLAUDE.md
```

### Folder roles

- `01_input_pdfs/`: raw PDFs waiting to be processed
- `02_processed/`: renamed PDFs after classification
- `03_metadata/`: one JSON file per processed PDF
- `04_exports/`: Obsidian-ready markdown generated from metadata
- `00_templates/`: text templates used for downstream note generation

---

## Core Concepts

### Naming contract

Processed PDFs are expected to follow this format:

```txt
TYPE_DOMAIN_YEAR_short-title-slug_authorlastname.pdf
```

Examples:

```txt
PAPER_COMPUTE_2023_attention-is-all-you-need_vaswani.pdf
REVIEW_BIO_2021_systematic-review-crispr-gene_zhang.pdf
SURVEY_COMPUTE_2022_survey-large-language-models_zhao.pdf
```

The naming contract is not cosmetic. It is the main stable interface between raw documents, exported metadata, and downstream knowledge tools.

### Classification

`cli.py` infers `TYPE` and `DOMAIN` from normalized text using keyword maps in `config.yaml`.

Signals include:

- embedded PDF metadata when available
- the original filename
- extracted first-page or front-matter text
- optional DOI-based enrichment sources

Fallbacks matter:

- `PAPER` is the default type when nothing stronger matches
- `META` is the default domain when classification is uncertain

### Metadata enrichment

The pipeline can enrich document metadata through optional external services:

- GROBID for structured document parsing
- CrossRef for DOI-based metadata
- Semantic Scholar as a DOI backfill source

These integrations are optional and should fail gracefully. The pipeline must remain useful when they are disabled or unreachable.

### Obsidian export

`export_to_obsidian.py` loads metadata JSON files, renders placeholders into `00_templates/obsidian-note-template.md`, and writes markdown notes to `04_exports/`.

Template compatibility matters. Changes to metadata keys or note structure should preserve the export path or include matching template updates.

---

## Commands

Run commands from `library_pipeline/` unless the command uses an explicit path.

```bash
pip install -r requirements.txt
python cli.py
python cli.py --file 01_input_pdfs/example.pdf
python cli.py --validate
python cli.py --watch
python export_to_obsidian.py
python export_to_obsidian.py --file 03_metadata/example.json
```

### CLI modes

- default run: process all PDFs in `01_input_pdfs/`
- `--file`: process a single PDF
- `--validate`: validate processed filenames in `02_processed/`
- `--watch`: poll `01_input_pdfs/` and process new files continuously

---

## Stack & Dependencies

| Layer | Technology |
|-------|------------|
| Runtime | Python |
| PDF text and metadata extraction | `pdfminer.six` |
| Config parsing | `PyYAML` |
| HTTP integrations | standard library `urllib` |
| Output formats | JSON and Markdown |
| Knowledge tools | Zotero, Better BibTeX, Obsidian |

The codebase currently favors a lightweight dependency surface and standard-library implementations where practical.

---

## How Claude Should Assist

### Assist with

- Python CLI improvements in `cli.py` and `export_to_obsidian.py`
- filename validation and naming-rule changes
- metadata extraction quality improvements
- safe integration of optional external metadata services
- template edits for Obsidian and Zotero note generation
- bug fixes in classification, slugification, author parsing, and export logic
- documentation updates for workflow, setup, and conventions
- tests or lightweight validation scripts where they improve confidence

### Priorities when making changes

1. Preserve the naming contract unless the user explicitly requests a breaking change
2. Avoid destructive behavior that can lose PDFs, metadata JSON, or exported notes
3. Keep external integrations optional and failure-tolerant
4. Prefer small, inspectable file-based workflows over hidden state
5. Keep commands runnable from the local repository without unnecessary infrastructure

### Do not do implicitly

- introduce a database or server architecture without an explicit request
- replace the naming convention with a looser scheme without updating validation and docs
- make network lookups mandatory for successful local processing
- delete or rewrite user files in processed folders without a clear reason and confirmation

---

## Implementation Notes

### Path handling

`cli.py` and `export_to_obsidian.py` resolve key directories relative to their own file location. Preserve that behavior so commands work from different current working directories.

### Output stability

Metadata JSON and exported markdown are user-facing artifacts. Changes to field names, filenames, or template placeholders should be deliberate and documented.

### Error handling

This project should degrade gracefully:

- missing optional dependencies should not crash unrelated workflows
- unreadable PDFs should log useful warnings
- failed HTTP enrichment should not prevent local metadata generation

### Configuration

`config.yaml` is part of the product surface. Keyword-map changes affect classification outcomes and should be treated as behavior changes, not internal refactors.

---

## Working Assumptions

- The user is building a durable personal knowledge workflow, not a one-off renamer
- The pipeline should remain understandable to a single developer operating locally
- Manual review is still acceptable for low-confidence metadata cases
- Accuracy improvements are valuable, but not at the cost of opaque behavior or fragile dependencies

---

## Integrity Note

This repository processes the user's own local document collection and exports structured notes for personal knowledge management. Any automation added here should favor traceability, reversibility, and filesystem-visible outputs over hidden side effects.
