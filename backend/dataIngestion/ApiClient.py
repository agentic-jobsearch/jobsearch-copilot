import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://api.apify.com/v2/datasets/GHL1cZOFH5JAEpkmI/items"
API_TOKEN = os.getenv('APIFY_API_KEY')

payload = {}
headers = {
  'Accept': 'application/json',
  'Authorization': f'Bearer {API_TOKEN}'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)