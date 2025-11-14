import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
from openai import OpenAI
from dataclasses import dataclass
from datetime import datetime
from app.core.env import require_env

OPENAI_KEY = require_env("OPENAI_API_KEY")
self.client = OpenAI(api_key=OPENAI_KEY)


@dataclass
class UserProfile:
    """User's genuine profile information"""
    # Personal Information
    name: str
    email: str
    phone: str
    location: str
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""
    
    # Professional Summary
    title: str = ""
    years_experience: int = 0
    summary: str = ""
    
    # Skills (categorized for better organization)
    technical_skills: List[str] = None
    soft_skills: List[str] = None
    languages: List[str] = None
    frameworks: List[str] = None
    tools: List[str] = None
    
    # Experience
    work_experience: List[Dict] = None
    
    # Education
    education: List[Dict] = None
    
    # Projects
    projects: List[Dict] = None
    
    # Certifications
    certifications: List[Dict] = None
    
    def __post_init__(self):
        # Initialize empty lists if None
        if self.technical_skills is None:
            self.technical_skills = []
        if self.soft_skills is None:
            self.soft_skills = []
        if self.languages is None:
            self.languages = []
        if self.frameworks is None:
            self.frameworks = []
        if self.tools is None:
            self.tools = []
        if self.work_experience is None:
            self.work_experience = []
        if self.education is None:
            self.education = []
        if self.projects is None:
            self.projects = []
        if self.certifications is None:
            self.certifications = []
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'UserProfile':
        """Load user profile from JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return cls(**data)
        except Exception as e:
            print(f"Error loading profile: {e}")
            return cls.create_sample_profile()
    
    @classmethod
    def create_sample_profile(cls) -> 'UserProfile':
        """Create a sample profile for testing"""
        return cls(
            name="Your Name",
            email="your.email@example.com", 
            phone="+1 (555) 123-4567",
            location="San Francisco, CA",
            linkedin_url="https://linkedin.com/in/yourname",
            github_url="https://github.com/yourname",
            title="Software Engineer",
            years_experience=3,
            summary="Experienced software engineer passionate about building scalable applications.",
            technical_skills=["Python", "JavaScript", "SQL"],
            frameworks=["React", "Django", "Flask"],
            tools=["Git", "Docker", "AWS"],
            soft_skills=["Problem Solving", "Team Collaboration"]
        )
    
    def save_to_file(self, file_path: str):
        """Save profile to JSON file"""
        try:
            # Convert to dictionary
            profile_dict = {
                'name': self.name,
                'email': self.email,
                'phone': self.phone,
                'location': self.location,
                'linkedin_url': self.linkedin_url,
                'github_url': self.github_url,
                'portfolio_url': self.portfolio_url,
                'title': self.title,
                'years_experience': self.years_experience,
                'summary': self.summary,
                'technical_skills': self.technical_skills,
                'soft_skills': self.soft_skills,
                'languages': self.languages,
                'frameworks': self.frameworks,
                'tools': self.tools,
                'work_experience': self.work_experience,
                'education': self.education,
                'projects': self.projects,
                'certifications': self.certifications
            }
            
            with open(file_path, 'w') as f:
                json.dump(profile_dict, f, indent=2)
            print(f"Profile saved to {file_path}")
            
        except Exception as e:
            print(f"Error saving profile: {e}")

class WriterAgent:
    def __init__(self, profile_path: str = "user_profile.json"):
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize BigQuery client for job data
        self.bigquery_client = self._init_bigquery_client()
        
        # Load user profile
        self.profile_path = profile_path
        self.user_profile = self._load_user_profile()
        
        print("WriterAgent initialized successfully")
        print(f"Loaded profile for: {self.user_profile.name}")
    
    def _init_bigquery_client(self) -> bigquery.Client:
        """Initialize BigQuery client"""
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            return bigquery.Client(credentials=credentials, project='agentic-jobsearch')
        else:
            return bigquery.Client(project='agentic-jobsearch')
    
    def _load_user_profile(self) -> UserProfile:
        """Load user profile from file or create sample"""
        if os.path.exists(self.profile_path):
            return UserProfile.load_from_file(self.profile_path)
        else:
            print(f"Profile file not found at {self.profile_path}")
            print("Creating sample profile - please update with your information")
            profile = UserProfile.create_sample_profile()
            profile.save_to_file(self.profile_path)
            return profile
    
    def load_profile_from_uploaded_resume(self, json_path: str):
        """Load user profile from uploaded resume JSON"""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Remove metadata if present
            if '_metadata' in data:
                del data['_metadata']
            
            self.user_profile = UserProfile(**data)
            print(f"Successfully loaded profile for: {self.user_profile.name}")
            
        except Exception as e:
            print(f"Error loading profile from uploaded resume: {e}")
            print("Using default sample profile")
            self.user_profile = UserProfile.create_sample_profile()
    
    def update_profile_interactive(self):
        """Interactive profile update"""
        print("Profile Information Update")
        print("Press Enter to keep current value, or type new value")
        print("-" * 50)
        
        # Personal Information
        self.user_profile.name = input(f"Name ({self.user_profile.name}): ").strip() or self.user_profile.name
        self.user_profile.email = input(f"Email ({self.user_profile.email}): ").strip() or self.user_profile.email
        self.user_profile.phone = input(f"Phone ({self.user_profile.phone}): ").strip() or self.user_profile.phone
        self.user_profile.location = input(f"Location ({self.user_profile.location}): ").strip() or self.user_profile.location
        
        # Professional Info
        self.user_profile.title = input(f"Job Title ({self.user_profile.title}): ").strip() or self.user_profile.title
        years_exp = input(f"Years Experience ({self.user_profile.years_experience}): ").strip()
        if years_exp:
            try:
                self.user_profile.years_experience = int(years_exp)
            except ValueError:
                print("Invalid number, keeping current value")
        
        # Skills
        tech_skills = input(f"Technical Skills (comma-separated): ").strip()
        if tech_skills:
            self.user_profile.technical_skills = [skill.strip() for skill in tech_skills.split(',')]
        
        frameworks = input(f"Frameworks (comma-separated): ").strip()
        if frameworks:
            self.user_profile.frameworks = [skill.strip() for skill in frameworks.split(',')]
        
        # Save updated profile
        self.user_profile.save_to_file(self.profile_path)
        print("Profile updated successfully")
    
    def get_job_details(self, job_id: str) -> Optional[Dict]:
        """Fetch specific job details from BigQuery"""
        query = """
        SELECT 
            jd.job_id,
            jd.job_title,
            c.company,
            jd.location,
            jd.work_type,
            jd.salary,
            jd.skills,
            jd.description,
            jd.benefits,
            jd.job_url,
            c.company_url
        FROM `agentic-jobsearch.job_search.job_details` jd
        JOIN `agentic-jobsearch.job_search.company` c 
            ON jd.company_urn = c.company_urn
        WHERE jd.job_id = @job_id
        """
        
        try:
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("job_id", "STRING", job_id)
                ]
            )
            
            results = self.bigquery_client.query(query, job_config=job_config)
            
            for row in results:
                return {
                    'job_id': row.job_id,
                    'job_title': row.job_title,
                    'company': row.company,
                    'location': row.location,
                    'work_type': row.work_type,
                    'salary': row.salary,
                    'skills': row.skills,
                    'description': row.description,
                    'benefits': row.benefits,
                    'job_url': row.job_url,
                    'company_url': row.company_url
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching job details: {e}")
            return None
    
    def create_resume_for_job(self, job_id: str) -> Dict:
        """Create resume and cover letter for a specific job ID"""
        
        print(f"Creating application materials for job ID: {job_id}")
        
        # Get job details
        job = self.get_job_details(job_id)
        if not job:
            return {"error": f"Job with ID '{job_id}' not found in database"}
        
        print(f"Found job: {job['job_title']} at {job['company']}")
        
        # Analyze job requirements
        job_analysis = self.analyze_job_requirements(job)
        
        # Find matches between user and job
        matches = self.match_user_to_job(self.user_profile, job_analysis)
        
        print(f"Skill match: {matches['skill_match_percentage']:.1f}%")
        
        # Generate resume
        print("Generating tailored resume...")
        resume = self.generate_tailored_resume(self.user_profile, job)
        
        # Generate cover letter
        print("Generating personalized cover letter...")
        cover_letter = self.generate_cover_letter(self.user_profile, job)
        
        # Save to files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        company_name = job['company'].replace(' ', '_').replace('.', '')
        
        resume_filename = f"resume_{company_name}_{timestamp}.md"
        cover_letter_filename = f"cover_letter_{company_name}_{timestamp}.md"
        
        try:
            # Save resume
            with open(resume_filename, 'w') as f:
                f.write(resume)
            print(f"Resume saved as: {resume_filename}")
            
            # Save cover letter
            with open(cover_letter_filename, 'w') as f:
                f.write(cover_letter)
            print(f"Cover letter saved as: {cover_letter_filename}")
            
        except Exception as e:
            print(f"Could not save files: {e}")
        
        return {
            'job_details': job,
            'resume': resume,
            'cover_letter': cover_letter,
            'match_analysis': {
                'skill_match_percentage': matches['skill_match_percentage'],
                'matching_skills': matches['matching_required_skills'] + matches['matching_preferred_skills'],
                'relevant_experience_count': len(matches.get('relevant_experience', [])),
                'relevant_projects_count': len(matches.get('relevant_projects', []))
            },
            'application_tips': self._generate_application_tips(matches, job_analysis),
            'files_saved': {
                'resume': resume_filename,
                'cover_letter': cover_letter_filename
            },
            'generated_at': datetime.now().isoformat()
        }
    
    def analyze_job_requirements(self, job: Dict) -> Dict:
        """Use AI to analyze job requirements and extract key information"""
        analysis_prompt = f"""
        Analyze this job posting and extract key requirements:
        
        Job Title: {job.get('job_title', '')}
        Company: {job.get('company', '')}
        Description: {job.get('description', '')}
        Skills: {job.get('skills', '')}
        
        Return JSON with:
        {{
            "required_skills": ["must-have skills"],
            "preferred_skills": ["nice-to-have skills"], 
            "experience_level": "entry/mid/senior",
            "key_responsibilities": ["main duties"],
            "technical_requirements": ["specific technologies"]
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error analyzing job: {e}")
            return {"required_skills": [], "preferred_skills": []}
    
    def match_user_to_job(self, user_profile: UserProfile, job_analysis: Dict) -> Dict:
        """Find matching skills between user and job"""
        all_user_skills = (
            user_profile.technical_skills + 
            user_profile.frameworks + 
            user_profile.tools
        )
        
        user_skills_lower = [skill.lower() for skill in all_user_skills]
        
        matching_required = []
        matching_preferred = []
        
        for skill in job_analysis.get('required_skills', []):
            if skill.lower() in user_skills_lower:
                matching_required.append(skill)
        
        for skill in job_analysis.get('preferred_skills', []):
            if skill.lower() in user_skills_lower:
                matching_preferred.append(skill)
        
        total_required = len(job_analysis.get('required_skills', []))
        skill_match_percentage = (len(matching_required) / max(total_required, 1)) * 100
        
        return {
            'matching_required_skills': matching_required,
            'matching_preferred_skills': matching_preferred,
            'skill_match_percentage': skill_match_percentage
        }
    
    def generate_tailored_resume(self, user_profile: UserProfile, job: Dict) -> str:
        """Generate tailored resume using AI"""
        
        resume_prompt = f"""
        Create a professional resume tailored for this job. Use ONLY the genuine information provided.
        
        USER INFORMATION:
        Name: {user_profile.name}
        Title: {user_profile.title}
        Experience: {user_profile.years_experience} years
        Technical Skills: {', '.join(user_profile.technical_skills)}
        Frameworks: {', '.join(user_profile.frameworks)}
        Tools: {', '.join(user_profile.tools)}
        Work Experience: {json.dumps(user_profile.work_experience)}
        Education: {json.dumps(user_profile.education)}
        Projects: {json.dumps(user_profile.projects)}
        
        TARGET JOB:
        Title: {job.get('job_title')}
        Company: {job.get('company')}
        Required Skills: {job.get('skills', '')}
        Description: {job.get('description', '')}
        
        Create a professional resume in markdown format that highlights relevant skills and experience.
        Focus on achievements and quantifiable results where possible.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": resume_prompt}],
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating resume: {e}"
    
    def generate_cover_letter(self, user_profile: UserProfile, job: Dict) -> str:
        """Generate personalized cover letter using AI"""
        
        cover_letter_prompt = f"""
        Write a professional cover letter for this job application using genuine information only.
        
        USER INFORMATION:
        Name: {user_profile.name}
        Title: {user_profile.title} 
        Years of Experience: {user_profile.years_experience}
        Key Skills: {', '.join(user_profile.technical_skills[:5])}
        Summary: {user_profile.summary}
        
        JOB INFORMATION:
        Position: {job.get('job_title')} 
        Company: {job.get('company')}
        Location: {job.get('location')}
        
        Write 3-4 paragraphs highlighting relevant skills and genuine interest in the role.
        Be professional, concise, and persuasive.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo", 
                messages=[{"role": "user", "content": cover_letter_prompt}],
                temperature=0.4
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating cover letter: {e}"
    
    def _generate_application_tips(self, matches: Dict, job_analysis: Dict) -> List[str]:
        """Generate application tips based on match analysis"""
        tips = []
        
        match_percentage = matches['skill_match_percentage']
        
        if match_percentage < 50:
            tips.append("Consider emphasizing transferable skills and learning ability")
        elif match_percentage > 80:
            tips.append("Strong match - highlight your expertise confidently")
        
        tips.append("Research the company's recent projects and news")
        tips.append("Prepare specific examples of your technical achievements")
        tips.append("Practice explaining complex technical concepts simply")
        
        return tips

# Main interactive interface
def integrated_job_application_flow():
    """Integrated flow: Search jobs with QA Agent, then create applications with WriterAgent"""
    
    print("Integrated Job Search & Application System")
    print("=" * 60)
    
    # Initialize WriterAgent
    writer = WriterAgent()
    
    print(f"\nCurrent profile: {writer.user_profile.name}")
    print(f"Email: {writer.user_profile.email}")
    print(f"Skills: {', '.join(writer.user_profile.technical_skills[:5])}")
    
    # Menu options
    while True:
        print("\n" + "=" * 60)
        print("What would you like to do?")
        print("1. Update my profile information")
        print("2. Load profile from uploaded resume JSON")
        print("3. Create resume & cover letter for specific job ID")
        print("4. Test with sample job")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            writer.update_profile_interactive()
            
        elif choice == "2":
            json_path = input("\nEnter path to uploaded resume JSON file: ").strip()
            if os.path.exists(json_path):
                writer.load_profile_from_uploaded_resume(json_path)
            else:
                print("File not found. Please check the path.")
            
        elif choice == "3":
            job_id = input("\nEnter job ID from your job search: ").strip()
            if job_id:
                print(f"\nCreating application materials for job ID: {job_id}")
                result = writer.create_resume_for_job(job_id)
                
                if "error" in result:
                    print(f"Error: {result['error']}")
                else:
                    print(f"\nApplication Summary:")
                    print(f"Job: {result['job_details']['job_title']}")
                    print(f"Company: {result['job_details']['company']}")
                    print(f"Location: {result['job_details']['location']}")
                    print(f"Salary: {result['job_details']['salary'] or 'Not specified'}")
                    print(f"Match: {result['match_analysis']['skill_match_percentage']:.1f}%")
                    print(f"Matching Skills: {', '.join(result['match_analysis']['matching_skills'][:5])}")
                    
                    print(f"\nFiles Created:")
                    print(f"Resume: {result['files_saved']['resume']}")
                    print(f"Cover Letter: {result['files_saved']['cover_letter']}")
                    
                    print(f"\nTips:")
                    for tip in result['application_tips']:
                        print(f"  - {tip}")
                    
                    # Ask if user wants to see the content
                    show = input(f"\nView generated content? (y/n): ").strip().lower()
                    if show == 'y':
                        print(f"\nRESUME:\n{'-'*40}\n{result['resume']}")
                        print(f"\nCOVER LETTER:\n{'-'*40}\n{result['cover_letter']}")
            
        elif choice == "4":
            # Test with sample job
            sample_job_data = {
                'job_id': 'test-123',
                'job_title': 'Senior Python Developer',
                'company': 'Tech Innovations Corp',
                'location': 'San Francisco, CA (Remote)',
                'salary': '$120,000 - $150,000',
                'skills': 'Python, Django, React, PostgreSQL, AWS',
                'description': 'We are seeking a Senior Python Developer to build scalable web applications...'
            }
            
            print(f"\nTesting with sample job: {sample_job_data['job_title']}")
            
            # Simulate the process without database lookup
            resume = writer.generate_tailored_resume(writer.user_profile, sample_job_data)
            cover_letter = writer.generate_cover_letter(writer.user_profile, sample_job_data)
            
            print(f"\nSAMPLE RESUME:\n{'-'*40}\n{resume}")
            print(f"\nSAMPLE COVER LETTER:\n{'-'*40}\n{cover_letter}")
            
        elif choice == "5":
            print("\nThank you for using the Job Application System!")
            break
            
        else:
            print("Invalid choice. Please select 1-5.")

# Main execution
if __name__ == "__main__":
    integrated_job_application_flow()