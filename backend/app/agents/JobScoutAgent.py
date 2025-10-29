# JobScout Agent: queries sources and yields normalized postings
class JobScoutAgent:
    def fetch_indeed(self, plan: dict) -> list:
        # TODO: Replace with real Indeed query
        return [{
            "source": "indeed", "job_id": "EXAMPLE-1",
            "title": "Software Engineer", "company":"Acme Inc.",
            "description": "Build backend services in FastAPI."
        }]
