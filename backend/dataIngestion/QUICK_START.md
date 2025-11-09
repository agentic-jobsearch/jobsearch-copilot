# BigQuery Service Account Setup Guide

This guide will help you set up and run the BigQuery test script on a new local machine.

## Prerequisites

Before you begin, ensure you have:
- Python 3.7 or higher installed
- A Google Cloud service account key JSON file
- Internet connection

## Step-by-Step Setup Instructions

### 1. Install Python (if not already installed)

**For macOS:**
```bash
# Check if Python 3 is installed
python3 --version

# If not installed, download from python.org or use Homebrew:
brew install python3
```

**For Windows:**
- Download Python from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"

**For Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Copy Required Files

Copy these files to your new machine:
1. `test.py` - The main script
2. Your Google Cloud service account key JSON file (e.g., `mydemo.json`)

### 3. Place Your Service Account Key

Put your service account key JSON file in a secure location. 

**Example locations:**
- macOS/Linux: `/Users/yourusername/Documents/mydemo.json`
- Windows: `C:\Users\yourusername\Documents\mydemo.json`

**Important:** Keep this file secure and never commit it to version control!

### 4. Update the Script with Your Key Path

Edit `test.py` and update line 5 with the path to your service account key:

```python
# Update this path to match your key file location
key_path = "/path/to/your/service-account-key.json"
```

### 5. Install Required Python Packages

Open a terminal/command prompt and run:

```bash
# Install the Google Cloud BigQuery library
pip3 install google-cloud-bigquery

# Or if using pip:
pip install google-cloud-bigquery
```

This will install:
- `google-cloud-bigquery` (main library)
- `google-auth` (authentication)
- `google-api-core` (API dependencies)
- Other required dependencies

### 6. Verify Your Setup

Before running the full script, verify your service account key is valid:

**Check the file exists:**
```bash
# macOS/Linux:
ls -la /path/to/your/service-account-key.json

# Windows:
dir C:\path\to\your\service-account-key.json
```

**Check the JSON is valid:**
```bash
python3 -c "import json; print(json.load(open('/path/to/your/key.json'))['project_id'])"
```

### 7. Run the Script

Navigate to the directory containing `test.py` and run:

```bash
python3 test.py
```

**Expected Output:**
```
Successfully connected to BigQuery project: your-project-id

Query results:
--------------------------------------------------------------------------------
Row(('job_id', 'job_title', 'job_url', ...
...
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: `ModuleNotFoundError: No module named 'google.cloud'`
**Solution:** Install the BigQuery library:
```bash
pip3 install google-cloud-bigquery
```

#### Issue: `FileNotFoundError: [Errno 2] No such file or directory`
**Solution:** 
- Check that the `key_path` in `test.py` points to the correct location
- Verify the file exists at that location
- Use absolute paths instead of relative paths

#### Issue: `google.api_core.exceptions.NotFound: 404 Not found: Dataset`
**Solution:** 
- The authentication is working, but the dataset/table doesn't exist
- Update the query in `test.py` to use a valid dataset and table name
- Run this helper script to list available datasets:

```python
from google.cloud import bigquery
from google.oauth2 import service_account

key_path = "/path/to/your/key.json"
credentials = service_account.Credentials.from_service_account_file(key_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

print(f"Project: {credentials.project_id}")
print("\nAvailable datasets:")
for dataset in client.list_datasets():
    print(f"  - {dataset.dataset_id}")
```

#### Issue: `google.auth.exceptions.DefaultCredentialsError`
**Solution:** 
- Verify your service account key JSON file is valid
- Ensure the file has proper read permissions
- Check that the service account has BigQuery access in Google Cloud Console

#### Issue: Permission denied errors
**Solution:**
- Verify the service account has the necessary BigQuery permissions:
  - `BigQuery Data Viewer` (to read data)
  - `BigQuery Job User` (to run queries)
- Check permissions in Google Cloud Console → IAM & Admin → IAM

## Security Best Practices

1. **Never commit service account keys to version control**
   ```bash
   # Add to .gitignore:
   *.json
   mydemo.json
   *-key.json
   ```

2. **Use environment variables for sensitive paths**
   ```python
   import os
   key_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '/default/path/key.json')
   ```

3. **Set appropriate file permissions**
   ```bash
   # macOS/Linux - Make file readable only by owner:
   chmod 600 /path/to/key.json
   ```

4. **Rotate keys periodically**
   - Create new service account keys regularly
   - Delete old keys from Google Cloud Console

## Additional Resources

- [Google Cloud BigQuery Python Client Documentation](https://cloud.google.com/python/docs/reference/bigquery/latest)
- [Service Account Authentication Guide](https://cloud.google.com/docs/authentication/production)
- [BigQuery Quickstart Guide](https://cloud.google.com/bigquery/docs/quickstarts)

## Project Information

- **Project ID:** agentic-jobsearch
- **Available Datasets:** 
  - `job_search` (contains: `company`, `job_details` tables)

## Sample Queries

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

**Last Updated:** November 9, 2025