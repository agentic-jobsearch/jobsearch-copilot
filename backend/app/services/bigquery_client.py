import os
from google.cloud import bigquery


class BigQueryClient:
    """Thin wrapper around BigQuery for fetching job listings."""

    def __init__(self):
        project = os.getenv("GOOGLE_PROJECT_ID")
        if not project:
            raise ValueError("GOOGLE_PROJECT_ID environment variable not set")

        self.client = bigquery.Client(project=project)

    def fetch_recent_jobs(self, limit: int = 20):
        """
        Returns the most recent job listings from BigQuery.
        Expected table schema:
            job_listings(title STRING, company STRING, location STRING,
                         url STRING, description STRING, created_at TIMESTAMP)
        """
        query = """
        SELECT
            title,
            company,
            location,
            url,
            description,
            created_at
        FROM `agentic-jobsearch.job_data.job_listings`
        ORDER BY created_at DESC
        LIMIT @limit
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("limit", "INT64", limit)
            ]
        )

        rows = self.client.query(query, job_config=job_config).result()

        return [dict(row) for row in rows]
