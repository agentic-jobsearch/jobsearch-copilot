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

### 2. Required Files
- `.env` file with API keys


## Installation

### Step 1: Create Virtual Environment
```bash
# Navigate to project directory
cd /Users/anan/Documents/jobsearch-copilot

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install required packages
pip install google-cloud-bigquery python-dotenv openai

# If SSL issues occur, use:
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org google-cloud-bigquery python-dotenv openai