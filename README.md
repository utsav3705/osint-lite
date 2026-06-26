# OSINT-Lite

**Open Source Intelligence and Due Diligence Investigation Dashboard**

OSINT-Lite is a lightweight, modular intelligence platform designed for junior investigators and due diligence analysts. It aggregates publicly available data from multiple sources, performs automated risk scoring, and generates professional PDF investigation reports — all from a single web interface.

---

## Features

- **GitHub Intelligence** — Retrieves public profile data, repository counts, follower metrics, and account creation dates via the GitHub REST API.
- **Username Enumeration** — Checks for the existence of a username across GitHub, GitLab, Reddit, Medium, and Pinterest.
- **Domain / WHOIS Intelligence** — Performs WHOIS lookups to extract registrar, creation date, expiration date, country, and domain age.
- **Risk Scoring Engine** — Computes a composite risk score (0–100) based on digital footprint signals, classifying subjects as Low, Medium, or High risk.
- **PDF Report Export** — Generates a professional, download-ready PDF investigation report using ReportLab.
- **Modern Dashboard UI** — Responsive, dark-themed interface built with Bootstrap 5 and custom CSS.

---

## Installation

### Prerequisites

- Python 3.11 or higher
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/your-username/osint-lite.git
cd osint-lite

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

```bash
# Start the development server
python app.py
```

Open your browser and navigate to **http://127.0.0.1:5000/**

1. Fill in one or more fields (Name, Username, Email, Company, Website).
2. Click **Investigate**.
3. Review the investigation report with risk scoring and intelligence findings.
4. Click **Download PDF** to save a copy of the report.

---

## Requirements

| Package       | Version  | Purpose                    |
|---------------|----------|----------------------------|
| Flask         | ≥ 3.0    | Web framework              |
| requests      | ≥ 2.31   | HTTP requests              |
| python-whois  | ≥ 0.9    | WHOIS domain lookups       |
| reportlab     | ≥ 4.0    | PDF report generation      |
| pandas        | ≥ 2.1    | Data manipulation          |

---

## Project Structure

```
osint-lite/
├── app.py                    # Flask application
├── requirements.txt          # Python dependencies
├── README.md
├── modules/
│   ├── github_search.py      # GitHub API intelligence
│   ├── username_search.py    # Cross-platform username check
│   ├── whois_lookup.py       # WHOIS domain analysis
│   ├── risk_engine.py        # Risk scoring engine
│   └── pdf_report.py         # PDF report generator
├── templates/
│   ├── base.html             # Base layout template
│   ├── index.html            # Investigation form
│   └── report.html           # Report display
├── static/
│   ├── css/style.css         # Custom styles
│   └── js/main.js            # Client-side logic
└── generated_reports/        # PDF output directory
```

---

## Screenshots

> Screenshots will be added here.

---

## Future Improvements

- [ ] Email breach lookup (Have I Been Pwned API)
- [ ] Social media content analysis
- [ ] LinkedIn intelligence module
- [ ] Investigation history with SQLite persistence
- [ ] Network graph visualization with NetworkX + Plotly
- [ ] Dark/Light theme toggle
- [ ] Multi-subject batch investigations
- [ ] REST API endpoints for programmatic access
- [ ] User authentication and case management
- [ ] Export reports in DOCX format

---

## License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
