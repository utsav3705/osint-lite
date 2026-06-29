"""
OSINT-Pro++ — Flask Application
Professional Due Diligence & Open Source Intelligence Platform
"""

import os
import json
import pandas as pd
from datetime import datetime, timezone
from flask import (
    Flask, render_template, request, send_from_directory,
    flash, redirect, url_for, session,
)
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# ── Existing modules (preserved) ──────────────────────────────
from modules.github_search import github_lookup
from modules.username_search import enumerate_user
from modules.whois_lookup import lookup_domain
from modules.risk_engine import calculate_risk
from modules.pdf_report import generate_pdf

# ── Pro modules ───────────────────────────────────────────────
from modules.alias_generator import generate_aliases
from modules.social_discovery import discover_profiles
from modules.news_screening import screen_media
from modules.company_lookup import lookup_company
from modules.court_parser import parse_court_document
from modules.ai_summary import generate_investigation_summary

# ── Pro++ modules ─────────────────────────────────────────────
from modules.hibp_lookup import check_email_breach
from modules.linkedin_lookup import get_linkedin_intelligence
from modules.social_analyzer import analyze_social_content
from modules.network_mapper import generate_relationship_graph
from modules.docx_report import generate_docx

# ── Database & API ────────────────────────────────────────────
from database import init_db, get_session
from models import Investigation, User
from api import api_bp


app = Flask(__name__)
app.secret_key = os.getenv(
    "SECRET_KEY",
    "utsav-osint-pro-secret-2026"
)

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "generated_reports")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    db = get_session()
    user = db.query(User).get(int(user_id))
    if user:
        db.expunge(user)
    db.close()
    return user

# Register API Blueprint
app.register_blueprint(api_bp)

# ══════════════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Render the investigation form."""
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    """Run the full OSINT-Pro++ investigation pipeline."""
    subject_info = {
        "name": request.form.get("name", "").strip(),
        "username": request.form.get("username", "").strip(),
        "email": request.form.get("email", "").strip(),
        "company": request.form.get("company", "").strip(),
        "website": request.form.get("website", "").strip(),
    }

    if not any(subject_info.values()):
        flash("Please provide at least one field to investigate.", "warning")
        return redirect(url_for("index"))

    return run_investigation(subject_info, request.form.get("save_case") == "on" or True)


def run_investigation(subject_info, save=True):
    # ── Modules ───────────────────────────────
    github_data = github_lookup(subject_info["username"])
    username_data = enumerate_user(subject_info["username"])
    whois_data = lookup_domain(subject_info["website"])
    aliases = generate_aliases(subject_info["name"])
    social_data = discover_profiles(subject_info["username"])
    news_data = screen_media(subject_info["name"])
    company_data = lookup_company(subject_info["company"])
    
    # ── Pro++ Modules ────────────────────────────────
    email_breaches = check_email_breach(subject_info["email"])
    linkedin_data = get_linkedin_intelligence(subject_info["name"], subject_info["company"])
    social_analysis = analyze_social_content(subject_info["name"], subject_info["username"])
    
    # ── Risk Engine V2 ─────────────
    risk_data = calculate_risk(
        github_data, username_data, whois_data,
        news_data=news_data, social_data=social_data,
    )
    # Adjust risk if social analysis is high risk or if breaches > 2
    if social_analysis.get("risk") == "High" or email_breaches.get("count", 0) > 2:
        risk_data["score"] = min(100, risk_data.get("score", 0) + 15)
        risk_data["classification"] = "High" if risk_data["score"] > 70 else ("Medium" if risk_data["score"] > 30 else "Low")

    # ── AI Investigator Summary ────────────────────────────
    ai_summary = generate_investigation_summary(
        subject_info=subject_info, github_data=github_data, username_data=username_data,
        whois_data=whois_data, risk_data=risk_data, aliases=aliases, social_data=social_data,
        news_data=news_data, company_data=company_data,
    )

    # ── Relationship Graph ─────────────────────────────────
    graph_html = generate_relationship_graph(
        subject_info["name"], github_data, social_data, subject_info["company"], email_breaches.get("breaches", [])
    )

    # ── Reports ───────────────────────────────────────
    try:
        pdf_filename = generate_pdf(
            subject_info, github_data, username_data, whois_data, risk_data,
            aliases=aliases, social_data=social_data, news_data=news_data,
            company_data=company_data, ai_summary=ai_summary,
        )
    except Exception:
        pdf_filename = None

    try:
        docx_filename = generate_docx(
            subject_info, github_data, username_data, whois_data, risk_data,
            aliases, social_data, news_data, company_data, ai_summary,
            email_breaches, REPORTS_DIR
        )
    except Exception:
        docx_filename = None

    # ── Save to database ───────────────────────────────────
    if save:
        try:
            db = get_session()
            json_blob = json.dumps({
                "github": github_data, "usernames": username_data, "whois": whois_data,
                "aliases": aliases, "social": social_data, "news": news_data,
                "company": company_data, "email_breaches": email_breaches,
                "linkedin": linkedin_data, "social_analysis": social_analysis
            })
            
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
                analyst=current_user.username if current_user.is_authenticated else "anonymous",
                status="Completed",
                json_blob=json_blob
            )
            db.add(investigation)
            db.commit()
            db.close()
        except Exception:
            pass 

    return render_template(
        "report.html", subject=subject_info, github=github_data, usernames=username_data,
        whois=whois_data, risk=risk_data, pdf_filename=pdf_filename, docx_filename=docx_filename,
        aliases=aliases, social_profiles=social_data, news_data=news_data,
        company_data=company_data, ai_summary=ai_summary, email_breaches=email_breaches,
        linkedin_data=linkedin_data, social_analysis=social_analysis, graph_html=graph_html
    )


@app.route("/download/<filename>")
def download_report(filename):
    """Serve a generated report for download."""
    return send_from_directory(REPORTS_DIR, filename, as_attachment=True)


@app.route("/batch", methods=["GET", "POST"])
@login_required
def batch():
    """Batch investigations via CSV."""
    if request.method == "POST":
        file = request.files.get("csv_file")
        if not file or file.filename == "":
            flash("Please upload a CSV file.", "warning")
            return redirect(url_for("batch"))
            
        if not file.filename.lower().endswith(".csv"):
            flash("Only CSV files are supported.", "warning")
            return redirect(url_for("batch"))
            
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filepath = os.path.join(UPLOAD_DIR, "batch_upload.csv")
        file.save(filepath)
        
        try:
            df = pd.read_csv(filepath)
            # Need columns: Name, Email, Username (others optional)
            count = 0
            for _, row in df.iterrows():
                subject_info = {
                    "name": str(row.get("Name", "")).strip() if pd.notna(row.get("Name")) else "",
                    "email": str(row.get("Email", "")).strip() if pd.notna(row.get("Email")) else "",
                    "username": str(row.get("Username", "")).strip() if pd.notna(row.get("Username")) else "",
                    "company": str(row.get("Company", "")).strip() if "Company" in df.columns and pd.notna(row.get("Company")) else "",
                    "website": ""
                }
                # Run headless (don't render template)
                if any(subject_info.values()):
                    # Call run_investigation but don't return the render
                    # Just process to save to DB
                    try:
                        github_data = github_lookup(subject_info["username"])
                        username_data = enumerate_user(subject_info["username"])
                        whois_data = lookup_domain(subject_info["website"])
                        aliases = generate_aliases(subject_info["name"])
                        social_data = discover_profiles(subject_info["username"])
                        news_data = screen_media(subject_info["name"])
                        company_data = lookup_company(subject_info["company"])
                        email_breaches = check_email_breach(subject_info["email"])
                        linkedin_data = get_linkedin_intelligence(subject_info["name"], subject_info["company"])
                        social_analysis = analyze_social_content(subject_info["name"], subject_info["username"])
                        risk_data = calculate_risk(github_data, username_data, whois_data, news_data=news_data, social_data=social_data)
                        
                        db = get_session()
                        inv = Investigation(
                            subject_name=subject_info.get("name") or subject_info.get("username") or "Unknown",
                            username=subject_info.get("username", ""), email=subject_info.get("email", ""),
                            company=subject_info.get("company", ""), website=subject_info.get("website", ""),
                            risk_score=risk_data.get("score", 0), risk_classification=risk_data.get("classification", "Low"),
                            analyst=current_user.username, status="Batch Completed"
                        )
                        db.add(inv)
                        db.commit()
                        db.close()
                        count += 1
                    except Exception as e:
                        pass
            flash(f"Successfully processed {count} records in batch.", "success")
        except Exception as e:
            flash(f"Error processing CSV: {str(e)}", "danger")
            
    return render_template("batch.html")


@app.route("/dashboard")
@login_required
def dashboard():
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


@app.route("/cases")
@login_required
def cases():
    try:
        db = get_session()
        investigations = db.query(Investigation).order_by(Investigation.id.desc()).all()
        db.close()
    except Exception:
        investigations = []

    return render_template("cases.html", investigations=investigations)


@app.route("/cases/<int:case_id>/delete", methods=["POST"])
@login_required
def delete_case(case_id):
    try:
        db = get_session()
        inv = db.query(Investigation).filter_by(id=case_id).first()
        if inv:
            if inv.report_path:
                pdf_path = os.path.join(REPORTS_DIR, inv.report_path)
                if os.path.exists(pdf_path): os.remove(pdf_path)
            db.delete(inv)
            db.commit()
            flash("Investigation deleted successfully.", "success")
        else:
            flash("Investigation not found.", "warning")
        db.close()
    except Exception as e:
        flash(f"Error deleting investigation: {str(e)}", "danger")

    return redirect(url_for("cases"))


@app.route("/court-analyzer", methods=["GET", "POST"])
@login_required
def court_analyzer():
    court_data = None
    if request.method == "POST":
        file = request.files.get("court_pdf")
        if not file or file.filename == "":
            flash("Please select a PDF file to upload.", "warning")
            return redirect(url_for("court_analyzer"))

        if not file.filename.lower().endswith(".pdf"):
            flash("Only PDF files are supported.", "warning")
            return redirect(url_for("court_analyzer"))

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        safe_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in file.filename)
        filepath = os.path.join(UPLOAD_DIR, safe_name)
        file.save(filepath)

        try:
            court_data = parse_court_document(filepath)
        except Exception as e:
            court_data = {"error": f"Analysis failed: {str(e)}", "parsed": False}
        finally:
            try:
                os.remove(filepath)
            except OSError:
                pass

    return render_template("court_analyzer.html", court_data=court_data)

# ── Authentication ────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_session()
        user = db.query(User).filter_by(username=username).first()
        
        # Fallback to hardcoded admin if DB has no users
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            db.close()
            flash(f"Welcome back, {username}.", "success")
            return redirect(url_for("dashboard"))
        elif username == "admin" and password == "admin":
            # Auto-create admin
            new_user = User(username="admin", password_hash=generate_password_hash("admin"), role="Admin")
            db.add(new_user)
            db.commit()
            login_user(new_user)
            db.close()
            return redirect(url_for("dashboard"))
        else:
            db.close()
            flash("Invalid credentials. Please try again.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        db = get_session()
        if db.query(User).filter_by(username=username).first():
            flash("Username already exists.", "warning")
            db.close()
            return redirect(url_for("register"))
            
        new_user = User(username=username, password_hash=generate_password_hash(password))
        db.add(new_user)
        db.commit()
        db.close()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))
        
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))


# ══════════════════════════════════════════════════════════════
#  ERROR HANDLERS
# ══════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    flash("Page not found.", "danger")
    return redirect(url_for("index"))

@app.errorhandler(500)
@app.errorhandler(Exception)
def server_error(e):
    import traceback
    traceback.print_exc()
    app.logger.exception(e)
    flash(str(e), "danger")
    return redirect(url_for("index"))

with app.app_context():
    init_db()

if __name__ == "__main__":
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.run(debug=True, port=5000)
