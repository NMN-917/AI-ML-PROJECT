"""
tfidf_matcher.py — Baseline Statistical Machine Learning Matcher.
Model: TF-IDF Vectorizer + Cosine Similarity (scikit-learn).
"""

import os
from sklearn.feature_extraction.text import TfidfVectorizer    # Model: TF-IDF; counts term frequencies dampened by corpus inverse doc frequencies
from sklearn.metrics.pairwise import cosine_similarity        # Metric: Cosine similarity; measures dot product between sparse keyword vectors


def compute_tfidf_score(resume_text: str, job_text: str) -> float:
    """
    Computes baseline keyword overlap similarity score using TF-IDF.
    """
    vectorizer = TfidfVectorizer(stop_words="english")        # Statistical ML: Filters ~300 common English syntactic stop words ('is', 'the')
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_text])  # Bag-of-Words: Maps text into sparse high-dimensional term frequency matrix

    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]  # Metric: Cosine angle between resume vector (row 0) and JD vector (row 1)
    return round(float(score), 4)                             # Output: Normalized similarity score bounded in [0.0, 1.0]


def get_top_tfidf_words(text: str, top_n: int = 10) -> list:
    """
    Extracts top N highest-weighted keywords from a single document for explainability.
    """
    vectorizer = TfidfVectorizer(stop_words="english")        # Model: Learns local unigram vocabulary and term weights for the document
    tfidf_matrix = vectorizer.fit_transform([text])           # Sparse Matrix: Computes TF-IDF vector of shape (1, vocab_size)

    feature_names = vectorizer.get_feature_names_out()         # Vocabulary: Array of distinct vocabulary words mapped by index
    scores = tfidf_matrix.toarray()[0]                        # Conversion: Dense 1D array of floats representing relative term weights

    word_score_pairs = list(zip(feature_names, scores))       # Tuple Mapping: Associates each keyword string with its numerical TF-IDF score
    word_score_pairs = sorted(word_score_pairs, key=lambda x: x[1], reverse=True)  # Ranking: Sorts terms in descending order of statistical importance

    return word_score_pairs[:top_n]                           # Pruning: Returns top N most salient tokens


# ──────────────────────────────────────────────────────────────────────
# Self-Test Harness: Validates Keyword Baseline
# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from data_loader import load_resume_and_job               # Helper: Multi-format document parser

    print("=== Testing tfidf_matcher.py ===")

    # Path resolution for sample files
    sample_res = os.path.join(os.path.dirname(__file__), "data", "resume.txt")
    sample_jd = os.path.join(os.path.dirname(__file__), "data", "job_description.txt")

    if not os.path.exists(sample_res):
        sample_res = os.path.join(os.path.dirname(__file__), "..", "sample_data", "resume.txt")
        sample_jd = os.path.join(os.path.dirname(__file__), "..", "sample_data", "job_description.txt")

    resume, job = load_resume_and_job(sample_res, sample_jd)  # Ingestion: Reads raw text strings
    tfidf_val = compute_tfidf_score(resume, job)              # Execution: Runs baseline vectorizer and cosine metric

    print(f"Sample Documents TF-IDF Score: {tfidf_val:.4f} ({tfidf_val:.1%})\n")

    # Keyword Failure Stress Test: Synonyms with 0 exact matches
    phrase_a = "Led a team of 5 engineers to deliver backend microservices"
    phrase_b = "Spearheaded a cohort of software developers building server-side logic"
    stress_val = compute_tfidf_score(phrase_a, phrase_b)      # Demonstrates: Orthogonal vectors evaluate to near zero

    print("--- Keyword Orthogonality Stress Test ---")
    print(f"Phrase A: '{phrase_a}'")
    print(f"Phrase B: '{phrase_b}'")
    print(f"TF-IDF Cosine Score: {stress_val:.4f} ({stress_val:.1%})")
    print("[NOTE] TF-IDF scored ~0.0 due to lack of identical word spellings!")
