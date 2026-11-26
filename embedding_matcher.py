
import os
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

_CACHED_MODEL = None  # Global cache: Prevents reloading model weights on each call


def load_model(model_name: str = "all-MiniLM-L6-v2"):
    """
    Loads and caches the distilled sentence transformer model.
    all-MiniLM-L6-v2: 6 transformer layers, 384 dimensions.
    """
    global _CACHED_MODEL
    if _CACHED_MODEL is None:
        _CACHED_MODEL = SentenceTransformer(model_name)
    return _CACHED_MODEL


def chunk_document(text: str, chunk_size: int = 150, overlap: int = 30) -> list:
    """
    Divides unstructured document text into overlapping windows of words.
    Prevents silent token truncation by ensuring every chunk fits within the
    transformer's maximum sequence length.
    """
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    
    chunks = []
    i = 0
    step = chunk_size - overlap
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += step
    return chunks


def compute_substance_factor(word_count: int, min_threshold: int = 50) -> float:
    """
    Substance Factor: Penalizes ultra-short text stubs (e.g., 14 words) that lack
    actual employment history or project depth, preventing false-positive keyword stuffing.
    """
    if word_count < min_threshold:
        return max(0.20, round(word_count / 100.0, 4))
    return 1.0


def check_domain_alignment(resume_text: str, job_text: str) -> float:
    """
    Domain Prerequisite Check: Verifies whether the candidate's primary skill profile
    aligns with the primary stack requested in the job description.
    Prevents false positives (e.g., Java developers applying for Python backend roles).
    """
    res_lower = resume_text.lower()
    jd_lower = job_text.lower()

    # Case 1: Job Description is Python-focused
    if "python" in jd_lower:
        has_python = "python" in res_lower
        java_count = res_lower.count("java")
        # If applicant mentions zero Python and is heavily Java-focused, apply mismatch penalty
        if not has_python and java_count >= 3:
            return 0.65

    # Case 2: Job Description is Java-focused
    elif "java" in jd_lower:
        has_java = "java" in res_lower or "spring" in res_lower
        python_count = res_lower.count("python")
        if not has_java and python_count >= 3:
            return 0.65

    # Case 3: Job Description is Business Analyst / Scrum focused
    elif "business analyst" in jd_lower or "scrum" in jd_lower:
        has_ba = any(k in res_lower for k in ["business analyst", "scrum", "agile", "brd", "requirements"])
        if not has_ba:
            return 0.70

    return 1.0  # Aligned domain


def compute_embedding_score(resume_text: str, job_text: str, model=None, top_k: int = 3) -> float:
    """
    Computes semantic cosine similarity using Windowed Chunk Pooling.
    Guarantees zero truncation across multi-page resumes and enforces substance/domain checks.
    """
    if model is None:
        model = load_model()

    # Step 1: Encode Job Description into continuous 384D vector space
    job_emb = model.encode([job_text], convert_to_numpy=True)

    # Step 2: Split Resume into chunks 
    chunks = chunk_document(resume_text, chunk_size=150, overlap=30)
    chunk_embs = model.encode(chunks, convert_to_numpy=True, batch_size=32)

    # Step 3: Compute cosine similarity for each chunk
    chunk_scores = cosine_similarity(job_emb, chunk_embs)[0]

    # Step 4: Top-K Best Matching Chunks (captures strongest evidence across all pages)
    k = min(top_k, len(chunk_scores))
    top_k_indices = np.argsort(chunk_scores)[-k:]
    raw_semantic_score = float(np.mean(chunk_scores[top_k_indices]))

    # Step 5: Apply Substance Factor (penalizes stubs < 50 words)
    words = len(resume_text.split())
    substance_factor = compute_substance_factor(words)

    # Step 6: Apply Domain Alignment Factor (penalizes cross-domain false positives)
    domain_factor = check_domain_alignment(resume_text, job_text)

    # Final Calibrated Score
    calibrated_score = raw_semantic_score * substance_factor * domain_factor
    return round(float(calibrated_score), 4)


# ──────────────────────────────────────────────────────────────────────
# Self-Test Harness
# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from data_loader import load_resume_and_job
    print("=== Testing Updated embedding_matcher.py with Windowed Pooling ===")
    
    sample_res = os.path.join(os.path.dirname(__file__), "sample_data", "resume.txt")
    sample_jd = os.path.join(os.path.dirname(__file__), "sample_data", "job_description.txt")
    
    if os.path.exists(sample_res) and os.path.exists(sample_jd):
        res, jd = load_resume_and_job(sample_res, sample_jd)
        score = compute_embedding_score(res, jd)
        print(f"Sample Python Resume Score: {score:.2%}")
