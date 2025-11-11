# QA Agent - Job Search Assistant

## Overview
The QA Agent is an AI-powered job search assistant that connects to your BigQuery database and uses OpenAI to provide intelligent responses to job-related questions.

## Setup

For complete installation and setup instructions, please refer to the [main README](../../../README.md#installation-and-setup).

**Quick Setup Checklist:**
- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from root `requirements.txt`
- [ ] BigQuery service account created with proper permissions
- [ ] `.env` file configured with required credentials
- [ ] OpenAI API key configured

## Testing the Agent

After completing the setup from the main README, test the QA Agent:

```bash
# From the project root
cd backend/app/agents

# Test connections
python test_connections.py
```

## Usage

```python
from qa_agent import QAAgent

# Initialize the agent
agent = QAAgent()

# Ask a question
response = agent.query("Find all software engineering jobs in California")
print(response)
```

## Environment Variables Required

Ensure your `.env` file (in project root) contains:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GCP_PROJECT_ID=your-project-id
BQ_DATASET=job_search
OPENAI_API_KEY=your-openai-api-key
```

## Troubleshooting

For common issues and solutions, see the [Troubleshooting section](../../../README.md#troubleshooting) in the main README.