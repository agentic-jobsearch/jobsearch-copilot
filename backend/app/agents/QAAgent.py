# QA Agent: reflection pass over generated artifacts
class QAAgent:
    def review(self, cover_letter: str) -> dict:
        ok = "I am" in cover_letter
        return {"quality_ok": ok, "notes": "Add quantifiable impact if available."}
