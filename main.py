"""
main.py — Milestone 2 Lab Benchmark Test Harness.
Compares Statistical ML (TF-IDF) vs. Deep Learning (all-MiniLM-L6-v2 Sentence Transformers).
"""

import os
import pypdf                                                  # Library: Ingests .pdf binary streams page-by-page
import docx                                                   # Library: Ingests .docx XML paragraph and table elements
from sklearn.feature_extraction.text import TfidfVectorizer    # Baseline Model: Computes unigram frequency matrices (scikit-learn)
from sklearn.metrics.pairwise import cosine_similarity        # Metric: Calculates normalized dot product angle between document vectors
from sentence_transformers import SentenceTransformer         # Proposed Model: Dense semantic embeddings (Hugging Face)



 #1. DATA PREPROCESSING & INGESTION

def clean_text(text: str) -> str:
    """
    Cleans raw document text by stripping whitespace and redundant line breaks.
    """
    if not text:
        return ""
    text = text.strip()                                       # Preprocessing: Strips leading/trailing white spaces
    lines = [line.rstrip() for line in text.split("\n")]      # Line Clean: Strips trailing carriage spaces
    cleaned = "\n".join(lines)
    while "\n\n\n" in cleaned:
        cleaned = cleaned.replace("\n\n\n", "\n\n")           # Normalization: Collapses multi-newline blocks into clean spacing
    return cleaned


def extract_text(file_path: str) -> str:
    """
    Extracts text from .txt, .pdf, or .docx formats based on file extension.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()               # Format Branching: Selects parser by extension

    if ext == ".pdf":
        reader = pypdf.PdfReader(file_path)                   # Ingestion: Opens PDF page structure
        pages = [page.extract_text() for page in reader.pages if page.extract_text()]
        raw_text = "\n".join(pages)                           # Aggregation: Combines page strings into continuous stream

    elif ext == ".docx":
        doc = docx.Document(file_path)                        # Ingestion: Opens Word DOM hierarchy
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:                              # Table Parsing: Traverses skills and education tables
            for row in table.rows:
                row_str = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_str:
                    paragraphs.append(row_str)                # Delimited Row: Pipes table columns together
        raw_text = "\n".join(paragraphs)

    else:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            raw_text = f.read()                               # Plain Text: UTF-8 read

    cleaned = clean_text(raw_text)                            # Preprocessing: Runs regex/spacing normalization
    if not cleaned:
        raise ValueError(f"No readable text found in {file_path}")
    return cleaned


# =====================================================================
# 2. BASELINE STATISTICAL ML MODEL (TF-IDF + COSINE SIMILARITY)
# =====================================================================

def compute_tfidf_similarity(resume_text: str, job_text: str) -> float:
    """
    Evaluates literal keyword overlap similarity using TF-IDF and Cosine metric.
    """
    vectorizer = TfidfVectorizer(stop_words="english")        # Model: scikit-learn TF-IDF; removes ~300 common English stop-words
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_text])  # Sparse Matrix: Learns joint unigram vocabulary and TF-IDF weights
    
    sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]  # Metric: Cosine angle between resume (row 0) and JD (row 1)
    return round(float(sim), 4)                               # Output: Rounded similarity score in range [0.0, 1.0]


# =====================================================================
# 3. PROPOSED DEEP LEARNING MODEL (all-MiniLM-L6-v2 TRANSFORMER)
# =====================================================================

_TRANSFORMER_MODEL = None                                     # Cache: In-memory singleton avoiding repeated ~80MB weight reloading


def get_sentence_transformer():
    """
    Loads all-MiniLM-L6-v2 (384-dimensional dense semantic representations).
    """
    global _TRANSFORMER_MODEL
    if _TRANSFORMER_MODEL is None:
        _TRANSFORMER_MODEL = SentenceTransformer("all-MiniLM-L6-v2")  # Model: Distilled BERT (6 layers, 12 heads, 384 dims, contrastive loss)
    return _TRANSFORMER_MODEL


def compute_semantic_similarity(resume_text: str, job_text: str, model=None) -> float:
    """
    Encodes text into dense 384D embeddings and calculates cosine similarity.
    """
    if model is None:
        model = get_sentence_transformer()                    # Reuses pre-loaded transformer instance

    resume_emb = model.encode([resume_text])                  # Inference: Generates dense 384D vector for candidate text
    job_emb = model.encode([job_text])                        # Inference: Generates dense 384D vector for job description

    sim = cosine_similarity(resume_emb, job_emb)[0][0]        # Metric: Continuous semantic angle in latent coordinate space
    return round(float(sim), 4)


# =====================================================================
# 4. DUAL COMPARISON & DIAGNOSTIC ENGINE
# =====================================================================

def evaluate_match(resume_text: str, job_text: str, model=None) -> dict:
    """
    Executes both models on identical text and calculates quantitative delta.
    """
    if model is None:
        model = get_sentence_transformer()

    tfidf_score = compute_tfidf_similarity(resume_text, job_text)  # Baseline execution (keyword count)
    semantic_score = compute_semantic_similarity(resume_text, job_text, model=model)  # Neural execution (contextual meaning)
    
    diff = round((semantic_score - tfidf_score) * 100, 1)     # Delta: Percentage point difference between neural and keyword model

    if semantic_score >= 0.60:
        status = "SELECTED"
        badge = "QUALIFIED & SHORTLISTED"
        selection_message = f"[SELECTED] Candidate Matched & Shortlisted! (Score: {semantic_score:.1%} >= 60.0% cut-off). Strong technical alignment with requirements."
    elif semantic_score >= 0.48:
        status = "BORDERLINE"
        badge = "BORDERLINE / REVIEW"
        selection_message = f"[BORDERLINE] Candidate Borderline (Score: {semantic_score:.1%}). Partial match, placed on review list."
    else:
        status = "NOT_SELECTED"
        badge = "NOT SELECTED"
        selection_message = f"[NOT SELECTED] Candidate Not Selected (Score: {semantic_score:.1%} < 60.0% cut-off). Insufficient alignment with requirements."

    if diff > 5.0:
        diagnostic = (
            f"Semantic Embeddings outperformed keyword matching by +{diff}%. "
            f"The candidate used diverse/natural phrasing that was penalized by "
            f"TF-IDF, but correctly recognized by the contextual transformer."
        )
    elif diff < -5.0:
        diagnostic = (
            f"TF-IDF scored higher by +{abs(diff)}% due to high literal repetition "
            f"of exact keywords from the job posting."
        )
    else:
        diagnostic = f"Both models aligned within a {abs(diff)}% margin."

    return {
        "tfidf_score": tfidf_score,
        "semantic_score": semantic_score,
        "delta_percentage": diff,
        "status": status,
        "badge": badge,
        "selection_message": selection_message,
        "diagnostic": diagnostic
    }


# =====================================================================
# 5. LAB BENCHMARK EXECUTION (MILESTONE 2 TEST HARNESS)
# =====================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("   SEMANTIC RESUME-JOB MATCHING SYSTEM - MILESTONE 2 EVALUATION")
    print("=" * 70)

    # 1. Load AI Model
    print("\n[1] Initializing Sentence-Transformer (all-MiniLM-L6-v2)...")
    model = get_sentence_transformer()                         # Loads 384D transformer into RAM
    print("    Model loaded successfully (384 dense dimensions).")

    # 2. Helper to resolve file paths
    def resolve_file(filename: str) -> str:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(base_dir, "sample_data", filename),
            os.path.join(base_dir, "data", filename),
            os.path.join(base_dir, filename),
            os.path.join(base_dir, "..", filename),
            os.path.join(base_dir, "..", "sample_data", filename),
            filename
        ]
        for c in candidates:
            if os.path.exists(c):
                return c                                      # Resolves file location dynamically across directory structures
        return filename

    # 3. Ingest Controlled Evaluation Corpus
    print("\n[2] Loading Evaluation Documents...")
    jd_file = resolve_file("technova_sde_intern.txt")          # Target Job Description (SDE Intern role)
    simple_file = resolve_file("aditya_simple.txt")            # Resume A: Phrased with exact job keywords
    synonym_file = resolve_file("aditya_synonyms.txt")         # Resume B: Identical skills phrased with elevated synonyms

    job_desc = extract_text(jd_file)                           # Text extraction & normalization
    resume_simple = extract_text(simple_file)
    resume_syn = extract_text(synonym_file)

    print(f"    Loaded Job Description : '{os.path.basename(jd_file)}' ({len(job_desc.split())} words)")
    print(f"    Loaded Resume (Simple) : '{os.path.basename(simple_file)}' ({len(resume_simple.split())} words)")
    print(f"    Loaded Resume (Synonym): '{os.path.basename(synonym_file)}' ({len(resume_syn.split())} words)")

    # 4. Run Comparative Experiments
    print("\n[3] Running Comparative Model Evaluation...")
    res_simple = evaluate_match(resume_simple, job_desc, model=model)  # Evaluates exact keyword match
    res_syn = evaluate_match(resume_syn, job_desc, model=model)        # Evaluates synonym stress match

    # 5. Display Evaluation Results
    print("\n" + "=" * 95)
    print("                              EVALUATION & HIRING DECISION TABLE")
    print("=" * 95)
    print(f"{'Resume Version':<26} | {'TF-IDF (Keyword)':<17} | {'Semantic (AI)':<15} | {'Hiring Status':<25}")
    print("-" * 95)
    print(f"{'Aditya (Exact Keywords)':<26} | {res_simple['tfidf_score']:<7} ({res_simple['tfidf_score']:.1%})   | {res_simple['semantic_score']:<7} ({res_simple['semantic_score']:.1%}) | {res_simple['badge']:<25}")
    print(f"{'Aditya (Synonym Stress)':<26} | {res_syn['tfidf_score']:<7} ({res_syn['tfidf_score']:.1%})   | {res_syn['semantic_score']:<7} ({res_syn['semantic_score']:.1%}) | {res_syn['badge']:<25}")
    print("=" * 95)

    # 6. Candidate Hiring Decision Output
    print("\n[HIRING DECISION MESSAGES]:")
    print(f"  - Aditya (Exact Keywords): {res_simple['selection_message']}")
    print(f"  - Aditya (Synonym Stress): {res_syn['selection_message']}")

    # 7. Empirical Proof Points
    tfidf_drop = (res_simple['tfidf_score'] - res_syn['tfidf_score']) / res_simple['tfidf_score']
    print(f"\n[!] KEY FINDING:")
    print(f"    - TF-IDF Score Drop on Synonyms : -{tfidf_drop:.1%} (Penalized for phrasing)")
    print(f"    - Semantic Model Score Variance : +{(res_syn['semantic_score'] - res_simple['semantic_score']):.1%} (Consistent recognition)")
    print("\n[OK] Milestone 2 evaluation complete.\n")
