import os
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

from dotenv import load_dotenv
from openai import OpenAI

from dataIngestion.BigQuerySearch import search_jobs, get_company_info

load_dotenv()

STOPWORDS = {
    "find",
    "me",
    "job",
    "jobs",
    "a",
    "an",
    "the",
    "and",
    "in",
    "for",
    "to",
    "with",
    "role",
    "position",
    "some",
    "of",
    "my",
    "about",
    "can",
    "you",
    "tell",
    "what",
    "are",
    "is",
    "on",
    "help",
}


@dataclass
class WorkflowTask:
    task_id: str
    description: str
    task_type: str
    status: str = "pending"
    output: Optional[Dict[str, Any]] = None


@dataclass
class WorkflowPlan:
    plan_id: str
    user_goal: str
    tasks: List[WorkflowTask]
    estimated_completion: datetime
    plan_details: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class PlannerAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("PlannerAgent initialized")
        self.active_workflows: Dict[str, WorkflowPlan] = {}

    def _normalize_terms(self, values: Optional[List[str]]) -> List[str]:
        terms: List[str] = []
        for value in values or []:
            if not isinstance(value, str):
                continue
            token = value.strip().lower()
            if token:
                terms.append(token)
        return terms

    def _score_job(self, profile: Optional[Dict[str, Any]], job: Dict[str, Any]) -> Dict[str, Any]:
        if not profile:
            return {"score": 0.0, "matched_skills": []}

        profile_skills = set(self._normalize_terms(profile.get("skills")))
        if isinstance(profile.get("custom_skills"), list):
            profile_skills.update(self._normalize_terms(profile["custom_skills"]))

        job_skill_terms: List[str] = []
        job_skills = job.get("skills")
        if isinstance(job_skills, list):
            job_skill_terms = self._normalize_terms(job_skills)
        elif isinstance(job_skills, str):
            job_skill_terms = self._normalize_terms(re.split(r"[;,/\n]", job_skills))

        matched_skills = []
        job_desc = (job.get("description") or "").lower()
        for skill in profile_skills:
            if skill in job_skill_terms or (skill and skill in job_desc):
                matched_skills.append(skill)

        skill_score = 0.0
        if profile_skills:
            skill_score = (len(matched_skills) / len(profile_skills)) * 70.0

        # Location bonus
        location_score = 0.0
        profile_location = (profile.get("location") or "").lower()
        job_location = (job.get("location") or "").lower()
        if profile_location and job_location and profile_location.split(",")[0] in job_location:
            location_score = 10.0

        # Title alignment bonus
        title_score = 0.0
        profile_title = (profile.get("title") or "").lower()
        job_title = (job.get("job_title") or job.get("title") or "").lower()
        if profile_title and job_title and any(token in job_title for token in profile_title.split()):
            title_score = 20.0

        final_score = min(100.0, round(skill_score + location_score + title_score, 1))
        return {
            "score": final_score,
            "matched_skills": matched_skills,
        }

    def _build_profile_insights(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(profile, dict):
            return {}

        insights: Dict[str, Any] = {}

        title = profile.get("title")
        years = profile.get("years_experience")
        location = profile.get("location")

        if title:
            headline = title
            try:
                years_int = int(float(years))
                if years_int > 0:
                    headline = f"{title} with {years_int}+ years of experience"
            except (TypeError, ValueError):
                pass
            if location:
                headline = f"{headline} based in {location}"
            insights["headline"] = headline

        skills = profile.get("skills") or []
        if isinstance(skills, list) and skills:
            insights["skills"] = skills[:12]

        work_history = profile.get("work_experience") or []
        if isinstance(work_history, list) and work_history:
            latest = work_history[0]
            role = latest.get("title") or latest.get("position")
            company = latest.get("company") or latest.get("organization")
            timeframe = latest.get("dates") or latest.get("duration")
            recent_role = role or "Experience"
            if company:
                recent_role = f"{recent_role} at {company}"
            if timeframe:
                recent_role = f"{recent_role} ({timeframe})"
            insights["recent_role"] = recent_role

        education = profile.get("education") or []
        if isinstance(education, list) and education:
            school = education[0].get("school") or education[0].get("institution")
            degree = education[0].get("degree")
            if school or degree:
                insights["education"] = f"{degree or ''} {('at ' + school) if school else ''}".strip()

        return insights

    def _build_search_terms(self, message: str, profile: Optional[Dict[str, Any]]) -> List[str]:
        terms: List[str] = []

        tokens = re.findall(r"[a-zA-Z0-9]+", (message or ""))
        for token in tokens:
            lower = token.lower()
            if lower in STOPWORDS or len(lower) < 3:
                continue
            terms.append(lower)

        if isinstance(profile, dict):
            title = profile.get("title")
            if title:
                terms.append(title)
            skills = profile.get("skills") or []
            if isinstance(skills, list):
                terms.extend(skills[:5])
            location = profile.get("location")
            if location:
                terms.append(location)

        ordered: List[str] = []
        seen = set()
        for term in terms:
            normalized = term.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            ordered.append(term)

        return ordered or [message]

    def plan(self, message: str, profile=None, language: str = "en"):

        profile = profile or {}

        prompt = f"""
        You are a job-search copilot.

        User message:
        "{message}"

        User profile:
        {json.dumps(profile, indent=2)}

        Your job:
        1. Determine the user's main goal
        2. Provide concrete actions
        3. Suggest next steps
        4. Use short JSON output

        JSON format:
        {{
            "goal": "...",
            "confidence": "...",
            "actions": [...],
            "job_recommendations": [],
            "notes": "..."
        }}
        """

        # Generate plan using GPT
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a structured planning assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        content = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(content)
        except:
            parsed = {"text": content}

        message_lower = message.lower()

        profile_insights = self._build_profile_insights(profile)
        if profile_insights:
            parsed["profile_insights"] = profile_insights

        profile_question = bool(
            profile
            and any(
                keyword in message_lower
                for keyword in ["resume", "skill", "experience", "background", "profile", "strength"]
            )
        )

        if profile_question and profile_insights:
            parsed["insight_summary"] = {
                "skills": profile_insights.get("skills", []),
                "recent_role": profile_insights.get("recent_role"),
            }

        # Determine whether to search BigQuery
        should_search = any(
            keyword in message_lower
            for keyword in ["job", "apply", "role", "opening", "position",
                            "engineer", "developer", "intern", "find me", "opportunity"]
        )

        parsed["searched_bigquery"] = should_search

        if should_search:
            search_terms = self._build_search_terms(message, profile)
            jobs = search_jobs(search_terms, limit=25)

            for job in jobs:
                comp = get_company_info(job["company_urn"])
                if comp:
                    job["company"] = comp["company"]
                    job["company_url"] = comp["company_url"]
                score_details = self._score_job(profile, job)
                job["match_score"] = score_details.get("score", 0.0)
                job["matched_skills"] = score_details.get("matched_skills", [])

            parsed["bigquery_jobs"] = jobs

        return {"ok": True, "plan": parsed}

    # ------------------------------------------------------------------
    # Workflow helpers for FastAPI routes
    # ------------------------------------------------------------------
    def create_workflow_plan(self, user_message: str, user_data: Optional[Dict[str, Any]] = None) -> WorkflowPlan:
        user_data = user_data or {}
        language = user_data.get("language", "en")
        profile = user_data.get("profile")

        plan_response = self.plan(user_message, profile=profile, language=language)
        plan_details = plan_response.get("plan", {})

        plan_id = str(uuid4())
        tasks = [
            WorkflowTask(
                task_id="goal_understanding",
                description="Understand the user's request and craft an action plan.",
                task_type="analysis",
            ),
            WorkflowTask(
                task_id="job_search",
                description="Query BigQuery for matching roles and summarize findings.",
                task_type="job_search",
            ),
        ]

        workflow_plan = WorkflowPlan(
            plan_id=plan_id,
            user_goal=plan_details.get("goal") or user_message,
            tasks=tasks,
            estimated_completion=datetime.utcnow() + timedelta(seconds=30),
            plan_details=plan_details,
        )

        self.active_workflows[plan_id] = workflow_plan
        return workflow_plan

    def execute_workflow(self, plan: WorkflowPlan) -> Dict[str, Any]:
        if plan.status == "completed":
            return self._serialize_plan(plan)

        for task in plan.tasks:
            if task.task_type == "analysis":
                task.status = "completed"
                task.output = {
                    "goal": plan.plan_details.get("goal", plan.user_goal),
                    "actions": plan.plan_details.get("actions", []),
                    "notes": plan.plan_details.get("notes"),
                    "profile_insights": plan.plan_details.get("profile_insights"),
                    "insight_summary": plan.plan_details.get("insight_summary"),
                }
            elif task.task_type == "job_search":
                task.status = "completed"
                task.output = {
                    "top_matches": plan.plan_details.get("bigquery_jobs", []),
                    "searched": plan.plan_details.get("searched_bigquery", False),
                }

        plan.status = "completed"
        plan.completed_at = datetime.utcnow()
        return self._serialize_plan(plan)

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        plan = self.active_workflows.get(workflow_id)
        if not plan:
            return {"status": "not_found", "workflow_id": workflow_id}

        if plan.status != "completed":
            # execute lazily so polling eventually completes
            self.execute_workflow(plan)

        return self._serialize_plan(plan)

    def combine_results(self, workflow_id: str) -> Dict[str, Any]:
        status = self.get_workflow_status(workflow_id)
        return {
            "workflow_id": workflow_id,
            "status": status.get("status"),
            "user_goal": status.get("user_goal"),
            "tasks": status.get("tasks", []),
            "summary": status.get("tasks", [])[0]["output"] if status.get("tasks") else None,
        }

    def _serialize_plan(self, plan: WorkflowPlan) -> Dict[str, Any]:
        return {
            "workflow_id": plan.plan_id,
            "status": plan.status,
            "user_goal": plan.user_goal,
            "estimated_completion": plan.estimated_completion.isoformat(),
            "tasks": [asdict(task) for task in plan.tasks],
            "completed_at": plan.completed_at.isoformat() if plan.completed_at else None,
        }
