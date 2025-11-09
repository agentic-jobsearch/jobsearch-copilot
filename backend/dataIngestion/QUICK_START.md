# Quick Start Guide - BigQuery Test Script

## 🚀 5-Minute Setup

### Step 1: Install Python 3
```bash
# Check if installed
python3 --version
```

### Step 2: Copy Files to New Machine
- `test.py`
- Your service account key JSON file (e.g., `mydemo.json`)

### Step 3: Update Key Path in test.py
```python
# Line 5 in test.py:
key_path = "/Users/yourusername/Documents/mydemo.json"  # Update this path
```

### Step 4: Install Dependencies
```bash
pip3 install google-cloud-bigquery
```

### Step 5: Run the Script
```bash
python3 test.py
```

## ✅ Expected Output
```
Successfully connected to BigQuery project: agentic-jobsearch

Query results:
--------------------------------------------------------------------------------
Row((job_data...))
...
```

## 🔧 Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: No module named 'google.cloud'` | Run: `pip3 install google-cloud-bigquery` |
| `FileNotFoundError` | Update `key_path` in test.py with correct path |
| `404 Not found: Dataset` | Authentication works! Update query with valid table name |

## 📋 Requirements
- Python 3.7+
- Google Cloud service account key (JSON file)
- Internet connection

## 🔐 Security Reminder
**Never commit your service account key to Git!**

Add to `.gitignore`:
```
*.json
mydemo.json
```

---
For detailed instructions, see `SETUP_GUIDE.md`

