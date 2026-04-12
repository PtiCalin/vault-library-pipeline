# vault-library-pipeline

A local-first pipeline that ingests PDFs, enforces a strict TYPE–DOMAIN naming
convention, extracts metadata, and syncs structured notes from Zotero to
Obsidian with YAML frontmatter for a scalable knowledge system.

---

## System architecture

```txt
PDF → cli.py → (renamed PDF + metadata.json)
                       ↓
              Zotero import (Better BibTeX)
                       ↓
            Zotero note template (auto-note)
                       ↓
      export_to_obsidian.py → exports/*.md (YAML frontmatter)
                       ↓
                Obsidian vault
```

Each step is independent and debuggable.

---

## Folder structure

```txt
library_pipeline/
  00_templates/
    zotero-note-template.md
    obsidian-note-template.md
  01_input_pdfs/          ← drop PDFs here
  02_processed/           ← renamed PDFs land here
  03_metadata/            ← one JSON per processed PDF
  04_exports/             ← Obsidian-ready markdown notes
  cli.py               ← core processing engine
  export_to_obsidian.py
  config.yaml          ← keyword rules for TYPE/DOMAIN inference
  requirements.txt
```

---

## Quick start

```bash
cd library_pipeline
pip install -r requirements.txt

# 1. Drop PDFs into input_pdfs/

# 2. Process all PDFs (rename + generate metadata JSON)
python cli.py

# 3. Validate the renamed filenames
python cli.py --validate

# 4. Export Obsidian notes from metadata
python export_to_obsidian.py

# 5. Import processed/ PDFs into Zotero manually (drag and drop)
#    Apply zotero-note-template.md via a note template plugin
```

---

## Naming convention

```txt
TYPE_DOMAIN_YEAR_short-title-slug_authorlastname.pdf
```

Examples:

```txt
PAPER_COMPUTE_2023_attention-is-all-you-need_vaswani.pdf
REVIEW_BIO_2021_systematic-review-crispr-gene_zhang.pdf
SURVEY_COMPUTE_2022_survey-large-language-models_zhao.pdf
```

---

## Watch mode

```bash
python cli.py --watch
```

Polls `input_pdfs/` every 10 seconds and processes new PDFs automatically.
Interval is configurable in `config.yaml`.

---

## Configuration

Edit `config.yaml` to add keywords for TYPE and DOMAIN inference.
Matches are case-insensitive and now use normalized title, filename, and,
when text extraction succeeds, the first PDF page.

Optional metadata enrichment can also be enabled in `config.yaml`:

- `grobid_url` to extract structured academic metadata from a local or remote GROBID service
- `crossref_enabled` to resolve DOI metadata from CrossRef
- `semantic_scholar_enabled` to backfill DOI metadata from Semantic Scholar

---

## Dependencies

| Package   | Purpose                          |
|-----------|----------------------------------|
| pdfminer.six | PDF text + embedded metadata extraction |
| PyYAML    | config.yaml parsing              |

---

## Accuracy

- Header-only metadata is often unreliable for noisy PDFs, ISBN-based filenames,
  and scanned exports
- TYPE and DOMAIN inference now uses title, filename, and first-page text to
  reduce `PAPER_META` fallbacks
- DOI extraction can be enriched through GROBID, CrossRef, and Semantic Scholar
  when those services are configured or reachable
- Manual correction can still be necessary for image-only PDFs or very sparse documents
