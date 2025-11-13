from fastapi import APIRouter, UploadFile, File, Form
from app.agents.UploadResume import ResumeParser
from app.agents.PlannerAgent import PlannerAgent

api_router = APIRouter()

parser = ResumeParser()
# profile = parser.process(file_path)

planner = PlannerAgent()

@api_router.post("/api/upload-docs")
async def upload_docs(
    cv: UploadFile = File(None),
    transcript: UploadFile = File(None),
    userId: str = Form(...)
):
    # Save files to temporary location
    saved_files = {}
    for file in [cv, transcript]:
        if file:
            path = f"/tmp/{file.filename}"
            with open(path, "wb") as f:
                f.write(await file.read())
            saved_files[file.filename] = path

    return {"ok": True, "files": list(saved_files.keys())}

@api_router.post("/api/chat")
async def chat_endpoint(payload: dict):
    message = payload["message"]
    language = payload.get("language", "en")

    # Optional: load a future parsed profile
    user_profile = None

    result = planner.plan(
        message=message,
        profile=user_profile,
        language=language
    )

    return result

@api_router.post("/api/apply")
async def apply(payload: dict):
    print("Applying to:", payload)
    return {"ok": True, "submitted": True}
