# BigQuery Quick Start Guide

This guide provides a quick reference for testing BigQuery connectivity. For complete setup instructions, see the [main README](../../README.md#installation-and-setup).

## Quick Setup

1. **Complete the main setup first**: Follow the [Installation and Setup](../../README.md#installation-and-setup) section in the root README
2. **Verify your `.env` file** contains all required BigQuery credentials
3. **Run the test script** (see below)

## Testing BigQuery Connection

After completing the main setup:

```bash
# Navigate to the dataIngestion directory
cd backend/dataIngestion

# Run the test script
python test.py
```

**Expected Output:**
```
Successfully connected to BigQuery project: your-project-id

Query results:
--------------------------------------------------------------------------------
Row(('job_id', 'job_title', 'job_url', ...
...
```

---

## Troubleshooting

### Common Issues

For detailed troubleshooting, see the [main README Troubleshooting section](../../README.md#troubleshooting).

#### Quick Checks:

1. **Connection fails**: Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct
2. **Permission denied**: Ensure service account has BigQuery Data Editor, Job User, and User roles
3. **Dataset not found**: Update the query to use your actual dataset/table names

---

## Sample Queries

### List available datasets:
```python
from google.cloud import bigquery
from google.oauth2 import service_account

key_path = "/path/to/your/key.json"
credentials = service_account.Credentials.from_service_account_file(key_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

print(f"Project: {credentials.project_id}")
print("\nAvailable datasets:")
for dataset in client.list_datasets():
    print(f"  - {dataset.dataset_id}")
```

### Query job details:
```python
query = "SELECT * FROM `job_search.job_details` LIMIT 10"
```

### Query with filters:
```python
query = """
    SELECT job_title, location, salary 
    FROM `job_search.job_details` 
    WHERE location LIKE '%CA%'
    LIMIT 20
"""
```

### Query company information:
```python
query = "SELECT * FROM `job_search.company` LIMIT 10"
```

---

## Additional Resources

- [Main README - Installation](../../README.md#installation-and-setup)
- [Main README - Troubleshooting](../../README.md#troubleshooting)
- [Data Ingestion Documentation](DataIngestion.md)
- [Google Cloud BigQuery Documentation](https://cloud.google.com/python/docs/reference/bigquery/latest)
- [Service Account Authentication Guide](https://cloud.google.com/docs/authentication/production)
