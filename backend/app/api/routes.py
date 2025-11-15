from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.agents.UploadResume import ResumeParser
from app.agents.PlannerAgent import PlannerAgent
from app.state.user_profiles import set_profile, get_profile, get_files, set_files
from app.services.document_generator import generate_documents

api_router = APIRouter()

parser = ResumeParser()
planner = PlannerAgent()

@api_router.post("/api/upload-docs")
async def upload_docs(
    cv: UploadFile = File(None),
    transcript: UploadFile = File(None),
    userId: str = Form(...)
):
    if not (cv or transcript):
        raise HTTPException(status_code=400, detail="Upload at least one document.")

    saved_files = {}
    parsed_profile = None

    async def _save_file(upload: UploadFile):
        user_dir = Path("storage") / "uploads" / userId
        user_dir.mkdir(parents=True, exist_ok=True)
        path = user_dir / upload.filename
        with open(path, "wb") as f:
            f.write(await upload.read())
        saved_files[upload.filename] = str(path)
        return str(path)

    cv_path = None
    transcript_path = None

    if cv:
        cv_path = await _save_file(cv)
    if transcript:
        transcript_path = await _save_file(transcript)

    files_record = get_files(userId)
    files_record.update(saved_files)

    source_path = cv_path or transcript_path
    if source_path:
        parsed_profile = parser.process(source_path)
        set_profile(userId, parsed_profile, files_record)
    else:
        set_files(userId, files_record)

    return {
        "ok": True,
        "files": files_record,
        "profile": parsed_profile
    }

@api_router.post("/api/chat")
async def chat_endpoint(payload: dict):
    message = payload["message"]
    language = payload.get("language", "en")
    user_profile = get_profile(payload.get("userId"))

    result = planner.plan(
        message=message,
        profile=user_profile,
        language=language
    )

    return result

@api_router.post("/api/apply")
async def apply(payload: dict):
    user_id = payload.get("userId")
    job = payload.get("job")

    if not user_id:
        raise HTTPException(status_code=400, detail="Missing userId")
    if not job:
        raise HTTPException(status_code=400, detail="Missing job details")

    profile = get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=400, detail="Upload a resume before applying.")

    documents = generate_documents(profile, job)

    return {
        "ok": True,
        "resume": documents["resume_text"],
        "cover_letter": documents["cover_letter"],
        "resume_pdf": documents["resume_pdf"],
        "cover_letter_pdf": documents["cover_letter_pdf"]
    }
