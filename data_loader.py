import os
import io

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import docx
except ImportError:
    docx = None


# ========================================================
# DATA PREPROCESSING PART 1: Text Cleaning & Normalization
# ========================================================

def clean_text(text: str) -> str:
    """
    DATA PREPROCESSING:
    Cleans up raw text by removing extra whitespace, trailing tabs,
    and collapsing multiple redundant blank lines.
    """
    if not text:
        return ""

    # Strip spaces from start, end, and each individual line
    text = text.strip()
    lines = [line.rstrip() for line in text.split("\n")]
    cleaned = "\n".join(lines)

    # Collapse multiple blank lines down to clean double newlines
    while "\n\n\n" in cleaned:
        cleaned = cleaned.replace("\n\n\n", "\n\n")

    return cleaned


# ========================================================
# DATA PREPROCESSING PART 2: Multi-Format Document Ingestion
# ========================================================

def extract_text_from_pdf(file_input) -> str:
    """
    DATA PREPROCESSING:
    Extracts text page by page from PDF files using pypdf.
    """
    if pypdf is None:
        raise ImportError("pypdf is required. Install it using: pip install pypdf")

    reader = pypdf.PdfReader(file_input)
    pages_text = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pages_text.append(page_text)

    return "\n".join(pages_text)


def extract_text_from_docx(file_input) -> str:
    """
    DATA PREPROCESSING:
    Extracts text from Word documents, including paragraphs
    and complex nested tables (skills, projects, education).
    """
    if docx is None:
        raise ImportError("python-docx is required. Install it using: pip install python-docx")

    doc = docx.Document(file_input)
    paragraphs = []

    # Read regular text paragraphs
    for p in doc.paragraphs:
        if p.text.strip():
            paragraphs.append(p.text.strip())

    # DATA PREPROCESSING: Parse nested tables and join columns using pipe delimiter (|)
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                paragraphs.append(row_text)

    return "\n".join(paragraphs)


def load_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    """
    DATA PREPROCESSING:
    Parses in-memory uploaded file bytes based on file extension.
    """
    extension = os.path.splitext(filename)[1].lower()
    stream = io.BytesIO(file_bytes)

    if extension == ".pdf":
        raw_text = extract_text_from_pdf(stream)
    elif extension == ".docx":
        raw_text = extract_text_from_docx(stream)
    else:
        raw_text = file_bytes.decode("utf-8", errors="replace")

    # DATA PREPROCESSING: Apply text cleaning
    cleaned = clean_text(raw_text)
    if len(cleaned) == 0:
        raise ValueError(f"File '{filename}' has no readable text.")

    return cleaned


# ========================================================
# DATA PREPROCESSING PART 3: Pipeline Loader & Sanitization
# ========================================================

def load_text_from_file(file_path: str) -> str:
    """
    DATA PREPROCESSING:
    Reads local files (.pdf, .docx, .txt), handles UTF-8 decoding fallbacks,
    and returns sanitized, normalized text.
    """
    if not os.path.exists(file_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.basename(file_path)
        candidates = [
            os.path.join(base_dir, "sample_data", filename),
            os.path.join(base_dir, "data", filename),
            os.path.join(base_dir, filename),
            os.path.join(base_dir, "..", "sample_data", filename),
            os.path.join(base_dir, "..", filename),
        ]
        found = False
        for alt in candidates:
            if os.path.exists(alt):
                file_path = alt
                found = True
                break
        if not found:
            raise FileNotFoundError(f"File not found: {file_path}")

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif extension == ".docx":
        raw_text = extract_text_from_docx(file_path)
    else:
        # DATA PREPROCESSING: UTF-8 decode with replacement fallback for corrupted bytes
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            raw_text = f.read()

    # DATA PREPROCESSING: Clean and normalize whitespace
    cleaned = clean_text(raw_text)
    if len(cleaned) == 0:
        raise ValueError(f"File '{file_path}' is empty or has no readable text.")

    return cleaned


def load_resume_and_job(resume_path: str, job_path: str) -> tuple:
    """Convenience loader returning both cleaned resume and job description text."""
    return load_text_from_file(resume_path), load_text_from_file(job_path)


if __name__ == "__main__":
    print("Testing data_loader.py (Data Preprocessing Pipeline)...")
    res_text, jd_text = load_resume_and_job("aditya_simple.txt", "technova_sde_intern.txt")
    print(f"Loaded Clean Job Description: {len(jd_text)} characters")
    print(f"Loaded Clean Resume         : {len(res_text)} characters")
    print("Data Preprocessing pipeline verified successfully!")
