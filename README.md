# OSINT-Lite

A professional Due Diligence / OSINT Investigation Platform inspired by enterprise investigation workflows, designed for analysts and investigators to aggregate and analyze public intelligence from a single interface.

---

## Features

- User Authentication
- Dashboard
- Case Management
- Investigation Workspace
- GitHub Intelligence
- Professional Profile Intelligence
- Company Intelligence
- Court Record Analysis
- News Screening
- HIBP Email Breach Lookup
- Social Media Intelligence
- Network Graph Visualization
- Risk Assessment Engine
- PDF Report Export
- DOCX Report Export
- REST API
- Batch Investigations
- Dark / Light Theme

---

## Screenshots

<!-- Add placeholders for screenshots -->
![Dashboard](https://via.placeholder.com/800x400?text=Dashboard+Screenshot)

![Investigation Workspace](https://via.placeholder.com/800x400?text=Investigation+Workspace+Screenshot)

![Network Graph](https://via.placeholder.com/800x400?text=Network+Graph+Screenshot)

---

## Technology Stack

**Frontend:**
- HTML
- CSS
- JavaScript
- Bootstrap

**Backend:**
- Flask
- SQLAlchemy
- SQLite

**Libraries:**
- Plotly
- NetworkX
- BeautifulSoup
- Requests
- ReportLab
- python-docx

**Deployment:**
- Render

---

## Installation

### Prerequisites
- Python 3.11 or higher
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/utsav3705/osint-lite.git
cd osint-lite

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

---

## Local Development

Run the application locally:
```bash
pip install -r requirements.txt
python app.py
```

Access the platform at `http://127.0.0.1:5000`.

---

## Deployment

This application is ready to be deployed on **Render**. Ensure you set the `SECRET_KEY` environment variable in your Render dashboard and configure the build/start commands (using Gunicorn).
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

---

## Project Structure

- `app.py`: Main Flask application and routing.
- `models.py`: Database schema and ORM models.
- `database.py`: Database configuration and initialization.
- `api.py`: REST API endpoints.
- `modules/`: Contains Python scripts for various OSINT tasks (Risk Assessment, Profile Lookups, AI Summaries, etc.).
- `templates/`: HTML files for rendering the frontend pages.
- `static/`: Custom CSS and JavaScript files.
- `generated_reports/`: Storage for generated PDF and DOCX reports.
- `uploads/`: Temporary storage for file processing (e.g., Court PDF parsing, CSV batch).
- `requirements.txt`: Python dependencies.

---

## Future Improvements

- Automated periodic continuous monitoring for active cases.
- Direct integration with proprietary databases and public APIs like Shodan and VirusTotal.
- Entity resolution to automatically cross-link profiles accurately.
- Customizable report templates tailored for different legal requirements.

---

## License

MIT License
