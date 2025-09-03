# AI-Powered Resume Analyzer

Flask web app that analyzes resumes and generates tailored job-fit recommendations using Pandas + SQL + OpenAI.

## Features
- Upload PDF/DOCX/TXT resumes
- Keyword overlap scoring (fast heuristic)
- SQLite via SQLAlchemy
- Responsive HTML/CSS/JS UI
- Seed sample jobs; view recent evaluations

## Quickstart (Local)
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# add your API key
cp .env.example .env
# edit .env and set OPENAI_API_KEY=sk-...

# init db and seed
python scripts/init_db.py
python scripts/seed_jobs.py

# run
flask --app app run --debug
# open http://127.0.0.1:5000
