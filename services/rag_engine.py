# services/rag_engine.py
from openai import OpenAI
import faiss
import numpy as np

client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

# Example domain knowledge base
documents = [
    "Resumes should emphasize quantifiable achievements and impact.",
    "Use action verbs like developed, implemented, optimized, and designed.",
    "Tailor each resume to the specific job description for better ATS scores.",
    "Include both technical and soft skills relevant to the role.",
    "Keep formatting simple and clean for ATS compatibility.",
    "For technical roles, highlight projects with measurable outcomes."
]

# Build embeddings and FAISS index (in memory)
embeddings = [client.embeddings.create(model="text-embedding-3-large", input=d).data[0].embedding for d in documents]
dim = len(embeddings[0])
index = faiss.IndexFlatL2(dim)
index.add(np.array(embeddings))
doc_map = {i: doc for i, doc in enumerate(documents)}

def retrieve_relevant_docs(query, top_k=3):
    """Retrieve top K related documents from knowledge base."""
    query_emb = client.embeddings.create(model="text-embedding-3-large", input=query).data[0].embedding
    distances, indices = index.search(np.array([query_emb]), top_k)
    return [doc_map[i] for i in indices[0]]

def generate_rag_advice(resume_text, job_title, matched_keywords):
    """Generate AI feedback with RAG context."""
    query = f"Provide resume improvement advice for a {job_title} resume focusing on {', '.join(matched_keywords)}."
    context_docs = retrieve_relevant_docs(query)
    context = "\n".join(context_docs)

    prompt = f"""
    You are an expert resume coach.
    Use the following context and resume snippet to provide feedback.

    Context:
    {context}

    Resume Snippet:
    {resume_text[:1000]}  # limit to avoid token overflow

    Job Title: {job_title}
    Matched Keywords: {', '.join(matched_keywords)}

    Provide:
    1. A short summary paragraph (2-3 sentences)
    2. 2-3 actionable recommendations for improvement
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
