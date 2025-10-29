from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="JobSearch Co-Pilot API")

class ResumeIn(BaseModel):
    text: str
    preferences: Optional[dict] = None

class JobPosting(BaseModel):
    source: str
    job_id: str
    title: str
    company: str
    location: Optional[str] = None
    description: str
    url: Optional[str] = None
    score: Optional[float] = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest/resume")
def ingest_resume(payload: ResumeIn):
    # TODO: call memory/indexing and skill extraction
    return {"ok": True, "skills": ["python", "fastapi", "langgraph"]}

@app.get("/jobs/search", response_model=List[JobPosting])
def jobs_search(q: str = "software engineer"):
    # TODO: call JobScoutAgent -> Indeed first
    return [
        JobPosting(
            source="indeed",
            job_id="EXAMPLE-1",
            title="Software Engineer",
            company="Acme Inc.",
            description="Build backend services in FastAPI.",
            score=0.78,
            url="https://example.com/jobs/1",
        )
    ]

@app.post("/apply/{source}/{job_id}")
def apply_job(source: str, job_id: str):
    # TODO: Hybrid auto-apply; for LinkedIn provide checklist
    return {"ok": True, "mode": "auto" if source in ["indeed","ziprecruiter"] else "checklist"}
