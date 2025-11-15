import json
import base64
import re
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
    contact_block = _contact_block(profile)

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
    else:
        cover_letter = _remove_placeholder_lines(cover_letter)

    core_resume_text = _clean_resume_sections(_strip_existing_contact(resume_text, contact_block))
    resume_text_full = _prepend_contact_block(core_resume_text, contact_block)
    cover_letter = _prepend_contact_block(cover_letter, contact_block)

    resume_plain = _markdown_to_plain(core_resume_text, is_resume=True)
    cover_plain = _markdown_to_plain(cover_letter)

    try:
        resume_pdf = _render_resume_pdf(resume_plain, contact_block)
    except Exception as exc:
        resume_pdf = _render_resume_pdf(resume_plain[:2000], contact_block)
        resume_text_full = f"{resume_text_full}\n\n(Note: PDF fallback due to error: {exc})"

    try:
        cover_pdf = _render_pdf(cover_plain, "Cover Letter", show_title=False)
    except Exception as exc:
        cover_pdf = _render_pdf(cover_plain[:2000], "Cover Letter (fallback)")
        cover_letter = f"{cover_letter}\n\n(Note: PDF fallback due to error: {exc})"

    return {
        "resume_text": resume_text_full,
        "cover_letter": cover_letter,
        "resume_pdf": base64.b64encode(resume_pdf).decode("utf-8"),
        "cover_letter_pdf": base64.b64encode(cover_pdf).decode("utf-8"),
    }


def _render_pdf(text: str, title: str, show_title: bool = True) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER
    margin = 0.8 * inch
    y = height - margin

    if show_title:
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


def _render_resume_pdf(body_text: str, contact_block: str) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER
    margin = 0.8 * inch
    y = height - margin

    contact_lines = [line.strip() for line in contact_block.splitlines() if line.strip()]
    if contact_lines:
        name = contact_lines[0]
        rest = contact_lines[1:]
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y, name)
        y -= 16
        if rest:
            c.setFont("Helvetica", 10)
            c.drawString(margin, y, " | ".join(rest))
            y -= 16
        c.line(margin, y, width - margin, y)
        y -= 18

    c.setFont("Helvetica", 11)
    line_height = 14
    heading_pattern = re.compile(r"^[A-Z][A-Z0-9\s&,-]{1,50}$")

    for raw_line in body_text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            y -= line_height
            continue
        if heading_pattern.match(stripped):
            y -= 4
            c.setFont("Helvetica-Bold", 11)
            c.drawString(margin, y, stripped)
            y -= line_height
            c.line(margin, y, width - margin, y)
            y -= 8
            c.setFont("Helvetica", 11)
            continue

        wrapped = wrap(stripped, width=90) or [""]
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


def _markdown_to_plain(text: str, is_resume: bool = False) -> str:
    if not text:
        return ""
    cleaned = text.replace("```", "")
    cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"__([^_]+)__", r"\1", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"^#+\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.replace("* ", "- ")
    cleaned = cleaned.replace("• ", "- ")
    lines = []
    for line in cleaned.splitlines():
        stripped = line.strip()
        if is_resume and re.fullmatch(r"\[[^\]]+\]", stripped):
            continue
        if stripped.lower() == "markdown":
            continue
        lines.append(line)
    cleaned = "\n".join(lines)

    if is_resume:
        cleaned = re.sub(
            r"^(summary|experience|work experience|skills|education)(:)?",
            lambda m: f"{m.group(1).upper()}{':' if m.group(2) else ''}",
            cleaned,
            flags=re.IGNORECASE | re.MULTILINE
        )
    return cleaned


def _contact_block(profile: Dict[str, Any]) -> str:
    lines = []
    name = profile.get("name") or profile.get("full_name")
    email = profile.get("email") or profile.get("contact_email")
    phone = profile.get("phone") or profile.get("phone_number")
    location = profile.get("location")
    links = profile.get("links") or {}
    linkedin = profile.get("linkedin_url") or links.get("linkedin")
    github = profile.get("github_url") or links.get("github")

    for value in [name, email, phone, location, linkedin, github]:
        if value:
            lines.append(str(value))
    return "\n".join(lines)


def _prepend_contact_block(text: str, block: str) -> str:
    text = text.strip()
    if text.startswith(block):
        return text
    return f"{block}\n\n{text}"


def _remove_placeholder_lines(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.fullmatch(r"\[[^\]]+\]", stripped):
            continue
        lines.append(line)
    return "\n".join(lines)


def _strip_existing_contact(text: str, contact_block: str) -> str:
    if not contact_block:
        return text
    contact_lines = [line.strip().lower() for line in contact_block.splitlines() if line.strip()]
    lines = []
    skipping = True
    for line in text.splitlines():
        stripped = line.strip().lower()
        if skipping and (not stripped or stripped in contact_lines):
            continue
        skipping = False
        lines.append(line)
    return "\n".join(lines).strip()


def _clean_resume_sections(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.fullmatch(r"\[[^\]]+\]", stripped):
            continue
        lines.append(stripped)
    return "\n".join(lines)
