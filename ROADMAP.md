# ROADMAP vault-library-pipeline

## v1 Core pipeline (current)
- [x] Folder structure (`input_pdfs/`, `processed/`, `metadata/`, `exports/`, `templates/`)
- [x] `cli.py` PDF ingestion, metadata extraction, TYPE–DOMAIN rename, JSON output
- [x] `config.yaml` keyword-driven TYPE/DOMAIN inference rules
- [x] Filename validation (`--validate`)
- [x] Watch mode (`--watch`)
- [x] `export_to_obsidian.py` render Obsidian markdown notes from metadata JSONs
- [x] Zotero note template (`templates/zotero-note-template.md`)
- [x] Obsidian note template with YAML frontmatter (`templates/obsidian-note-template.md`)

---

## v2 Better metadata
- [ ] Replace PyPDF2 with `pdfminer.six` for richer text extraction
- [ ] Add GROBID integration for structured academic metadata (title, abstract, authors)
- [ ] Pull metadata from CrossRef / Semantic Scholar APIs by DOI
- [ ] Smarter author disambiguation (handle "Last, First" and "First Last" formats)

---

## v3 Smarter inference
- [ ] Replace keyword lists with a small ML text classifier (scikit-learn, TF-IDF)
- [ ] Add keyword-to-concept mapping for auto-tagging from abstract
- [ ] Domain ontology file (YAML) with hierarchical categories

---

## v4 Full automation
- [ ] Stable watch-mode daemon with inotify/FSEvents instead of polling
- [ ] Zotero API integration (auto-import via Zotero Web API)
- [ ] Direct push to Obsidian vault via configurable vault path
- [ ] Duplicate detection (hash-based)
- [ ] Web UI or TUI for review and correction

---

## Future ideas
- [ ] `vault-cli` package installable CLI with `vault process`, `vault watch`, `vault export`
- [ ] Support for EPUB, DOCX ingestion
- [ ] Citation graph extraction
- [ ] Obsidian Dataview-compatible tag schema
