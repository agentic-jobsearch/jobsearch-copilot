import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from app.core.env import require_env

# Load the required environment variable (NO "self" here)
OPENAI_API_KEY = require_env("OPENAI_API_KEY")


class PlannerAgent:
    """Simplified PlannerAgent"""

    def __init__(self):
        # This now works correctly
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        print("Simplified PlannerAgent initialized")

    def plan(self, message: str, profile=None, language: str = "en"):
        profile = profile or {}

        prompt = f"""
        You are a job-search copilot.

        User message:
        "{message}"

        User profile:
        {json.dumps(profile, indent=2)}

        Your job:
        1. Determine the user's goal
        2. Produce 3–6 concrete actions
        3. Optionally recommend relevant jobs
        4. Respond with a structured JSON object
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a structured planning assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
            )

            raw = response.choices[0].message.content.strip()

            try:
                data = json.loads(raw)
            except:
                data = {"text": raw}

            return {"ok": True, "plan": data}

        except Exception as e:
            return {"ok": False, "error": str(e)}
