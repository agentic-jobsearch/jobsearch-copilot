#Important libraries to test connections to BigQuery and OpenAI.
import os
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account

load_dotenv()

# Test BigQuery connection
def test_bigquery_connection():
    try:
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        print(f"Credentials path: {credentials_path}")
        
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            client = bigquery.Client(credentials=credentials, project='agentic-jobsearch')
        else:
            client = bigquery.Client(project='agentic-jobsearch')

        
        print(f"Connected to BigQuery project: {client.project}")
        
        # Test a simple query
        query = "SELECT COUNT(*) as job_count FROM `agentic-jobsearch.job_search.job_details`"
        results = client.query(query)
        
        for row in results:
            print(f"Found {row.job_count} jobs in database")
            
        return True
        
    except Exception as e:
        print(f"BigQuery connection failed: {e}")
        return False

# Test OpenAI connection
def test_openai_connection():
    try:
        from openai import OpenAI
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("OPENAI_API_KEY not found in environment")
            return False
            
        client = OpenAI(api_key=api_key)
        
        # Test a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        
        print(f"OpenAI connection successful: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"OpenAI connection failed: {e}")
        return False

# Test environment variables
def test_env_variables():
    print("Checking environment variables:")

    google_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    openai_key = os.getenv('OPENAI_API_KEY')
    apify_key = os.getenv('APIFY_API_KEY')
    
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {'Set' if google_creds else 'Missing'}")
    print(f"OPENAI_API_KEY: {'Set' if openai_key else 'Missing'}")
    print(f"APIFY_API_KEY: {'Set' if apify_key else 'Missing'}")
    
    if google_creds:
        print(f"Google credentials file: {google_creds}")
    
        if os.path.exists(google_creds):
            print("Google credentials file exists")
        else:
            print("Google credentials file not found")

# Main test execution
if __name__ == "__main__":
    print("Testing Connections...\n")
    
    print("Testing Environment Variables:")
    test_env_variables()
    
    print("\nTesting BigQuery Connection:")
    bigquery_ok = test_bigquery_connection()
    
    print("\nTesting OpenAI Connection:")
    openai_ok = test_openai_connection()
    
    print(f"\n Results:")
    print(f"BigQuery: {'yes' if bigquery_ok else 'no'}")
    print(f"OpenAI: {'yes' if openai_ok else 'no'}")
    
    if bigquery_ok and openai_ok:
        print("\n All connections successful! Ready to run agents.")
    else:
        print("\n Some connections failed. Check your credentials.")