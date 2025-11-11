# JobSearch Co-Pilot
**Always applying. Always improving.**

Agentic AI that finds jobs, tailors materials, and applies where allowed (hybrid auto-apply).

## Stack
- Frontend: ReactJS + Tailwind (desktop dashboard)
- Backend: FastAPI (Python) + LangGraph (agents)
- Memory: FAISS (local dev)
- Packaging: Docker + docker-compose
- CI: GitHub Actions

## MVP
1) Upload resume + extract skills
2) Pull jobs (Indeed first) → score fits
3) Tailored cover letter + résumé
4) Auto-apply on supported platforms (Indeed/ZipRecruiter); checklist for others

---

## Installation and Setup

### Prerequisites
- Python 3.10 or higher
- Git
- Google Cloud account (for BigQuery)
- OpenAI API key (for AI agents)

### Step 1: Clone the Repository
```bash
git clone https://github.com/agentic-jobsearch/jobsearch-copilot.git
cd jobsearch-copilot
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# If SSL issues occur (common on some networks), use:
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Step 4: Configure Google Cloud BigQuery

#### 4.1 Create Service Account
1. Navigate to [Google Cloud Console](https://console.cloud.google.com/)
2. Go to **IAM & Admin** > **Service Accounts**
3. Click **"Create Service Account"**
4. Give it a name (e.g., `jobsearch-data-ingestion`)
5. Assign the following roles:
   - **BigQuery Data Editor** - To read/write data in BigQuery
   - **BigQuery Job User** - To run BigQuery jobs
   - **BigQuery User** - To access BigQuery resources

#### 4.2 Create and Download Key
1. Click on the created service account
2. Go to the **"Keys"** tab
3. Click **"Add Key"** > **"Create new key"**
4. Select **JSON** format
5. Click **"Create"** - this will download the JSON key file
6. Save the file securely (e.g., `~/credentials/jobsearch-service-account.json`)

**Security Note:** Never commit this JSON key file to version control!

### Step 5: Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Google Cloud BigQuery
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
GCP_PROJECT_ID=your-project-id
BQ_DATASET=job_search

# OpenAI API
OPENAI_API_KEY=your-openai-api-key

# Optional: Apify API (for job scraping)
APIFY_API_TOKEN=your-apify-token
```

**File Permissions (macOS/Linux):**
```bash
# Make credentials file readable only by owner
chmod 600 /path/to/your/service-account-key.json

# Ensure .env is not committed
echo ".env" >> .gitignore
```

### Step 6: Verify Installation

Test your BigQuery connection:
```bash
cd backend/dataIngestion
python test.py
```

Expected output:
```
Successfully connected to BigQuery project: your-project-id
Query results:
...
```

Test the QA Agent connection:
```bash
cd backend/app/agents
python test_connections.py
```

---

## Project Structure

```
jobsearch-copilot/
├── backend/
│   ├── app/               # FastAPI application
│   │   └── agents/        # AI agents (QA, job matching, etc.)
│   ├── dataIngestion/     # BigQuery data ingestion scripts
│   └── requirements.txt   # Backend-specific dependencies (deprecated - use root)
├── frontend/              # React dashboard
├── data/                  # Local data files
├── docs/                  # Documentation
├── infra/                 # Infrastructure and deployment configs
├── requirements.txt       # All Python dependencies
└── README.md             # This file
```

---

## Troubleshooting

### SSL Certificate Issues
If you encounter SSL certificate errors during package installation:
```bash
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### BigQuery Connection Issues
1. **"404 Not found: Dataset"**
   - Verify the dataset exists in your BigQuery project
   - Check that your service account has the correct permissions
   - Ensure the dataset name in `.env` matches your BigQuery dataset

2. **"Permission denied"**
   - Verify your service account has the required roles (BigQuery Data Editor, Job User, User)
   - Check that the `GOOGLE_APPLICATION_CREDENTIALS` path is correct
   - Ensure the JSON key file has proper read permissions

3. **"DefaultCredentialsError"**
   - Verify the service account JSON key file is valid
   - Check that the file path in `.env` is absolute, not relative
   - Ensure the file has not been corrupted

### OpenAI API Issues
- Verify your API key is correct and active
- Check that you have sufficient credits in your OpenAI account
- Ensure the `OPENAI_API_KEY` is properly set in your `.env` file

---

## Additional Resources

- [Backend Agent Documentation](backend/app/agents/Agent.md)
- [Data Ingestion Guide](backend/dataIngestion/DataIngestion.md)
- [BigQuery Quick Start](backend/dataIngestion/QUICK_START.md)
- [Agent Design Documentation](docs/agent-design.md)
- [Project Roadmap](docs/roadmap.md)

---

## Contributing

We welcome contributions! Please ensure you:
1. Follow the installation steps above to set up your environment
2. Install all dependencies from `requirements.txt`
3. Test your changes before submitting a PR
4. Follow the existing code style and conventions

---

## Security Best Practices

1. **Never commit secrets to version control**
   - Service account keys
   - API keys
   - Passwords or tokens

2. **Use environment variables for sensitive data**
   - Store credentials in `.env` file
   - Add `.env` to `.gitignore`

3. **Rotate credentials periodically**
   - Create new service account keys regularly
   - Delete old keys from Google Cloud Console

4. **Set appropriate file permissions**
   ```bash
   chmod 600 /path/to/credentials.json
   chmod 600 .env
   ```
