import os
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import PyPDF2
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv
from app.core.env import require_env

load_dotenv()

# FIX: load required key at module level
OPENAI_API_KEY = require_env("OPENAI_API_KEY")


class ResumeParser:
    """Parse uploaded resumes and convert to UserProfile JSON"""

    def __init__(self):
        # FIX: use the validated key
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("ResumeParser initialized successfully")


    # -------------------------
    # FILE EXTRACTION
    # -------------------------
    def _extract_pdf(self, path: str) -> str:
        try:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        except (FileNotFoundError, PermissionError, PyPDF2.errors.PdfReadError, Exception) as e:
            print(f"Error extracting PDF: {e}")
            return ""

    def _extract_docx(self, path: str) -> str:
        try:
            doc = Document(path)
            return "\n".join(p.text for p in doc.paragraphs).strip()
        except (FileNotFoundError, PermissionError, Exception) as e:
            print(f"Error extracting DOCX: {e}")
            return ""

    def _extract_txt(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except (FileNotFoundError, PermissionError, UnicodeDecodeError, Exception) as e:
            print(f"Error extracting TXT: {e}")
            return ""

    def extract_text(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            return self._extract_pdf(path)
        if ext == ".docx":
            return self._extract_docx(path)
        if ext == ".txt":
            return self._extract_txt(path)
        return ""

    # -------------------------
    # AI PARSING
    # -------------------------
    def parse_with_ai(self, text: str) -> Dict:
        """
        Converts resume text → clean user profile JSON.
        Schema is intentionally small & useful for downstream agents.
        """

        prompt = f"""
        Extract structured resume information from the text below.

        Keep ONLY factual information explicitly present.

        Return JSON in this exact structure:

        {{
            "name": "",
            "email": "",
            "phone": "",
            "location": "",
            "title": "",
            "years_experience": 0,
            "skills": [],
            "education": [],
            "work_experience": [],
            "links": {{
                "linkedin": "",
                "github": "",
                "portfolio": ""
            }}
        }}

        RULES:
        - If missing, leave empty or 0.
        - years_experience must be an integer.
        - skills should be simple strings.
        - education and work_experience must be arrays of objects.

        RESUME:
        {text}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You extract structured info from resumes. Respond ONLY in JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2
            )

            raw = response.choices[0].message.content.strip()

            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"raw": raw, "error": "Invalid JSON from model"}

        except Exception as e:
            return {"error": str(e)}

    # -------------------------
    # HIGH-LEVEL METHOD
    # -------------------------
    def process(self, path: str) -> Dict:
        """
        Full pipeline:
        - Extract text
        - AI parse
        - Add metadata
        """

        text = self.extract_text(path)
        if not text:
            return {"error": f"Could not extract text from {path}"}

        parsed = self.parse_with_ai(text)

        parsed["_metadata"] = {
            "source_file": os.path.basename(path),
            "processed_at": datetime.now().isoformat(),
            "text_length": len(text),
        }

        return parsed
