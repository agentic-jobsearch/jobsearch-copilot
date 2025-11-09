# Data Ingestion Process

This folder contains the data ingestion pipeline for the job search application. The process extracts job data from Apify API and loads it into Google BigQuery using an upsert mechanism.

## Overview

The data ingestion process consists of:
1. **Data Extraction**: Fetch job data from Apify API
2. **Data Transformation**: Clean and format data for BigQuery
3. **Data Loading**: Upsert data into BigQuery tables using MERGE operations

## Files

### `ApiClient.py`
Main data ingestion script that:
- Fetches job data from Apify API
- Transforms and cleans the data
- Splits data into company and job details DataFrames
- Loads data into BigQuery tables

### `BigqueryUpsert.py`
Utility module for upserting DataFrames to BigQuery:
- Creates temporary staging tables
- Performs MERGE operations (INSERT/UPDATE)
- Handles schema validation
- Cleans up temporary tables

### `.env`
Environment configuration file containing:


# How to Run Data Ingestion on Your Local Machine

## Prerequisites

### 1. System Requirements
- Python 3.10 or higher

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


