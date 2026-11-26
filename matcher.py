"""
matcher.py — Unified Dual-Evaluation Engine & Candidate Qualification Classifier.
Integrates Baseline (TF-IDF), Proposed (Sentence Transformers all-MiniLM-L6-v2),
and automated candidate qualification / selection decision logic.
"""

import os
from tfidf_matcher import compute_tfidf_score                  # Baseline Model: Computes keyword-based sparse TF-IDF cosine similarity
from embedding_matcher import compute_embedding_score, load_model  # Proposed Model: Computes dense 384D semantic transformer similarity


def determine_qualification(semantic_score: float, threshold: float = 0.60) -> dict:
    """
    Classifies candidate qualification and generates an automated hiring decision message.
    """
    if semantic_score >= threshold:
        status = "SELECTED"
        is_selected = True
        badge = "QUALIFIED & SHORTLISTED FOR INTERVIEW"
        message = (
            f"[SELECTED] Candidate Matched & Shortlisted! "
            f"The candidate's qualifications exhibit strong semantic alignment "
            f"({semantic_score:.1%} match, exceeding the {threshold:.0%} requirement cut-off). "
            f"The profile demonstrates the necessary technical competencies and is officially selected for the technical interview."
        )
    elif semantic_score >= (threshold - 0.12):
        status = "BORDERLINE"
        is_selected = False
        badge = "BORDERLINE — REQUIRES MANUAL REVIEW"
        message = (
            f"[BORDERLINE] Candidate Borderline / Under Review. "
            f"The candidate achieved a match score of {semantic_score:.1%}, indicating partial overlap with role requirements. "
            f"Placed on hold for manual recruiter review."
        )
    else:
        status = "NOT_SELECTED"
        is_selected = False
        badge = "NOT SELECTED / REJECTED"
        message = (
            f"[NOT SELECTED] Candidate Not Selected. "
            f"The candidate's score ({semantic_score:.1%}) falls below the minimum qualification cut-off ({threshold:.0%}). "
            f"The profile lacks the required technical competencies for this job description."
        )

    return {
        "status": status,
        "is_selected": is_selected,
        "qualification_badge": badge,
        "selection_message": message,
    }


def compare_methods(resume_text: str, job_text: str, model=None, threshold: float = 0.60) -> dict:
    """
    Executes concurrent dual-model evaluation and generates hiring decision.
    """
    if model is None:
        model = load_model()                                  # Optimization: Reuses single in-memory instance of all-MiniLM-L6-v2

    tfidf_score = compute_tfidf_score(resume_text, job_text)  # Statistical ML: Baseline keyword overlap score
    embedding_score = compute_embedding_score(resume_text, job_text, model=model)  # Deep Learning: Contextual semantic score

    explanation = generate_explanation(tfidf_score, embedding_score)  # Diagnostics: Lexical vs semantic explanation
    decision = determine_qualification(embedding_score, threshold=threshold)  # Decision Logic: Qualification & selection message

    return {                                                  # Output Schema: Consumed by CLI and FastAPI endpoints
        "tfidf_score": tfidf_score,
        "embedding_score": embedding_score,
        "explanation": explanation,
        "status": decision["status"],
        "is_selected": decision["is_selected"],
        "qualification_badge": decision["qualification_badge"],
        "selection_message": decision["selection_message"],
    }


def generate_explanation(tfidf_score: float, embedding_score: float) -> str:
    """
    Produces qualitative diagnosis based on mathematical delta between models.
    """
    diff_percent = round(abs(embedding_score - tfidf_score) * 100, 1)  # Metric Delta: Absolute percentage point shift between models

    if embedding_score > tfidf_score:
        return (                                              # Case 1: Semantic superiority (synonyms/natural phrasing detected)
            f"The semantic (embedding) matcher scored higher by +{diff_percent}% "
            f"({embedding_score:.2%} vs {tfidf_score:.2%}). "
            f"The candidate expressed relevant skills using natural phrasing or synonyms "
            f"penalized by keyword TF-IDF, but captured by the contextual transformer."
        )
    elif tfidf_score > embedding_score:
        return (                                              # Case 2: Exact keyword repetition / high literal token frequency
            f"TF-IDF scored higher by +{diff_percent}% "
            f"({tfidf_score:.2%} vs {embedding_score:.2%}) "
            f"due to high literal keyword repetition from the job posting."
        )
    else:
        return (                                              # Case 3: Complete alignment between lexical and semantic distributions
            f"Both models aligned identically at {tfidf_score:.2%}, "
            f"indicating balanced keyword overlap and conceptual alignment."
        )


# ──────────────────────────────────────────────────────────────────────
# Self-Test Harness
# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from data_loader import load_resume_and_job               # Helper: Multi-format document parser

    print("=== Testing matcher.py with Qualification Classifier ===")

    # Path resolution
    sample_res = os.path.join(os.path.dirname(__file__), "data", "aditya_simple.txt")
    sample_jd = os.path.join(os.path.dirname(__file__), "data", "technova_sde_intern.txt")

    if not os.path.exists(sample_res):
        sample_res = os.path.join(os.path.dirname(__file__), "aditya_simple.txt")
        sample_jd = os.path.join(os.path.dirname(__file__), "technova_sde_intern.txt")

    resume, job = load_resume_and_job(sample_res, sample_jd)  # Ingestion: Loads documents
    transformer = load_model()                                # Model Init: all-MiniLM-L6-v2
    res = compare_methods(resume, job, model=transformer)     # Evaluation: Dual execution

    print(f"TF-IDF Score       : {res['tfidf_score']:.4f} ({res['tfidf_score']:.1%})")
    print(f"Embedding Score    : {res['embedding_score']:.4f} ({res['embedding_score']:.1%})")
    print(f"Status             : {res['status']} ({res['qualification_badge']})")
    print(f"Selection Message  :\n{res['selection_message']}")
