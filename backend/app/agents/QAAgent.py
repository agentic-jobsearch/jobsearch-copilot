import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
from openai import OpenAI
from app.core.env import require_env

OPENAI_KEY = require_env("OPENAI_API_KEY")
self.client = OpenAI(api_key=OPENAI_KEY)


# QA Agent for Job Search
class QAAgent:
    def __init__(self):
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize BigQuery client
        self.bigquery_client = self._init_bigquery_client()
        
        # System prompt for the AI agent
        self.system_prompt = """
        You are an intelligent job search assistant with access to a job database containing software engineer roles. 
        You help users find jobs by analyzing their queries and retrieving relevant information from the database.
        
        When users ask about jobs, you should:
        1. Understand what they're looking for (skills, location, company, etc.)
        2. Present the results in a helpful, conversational way
        3. Provide specific details like job titles, companies, locations, salaries, and skills
        4. Give insights and recommendations when appropriate
        
        Always be helpful and provide actionable information.
        """
        
        print("QA Agent initialized successfully!")
    
    # Initialize BigQuery client
    def _init_bigquery_client(self) -> bigquery.Client:
        """Initialize BigQuery client using service account credentials"""
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            return bigquery.Client(credentials=credentials, project='agentic-jobsearch')
        else:
            return bigquery.Client(project='agentic-jobsearch')
    
    # Analyze user query to extract search parameters
    def analyze_user_query(self, user_question: str) -> Dict[str, Any]:
        """Use OpenAI to analyze user question and extract search parameters"""
        analysis_prompt = f"""
        Analyze this user question about jobs and extract search parameters:
        
        User Question: "{user_question}"
        
        Extract these parameters when mentioned or implied:
        - keywords: list of job titles, skills, technologies, or industry terms
        - location: city, state, country, or remote preferences  
        - company: specific company names
        - work_type: full-time, part-time, contract, remote, hybrid, etc.
        - salary_interest: if user asks about salary information
        - experience_level: entry, junior, mid, senior, lead, manager
        - question_type: "job_search", "job_details", "salary_info", "company_info", "general_advice"
        
        Return JSON format only:
        {{
            "question_type": "job_search",
            "keywords": ["python", "developer"],
            "location": "san francisco",
            "company": null,
            "work_type": null,
            "salary_interest": false,
            "search_intent": "brief description of what user wants"
        }}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.1
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            print(f"Error analyzing query: {e}")
            return {
                "question_type": "job_search",
                "keywords": user_question.lower().split(),
                "search_intent": "Find relevant jobs"
            }
    
    # Query BigQuery database for jobs
    def query_database(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query BigQuery database based on search parameters"""
        base_query = """
        SELECT 
            jd.job_id,
            jd.job_title,
            c.company,
            c.company_url,
            jd.location,
            jd.work_type,
            jd.salary,
            jd.skills,
            jd.description,
            jd.posted_at,
            jd.job_url,
            jd.applicant_count,
            jd.is_easy_apply,
            jd.benefits
        FROM `agentic-jobsearch.job_search.job_details` jd
        JOIN `agentic-jobsearch.job_search.company` c 
            ON jd.company_urn = c.company_urn
        WHERE 1=1
        """
        
        conditions = []
        
        # Add keyword search: Use LIKE instead of CONTAINS
        if search_params.get('keywords'):
            keywords = search_params['keywords']
            keyword_conditions = []
            for keyword in keywords:
                # Escape single quotes and use proper SQL syntax
                safe_keyword = keyword.replace("'", "\\'")
                keyword_conditions.append(
                    f"(LOWER(jd.job_title) LIKE LOWER('%{safe_keyword}%') OR "
                    f"LOWER(jd.description) LIKE LOWER('%{safe_keyword}%') OR "
                    f"LOWER(jd.skills) LIKE LOWER('%{safe_keyword}%'))"
                )
       ### If you want to be more specific, you can use AND between keywords instead of OR

            if keyword_conditions:
                conditions.append(f"({' OR '.join(keyword_conditions)})")
        
        # Add location filter
        if search_params.get('location'):
            safe_location = search_params['location'].replace("'", "\\'")
            conditions.append(f"LOWER(jd.location) LIKE LOWER('%{safe_location}%')")
        
        # Add company filter 
        if search_params.get('company'):
            safe_company = search_params['company'].replace("'", "\\'")
            conditions.append(f"LOWER(c.company) LIKE LOWER('%{safe_company}%')")
        
        # Add work type filter
        if search_params.get('work_type'):
            safe_work_type = search_params['work_type'].replace("'", "\\'")
            conditions.append(f"LOWER(jd.work_type) LIKE LOWER('%{safe_work_type}%')")
        
        # Add conditions to query
        if conditions:
            base_query += " AND " + " AND ".join(conditions)
        
        # Order by posted date and limit results
        base_query += " ORDER BY jd.posted_at DESC LIMIT 10"
        
       # print(f"Executing SQL: {base_query}")
        
        try:
            results = self.bigquery_client.query(base_query)
            jobs = []
            
            for row in results:
                job = {
                    'job_id': row.job_id,
                    'job_title': row.job_title,
                    'company': row.company,
                    'company_url': row.company_url,
                    'location': row.location,
                    'work_type': row.work_type,
                    'salary': row.salary,
                    'skills': row.skills,
                    'description': row.description,
                    'posted_at': str(row.posted_at) if row.posted_at else None,
                    'job_url': row.job_url,
                    'applicant_count': row.applicant_count,
                    'is_easy_apply': row.is_easy_apply,
                    'benefits': row.benefits
                }
                jobs.append(job)
            
            return jobs
            
        except Exception as e:
            print(f"Error querying database: {e}")
            return []
    # Generate AI response based on job data
    def generate_response(self, user_question: str, search_params: Dict, jobs_data: List[Dict]) -> str:
        
        context = f"""
        User Question: "{user_question}"
        Search Parameters: {json.dumps(search_params, indent=2)}
        
        Found {len(jobs_data)} software engineer jobs in the database:
        """
        
        # Add job details to context
        for i, job in enumerate(jobs_data[:5]):  # Limit to top 5 jobs for context
            context += f"""
            
            Job {i+1}:
            - Title: {job['job_title']}
            - Company: {job['company']}
            - Location: {job['location']}
            - Salary: {job['salary'] or 'Not specified'}
            - Work Type: {job['work_type'] or 'Not specified'}
            - Skills: {job['skills'] or 'Not specified'}
            - Posted: {job['posted_at'] or 'Not specified'}
            - Easy Apply: {'Yes' if job['is_easy_apply'] else 'No'}
            - Applicants: {job['applicant_count'] or 'Not specified'}
            - Job URL: {job['job_url'] or 'Not available'}
            - Benefits: {job['benefits'] or 'Not specified'}
            """
        
        # Create response prompt
        response_prompt = f"""
        Based on the job search results, provide a helpful and conversational response to the user's question.
        
        {context}
        
        Instructions:
        1. Directly answer the user's question
        2. Highlight the most relevant jobs
        3. Include specific details like company names, locations, salaries when available
        4. If no jobs found, provide helpful suggestions
        5. Be conversational and helpful
        6. Include job URLs when available
        7. Mention key skills or requirements
        8. Keep the response informative but concise (under 500 words)
        
        Format the response in a friendly, conversational tone.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": response_prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._fallback_response(jobs_data)
    
    #  Fallback response method
    def _fallback_response(self, jobs_data: List[Dict]) -> str:
        """Fallback response if OpenAI fails"""
        if not jobs_data:
            return "I couldn't find any jobs matching your criteria in our database. Try broadening your search terms or check back later for new postings."
        
        response = f"I found {len(jobs_data)} software engineer jobs for you:\n\n"
        
        for i, job in enumerate(jobs_data[:5]):
            response += f"{i+1}. **{job['job_title']}** at **{job['company']}**\n"
            response += f"    {job['location']}\n"
            if job['salary']:
                response += f"   {job['salary']}\n"
            if job['skills']:
                response += f"   Skills: {job['skills']}\n"
            if job['job_url']:
                response += f"   Apply: {job['job_url']}\n"
            response += "\n"
        
        return response
    
    # Main method to handle user questions
    def ask_about_jobs(self, user_question: str) -> str:
        """Main method to handle job-related questions"""
        print(f"Processing question: {user_question}")
        
        try:
            # 1. Analyze the user's question
            search_params = self.analyze_user_query(user_question)
            print(f"Search parameters: {search_params}")
            
            # 2. Query the database
            jobs_data = self.query_database(search_params)
            print(f"Found {len(jobs_data)} jobs")
            
            # 3. Generate AI response
            response = self.generate_response(user_question, search_params, jobs_data)
            
            return response
            
        except Exception as e:
            print(f"Error in ask_about_jobs: {e}")
            return "I'm sorry, I encountered an error while searching for jobs. Please try again with a different question."

# Test the QA Agent with Interactive Input
if __name__ == "__main__":
    print("Job Search QA Agent Ready!")
    print("=" * 60)
    print("Ask me anything about jobs!")
    print("Type 'quit', 'exit', or 'q' to stop.")
    print("=" * 60)
    
    agent = QAAgent()
    
    while True:
        try:
            # Get user input
            user_question = input("\n Your question: ").strip()
            
            # Check for exit commands
            if user_question.lower() in ['quit', 'exit', 'q', '']:
                print("\n Thank you for using the Job Search QA Agent!")
                print("Happy job hunting! Goodbye!")
                break
            
            # Process the question
            print("\n Thinking...")
            print("-" * 40)
            
            answer = agent.ask_about_jobs(user_question)
            print(f"Answer:\n{answer}")
            print("\n" + "=" * 60)
            
        except KeyboardInterrupt:
            print("\n\n Goodbye! Thanks for using the Job Search QA Agent!")
            break
        except Exception as e:
            print(f"\n An error occurred: {e}")
            print("Please try asking your question again.")