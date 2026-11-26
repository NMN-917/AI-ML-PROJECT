"""
api.py — Asynchronous REST API Backend & Interactive UI Server.
Framework: FastAPI + Uvicorn + Pydantic v2.
Includes Candidate Qualification / Selection Classification.
"""

import os
from fastapi import FastAPI, HTTPException, UploadFile, File   # Framework: FastAPI async routing and HTTP exception handling
from fastapi.responses import HTMLResponse                    # Response: Renders HTML dashboard for browser requests
from pydantic import BaseModel, Field                         # Schema: Pydantic data validation and auto-generated Swagger OpenAPI spec

from matcher import compare_methods                           # Comparator: Unified dual-model execution pipeline
from embedding_matcher import load_model                      # Neural Model: all-MiniLM-L6-v2 cached loader
from data_loader import load_text_from_bytes                  # Parser: Multi-format in-memory byte extractor (.pdf, .docx, .txt)


# =====================================================================
# PYDANTIC DATA VALIDATION SCHEMAS
# =====================================================================

class MatchRequest(BaseModel):
    """Input payload validation schema for POST /match."""
    resume_text: str = Field(..., min_length=1, description="Raw text of candidate resume")
    job_text: str = Field(..., min_length=1, description="Raw text of target job posting")


class MatchResponse(BaseModel):
    """Output payload schema defining dual-model scores, diagnosis, and selection decision."""
    tfidf_score: float = Field(..., description="TF-IDF keyword cosine similarity (0.0 - 1.0)")
    embedding_score: float = Field(..., description="Sentence transformer semantic cosine similarity (0.0 - 1.0)")
    explanation: str = Field(..., description="Diagnostic comparison detailing lexical vs semantic shift")
    status: str = Field(default="SELECTED", description="Hiring qualification status: SELECTED, BORDERLINE, or NOT_SELECTED")
    is_selected: bool = Field(default=True, description="True if candidate passed qualification cut-off")
    qualification_badge: str = Field(default="", description="Badge label indicating hiring decision")
    selection_message: str = Field(default="", description="Detailed message stating whether candidate is selected or rejected")


# =====================================================================
# APPLICATION & MODEL INITIALIZATION
# =====================================================================

app = FastAPI(                                                # App Instance: Generates Swagger UI at /docs and ReDoc at /redoc
    title="RESUMATCH API",
    description="RESUMATCH: AI-Driven Semantic Resume–Job Matching System with Automated Candidate Selection.",
    version="2.1.0",
)

print("Loading AI Model at server startup...")
model = load_model()                                          # In-Memory Cache: Single-instance MiniLM transformer for zero-latency inference
print("Model loaded into memory. Server ready.\n")


# =====================================================================
# REST ENDPOINTS
# =====================================================================

@app.get("/", response_class=HTMLResponse)
def read_root():
    """
    Renders interactive glassmorphism web dashboard.
    """
    html_file = os.path.join(os.path.dirname(__file__), "frontend.html")  # Resolution: Serves co-located frontend dashboard
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())             # Serving: Transmits HTML to client browser
    return HTMLResponse("<h1>RESUMATCH</h1><p>Frontend file not found.</p>")


@app.post("/match", response_model=MatchResponse)
def match_resume_to_job(request: MatchRequest):
    """
    Evaluates JSON raw text payloads using TF-IDF and Sentence Transformers with hiring classification.
    """
    if not request.resume_text.strip() or not request.job_text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty or whitespace only.")

    result = compare_methods(                                 # Pipeline Execution: Evaluates both algorithms on input texts
        resume_text=request.resume_text,
        job_text=request.job_text,
        model=model,                                          # Reuses in-memory 384D transformer instance
    )

    return MatchResponse(                                     # Serialization: Validates and returns JSON response payload
        tfidf_score=result["tfidf_score"],
        embedding_score=result["embedding_score"],
        explanation=result["explanation"],
        status=result["status"],
        is_selected=result["is_selected"],
        qualification_badge=result["qualification_badge"],
        selection_message=result["selection_message"],
    )


@app.post("/match-files", response_model=MatchResponse)
async def match_resume_files(
    resume_file: UploadFile = File(..., description="Upload resume (.pdf, .docx, .txt)"),
    job_file: UploadFile = File(..., description="Upload job posting (.pdf, .docx, .txt)"),
):
    """
    Extracts text from uploaded multi-format files and executes dual-model evaluation with hiring decision.
    """
    try:
        resume_bytes = await resume_file.read()               # Async Stream: Reads incoming multipart file bytes
        resume_text = load_text_from_bytes(resume_bytes, resume_file.filename)  # In-Memory Parse: Converts bytes to string
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing resume '{resume_file.filename}': {str(e)}")

    try:
        job_bytes = await job_file.read()                     # Async Stream: Reads incoming job description bytes
        job_text = load_text_from_bytes(job_bytes, job_file.filename)  # In-Memory Parse: Converts bytes to string
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing job description '{job_file.filename}': {str(e)}")

    result = compare_methods(resume_text, job_text, model=model)  # Execution: Computes dual scores and candidate selection

    return MatchResponse(
        tfidf_score=result["tfidf_score"],
        embedding_score=result["embedding_score"],
        explanation=result["explanation"],
        status=result["status"],
        is_selected=result["is_selected"],
        qualification_badge=result["qualification_badge"],
        selection_message=result["selection_message"],
    )


# =====================================================================
# ASGI SERVER RUNNER
# =====================================================================

if __name__ == "__main__":
    import uvicorn                                            # ASGI Server: High-performance asynchronous HTTP server
    print("Starting API Server at http://localhost:8000")
    print("Interactive Swagger Docs at http://localhost:8000/docs\n")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
