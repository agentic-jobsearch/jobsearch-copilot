import os
from typing import Iterable, List

from google.cloud import bigquery
from google.oauth2 import service_account


def get_bq_client() -> bigquery.Client:
    """
    Initializes a BigQuery client using GOOGLE_APPLICATION_CREDENTIALS.
    """
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise RuntimeError("Missing GOOGLE_APPLICATION_CREDENTIALS")

    project_id = os.getenv("GOOGLE_PROJECT_ID")
    if not project_id:
        raise RuntimeError("Missing GOOGLE_PROJECT_ID")

    credentials = service_account.Credentials.from_service_account_file(
        credentials_path
    )

    return bigquery.Client(credentials=credentials, project=project_id)


def _normalize_terms(terms: Iterable[str]) -> List[str]:
    normalized = []
    seen = set()
    for term in terms or []:
        if not term:
            continue
        cleaned = (
            term.replace("'", "''")
            .strip()
        )
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        normalized.append(cleaned)
    return normalized


def search_jobs(terms: Iterable[str], limit: int = 10):
    """
    Performs a keyword search across job_details using multiple terms combined with OR.
    """

    normalized_terms = _normalize_terms(terms)
    if not normalized_terms:
        return []

    client = get_bq_client()

    conditions = []
    for term in normalized_terms:
        like_clause = f"%{term}%"
        conditions.append(
            f"""(
                LOWER(job_title) LIKE LOWER('{like_clause}') OR
                LOWER(description) LIKE LOWER('{like_clause}') OR
                LOWER(skills) LIKE LOWER('{like_clause}')
            )"""
        )

    where_clause = " OR ".join(conditions)

    sql = f"""
    SELECT
        job_id,
        job_title,
        company_urn,
        job_url,
        description,
        skills,
        location,
        posted_at,
        applicant_count
    FROM `agentic-jobsearch.job_search.job_details`
    WHERE {where_clause}
    ORDER BY posted_at DESC
    LIMIT {limit}
    """

    results = client.query(sql).result()
    return [dict(row) for row in results]


def get_company_info(company_urn: str):
    """
    Fetch company name + URL from company table.
    """

    client = get_bq_client()

    sql = f"""
    SELECT company, company_url
    FROM `agentic-jobsearch.job_search.company`
    WHERE company_urn = '{company_urn}'
    LIMIT 1
    """

    rows = [dict(r) for r in client.query(sql).result()]
    return rows[0] if rows else None
