"""
AI Investigator Summary Module
Generates a structured executive summary from all collected OSINT data.
Rule-based summariser — no external LLM dependency.
"""


def generate_investigation_summary(
    subject_info,
    github_data=None,
    username_data=None,
    whois_data=None,
    risk_data=None,
    aliases=None,
    social_data=None,
    news_data=None,
    company_data=None,
):
    """
    Produce a structured AI-style investigation summary.

    Returns:
        dict: {
            "executive_summary": str,
            "red_flags": list[str],
            "observations": list[str],
            "recommendations": list[str],
        }
    """
    github_data = github_data or {}
    username_data = username_data or {}
    whois_data = whois_data or {}
    risk_data = risk_data or {}
    aliases = aliases or []
    social_data = social_data or []
    news_data = news_data or {}
    company_data = company_data or {}

    name = subject_info.get("name", "The subject") or "The subject"
    score = risk_data.get("score", 0)
    classification = risk_data.get("classification", "Unknown")

    # ── Executive Summary ──────────────────────────────────
    exec_parts = [
        f"An open-source intelligence investigation was conducted on {name}.",
    ]

    # Digital presence assessment
    social_found = sum(1 for s in social_data if s.get("found")) if social_data else 0
    social_total = len(social_data) if social_data else 0

    if social_found > 0:
        exec_parts.append(
            f"Subject maintains a digital presence across {social_found} of "
            f"{social_total} platforms checked."
        )
    else:
        exec_parts.append("Subject has minimal to no detectable digital footprint.")

    # GitHub assessment
    if github_data.get("found"):
        repos = github_data.get("repos", 0)
        followers = github_data.get("followers", 0)
        exec_parts.append(
            f"A GitHub profile was identified with {repos} public repositories "
            f"and {followers} followers."
        )
    else:
        exec_parts.append("No GitHub profile was identified.")

    # News / media assessment
    neg_count = news_data.get("negative_count", 0)
    if neg_count > 0:
        exec_parts.append(
            f"{neg_count} adverse media article(s) were discovered during screening."
        )
    else:
        exec_parts.append("No adverse media mentions were identified.")

    # Domain assessment
    if whois_data.get("found"):
        age = whois_data.get("domain_age")
        if age is not None:
            exec_parts.append(
                f"The associated domain has been registered for approximately {age} years."
            )

    exec_parts.append(
        f"Overall risk classification: {classification} ({score}/100)."
    )

    executive_summary = " ".join(exec_parts)

    # ── Red Flags ──────────────────────────────────────────
    red_flags = []

    if neg_count > 0:
        keywords = news_data.get("keywords_matched", [])
        red_flags.append(
            f"Adverse media detected: {neg_count} article(s) matching keywords "
            f"[{', '.join(keywords)}]."
        )

    if not github_data.get("found") and social_found == 0:
        red_flags.append(
            "No digital footprint detected — subject may be using alternative identities "
            "or deliberately maintaining low visibility."
        )

    if whois_data.get("found"):
        domain_age = whois_data.get("domain_age")
        if domain_age is not None and domain_age < 2:
            red_flags.append(
                f"Associated domain is only {domain_age} years old — "
                f"newly registered domains may indicate recently created entities."
            )

    if github_data.get("found") and github_data.get("followers", 0) < 5:
        red_flags.append(
            "GitHub profile has very low engagement — may be a placeholder or rarely used account."
        )

    if score >= 60:
        red_flags.append(
            f"Composite risk score is {score}/100 (HIGH) — enhanced due diligence recommended."
        )

    if not red_flags:
        red_flags.append("No significant red flags identified during this investigation.")

    # ── Observations ───────────────────────────────────────
    observations = []

    if aliases:
        observations.append(
            f"{len(aliases)} potential username aliases were generated from the subject's name."
        )

    if social_found > 0:
        found_platforms = [s["platform"] for s in social_data if s.get("found")]
        observations.append(
            f"Active profiles found on: {', '.join(found_platforms)}."
        )

    if company_data.get("found"):
        observations.append(
            f"Company domain verified — registered in {company_data.get('country', 'N/A')}."
        )

    if username_data:
        total_found = sum(1 for v in username_data.values() if v)
        observations.append(
            f"Username enumeration: found on {total_found} of {len(username_data)} platforms."
        )

    if not observations:
        observations.append("Limited data available for detailed observations.")

    # ── Recommendations ────────────────────────────────────
    recommendations = []

    if score >= 60:
        recommendations.append(
            "Conduct enhanced due diligence including manual review of adverse media articles."
        )
        recommendations.append(
            "Consider engaging a professional investigation firm for deeper analysis."
        )
    elif score >= 30:
        recommendations.append(
            "Standard due diligence checks are sufficient. Monitor for new adverse information."
        )
    else:
        recommendations.append(
            "No elevated risk indicators detected. Routine monitoring recommended."
        )

    if neg_count > 0:
        recommendations.append(
            "Manually review each adverse media article for relevance and accuracy."
        )

    if not github_data.get("found") and social_found == 0:
        recommendations.append(
            "Attempt alternative name spellings or known aliases to expand the search."
        )

    recommendations.append(
        "This report is based solely on publicly available information and should be used "
        "as a preliminary assessment. Further investigation may be warranted."
    )

    return {
        "executive_summary": executive_summary,
        "red_flags": red_flags,
        "observations": observations,
        "recommendations": recommendations,
    }
