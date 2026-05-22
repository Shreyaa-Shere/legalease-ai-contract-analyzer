"""
Text Extraction Utility Module

Extracts text from PDF and DOCX files using pdfplumber (primary) and PyPDF2 (fallback).
"""

import re
import logging
import unicodedata
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from docx import Document
except ImportError:
    Document = None

logger = logging.getLogger(__name__)


def _line_looks_real(line):
    """
    Return True if a line contains enough real English text to be worth keeping.

    Garbage lines from PDFs with broken font encoding look like:
      "ï q ï ï ð ï q ñ q ð"   (isolated single-char tokens, no real words)
      "æ þ ü å (cid:0) ý"     (unmapped chars, no words)
      "P P P P q r t t s"     (same pattern)

    Real contract text has multi-character words and mostly ASCII characters.
    """
    stripped = line.strip()
    if not stripped:
        return True  # keep blank lines (paragraph separators)

    # Remove (cid:N) tokens from consideration
    without_cid = re.sub(r'\(cid:\d+\)', '', stripped).strip()

    tokens = without_cid.split()
    if not tokens:
        return False  # nothing left after stripping cid tokens

    # Count tokens that look like real words: ≥3 chars with 3+ consecutive letters
    real_word_count = sum(
        1 for t in tokens
        if len(t) >= 3 and re.search(r'[A-Za-z]{3,}', t)
    )

    # A line is "real" if:
    # (a) it has at least one real word, OR
    # (b) it is a short heading/number (≤ 40 chars) — e.g. "5. KEYS."
    if real_word_count >= 1:
        return True
    if len(stripped) <= 40:
        # Short line: keep only if it has at least 3 consecutive ASCII letters
        return bool(re.search(r'[A-Za-z]{3,}', stripped))

    return False


def clean_text(text):
    """
    Remove garbage characters from PDF-extracted text.

    PDFs with custom/broken font encodings produce two kinds of garbage:
    1. Non-standard Unicode glyphs (arrows, ornamental brackets, dingbats)
    2. Lines of isolated single characters from form checkboxes / fill fields

    Strategy:
    - Remove (cid:N) unmapped-character tokens
    - Character filter: keep printable ASCII + common Latin only
    - Line filter: discard lines that contain no real English words
    """
    # Step 0: remove (cid:N) unmapped character placeholders
    text = re.sub(r'\(cid:\d+\)', ' ', text)

    # Step 1: character-level filter — keep only printable ASCII and common Latin
    result = []
    for char in text:
        cp = ord(char)
        if char in '\n\r\t':
            result.append(char)
        elif 0x20 <= cp <= 0x7E:      # printable ASCII (space through ~)
            result.append(char)
        elif unicodedata.category(char) == 'Sc':  # currency ($, €, £…)
            result.append(char)
        else:
            result.append(' ')        # replace everything else with space

    intermediate = ''.join(result)
    # Collapse spaces within lines
    intermediate = re.sub(r'[ \t]+', ' ', intermediate)
    intermediate = re.sub(r' *\n *', '\n', intermediate)

    # Step 2: line-level filter — drop lines with no real words
    kept = [line for line in intermediate.splitlines() if _line_looks_real(line)]

    cleaned = '\n'.join(kept)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()


def extract_text_from_pdf(file_path):
    """Extract text from a PDF, preferring pdfplumber over PyPDF2."""

    # --- pdfplumber (primary) ---
    if pdfplumber is not None:
        try:
            pages_text = []
            with pdfplumber.open(file_path) as pdf:
                num_pages = len(pdf.pages)
                logger.info(f"Extracting text from PDF with {num_pages} pages (pdfplumber)")
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ''
                    pages_text.append(page_text)
                    if i < num_pages - 1:
                        pages_text.append(f"\n\n--- Page {i + 1} ---\n\n")
            raw = ''.join(pages_text)
            logger.info(f"pdfplumber extracted {len(raw)} characters")
            return raw
        except Exception as e:
            logger.warning(f"pdfplumber failed ({e}), falling back to PyPDF2")

    # --- PyPDF2 (fallback) ---
    if PyPDF2 is None:
        logger.error("No PDF extraction library available.")
        return ""

    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            num_pages = len(reader.pages)
            logger.info(f"Extracting text from PDF with {num_pages} pages (PyPDF2)")
            parts = []
            for i, page in enumerate(reader.pages):
                parts.append(page.extract_text() or '')
                if i < num_pages - 1:
                    parts.append(f"\n\n--- Page {i + 1} ---\n\n")
            raw = ''.join(parts)
            logger.info(f"PyPDF2 extracted {len(raw)} characters")
            return raw
    except Exception as e:
        logger.error(f"PyPDF2 extraction failed: {e}")
        return ""


def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    if Document is None:
        logger.error("python-docx not installed.")
        return ""
    try:
        doc = Document(file_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        text = "\n\n".join(paragraphs)
        logger.info(f"Extracted {len(text)} characters from DOCX")
        return text
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        return ""


def extract_text_from_file(file_path, file_type):
    """Extract and clean text from a PDF or DOCX file."""
    file_path = Path(file_path)
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return ""

    file_type_lower = file_type.lower()
    if file_type_lower == 'pdf':
        raw = extract_text_from_pdf(file_path)
    elif file_type_lower == 'docx':
        raw = extract_text_from_docx(file_path)
    else:
        logger.warning(f"Unsupported file type: {file_type}")
        return ""

    # Remove NUL bytes (PostgreSQL rejects them) then clean garbage characters
    raw = raw.replace('\x00', '')
    cleaned = clean_text(raw)
    logger.info(f"After cleaning: {len(cleaned)} characters (was {len(raw)})")
    return cleaned
