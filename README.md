# 🚀 AI-Powered Resume Analyzer

An intelligent **Flask-based web application** that evaluates resumes using **AI-driven text analysis** and **Retrieval-Augmented Generation (RAG)** to provide job-fit insights, concise summaries, and actionable recommendations.

---

## 🧠 Overview

The **AI Resume Analyzer** helps candidates and recruiters assess how well a resume matches a specific job description.  
By combining **keyword scoring**, **semantic search**, and **GPT-based reasoning**, it produces instant, recruiter-like evaluations that highlight strengths, gaps, and improvement opportunities.

---

## ✨ Key Features

- 📄 **Smart Resume Upload:** Supports PDF, DOCX, and TXT file formats.  
- 🧩 **AI-Powered Insights:** Generates concise summaries and 3 actionable recommendations using RAG and OpenRouter API.  
- 🎯 **Keyword Matching:** Measures alignment between job descriptions and resume content with a normalized score.  
- 🗃️ **Database Integration:** Uses SQLite with SQLAlchemy ORM for structured storage of candidates, jobs, and evaluations.  
- 🎨 **User-Friendly Interface:** Clean and responsive design built with HTML/CSS and Flask templates.  
- 🔐 **Secure File Handling:** Limits file size and validates allowed file types for safe uploads.  

---

## 🧩 System Architecture

```
AI_Resume_Analyzer/
│
├── app.py                    # Main Flask application
├── models.py                 # SQLAlchemy models
├── services/
│   ├── resume_parser.py      # Extracts and cleans resume text
│   ├── scoring.py            # Keyword scoring and normalization
│   └── rag_engine.py         # RAG model for AI feedback
│
├── templates/
│   ├── index.html            # Upload & job selection page
│   └── results.html          # Display score and recommendations
│
├── scripts/
│   ├── init_db.py            # Initialize the database
│   └── seed_jobs.py          # Seed sample job data
│
├── instance/                 # Local DB and uploaded files (ignored by Git)
├── .env                      # API keys and environment secrets (ignored)
├── .gitignore                # Excluded files and directories
├── requirements.txt          # Python dependencies
└── README.md                 # Documentation
```

---

## ⚙️ Installation & Setup Guide

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/SAIKUMAR-69/AI_Resume_Analyzer.git
cd AI_Resume_Analyzer
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv .venv
# Activate on Windows
.venv\Scripts\activate
# Activate on macOS/Linux
source .venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables
```bash
cp .env.example .env
# Then open .env and set:
# OPENROUTER_API_KEY=your_api_key_here
```

### 5️⃣ Initialize the Database
```bash
python scripts/init_db.py
python scripts/seed_jobs.py
```

### 6️⃣ Run the Application
```bash
flask --app app run --debug
```

Visit the app in your browser at:  
👉 **http://127.0.0.1:5000**

---

## 🔍 How It Works

1. **Upload a Resume:** The app parses and extracts the resume text using NLP.  
2. **Job Selection:** Choose a job role for analysis from pre-seeded job data.  
3. **Keyword Scoring:** Calculates keyword overlap and generates a normalized score (0–100).  
4. **AI Feedback:** RAG-powered AI generates a concise 3-line summary and 3 personalized recommendations.  
5. **Result Display:** The app shows the overall score, summary, and actionable improvements in a structured format.  

---
