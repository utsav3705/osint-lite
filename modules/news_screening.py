"""
Adverse Media Screening Module
Searches public news sources for negative / adverse mentions of a subject.
Uses Google News RSS feeds — no API key required.
"""

import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from datetime import datetime

# Adverse keywords used in due-diligence screening
ADVERSE_KEYWORDS = [
    "fraud",
    "corruption",
    "bankruptcy",
    "money laundering",
    "bribery",
    "ponzi",
    "sanctions",
    "arrest",
    "indictment",
    "embezzlement",
    "investigation",
    "lawsuit",
]

HEADERS = {
    "User-Agent": "OSINT-Pro/2.0 (Due Diligence Investigation Platform)",
}


def screen_media(name):
    """
    Screen a subject for adverse media mentions.

    Args:
        name (str): Subject name to screen (e.g. "John Doe").

    Returns:
        dict: {
            "articles": list[dict],   # headline, date, source, link, keyword
            "negative_count": int,     # total adverse articles found
            "keywords_matched": list,  # which keywords had hits
        }
    """
    if not name or not name.strip():
        return {"articles": [], "negative_count": 0, "keywords_matched": []}

    name = name.strip()
    articles = []
    keywords_matched = set()
    seen_titles = set()

    for keyword in ADVERSE_KEYWORDS:
        query = f"{name} {keyword}"
        try:
            rss_url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en&gl=US&ceid=US:en"
            resp = requests.get(rss_url, timeout=8, headers=HEADERS)

            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.content, "xml")
            items = soup.find_all("item", limit=3)  # Top 3 per keyword

            for item in items:
                title = item.find("title")
                link = item.find("link")
                pub_date = item.find("pubDate")
                source = item.find("source")

                title_text = title.get_text(strip=True) if title else "No title"

                # De-duplicate by title
                if title_text.lower() in seen_titles:
                    continue
                seen_titles.add(title_text.lower())

                # Check relevance — the subject name should appear in the title
                if name.lower().split()[0] not in title_text.lower():
                    continue

                articles.append({
                    "headline": title_text,
                    "date": _parse_date(pub_date.get_text(strip=True) if pub_date else ""),
                    "source": source.get_text(strip=True) if source else "Unknown",
                    "link": link.get_text(strip=True) if link else "#",
                    "keyword": keyword,
                })
                keywords_matched.add(keyword)

        except requests.exceptions.RequestException:
            continue
        except Exception:
            continue

    return {
        "articles": articles[:20],  # Cap at 20 articles total
        "negative_count": len(articles),
        "keywords_matched": sorted(keywords_matched),
    }


def _parse_date(date_str):
    """Parse an RSS pubDate string into a readable format."""
    if not date_str:
        return "N/A"
    try:
        # RSS format: "Mon, 01 Jan 2026 12:00:00 GMT"
        dt = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return date_str[:16] if len(date_str) > 16 else date_str
