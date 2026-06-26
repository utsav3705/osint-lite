"""
OSINT-Pro — Flask Application
Professional Due Diligence & Open Source Intelligence Platform

Extended from OSINT-Lite with:
  - Alias generation
  - Social discovery
  - Adverse media screening
  - Company intelligence
  - Court document analysis
  - AI investigator summary
  - Risk Engine V2
  - Case management (SQLite)
  - Login / session auth
  - Dashboard
"""

import os
from datetime import datetime, timezone
from flask import (
    Flask, render_template, request, send_from_directory,
    flash, redirect, url_for, session,
)

# ── Existing modules (preserved) ──────────────────────────────
from modules.github_search import github_lookup
from modules.username_search import enumerate_user
from modules.whois_lookup import lookup_domain
from modules.risk_engine import calculate_risk
from modules.pdf_report import generate_pdf

# ── New Pro modules ───────────────────────────────────────────
from modules.alias_generator import generate_aliases
from modules.social_discovery import discover_profiles
from modules.news_screening import screen_media
from modules.company_lookup import lookup_company
from modules.court_parser import parse_court_document
from modules.ai_summary import generate_investigation_summary

# ── Database ──────────────────────────────────────────────────
from database import init_db, get_session
from models import Investigation


app = Flask(__name__)
app.secret_key = os.urandom(24)

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "generated_reports")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")

# ── Hardcoded analyst credentials (demo) ──────────────────────
ANALYST_CREDENTIALS = {
    "analyst": "osint2026",
}


# ══════════════════════════════════════════════════════════════
#  EXISTING ROUTES (preserved from OSINT-Lite)
# ══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Render the investigation form."""
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    """Run the full OSINT-Pro investigation pipeline and render the report."""
    # ── Collect form data ──────────────────────────────────
    subject_info = {
        "name": request.form.get("name", "").strip(),
        "username": request.form.get("username", "").strip(),
        "email": request.form.get("email", "").strip(),
        "company": request.form.get("company", "").strip(),
        "website": request.form.get("website", "").strip(),
    }

    # At least one field must be provided
    if not any(subject_info.values()):
        flash("Please provide at least one field to investigate.", "warning")
        return redirect(url_for("index"))

    # ── Run existing modules ───────────────────────────────
    github_data = github_lookup(subject_info["username"])
    username_data = enumerate_user(subject_info["username"])
    whois_data = lookup_domain(subject_info["website"])

    # ── Run new Pro modules ────────────────────────────────
    aliases = generate_aliases(subject_info["name"])
    social_data = discover_profiles(subject_info["username"])
    news_data = screen_media(subject_info["name"])
    company_data = lookup_company(subject_info["company"])

    # ── Risk Engine V2 (with new data sources) ─────────────
    risk_data = calculate_risk(
        github_data, username_data, whois_data,
        news_data=news_data, social_data=social_data,
    )

    # ── AI Investigator Summary ────────────────────────────
    ai_summary = generate_investigation_summary(
        subject_info=subject_info,
        github_data=github_data,
        username_data=username_data,
        whois_data=whois_data,
        risk_data=risk_data,
        aliases=aliases,
        social_data=social_data,
        news_data=news_data,
        company_data=company_data,
    )

    # ── Generate PDF ───────────────────────────────────────
    try:
        pdf_filename = generate_pdf(
            subject_info, github_data, username_data, whois_data, risk_data,
            aliases=aliases, social_data=social_data, news_data=news_data,
            company_data=company_data, ai_summary=ai_summary,
        )
    except Exception:
        pdf_filename = None

    # ── Save to database ───────────────────────────────────
    try:
        db = get_session()
        investigation = Investigation(
            subject_name=subject_info.get("name") or subject_info.get("username") or "Unknown",
            username=subject_info.get("username", ""),
            email=subject_info.get("email", ""),
            company=subject_info.get("company", ""),
            website=subject_info.get("website", ""),
            date_created=datetime.now(timezone.utc),
            risk_score=risk_data.get("score", 0),
            risk_classification=risk_data.get("classification", "Low"),
            report_path=pdf_filename or "",
            analyst=session.get("username", "analyst"),
            status="Completed",
        )
        db.add(investigation)
        db.commit()
        db.close()
    except Exception:
        pass  # Don't let DB errors break the investigation flow

    return render_template(
        "report.html",
        subject=subject_info,
        github=github_data,
        usernames=username_data,
        whois=whois_data,
        risk=risk_data,
        pdf_filename=pdf_filename,
        aliases=aliases,
        social_profiles=social_data,
        news_data=news_data,
        company_data=company_data,
        ai_summary=ai_summary,
    )


@app.route("/download/<filename>")
def download_report(filename):
    """Serve a generated PDF report for download."""
    return send_from_directory(REPORTS_DIR, filename, as_attachment=True)


# ══════════════════════════════════════════════════════════════
#  NEW ROUTES (OSINT-Pro extensions)
# ══════════════════════════════════════════════════════════════

# ── Dashboard ─────────────────────────────────────────────────

@app.route("/dashboard")
def dashboard():
    """Render the case management dashboard."""
    try:
        db = get_session()
        all_cases = db.query(Investigation).order_by(Investigation.id.desc()).all()
        recent_cases = all_cases[:10]

        stats = {
            "total": len(all_cases),
            "high_risk": sum(1 for c in all_cases if c.risk_classification == "High"),
            "medium_risk": sum(1 for c in all_cases if c.risk_classification == "Medium"),
            "low_risk": sum(1 for c in all_cases if c.risk_classification == "Low"),
        }
        db.close()
    except Exception:
        recent_cases = []
        stats = {"total": 0, "high_risk": 0, "medium_risk": 0, "low_risk": 0}

    return render_template("dashboard.html", recent_cases=recent_cases, stats=stats)


# ── Cases ─────────────────────────────────────────────────────

@app.route("/cases")
def cases():
    """Render the full investigation history."""
    try:
        db = get_session()
        investigations = db.query(Investigation).order_by(Investigation.id.desc()).all()
        db.close()
    except Exception:
        investigations = []

    return render_template("cases.html", investigations=investigations)


@app.route("/cases/<int:case_id>/delete", methods=["POST"])
def delete_case(case_id):
    """Delete an investigation record."""
    try:
        db = get_session()
        inv = db.query(Investigation).filter_by(id=case_id).first()
        if inv:
            # Remove associated PDF if it exists
            if inv.report_path:
                pdf_path = os.path.join(REPORTS_DIR, inv.report_path)
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
            db.delete(inv)
            db.commit()
            flash("Investigation deleted successfully.", "success")
        else:
            flash("Investigation not found.", "warning")
        db.close()
    except Exception as e:
        flash(f"Error deleting investigation: {str(e)}", "danger")

    return redirect(url_for("cases"))


# ── Court Document Analyzer ───────────────────────────────────

@app.route("/court-analyzer", methods=["GET", "POST"])
def court_analyzer():
    """Upload and analyze court documents."""
    court_data = None

    if request.method == "POST":
        file = request.files.get("court_pdf")
        if not file or file.filename == "":
            flash("Please select a PDF file to upload.", "warning")
            return redirect(url_for("court_analyzer"))

        if not file.filename.lower().endswith(".pdf"):
            flash("Only PDF files are supported.", "warning")
            return redirect(url_for("court_analyzer"))

        # Save uploaded file
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in file.filename)
        filepath = os.path.join(UPLOAD_DIR, safe_name)
        file.save(filepath)

        # Parse the document
        try:
            court_data = parse_court_document(filepath)
        except Exception as e:
            court_data = {"error": f"Analysis failed: {str(e)}", "parsed": False}
        finally:
            # Clean up uploaded file
            try:
                os.remove(filepath)
            except OSError:
                pass

    return render_template("court_analyzer.html", court_data=court_data)


# ── Authentication ────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    """Simple session-based login."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username in ANALYST_CREDENTIALS and ANALYST_CREDENTIALS[username] == password:
            session["logged_in"] = True
            session["username"] = username
            flash(f"Welcome back, {username}.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Clear the session."""
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))


# ══════════════════════════════════════════════════════════════
#  ERROR HANDLERS (preserved)
# ══════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    flash("Page not found.", "danger")
    return redirect(url_for("index"))


@app.errorhandler(500)
def server_error(e):
    flash("An internal error occurred. Please try again.", "danger")
    return redirect(url_for("index"))


# ══════════════════════════════════════════════════════════════
#  APPLICATION ENTRY POINT
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    init_db()
    app.run(debug=True, port=5000)
