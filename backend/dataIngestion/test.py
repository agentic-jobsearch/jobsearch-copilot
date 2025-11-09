from google.cloud import bigquery
from google.oauth2 import service_account

# Path to your service account key
key_path = "/Users/lebak/Documents/mydemo.json"

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

