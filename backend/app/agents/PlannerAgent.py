import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class PlannerAgent:
    """
    Simplified PlannerAgent:
    - Interprets the user's message
    - Generates a structured plan (goal + steps)
    - No workflow engine
    - No dependencies
    - One OpenAI call
    """

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("Simplified PlannerAgent initialized")

    def plan(self, message: str, profile=None, language: str = "en"):
        """
        Main planner function:
        - Understand user intent
        - Propose next actions
        """

        profile = profile or {}

        prompt = f"""
        You are a job-search copilot.

        User message:
        "{message}"

        User profile:
        {json.dumps(profile, indent=2)}

        Your job:
        1. Determine what the user wants ("goal")
        2. Produce 3-6 concrete "actions" you recommend
        3. If useful, include suggested jobs or application tips
        4. Keep responses short, structured, machine-readable

        Respond in this JSON format:

        {{
            "goal": "string — the user's intent",
            "confidence": "low|medium|high",
            "actions": [
                "step 1",
                "step 2",
                "step 3"
            ],
            "job_recommendations": [
                {{
                    "title": "Role",
                    "company": "Company",
                    "reason": "Why it fits the user"
                }}
            ],
            "notes": "optional extra helpful info"
        }}
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

            content = response.choices[0].message.content.strip()

            # Try parsing JSON — if GPT returns text, wrap it
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                parsed = {"text": content}

            return {
                "ok": True,
                "plan": parsed
            }

        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "fallback_plan": {
                    "goal": message,
                    "confidence": "low",
                    "actions": ["Try rephrasing your request."],
                }
            }
