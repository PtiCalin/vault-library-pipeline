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
import unicodedata
from difflib import SequenceMatcher
from io import BytesIO
from pathlib import Path
from datetime import datetime
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request
from xml.etree import ElementTree

try:
    from pdfminer.high_level import extract_text as pdf_extract_text
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfparser import PDFParser
except ImportError:
    pdf_extract_text = None
    PDFDocument = None
    PDFParser = None

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

DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[-._;()/:a-z0-9]+\b", re.IGNORECASE)
YEAR_PATTERN = re.compile(r"(?:19|20)\d{2}")
DEFAULT_USER_AGENT = "vault-library-pipeline/1.1"

# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------
def validate_classification_config(cfg: dict) -> None:
    class_cfg = cfg.get("classification", {})
    field_weights = class_cfg.get("field_weights", {})
    for key, value in field_weights.items():
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"Invalid field weight for '{key}': {value}")

    fuzzy_cfg = class_cfg.get("fuzzy", {})
    for key in ("threshold", "partial_threshold", "fuzzy_boost"):
        value = fuzzy_cfg.get(key)
        if not isinstance(value, (int, float)):
            raise ValueError(f"Invalid fuzzy value for '{key}': {value}")
        if key in {"threshold", "partial_threshold"} and not 0 <= float(value) <= 1:
            raise ValueError(f"Invalid fuzzy threshold for '{key}': {value}")
        if key == "fuzzy_boost" and float(value) <= 0:
            raise ValueError(f"Invalid fuzzy boost for '{key}': {value}")

    secondary_cfg = class_cfg.get("secondary_domains", {})
    max_count = secondary_cfg.get("max_count", 3)
    min_relative = secondary_cfg.get("min_relative_score", 0.35)
    if not isinstance(max_count, int) or max_count < 0:
        raise ValueError(f"Invalid secondary domain max_count: {max_count}")
    if not isinstance(min_relative, (int, float)) or float(min_relative) < 0:
        raise ValueError(f"Invalid secondary domain min_relative_score: {min_relative}")

    concept_cfg = class_cfg.get("concept_tags", {})
    min_count = concept_cfg.get("min_count", 1)
    if not isinstance(min_count, int) or min_count < 1:
        raise ValueError(f"Invalid concept tag min_count: {min_count}")


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
        "metadata_enrichment": {
            "enabled": True,
            "grobid_url": "",
            "grobid_timeout_seconds": 20,
            "crossref_enabled": True,
            "semantic_scholar_enabled": True,
            "api_timeout_seconds": 15,
            "user_agent": DEFAULT_USER_AGENT,
        },
        "classification": {
            "field_weights": {
                "title": 3.0,
                "filename": 2.0,
                "first_page": 1.5,
                "abstract": 1.2,
            },
            "fuzzy": {
                "enabled": True,
                "threshold": 0.88,
                "partial_threshold": 0.92,
                "fuzzy_boost": 0.7,
            },
            "secondary_domains": {
                "max_count": 3,
                "min_relative_score": 0.35,
            },
            "concept_tags": {
                "min_count": 1,
                "fallback": "general",
            },
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
        if "metadata_enrichment" in user_cfg:
            defaults["metadata_enrichment"].update(user_cfg["metadata_enrichment"])
        if "classification" in user_cfg:
            classification_cfg = user_cfg["classification"] or {}
            for subsection in ("field_weights", "fuzzy", "secondary_domains", "concept_tags"):
                if subsection in classification_cfg:
                    defaults["classification"][subsection].update(classification_cfg[subsection] or {})
        for key in ("watch_interval_seconds", "slug_word_limit"):
            if key in user_cfg:
                defaults[key] = user_cfg[key]

    validate_classification_config(defaults)
    return defaults

# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
FILLER_WORDS = {
    "a", "an", "the", "of", "in", "on", "at", "to", "for", "with",
    "and", "or", "is", "are", "its", "via", "by", "as", "from",
    "into", "this", "that", "which", "how", "why", "what", "when",
}

NOISE_WORDS = {
    "doi", "isbn", "issn", "springer", "elsevier", "wiley", "ieee",
    "acm", "unknown", "untitled", "www", "http", "https",
}

DOMAIN_STOPWORDS = {
    "analysis", "approach", "study", "studies", "method", "methods",
    "framework", "model", "models", "system", "systems", "paper",
    "using", "based", "towards", "across", "through", "review",
}

def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char))

def clean_text(text: str) -> str:
    return re.sub(r"[^a-z0-9\- ]", "", strip_accents(text).lower()).strip()

def slugify(title: str, word_limit: int = 6) -> str:
    words = [w for w in clean_text(title).split() if w not in FILLER_WORDS]
    return "-".join(words[:word_limit])

def decode_pdf_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        for encoding in ("utf-8", "utf-16", "latin-1"):
            try:
                return value.decode(encoding).strip()
            except UnicodeDecodeError:
                continue
        return value.decode("utf-8", errors="ignore").strip()
    return str(value).strip()

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", strip_accents(text).lower())).strip()

def tokenize_text(text: str) -> list[str]:
    return [token for token in normalize_text(text).split() if token and token not in NOISE_WORDS]

def looks_like_identifier(text: str) -> bool:
    tokens = tokenize_text(text)
    if not tokens:
        return True
    if len(tokens) == 1 and re.fullmatch(r"[0-9x\-]+", tokens[0]):
        return True
    digit_count = sum(char.isdigit() for char in text)
    alpha_count = sum(char.isalpha() for char in text)
    return digit_count > alpha_count and alpha_count < 6

def extract_year(text: str) -> str:
    if not text:
        return "0000"
    match = YEAR_PATTERN.search(text)
    return match.group(0) if match else "0000"

def sanitize_author_token(value: str) -> str:
    if not value:
        return "unknown"
    if "," in value:
        value = value.split(",", 1)[0]
    parts = re.findall(r"[A-Za-z]+", value)
    return parts[-1].lower() if parts else "unknown"

def extract_doi(text: str) -> str:
    if not text:
        return ""
    match = DOI_PATTERN.search(text)
    if not match:
        return ""
    doi = match.group(0).rstrip(".,;)\"]'")
    return doi.lower()

def parse_author_list(raw_value: str) -> list[str]:
    if not raw_value:
        return []
    parts = [part.strip() for part in re.split(r";| and ", raw_value) if part.strip()]
    return parts

def format_author_name(given: str, family: str) -> str:
    return " ".join(part for part in (given.strip(), family.strip()) if part).strip()

def prefer_title(current: str, candidate: str) -> bool:
    if not candidate:
        return False
    if not current:
        return True
    if looks_like_identifier(current) and not looks_like_identifier(candidate):
        return True
    current_tokens = tokenize_text(current)
    candidate_tokens = tokenize_text(candidate)
    return len(candidate_tokens) >= max(3, len(current_tokens) + 2) and len(candidate) > len(current)

def extract_pdf_info(path: Path) -> dict[str, str]:
    if PDFParser is None or PDFDocument is None:
        return {}
    try:
        with path.open("rb") as fh:
            parser = PDFParser(fh)
            document = PDFDocument(parser)
            info = document.info[0] if document.info else {}
    except Exception as exc:
        log.warning("Could not read PDF info for %s: %s", path.name, exc)
        return {}

    decoded: dict[str, str] = {}
    for key, value in info.items():
        normalized_key = str(key).lstrip("/").lower()
        decoded[normalized_key] = decode_pdf_value(value)
    return decoded

def extract_pdf_text(path: Path, page_numbers: list[int], char_limit: int) -> str:
    if pdf_extract_text is None:
        return ""
    try:
        return (pdf_extract_text(str(path), page_numbers=page_numbers) or "")[:char_limit]
    except Exception as exc:
        log.warning("Could not extract PDF text for %s: %s", path.name, exc)
        return ""

def extract_first_page_text(path: Path) -> str:
    return extract_pdf_text(path, [0], 8000)

def extract_front_matter_text(path: Path) -> str:
    return extract_pdf_text(path, [0, 1], 16000)

def build_classification_text(path: Path, title: str, first_page_text: str = "") -> str:
    parts = [title, path.stem]
    if first_page_text:
        parts.append(first_page_text)

    if looks_like_identifier(title):
        stem_tokens = tokenize_text(path.stem)
        if stem_tokens:
            parts.append(" ".join(stem_tokens))

    return normalize_text(" ".join(part for part in parts if part))

def build_classification_sources(path: Path, metadata: dict) -> dict[str, str]:
    return {
        "title": normalize_text(metadata.get("title", "")),
        "filename": normalize_text(path.stem),
        "first_page": normalize_text(metadata.get("first_page_text", "")),
        "abstract": normalize_text(metadata.get("abstract", "")),
    }

def iterate_keyword_entries(raw_keywords: object) -> list[dict]:
    entries: list[dict] = []
    if isinstance(raw_keywords, dict):
        if "term" in raw_keywords:
            entries.append({
                "term": str(raw_keywords.get("term", "")),
                "weight": float(raw_keywords.get("weight", 1.0) or 1.0),
                "aliases": [str(alias) for alias in (raw_keywords.get("aliases") or []) if str(alias).strip()],
                "concepts": [str(concept) for concept in (raw_keywords.get("concepts") or []) if str(concept).strip()],
            })
            return entries
        for term, weight in raw_keywords.items():
            entries.append({
                "term": str(term),
                "weight": float(weight if isinstance(weight, (int, float)) else 1.0),
                "aliases": [],
                "concepts": [],
            })
        return entries

    if isinstance(raw_keywords, (list, tuple, set)):
        for item in raw_keywords:
            if isinstance(item, str):
                entries.append({"term": item, "weight": 1.0, "aliases": [], "concepts": []})
            elif isinstance(item, dict):
                term = str(item.get("term", "")).strip()
                if term:
                    entries.append({
                        "term": term,
                        "weight": float(item.get("weight", 1.0) or 1.0),
                        "aliases": [str(alias) for alias in (item.get("aliases") or []) if str(alias).strip()],
                        "concepts": [str(concept) for concept in (item.get("concepts") or []) if str(concept).strip()],
                    })
    return entries

def best_ngram_similarity(term: str, text: str) -> float:
    term_tokens = term.split()
    text_tokens = text.split()
    if not term_tokens or not text_tokens:
        return 0.0
    n = len(term_tokens)
    if len(text_tokens) < n:
        return SequenceMatcher(None, term, " ".join(text_tokens)).ratio()
    best = 0.0
    for idx in range(0, len(text_tokens) - n + 1):
        chunk = " ".join(text_tokens[idx:idx + n])
        best = max(best, SequenceMatcher(None, term, chunk).ratio())
    return best

def score_term_against_text(term: str, text: str, fuzzy_cfg: dict) -> tuple[float, bool]:
    if not term or not text:
        return 0.0, False
    normalized_term = normalize_text(term)
    if not normalized_term:
        return 0.0, False

    if f" {normalized_term} " in f" {text} ":
        return float(len(normalized_term.split())), True

    if not fuzzy_cfg.get("enabled", True):
        return 0.0, False

    similarity = best_ngram_similarity(normalized_term, text)
    fuzzy_threshold = float(fuzzy_cfg.get("threshold", 0.88))
    partial_threshold = float(fuzzy_cfg.get("partial_threshold", 0.92))
    boost = float(fuzzy_cfg.get("fuzzy_boost", 0.7))

    if similarity >= partial_threshold and len(normalized_term.split()) >= 2:
        return float(len(normalized_term.split()) * similarity * boost), False
    if similarity >= fuzzy_threshold:
        return float(len(normalized_term.split()) * similarity * boost), False
    return 0.0, False

def score_label_against_sources(entries: list[dict], sources: dict[str, str], cfg: dict) -> tuple[float, int, set[str], list[str]]:
    class_cfg = cfg.get("classification", {})
    field_weights = class_cfg.get("field_weights", {})
    fuzzy_cfg = class_cfg.get("fuzzy", {})

    score = 0.0
    matched = 0
    concepts: set[str] = set()
    matched_terms: list[str] = []

    for entry in entries:
        entry_weight = float(entry.get("weight", 1.0) or 1.0)
        candidates = [entry.get("term", "")] + list(entry.get("aliases", []))
        best_entry_score = 0.0
        matched_exact = False

        for candidate in candidates:
            normalized_candidate = normalize_text(candidate)
            if not normalized_candidate:
                continue
            for source_name, source_text in sources.items():
                if not source_text:
                    continue
                source_weight = float(field_weights.get(source_name, 1.0))
                term_score, exact = score_term_against_text(normalized_candidate, source_text, fuzzy_cfg)
                weighted_score = term_score * entry_weight * source_weight
                if weighted_score > best_entry_score:
                    best_entry_score = weighted_score
                    matched_exact = exact

        if best_entry_score > 0:
            score += best_entry_score
            matched += 1
            matched_terms.append(normalize_text(entry.get("term", "")))
            base_concepts = entry.get("concepts") or [entry.get("term", "")]
            for concept in base_concepts:
                normalized_concept = normalize_text(concept).replace(" ", "-")
                if normalized_concept and normalized_concept not in DOMAIN_STOPWORDS:
                    concepts.add(normalized_concept)
            if matched_exact:
                score += 0.25 * entry_weight

    return score, matched, concepts, matched_terms

def rank_labels(sources: dict[str, str], keyword_map: dict, cfg: dict, fallback: str) -> list[dict]:
    ranked: list[dict] = []
    for label, raw_keywords in keyword_map.items():
        if label == fallback:
            continue
        entries = iterate_keyword_entries(raw_keywords)
        if not entries:
            continue
        score, matched, concepts, matched_terms = score_label_against_sources(entries, sources, cfg)
        if score > 0:
            ranked.append({
                "label": label,
                "score": score,
                "matched": matched,
                "concepts": concepts,
                "matched_terms": matched_terms,
            })

    ranked.sort(key=lambda item: (item["score"], item["matched"]), reverse=True)
    return ranked

def score_label_matches(text: str, keywords: list[str]) -> tuple[int, int]:
    score = 0
    matched_keywords = 0
    for keyword in keywords:
        normalized_keyword = normalize_text(keyword)
        if not normalized_keyword:
            continue
        if f" {normalized_keyword} " in f" {text} ":
            matched_keywords += 1
            score += max(1, len(normalized_keyword.split()))
    return score, matched_keywords

def infer_label(text: str, keyword_map: dict, fallback: str) -> str:
    best_label = fallback
    best_score = 0
    best_match_count = 0

    for label, keywords in keyword_map.items():
        if not keywords:
            continue
        score, match_count = score_label_matches(text, keywords)
        if score > best_score or (score == best_score and match_count > best_match_count):
            best_label = label
            best_score = score
            best_match_count = match_count

    return best_label if best_score else fallback

def infer_primary_and_secondary_domains(sources: dict[str, str], cfg: dict) -> tuple[str, list[str], list[dict]]:
    ranked = rank_labels(sources, cfg["domain_keywords"], cfg, "META")
    if not ranked:
        return "META", [], []

    primary = ranked[0]["label"]
    primary_score = ranked[0]["score"]
    secondary_cfg = cfg.get("classification", {}).get("secondary_domains", {})
    max_count = int(secondary_cfg.get("max_count", 3))
    min_relative = float(secondary_cfg.get("min_relative_score", 0.35))

    secondary: list[str] = []
    for candidate in ranked[1:]:
        if len(secondary) >= max_count:
            break
        if primary_score <= 0:
            break
        if candidate["score"] >= primary_score * min_relative:
            secondary.append(candidate["label"])

    return primary, secondary, ranked

def infer_type_with_ranking(sources: dict[str, str], cfg: dict) -> tuple[str, list[dict]]:
    ranked = rank_labels(sources, cfg["type_keywords"], cfg, "PAPER")
    return (ranked[0]["label"], ranked) if ranked else ("PAPER", [])

def build_concept_tags(title: str, ranked_type: list[dict], ranked_domains: list[dict], cfg: dict) -> list[str]:
    concepts: list[str] = []
    seen: set[str] = set()

    for bucket in (ranked_type[:2], ranked_domains[:3]):
        for item in bucket:
            for concept in sorted(item.get("concepts", set())):
                normalized = normalize_text(concept).replace(" ", "-")
                if not normalized or normalized in DOMAIN_STOPWORDS:
                    continue
                if normalized not in seen:
                    seen.add(normalized)
                    concepts.append(normalized)

    if not concepts:
        title_tokens = [token for token in tokenize_text(title) if token not in FILLER_WORDS and token not in DOMAIN_STOPWORDS]
        if title_tokens:
            candidate = "-".join(title_tokens[:2])
            if candidate:
                concepts.append(candidate)

    concept_cfg = cfg.get("classification", {}).get("concept_tags", {})
    min_count = int(concept_cfg.get("min_count", 1))
    fallback_tag = normalize_text(concept_cfg.get("fallback", "general")).replace(" ", "-") or "general"

    while len(concepts) < min_count:
        if fallback_tag not in concepts:
            concepts.append(fallback_tag)
        else:
            break

    return concepts[:5]

def fetch_json(url: str, headers: dict[str, str], timeout: int) -> dict | None:
    request = urllib_request.Request(url, headers=headers)
    try:
        with urllib_request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib_error.URLError, urllib_error.HTTPError, json.JSONDecodeError) as exc:
        log.warning("HTTP metadata lookup failed for %s: %s", url, exc)
        return None

def build_multipart_body(path: Path, field_name: str = "input") -> tuple[bytes, str]:
    boundary = f"----vaultpipeline{int(time.time() * 1000)}"
    with path.open("rb") as fh:
        payload = fh.read()
    buffer = BytesIO()
    buffer.write(f"--{boundary}\r\n".encode("utf-8"))
    disposition = (
        f'Content-Disposition: form-data; name="{field_name}"; '
        f'filename="{path.name}"\r\n'
    )
    buffer.write(disposition.encode("utf-8"))
    buffer.write(b"Content-Type: application/pdf\r\n\r\n")
    buffer.write(payload)
    buffer.write(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    return buffer.getvalue(), boundary

def post_xml(url: str, path: Path, headers: dict[str, str], timeout: int) -> str:
    body, boundary = build_multipart_body(path)
    request_headers = {
        **headers,
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Accept": "application/xml",
    }
    request = urllib_request.Request(url, data=body, headers=request_headers, method="POST")
    with urllib_request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")

def parse_grobid_metadata(xml_text: str) -> dict:
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError as exc:
        log.warning("Could not parse GROBID response: %s", exc)
        return {}

    title = " ".join(root.findtext(".//tei:titleStmt/tei:title", default="", namespaces=ns).split())
    abstract = " ".join(root.findtext(".//tei:profileDesc/tei:abstract", default="", namespaces=ns).split())
    doi = root.findtext(".//tei:idno[@type='DOI']", default="", namespaces=ns).strip().lower()

    author_names: list[str] = []
    for author in root.findall(".//tei:sourceDesc//tei:author", ns):
        given_parts = [part.text.strip() for part in author.findall(".//tei:forename", ns) if part.text]
        surname = author.findtext(".//tei:surname", default="", namespaces=ns).strip()
        full_name = format_author_name(" ".join(given_parts), surname)
        if full_name:
            author_names.append(full_name)

    date_node = root.find(".//tei:publicationStmt/tei:date", ns)
    year = "0000"
    if date_node is not None:
        year = extract_year(date_node.attrib.get("when", "") or (date_node.text or ""))

    return {
        "title": title,
        "authors": author_names,
        "author": sanitize_author_token(author_names[0]) if author_names else "unknown",
        "year": year,
        "doi": doi,
        "abstract": abstract,
    }

def fetch_grobid_metadata(path: Path, cfg: dict) -> dict:
    enrichment_cfg = cfg["metadata_enrichment"]
    grobid_url = enrichment_cfg.get("grobid_url", "").strip()
    if not grobid_url:
        return {}
    endpoint = grobid_url.rstrip("/")
    if not endpoint.endswith("/api/processHeaderDocument"):
        endpoint = f"{endpoint}/api/processHeaderDocument"

    headers = {"User-Agent": enrichment_cfg.get("user_agent", DEFAULT_USER_AGENT)}
    try:
        xml_text = post_xml(endpoint, path, headers, enrichment_cfg.get("grobid_timeout_seconds", 20))
    except urllib_error.URLError as exc:
        log.warning("GROBID lookup failed for %s: %s", path.name, exc)
        return {}
    return parse_grobid_metadata(xml_text)

def parse_crossref_metadata(payload: dict) -> dict:
    message = payload.get("message") or {}
    title = " ".join((message.get("title") or [""])[0].split())
    authors = []
    for author in message.get("author") or []:
        full_name = format_author_name(author.get("given", ""), author.get("family", ""))
        if full_name:
            authors.append(full_name)
    abstract = " ".join((message.get("abstract") or "").split())
    year = "0000"
    for field in ("published-print", "published-online", "issued", "created"):
        date_parts = (((message.get(field) or {}).get("date-parts") or [[None]])[0])
        if date_parts and date_parts[0]:
            year = str(date_parts[0])
            break
    doi = (message.get("DOI") or "").lower()
    return {
        "title": title,
        "authors": authors,
        "author": sanitize_author_token(authors[0]) if authors else "unknown",
        "year": year,
        "doi": doi,
        "abstract": abstract,
    }

def fetch_crossref_metadata(doi: str, cfg: dict) -> dict:
    enrichment_cfg = cfg["metadata_enrichment"]
    if not enrichment_cfg.get("crossref_enabled", True) or not doi:
        return {}
    headers = {
        "Accept": "application/json",
        "User-Agent": enrichment_cfg.get("user_agent", DEFAULT_USER_AGENT),
    }
    url = f"https://api.crossref.org/works/{urllib_parse.quote(doi)}"
    payload = fetch_json(url, headers, enrichment_cfg.get("api_timeout_seconds", 15))
    return parse_crossref_metadata(payload) if payload else {}

def parse_semantic_scholar_metadata(payload: dict) -> dict:
    authors = [author.get("name", "").strip() for author in payload.get("authors") or [] if author.get("name")]
    return {
        "title": " ".join((payload.get("title") or "").split()),
        "authors": authors,
        "author": sanitize_author_token(authors[0]) if authors else "unknown",
        "year": str(payload.get("year") or "0000"),
        "doi": ((payload.get("externalIds") or {}).get("DOI") or "").lower(),
        "abstract": " ".join((payload.get("abstract") or "").split()),
    }

def fetch_semantic_scholar_metadata(doi: str, cfg: dict) -> dict:
    enrichment_cfg = cfg["metadata_enrichment"]
    if not enrichment_cfg.get("semantic_scholar_enabled", True) or not doi:
        return {}
    headers = {
        "Accept": "application/json",
        "User-Agent": enrichment_cfg.get("user_agent", DEFAULT_USER_AGENT),
    }
    fields = "title,authors,year,abstract,externalIds"
    url = (
        "https://api.semanticscholar.org/graph/v1/paper/DOI:"
        f"{urllib_parse.quote(doi)}?fields={urllib_parse.quote(fields)}"
    )
    payload = fetch_json(url, headers, enrichment_cfg.get("api_timeout_seconds", 15))
    return parse_semantic_scholar_metadata(payload) if payload else {}

def merge_metadata(base: dict, candidate: dict, source: str) -> None:
    if not candidate:
        return
    if source not in base["metadata_sources"]:
        base["metadata_sources"].append(source)
    if candidate.get("title") and prefer_title(base.get("title", ""), candidate["title"]):
        base["title"] = candidate["title"]
    if candidate.get("authors") and not base.get("authors"):
        base["authors"] = candidate["authors"]
    if candidate.get("author") and (base.get("author") in {"", "unknown"}):
        base["author"] = sanitize_author_token(candidate["author"])
    if candidate.get("year") and base.get("year") == "0000" and candidate["year"] != "0000":
        base["year"] = candidate["year"]
    if candidate.get("doi") and not base.get("doi"):
        base["doi"] = candidate["doi"]
    if candidate.get("abstract") and not base.get("abstract"):
        base["abstract"] = candidate["abstract"]

def extract_document_metadata(path: Path, cfg: dict) -> dict:
    title = path.stem
    author = "unknown"
    year = "0000"
    authors: list[str] = []
    pdf_info = extract_pdf_info(path)
    if pdf_info.get("title"):
        title = pdf_info["title"]
    if pdf_info.get("author"):
        authors = parse_author_list(pdf_info["author"])
        if authors:
            author = sanitize_author_token(authors[0])
    if pdf_info.get("creationdate"):
        year = extract_year(pdf_info["creationdate"])
    if pdf_info.get("moddate") and year == "0000":
        year = extract_year(pdf_info["moddate"])

    first_page_text = extract_first_page_text(path)
    front_matter_text = extract_front_matter_text(path)
    metadata = {
        "title": title,
        "author": author,
        "authors": authors,
        "year": year,
        "doi": extract_doi(" ".join(part for part in (title, front_matter_text) if part)),
        "abstract": "",
        "first_page_text": first_page_text,
        "metadata_sources": ["pdf"],
    }

    enrichment_cfg = cfg.get("metadata_enrichment", {})
    if enrichment_cfg.get("enabled", True):
        merge_metadata(metadata, fetch_grobid_metadata(path, cfg), "grobid")
        if metadata.get("doi"):
            merge_metadata(metadata, fetch_crossref_metadata(metadata["doi"], cfg), "crossref")
            merge_metadata(metadata, fetch_semantic_scholar_metadata(metadata["doi"], cfg), "semantic_scholar")

    metadata["author"] = sanitize_author_token(metadata.get("author", ""))
    metadata["year"] = metadata.get("year") or "0000"
    return metadata

# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------
def infer_type(classification_text: str, cfg: dict) -> str:
    return infer_label(classification_text, cfg["type_keywords"], "PAPER")

def infer_domain(classification_text: str, cfg: dict) -> str:
    return infer_label(classification_text, cfg["domain_keywords"], "META")

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

    document_metadata = extract_document_metadata(path, cfg)
    title = document_metadata["title"]
    author = document_metadata["author"]
    year = document_metadata["year"]
    classification_sources = build_classification_sources(path, document_metadata)
    short_title = slugify(title, cfg.get("slug_word_limit", 6))
    doc_type, ranked_type = infer_type_with_ranking(classification_sources, cfg)
    domain, secondary_domains, ranked_domains = infer_primary_and_secondary_domains(classification_sources, cfg)
    concept_tags = build_concept_tags(title, ranked_type, ranked_domains, cfg)

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
        "primary_domain": domain,
        "secondary_domains": secondary_domains,
        "year":     year,
        "title":    title,
        "author":   author,
        "authors":  document_metadata["authors"],
        "doi":      document_metadata["doi"],
        "abstract": document_metadata["abstract"],
        "metadata_sources": document_metadata["metadata_sources"],
        "filename": new_name,
        "source":   str(path),
        "processed_at": datetime.utcnow().isoformat() + "Z",
        "concept_tags": concept_tags,
        "classification_scores": {
            "type": [{"label": item["label"], "score": round(item["score"], 3)} for item in ranked_type[:5]],
            "domain": [{"label": item["label"], "score": round(item["score"], 3)} for item in ranked_domains[:5]],
        },
    }

    domain_tags = [domain.lower()] + [label.lower() for label in secondary_domains]
    merged_tags = []
    for tag in domain_tags + [doc_type.lower()] + concept_tags:
        if tag and tag not in merged_tags:
            merged_tags.append(tag)
    metadata["tags"] = merged_tags

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
                    result = process_file(pdf, cfg)
                    if result is not None:
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
    p.add_argument("--dry-run",  action="store_true", help="Process without moving files (for testing).")
    p.add_argument("--explain",  action="store_true", help="Print detailed classification scores (use with --dry-run --file).")
    return p

def format_score_breakdown(label: str, ranked: list[dict], max_lines: int = 10) -> str:
    if not ranked:
        return f"  {label}: (no candidates ranked)\n"
    
    output = f"  {label}:\n"
    for idx, item in enumerate(ranked[:max_lines], 1):
        score = item.get("score", 0)
        matched = item.get("matched", 0)
        output += f"    {idx}. {item['label']:15} score={score:7.2f}  matched_terms={matched}\n"
        concepts = item.get("concepts", set())
        if concepts:
            output += f"       → concepts: {', '.join(sorted(concepts)[:3])}\n"
    return output

def run_dry_run_explain(path: Path, cfg: dict, explain: bool = False) -> None:
    """Process a PDF without writing output; optionally print detailed scores."""
    log.info("DRY RUN: Processing %s (no files will be moved or written)", path.name)
    
    document_metadata = extract_document_metadata(path, cfg)
    title = document_metadata["title"]
    author = document_metadata["author"]
    year = document_metadata["year"]
    
    classification_sources = build_classification_sources(path, document_metadata)
    short_title = slugify(title, cfg.get("slug_word_limit", 6))
    doc_type, ranked_type = infer_type_with_ranking(classification_sources, cfg)
    domain, secondary_domains, ranked_domains = infer_primary_and_secondary_domains(classification_sources, cfg)
    concept_tags = build_concept_tags(title, ranked_type, ranked_domains, cfg)
    
    new_name = f"{doc_type}_{domain}_{year}_{short_title}_{author}.pdf"
    if len(new_name) > 100:
        fixed = len(doc_type) + len(domain) + len(author) + 12
        max_slug = max(3, 100 - fixed)
        trimmed = short_title[:max_slug].rstrip("-")
        new_name = f"{doc_type}_{domain}_{year}_{trimmed}_{author}.pdf"
    
    if explain:
        print("\n" + "=" * 80)
        print(f"CLASSIFICATION ANALYSIS: {path.name}")
        print("=" * 80)
        
        print("\nSources analyzed:")
        for source_name, source_text in classification_sources.items():
            preview = (source_text[:60] + "...") if len(source_text) > 60 else source_text
            print(f"  {source_name:12} ({len(source_text):4d} chars): {preview}")
        
        print("\n" + "-" * 80)
        print("TYPE Classification:")
        print("-" * 80)
        print(format_score_breakdown("Candidates", ranked_type, max_lines=8))
        print(f"  ✓ SELECTED: {doc_type}\n")
        
        print("-" * 80)
        print("DOMAIN Classification:")
        print("-" * 80)
        print(format_score_breakdown("Candidates", ranked_domains, max_lines=8))
        print(f"  ✓ PRIMARY: {domain}")
        if secondary_domains:
            print(f"  ✓ SECONDARY: {', '.join(secondary_domains)}")
        print()
        
        print("-" * 80)
        print("Extracted Metadata:")
        print("-" * 80)
        print(f"  Title:      {title}")
        print(f"  Author:     {author}")
        print(f"  Year:       {year}")
        print(f"  DOI:        {document_metadata.get('doi', '(none)')}")
        print(f"  Concepts:   {', '.join(concept_tags)}")
        print()
        
        print("-" * 80)
        print("Generated Filename:")
        print("-" * 80)
        print(f"  {new_name}")
        if not validate_filename(new_name):
            print(f"  ✗ VALIDATION FAILED")
        else:
            print(f"  ✓ Valid")
        print()
    else:
        print(f"DRY RUN: {path.name} → {new_name}")
        print(f"  TYPE={doc_type}, DOMAIN={domain}, concepts={concept_tags}")


def main() -> None:
    args   = build_parser().parse_args()
    cfg    = load_config()

    if args.validate:
        run_validate()
    elif args.watch:
        run_watch(cfg)
    elif args.dry_run:
        if not args.file:
            log.error("--dry-run requires --file <path>")
            raise SystemExit(1)
        p = Path(args.file)
        if not p.exists():
            log.error("File not found: %s", args.file)
            raise SystemExit(1)
        run_dry_run_explain(p, cfg, explain=args.explain)
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
