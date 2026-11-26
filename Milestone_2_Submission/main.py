import os
import pypdf
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer


# 1. Preprocessing and Text Extraction

def clean_text(text: str) -> str:
    """Removes extra whitespace and cleans up blank lines."""
    if not text:
        return ""
    text = text.strip()
    lines = [line.rstrip() for line in text.split("\n")]
    cleaned = "\n".join(lines)
    while "\n\n\n" in cleaned:
        cleaned = cleaned.replace("\n\n\n", "\n\n")
    return cleaned


def extract_text(file_path: str) -> str:
    """Extracts text from .txt, .pdf, or .docx files."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        reader = pypdf.PdfReader(file_path)
        pages = [page.extract_text() for page in reader.pages if page.extract_text()]
        raw_text = "\n".join(pages)

    elif ext == ".docx":
        doc = docx.Document(file_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        # Extract tables and join columns using pipe
        for table in doc.tables:
            for row in table.rows:
                row_str = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_str:
                    paragraphs.append(row_str)
        raw_text = "\n".join(paragraphs)

    else:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            raw_text = f.read()

    cleaned = clean_text(raw_text)
    if not cleaned:
        raise ValueError(f"No readable text found in {file_path}")
    return cleaned


# 2. Baseline Model: TF-IDF with Cosine Similarity

def compute_tfidf_similarity(resume_text: str, job_text: str) -> float:
    """Computes keyword match score using scikit-learn TF-IDF."""
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([resume_text, job_text])
    sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(sim), 4)


# 3. Proposed AI Model: Sentence-BERT (all-MiniLM-L6-v2)

_TRANSFORMER_MODEL = None

def get_sentence_transformer():
    """Loads and caches all-MiniLM-L6-v2 model in memory."""
    global _TRANSFORMER_MODEL
    if _TRANSFORMER_MODEL is None:
        _TRANSFORMER_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _TRANSFORMER_MODEL


def compute_semantic_similarity(resume_text: str, job_text: str, model=None) -> float:
    """Encodes texts into 384-dimensional dense vectors and calculates cosine similarity."""
    if model is None:
        model = get_sentence_transformer()

    resume_emb = model.encode([resume_text])
    job_emb = model.encode([job_text])

    sim = cosine_similarity(resume_emb, job_emb)[0][0]
    return round(float(sim), 4)


# 4. Evaluation and Candidate Qualification

def evaluate_match(resume_text: str, job_text: str, model=None) -> dict:
    """Runs both models and determines if candidate is shortlisted."""
    if model is None:
        model = get_sentence_transformer()

    tfidf_score = compute_tfidf_similarity(resume_text, job_text)
    semantic_score = compute_semantic_similarity(resume_text, job_text, model=model)
    diff = round((semantic_score - tfidf_score) * 100, 1)

    # Qualification threshold: 60% cut-off
    if semantic_score >= 0.60:
        badge = "QUALIFIED & SHORTLISTED"
        selection_message = f"[SELECTED] Candidate Matched & Shortlisted! (Score: {semantic_score:.1%} >= 60% cut-off)."
    elif semantic_score >= 0.48:
        badge = "BORDERLINE / REVIEW"
        selection_message = f"[BORDERLINE] Candidate placed on manual review (Score: {semantic_score:.1%})."
    else:
        badge = "NOT SELECTED"
        selection_message = f"[NOT SELECTED] Candidate does not meet requirements (Score: {semantic_score:.1%} < 60% cut-off)."

    return {
        "tfidf_score": tfidf_score,
        "semantic_score": semantic_score,
        "delta_percentage": diff,
        "badge": badge,
        "selection_message": selection_message,
    }


# 5. Benchmark Execution

if __name__ == "__main__":
    print("=" * 70)
    print("   RESUMATCH - MILESTONE 2 MODEL EVALUATION")
    print("=" * 70)

    print("\n[1] Loading Sentence-Transformer (all-MiniLM-L6-v2)...")
    model = get_sentence_transformer()
    print("    Model loaded successfully.")

    def resolve_file(filename: str) -> str:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(base_dir, "sample_data", filename),
            os.path.join(base_dir, "data", filename),
            os.path.join(base_dir, filename),
            os.path.join(base_dir, "..", "sample_data", filename),
            os.path.join(base_dir, "..", filename),
            filename
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return filename

    print("\n[2] Loading Evaluation Documents...")
    jd_file = resolve_file("technova_sde_intern.txt")
    simple_file = resolve_file("aditya_simple.txt")
    synonym_file = resolve_file("aditya_synonyms.txt")

    job_desc = extract_text(jd_file)
    resume_simple = extract_text(simple_file)
    resume_syn = extract_text(synonym_file)

    print(f"    Loaded Job Description : '{os.path.basename(jd_file)}' ({len(job_desc.split())} words)")
    print(f"    Loaded Resume (Simple) : '{os.path.basename(simple_file)}' ({len(resume_simple.split())} words)")
    print(f"    Loaded Resume (Synonym): '{os.path.basename(synonym_file)}' ({len(resume_syn.split())} words)")

    print("\n[3] Running Comparative Model Evaluation...")
    res_simple = evaluate_match(resume_simple, job_desc, model=model)
    res_syn = evaluate_match(resume_syn, job_desc, model=model)

    print("\n" + "=" * 85)
    print("                          EVALUATION RESULTS TABLE")
    print("=" * 85)
    print(f"{'Resume Version':<26} | {'TF-IDF (Keyword)':<17} | {'Semantic (AI)':<15} | {'Status':<20}")
    print("-" * 85)
    print(f"{'Aditya (Exact Keywords)':<26} | {res_simple['tfidf_score']:<7} ({res_simple['tfidf_score']:.1%})   | {res_simple['semantic_score']:<7} ({res_simple['semantic_score']:.1%}) | {res_simple['badge']}")
    print(f"{'Aditya (Synonym Stress)':<26} | {res_syn['tfidf_score']:<7} ({res_syn['tfidf_score']:.1%})   | {res_syn['semantic_score']:<7} ({res_syn['semantic_score']:.1%}) | {res_syn['badge']}")
    print("=" * 85)

    print("\n[HIRING DECISIONS]:")
    print(f"  - Aditya (Exact Keywords): {res_simple['selection_message']}")
    print(f"  - Aditya (Synonym Stress): {res_syn['selection_message']}")

    tfidf_drop = (res_simple['tfidf_score'] - res_syn['tfidf_score']) / res_simple['tfidf_score']
    print(f"\n[KEY FINDING FOR MILESTONE 2]:")
    print(f"  - TF-IDF Drop on Synonyms : -{tfidf_drop:.1%} (Penalized for vocabulary)")
    print(f"  - Semantic Model Variance : +{(res_syn['semantic_score'] - res_simple['semantic_score']):.1%} (Consistently recognized)")
    print("\nMilestone 2 benchmark completed successfully.\n")
