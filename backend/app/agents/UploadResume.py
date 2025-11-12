import os
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import PyPDF2
from docx import Document
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ResumeParser:
    """Parse uploaded resumes and convert to UserProfile JSON"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("ResumeParser initialized successfully")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF resume"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return ""
    
    def extract_text_from_docx(self, docx_path: str) -> str:
        """Extract text from DOCX resume"""
        try:
            doc = Document(docx_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            return ""
    
    def extract_text_from_txt(self, txt_path: str) -> str:
        """Extract text from TXT resume"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error reading TXT: {e}")
            return ""
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from any supported file format"""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            return self.extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            return self.extract_text_from_txt(file_path)
        else:
            print(f"Unsupported file format: {file_extension}")
            return ""
    
    def parse_resume_with_ai(self, resume_text: str) -> Dict:
        """Use OpenAI to parse resume text into structured JSON"""
        
        parsing_prompt = f"""
        Parse this resume text and extract information into a structured JSON format. 
        Be precise and only extract information that is explicitly mentioned.
        
        RESUME TEXT:
        {resume_text}
        
        Return a JSON object with this exact structure:
        {{
            "name": "Full Name",
            "email": "email@example.com",
            "phone": "phone number",
            "location": "City, State/Country",
            "linkedin_url": "LinkedIn URL if mentioned",
            "github_url": "GitHub URL if mentioned", 
            "portfolio_url": "Portfolio URL if mentioned",
            "title": "Current or desired job title",
            "years_experience": number_of_years_as_integer,
            "summary": "Professional summary or objective",
            "technical_skills": ["skill1", "skill2", "skill3"],
            "frameworks": ["framework1", "framework2"],
            "tools": ["tool1", "tool2"],
            "soft_skills": ["communication", "leadership"],
            "languages": ["English", "Spanish"],
            "work_experience": [
                {{
                    "title": "Job Title",
                    "company": "Company Name",
                    "start_date": "Month Year",
                    "end_date": "Month Year or Present",
                    "location": "City, State",
                    "description": "Job description and achievements",
                    "skills": ["relevant", "skills", "used"]
                }}
            ],
            "education": [
                {{
                    "degree": "Degree Name",
                    "institution": "University Name", 
                    "graduation_date": "Year",
                    "location": "City, State",
                    "gpa": "GPA if mentioned"
                }}
            ],
            "projects": [
                {{
                    "name": "Project Name",
                    "duration": "Timeline",
                    "description": "Project description",
                    "technologies": ["tech1", "tech2"],
                    "url": "Project URL if available"
                }}
            ],
            "certifications": [
                {{
                    "name": "Certification Name",
                    "issuer": "Issuing Organization",
                    "date": "Date received",
                    "expiry": "Expiry date if applicable"
                }}
            ]
        }}
        
        IMPORTANT:
        - If information is not available, use empty string "" or empty array []
        - For years_experience, calculate from work history or use 0 if unclear
        - Extract ALL technical skills, frameworks, and tools mentioned
        - Be consistent with date formats
        - Only include information that is explicitly stated
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional resume parser. Extract information accurately and return valid JSON."},
                    {"role": "user", "content": parsing_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse the JSON response
            parsed_data = json.loads(response.choices[0].message.content)
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return self._create_empty_profile()
        except Exception as e:
            print(f"AI parsing error: {e}")
            return self._create_empty_profile()
    
    def _create_empty_profile(self) -> Dict:
        """Create empty profile template"""
        return {
            "name": "",
            "email": "", 
            "phone": "",
            "location": "",
            "linkedin_url": "",
            "github_url": "",
            "portfolio_url": "",
            "title": "",
            "years_experience": 0,
            "summary": "",
            "technical_skills": [],
            "frameworks": [],
            "tools": [],
            "soft_skills": [],
            "languages": [],
            "work_experience": [],
            "education": [],
            "projects": [],
            "certifications": []
        }
    
    def parse_resume_fallback(self, resume_text: str) -> Dict:
        """Fallback parsing using regex patterns (no AI)"""
        profile = self._create_empty_profile()
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, resume_text)
        if email_match:
            profile["email"] = email_match.group()
        
        # Extract phone
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, resume_text)
        if phone_match:
            profile["phone"] = phone_match.group()
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, resume_text)
        if linkedin_match:
            profile["linkedin_url"] = f"https://{linkedin_match.group()}"
        
        # Extract GitHub
        github_pattern = r'github\.com/[\w-]+'
        github_match = re.search(github_pattern, resume_text)
        if github_match:
            profile["github_url"] = f"https://{github_match.group()}"
        
        # Extract name (first line or lines before email)
        lines = resume_text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line.split()) <= 4 and not any(char in line for char in ['@', '(', ')', '+', 'www']):
                profile["name"] = line
                break
        
        # Basic skill extraction
        skill_keywords = ['python', 'javascript', 'java', 'react', 'node', 'sql', 'aws', 'docker', 'git']
        found_skills = []
        text_lower = resume_text.lower()
        
        for skill in skill_keywords:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        profile["technical_skills"] = found_skills
        
        return profile
    
    def process_resume_upload(self, file_path: str, use_ai: bool = True) -> Dict:
        """Complete resume processing pipeline"""
        
        print(f"Processing resume: {os.path.basename(file_path)}")
        
        # Extract text
        resume_text = self.extract_text_from_file(file_path)
        
        if not resume_text:
            return {"error": "Could not extract text from resume"}
        
        print(f"Extracted {len(resume_text)} characters of text")
        
        # Parse with AI or fallback
        if use_ai:
            try:
                print("Parsing resume with AI...")
                parsed_profile = self.parse_resume_with_ai(resume_text)
            except Exception as e:
                print(f"AI parsing failed: {e}")
                print("Using fallback parser...")
                parsed_profile = self.parse_resume_fallback(resume_text)
        else:
            print("Using fallback parser...")
            parsed_profile = self.parse_resume_fallback(resume_text)
        
        # Add metadata
        parsed_profile["_metadata"] = {
            "source_file": os.path.basename(file_path),
            "processed_at": datetime.now().isoformat(),
            "text_length": len(resume_text),
            "parsing_method": "ai" if use_ai else "fallback"
        }
        
        return parsed_profile
    
    def save_profile_json(self, profile_data: Dict, output_path: str = "user_profile.json"):
        """Save parsed profile to JSON file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(profile_data, f, indent=2)
            print(f"Profile saved successfully to: {output_path}")
            return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False
    
    def validate_profile_data(self, profile_data: Dict) -> List[str]:
        """Validate parsed profile data and return list of issues"""
        issues = []
        
        # Check required fields
        required_fields = ["name", "email"]
        for field in required_fields:
            if not profile_data.get(field):
                issues.append(f"Missing required field: {field}")
        
        # Validate email format
        email = profile_data.get("email", "")
        if email and not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
            issues.append("Invalid email format")
        
        # Check years of experience
        years_exp = profile_data.get("years_experience", 0)
        if not isinstance(years_exp, int) or years_exp < 0 or years_exp > 50:
            issues.append("Invalid years of experience")
        
        # Check if arrays are actually arrays
        array_fields = ["technical_skills", "frameworks", "tools", "work_experience", "education"]
        for field in array_fields:
            if not isinstance(profile_data.get(field, []), list):
                issues.append(f"{field} should be an array")
        
        return issues

# Interactive resume uploader
def interactive_resume_uploader():
    """Interactive interface for uploading and parsing resumes"""
    
    print("Resume Upload & Parser")
    print("=" * 50)
    print("Supported formats: PDF, DOCX, TXT")
    print("=" * 50)
    
    parser = ResumeParser()
    
    while True:
        print("\nAvailable Options:")
        print("1. Upload and parse resume file")
        print("2. View/edit existing profile") 
        print("3. Test with sample resume text")
        print("4. Validate existing profile")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            # File upload
            file_path = input("\nEnter resume file path: ").strip().strip('"\'')
            
            if not os.path.exists(file_path):
                print("Error: File not found. Please check the path.")
                continue
            
            # Check if user wants AI parsing
            use_ai_input = input("\nUse AI parsing? (y/n, default=y): ").strip().lower()
            use_ai = use_ai_input != 'n'
            
            # Process resume
            result = parser.process_resume_upload(file_path, use_ai=use_ai)
            
            if "error" in result:
                print(f"Error: {result['error']}")
                continue
            
            # Validate the parsed data
            issues = parser.validate_profile_data(result)
            if issues:
                print("\nValidation Issues Found:")
                for issue in issues:
                    print(f"  - {issue}")
            
            # Show results summary
            print("\nParsed Profile Summary:")
            print(f"Name: {result.get('name', 'Not found')}")
            print(f"Email: {result.get('email', 'Not found')}")
            print(f"Phone: {result.get('phone', 'Not found')}")
            print(f"Job Title: {result.get('title', 'Not found')}")
            print(f"Years of Experience: {result.get('years_experience', 0)}")
            print(f"Technical Skills: {len(result.get('technical_skills', []))} skills found")
            print(f"Work Experience: {len(result.get('work_experience', []))} positions")
            print(f"Education: {len(result.get('education', []))} entries")
            print(f"Projects: {len(result.get('projects', []))} projects")
            
            # Save option
            save_input = input("\nSave this profile? (y/n): ").strip().lower()
            if save_input == 'y':
                output_name = input("Output filename (default: user_profile.json): ").strip()
                output_name = output_name or "user_profile.json"
                
                if parser.save_profile_json(result, output_name):
                    print(f"\nSuccess! Profile saved. You can now use it with WriterAgent:")
                    print("python3 backend/app/agents/WriterAgent.py")
            
            # View full profile option
            view_full_input = input("\nView complete parsed data? (y/n): ").strip().lower()
            if view_full_input == 'y':
                print("\nComplete Profile Data:")
                print("-" * 50)
                print(json.dumps(result, indent=2))
        
        elif choice == "2":
            # View existing profile
            profile_path = input("\nProfile JSON path (default: user_profile.json): ").strip()
            profile_path = profile_path or "user_profile.json"
            
            if os.path.exists(profile_path):
                try:
                    with open(profile_path, 'r') as f:
                        profile = json.load(f)
                    
                    print(f"\nCurrent Profile from {profile_path}:")
                    print("-" * 50)
                    
                    # Show summary first
                    print(f"Name: {profile.get('name', 'Not set')}")
                    print(f"Email: {profile.get('email', 'Not set')}")
                    print(f"Title: {profile.get('title', 'Not set')}")
                    print(f"Skills: {len(profile.get('technical_skills', []))}")
                    print(f"Experience: {len(profile.get('work_experience', []))}")
                    
                    view_full = input("\nView complete profile data? (y/n): ").strip().lower()
                    if view_full == 'y':
                        print(json.dumps(profile, indent=2))
                    
                    edit_input = input("\nEdit this profile manually? (y/n): ").strip().lower()
                    if edit_input == 'y':
                        print("To edit manually, open the JSON file in a text editor:")
                        print(f"File location: {os.path.abspath(profile_path)}")
                        
                except Exception as e:
                    print(f"Error reading profile: {e}")
            else:
                print("Error: Profile file not found")
        
        elif choice == "3":
            # Test with sample resume text
            sample_resume_text = """
            Jane Smith
            Senior Software Engineer
            jane.smith@email.com | (555) 987-6543 | Seattle, WA
            LinkedIn: linkedin.com/in/janesmith | GitHub: github.com/janesmith
            
            PROFESSIONAL SUMMARY
            Experienced full-stack software engineer with 7+ years developing scalable web applications 
            using modern technologies including React, Python, and cloud services.
            
            TECHNICAL SKILLS
            Languages: Python, JavaScript, TypeScript, SQL, HTML/CSS
            Frameworks: React, Django, Flask, Node.js, Express
            Tools: Git, Docker, Kubernetes, AWS, PostgreSQL, MongoDB
            
            WORK EXPERIENCE
            Senior Software Engineer | TechCorp Inc | Jan 2021 - Present
            Seattle, WA
            - Lead development of microservices architecture serving 1M+ users
            - Improved application performance by 60% through optimization
            - Mentor junior developers and conduct code reviews
            Skills: Python, React, AWS, Kubernetes, PostgreSQL
            
            Software Engineer | WebStart Solutions | Jun 2018 - Dec 2020
            Portland, OR
            - Developed full-stack web applications using Django and React
            - Implemented CI/CD pipelines reducing deployment time by 50%
            - Collaborated with cross-functional teams in Agile environment
            Skills: Python, Django, React, Docker, PostgreSQL
            
            EDUCATION
            Bachelor of Science in Computer Science | University of Washington | 2018
            Seattle, WA
            GPA: 3.7
            
            PROJECTS
            E-commerce Platform | 2023
            Built a full-featured e-commerce platform with payment integration
            Technologies: React, Node.js, MongoDB, Stripe API
            GitHub: github.com/janesmith/ecommerce-platform
            """
            
            print("\nTesting with sample resume text...")
            print("Sample resume length:", len(sample_resume_text), "characters")
            
            use_ai_sample = input("\nUse AI parsing for sample? (y/n, default=y): ").strip().lower()
            use_ai = use_ai_sample != 'n'
            
            if use_ai:
                result = parser.parse_resume_with_ai(sample_resume_text)
            else:
                result = parser.parse_resume_fallback(sample_resume_text)
            
            print("\nSample Parse Results:")
            print("-" * 30)
            print(json.dumps(result, indent=2))
        
        elif choice == "4":
            # Validate existing profile
            profile_path = input("\nProfile JSON path to validate (default: user_profile.json): ").strip()
            profile_path = profile_path or "user_profile.json"
            
            if os.path.exists(profile_path):
                try:
                    with open(profile_path, 'r') as f:
                        profile = json.load(f)
                    
                    issues = parser.validate_profile_data(profile)
                    
                    if issues:
                        print(f"\nValidation Issues Found ({len(issues)}):")
                        for i, issue in enumerate(issues, 1):
                            print(f"{i}. {issue}")
                    else:
                        print("\nProfile validation passed! No issues found.")
                        
                except Exception as e:
                    print(f"Error validating profile: {e}")
            else:
                print("Error: Profile file not found")
        
        elif choice == "5":
            print("\nThank you for using the Resume Parser!")
            break
        
        else:
            print("Invalid choice. Please select 1-5.")

# Command line usage
if __name__ == "__main__":
    interactive_resume_uploader()