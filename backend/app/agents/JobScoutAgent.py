import os
import json
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()


class JobScoutAgent:
    """
    Hybrid Job Search Agent:
    - Queries BigQuery job listings
    - Applies AI search & reasoning
    - Merges, enriches, and re-ranks results
    """

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.bq = bigquery.Client()
        print("JobScoutAgent initialized with BigQuery + AI search")

    # ---------------------------------------------------------------------
    # 1. BIGQUERY SEARCH
    # ---------------------------------------------------------------------
    def search_bigquery(self, query: str) -> List[Dict]:
        """
        Run SQL over your BigQuery dataset.
        You can tune column names to match your schema.
        """

        sql = f"""
        SELECT 
            job_id,
            title,
            company,
            location,
            description,
            url,
            detected_role,
            detected_level
        FROM `agentic-jobsearch.jobs.jobs_table`
        WHERE LOWER(title) LIKE '%{query.lower()}%'
           OR LOWER(description) LIKE '%{query.lower()}%'
        LIMIT 20;
        """

        try:
            rows = list(self.bq.query(sql).result())
        except Exception as e:
            print("BigQuery error:", e)
            return []

        jobs = []
        for row in rows:
            jobs.append({
                "title": row.title,
                "company": row.company,
                "location": row.location,
                "seniority": row.detected_level or "",
                "description": row.description,
                "url": row.url,
                "why_match": "Matched via BigQuery search",
                "score": 60  # base score, will re-rank later
            })

        return jobs

    # ---------------------------------------------------------------------
    # 2. AI JOB SEARCH (for expansion)
    # ---------------------------------------------------------------------
    def search_ai(self, query: str, profile: Dict) -> List[Dict]:
        prompt = f"""
        You are an AI job search engine.

        The user is looking for: "{query}"
        Their profile: {profile}

        Return 5 realistic jobs (US-based) in JSON array only.
        Format:
        {{
            "title": "",
            "company": "",
            "location": "",
            "seniority": "",
            "description": "",
            "why_match": "",
            "score": 0
        }}
        """

        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800
        )

        raw = resp.choices[0].message.content.strip()
        try:
            return json.loads(raw)
        except:
            return []

    # ---------------------------------------------------------------------
    # 3. MERGE + RE-RANK
    # ---------------------------------------------------------------------
    def merge_and_rank(self, bq_jobs: List[Dict], ai_jobs: List[Dict], profile: Dict):
        all_jobs = bq_jobs + ai_jobs

        # Example: simple score boost based on profile skills
        skills = set(x.lower() for x in (profile.get("technical_skills") or []))

        for job in all_jobs:
            desc = job["description"].lower()
            match_count = sum(1 for s in skills if s in desc)
            job["score"] += min(match_count * 5, 20)  # skill-based boost

        # Highest score first
        return sorted(all_jobs, key=lambda j: j["score"], reverse=True)[:10]

    # ---------------------------------------------------------------------
    # MAIN METHOD CALLED BY PlannerAgent
    # ---------------------------------------------------------------------
    def search(self, query: str, profile: Dict) -> List[Dict]:
        bq_results = self.search_bigquery(query)
        ai_results = self.search_ai(query, profile)
        merged = self.merge_and_rank(bq_results, ai_results, profile or {})
        return merged
