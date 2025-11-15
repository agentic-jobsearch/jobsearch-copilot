import json
import base64
from io import BytesIO
from textwrap import wrap
from typing import Dict, Any

from openai import OpenAI
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from app.core.env import require_env

_client = OpenAI(api_key=require_env("OPENAI_API_KEY"))


def _format_profile(profile: Dict[str, Any]) -> str:
    skills = profile.get("skills") or []
    education = profile.get("education") or []
    work = profile.get("work_experience") or profile.get("workExperience") or []

    education_text = json.dumps(education[:3], ensure_ascii=False)
    work_text = json.dumps(work[:5], ensure_ascii=False)

    return f"""
Name: {profile.get('name', 'Candidate')}
Title: {profile.get('title', '')}
Location: {profile.get('location', '')}
Years Experience: {profile.get('years_experience', '')}
Skills: {', '.join(skills)}
Education: {education_text}
Work History: {work_text}
Summary: {profile.get('summary', '')}
"""


def _format_job(job: Dict[str, Any]) -> str:
    skills = job.get("skills") or job.get("skill_keywords") or ""
    description = job.get("description") or job.get("job_description") or ""
    requirements = job.get("requirements") or ""

    return f"""
Job Title: {job.get('job_title') or job.get('title')}
Company: {job.get('company')}
Location: {job.get('location')}
Skills Requested: {skills}
Responsibilities/Description: {description}
Additional Requirements: {requirements}
"""


def _chat_completion(prompt: str, temperature: float = 0.2) -> str:
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that writes professional job application materials using only the provided information."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def generate_documents(profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, str]:
    formatted_profile = _format_profile(profile)
    formatted_job = _format_job(job)

    resume_prompt = f"""
Using the candidate and job information below, draft a concise, tailored resume in Markdown.
Focus on relevant accomplishments and align their experience to the job.
Do not invent skills or experience beyond what is provided.

Candidate Info:
{formatted_profile}

Job Info:
{formatted_job}
"""

    cover_prompt = f"""
Write a professional cover letter (max 4 paragraphs) tailored to the job below.
Link the candidate's actual experience to the responsibilities and highlight genuine skills.
Keep tone confident and respectful.

Candidate Info:
{formatted_profile}

Job Info:
{formatted_job}
"""

    try:
        resume_text = _chat_completion(resume_prompt, temperature=0.3)
    except Exception as exc:
        resume_text = f"Unable to generate resume: {exc}"

    try:
        cover_letter = _chat_completion(cover_prompt, temperature=0.25)
    except Exception as exc:
        cover_letter = f"Unable to generate cover letter: {exc}"

    try:
        resume_pdf = _render_pdf(resume_text, "Tailored Resume")
    except Exception as exc:
        resume_pdf = _render_pdf(str(resume_text)[:2000], "Tailored Resume (fallback)")
        resume_text = f"{resume_text}\n\n(Note: PDF fallback due to error: {exc})"

    try:
        cover_pdf = _render_pdf(cover_letter, "Cover Letter")
    except Exception as exc:
        cover_pdf = _render_pdf(str(cover_letter)[:2000], "Cover Letter (fallback)")
        cover_letter = f"{cover_letter}\n\n(Note: PDF fallback due to error: {exc})"

    return {
        "resume_text": resume_text,
        "cover_letter": cover_letter,
        "resume_pdf": base64.b64encode(resume_pdf).decode("utf-8"),
        "cover_letter_pdf": base64.b64encode(cover_pdf).decode("utf-8"),
    }


def _render_pdf(text: str, title: str) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER
    margin = 0.8 * inch
    y = height - margin

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, title)
    y -= 0.4 * inch

    c.setFont("Helvetica", 11)
    max_line_width = width - 2 * margin
    line_height = 14

    for raw_line in text.splitlines():
        if not raw_line.strip():
            y -= line_height
            continue
        wrapped = wrap(raw_line, width=90) or [""]
        for line in wrapped:
            if y <= margin:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica", 11)
            c.drawString(margin, y, line)
            y -= line_height

    c.save()
    buffer.seek(0)
    return buffer.read()
