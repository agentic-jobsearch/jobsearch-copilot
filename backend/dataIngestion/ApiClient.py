import os
import requests
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.dataIngestion.BigqueryUpsert import upsert_dataframe_to_bigquery

# Load environment variables
load_dotenv()

# Set up credentials
credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
credentials = service_account.Credentials.from_service_account_file(credentials_path)
client = bigquery.Client(credentials=credentials, project='agentic-jobsearch')

# API setup
url = "https://api.apify.com/v2/datasets/GHL1cZOFH5JAEpkmI/items"
API_TOKEN = os.getenv('APIFY_API_KEY')

payload = {}
headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {API_TOKEN}'
}

try:
    response = requests.request("GET", url, headers=headers, data=payload)
    response.raise_for_status()
    
    data = response.json()
    df = pd.DataFrame(data)
    
    # Create company DataFrame
    company_df = df[['company', 'company_url', 'company_urn']].drop_duplicates()
    
    # Remove rows where company_urn is null or empty
    company_df = company_df.dropna(subset=['company_urn'])
    company_df = company_df[company_df['company_urn'].str.strip() != '']
    
    # Create job details DataFrame
    job_details_df = df[[
        'job_id', 'job_title', 'job_url', 'location', 'work_type', 'salary',
        'posted_at', 'posted_at_epoch', 'skills', 'benefits', 'is_easy_apply',
        'is_promoted', 'applicant_count', 'description', 'created_at',
        'created_at_epoch', 'geo_id', 'navigation_subtitle', 'is_verified',
        'job_insights', 'apply_url', 'company_urn'
    ]].copy()  # Add .copy() to avoid SettingWithCopyWarning
    
    # Convert array columns to strings
    if 'skills' in job_details_df.columns:
        job_details_df['skills'] = job_details_df['skills'].apply(
            lambda x: ', '.join(x) if isinstance(x, list) else str(x) if x is not None else ''
        )
    
    if 'benefits' in job_details_df.columns:
        job_details_df['benefits'] = job_details_df['benefits'].apply(
            lambda x: ', '.join(x) if isinstance(x, list) else str(x) if x is not None else ''
        )
    
    if 'job_insights' in job_details_df.columns:
        job_details_df['job_insights'] = job_details_df['job_insights'].apply(
            lambda x: ', '.join(x) if isinstance(x, list) else str(x) if x is not None else ''
        )
    
    # Convert numeric columns to integers (for BigQuery INT64)
    if 'applicant_count' in job_details_df.columns:
        job_details_df['applicant_count'] = pd.to_numeric(job_details_df['applicant_count'], errors='coerce').fillna(0).astype(int)
    
    if 'posted_at_epoch' in job_details_df.columns:
        job_details_df['posted_at_epoch'] = pd.to_numeric(job_details_df['posted_at_epoch'], errors='coerce').fillna(0).astype(int)
    
    if 'created_at_epoch' in job_details_df.columns:
        job_details_df['created_at_epoch'] = pd.to_numeric(job_details_df['created_at_epoch'], errors='coerce').fillna(0).astype(int)
    
    # Convert timestamp columns from string to timezone-aware datetime (for TIMESTAMP type)
    if 'posted_at' in job_details_df.columns:
        job_details_df['posted_at'] = pd.to_datetime(job_details_df['posted_at'], errors='coerce', utc=True)
    
    if 'created_at' in job_details_df.columns:
        job_details_df['created_at'] = pd.to_datetime(job_details_df['created_at'], errors='coerce', utc=True)
    
    # Remove rows where job_id or company_urn is null
    job_details_df = job_details_df.dropna(subset=['job_id', 'company_urn'])
    job_details_df = job_details_df[job_details_df['job_id'].str.strip() != '']
    job_details_df = job_details_df[job_details_df['company_urn'].str.strip() != '']
    
    print(f"Company DataFrame shape: {company_df.shape}")
    print(f"Job Details DataFrame shape: {job_details_df.shape}")
    
    # Check data types
    print("\nData types:")
    print(job_details_df[['posted_at', 'created_at', 'skills', 'applicant_count', 'is_easy_apply']].dtypes)
    
    # Load data into BigQuery only if we have valid data
    if not company_df.empty:
        company_df_copy = company_df.copy()
        upsert_dataframe_to_bigquery(
            df=company_df_copy,
            destination="agentic-jobsearch.job_search.company",
            key_columns="company_urn",
            project="agentic-jobsearch"
        )
        print("Company data successfully loaded!")
    else:
        print("No valid company data to load (all company_urn values are null)")
    
    if not job_details_df.empty:
        upsert_dataframe_to_bigquery(
            df=job_details_df,
            destination="agentic-jobsearch.job_search.job_details",
            key_columns="job_id",
            project="agentic-jobsearch"
        )
        print("Job details data successfully loaded!")
    else:
        print("No valid job details data to load (all key values are null)")

except Exception as e:
    print(f"An error occurred: {e}")