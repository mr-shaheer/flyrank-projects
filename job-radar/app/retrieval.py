from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def get_top_jobs(resume_text, jobs, top_k=10):
    documents = [resume_text]

    for job in jobs:
        documents.append(f"{job.title}\n{job.description}")

    embeddings = model.encode(documents)

    resume_embedding = embeddings[0]
    job_embeddings = embeddings[1:]

    similarities = cosine_similarity(
        [resume_embedding],
        job_embeddings
    )[0]

    ranked = sorted(
        zip(jobs, similarities),
        key=lambda x: x[1],
        reverse=True
    )

    return [job for job, _ in ranked[:top_k]]