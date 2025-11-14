from google.cloud import bigquery
from google.oauth2 import service_account
import os
from pathlib import Path
from dotenv import load_dotenv
from app.core.env import require_env

OPENAI_KEY = require_env("OPENAI_API_KEY")
self.client = OpenAI(api_key=OPENAI_KEY)


# Path to your service account key 
# python backend\dataIngestion\test.py
key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Create credentials
credentials = service_account.Credentials.from_service_account_file(key_path)

# Initialize BigQuery client
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Example query - using the job_search.job_details table
query = "SELECT * FROM `job_search.job_details` LIMIT 10"
results = client.query(query)

print(f"Successfully connected to BigQuery project: {credentials.project_id}\n")
print("Query results:")
print("-" * 80)

for row in results:
    print(row)

