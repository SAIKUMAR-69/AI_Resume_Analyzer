import os
import re
from collections import Counter
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from models import db, Candidate, Job, Evaluation
from services.resume_parser import extract_text_from_upload
from services.scoring import keyword_score, normalize_score

import faiss
import numpy as np
import requests

# === Config ===
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_KEY:
    raise ValueError("OpenRouter API key not found in .env")

BASE_URL = "https://openrouter.ai/api/v1"
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
EMBED_CACHE = "instance/embeddings.npy"

# === RAG Knowledge Base ===
documents = [
    "Resumes should emphasize quantifiable achievements and impact.",
    "Use action verbs like developed, implemented, optimized, and designed.",
    "Tailor each resume to the specific job description for better ATS scores.",
    "Include both technical and soft skills relevant to the role.",
    "Keep formatting simple and clean for ATS compatibility.",
    "For technical roles, highlight projects with measurable outcomes."
]

# === Helper functions for OpenRouter ===
def get_embedding(text: str, model="text-embedding-3-large"):
    url = f"{BASE_URL}/embeddings"
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "input": text}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]
    except requests.RequestException as e:
        print(f"Error fetching embedding: {e}")
        return [0.0] * 1536

def chat_completion(messages, model="gpt-4o-mini"):
    url = f"{BASE_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        print(f"Error generating chat completion: {e}")
        return "Unable to generate RAG advice at this time."

# === Build embeddings and FAISS index ===
if os.path.exists(EMBED_CACHE):
    embeddings = np.load(EMBED_CACHE, allow_pickle=True)
else:
    print("Building RAG knowledge base embeddings...")
    os.makedirs("instance", exist_ok=True)
    embeddings = [get_embedding(d) for d in documents]
    np.save(EMBED_CACHE, embeddings)

dim = len(embeddings[0])
index = faiss.IndexFlatL2(dim)
index.add(np.array(embeddings))
doc_map = {i: doc for i, doc in enumerate(documents)}

def retrieve_relevant_docs(query, top_k=3):
    query_emb = get_embedding(query)
    distances, indices = index.search(np.array([query_emb]), top_k)
    return [doc_map[i] for i in indices[0]]

def generate_rag_advice(resume_text, job_title, matched_keywords):
    query = f"Provide resume improvement advice for a {job_title} resume focusing on {', '.join(matched_keywords)}."
    context_docs = retrieve_relevant_docs(query)
    context = "\n".join(context_docs)

    prompt = f"""
You are an expert resume coach.
Use the following context and resume snippet to provide feedback in this format:

Context:
{context}

Resume Snippet:
{resume_text[:1000]}

Job Title: {job_title}
Matched Keywords: {', '.join(matched_keywords)}

Instructions:
-Summary (max 4 lines):
[Concise summary here]
- Provide a short, small summary paragraph about the candidate's strengths and areas to improve.
- The summary must be strictly 3 lines, no headings or Markdown formatting.
- Recommendations (3 bullet points):
• First recommendation
• Second recommendation
• Third recommendation

Output format:
Summary:
<your 3-line summary>

Recommendations:
• Recommendation 1
• Recommendation 2
• Recommendation 3
"""
    rag_feedback = chat_completion([{"role": "user", "content": prompt}])

    # Split summary and recommendations
    if "Recommendations" in rag_feedback:
        parts = rag_feedback.split("Recommendations")
        ai_summary = parts[0].replace("Summary:", "").strip()
        ai_recommendations = parts[1].strip() if len(parts) > 1 else ""
    else:
        ai_summary = rag_feedback
        ai_recommendations = ""

    # Enforce 4 lines strictly
    summary_lines = ai_summary.split("\n")
    ai_summary = "\n".join(summary_lines[:4])

    return ai_summary, ai_recommendations

# === Flask app ===
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "dev-secret"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL",
            "sqlite:///" + os.path.join(app.instance_path, "resume_analyzer.db")
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAX_CONTENT_LENGTH=10 * 1024 * 1024,
    )

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/", methods=["GET"])
    def index():
        jobs = Job.query.order_by(Job.title.asc()).all()
        return render_template("index.html", jobs=jobs)

    @app.route("/analyze", methods=["POST"])
    def analyze():
        job_id = request.form.get("job_id")
        if not job_id:
            flash("Please select a job.", "error")
            return redirect(url_for("index"))

        job = Job.query.get(int(job_id))
        if "resume" not in request.files:
            flash("No resume file provided.", "error")
            return redirect(url_for("index"))
        file = request.files["resume"]
        if file.filename == "" or not allowed_file(file.filename):
            flash("Please upload a PDF, DOCX, or TXT resume.", "error")
            return redirect(url_for("index"))

        filename = secure_filename(file.filename)
        uploaded_path = os.path.join(
            "instance", f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
        )
        file.save(uploaded_path)

        resume_text = extract_text_from_upload(uploaded_path).lower()
        candidate_name = request.form.get("candidate_name", "Candidate")

        candidate = Candidate(name=candidate_name, resume_text=resume_text, skills_text="")
        db.session.add(candidate)
        db.session.commit()

        job_title = job.title
        job_desc = job.description.lower()

        # ---------- Keyword scoring ----------
        kw_score = keyword_score(resume_text, job_desc)
        norm = normalize_score(kw_score)
        score = norm  # normalized score directly saved

        # Extract top keywords
        words = re.findall(r'\b\w+\b', job_desc)
        stop_words = {"and","or","the","a","an","to","for","with","in","on","of"}
        keywords = [w for w in words if w not in stop_words]
        top_keywords = [k for k,_ in Counter(keywords).most_common(10)]
        matched_keywords = [kw for kw in top_keywords if kw in resume_text]
        if not matched_keywords:
            matched_keywords = top_keywords[:3]

        # Generate RAG feedback
        try:
            ai_summary, ai_recommendations = generate_rag_advice(resume_text, job_title, matched_keywords)
        except Exception as e:
            print(f"RAG generation failed: {e}")
            ai_summary, ai_recommendations = "", ""

        # Convert recommendations string into list for proper rendering
        recommendation_list = [
            r.strip("• .: ").strip()  # remove leading bullets, dots, colons, spaces
            for r in ai_recommendations.split("\n") 
            if r.strip()
        ][1:4]

        # Persist evaluation
        eval_obj = Evaluation(
            candidate_id=candidate.id,
            job_id=job.id,
            score=score,
            summary=ai_summary,
            recommendations=ai_recommendations,
            created_at=datetime.utcnow()
        )
        db.session.add(eval_obj)
        db.session.commit()

        return render_template(
            "results.html",
            candidate=candidate,
            job_title=job_title,
            job_desc=job_desc,
            score=score,
            summary=ai_summary,
            recommendation_list=recommendation_list
        )

    def allowed_file(filename):
        return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

    return app

# Run app
app = create_app()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=True)
