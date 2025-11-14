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

# QA Agent - Job Search Assistant

## Overview
The QA Agent is an AI-powered job search assistant that connects to your BigQuery database and uses OpenAI to provide intelligent responses to job-related questions.

## Prerequisites

### 1. Environment Setup
- Python 3.10 or higher
- Virtual environment (recommended)
- BigQuery database with job data
- OpenAI API key
- Google Cloud credentials

# Create and Active Virtual Environment 
- python3 -m venv venv
- source venv/bin/activate   # macOS/Linux
- venv\Scripts\activate      # Windows

# Install Requirements
- pip install -r requirements.txt

# Create a .env file in the project root:
- OPENAI_API_KEY=your_key_here
- GOOGLE_APPLICATION_CREDENTIALS=/absolute/path/to/service_account.json
- APIFY_API_TOKEN=your_apify_token

# How to Run Data Ingestion on Your Local Machine & BigQuery Setup (Service Account)


# Data Ingestion Process
This folder contains the data ingestion pipeline for the job search application. The process extracts job data from Apify API and loads it into Google BigQuery using an upsert mechanism.

The data ingestion process consists of:
1. **Data Extraction**: Fetch job data from Apify API
2. **Data Transformation**: Clean and format data for BigQuery
3. **Data Loading**: Upsert data into BigQuery tables using MERGE operations

### 2. Google Cloud Setup
Before running the data ingestion, you need to set up Google Cloud access:

#### Step 1:Create Service Account
1. Navigate to IAM & Admin > Service Accounts
2. Click "Create Service Account"
3. Give it a name (e.g., `jobsearch-data-ingestion`)
4. Assign roles:
   - BigQuery Data Editor
   - BigQuery Job User
   - BigQuery User
5. Create and download the JSON key file
6. Save the key file securely (e.g., `~/Downloads/agentic-jobsearch-service-account.json`)

#### Step 2: Assign Roles
Assign the following roles to your service account:
- **BigQuery Data Editor** - To read/write data in BigQuery
- **BigQuery Job User** - To run BigQuery jobs
- **BigQuery User** - To access BigQuery resources

#### Step 3: Create and Download Key
1. Click on the created service account
2. Go to the **"Keys"** tab
3. Click **"Add Key"** > **"Create new key"**
4. Select **JSON** format
5. Click **"Create"** - this will download the JSON key file
6. Save the file securely (e.g., `~/Downloads/agentic-jobsearch-service-account.json`)

#### Step 4: Configure Environment Variables
1. Create/update the `.env` file in your project root:
```bash

pip install -r requirements.txt

# Backend
cd backend
uvicorn main:app --reload

# Frontend- (in a separate terminal)
cd frontend
npm install
npm run dev
```
Open http://localhost:5173/ in a browser to use the app.