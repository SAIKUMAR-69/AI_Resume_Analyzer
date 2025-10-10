import os
import numpy as np
from app import create_app, db, documents, get_embedding, EMBED_CACHE

os.makedirs("instance", exist_ok=True)

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created.")

    if not os.path.exists(EMBED_CACHE):
        print("Building RAG knowledge base embeddings...")
        embeddings = [get_embedding(d) for d in documents]
        np.save(EMBED_CACHE, embeddings)
        print(f"Saved embeddings to {EMBED_CACHE}")
    else:
        print(f"Embeddings already cached at {EMBED_CACHE}")
