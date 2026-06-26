"""
PDF Report Generator V2 (OSINT-Pro)
Creates professional investigation reports using ReportLab.
Extended with: Aliases, Social Discovery, Media Screening, Company Intel,
Court Records, and AI Summary sections.
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)


# Directory where reports are saved
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_reports")


def _ensure_reports_dir():
    os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_pdf(subject_info, github_data, username_data, whois_data, risk_data,
                 aliases=None, social_data=None, news_data=None,
                 company_data=None, court_data=None, ai_summary=None):
    """
    Generate a styled PDF investigation report.

    V2 accepts optional new data sources. The original 5-argument call
    still works for backward compatibility.

    Returns:
        str: The filename of the generated PDF.
    """
    aliases = aliases or []
    social_data = social_data or []
    news_data = news_data or {}
    company_data = company_data or {}
    court_data = court_data or {}
    ai_summary = ai_summary or {}

    _ensure_reports_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in (subject_info.get("name") or "subject"))
    filename = f"OSINT_Pro_Report_{safe_name}_{timestamp}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#0a1628"),
        spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="SectionHead",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1a73e8"),
        spaceBefore=16,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="BodyText2",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        name="SmallText",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#555555"),
    ))

    elements = []
    section_num = 1

    # ── Title ──────────────────────────────────────────────
    elements.append(Paragraph("OSINT-Pro Investigation Report", styles["ReportTitle"]))
    elements.append(Paragraph(
        f'<font color="#666666">Professional Due Diligence &amp; Open Source Intelligence Platform</font>',
        styles["BodyText2"],
    ))
    elements.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        styles["BodyText2"],
    ))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a73e8")))
    elements.append(Spacer(1, 12))

    # ── 1. Subject Information ─────────────────────────────
    elements.append(Paragraph(f"{section_num}. Subject Information", styles["SectionHead"]))
    section_num += 1
    subject_table_data = [
        ["Field", "Value"],
        ["Name", subject_info.get("name", "N/A")],
        ["Username", subject_info.get("username", "N/A")],
        ["Email", subject_info.get("email", "N/A")],
        ["Company", subject_info.get("company", "N/A")],
        ["Website", subject_info.get("website", "N/A")],
    ]
    elements.append(_styled_table(subject_table_data))
    elements.append(Spacer(1, 12))

    # ── 2. GitHub Intelligence ─────────────────────────────
    elements.append(Paragraph(f"{section_num}. GitHub Intelligence", styles["SectionHead"]))
    section_num += 1
    if github_data.get("found"):
        gh_table = [
            ["Field", "Value"],
            ["Name", str(github_data.get("name", "N/A"))],
            ["Bio", str(github_data.get("bio", "N/A"))],
            ["Followers", str(github_data.get("followers", 0))],
            ["Following", str(github_data.get("following", 0))],
            ["Repositories", str(github_data.get("repos", 0))],
            ["Account Created", str(github_data.get("created_at", "N/A"))],
            ["Profile URL", str(github_data.get("profile_url", "N/A"))],
        ]
        elements.append(_styled_table(gh_table))
    else:
        elements.append(Paragraph(
            f"GitHub profile not found. {github_data.get('error', '')}",
            styles["BodyText2"],
        ))
    elements.append(Spacer(1, 12))

    # ── 3. Aliases ─────────────────────────────────────────
    elements.append(Paragraph(f"{section_num}. Generated Aliases", styles["SectionHead"]))
    section_num += 1
    if aliases:
        alias_text = ", ".join(aliases[:20])
        elements.append(Paragraph(
            f"The following username aliases were generated: <b>{alias_text}</b>",
            styles["BodyText2"],
        ))
        elements.append(Paragraph(
            f"Total aliases: {len(aliases)}", styles["SmallText"],
        ))
    else:
        elements.append(Paragraph("No aliases generated.", styles["BodyText2"]))
    elements.append(Spacer(1, 12))

    # ── 4. Social Discovery ────────────────────────────────
    elements.append(Paragraph(f"{section_num}. Social Media Discovery", styles["SectionHead"]))
    section_num += 1
    if social_data:
        social_table = [["Platform", "Status", "Profile URL", "Followers"]]
        for s in social_data:
            social_table.append([
                s.get("platform", ""),
                "Found" if s.get("found") else "Not Found",
                s.get("url", "N/A") or "N/A",
                str(s.get("followers", "N/A")) if s.get("followers") is not None else "N/A",
            ])
        elements.append(_styled_table(social_table))
    else:
        elements.append(Paragraph("No social discovery data available.", styles["BodyText2"]))
    elements.append(Spacer(1, 12))

    # ── 5. Username Enumeration ────────────────────────────
    elements.append(Paragraph(f"{section_num}. Username Enumeration", styles["SectionHead"]))
    section_num += 1
    if username_data:
        user_table = [["Platform", "Status"]]
        for platform, found in username_data.items():
            user_table.append([platform, "Found" if found else "Not Found"])
        elements.append(_styled_table(user_table))
    else:
        elements.append(Paragraph("No username enumeration data.", styles["BodyText2"]))
    elements.append(Spacer(1, 12))

    # ── 6. Adverse Media Screening ─────────────────────────
    elements.append(Paragraph(f"{section_num}. Adverse Media Screening", styles["SectionHead"]))
    section_num += 1
    articles = news_data.get("articles", [])
    if articles:
        elements.append(Paragraph(
            f'<font color="#dc3545"><b>{news_data.get("negative_count", 0)} '
            f'adverse article(s) found</b></font>',
            styles["BodyText2"],
        ))
        media_table = [["Headline", "Source", "Date"]]
        for art in articles[:10]:
            media_table.append([
                art.get("headline", "N/A")[:80],
                art.get("source", "N/A"),
                art.get("date", "N/A"),
            ])
        elements.append(_styled_table(media_table))
    else:
        elements.append(Paragraph(
            '<font color="#28a745">No adverse media articles found.</font>',
            styles["BodyText2"],
        ))
    elements.append(Spacer(1, 12))

    # ── 7. Domain Intelligence ─────────────────────────────
    elements.append(Paragraph(f"{section_num}. Domain Intelligence", styles["SectionHead"]))
    section_num += 1
    if whois_data.get("found"):
        domain_table = [
            ["Field", "Value"],
            ["Domain", str(whois_data.get("domain", "N/A"))],
            ["Registrar", str(whois_data.get("registrar", "N/A"))],
            ["Creation Date", str(whois_data.get("creation_date", "N/A"))],
            ["Expiration Date", str(whois_data.get("expiration_date", "N/A"))],
            ["Country", str(whois_data.get("country", "N/A"))],
            ["Domain Age (yrs)", str(whois_data.get("domain_age", "N/A"))],
        ]
        elements.append(_styled_table(domain_table))
    else:
        elements.append(Paragraph(
            f"Domain data unavailable. {whois_data.get('error', '')}",
            styles["BodyText2"],
        ))
    elements.append(Spacer(1, 12))

    # ── 8. Company Intelligence ────────────────────────────
    if company_data.get("found"):
        elements.append(Paragraph(f"{section_num}. Company Intelligence", styles["SectionHead"]))
        section_num += 1
        comp_table = [
            ["Field", "Value"],
            ["Company", str(company_data.get("name", "N/A"))],
            ["Website", str(company_data.get("website", "N/A"))],
            ["Country", str(company_data.get("country", "N/A"))],
            ["Domain Age (yrs)", str(company_data.get("domain_age", "N/A"))],
            ["Industry", str(company_data.get("industry", "N/A"))],
            ["Description", str(company_data.get("description", "N/A"))[:200]],
        ]
        elements.append(_styled_table(comp_table))
        elements.append(Spacer(1, 12))

    # ── 9. Risk Assessment ─────────────────────────────────
    elements.append(Paragraph(f"{section_num}. Risk Assessment", styles["SectionHead"]))
    section_num += 1
    score = risk_data.get("score", 0)
    classification = risk_data.get("classification", "N/A")
    risk_color = _risk_color(classification)

    elements.append(Paragraph(
        f'Risk Score: <font color="{risk_color}"><b>{score}/100</b></font> '
        f'— Classification: <font color="{risk_color}"><b>{classification}</b></font>',
        styles["BodyText2"],
    ))
    elements.append(Spacer(1, 6))

    factors = risk_data.get("factors", [])
    if factors:
        elements.append(Paragraph("<b>Contributing Factors:</b>", styles["BodyText2"]))
        for factor in factors:
            elements.append(Paragraph(f"• {factor}", styles["BodyText2"]))
    elements.append(Spacer(1, 12))

    # ── 10. AI Investigator Summary ────────────────────────
    elements.append(Paragraph(f"{section_num}. Investigator Summary", styles["SectionHead"]))
    section_num += 1

    if ai_summary.get("executive_summary"):
        elements.append(Paragraph("<b>Executive Summary</b>", styles["BodyText2"]))
        elements.append(Paragraph(ai_summary["executive_summary"], styles["BodyText2"]))
        elements.append(Spacer(1, 8))

    if ai_summary.get("red_flags"):
        elements.append(Paragraph('<font color="#dc3545"><b>Red Flags</b></font>', styles["BodyText2"]))
        for flag in ai_summary["red_flags"]:
            elements.append(Paragraph(f'• <font color="#dc3545">{flag}</font>', styles["SmallText"]))
        elements.append(Spacer(1, 8))

    if ai_summary.get("observations"):
        elements.append(Paragraph("<b>Observations</b>", styles["BodyText2"]))
        for obs in ai_summary["observations"]:
            elements.append(Paragraph(f"• {obs}", styles["SmallText"]))
        elements.append(Spacer(1, 8))

    if ai_summary.get("recommendations"):
        elements.append(Paragraph("<b>Recommendations</b>", styles["BodyText2"]))
        for rec in ai_summary["recommendations"]:
            elements.append(Paragraph(f"• {rec}", styles["SmallText"]))

    if not ai_summary:
        summary = _generate_summary(subject_info, github_data, username_data, whois_data, risk_data)
        elements.append(Paragraph(summary, styles["BodyText2"]))

    # ── Footer note ────────────────────────────────────────
    elements.append(Spacer(1, 24))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Paragraph(
        "This report was generated by OSINT-Pro. All data is sourced from publicly available information.",
        ParagraphStyle("Footer", parent=styles["BodyText"], fontSize=8, textColor=colors.grey),
    ))

    doc.build(elements)
    return filename


# ── Helpers ────────────────────────────────────────────────

def _styled_table(data):
    """Create a consistently styled ReportLab table."""
    table = Table(data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a1628")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def _risk_color(classification):
    mapping = {"Low": "#28a745", "Medium": "#fd7e14", "High": "#dc3545"}
    return mapping.get(classification, "#6c757d")


def _generate_summary(subject_info, github_data, username_data, whois_data, risk_data):
    """Build a short narrative summary (fallback when AI summary is not available)."""
    name = subject_info.get("name", "The subject")
    classification = risk_data.get("classification", "Unknown")
    score = risk_data.get("score", 0)

    parts = [
        f"An open-source intelligence investigation was conducted on <b>{name}</b>. "
        f"The overall risk classification is <b>{classification}</b> with a composite score of "
        f"<b>{score}/100</b>."
    ]

    if github_data.get("found"):
        parts.append(
            f"A GitHub profile was identified with {github_data.get('repos', 0)} public repositories "
            f"and {github_data.get('followers', 0)} followers."
        )
    else:
        parts.append("No GitHub profile was found for the provided username.")

    if username_data:
        found_platforms = [p for p, v in username_data.items() if v]
        if found_platforms:
            parts.append(f"The username was found on: {', '.join(found_platforms)}.")
        else:
            parts.append("The username was not found on any of the checked platforms.")

    if whois_data.get("found"):
        parts.append(
            f"The domain is registered with {whois_data.get('registrar', 'an unknown registrar')} "
            f"and has been active for approximately {whois_data.get('domain_age', 'N/A')} years."
        )

    parts.append(
        "This report is based solely on publicly available information and should be used as a "
        "preliminary assessment. Further investigation may be warranted depending on the use case."
    )

    return " ".join(parts)
