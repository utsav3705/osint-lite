"""
Domain Intelligence Module
Performs WHOIS lookups to extract registrar, dates, country, and domain age.
"""

import whois
from datetime import datetime


def lookup_domain(domain):
    """
    Perform a WHOIS lookup on the given domain.

    Args:
        domain (str): The domain to look up (e.g. "example.com").

    Returns:
        dict: WHOIS intelligence or error information.
    """
    if not domain or not domain.strip():
        return {"error": "No domain provided", "found": False}

    # Strip protocol and path if the user pasted a full URL
    domain = domain.strip()
    for prefix in ("https://", "http://", "www."):
        if domain.lower().startswith(prefix):
            domain = domain[len(prefix):]
    domain = domain.rstrip("/").split("/")[0]

    try:
        w = whois.whois(domain)

        if not w or not w.domain_name:
            return {"error": "Domain not found or WHOIS data unavailable", "found": False}

        # Creation date may be a list — take the first
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        expiration_date = w.expiration_date
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]

        # Calculate domain age in years
        domain_age = None
        if creation_date and isinstance(creation_date, datetime):
            # Normalize to naive datetime to avoid offset-aware vs offset-naive errors
            naive_creation = creation_date.replace(tzinfo=None) if creation_date.tzinfo else creation_date
            delta = datetime.now() - naive_creation
            domain_age = round(delta.days / 365.25, 1)

        # Country may also be a list
        country = w.country
        if isinstance(country, list):
            country = country[0] if country else "N/A"

        registrar = w.registrar or "N/A"

        return {
            "found": True,
            "domain": domain,
            "registrar": registrar,
            "creation_date": str(creation_date) if creation_date else "N/A",
            "expiration_date": str(expiration_date) if expiration_date else "N/A",
            "country": country or "N/A",
            "domain_age": domain_age,
        }

    except Exception as e:
        return {"error": f"WHOIS lookup failed: {str(e)}", "found": False}
