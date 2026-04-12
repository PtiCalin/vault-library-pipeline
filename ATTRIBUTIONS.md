# Attributions

This project depends on third-party libraries and can optionally integrate with
external tools and metadata services. Their respective authors, maintainers,
and license holders retain all rights to their work.

## Runtime Dependencies

- pdfminer.six — PDF text and metadata extraction used by the ingestion pipeline.
	Project: https://github.com/pdfminer/pdfminer.six
	Authors listed in the installed package metadata: Yusuke Shinyama, Pieter Marsman.
	License: MIT.

- PyYAML — YAML parsing for pipeline configuration.
	Project: https://pyyaml.org/
	Author listed in the installed package metadata: Kirill Simonov.
	License: MIT.

## Optional Integrations and Services

- GROBID — optional structured metadata extraction for academic PDFs.
	Project: https://github.com/kermitt2/grobid

- CrossRef API — optional DOI-based metadata lookup.
	Service: https://api.crossref.org/

- Semantic Scholar API — optional DOI-based metadata enrichment.
	Service: https://api.semanticscholar.org/

- Zotero and Better BibTeX — supported downstream workflow tools for citation
	management and note generation.
	Projects: https://www.zotero.org/ and https://retorque.re/zotero-better-bibtex/

- Obsidian — supported downstream note-taking environment for exported markdown.
	Project: https://obsidian.md/

## Notes

- This repository does not bundle or redistribute third-party source code.
- Use of external APIs and services is optional and controlled by local configuration.
- If this project adopts additional dependencies or embedded assets, they should be
	added to this file with their source and license information.
