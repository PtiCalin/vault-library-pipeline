"""
vault-library-pipeline — CLI
PDF ingestion, TYPE–DOMAIN renaming, metadata extraction.

Usage:
    python cli.py                  # process all PDFs in input_pdfs/
    python cli.py --file path.pdf  # process a single file
    python cli.py --validate       # validate filenames in processed/
    python cli.py --watch          # watch input_pdfs/ continuously
"""

import os
import re
import json
import time
import shutil
import argparse
import logging
from pathlib import Path
from datetime import datetime

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    import yaml
except ImportError:
    yaml = None

# ---------------------------------------------------------------------------
# Paths (resolved relative to this file so the CLI works from any cwd)
# ---------------------------------------------------------------------------
BASE_DIR    = Path(__file__).parent
INPUT_DIR   = BASE_DIR / "01_input_pdfs"
OUTPUT_DIR  = BASE_DIR / "02_processed"
META_DIR    = BASE_DIR / "03_metadata"
CONFIG_FILE = BASE_DIR / "config.yaml"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("vault-pipeline")

# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------
def load_config() -> dict:
    """Load config.yaml if available; fall back to safe defaults."""
    defaults = {
        "type_keywords": {
            "REVIEW":       ["review", "systematic review", "literature review"],
            "SURVEY":       ["survey"],
            "META":         ["meta-analysis"],
            "THESIS":       ["thesis"],
            "DISSERTATION": ["dissertation", "doctoral"],
            "PREPRINT":     ["preprint", "arxiv"],
            "PROCEEDING":   ["proceedings", "conference paper"],
            "POSTER":       ["poster"],
            "TALK":         ["presentation", "slide deck"],
            "BOOK":         ["handbook", "textbook", "introduction to"],
            "CHAPTER":      ["chapter"],
            "MONOGRAPH":    ["monograph"],
            "REPORT":       ["report", "technical report"],
            "WHITEPAPER":   ["white paper", "whitepaper"],
            "STANDARD":     ["iso", "rfc", "w3c"],
            "SPEC":         ["specification"],
            "DOC":          ["documentation"],
            "TUTORIAL":     ["tutorial"],
            "GUIDE":        ["guide", "how to"],
            "COURSE":       ["course", "lecture notes"],
            "NOTE":         ["notes"],
            "DATASET":      ["dataset"],
            "BENCHMARK":    ["benchmark"],
            "CODE":         ["implementation"],
            "MODEL":        ["model architecture"],
            "ARTICLE":      ["magazine article"],
            "BLOG":         ["blog"],
            "NEWS":         ["news"],
            "INTERVIEW":    ["interview"],
            "POLICY":       ["policy"],
            "LAW":          ["legal text"],
            "REGULATION":   ["regulation"],
            "PAPER":        [],
        },
        "domain_keywords": {
            "FORMAL":      ["mathematics", "logic", "statistics", "optimization",
                            "algebra", "topology", "probability", "calculus"],
            "COMPUTE":     ["algorithm", "machine learning", "deep learning",
                            "neural network", "recommendation", "nlp",
                            "computer vision", "artificial intelligence",
                            "transformer", "large language model", "llm",
                            "software", "database", "computing"],
            "NATURE":      ["biology", "genomics", "protein", "cell", "gene",
                            "bioinformatics", "ecology", "physics", "chemistry",
                            "molecule", "quantum", "particle", "medicine"],
            "HUMAN":       ["psychology", "cognition", "neuroscience", "behavior",
                            "perception", "decision making"],
            "SOCIAL":      ["sociology", "economics", "political science",
                            "governance", "anthropology", "organization"],
            "CULTURE":     ["art", "music", "cinema", "film", "literature",
                            "philosophy", "religion", "ethics"],
            "DESIGN":      ["ux", "user experience", "product design",
                            "architecture", "systems thinking"],
            "ENGINEERING": ["infrastructure", "hardware", "energy",
                            "systems engineering", "applied engineering"],
            "META":        [],
        },
        "watch_interval_seconds": 10,
        "slug_word_limit": 6,
    }
    if yaml and CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as fh:
            user_cfg = yaml.safe_load(fh) or {}
        # Deep-merge keyword lists
        for section in ("type_keywords", "domain_keywords"):
            if section in user_cfg:
                defaults[section].update(user_cfg[section])
        for key in ("watch_interval_seconds", "slug_word_limit"):
            if key in user_cfg:
                defaults[key] = user_cfg[key]
    return defaults

# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
FILLER_WORDS = {
    "a", "an", "the", "of", "in", "on", "at", "to", "for", "with",
    "and", "or", "is", "are", "its", "via", "by", "as", "from",
    "into", "this", "that", "which", "how", "why", "what", "when",
}

def clean_text(text: str) -> str:
    return re.sub(r"[^a-z0-9\- ]", "", text.lower()).strip()

def slugify(title: str, word_limit: int = 6) -> str:
    words = [w for w in clean_text(title).split() if w not in FILLER_WORDS]
    return "-".join(words[:word_limit])

# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------
def extract_pdf_metadata(path: Path) -> tuple[str, str, str]:
    """Return (title, author, year) from PDF metadata or safe fallbacks."""
    title  = path.stem
    author = "unknown"
    year   = "0000"  # unknown until extracted from PDF

    if PdfReader is None:
        log.warning("PyPDF2 not installed — using filename as title.")
        return title, author, year

    try:
        reader = PdfReader(str(path))
        meta   = reader.metadata
        if meta:
            if meta.title:
                title = meta.title.strip()
            if meta.author:
                first_author = meta.author.split(";")[0].split(",")[0].split()
                author = first_author[-1].lower() if first_author else "unknown"
            # /CreationDate format: D:20210415...
            creation = getattr(meta, "creation_date", None)
            if creation:
                year = str(creation.year)
    except Exception as exc:
        log.warning("Could not read PDF metadata for %s: %s", path.name, exc)

    # Sanitise author (strip non-alpha)
    author = re.sub(r"[^a-z]", "", author) or "unknown"
    return title, author, year

# ---------------------------------------------------------------------------
# TYPE / DOMAIN inference
# ---------------------------------------------------------------------------
def infer_type(title: str, cfg: dict) -> str:
    t = title.lower()
    for type_label, keywords in cfg["type_keywords"].items():
        if keywords and any(k in t for k in keywords):
            return type_label
    return "PAPER"

def infer_domain(title: str, cfg: dict) -> str:
    t = title.lower()
    for domain_label, keywords in cfg["domain_keywords"].items():
        if keywords and any(k in t for k in keywords):
            return domain_label
    return "META"

# ---------------------------------------------------------------------------
# Filename validation
# ---------------------------------------------------------------------------
FILENAME_PATTERN = re.compile(r"^[A-Z]+_[A-Z]+_\d{4}_[a-z0-9\-]+_[a-z]+(?:_v\d+)?\.pdf$")

def validate_filename(name: str) -> bool:
    return bool(FILENAME_PATTERN.match(name))

# ---------------------------------------------------------------------------
# Core processing
# ---------------------------------------------------------------------------
def process_file(path: Path, cfg: dict) -> dict | None:
    """Rename a PDF and write its metadata JSON. Returns metadata dict or None."""
    log.info("Processing: %s", path.name)

    title, author, year = extract_pdf_metadata(path)
    short_title = slugify(title, cfg.get("slug_word_limit", 6))
    doc_type    = infer_type(title, cfg)
    domain      = infer_domain(title, cfg)

    new_name = f"{doc_type}_{domain}_{year}_{short_title}_{author}.pdf"

    # Enforce 100-character filename limit by trimming the slug
    if len(new_name) > 100:
        fixed = len(doc_type) + len(domain) + len(author) + 12
        max_slug = max(3, 100 - fixed)
        trimmed = short_title[:max_slug].rstrip("-")
        new_name = f"{doc_type}_{domain}_{year}_{trimmed}_{author}.pdf"
        log.warning("Filename trimmed to fit 100-char limit: %s", new_name)

    if not validate_filename(new_name):
        log.error("Generated filename failed validation: %s", new_name)
        return None

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Resolve duplicates: append _v2, _v3, …
    dest = OUTPUT_DIR / new_name
    if dest.exists():
        stem = Path(new_name).stem
        for version in range(2, 100):
            candidate = f"{stem}_v{version}.pdf"
            dest = OUTPUT_DIR / candidate
            if not dest.exists():
                new_name = candidate
                log.info("Duplicate detected — versioned as: %s", new_name)
                break
        else:
            log.error("Could not find a free filename for %s", new_name)
            return None

    shutil.move(str(path), str(dest))
    log.info("Renamed → %s", new_name)

    metadata = {
        "type":     doc_type,
        "domain":   domain,
        "year":     year,
        "title":    title,
        "author":   author,
        "filename": new_name,
        "source":   str(path),
        "processed_at": datetime.utcnow().isoformat() + "Z",
        "tags":     [domain.lower(), doc_type.lower()],
    }

    META_DIR.mkdir(parents=True, exist_ok=True)
    meta_path = META_DIR / (new_name + ".json")
    with open(meta_path, "w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2, ensure_ascii=False)
    log.info("Metadata → %s", meta_path.name)

    return metadata

# ---------------------------------------------------------------------------
# Batch / watch
# ---------------------------------------------------------------------------
def run_batch(cfg: dict) -> None:
    """Process all PDFs currently in input_pdfs/."""
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    pdfs = list(INPUT_DIR.glob("*.pdf"))
    if not pdfs:
        log.info("No PDFs found in %s", INPUT_DIR)
        return
    for pdf in pdfs:
        process_file(pdf, cfg)

def run_validate() -> None:
    """Validate all filenames in processed/."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    errors = 0
    for pdf in OUTPUT_DIR.glob("*.pdf"):
        if validate_filename(pdf.name):
            log.info("[OK]    %s", pdf.name)
        else:
            log.error("[FAIL]  %s", pdf.name)
            errors += 1
    if errors == 0:
        log.info("All filenames valid.")
    else:
        log.warning("%d filename(s) failed validation.", errors)

def run_watch(cfg: dict) -> None:
    """Poll input_pdfs/ and process new PDFs on arrival."""
    interval = cfg.get("watch_interval_seconds", 10)
    log.info("Watching %s every %ds — Ctrl+C to stop.", INPUT_DIR, interval)
    seen: set[str] = set()
    try:
        while True:
            INPUT_DIR.mkdir(parents=True, exist_ok=True)
            for pdf in INPUT_DIR.glob("*.pdf"):
                if pdf.name not in seen:
                    process_file(pdf, cfg)
                    seen.add(pdf.name)
            time.sleep(interval)
    except KeyboardInterrupt:
        log.info("Watch stopped.")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="vault-library-pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--file",     metavar="PATH", help="Process a single PDF file.")
    p.add_argument("--validate", action="store_true", help="Validate filenames in processed/.")
    p.add_argument("--watch",    action="store_true", help="Watch input_pdfs/ continuously.")
    return p

def main() -> None:
    args   = build_parser().parse_args()
    cfg    = load_config()

    if args.validate:
        run_validate()
    elif args.watch:
        run_watch(cfg)
    elif args.file:
        p = Path(args.file)
        if not p.exists():
            log.error("File not found: %s", args.file)
            raise SystemExit(1)
        process_file(p, cfg)
    else:
        run_batch(cfg)

if __name__ == "__main__":
    main()
