# Planner Agent: creates search plan + constraints
class PlannerAgent:
    def plan(self, resume_skills: list, preferences: dict) -> dict:
        return {
            "keywords": preferences.get("keywords", ["software engineer"]),
            "locations": preferences.get("locations", ["remote"]),
            "constraints": {"salary_min": preferences.get("salary_min", None)}
        }
