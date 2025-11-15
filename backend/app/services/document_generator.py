import json
from typing import Dict, Any

from openai import OpenAI
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

    resume_text = _chat_completion(resume_prompt, temperature=0.3)
    cover_letter = _chat_completion(cover_prompt, temperature=0.25)

    return {
        "resume_text": resume_text,
        "cover_letter": cover_letter
    }
