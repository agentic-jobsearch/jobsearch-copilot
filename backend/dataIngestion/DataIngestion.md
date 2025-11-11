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

### `test.py`
Test script to verify BigQuery connection

---

## Setup

For complete installation and setup instructions including BigQuery configuration, please refer to the [main README](../../README.md#installation-and-setup).

**Quick Setup Checklist:**
- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from root `requirements.txt`
- [ ] BigQuery service account created with required permissions
- [ ] `.env` file configured in project root

---

## Running Data Ingestion

After completing the setup from the main README:

### 1. Test BigQuery Connection
```bash
cd backend/dataIngestion
python test.py
```

### 2. Run Data Ingestion
```bash
python ApiClient.py
```

### 3. Verify Data
Check your BigQuery console to verify data has been loaded into:
- `job_search.job_details` table
- `job_search.company` table

---

## Environment Variables Required

Ensure your `.env` file (in project root) contains:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GCP_PROJECT_ID=your-project-id
BQ_DATASET=job_search
APIFY_API_TOKEN=your-apify-token
```

---

## Troubleshooting

For common BigQuery connection issues and solutions, see the [Troubleshooting section](../../README.md#troubleshooting) in the main README.

### Data Ingestion Specific Issues

**Issue: "Apify API token not found"**
- Verify `APIFY_API_TOKEN` is set in your `.env` file
- Check that you have an active Apify account

**Issue: "Table not found"**
- The script will create tables automatically on first run
- Ensure your service account has BigQuery Data Editor permissions

**Issue: "Duplicate key errors"**
- The upsert mechanism handles duplicates automatically
- Check the MERGE operation logs for details


