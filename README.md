# vault-library-pipeline

A local-first pipeline that ingests PDFs, enforces a strict
TYPE-DOMAIN-YEAR-SLUG-AUTHOR naming convention, extracts metadata, and exports
structured notes to Obsidian with YAML frontmatter.

---

## System architecture

```txt
PDF → cli.py → (renamed PDF + metadata.json + base tags)
        ↓
      export_to_obsidian.py → exports/*.md (YAML frontmatter)
        ↓
      Obsidian vault / Zotero workflow
```

Each step is independent, file-based, and debuggable.

---

## Documentation hub

Use this section as the single point of entry for rules and conventions.

- File naming convention: [docs/FILE-NAMING.md](docs/FILE-NAMING.md)
- TYPE taxonomy: [docs/TYPES.md](docs/TYPES.md)
- DOMAIN taxonomy: [docs/DOMAINS.md](docs/DOMAINS.md)
- Inference logic and scoring: [docs/INFERENCE-RULES.md](docs/INFERENCE-RULES.md)
- Metadata extraction and enrichment: [docs/EXTRACT-METADATA.md](docs/EXTRACT-METADATA.md)
- PDF content parsing: [docs/PARSE-CONTENT.md](docs/PARSE-CONTENT.md)
- Tags system (secondary domains + concepts): [docs/TAGS.md](docs/TAGS.md)

---

## Folder structure

```txt
library_pipeline/
  00_templates/
    zotero-note-template.md
    obsidian-note-template.md
  01_input_pdfs/          ← drop PDFs here
  02_processed/           ← renamed PDFs land here
  03_metadata/            ← one JSON per processed PDF (classification + sources)
  04_exports/             ← Obsidian-ready markdown notes with frontmatter
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
REVIEW_NATURE_2021_systematic-review-crispr-gene_zhang.pdf
SURVEY_COMPUTE_2022_survey-large-language-models_zhao.pdf
```

Classification contract:

- exactly 1 TYPE
- exactly 1 primary DOMAIN in filename
- 0 to 3 secondary domains in tags
- at least 1 concept tag

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

Fallbacks are explicit:

- TYPE fallback: PAPER
- DOMAIN fallback: META

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
- TYPE and DOMAIN inference uses title, filename, and first-page text to reduce
  PAPER/META fallbacks
- DOI extraction can be enriched through GROBID, CrossRef, and Semantic Scholar
  when those services are configured or reachable
- Manual correction can still be necessary for image-only PDFs or very sparse documents
