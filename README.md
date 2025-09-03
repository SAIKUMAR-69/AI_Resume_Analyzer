# 📄 AI-Powered Resume Analyzer  

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)  
[![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)](https://flask.palletsprojects.com/)  
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)  

> A simple yet powerful Flask web app that analyzes resumes and generates tailored job-fit recommendations using **Pandas**, **SQLAlchemy**, and **OpenAI**.

---

## 📑 Table of Contents
- [✨ Features](#-features)
- [🚀 Quickstart (Local)](#-quickstart-local)
- [🐳 Docker Setup](#-docker-setup)
- [⚙️ Environment Variables](#️-environment-variables)
- [📊 System Architecture](#-system-architecture)
- [🔄 Resume Analysis Workflow](#-resume-analysis-workflow)
- [🖼️ Screenshots](#️-screenshots)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚧 Future Improvements](#-future-improvements)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)

---

## ✨ Features
- 📂 Upload **PDF / DOCX / TXT** resumes  
- 🔍 Keyword overlap scoring (fast heuristic)  
- 🗄️ SQLite database via SQLAlchemy  
- 💻 Responsive **Flask + HTML/CSS/JS** UI  
- 📝 Seed sample jobs & view recent evaluations  
- 🤖 Optional **OpenAI API integration** for smarter job-fit scoring  

---

## 🚀 Quickstart (Local)

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/ai_resume_analyzer.git
cd ai_resume_analyzer

# 2. Create a virtual environment
python -m venv .venv
# Activate it:
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and set:
# OPENAI_API_KEY=sk-xxxxxx

# 5. Initialize database
python scripts/init_db.py
python scripts/seed_jobs.py

# 6. Run the app
flask --app app run --debug
# Open http://127.0.0.1:5000 in browser
