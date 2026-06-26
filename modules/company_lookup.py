"""
Company Intelligence Module
Gathers basic company information using WHOIS and public web data.
"""

import requests
import whois
from datetime import datetime
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "OSINT-Pro/2.0 (Due Diligence Investigation Platform)",
    "Accept": "text/html,application/xhtml+xml",
}


def lookup_company(company_name):
    """
    Gather open-source intelligence on a company.

    Args:
        company_name (str): Company or organisation name.

    Returns:
        dict: Company profile data or error information.
    """
    if not company_name or not company_name.strip():
        return {"error": "No company name provided", "found": False}

    company_name = company_name.strip()
    result = {
        "found": False,
        "name": company_name,
        "website": "",
        "domain_age": None,
        "country": "N/A",
        "industry": "N/A",
        "description": "N/A",
        "executives": [],
    }

    # ── Step 1: Try to find the company website via a search-style heuristic ──
    domain_guess = _guess_domain(company_name)
    if domain_guess:
        result["website"] = f"https://{domain_guess}"

        # ── Step 2: WHOIS lookup on the guessed domain ──
        try:
            w = whois.whois(domain_guess)
            if w and w.domain_name:
                result["found"] = True

                creation_date = w.creation_date
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]

                if creation_date and isinstance(creation_date, datetime):
                    naive = creation_date.replace(tzinfo=None) if creation_date.tzinfo else creation_date
                    delta = datetime.now() - naive
                    result["domain_age"] = round(delta.days / 365.25, 1)

                country = w.country
                if isinstance(country, list):
                    country = country[0] if country else "N/A"
                result["country"] = country or "N/A"

        except Exception:
            pass

        # ── Step 3: Scrape homepage for meta description ──
        try:
            resp = requests.get(
                result["website"], timeout=8, headers=HEADERS, allow_redirects=True
            )
            if resp.status_code == 200:
                result["found"] = True
                soup = BeautifulSoup(resp.text, "html.parser")

                # Meta description
                meta_desc = soup.find("meta", attrs={"name": "description"})
                if meta_desc and meta_desc.get("content"):
                    result["description"] = meta_desc["content"][:300]

                # Try to extract title as a fallback name
                title_tag = soup.find("title")
                if title_tag and title_tag.string:
                    result["page_title"] = title_tag.string.strip()[:120]

        except requests.exceptions.RequestException:
            pass

    # If we still haven't found anything, try a direct domain from the name
    if not result["found"]:
        # Try common TLDs
        for tld in [".com", ".net", ".org", ".io"]:
            slug = company_name.lower().replace(" ", "").replace(",", "").replace(".", "")
            test_domain = slug + tld
            try:
                w = whois.whois(test_domain)
                if w and w.domain_name:
                    result["found"] = True
                    result["website"] = f"https://{test_domain}"

                    creation_date = w.creation_date
                    if isinstance(creation_date, list):
                        creation_date = creation_date[0]
                    if creation_date and isinstance(creation_date, datetime):
                        naive = creation_date.replace(tzinfo=None) if creation_date.tzinfo else creation_date
                        delta = datetime.now() - naive
                        result["domain_age"] = round(delta.days / 365.25, 1)

                    country = w.country
                    if isinstance(country, list):
                        country = country[0] if country else "N/A"
                    result["country"] = country or "N/A"
                    break
            except Exception:
                continue

    return result


def _guess_domain(company_name):
    """
    Generate the most likely domain for a company name.
    E.g. "Tesla" → "tesla.com", "Open AI" → "openai.com"
    """
    slug = (
        company_name.lower()
        .replace(" ", "")
        .replace(",", "")
        .replace(".", "")
        .replace("inc", "")
        .replace("ltd", "")
        .replace("llc", "")
        .replace("corp", "")
        .strip()
    )
    if slug:
        return f"{slug}.com"
    return None
