# Writer Agent: generates tailored resume/cover letters
class WriterAgent:
    def cover_letter(self, resume: str, job: dict) -> str:
        return f"Dear {job.get('company','Hiring Team')}, I am a strong fit for {job.get('title')}..."
