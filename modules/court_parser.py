"""
Court Document Parser Module
Extracts structured data from uploaded PDF court documents
using pdfplumber for text extraction and regex/spaCy for entity recognition.
"""

import os
import re

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        nlp = None
except ImportError:
    spacy = None
    nlp = None


# ── Regex patterns for court document fields ──────────────────

CASE_NUMBER_PATTERNS = [
    r'(?:Case|Cause|Docket)\s*(?:No\.?|Number|#)\s*[:.]?\s*([A-Z0-9][\w\-:\/]+)',
    r'(\d{1,2}:\d{2}-[a-z]{2}-\d{4,})',  # Federal format: 1:23-cv-12345
    r'(\d{4}-[A-Z]{2,4}-\d{3,})',          # State format: 2024-CI-1234
]

AMOUNT_PATTERNS = [
    r'\$[\d,]+(?:\.\d{2})?',
    r'(?:USD|dollars?)\s*[\d,]+(?:\.\d{2})?',
]

DATE_PATTERNS = [
    r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
    r'\d{1,2}/\d{1,2}/\d{2,4}',
    r'\d{4}-\d{2}-\d{2}',
]

VERDICT_KEYWORDS = [
    "guilty", "not guilty", "dismissed", "sustained",
    "overruled", "granted", "denied", "judgment for",
    "settled", "acquitted", "convicted", "liable", "not liable",
]


def parse_court_document(pdf_path):
    """
    Parse a PDF court document and extract structured intelligence.

    Args:
        pdf_path (str): Absolute path to the uploaded PDF file.

    Returns:
        dict: Extracted fields or error information.
    """
    if not pdf_path or not os.path.exists(pdf_path):
        return {"error": "PDF file not found", "parsed": False}

    if pdfplumber is None:
        return {"error": "pdfplumber is not installed", "parsed": False}

    # ── Extract raw text from PDF ──────────────────────────
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
    except Exception as e:
        return {"error": f"Failed to read PDF: {str(e)}", "parsed": False}

    if not full_text.strip():
        return {"error": "No text could be extracted from the PDF", "parsed": False}

    # ── Extract fields ─────────────────────────────────────
    result = {
        "parsed": True,
        "case_number": _extract_case_number(full_text),
        "plaintiff": "",
        "defendant": "",
        "judge": "",
        "court": _extract_court(full_text),
        "dates": _extract_dates(full_text),
        "amounts": _extract_amounts(full_text),
        "verdict": _extract_verdict(full_text),
        "text_preview": full_text[:1000],
    }

    # ── Use spaCy NER for person/org extraction ────────────
    if nlp is not None:
        _extract_entities_spacy(full_text, result)
    else:
        _extract_entities_regex(full_text, result)

    return result


# ── Private helpers ────────────────────────────────────────────

def _extract_case_number(text):
    """Find a case / docket number in the text."""
    for pattern in CASE_NUMBER_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1) if match.lastindex else match.group(0)
    return "N/A"


def _extract_court(text):
    """Identify the court name."""
    patterns = [
        r'(?:IN THE\s+)?((?:UNITED STATES\s+)?(?:DISTRICT|CIRCUIT|SUPREME|SUPERIOR|COUNTY|MUNICIPAL|BANKRUPTCY|APPELLATE)\s+COURT[^\n]{0,80})',
        r'((?:Supreme|District|Circuit|Superior|County)\s+Court\s+of[^\n]{0,60})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()[:120]
    return "N/A"


def _extract_dates(text):
    """Extract all date mentions from the text."""
    dates = []
    for pattern in DATE_PATTERNS:
        matches = re.findall(pattern, text)
        dates.extend(matches)
    # De-duplicate and limit
    return list(dict.fromkeys(dates))[:10]


def _extract_amounts(text):
    """Extract monetary amounts."""
    amounts = []
    for pattern in AMOUNT_PATTERNS:
        matches = re.findall(pattern, text)
        amounts.extend(matches)
    return list(dict.fromkeys(amounts))[:10]


def _extract_verdict(text):
    """Look for verdict / judgment language."""
    text_lower = text.lower()
    for keyword in VERDICT_KEYWORDS:
        if keyword in text_lower:
            # Extract the sentence containing the verdict keyword
            idx = text_lower.index(keyword)
            start = max(0, text_lower.rfind(".", 0, idx) + 1)
            end = text_lower.find(".", idx)
            if end == -1:
                end = min(len(text), idx + 200)
            sentence = text[start:end + 1].strip()
            if sentence:
                return sentence[:300]
    return "N/A"


def _extract_entities_spacy(text, result):
    """Use spaCy NER to find people, organisations, and roles."""
    # Process first 5000 chars to stay fast
    doc = nlp(text[:5000])

    persons = []
    orgs = []
    for ent in doc.ents:
        if ent.label_ == "PERSON" and ent.text not in persons:
            persons.append(ent.text)
        elif ent.label_ == "ORG" and ent.text not in orgs:
            orgs.append(ent.text)

    # Heuristic: look for plaintiff/defendant patterns
    plaintiff_match = re.search(
        r'(?:Plaintiff|Petitioner)[:\s]*([A-Z][A-Za-z\s,.]+?)(?:\n|,\s*(?:v\.|vs\.|versus))',
        text[:3000], re.IGNORECASE
    )
    defendant_match = re.search(
        r'(?:Defendant|Respondent)[:\s]*([A-Z][A-Za-z\s,.]+?)(?:\n|,)',
        text[:3000], re.IGNORECASE
    )

    if plaintiff_match:
        result["plaintiff"] = plaintiff_match.group(1).strip()[:100]
    elif persons:
        result["plaintiff"] = persons[0] if persons else "N/A"

    if defendant_match:
        result["defendant"] = defendant_match.group(1).strip()[:100]
    elif len(persons) > 1:
        result["defendant"] = persons[1]

    # Judge
    judge_match = re.search(
        r'(?:Judge|Justice|Hon\.|Honorable)\s+([A-Z][A-Za-z\s.]+?)(?:\n|,|presiding)',
        text[:3000], re.IGNORECASE
    )
    if judge_match:
        result["judge"] = judge_match.group(1).strip()[:80]

    if not result["plaintiff"]:
        result["plaintiff"] = "N/A"
    if not result["defendant"]:
        result["defendant"] = "N/A"
    if not result["judge"]:
        result["judge"] = "N/A"


def _extract_entities_regex(text, result):
    """Fallback: use regex only when spaCy is not available."""
    plaintiff_match = re.search(
        r'(?:Plaintiff|Petitioner)[:\s]*([A-Z][A-Za-z\s,.]+?)(?:\n|,\s*(?:v\.|vs\.|versus))',
        text[:3000], re.IGNORECASE
    )
    defendant_match = re.search(
        r'(?:Defendant|Respondent)[:\s]*([A-Z][A-Za-z\s,.]+?)(?:\n|,)',
        text[:3000], re.IGNORECASE
    )
    judge_match = re.search(
        r'(?:Judge|Justice|Hon\.|Honorable)\s+([A-Z][A-Za-z\s.]+?)(?:\n|,|presiding)',
        text[:3000], re.IGNORECASE
    )

    result["plaintiff"] = plaintiff_match.group(1).strip()[:100] if plaintiff_match else "N/A"
    result["defendant"] = defendant_match.group(1).strip()[:100] if defendant_match else "N/A"
    result["judge"] = judge_match.group(1).strip()[:80] if judge_match else "N/A"
