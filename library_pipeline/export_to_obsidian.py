"""
export_to_obsidian.py — render Obsidian notes from metadata JSONs.

Usage:
    python export_to_obsidian.py                  # export all metadata JSONs
    python export_to_obsidian.py --file meta.json # export a single file
"""

import json
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("obsidian-export")

BASE_DIR      = Path(__file__).parent
META_DIR      = BASE_DIR / "03_metadata"
EXPORTS_DIR   = BASE_DIR / "04_exports"
TEMPLATE_FILE = BASE_DIR / "00_templates" / "obsidian-note-template.md"


def load_template() -> str:
    if not TEMPLATE_FILE.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_FILE}")
    return TEMPLATE_FILE.read_text(encoding="utf-8")


def render(template: str, meta: dict) -> str:
    result = template
    for key, value in meta.items():
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)
        result = result.replace("{{" + key + "}}", str(value))
    return result


def export_file(json_path: Path, template: str) -> None:
    with open(json_path, "r", encoding="utf-8") as fh:
        meta = json.load(fh)

    note = render(template, meta)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Use the PDF filename stem as the note name
    stem     = Path(meta.get("filename", json_path.stem)).stem
    out_path = EXPORTS_DIR / (stem + ".md")

    out_path.write_text(note, encoding="utf-8")
    log.info("Exported → %s", out_path.name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export metadata JSONs to Obsidian markdown.")
    parser.add_argument("--file", metavar="PATH", help="Process a single metadata JSON.")
    args = parser.parse_args()

    template = load_template()

    if args.file:
        p = Path(args.file)
        if not p.exists():
            log.error("File not found: %s", args.file)
            raise SystemExit(1)
        export_file(p, template)
    else:
        META_DIR.mkdir(parents=True, exist_ok=True)
        jsons = list(META_DIR.glob("*.json"))
        if not jsons:
            log.info("No metadata JSON files found in %s", META_DIR)
            return
        for j in jsons:
            export_file(j, template)


if __name__ == "__main__":
    main()
