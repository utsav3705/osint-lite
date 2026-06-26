"""
Risk Scoring Engine V2
Weighted composite risk score (0–100) incorporating all OSINT data sources.
Backward-compatible: original calculate_risk() signature still works.
"""


# ── Weight configuration ───────────────────────────────────────
RISK_WEIGHTS = {
    "criminal":           40,
    "bankruptcy":         30,
    "sanction":           50,
    "negative_media":     25,
    "no_social_footprint": 15,
    "no_github":          20,
    "young_domain":       20,
    "low_github_followers": 10,
    "no_domain_data":     15,
}

MAX_SCORE = 100


def calculate_risk(github_data, username_data, whois_data,
                   news_data=None, social_data=None):
    """
    Compute a weighted risk score from all collected OSINT data.

    V2 accepts optional news_data and social_data.
    The original 3-argument call signature is preserved for backward compatibility.

    Args:
        github_data   (dict): Output from github_lookup().
        username_data (dict): Output from enumerate_user().
        whois_data    (dict): Output from lookup_domain().
        news_data     (dict, optional): Output from screen_media().
        social_data   (list, optional): Output from discover_profiles().

    Returns:
        dict: {"score": int, "classification": str, "factors": list}
    """
    news_data = news_data or {}
    social_data = social_data or []

    score = 0
    factors = []

    # ── GitHub presence ────────────────────────────────────
    if not github_data.get("found", False):
        score += RISK_WEIGHTS["no_github"]
        factors.append(f"No GitHub profile found (+{RISK_WEIGHTS['no_github']})")
    else:
        followers = github_data.get("followers", 0)
        if followers < 10:
            score += RISK_WEIGHTS["low_github_followers"]
            factors.append(
                f"Low GitHub followers ({followers} < 10) "
                f"(+{RISK_WEIGHTS['low_github_followers']})"
            )

    # ── Domain age ─────────────────────────────────────────
    if whois_data.get("found", False):
        domain_age = whois_data.get("domain_age")
        if domain_age is not None and domain_age < 2:
            score += RISK_WEIGHTS["young_domain"]
            factors.append(
                f"Domain is young ({domain_age} years < 2) "
                f"(+{RISK_WEIGHTS['young_domain']})"
            )
    else:
        score += RISK_WEIGHTS["no_domain_data"]
        factors.append(
            f"No domain / WHOIS data available (+{RISK_WEIGHTS['no_domain_data']})"
        )

    # ── Social footprint ───────────────────────────────────
    social_found = 0
    if social_data:
        social_found = sum(1 for s in social_data if s.get("found"))
    elif username_data:
        social_found = sum(1 for v in username_data.values() if v)

    if social_found == 0:
        score += RISK_WEIGHTS["no_social_footprint"]
        factors.append(
            f"No social media footprint found "
            f"(+{RISK_WEIGHTS['no_social_footprint']})"
        )

    # ── Adverse media ──────────────────────────────────────
    neg_count = news_data.get("negative_count", 0)
    if neg_count > 0:
        score += RISK_WEIGHTS["negative_media"]
        factors.append(
            f"{neg_count} adverse media article(s) detected "
            f"(+{RISK_WEIGHTS['negative_media']})"
        )

    # Check for specific keyword categories in news
    keywords_matched = news_data.get("keywords_matched", [])
    for kw in keywords_matched:
        if kw in ("sanctions",):
            score += RISK_WEIGHTS["sanction"]
            factors.append(
                f"Sanction-related media detected (keyword: {kw}) "
                f"(+{RISK_WEIGHTS['sanction']})"
            )
            break  # Only apply once

    for kw in keywords_matched:
        if kw in ("fraud", "arrest", "indictment", "embezzlement"):
            score += RISK_WEIGHTS["criminal"]
            factors.append(
                f"Criminal-related media detected (keyword: {kw}) "
                f"(+{RISK_WEIGHTS['criminal']})"
            )
            break

    for kw in keywords_matched:
        if kw in ("bankruptcy",):
            score += RISK_WEIGHTS["bankruptcy"]
            factors.append(
                f"Bankruptcy-related media detected "
                f"(+{RISK_WEIGHTS['bankruptcy']})"
            )
            break

    # ── Cap at MAX_SCORE ───────────────────────────────────
    score = min(score, MAX_SCORE)

    # ── Classification ─────────────────────────────────────
    if score <= 30:
        classification = "Low"
    elif score <= 60:
        classification = "Medium"
    else:
        classification = "High"

    return {
        "score": score,
        "classification": classification,
        "factors": factors,
    }
