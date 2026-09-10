import os
import io
import sys
import shutil
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from service.service import trainer_service

# Initialize FastAPI app
app = FastAPI(
    title="AI Interview Trainer Agent (RAG & Watsonx)",
    description="Problem Statement No.22 – AI-powered Interview Trainer Agent for technical, behavioral, and HR interview mastery.",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory setup
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Static and template directories
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Request Models
class PlanRequest(BaseModel):
    profile_name: str
    experience_level: str
    job_role: str
    target_company: Optional[str] = "Top Tier Tech"
    custom_notes: Optional[str] = ""

class EvaluationRequest(BaseModel):
    question: str
    user_answer: str
    question_category: Optional[str] = "Technical"
    role: Optional[str] = "Software Engineer"


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serves the main single-page web application."""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        return HTMLResponse("<h1>Loading Interview Trainer UI...</h1>", status_code=200)
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/api/generate-plan")
async def generate_plan(payload: PlanRequest):
    """Generates tailored question set, model answers, and preparation roadmap via RAG."""
    try:
        plan = trainer_service.generate_interview_plan(
            profile_name=payload.profile_name,
            experience_level=payload.experience_level,
            job_role=payload.job_role,
            target_company=payload.target_company or "Top Tier Tech",
            custom_notes=payload.custom_notes or ""
        )
        return JSONResponse(content={"status": "success", "data": plan})
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": f"Failed to generate plan: {str(e)}"},
            status_code=500
        )


@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Receives resume (PDF, TXT, DOCX), parses and indexes candidate skills in VectorDB."""
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = trainer_service.ingest_resume(str(file_path))
        return JSONResponse(content={
            "status": "success",
            "filename": file.filename,
            "skills_summary": result.get("skills_summary", []),
            "preview": result.get("preview", "")
        })
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": f"Resume upload failed: {str(e)}"},
            status_code=500
        )


@app.post("/api/evaluate-answer")
async def evaluate_answer(payload: EvaluationRequest):
    """Evaluates candidate response in live mock interview simulation."""
    try:
        feedback = trainer_service.evaluate_mock_answer(
            question=payload.question,
            user_answer=payload.user_answer,
            question_category=payload.question_category or "Technical",
            role=payload.role or "Software Engineer"
        )
        return JSONResponse(content={"status": "success", "data": feedback})
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": f"Evaluation error: {str(e)}"},
            status_code=500
        )


@app.get("/api/roles")
async def get_preconfigured_roles():
    """Returns curated job roles and experience levels."""
    return JSONResponse(content={
        "roles": [
            "Full Stack Developer",
            "Frontend Engineer (React / Next.js)",
            "Backend Engineer (Python / Node.js / Go)",
            "AI / Machine Learning Engineer",
            "Data Scientist",
            "DevOps & Cloud Engineer (AWS / Kubernetes)",
            "Software Architect / System Designer",
            "Product Manager (Technical)",
            "Cybersecurity Specialist",
            "Mobile App Developer (Flutter / React Native / iOS)"
        ],
        "experience_levels": [
            "Entry Level / College Graduate (0-1 yrs)",
            "Junior Engineer (1-3 yrs)",
            "Mid-Level Professional (3-5 yrs)",
            "Senior Engineer (5-8 yrs)",
            "Staff / Lead Architect (8+ yrs)"
        ]
    })


if __name__ == "__main__":
    print("=" * 65)
    print("🚀 Starting AI Interview Trainer Agent on http://127.0.0.1:8000")
    print("=" * 65)
    uvicorn.run("main.py:app", host="127.0.0.1", port=8000, reload=False)
