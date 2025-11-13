# backend/main.py
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.agents.PlannerAgent import PlannerAgent
from app.agents.UploadResume import UploadResumeAgent
from app.memory.vector import VectorStore

app = FastAPI(title="JobSearch Co-Pilot API (Python Orchestrator)")

# ------------------------------------------------------
# GLOBAL AGENT SINGLETONS
# ------------------------------------------------------
planner = PlannerAgent()
uploader = UploadResumeAgent()
vector_store = VectorStore()

# ------------------------------------------------------
# MODELS
# ------------------------------------------------------
class StartWorkflowInput(BaseModel):
    user_message: str
    user_data: Optional[Dict[str, Any]] = None

# ------------------------------------------------------
# BASIC HEALTH ROUTE
# ------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "agents_loaded": list(planner.agents.keys())}

# ------------------------------------------------------
# 1) START WORKFLOW
# ------------------------------------------------------
@app.post("/workflow/start")
def start_workflow(payload: StartWorkflowInput):
    plan = planner.create_workflow_plan(payload.user_message, payload.user_data)
    planner.active_workflows[plan.plan_id] = plan

    return {
        "workflow_id": plan.plan_id,
        "user_goal": plan.user_goal,
        "status": "running",
        "tasks": [t.description for t in plan.tasks],
        "estimated_completion": plan.estimated_completion.isoformat(),
        "progress": {
            "percentage": 0,
            "total_tasks": len(plan.tasks)
        }
    }

# ------------------------------------------------------
# 2) EXECUTE WORKFLOW (blocking)
# ------------------------------------------------------
@app.post("/workflow/{workflow_id}/execute")
def execute_workflow(workflow_id: str):
    if workflow_id not in planner.active_workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    plan = planner.active_workflows[workflow_id]
    results = planner.execute_workflow(plan)
    return results

# ------------------------------------------------------
# 3) CHECK STATUS
# ------------------------------------------------------
@app.get("/workflow/{workflow_id}/status")
def workflow_status(workflow_id: str):
    return planner.get_workflow_status(workflow_id)

# ------------------------------------------------------
# 4) GET FINAL RESULTS
# ------------------------------------------------------
@app.get("/workflow/{workflow_id}/results")
def workflow_results(workflow_id: str):
    return planner.combine_results(workflow_id)

# ------------------------------------------------------
# 5) UPLOAD DOCUMENTS (resume, transcript, etc.)
# ------------------------------------------------------
@app.post("/upload/documents")
async def upload_docs(file: UploadFile = File(...)):
    file_bytes = await file.read()

    # Extract text and profile
    parsed = uploader.process_file_bytes(file_bytes, file.filename)

    # Store vector embedding
    vector_id = str(uuid.uuid4())
    vector_store.add_vector(vector_id, parsed["text"])

    return {
        "filename": file.filename,
        "resume_text": parsed.get("text"),
        "skills": parsed.get("skills", []),
        "vector_id": vector_id
    }
